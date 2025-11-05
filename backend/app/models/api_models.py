from pydantic import BaseModel,HttpUrl
from typing import List, Dict, Any,Optional

class AnalyzeRequest (BaseModel):
    """The request model for the /analyze endpoint"""
    target_url: HttpUrl
    query:str
    
class AnalyzeResponse (BaseModel):
    """The response model for the /analyze endpoint"""
    job_id:str
    status:str
    message:str

class ReportStatusResponse(BaseModel):
    """The response model for the /results/{job_id} endpoint"""
    job_id: str
    status: str  # "PENDING", "RUNNING", "COMPLETE", "FAILED"
    report: Optional[Dict[str, Any]] = None # This will hold the LLM JSON
    error: Optional[str] = None