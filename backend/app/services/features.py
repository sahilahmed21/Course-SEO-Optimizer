# backend/app/services/features.py

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from sklearn.feature_extraction.text import TfidfVectorizer
import string
import logging
from app.models.page_data import PageData, ExtractedFeatures # Absolute import
from collections import Counter
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- NLTK Setup ---
def download_nltk_resources():
    """Downloads NLTK resources if not found."""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        logger.info("Downloading NLTK 'punkt' tokenizer...")
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        logger.info("Downloading NLTK 'stopwords'...")
        nltk.download('stopwords', quiet=True)

# Call this once when the module is loaded
download_nltk_resources()
# --- End NLTK Setup ---


def _clean_and_tokenize(text: str) -> List[str]:
    """
    Cleans raw text:
    1. Lowercases
    2. Tokenizes
    3. Removes punctuation & stop words
    """
    if not text:
        return []
    
    text = text.lower()
    tokens = word_tokenize(text)
    
    stop_words = set(stopwords.words('english'))
    punct = set(string.punctuation)
    
    cleaned_tokens = [
        word for word in tokens 
        if word.isalpha() and word not in stop_words and word not in punct
    ]
    
    return cleaned_tokens

def calculate_keyword_densities(tokens: List[str], top_n: int = 50) -> Dict[str, float]:
    """
    Calculates keyword density for 1, 2, and 3-grams.
    Returns a dictionary of the top_n {ngram: density}
    """
    if not tokens or len(tokens) == 0:
        return {}

    total_words = len(tokens)
    densities = {}

    # 1-grams
    unigram_counts = Counter(tokens)
    for word, count in unigram_counts.items():
        densities[word] = (count / total_words) * 100

    # 2-grams
    bigrams = ngrams(tokens, 2)
    bigram_counts = Counter(bigrams)
    for bigram, count in bigram_counts.items():
        key = " ".join(bigram)
        densities[key] = (count / total_words) * 100

    # 3-grams
    trigrams = ngrams(tokens, 3)
    trigram_counts = Counter(trigrams)
    for trigram, count in trigram_counts.items():
        key = " ".join(trigram)
        densities[key] = (count / total_words) * 100
        
    # Return only the top N most frequent
    sorted_densities = sorted(densities.items(), key=lambda item: item[1], reverse=True)
    return dict(sorted_densities[:top_n])

def calculate_tf_idf(documents: List[str], max_features: int = 100) -> Dict[str, Any]:
    """
    Calculates TF-IDF for a list of documents (e.g., 4 course pages).
    
    Args:
        documents: A list of raw text strings [doc1_content, doc2_content, ...]
        
    Returns:
        A dictionary:
        {
            "doc_scores": [
                [{"term": "data", "score": 0.45}, ...], # for doc 1
                [{"term": "science", "score": 0.55}, ...], # for doc 2
            ],
            "top_terms": ["data", "science", ...]
        }
    """
    if not documents or len(documents) == 0:
        return {"doc_scores": [], "top_terms": []}

    try:
        vectorizer = TfidfVectorizer(
            tokenizer=_clean_and_tokenize,
            stop_words=stopwords.words('english'),
            ngram_range=(1, 3), 
            max_features=max_features
        )
        
        tfidf_matrix = vectorizer.fit_transform(documents)
        feature_names = vectorizer.get_feature_names_out()
        
        all_doc_scores = []
        
        for doc_index in range(tfidf_matrix.shape[0]):
            doc_scores = []
            scores = tfidf_matrix.toarray()[doc_index]
            for score_index, score in enumerate(scores):
                if score > 0:
                    doc_scores.append({
                        "term": feature_names[score_index],
                        "score": round(score, 4)
                    })
            
            doc_scores.sort(key=lambda x: x['score'], reverse=True)
            all_doc_scores.append(doc_scores)
            
        return {"doc_scores": all_doc_scores, "top_terms": list(feature_names)}

    except ValueError as e:
        logger.warning(f"TF-IDF failed: {e}. Likely empty documents.")
        return {"doc_scores": [[] for _ in documents], "top_terms": []}
    except Exception as e:
        logger.error(f"Error in TF-IDF calculation: {e}")
        return {"doc_scores": [[] for _ in documents], "top_terms": []}


def extract_features_from_page(page_data: PageData) -> ExtractedFeatures:
    """
    Main function to extract all features from a single PageData object.
    Note: TF-IDF is not calculated here as it requires *all* documents.
    """
    logger.info(f"Extracting features for {page_data.url}")
    
    main_content = page_data.main_content or ""
    tokens = _clean_and_tokenize(main_content)
    
    # Keyword Densities
    densities = calculate_keyword_densities(tokens, top_n=50)
    
    # Simple Metrics
    avg_word_len = 0.0
    if tokens:
        avg_word_len = sum(len(word) for word in tokens) / len(tokens)
    
    # Schema Types
    schema_types = []
    if page_data.json_ld:
        for schema in page_data.json_ld:
            if isinstance(schema, dict) and '@type' in schema:
                schema_type = schema.get('@type')
                if isinstance(schema_type, list):
                    schema_types.extend(schema_type)
                elif isinstance(schema_type, str):
                    schema_types.append(schema_type)
    
    features = ExtractedFeatures(
        url=str(page_data.url),
        word_count=page_data.word_count,
        keyword_densities=densities,
        avg_word_length=round(avg_word_len, 2),
        schema_types_present=list(set(schema_types)) # Get unique types
    )
    
    return features