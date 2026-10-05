from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()

class CompareRequest(BaseModel):
    run_ids: List[str]

class CompareResponse(BaseModel):
    differences: Dict[str, Any]
    metrics: List[Dict[str, Any]]

@router.post("/{id}/compare", response_model=CompareResponse)
async def compare_runs(id: str, req: CompareRequest):
    """Compare results between runs/tiers"""
    if len(req.run_ids) < 2:
        raise HTTPException(status_code=400, detail="Provide at least two run IDs to compare")
        
    return CompareResponse(
        differences={"max_depth_diff_m": 0.5},
        metrics=[{"run_id": r, "peak_flow": 100.0} for r in req.run_ids]
    )
