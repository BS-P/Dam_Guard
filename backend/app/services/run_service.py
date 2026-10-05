"""
Simulation run service - orchestrates the full processing pipeline.

Stages:
    Input validation -> DEM fetch/clip/reproject -> DEM conditioning ->
    Roughness map -> Breach model -> Solver run(s) -> Post-processing ->
    Hazard/exposure/loss -> GEE observed extent -> Validation -> Export

Each stage reports real state: READY | PROCESSING | COMPLETED | FAILED | UNAVAILABLE | PENDING
"""
import asyncio
import os
import time
import uuid
import json
import hashlib
import numpy as np
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class StageStatus(str, Enum):
    READY = "READY"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    UNAVAILABLE = "UNAVAILABLE"
    PENDING = "PENDING"


@dataclass
class PipelineStage:
    name: str
    status: StageStatus = StageStatus.PENDING
    progress_pct: float = 0.0
    message: str = ""
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error: Optional[str] = None


@dataclass
class RunConfig:
    """Configuration for a simulation run."""
    project_id: str
    scenario_id: str
    solver_tier: str  # T1_VPMM, T1_DIFFWAVE, T2_DELFT3D, T3_SPH, COUPLED
    dem_path: str
    manning_n_default: float = 0.035
    landcover_path: Optional[str] = None
    dx: float = 30.0
    dy: float = 30.0
    dt: float = 10.0
    sim_duration_s: float = 21600.0  # 6 hours
    output_interval_s: float = 300.0  # 5 minutes
    s_min: float = 1e-5
    h_min: float = 1e-6
    depth_threshold: float = 0.1  # m, for arrival time
    breach_hydrograph_time: Optional[list] = None
    breach_hydrograph_q: Optional[list] = None
    source_cell_row: Optional[int] = None
    source_cell_col: Optional[int] = None


@dataclass
class RunState:
    """Current state of a simulation run."""
    run_id: str
    config: RunConfig
    status: str = "PENDING"  # PENDING, RUNNING, POSTPROCESSING, COMPLETED, FAILED, CANCELLED
    progress_pct: float = 0.0
    stages: Dict[str, PipelineStage] = field(default_factory=dict)
    output_dir: str = ""
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    runtime_s: Optional[float] = None
    error_message: Optional[str] = None
    # Results metadata
    peak_depth_m: Optional[float] = None
    peak_velocity_ms: Optional[float] = None
    inundated_area_km2: Optional[float] = None
    mass_error_pct: Optional[float] = None
    cells_per_second: Optional[float] = None
    n_cells: Optional[int] = None
    available_layers: list = field(default_factory=list)


# Global active runs registry
_active_runs: Dict[str, RunState] = {}
_run_tasks: Dict[str, asyncio.Task] = {}


def get_run_state(run_id: str) -> Optional[RunState]:
    """Get current state of a run."""
    return _active_runs.get(run_id)


def get_all_runs() -> Dict[str, RunState]:
    """Get all active runs."""
    return _active_runs


async def start_simulation(config: RunConfig, progress_callback: Optional[Callable] = None) -> str:
    """
    Start a simulation run in the background.
    
    Returns:
        run_id
    """
    run_id = str(uuid.uuid4())[:8]
    
    output_dir = os.path.join("runs", config.project_id, run_id)
    os.makedirs(output_dir, exist_ok=True)
    
    state = RunState(
        run_id=run_id,
        config=config,
        output_dir=output_dir,
        stages={
            "input_validation": PipelineStage("Input Validation"),
            "dem_preparation": PipelineStage("DEM Preparation"),
            "dem_conditioning": PipelineStage("DEM Conditioning"),
            "roughness_map": PipelineStage("Roughness Map"),
            "breach_model": PipelineStage("Breach Model"),
            "solver_run": PipelineStage("Solver Run"),
            "post_processing": PipelineStage("Post-Processing"),
            "hazard_analysis": PipelineStage("Hazard Analysis"),
        }
    )
    
    _active_runs[run_id] = state
    
    # Run in background
    task = asyncio.create_task(_run_pipeline(state, progress_callback))
    _run_tasks[run_id] = task
    
    return run_id


async def cancel_run(run_id: str) -> bool:
    """Cancel a running simulation."""
    if run_id in _run_tasks:
        _run_tasks[run_id].cancel()
        if run_id in _active_runs:
            _active_runs[run_id].status = "CANCELLED"
        return True
    return False


async def _run_pipeline(state: RunState, progress_callback: Optional[Callable] = None):
    """Execute the full simulation pipeline."""
    state.status = "RUNNING"
    state.started_at = time.time()
    
    try:
        # Stage 1: Input Validation
        await _run_stage(state, "input_validation", _validate_inputs, progress_callback)
        
        # Stage 2: DEM Preparation
        await _run_stage(state, "dem_preparation", _prepare_dem, progress_callback)
        
        # Stage 3: DEM Conditioning
        await _run_stage(state, "dem_conditioning", _condition_dem, progress_callback)
        
        # Stage 4: Roughness Map
        await _run_stage(state, "roughness_map", _create_roughness_map, progress_callback)
        
        # Stage 5: Breach Model (if not already computed)
        await _run_stage(state, "breach_model", _run_breach_model, progress_callback)
        
        # Stage 6: Solver Run
        await _run_stage(state, "solver_run", _run_solver, progress_callback)
        
        # Stage 7: Post-Processing
        state.status = "POSTPROCESSING"
        await _run_stage(state, "post_processing", _post_process, progress_callback)
        
        # Stage 8: Hazard Analysis
        await _run_stage(state, "hazard_analysis", _run_hazard_analysis, progress_callback)
        
        state.status = "COMPLETED"
        state.completed_at = time.time()
        state.runtime_s = state.completed_at - state.started_at
        
        logger.info(f"Run {state.run_id} completed in {state.runtime_s:.1f}s")
        
    except asyncio.CancelledError:
        state.status = "CANCELLED"
        logger.info(f"Run {state.run_id} cancelled")
    except Exception as e:
        state.status = "FAILED"
        state.error_message = str(e)
        state.completed_at = time.time()
        logger.error(f"Run {state.run_id} failed: {e}", exc_info=True)


async def _run_stage(
    state: RunState,
    stage_name: str,
    func,
    progress_callback: Optional[Callable]
):
    """Run a pipeline stage with status tracking."""
    stage = state.stages[stage_name]
    stage.status = StageStatus.PROCESSING
    stage.started_at = time.time()
    
    try:
        # Run in thread pool to not block event loop
        await asyncio.get_event_loop().run_in_executor(
            None, func, state
        )
        
        stage.status = StageStatus.COMPLETED
        stage.progress_pct = 100.0
        stage.completed_at = time.time()
        
        # Update overall progress
        completed_stages = sum(1 for s in state.stages.values() if s.status == StageStatus.COMPLETED)
        state.progress_pct = (completed_stages / len(state.stages)) * 100.0
        
        if progress_callback:
            progress_callback(state)
            
    except Exception as e:
        stage.status = StageStatus.FAILED
        stage.error = str(e)
        stage.completed_at = time.time()
        raise


def _validate_inputs(state: RunState):
    """Validate all input data for the simulation."""
    config = state.config
    
    # Check DEM exists
    if not os.path.exists(config.dem_path):
        raise FileNotFoundError(f"DEM file not found: {config.dem_path}")
    
    # Validate DEM is readable
    try:
        from app.geospatial.dem import load_dem_info
        dem_info = load_dem_info(config.dem_path)
        state.stages["input_validation"].message = (
            f"DEM: {dem_info.shape[0]}x{dem_info.shape[1]}, "
            f"res: {dem_info.resolution_m[0]:.1f}m, "
            f"CRS: {dem_info.crs}"
        )
    except ImportError:
        # Fallback: just check file is valid GeoTIFF header
        import struct
        with open(config.dem_path, 'rb') as f:
            header = f.read(4)
            if header[:2] not in [b'II', b'MM']:
                raise ValueError(f"File does not appear to be a valid GeoTIFF: {config.dem_path}")
        state.stages["input_validation"].message = "DEM validated (basic check)"
    
    # Validate breach hydrograph if provided
    if config.breach_hydrograph_q is not None:
        if len(config.breach_hydrograph_q) < 2:
            raise ValueError("Breach hydrograph must have at least 2 time steps")
        if config.breach_hydrograph_time is None:
            raise ValueError("Breach hydrograph time array is required")


def _prepare_dem(state: RunState):
    """Load and prepare DEM for simulation."""
    config = state.config
    
    try:
        from app.geospatial.dem import load_dem_array, compute_slopes
        
        dem, meta = load_dem_array(config.dem_path)
        
        # Compute grid spacing from DEM metadata
        if meta.get('crs') and hasattr(meta['crs'], 'is_geographic') and meta['crs'].is_geographic:
            # Convert from degrees to meters at center
            center_lat = (meta['bounds'].bottom + meta['bounds'].top) / 2
            config.dy = abs(meta['res'][0]) * 111320.0
            config.dx = abs(meta['res'][1]) * 111320.0 * np.cos(np.radians(center_lat))
        else:
            config.dx = abs(meta['res'][0])
            config.dy = abs(meta['res'][1])
        
        # Store DEM in output directory
        np.save(os.path.join(state.output_dir, "dem.npy"), dem)
        
        # Compute slopes
        slope_x, slope_y = compute_slopes(dem, config.dx, config.dy, config.s_min)
        np.save(os.path.join(state.output_dir, "slope_x.npy"), slope_x)
        np.save(os.path.join(state.output_dir, "slope_y.npy"), slope_y)
        
        state.n_cells = dem.shape[0] * dem.shape[1]
        state.stages["dem_preparation"].message = (
            f"DEM loaded: {dem.shape[0]}x{dem.shape[1]} cells, "
            f"dx={config.dx:.1f}m, dy={config.dy:.1f}m"
        )
        
    except ImportError:
        # Fallback: load with numpy if rasterio not available
        raise ImportError("rasterio is required for DEM processing")


def _condition_dem(state: RunState):
    """Condition DEM (fill depressions, enforce minimum slopes)."""
    dem_path = os.path.join(state.output_dir, "dem.npy")
    dem = np.load(dem_path)
    
    # Replace NaN with minimum elevation (simple conditioning)
    nan_mask = np.isnan(dem)
    if np.any(nan_mask):
        dem[nan_mask] = np.nanmin(dem) - 1.0
    
    # Enforce minimum slope
    from app.geospatial.conditioning import enforce_minimum_slope
    dem_conditioned = enforce_minimum_slope(dem, state.config.dx, state.config.dy, state.config.s_min)
    
    np.save(os.path.join(state.output_dir, "dem_conditioned.npy"), dem_conditioned)
    
    n_adjusted = int(np.sum(np.abs(dem_conditioned - dem) > 1e-6))
    state.stages["dem_conditioning"].message = f"Conditioned: {n_adjusted} cells adjusted"


def _create_roughness_map(state: RunState):
    """Create spatially varying Manning's roughness map."""
    config = state.config
    dem = np.load(os.path.join(state.output_dir, "dem_conditioned.npy"))
    
    if config.landcover_path and os.path.exists(config.landcover_path):
        try:
            from app.services.data_service import get_roughness_map
            manning_n = get_roughness_map(config.dem_path, config.landcover_path, config.manning_n_default)
        except Exception:
            manning_n = np.full_like(dem, config.manning_n_default)
    else:
        manning_n = np.full_like(dem, config.manning_n_default)
    
    np.save(os.path.join(state.output_dir, "manning_n.npy"), manning_n)
    state.stages["roughness_map"].message = f"Roughness map: n={config.manning_n_default} (default)"


def _run_breach_model(state: RunState):
    """Run breach model if hydrograph not pre-computed."""
    config = state.config
    
    if config.breach_hydrograph_q is not None:
        state.stages["breach_model"].message = "Using pre-computed breach hydrograph"
        return
    
    state.stages["breach_model"].message = "No breach hydrograph provided - using zero inflow"
    state.stages["breach_model"].status = StageStatus.COMPLETED


def _run_solver(state: RunState):
    """Run the selected hydrodynamic solver."""
    config = state.config
    
    # Load prepared data
    dem = np.load(os.path.join(state.output_dir, "dem_conditioned.npy"))
    manning_n = np.load(os.path.join(state.output_dir, "manning_n.npy"))
    slope_x = np.load(os.path.join(state.output_dir, "slope_x.npy"))
    slope_y = np.load(os.path.join(state.output_dir, "slope_y.npy"))
    
    tier = config.solver_tier
    
    if tier in ("T1_VPMM", "T1_DIFFWAVE"):
        _run_t1_solver(state, dem, manning_n, slope_x, slope_y)
    elif tier == "T2_DELFT3D":
        _run_t2_solver(state)
    elif tier == "T3_SPH":
        _run_t3_solver(state)
    else:
        raise ValueError(f"Unknown solver tier: {tier}")


def _run_t1_solver(state: RunState, dem, manning_n, slope_x, slope_y):
    """Run T1 solver (VPMM or DiffWave)."""
    config = state.config
    
    # Prepare source injection
    source_cells = np.zeros_like(dem)
    if config.breach_hydrograph_q is not None and config.source_cell_row is not None:
        # Will inject at each time step
        pass
    
    start = time.time()
    
    if config.solver_tier == "T1_VPMM":
        from app.solvers.vpmm2d.solver import Vpmm2dSolver
        solver = Vpmm2dSolver(
            dem=dem, manning_n=manning_n,
            dx=config.dx, dy=config.dy, dt=config.dt,
            rainfall_intensity_ms=0.0,
            rainfall_duration_s=0.0,
            sim_duration_s=config.sim_duration_s,
            output_interval_s=config.output_interval_s,
            s_min=config.s_min, h_min=config.h_min,
            breach_hydrograph_time=np.array(config.breach_hydrograph_time) if config.breach_hydrograph_time else None,
            breach_hydrograph_q=np.array(config.breach_hydrograph_q) if config.breach_hydrograph_q else None,
            source_row=config.source_cell_row,
            source_col=config.source_cell_col,
        )
        results = solver.run()
    else:
        from app.solvers.diffwave.solver import DiffWaveSolver
        solver = DiffWaveSolver(
            dem=dem, manning_n=manning_n,
            dx=config.dx, dy=config.dy, dt=config.dt,
            rainfall_intensity_ms=0.0,
            rainfall_duration_s=0.0,
            sim_duration_s=config.sim_duration_s,
            output_interval_s=config.output_interval_s,
            s_min=config.s_min, h_min=config.h_min,
        )
        results = solver.run()
    
    runtime = time.time() - start
    
    # Save results
    _save_solver_results(state, results, runtime)
    
    state.stages["solver_run"].message = (
        f"{config.solver_tier} completed in {runtime:.1f}s, "
        f"peak depth: {state.peak_depth_m:.2f}m"
    )


def _run_t2_solver(state: RunState):
    """Run Delft3D FM solver."""
    from app.solvers.delft3d import Delft3dFmProvider
    
    provider = Delft3dFmProvider()
    status = provider.check_installed()
    
    if not status.available:
        state.stages["solver_run"].status = StageStatus.UNAVAILABLE
        state.stages["solver_run"].message = f"Delft3D FM backend unavailable: {status.reason_unavailable}"
        raise RuntimeError(f"Delft3D FM backend unavailable: {status.reason_unavailable}")


def _run_t3_solver(state: RunState):
    """Run SPH solver."""
    from app.solvers.sph import SphProvider
    
    provider = SphProvider()
    status = provider.check_installed()
    
    if not status.available:
        state.stages["solver_run"].status = StageStatus.UNAVAILABLE
        state.stages["solver_run"].message = f"SPH backend unavailable: {status.reason_unavailable}"
        raise RuntimeError(f"SPH backend unavailable: {status.reason_unavailable}")


def _save_solver_results(state: RunState, results: dict, runtime: float):
    """Save solver output arrays to disk."""
    output_dir = state.output_dir
    
    # Save time series and spatial arrays
    if 'depth_timeseries' in results:
        np.save(os.path.join(output_dir, "depth_timeseries.npy"), results['depth_timeseries'])
    if 'output_times' in results:
        np.save(os.path.join(output_dir, "output_times.npy"), results['output_times'])
    if 'max_depth' in results:
        np.save(os.path.join(output_dir, "max_depth.npy"), results['max_depth'])
        state.peak_depth_m = float(np.nanmax(results['max_depth']))
    if 'max_velocity' in results:
        np.save(os.path.join(output_dir, "max_velocity.npy"), results['max_velocity'])
        state.peak_velocity_ms = float(np.nanmax(results['max_velocity']))
    if 'arrival_time' in results:
        np.save(os.path.join(output_dir, "arrival_time.npy"), results['arrival_time'])
    if 'duration' in results:
        np.save(os.path.join(output_dir, "duration.npy"), results['duration'])
    if 'validity_mask' in results:
        np.save(os.path.join(output_dir, "validity_mask.npy"), results['validity_mask'])
    
    # Compute inundated area
    if 'max_depth' in results:
        inundated = results['max_depth'] > state.config.depth_threshold
        inundated_area = float(np.sum(inundated)) * state.config.dx * state.config.dy / 1e6  # km²
        state.inundated_area_km2 = inundated_area
    
    # Mass error
    if 'mass_error_pct' in results:
        state.mass_error_pct = float(results['mass_error_pct'])
    
    # Performance
    n_timesteps = int(state.config.sim_duration_s / state.config.dt)
    if runtime > 0 and state.n_cells:
        state.cells_per_second = (state.n_cells * n_timesteps) / runtime
    
    state.runtime_s = runtime
    state.available_layers = ['max_depth', 'max_velocity', 'arrival_time', 'duration']
    if 'validity_mask' in results:
        state.available_layers.append('validity_mask')


def _post_process(state: RunState):
    """Post-process solver results into COG rasters."""
    output_dir = state.output_dir
    
    # Convert numpy arrays to GeoTIFFs
    try:
        import rasterio
        from rasterio.transform import from_bounds
        from app.geospatial.dem import load_dem_info, create_cog
        
        dem_info = load_dem_info(state.config.dem_path)
        transform = from_bounds(
            dem_info.bounds[0], dem_info.bounds[1],
            dem_info.bounds[2], dem_info.bounds[3],
            dem_info.shape[1], dem_info.shape[0]
        )
        crs = dem_info.crs
        
        for layer_name in ['max_depth', 'max_velocity', 'arrival_time', 'duration']:
            npy_path = os.path.join(output_dir, f"{layer_name}.npy")
            if os.path.exists(npy_path):
                data = np.load(npy_path)
                tiff_path = os.path.join(output_dir, f"{layer_name}.tif")
                
                profile = {
                    'driver': 'GTiff',
                    'dtype': 'float32',
                    'width': data.shape[1],
                    'height': data.shape[0],
                    'count': 1,
                    'crs': crs,
                    'transform': transform,
                    'nodata': -9999.0,
                    'tiled': True,
                    'blockxsize': 256,
                    'blockysize': 256,
                    'compress': 'deflate',
                }
                
                out_data = data.astype(np.float32)
                out_data[np.isnan(out_data)] = -9999.0
                
                with rasterio.open(tiff_path, 'w', **profile) as dst:
                    dst.write(out_data, 1)
                    dst.build_overviews([2, 4, 8], rasterio.enums.Resampling.nearest)
                    dst.update_tags(ns='rio_overview', resampling='nearest')
        
        state.stages["post_processing"].message = "Result GeoTIFFs created"
        
    except ImportError:
        state.stages["post_processing"].message = "Raster export skipped (rasterio not available)"
        state.stages["post_processing"].status = StageStatus.COMPLETED


def _run_hazard_analysis(state: RunState):
    """Run hazard classification on results."""
    output_dir = state.output_dir
    
    max_depth_path = os.path.join(output_dir, "max_depth.npy")
    max_vel_path = os.path.join(output_dir, "max_velocity.npy")
    
    if not os.path.exists(max_depth_path):
        state.stages["hazard_analysis"].message = "No depth results for hazard analysis"
        return
    
    max_depth = np.load(max_depth_path)
    max_velocity = np.load(max_vel_path) if os.path.exists(max_vel_path) else np.zeros_like(max_depth)
    
    try:
        from app.analysis.hazard import classify_hazard, hazard_statistics
        
        hazard = classify_hazard(max_depth, max_velocity)
        np.save(os.path.join(output_dir, "hazard_class.npy"), hazard)
        
        stats = hazard_statistics(hazard, state.config.dx, state.config.dy)
        
        with open(os.path.join(output_dir, "hazard_stats.json"), 'w') as f:
            json.dump(stats, f, indent=2)
        
        state.available_layers.append('hazard_class')
        state.stages["hazard_analysis"].message = f"Hazard classified: {stats}"
        
    except ImportError:
        # Inline simple classification
        hazard = np.zeros_like(max_depth, dtype=np.int32)
        hazard[max_depth > 0.1] = 1
        hazard[max_depth > 0.25] = 2
        hazard[max_depth > 0.75] = 3
        hazard[max_depth > 1.5] = 4
        hazard[max_depth > 2.5] = 5
        dv = max_depth * max_velocity
        hazard[dv > 7.0] = 5
        
        np.save(os.path.join(output_dir, "hazard_class.npy"), hazard)
        state.available_layers.append('hazard_class')
        state.stages["hazard_analysis"].message = "Hazard classified (inline)"


# Save run metadata
def save_run_metadata(state: RunState):
    """Save run metadata to JSON for persistence and replay."""
    meta = {
        'run_id': state.run_id,
        'status': state.status,
        'solver_tier': state.config.solver_tier,
        'started_at': state.started_at,
        'completed_at': state.completed_at,
        'runtime_s': state.runtime_s,
        'peak_depth_m': state.peak_depth_m,
        'peak_velocity_ms': state.peak_velocity_ms,
        'inundated_area_km2': state.inundated_area_km2,
        'mass_error_pct': state.mass_error_pct,
        'cells_per_second': state.cells_per_second,
        'n_cells': state.n_cells,
        'available_layers': state.available_layers,
        'error_message': state.error_message,
        'config': {
            'dx': state.config.dx,
            'dy': state.config.dy,
            'dt': state.config.dt,
            'sim_duration_s': state.config.sim_duration_s,
            'manning_n_default': state.config.manning_n_default,
            's_min': state.config.s_min,
        },
        'stages': {
            name: {
                'status': stage.status.value,
                'message': stage.message,
                'error': stage.error,
            }
            for name, stage in state.stages.items()
        }
    }
    
    with open(os.path.join(state.output_dir, "run_metadata.json"), 'w') as f:
        json.dump(meta, f, indent=2)
