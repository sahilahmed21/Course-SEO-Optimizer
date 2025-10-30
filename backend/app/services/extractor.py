import json
from bs4 import BeautifulSoup
from typing import List,Dict,Any,Optional
import re


def clean_text(text:str)->str:
    """ a simple text cleaner to remove extra whitespace and newlines """
    return re.sub(r'\s+', ' ', text).strip()


def extract_title(soup:BeautifulSoup)->Optional[str]:
    try:
        return soup.title.string if soup.title else None
    except Exception:
        return None
    
    
def extract_meta_description(soup:BeautifulSoup)->Optional[str]:
    try:
        meta = soup.find('meta', attrs={'name':'description'})
        if meta:
            return meta.get('content', '').strip()
    except Exception:
        return None
    
def extract_meta_keywords(soup: BeautifulSoup) -> Optional[str]:
    try:
        meta = soup.find('meta', attrs={'name': 'keywords'})
        if meta:
            return meta.get('content', '').strip()
    except Exception:
        return None
    return None

def extract_canonical_url(soup: BeautifulSoup) -> Optional[str]:
    try:
        link = soup.find('link', attrs={'rel': 'canonical'})
        if link:
            return link.get('href', '').strip()
    except Exception:
        return None
    return None

def extract_h1(soup: BeautifulSoup) -> Optional[str]:
    """
    Finds the first <h1> tag with text.
    """
    try:
        h1_tags = soup.find_all('h1')
        for h1 in h1_tags:
            text = clean_text(h1.get_text())
            if text:
                return text  # Return the first one that's not empty
        return None # No H1s had text
    except Exception:
        return None
def extract_headings(soup: BeautifulSoup) -> Dict[str, List[str]]:
    headings = {"h1": [], "h2": [], "h3": [], "h4": [], "h5": [], "h6": []}
    try:
        for tag in headings.keys():
            found_tags = soup.find_all(tag)
            for h in found_tags:
                headings[tag].append(clean_text(h.get_text()))
    except Exception:
        pass
    return headings

def extract_main_content(soup: BeautifulSoup) -> str:
    """
    Tries to find the main content, falling back to body.
    Removes nav and footer for cleaner text.
    """
    try:
        # Try <main> tag
        main_content = soup.find('main')
        
        if not main_content:
            # Fallback to <body>
            main_content = soup.body

        if not main_content:
            return ""

        # Remove common noise
        for tag in main_content(['nav', 'footer', 'header', 'script', 'style', 'aside']):
            tag.decompose()

        return clean_text(main_content.get_text())
    except Exception:
        return ""

def extract_json_ld(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    json_ld_scripts = []
    try:
        scripts = soup.find_all('script', attrs={'type': 'application/ld+json'})
        for script in scripts:
            try:
                data = json.loads(script.string)
                json_ld_scripts.append(data)
            except json.JSONDecodeError:
                continue
    except Exception:
        pass
    return json_ld_scripts

def extract_links(soup: BeautifulSoup) -> List[Dict[str, str]]:
    links = []
    try:
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Avoid internal anchors and javascript links
            if href and not href.startswith(('#', 'javascript:')):
                links.append({
                    "text": clean_text(a.get_text()),
                    "href": href
                })
    except Exception:
        pass
    return links

def extract_image_alt_texts(soup: BeautifulSoup) -> List[str]:
    alt_texts = []
    try:
        for img in soup.find_all('img'):
            alt = img.get('alt')
            if alt:
                alt_texts.append(clean_text(alt))
    except Exception:
        pass
    return alt_texts