from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.annotation import Annotation, AnnotationType

router = APIRouter()

class AnnotationCreate(BaseModel):
    type: AnnotationType
    name: Optional[str] = None
    geometry_geojson: dict
    properties_json: Optional[dict] = None
    notes: Optional[str] = None
    visible: bool = True

class AnnotationUpdate(BaseModel):
    name: Optional[str] = None
    geometry_geojson: Optional[dict] = None
    properties_json: Optional[dict] = None
    notes: Optional[str] = None
    visible: Optional[bool] = None

class AnnotationResponse(BaseModel):
    id: str
    project_id: str
    type: AnnotationType
    name: Optional[str]
    geometry_geojson: dict
    properties_json: Optional[dict]
    notes: Optional[str]
    visible: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/{id}/annotations", response_model=AnnotationResponse, status_code=status.HTTP_201_CREATED)
async def create_annotation(id: str, annotation: AnnotationCreate, db: AsyncSession = Depends(get_db)):
    """Create a new annotation"""
    db_ann = Annotation(project_id=id, **annotation.model_dump())
    db.add(db_ann)
    await db.commit()
    await db.refresh(db_ann)
    return db_ann

@router.get("/{id}/annotations", response_model=List[AnnotationResponse])
async def list_annotations(id: str, db: AsyncSession = Depends(get_db)):
    """List annotations"""
    result = await db.execute(select(Annotation).where(Annotation.project_id == id))
    return result.scalars().all()

@router.put("/{id}/annotations/{aid}", response_model=AnnotationResponse)
async def update_annotation(id: str, aid: str, update_data: AnnotationUpdate, db: AsyncSession = Depends(get_db)):
    """Update annotation"""
    ann = await db.get(Annotation, aid)
    if not ann or ann.project_id != id:
        raise HTTPException(status_code=404, detail="Annotation not found")
        
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(ann, key, value)
        
    await db.commit()
    await db.refresh(ann)
    return ann

@router.delete("/{id}/annotations/{aid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_annotation(id: str, aid: str, db: AsyncSession = Depends(get_db)):
    """Delete annotation"""
    ann = await db.get(Annotation, aid)
    if not ann or ann.project_id != id:
        raise HTTPException(status_code=404, detail="Annotation not found")
    await db.delete(ann)
    await db.commit()
