# backend/test_api.py
import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

TEST_DATA = {
    "target_url": "https://www.mygreatcourse.com/msc-data-analytics", # A dummy URL
    "query": "MSc Data Science course UK"
}

def run_test():
    # --- 1. Start the Job ---
    print(f"--- Starting analysis for: {TEST_DATA['query']} ---")
    
    try:
        response = requests.post(f"{BASE_URL}/analyze", json=TEST_DATA)
        response.raise_for_status() # Raise error for bad status
        
        job_data = response.json()
        job_id = job_data.get("job_id")
        
        if not job_id:
            print("Error: Did not receive job_id.")
            return

        print(f"Job created successfully! Job ID: {job_id}")
        print(f"Polling for results...\n")
        
        # --- 2. Poll for Results ---
        status = ""
        while status not in ["COMPLETE", "FAILED"]:
            time.sleep(10) # Wait 10 seconds between checks
            
            try:
                poll_response = requests.get(f"{BASE_URL}/results/{job_id}")
                poll_response.raise_for_status()
                
                result_data = poll_response.json()
                status = result_data.get("status")
                print(f"Job Status: {status}")

            except requests.exceptions.RequestException as e:
                print(f"Polling failed: {e}")
                status = "FAILED"
        
        # --- 3. Print Final Report ---
        if status == "COMPLETE":
            print("\n--- Analysis Complete! ---")
            report = result_data.get("report")
            print(json.dumps(report, indent=2))
        else:
            print("\n--- Analysis Failed ---")
            print(f"Error: {result_data.get('error')}")
            
    except requests.exceptions.HTTPError as e:
        print(f"Error starting job: {e.response.status_code}")
        print(f"Response body: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    run_test()