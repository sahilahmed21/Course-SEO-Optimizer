# backend/test_features.py

import json
from app.services.scraper import scrape_page
from app.services.features import extract_features_from_page, calculate_tf_idf
import logging

# Set logging level higher for a cleaner test output
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("app")
logger.setLevel(logging.WARNING)

# Use the same trusty URL from Phase 2
TEST_URL_1 = "https://www.kcl.ac.uk/study/postgraduate-taught/courses/data-science-msc"
# And a competitor
TEST_URL_2 = "https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees/data-science-msc"

if __name__ == "__main__":
    print(f"--- Testing Feature Extraction (Phase 4) ---")
    
    # 1. Scrape pages (using Phase 2 code)
    print(f"Scraping {TEST_URL_1}...")
    page_data_1 = scrape_page(TEST_URL_1)
    print(f"Scraping {TEST_URL_2}...")
    page_data_2 = scrape_page(TEST_URL_2)

    if page_data_1.error or page_data_2.error:
        print("Scraping failed, cannot test features.")
        exit()

    # 2. Test single-page feature extraction
    print(f"\n--- Extracting features for Page 1 (KCL) ---")
    features_1 = extract_features_from_page(page_data_1)
    
    print(f"URL: {features_1.url}")
    print(f"Word Count: {features_1.word_count}")
    print(f"Avg. Word Length: {features_1.avg_word_length}")
    print(f"Schema Types: {features_1.schema_types_present}")
    
    # Show top 5 keywords
    top_5_keywords = list(features_1.keyword_densities.items())[:5]
    print(f"Top 5 Keywords (density %): {top_5_keywords}")
    
    # 3. Test comparative TF-IDF
    print("\n--- Calculating TF-IDF (KCL vs UCL) ---")
    documents = [
        page_data_1.main_content, 
        page_data_2.main_content
    ]
    
    tfidf_results = calculate_tf_idf(documents)
    
    print(f"Found {len(tfidf_results['top_terms'])} top terms across both docs.")
    
    print("\n--- Top 5 TF-IDF terms for Page 1 (KCL) ---")
    print(json.dumps(tfidf_results['doc_scores'][0][:5], indent=2))
    
    print("\n--- Top 5 TF-IDF terms for Page 2 (UCL) ---")
    print(json.dumps(tfidf_results['doc_scores'][1][:5], indent=2))

    print("\n--- Testing Complete ---")