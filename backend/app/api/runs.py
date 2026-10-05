"""
Simulation runs API - start, monitor, and manage solver runs.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
import os

from app.database import get_db

router = APIRouter()


class RunStartRequest(BaseModel):
    solver_tier: str  # T1_VPMM, T1_DIFFWAVE, T2_DELFT3D, T3_SPH, COUPLED
    dem_path: Optional[str] = None
    manning_n_default: float = 0.035
    dx: float = 30.0
    dy: float = 30.0
    dt: float = 10.0
    sim_duration_s: float = 21600.0
    output_interval_s: float = 300.0
    breach_hydrograph_time: Optional[List[float]] = None
    breach_hydrograph_q: Optional[List[float]] = None
    source_cell_row: Optional[int] = None
    source_cell_col: Optional[int] = None


class StageInfo(BaseModel):
    name: str
    status: str
    progress_pct: float = 0.0
    message: str = ""
    error: Optional[str] = None


class RunStatusResponse(BaseModel):
    run_id: str
    status: str
    progress_pct: float = 0.0
    solver_tier: str = ""
    stages: dict = {}
    output_dir: str = ""
    runtime_s: Optional[float] = None
    peak_depth_m: Optional[float] = None
    peak_velocity_ms: Optional[float] = None
    inundated_area_km2: Optional[float] = None
    mass_error_pct: Optional[float] = None
    cells_per_second: Optional[float] = None
    available_layers: List[str] = []
    error_message: Optional[str] = None


@router.post("/{project_id}/scenarios/{scenario_id}/runs")
async def start_run(project_id: str, scenario_id: str, req: RunStartRequest):
    """Start a new simulation run."""
    from app.services.run_service import start_simulation, RunConfig
    
    # Determine DEM path
    dem_path = req.dem_path
    if not dem_path:
        # Look for DEM in project directory
        project_dir = os.path.join("projects", project_id)
        for f in ['dem.tif', 'dem.tiff', 'elevation.tif']:
            candidate = os.path.join(project_dir, f)
            if os.path.exists(candidate):
                dem_path = candidate
                break
    
    if not dem_path or not os.path.exists(dem_path):
        raise HTTPException(400, "No DEM file found. Upload a DEM first.")
    
    config = RunConfig(
        project_id=project_id,
        scenario_id=scenario_id,
        solver_tier=req.solver_tier,
        dem_path=dem_path,
        manning_n_default=req.manning_n_default,
        dx=req.dx,
        dy=req.dy,
        dt=req.dt,
        sim_duration_s=req.sim_duration_s,
        output_interval_s=req.output_interval_s,
        breach_hydrograph_time=req.breach_hydrograph_time,
        breach_hydrograph_q=req.breach_hydrograph_q,
        source_cell_row=req.source_cell_row,
        source_cell_col=req.source_cell_col,
    )
    
    run_id = await start_simulation(config)
    
    return {"run_id": run_id, "status": "RUNNING", "message": f"Simulation started with {req.solver_tier}"}


@router.get("/{project_id}/runs")
async def list_runs(project_id: str):
    """List all runs for a project."""
    from app.services.run_service import get_all_runs
    
    runs = get_all_runs()
    project_runs = [
        RunStatusResponse(
            run_id=state.run_id,
            status=state.status,
            progress_pct=state.progress_pct,
            solver_tier=state.config.solver_tier,
            stages={name: {"status": s.status.value, "message": s.message} for name, s in state.stages.items()},
            output_dir=state.output_dir,
            runtime_s=state.runtime_s,
            peak_depth_m=state.peak_depth_m,
            peak_velocity_ms=state.peak_velocity_ms,
            inundated_area_km2=state.inundated_area_km2,
            mass_error_pct=state.mass_error_pct,
            cells_per_second=state.cells_per_second,
            available_layers=state.available_layers,
            error_message=state.error_message,
        )
        for state in runs.values()
        if state.config.project_id == project_id
    ]
    
    return project_runs


@router.get("/{project_id}/runs/{run_id}")
async def get_run(project_id: str, run_id: str):
    """Get detailed status of a specific run."""
    from app.services.run_service import get_run_state
    
    state = get_run_state(run_id)
    if not state or state.config.project_id != project_id:
        raise HTTPException(404, "Run not found")
    
    return RunStatusResponse(
        run_id=state.run_id,
        status=state.status,
        progress_pct=state.progress_pct,
        solver_tier=state.config.solver_tier,
        stages={name: {"status": s.status.value, "message": s.message, "error": s.error} for name, s in state.stages.items()},
        output_dir=state.output_dir,
        runtime_s=state.runtime_s,
        peak_depth_m=state.peak_depth_m,
        peak_velocity_ms=state.peak_velocity_ms,
        inundated_area_km2=state.inundated_area_km2,
        mass_error_pct=state.mass_error_pct,
        cells_per_second=state.cells_per_second,
        available_layers=state.available_layers,
        error_message=state.error_message,
    )


@router.delete("/{project_id}/runs/{run_id}")
async def cancel_run(project_id: str, run_id: str):
    """Cancel a running simulation."""
    from app.services.run_service import cancel_run as do_cancel
    
    success = await do_cancel(run_id)
    if not success:
        raise HTTPException(404, "Run not found or already completed")
    
    return {"message": "Run cancelled", "run_id": run_id}
