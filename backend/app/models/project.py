import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.database import Base

class ProjectStatus(str, enum.Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

class DatasetType(str, enum.Enum):
    DEM = "DEM"
    IMAGERY = "IMAGERY"
    LANDCOVER = "LANDCOVER"
    HYDROLOGY = "HYDROLOGY"
    OBSERVED_FLOOD = "OBSERVED_FLOOD"
    OTHER = "OTHER"

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    aoi_geojson = Column(JSON, nullable=True)
    crs = Column(String, nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.CREATED)
    
    dam_config = Column(JSON, nullable=True)
    breach_config = Column(JSON, nullable=True)
    
    datasets = relationship("Dataset", back_populates="project", cascade="all, delete-orphan")

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(DatasetType), nullable=False)
    
    source = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    license = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    
    crs = Column(String, nullable=True)
    resolution_m = Column(String, nullable=True) # string or float depending on usage
    bounds_geojson = Column(JSON, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    is_demo = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="datasets")
