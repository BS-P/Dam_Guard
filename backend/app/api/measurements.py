from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Any
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.measurement import Measurement, MeasurementType

router = APIRouter()

class MeasurementCreate(BaseModel):
    run_id: Optional[str] = None
    type: MeasurementType
    geometry_geojson: dict
    name: Optional[str] = None
    notes: Optional[str] = None

class MeasurementResponse(BaseModel):
    id: str
    project_id: str
    run_id: Optional[str]
    type: MeasurementType
    geometry_geojson: dict
    results_json: Optional[dict]
    name: Optional[str]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/{id}/measurements", response_model=MeasurementResponse, status_code=status.HTTP_201_CREATED)
async def create_measurement(id: str, measurement: MeasurementCreate, db: AsyncSession = Depends(get_db)):
    """Create a new measurement"""
    db_meas = Measurement(project_id=id, **measurement.model_dump())
    db.add(db_meas)
    await db.commit()
    await db.refresh(db_meas)
    return db_meas

@router.get("/{id}/measurements", response_model=List[MeasurementResponse])
async def list_measurements(id: str, db: AsyncSession = Depends(get_db)):
    """List measurements"""
    result = await db.execute(select(Measurement).where(Measurement.project_id == id))
    return result.scalars().all()

@router.delete("/{id}/measurements/{mid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_measurement(id: str, mid: str, db: AsyncSession = Depends(get_db)):
    """Delete measurement"""
    meas = await db.get(Measurement, mid)
    if not meas or meas.project_id != id:
        raise HTTPException(status_code=404, detail="Measurement not found")
    await db.delete(meas)
    await db.commit()
