# backend/app/services/llm_engine.py

import os
import json
import logging
from openai import OpenAI
from typing import List, Dict, Any

from app.models.page_data import PageData, ExtractedFeatures # Absolute import
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env file and initialize OpenAI client
load_dotenv()
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file.")
    
    client = OpenAI(api_key=api_key)
    # Use a cost-effective and fast model that supports JSON mode
    MODEL = "gpt-3.5-turbo-0125" 
    # You can swap this for "gpt-4o-mini" or "gpt-4-turbo" for more power
    
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    client = None

def _create_compact_summary(page_data: PageData, features: ExtractedFeatures) -> Dict[str, Any]:
    """
    Creates a compact dictionary summary of a page to be fed to the LLM.
    This keeps our token usage low.
    """
    return {
        "url": str(page_data.url),
        "title": page_data.title,
        "meta_description": page_data.meta_description,
        "h1": page_data.h1,
        "top_headings": list(features.keyword_densities.keys()), # <-- THE FIX IS HERE
        "word_count": features.word_count,
        "schema_types": features.schema_types_present,
        "top_keywords": list(features.keyword_densities.items())[:20] 
    }
def _build_system_prompt() -> str:
    """Defines the role and expected JSON output format for the LLM."""
    
    # This structure is based on your Phase 5 and Phase 6 deliverables
    json_structure = """
    {
      "seo_score": {
        "score": 0,
        "explanation": "A brief 1-2 sentence rationale for the score."
      },
      "top_missing_keywords": [
        {"keyword": "example keyword 1", "reason": "Competitors rank for this."},
        {"keyword": "example keyword 2", "reason": "High intent search term."}
      ],
      "quick_wins": [
        {"type": "Metadata", "priority": "High", "suggestion": "Update meta title to be..."},
        {"type": "Content", "priority": "Medium", "suggestion": "Add a new H2 section about..."},
        {"type": "Schema", "priority": "Low", "suggestion": "Implement FAQPage schema."}
      ],
      "suggested_meta": {
        "title": "A new, optimized meta title.",
        "description": "A new, optimized meta description."
      },
      "suggested_outline": [
        "H1: Optimized H1 Tag",
        "H2: Key Topic 1 (e.g., Course Modules)",
        "H2: Key Topic 2 (e.g., Entry Requirements)",
        "H2: Key Topic 3 (e.g., Fees and Funding)",
        "H2: Call to Action (e.g., Apply Now)"
      ],
      "sample_paragraph": "A 150-word sample paragraph optimized for the missing keywords. This text should be well-written, engaging, and informative.",
      "faq_schema_suggestions": [
        {"question": "What are the entry requirements?", "answer": "You need a 2:1 degree in a related field..."},
        {"question": "What is the course duration?", "answer": "1 year full-time or 2 years part-time."}
      ]
    }
    """
    
    return f"""
    You are an expert SEO analyst specializing in the education sector. Your task is to compare a 'Target' course page against its 'Competitors'.
    Analyze the provided structured data (titles, word counts, keywords, schema).
    
    RULES:
    1.  Provide concise, actionable advice.
    2.  Base all analysis ONLY on the data provided. Do not invent facts.
    3.  Your response MUST be a single, valid JSON object.
    4.  Follow this exact JSON structure: {json_structure}
    """

def get_llm_recommendations(target_page: PageData, target_features: ExtractedFeatures, competitor_pages: List[PageData], competitor_features: List[ExtractedFeatures]) -> Dict[str, Any]:
    """
    The main function for Phase 5.
    Takes scraped data, formats it, and gets SEO recommendations from the LLM.
    """
    if not client:
        return {"error": "OpenAI client not initialized."}

    logger.info(f"Generating LLM recommendations for target: {target_page.url}")

    # Create compact summaries
    target_summary = _create_compact_summary(target_page, target_features)
    competitor_summaries = [
        _create_compact_summary(cp, cf) 
        for cp, cf in zip(competitor_pages, competitor_features)
    ]
    
    # Build the user prompt
    user_prompt = f"""
    Here is the data for analysis:

    **Target Page:**
    {json.dumps(target_summary, indent=2)}

    **Competitor Pages:**
    {json.dumps(competitor_summaries, indent=2)}

    Please provide the full SEO analysis in the required JSON format.
    """
    
    system_prompt = _build_system_prompt()
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5, # Keep it factual
        )
        
        response_content = response.choices[0].message.content
        report_json = json.loads(response_content)
        
        logger.info(f"Successfully generated LLM report for {target_page.url}")
        return report_json

    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return {"error": f"Failed to get LLM response: {e}"}