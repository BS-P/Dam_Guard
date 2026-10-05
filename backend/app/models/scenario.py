import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, JSON, ForeignKey, DateTime, Enum
from app.database import Base

class BreachMode(str, enum.Enum):
    OVERTOPPING = "OVERTOPPING"
    PIPING = "PIPING"
    SUDDEN = "SUDDEN"
    BLOCKAGE_RELEASE = "BLOCKAGE_RELEASE"
    CUSTOM = "CUSTOM"

class BreachMethod(str, enum.Enum):
    FROEHLICH = "FROEHLICH"
    VON_THUN_GILLETTE = "VON_THUN_GILLETTE"
    USER_DEFINED = "USER_DEFINED"

class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    
    breach_mode = Column(Enum(BreachMode), nullable=False)
    breach_method = Column(Enum(BreachMethod), nullable=False)
    breach_params = Column(JSON, nullable=True)
    
    initial_water_level_m = Column(Float, nullable=True)
    inflow_hydrograph_json = Column(JSON, nullable=True)
    
    manning_n_default = Column(Float, nullable=True)
    roughness_source = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
