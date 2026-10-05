import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, JSON, ForeignKey, DateTime, Enum
from app.database import Base

class MeasurementType(str, enum.Enum):
    POINT_PROBE = "POINT_PROBE"
    DISTANCE = "DISTANCE"
    AREA = "AREA"
    CROSS_SECTION = "CROSS_SECTION"
    TIME_SERIES = "TIME_SERIES"
    HYDROGRAPH_SECTION = "HYDROGRAPH_SECTION"
    EXPOSURE_POLYGON = "EXPOSURE_POLYGON"

class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    run_id = Column(String(36), ForeignKey("simulation_runs.id"), nullable=True)
    
    type = Column(Enum(MeasurementType), nullable=False)
    geometry_geojson = Column(JSON, nullable=False)
    results_json = Column(JSON, nullable=True)
    
    name = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
