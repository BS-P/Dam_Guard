import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.project import Project, Dataset, DatasetType
from app.config import settings

router = APIRouter()

class DatasetResponse(BaseModel):
    id: str
    project_id: str
    name: str
    type: DatasetType
    file_path: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/{id}/upload", response_model=DatasetResponse)
async def upload_dataset(
    id: str,
    file: UploadFile = File(...),
    dataset_type: DatasetType = Form(...),
    name: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload DEM/data file, validate format, store metadata"""
    project = await db.get(Project, id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    project_data_dir = settings.DATA_DIR / id
    project_data_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = project_data_dir / file.filename
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    dataset = Dataset(
        project_id=id,
        name=name or file.filename,
        type=dataset_type,
        file_path=str(file_path)
    )
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)
    return dataset

@router.get("/{id}/datasets", response_model=List[DatasetResponse])
async def list_datasets(id: str, db: AsyncSession = Depends(get_db)):
    """List datasets for a project"""
    result = await db.execute(select(Dataset).where(Dataset.project_id == id))
    return result.scalars().all()
