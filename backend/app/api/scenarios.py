from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.scenario import Scenario, BreachMode, BreachMethod

router = APIRouter()

class ScenarioCreate(BaseModel):
    name: str
    breach_mode: BreachMode
    breach_method: BreachMethod
    breach_params: Optional[dict] = None
    initial_water_level_m: Optional[float] = None
    inflow_hydrograph_json: Optional[dict] = None
    manning_n_default: Optional[float] = None
    roughness_source: Optional[str] = None

class ScenarioResponse(BaseModel):
    id: str
    project_id: str
    name: str
    breach_mode: BreachMode
    breach_method: BreachMethod
    breach_params: Optional[dict]
    initial_water_level_m: Optional[float]
    inflow_hydrograph_json: Optional[dict]
    manning_n_default: Optional[float]
    roughness_source: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/{id}/scenarios", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario(id: str, scenario: ScenarioCreate, db: AsyncSession = Depends(get_db)):
    """Create a new scenario for a project"""
    db_scenario = Scenario(project_id=id, **scenario.model_dump())
    db.add(db_scenario)
    await db.commit()
    await db.refresh(db_scenario)
    return db_scenario

@router.get("/{id}/scenarios", response_model=List[ScenarioResponse])
async def list_scenarios(id: str, db: AsyncSession = Depends(get_db)):
    """List scenarios for a project"""
    result = await db.execute(select(Scenario).where(Scenario.project_id == id))
    return result.scalars().all()

@router.get("/{id}/scenarios/{sid}", response_model=ScenarioResponse)
async def get_scenario(id: str, sid: str, db: AsyncSession = Depends(get_db)):
    """Get scenario details"""
    scenario = await db.get(Scenario, sid)
    if not scenario or scenario.project_id != id:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario
