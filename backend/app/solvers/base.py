from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
from app.models.run import RunStatus, SolverTier

@dataclass
class SolverStatus:
    available: bool
    name: str
    tier: SolverTier
    version: str
    reason_unavailable: Optional[str] = None

@dataclass
class PrepareResult:
    success: bool
    config_path: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class RunHandle:
    run_id: str
    process_id: Optional[int] = None
    job_id: Optional[str] = None

@dataclass
class RunResult:
    output_dir: str
    layers: Dict[str, str]
    runtime_s: float
    mass_error_pct: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class SolverProvider(ABC):
    @abstractmethod
    def check_installed(self) -> SolverStatus:
        """Check if solver is installed and available"""
        pass
        
    @abstractmethod
    def prepare(self, scenario: Any, datasets: Any) -> PrepareResult:
        """Prepare inputs and config for the solver"""
        pass
        
    @abstractmethod
    def start(self, config: Dict[str, Any]) -> RunHandle:
        """Start the simulation"""
        pass
        
    @abstractmethod
    def status(self, handle: RunHandle) -> RunStatus:
        """Check current status of the simulation"""
        pass
        
    @abstractmethod
    def result(self, handle: RunHandle) -> RunResult:
        """Retrieve results after completion"""
        pass
        
    @abstractmethod
    def cancel(self, handle: RunHandle):
        """Cancel a running simulation"""
        pass
