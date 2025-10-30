# backend/app/services/scraper.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
from app.models.page_data import PageData
from app.services import extractor
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Re-use the User-Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _parse_html(url: str, html: str, status_code: int) -> PageData:
    """
    Internal function to parse HTML using BeautifulSoup and our extractor.
    This is re-used by both simple and playwright scrapers.
    """
    try:
        soup = BeautifulSoup(html, 'lxml')

        # 1. Extract all headings at once
        all_headings = extractor.extract_headings(soup)
        
        # 2. Get the first H1 from the list, if it exists
        first_h1 = ""
        if 'h1' in all_headings and all_headings['h1']:
            first_h1 = all_headings['h1'][0]

        # 3. Use extractor functions
        main_content = extractor.extract_main_content(soup)
        word_count = len(main_content.split())
        
        page_data = PageData(
            url=url,
            status_code=status_code,
            title=extractor.extract_title(soup),
            meta_description=extractor.extract_meta_description(soup),
            meta_keywords=extractor.extract_meta_keywords(soup),
            canonical_url=extractor.extract_canonical_url(soup),
            h1=first_h1,
            headings=all_headings,
            main_content=main_content,
            word_count=word_count,
            json_ld=extractor.extract_json_ld(soup),
            links=extractor.extract_links(soup),
            image_alt_texts=extractor.extract_image_alt_texts(soup)
        )
        return page_data
    except Exception as e:
        logger.error(f"Failed to parse HTML for {url}. Error: {e}")
        return PageData(url=url, status_code=status_code, error=f"HTML parsing error: {e}")

def _scrape_with_playwright(url: str) -> PageData:
    """
    Scrapes a single page using the "Fallback" (Playwright) method.
    """
    logger.info(f"Using Playwright fallback for: {url}")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=USER_AGENT)
            
            # Wait for the page to be fully loaded
            response = page.goto(url, wait_until='networkidle', timeout=15000)
            
            html = page.content()
            status_code = response.status if response else 0
            
            browser.close()

            if status_code != 200:
                 logger.error(f"Playwright failed to load {url}. Status: {status_code}")
                 return PageData(url=url, status_code=status_code, error=f"Playwright received status {status_code}")

            logger.info(f"Playwright successfully fetched: {url}")
            # Now, parse the HTML
            return _parse_html(url=url, html=html, status_code=status_code)

    except PlaywrightTimeoutError:
        logger.error(f"Playwright timeout while scraping {url}")
        return PageData(url=url, status_code=408, error="Playwright timeout")
    except Exception as e:
        logger.error(f"Playwright unexpected error for {url}. Error: {e}")
        return PageData(url=url, status_code=500, error=f"Playwright error: {e}")

def scrape_page(url: str) -> PageData:
    """
    Scrapes a single page. Tries "Simple" (requests) first,
    then falls back to "Robust" (Playwright) if needed.
    """
    logger.info(f"Starting scrape for URL: {url}")
    
    headers = {
        'User-Agent': USER_AGENT,
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive'
    }

    try:
        # --- SIMPLE ATTEMPT (requests) ---
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        page_data = _parse_html(url=url, html=response.text, status_code=response.status_code)

        # CHECK for signs of a JS-heavy page (e.g., bot block or empty body)
        if page_data.word_count < 100 and (page_data.h1 is None or page_data.h1 == ""):
             logger.warning(f"Low word count ({page_data.word_count})... possible JS page. Retrying with Playwright.")
             return _scrape_with_playwright(url)
        
        logger.info(f"Successfully scraped with 'simple' method: {url}")
        return page_data

    except requests.exceptions.HTTPError as e:
        # A 4xx or 5xx error is a perfect reason to try Playwright
        logger.warning(f"Simple scrape failed for {url} with HTTP error {e.response.status_code}. Trying Playwright.")
        return _scrape_with_playwright(url)
        
    except requests.exceptions.RequestException as e:
        # Other network errors (timeout, connection error)
        logger.error(f"Simple scrape failed for {url} ({e}). Trying Playwright.")
        return _scrape_with_playwright(url)
        
    except Exception as e:
        logger.error(f"An unexpected error occurred with simple scrape {url}. Error: {e}. Trying Playwright.")
        return _scrape_with_playwright(url)