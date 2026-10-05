import enum
import uuid
from sqlalchemy import Column, String, Float, JSON, Boolean, ForeignKey
from app.database import Base

class DamType(str, enum.Enum):
    EARTHFILL = "EARTHFILL"
    CONCRETE_GRAVITY = "CONCRETE_GRAVITY"
    CONCRETE_ARCH = "CONCRETE_ARCH"
    ROCKFILL = "ROCKFILL"

class DamProfile(Base):
    __tablename__ = "dam_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    dam_type = Column(String, nullable=False) # Store Enum as string for sqlite comp
    
    height_m = Column(Float, nullable=True)
    crest_length_m = Column(Float, nullable=True)
    crest_elevation_m = Column(Float, nullable=True)
    
    reservoir_volume_m3 = Column(Float, nullable=True)
    reservoir_area_m2 = Column(Float, nullable=True)
    spillway_capacity_m3s = Column(Float, nullable=True)
    
    stage_storage_json = Column(JSON, nullable=True)
    source_citation = Column(String, nullable=True)
    
    # Flags to indicate if a parameter was assumed/estimated
    is_assumed = Column(Boolean, default=False)
