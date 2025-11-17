# backend/app/services/llm_engine.py

import os
import json
import logging
from openai import OpenAI
from typing import List, Dict, Any

from app.models.page_data import PageData, ExtractedFeatures
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file.")
    
    client = OpenAI(api_key=api_key)
    MODEL = "gpt-4o-mini" 
    
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    client = None

def _create_compact_summary(page_data: PageData, features: ExtractedFeatures) -> Dict[str, Any]:
    return {
        "url": str(page_data.url),
        "title": page_data.title,
        "meta_description": page_data.meta_description,
        "h1": page_data.h1,
        "word_count": features.word_count,
        "schema_types": features.schema_types_present,
        "top_keywords_with_density": list(features.keyword_densities.items())[:20]
    }

def _build_system_prompt() -> str:
    """
    Defines the new 4-node + final_scores structure.
    Node 6 (QA) is removed. Node 7 is now a top-level 'final_scores' block.
    """
    
    json_structure = """
    {
      "node_1_keywords": {
        "performance_score": 85,
        "must_have_keywords": ["keyword 1", "keyword 2", "keyword 3", "keyword 4"],
        "trending_keywords": ["trending 1", "trending 2", "trending 3", "trending 4"]
      },
      "node_2_competitors": {
        "top_competitors": [
          {
            "rank": 1, 
            "url": "https://example.com/course",
            "name": "University of Example", 
            "top_keywords": ["keyword a", "keyword b"],
            "differentiator": "Focuses heavily on 'career placements'."
          }
        ]
      },
      "node_3_content_rewrite": {
        "title": "BA (Hons) Example Title",
        "empower_paragraph": "A new, rewritten introductory paragraph.",
        "why_choose_points": [
          "Career-ready skills: A bullet point about skills.",
          "Accredited for success: A bullet point about accreditation."
        ],
        "seo_score": 92
      },
      "node_5_metadata": {
        "meta_title": "Optimized Meta Title",
        "meta_description": "Optimized meta description, 155 characters.",
        "meta_keywords": ["keyword 1", "keyword 2", "keyword 3", "keyword 4"]
      },
      "final_scores": {
        "final_seo_score": 92,
        "final_readability": 89,
        "engagement_lift": 67,
        "avg_rank_improvement": 43
      }
    }
    """
    
    return f"""
    You are an expert SEO analyst. Your task is to compare a 'Target' course page against its 'Competitors'.
    Analyze the provided data and generate a comprehensive SEO report.
    
    RULES:
    1.  Base all analysis ONLY on the data provided.
    2.  For 'node_1_keywords', generate "must-have" and "trending" keywords. Estimate a "performance_score" (0-100).
    3.  For 'node_2_competitors', analyze each competitor. 'name' is their page title. 'top_keywords' are 2-3 of their most important keywords. 'differentiator' is a 1-sentence analysis.
    4.  For 'node_3_content_rewrite', rewrite the target's content. Generate a new title, a 2-sentence intro paragraph, and 3-4 "Why Choose This Course" bullet points. Estimate an "seo_score" (0-100).
    5.  For 'node_5_metadata', generate an optimized meta title, description, and 4 meta keywords.
    6.  For 'final_scores', **estimate** all 4 scores (0-100) for the target page.
    7.  Your response MUST be a single, valid JSON object following this exact structure: {json_structure}
    """

def get_llm_recommendations(target_page: PageData, target_features: ExtractedFeatures, competitor_pages: List[PageData], competitor_features: List[ExtractedFeatures]) -> Dict[str, Any]:
    if not client:
        return {"error": "OpenAI client not initialized."}

    logger.info(f"Generating NEW 4-node report for target: {target_page.url}")

    target_summary = _create_compact_summary(target_page, target_features)
    
    competitor_data_for_prompt = []
    for i, page in enumerate(competitor_pages):
        if i < len(competitor_features):
            competitor_data_for_prompt.append({
                "rank": i + 1,
                "url": str(page.url),
                "title": page.title,
                "summary": _create_compact_summary(page, competitor_features[i])
            })
    
    user_prompt = f"""
    Here is the data for analysis:

    **Target Page:**
    {json.dumps(target_summary, indent=2)}

    **Competitor Data:**
    {json.dumps(competitor_data_for_prompt, indent=2)}

    Please provide the full SEO analysis in the required JSON format.
    Fill in all nodes (1, 2, 3, 5) and the final_scores block as requested.
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
            temperature=0.5, 
        )
        
        response_content = response.choices[0].message.content
        report_json = json.loads(response_content)
        
        logger.info(f"Successfully generated NEW 4-node report for {target_page.url}")
        return report_json

    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return {"error": f"Failed to get LLM response: {e}"}