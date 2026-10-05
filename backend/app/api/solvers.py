from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import os

from app.config import settings

router = APIRouter()

class SolverInfo(BaseModel):
    name: str
    tier: str
    available: bool
    version: str
    reason_unavailable: str = ""

@router.get("", response_model=List[SolverInfo])
async def list_solvers():
    """List all solver tiers with availability"""
    solvers = [
        SolverInfo(
            name="VPMM2D",
            tier="T1_VPMM",
            available=True,
            version="1.0.0"
        ),
        SolverInfo(
            name="DiffWave",
            tier="T1_DIFFWAVE",
            available=True,
            version="1.0.0"
        ),
        SolverInfo(
            name="Delft3D",
            tier="T2_DELFT3D",
            available=bool(settings.DELFT3D_PATH and os.path.exists(settings.DELFT3D_PATH)),
            version="4.04",
            reason_unavailable="DELFT3D_PATH not configured" if not settings.DELFT3D_PATH else ""
        ),
        SolverInfo(
            name="DualSPHysics",
            tier="T3_SPH",
            available=bool(settings.DUALSPHYSICS_PATH and os.path.exists(settings.DUALSPHYSICS_PATH)),
            version="5.0",
            reason_unavailable="DUALSPHYSICS_PATH not configured" if not settings.DUALSPHYSICS_PATH else ""
        )
    ]
    return solvers
