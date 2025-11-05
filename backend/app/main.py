# backend/app/main.py

import uuid
import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

# Import our new API models
from app.models.api_models import AnalyzeRequest, AnalyzeResponse, ReportStatusResponse

# Import all our services
from app.services import search_service
from app.services import scraper
from app.services import features
from app.services import llm_engine
from app.models.page_data import PageData, ExtractedFeatures

# --- App Setup ---

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SEO Optimizer API",
    description="Analyzes a target URL against competitors for a search query.",
    version="1.0.0"
)

# --- CORS Middleware ---
# This allows our React frontend (running on a different port)
# to communicate with this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For demo, allow all. In production, restrict.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Job Store ---
# A simple in-memory dictionary to store job status.
# For a real app, you'd use a database (Redis, SQL, etc.)
job_store: Dict[str, ReportStatusResponse] = {}

# --- The Main Workflow (Run in Background) ---

def run_analysis_workflow(job_id: str, query: str, target_url: str):
    """
    This is the core function that runs all our phases.
    It will be executed in the background.
    """
    try:
        # Update job status
        job_store[job_id].status = "RUNNING"
        logger.info(f"Job {job_id}: Workflow started. Query: '{query}', Target: {target_url}")

        # --- Phase 1: Search ---
        logger.info(f"Job {job_id}: Starting Phase 1 (Search)")
        search_results = search_service.get_search_results(query, num_results=3)
        if not search_results.get("results"):
            raise Exception("Phase 1 failed: No search results found.")
        
        competitor_urls = [r["url"] for r in search_results["results"]]
        logger.info(f"Job {job_id}: Found competitors: {competitor_urls}")

        # --- Phase 2 & 3: Scrape ---
        logger.info(f"Job {job_id}: Starting Phase 2/3 (Scraping)")
        
        # Scrape target page
        target_page = scraper.scrape_page(target_url)
        if target_page.error:
            logger.warning(f"Job {job_id}: Target page scrape failed: {target_page.error}. Continuing...")
            # We can still analyze competitors

        # Scrape competitor pages
        competitor_pages: List[PageData] = []
        for url in competitor_urls:
            page = scraper.scrape_page(url)
            if not page.error:
                competitor_pages.append(page)
            else:
                logger.warning(f"Job {job_id}: Competitor scrape failed: {url}. Skipping.")
        
        if not competitor_pages:
             raise Exception("Phase 2 failed: Could not scrape any competitor pages.")

        # --- Phase 4: Feature Extraction ---
        logger.info(f"Job {job_id}: Starting Phase 4 (Feature Extraction)")
        
        all_pages = [target_page] + competitor_pages
        all_features: List[ExtractedFeatures] = []
        all_content: List[str] = []

        for page in all_pages:
            if not page.error:
                all_features.append(features.extract_features_from_page(page))
                all_content.append(page.main_content or "")
            else:
                # Add empty placeholders if scrape failed
                all_features.append(ExtractedFeatures(url=str(page.url), word_count=0))
                all_content.append("")

        target_features = all_features[0]
        competitor_features = all_features[1:]
        
        # Note: We won't use TF-IDF for this demo to simplify the LLM prompt,
        # as keyword density is already a very strong signal.

        # --- Phase 5: LLM Comparison ---
        logger.info(f"Job {job_id}: Starting Phase 5 (LLM Analysis)")
        
        report = llm_engine.get_llm_recommendations(
            target_page=target_page,
            target_features=target_features,
            competitor_pages=competitor_pages,
            competitor_features=competitor_features
        )
        
        if "error" in report:
            raise Exception(f"Phase 5 failed: {report['error']}")

        # --- Phase 6: Report Complete ---
        logger.info(f"Job {job_id}: Workflow complete. Storing report.")
        job_store[job_id].status = "COMPLETE"
        job_store[job_id].report = report

    except Exception as e:
        logger.error(f"Job {job_id}: Workflow failed. Error: {e}")
        job_store[job_id].status = "FAILED"
        job_store[job_id].error = str(e)


# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "SEO Optimizer API is running."}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Triggers a new analysis job.
    This returns a job ID immediately and runs the analysis in the background.
    """
    job_id = str(uuid.uuid4())
    
    # Create the initial job entry
    job_store[job_id] = ReportStatusResponse(
        job_id=job_id,
        status="PENDING",
    )
    
    # Add the long-running task to the background
    background_tasks.add_task(
        run_analysis_workflow,
        job_id,
        request.query,
        str(request.target_url)
    )
    
    logger.info(f"Job {job_id}: Created and queued.")
    
    return AnalyzeResponse(
        job_id=job_id,
        status="PENDING",
        message="Analysis has been queued."
    )

@app.get("/results/{job_id}", response_model=ReportStatusResponse)
async def get_results(job_id: str):
    """
    Polls for the results of an analysis job.
    """
    job = job_store.get(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
        
    logger.info(f"Job {job_id}: Status check. Current status: {job.status}")
    
    return job