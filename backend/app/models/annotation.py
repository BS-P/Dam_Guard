import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, JSON, ForeignKey, DateTime, Enum, Boolean
from app.database import Base

class AnnotationType(str, enum.Enum):
    DAM = "DAM"
    BREACH_POINT = "BREACH_POINT"
    VILLAGE = "VILLAGE"
    CRITICAL_FACILITY = "CRITICAL_FACILITY"
    SHELTER = "SHELTER"
    ROAD_BRIDGE = "ROAD_BRIDGE"
    GAUGE = "GAUGE"
    INSPECTION_AREA = "INSPECTION_AREA"
    CUSTOM_POLYGON = "CUSTOM_POLYGON"
    MARKER = "MARKER"
    LINE = "LINE"
    NOTE = "NOTE"

class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    
    type = Column(Enum(AnnotationType), nullable=False)
    name = Column(String, nullable=True)
    
    geometry_geojson = Column(JSON, nullable=False)
    properties_json = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)
    
    visible = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
