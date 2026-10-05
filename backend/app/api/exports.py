from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class ExportRequest(BaseModel):
    format: str # shp, kml, geojson, geotiff, csv, pdf
    layers: List[str]

class ExportResponse(BaseModel):
    export_id: str
    status: str
    download_url: Optional[str] = None

@router.post("/projects/{id}/runs/{rid}/export", response_model=ExportResponse)
async def create_export(id: str, rid: str, req: ExportRequest):
    """Export results in specified format"""
    return ExportResponse(export_id="export_123", status="PENDING")

@router.get("/projects/{id}/exports", response_model=List[ExportResponse])
async def list_exports(id: str):
    """List exports"""
    return []

@router.get("/exports/{eid}/download")
async def download_export(eid: str):
    """Download export file"""
    raise HTTPException(status_code=404, detail="Export not ready")
