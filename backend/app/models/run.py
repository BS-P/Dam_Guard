import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, JSON, ForeignKey, DateTime, Enum, Integer
from app.database import Base

class SolverTier(str, enum.Enum):
    T1_VPMM = "T1_VPMM"
    T1_DIFFWAVE = "T1_DIFFWAVE"
    T2_DELFT3D = "T2_DELFT3D"
    T3_SPH = "T3_SPH"
    COUPLED = "COUPLED"
    EXTERNAL = "EXTERNAL"

class RunStatus(str, enum.Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    POSTPROCESSING = "POSTPROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario_id = Column(String(36), ForeignKey("scenarios.id"), nullable=False)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    
    solver_tier = Column(Enum(SolverTier), nullable=False)
    status = Column(Enum(RunStatus), default=RunStatus.PENDING)
    
    config_json = Column(JSON, nullable=True)
    input_hash = Column(String, nullable=True)
    software_versions_json = Column(JSON, nullable=True)
    
    random_seed = Column(Integer, nullable=True)
    runtime_seconds = Column(Float, nullable=True)
    output_checksums_json = Column(JSON, nullable=True)
    output_dir = Column(String, nullable=True)
    
    grid_dx_m = Column(Float, nullable=True)
    grid_dy_m = Column(Float, nullable=True)
    dt_s = Column(Float, nullable=True)
    domain_bounds = Column(JSON, nullable=True)
    
    n_cells = Column(Integer, nullable=True)
    cells_per_second = Column(Float, nullable=True)
    mass_error_pct = Column(Float, nullable=True)
    
    peak_depth_m = Column(Float, nullable=True)
    peak_velocity_ms = Column(Float, nullable=True)
    inundated_area_km2 = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    error_message = Column(String, nullable=True)
    progress_pct = Column(Float, default=0.0)
