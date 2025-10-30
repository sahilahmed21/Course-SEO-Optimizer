from pydantic import BaseModel,HttpUrl
from typing import Optional,List,Any,Dict

class PageData(BaseModel):
    """Pydantic model to structure the scraped page data.
    This ensures all scraped data is clean and typed.

    """
    
    url:HttpUrl
    status_code:int
    
    #core meta 
    
    title :Optional[str]=""
    meta_description :Optional[str]=""
    meta_keywords :Optional[str]=""
    canonical_url: Optional[str] = ""

    h1: Optional[str] = ""
    headings: Dict[str, List[str]] = {}  # e.g., {"h1": ["Main title"], "h2": ["Subtopic 1", "Subtopic 2"]}
    main_content: Optional[str] = ""
    word_count: int = 0
    
    json_ld: List[Dict[str, Any]] = []
    links: List[Dict[str, str]] = []  # [{"text": "Home", "href": "/"}]
    image_alt_texts: List[str] = []


    # Simple Metrics (from plan)
    # We will compute these in a later phase, but define them here
    readability_scores: Dict[str, float] = {}
    
    # Error message if scraping failed
    error: Optional[str] = None
    
    # --- ADD THIS NEW CLASS AT THE BOTTOM ---
class ExtractedFeatures(BaseModel):
    """
    Pydantic model for the features extracted from a PageData object.
    This is the deliverable for Phase 4.
    """
    url: str
    word_count: int
    
    # Top 50 1-3 grams and their densities
    keyword_densities: Dict[str, float] = {}
    
    # Simple Metrics
    avg_word_length: float = 0.0
    
    # Schema
    schema_types_present: List[str] = []