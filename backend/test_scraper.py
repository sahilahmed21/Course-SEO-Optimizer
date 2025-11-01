# backend/test_scraper.py

import json
from app.services.scraper import scrape_page
from app.models.page_data import PageData

# Use one of the URLs from our Phase 1 test
TEST_URL = "https://www.realtor.com/realestateandhomes-detail/M55554-01683"
# TEST_URL = "https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees/data-science-msc"

if __name__ == "__main__":
    print(f"--- Testing Scraper Service ---")
    print(f"Scraping URL: {TEST_URL}")
    
    page_data = scrape_page(TEST_URL)
    
    print(f"\n--- Scrape Status ---")
    print(f"URL: {page_data.url}")
    print(f"Status Code: {page_data.status_code}")
    print(f"Error: {page_data.error}")

    if page_data.error is None:
        print("\n--- Extracted Data (Sample) ---")
        print(f"Title: {page_data.title}")
        print(f"Meta Desc: {page_data.meta_description[:70]}...")
        print(f"H1: {page_data.h1}")
        print(f"Word Count: {page_data.word_count}")
        print(f"Found H2s: {len(page_data.headings.get('h2', []))}")
        print(f"Found JSON-LD Schemas: {len(page_data.json_ld)}")
        
        # Uncomment this to see the full JSON
        print("\n--- Full JSON Output ---")
        print(page_data.model_dump_json(indent=2))

    print("\n--- Testing Complete ---")