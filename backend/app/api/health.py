import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
from app.config import settings

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    version: str

class SolversHealthResponse(BaseModel):
    vpmm2d: bool
    diffwave: bool
    delft3d: bool
    dualsphysics: bool

class GEEHealthResponse(BaseModel):
    configured: bool

@router.get("", response_model=HealthResponse)
async def check_health():
    """Returns system status"""
    return HealthResponse(status="ok", version="1.0.0")

@router.get("/solvers", response_model=SolversHealthResponse)
async def check_solvers():
    """Checks each solver availability"""
    return SolversHealthResponse(
        vpmm2d=True,
        diffwave=True,
        delft3d=bool(settings.DELFT3D_PATH and os.path.exists(settings.DELFT3D_PATH)),
        dualsphysics=bool(settings.DUALSPHYSICS_PATH and os.path.exists(settings.DUALSPHYSICS_PATH))
    )

@router.get("/gee", response_model=GEEHealthResponse)
async def check_gee():
    """Check GEE credentials"""
    configured = bool(settings.GEE_CREDENTIALS_FILE and os.path.exists(settings.GEE_CREDENTIALS_FILE))
    return GEEHealthResponse(configured=configured)
