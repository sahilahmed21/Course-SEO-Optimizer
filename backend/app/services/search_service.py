# backend/app/services/search_service.py

import os
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get keys from environment
API_KEY = os.getenv("GOOGLE_API_KEY")
CX = os.getenv("GOOGLE_CX")

# Domains to ignore (Google-owned, social media, trackers, etc.)
BLACKLISTED_DOMAINS = [
    "google.com",
    "youtube.com",
    "facebook.com",
    "twitter.com",
    "linkedin.com",
    "pinterest.com",
    "reddit.com",
    "wikipedia.org",
    "support.google.com",
    "goo.gl",
    "t.co",
]

def get_search_results(query: str, num_results: int = 3) -> dict:
    """
    Fetches Google search results using the official Custom Search JSON API.
    """
    
    logger.info(f"Starting API search for query: '{query}'")

    if not API_KEY or not CX:
        logger.error("GOOGLE_API_KEY or GOOGLE_CX not found in .env file.")
        return {"query": query, "results": []}

    try:
        # Build the service object
        service = build("customsearch", "v1", developerKey=API_KEY)
        
        # Make the API call
        # We ask for more than num_results to have candidates for filtering
        res = service.cse().list(
            q=query,
            cx=CX,
            num=10  # Ask for 10 results to filter from
        ).execute()

    except HttpError as e:
        logger.error(f"Google API HttpError: {e}")
        return {"query": query, "results": []}
    except Exception as e:
        logger.error(f"Google API call failed: {e}")
        return {"query": query, "results": []}

    final_results = []
    seen_domains = set()
    rank = 1

    if 'items' not in res:
        logger.warning(f"No results returned from API for query: '{query}'")
        return {"query": query, "results": []}

    for item in res['items']:
        try:
            url = item['link']
            
            # 1. Parse the URL to get the domain
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace("www.", "")

            # 2. Check against blacklist
            if not domain or domain in BLACKLISTED_DOMAINS:
                logger.info(f"Skipping blacklisted or invalid domain: {url}")
                continue

            # 3. Check for unique domain
            if domain in seen_domains:
                logger.info(f"Skipping duplicate domain: {url}")
                continue

            # 4. If it's a good result, add it
            seen_domains.add(domain)
            
            result_item = {
                "rank": rank,
                "url": url,
                "title": item.get('title', ''),       # We get the title!
                "snippet": item.get('snippet', '')    # We get the snippet!
            }
            
            final_results.append(result_item)
            rank += 1

            # 5. Stop when we have enough results
            if len(final_results) >= num_results:
                break
                
        except Exception as e:
            logger.error(f"Error processing item '{item.get('link')}': {e}")
            continue

    logger.info(f"Found {len(final_results)} valid results.")
    
    return {
        "query": query,
        "results": final_results
    }