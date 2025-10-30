# backend/test_search.py

import json
from app.services.search_service import get_search_results

# Get one of the sample queries from Phase 0
TEST_QUERY = "MSc Data Science course UK"

if __name__ == "__main__":
    print(f"--- Testing Search Service ---")
    print(f"Query: '{TEST_QUERY}'")

    results_data = get_search_results(TEST_QUERY, num_results=3)

    print("\n--- Results (JSON Output) ---")
    print(json.dumps(results_data, indent=2))

    print("\n--- Testing Complete ---")

    if results_data["results"]:
        print(f"Successfully found {len(results_data['results'])} results.")
    else:
        print("Could not find any results. This might be due to a CAPTCHA.")