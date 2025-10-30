# backend/test_llm.py

import json
import logging
from app.services.llm_engine import get_llm_recommendations
from app.models.page_data import PageData, ExtractedFeatures

# Set logging level higher for a cleaner test output
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("app")
logger.setLevel(logging.WARNING)

if __name__ == "__main__":
    print(f"--- Testing LLM Engine (Phase 5) ---")
    
    # --- Create Mock Data (with corrected https:// URLs) ---
    
    # Mock Target Page (Our Page)
    target_pd = PageData(
        url="https://my-university.com/msc-data-course",  # <-- FIXED
        status_code=200,
        title="MSc Data Course | My University",
        meta_description="Our new MSc in Data.",
        h1="MSc Data Course",
        word_count=300,
        json_ld=[{"@type": "Course"}]
    )
    target_ft = ExtractedFeatures(
        url="https://my-university.com/msc-data-course",  # <-- FIXED
        word_count=300,
        keyword_densities={"data": 2.0, "course": 1.5, "apply": 1.0},
        schema_types_present=["Course"]
    )
    
    # Mock Competitor 1
    comp1_pd = PageData(
        url="https://big-uni.com/data-science-masters",  # <-- FIXED
        status_code=200,
        title="Data Science Masters (MSc) | Big University",
        meta_description="Join our world-leading Data Science MSc. Learn machine learning, AI, and big data.",
        h1="Masters in Data Science",
        word_count=1200,
        json_ld=[{"@type": "Course"}, {"@type": "FAQPage"}]
    )
    comp1_ft = ExtractedFeatures(
        url="https://big-uni.com/data-science-masters",  # <-- FIXED
        word_count=1200,
        keyword_densities={"data science": 3.0, "machine learning": 2.5, "ai": 2.0, "modules": 1.5},
        schema_types_present=["Course", "FAQPage"]
    )

    # Mock Competitor 2
    comp2_pd = PageData(
        url="https://top-uni.edu/msc-data-analytics",  # <-- FIXED
        status_code=200,
        title="MSc Data Analytics | Top Uni",
        meta_description="Our MSc in Data Analytics prepares you for a career in business intelligence and data analysis.",
        h1="MSc Data Analytics",
        word_count=1000,
        json_ld=[{"@type": "Course"}, {"@type": "BreadcrumbList"}]
    )
    comp2_ft = ExtractedFeatures(
        url="https://top-uni.edu/msc-data-analytics",  # <-- FIXED
        word_count=1000,
        keyword_densities={"data analytics": 2.8, "business intelligence": 2.2, "career": 1.8, "modules": 1.2},
        schema_types_present=["Course", "BreadcrumbList"]
    )
    # --- End Mock Data ---

    print("Sending mock data to OpenAI API... (This may take 10-20 seconds)")
    
    # Run the LLM engine
    report = get_llm_recommendations(
        target_page=target_pd,
        target_features=target_ft,
        competitor_pages=[comp1_pd, comp2_pd],
        competitor_features=[comp1_ft, comp2_ft] # <-- This is the fix
    )

    print("\n--- LLM JSON Response ---")
    if "error" in report:
        print(f"Error: {report['error']}")
    else:
        # Print the full, structured JSON report
        print(json.dumps(report, indent=2))
        print("\n--- Test Complete ---")
        print(f"Successfully received SEO score: {report.get('seo_score', {}).get('score')}")