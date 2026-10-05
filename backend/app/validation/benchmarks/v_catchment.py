"""
V-Catchment benchmark test for 2D-VPMM and 2D Explicit Diffusion-Wave solvers.

From NIH Roorkee (2019) Report, Section 4.1.
Original benchmark: Di Giammarco et al. (1996).

Geometry:
    Two symmetric overland planes: 1000m (length) × 800m (width each)
    Central drainage channel: 20m wide, 1m deep, 1000m long
    Lateral slope towards channel: S0y = 0.05 (5%)
    Longitudinal slope: S0x = 0.02 (2%)
    Channel bed slope: S0 = 0.02 (2%)

Rainfall:
    Uniform effective rainfall: Re = 10.8 mm/hr (3.0e-6 m/s)
    Duration: 90 minutes (5400 s)

Manning's roughness:
    Overland planes: n = 0.015
    Channel: n = 0.15

Grid:
    dx = dy = 50m, dt = 6s (baseline)

Acceptance criteria (from report):
    2D-VPMM: NSE >= 0.97, |EVOL| <= 0.5%, |Qper| <= 2%
    2D-DW-Explicit: NSE >= 0.97 (for baseline grid)
"""
import numpy as np
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class BenchmarkResult:
    """Results from a benchmark test."""
    test_name: str
    solver_name: str
    nse: float  # Nash-Sutcliffe Efficiency
    evol_pct: float  # Volume error (%)
    qpeak_error_pct: float  # Peak discharge error (%)
    tpeak_error_pct: float  # Time-to-peak error (%)
    runtime_s: float
    mass_error_pct: float
    passed: bool
    details: Dict[str, Any]
    hydrograph_time: Optional[np.ndarray] = None
    hydrograph_q: Optional[np.ndarray] = None


def create_v_catchment_dem(
    dx: float = 50.0,
    dy: float = 50.0,
    plane_length: float = 1000.0,
    plane_width: float = 800.0,
    channel_width: float = 20.0,
    s0x: float = 0.02,
    s0y: float = 0.05,
    base_elevation: float = 100.0
) -> tuple:
    """
    Create V-catchment DEM array.
    
    The V-catchment has two symmetric planes draining to a central channel.
    The channel runs along the x-direction (columns).
    
    Returns:
        (dem, manning_n, nx, ny, channel_row_indices)
    """
    # Grid dimensions
    total_width = 2 * plane_width + channel_width
    nx = int(plane_length / dx)  # columns (x-direction, along channel)
    ny = int(total_width / dy)  # rows (y-direction, across valley)
    
    dem = np.zeros((ny, nx), dtype=np.float64)
    manning_n = np.zeros((ny, nx), dtype=np.float64)
    
    # Channel center row
    center_row = ny // 2
    channel_half_cells = max(1, int(channel_width / (2 * dy)))
    
    for i in range(ny):
        for j in range(nx):
            x = j * dx
            y_from_center = abs(i - center_row) * dy
            
            # Longitudinal slope (elevation decreases in x-direction)
            elev_x = base_elevation - s0x * x
            
            # Cross-valley slope (V-shape, elevation increases away from center)
            is_channel = abs(i - center_row) <= channel_half_cells
            
            if is_channel:
                elev_y = 0  # Channel at baseline
                manning_n[i, j] = 0.15  # Channel roughness
            else:
                # Overland plane - lateral slope towards channel
                dist_from_channel = (y_from_center - channel_half_cells * dy)
                elev_y = s0y * dist_from_channel
                manning_n[i, j] = 0.015  # Overland roughness
            
            dem[i, j] = elev_x + elev_y
    
    channel_rows = list(range(center_row - channel_half_cells, center_row + channel_half_cells + 1))
    
    return dem, manning_n, nx, ny, channel_rows


def compute_nse(observed: np.ndarray, simulated: np.ndarray) -> float:
    """
    Compute Nash-Sutcliffe Efficiency.
    
    NSE = 1 - sum((Qobs - Qsim)^2) / sum((Qobs - Qobs_mean)^2)
    """
    mean_obs = np.mean(observed)
    ss_res = np.sum((observed - simulated) ** 2)
    ss_tot = np.sum((observed - mean_obs) ** 2)
    
    if ss_tot == 0:
        return 1.0 if ss_res == 0 else 0.0
    
    return 1.0 - ss_res / ss_tot


def compute_volume_error(observed: np.ndarray, simulated: np.ndarray,
                          time_array: np.ndarray) -> float:
    """
    Compute volume error percentage.
    
    EVOL = (V_sim - V_obs) / V_obs * 100
    """
    v_obs = np.trapz(observed, time_array)
    v_sim = np.trapz(simulated, time_array)
    
    if v_obs == 0:
        return 0.0 if v_sim == 0 else 100.0
    
    return (v_sim - v_obs) / v_obs * 100.0


def run_v_catchment_benchmark(
    solver_name: str = "vpmm2d",
    dx: float = 50.0,
    dy: float = 50.0,
    dt: float = 6.0,
    rainfall_mmhr: float = 10.8,
    rain_duration_s: float = 5400.0,
    sim_duration_s: float = 10800.0,
    output_interval_s: float = 60.0
) -> BenchmarkResult:
    """
    Run V-catchment benchmark test.
    
    Args:
        solver_name: 'vpmm2d' or 'diffwave'
        dx, dy: Grid spacing (m)
        dt: Time step (s)
        rainfall_mmhr: Rainfall intensity (mm/hr)
        rain_duration_s: Rainfall duration (s)
        sim_duration_s: Total simulation duration (s)
        output_interval_s: Output interval (s)
        
    Returns:
        BenchmarkResult with NSE, EVOL, and other metrics
    """
    # Create V-catchment geometry
    dem, manning_n, nx, ny, channel_rows = create_v_catchment_dem(dx=dx, dy=dy)
    
    # Rainfall excess (m/s)
    re_ms = rainfall_mmhr / (3600.0 * 1000.0)  # mm/hr -> m/s
    
    # Create rainfall array (applied to overland cells only, not channel)
    n_timesteps = int(sim_duration_s / dt)
    
    # Outlet: last column of channel
    outlet_row = ny // 2
    outlet_col = nx - 1
    
    start_time = time.time()
    
    if solver_name == "vpmm2d":
        from app.solvers.vpmm2d.solver import Vpmm2dSolver
        
        solver = Vpmm2dSolver(
            dem=dem,
            manning_n=manning_n,
            dx=dx,
            dy=dy,
            dt=dt,
            rainfall_intensity_ms=re_ms,
            rainfall_duration_s=rain_duration_s,
            sim_duration_s=sim_duration_s,
            output_interval_s=output_interval_s,
            s_min=1e-5,
            h_min=1e-6
        )
        
        results = solver.run()
        
    elif solver_name == "diffwave":
        from app.solvers.diffwave.solver import DiffWaveSolver
        
        solver = DiffWaveSolver(
            dem=dem,
            manning_n=manning_n,
            dx=dx,
            dy=dy,
            dt=dt,
            rainfall_intensity_ms=re_ms,
            rainfall_duration_s=rain_duration_s,
            sim_duration_s=sim_duration_s,
            output_interval_s=output_interval_s,
            s_min=1e-5,
            h_min=1e-6
        )
        
        results = solver.run()
    else:
        raise ValueError(f"Unknown solver: {solver_name}")
    
    runtime = time.time() - start_time
    
    # Extract outlet hydrograph
    # Discharge at outlet = velocity * depth * cell_width
    output_times = results['output_times']
    depth_series = results['depth_timeseries']  # (n_outputs, ny, nx)
    
    # Compute discharge at outlet (sum across channel cells at outlet column)
    outlet_q = np.zeros(len(output_times))
    for t_idx in range(len(output_times)):
        for row in channel_rows:
            h = depth_series[t_idx, row, outlet_col]
            if h > 1e-6:
                # Estimate velocity from Manning's equation
                s0x = 0.02  # Channel slope
                n_ch = 0.15
                v = (1.0 / n_ch) * (h ** (2.0/3.0)) * (s0x ** 0.5)
                outlet_q[t_idx] += v * h * dy  # Q = v * A = v * h * width
    
    # Mass conservation error
    total_rain_volume = re_ms * rain_duration_s * (2 * 800 * 1000)  # m³ (excluding channel area)
    total_outflow = np.trapz(outlet_q, output_times)
    remaining_storage = 0.0
    final_depth = depth_series[-1]
    remaining_storage = float(np.sum(final_depth) * dx * dy)
    
    mass_error_pct = ((total_outflow + remaining_storage - total_rain_volume) / total_rain_volume) * 100.0
    
    # Peak discharge
    peak_q = float(np.max(outlet_q))
    peak_idx = np.argmax(outlet_q)
    time_to_peak = float(output_times[peak_idx])
    
    # For this benchmark, we compare VPMM vs explicit
    # Since we're running one at a time, we check absolute criteria
    details = {
        'grid_dx_m': dx,
        'grid_dy_m': dy,
        'dt_s': dt,
        'n_cells': ny * nx,
        'peak_discharge_m3s': peak_q,
        'time_to_peak_s': time_to_peak,
        'total_rain_volume_m3': total_rain_volume,
        'total_outflow_m3': total_outflow,
        'remaining_storage_m3': remaining_storage,
        'cells_per_second': (ny * nx * n_timesteps) / runtime if runtime > 0 else 0
    }
    
    # Acceptance criteria
    passed = abs(mass_error_pct) <= 0.5
    
    return BenchmarkResult(
        test_name=f"V-Catchment (dx={dx}m, dt={dt}s)",
        solver_name=solver_name,
        nse=0.0,  # Needs reference to compute - set in comparison
        evol_pct=mass_error_pct,
        qpeak_error_pct=0.0,  # Needs reference
        tpeak_error_pct=0.0,  # Needs reference
        runtime_s=runtime,
        mass_error_pct=mass_error_pct,
        passed=passed,
        details=details,
        hydrograph_time=output_times,
        hydrograph_q=outlet_q
    )


def compare_solvers_v_catchment(
    dx: float = 50.0,
    dy: float = 50.0,
    dt: float = 6.0
) -> Dict[str, BenchmarkResult]:
    """
    Run V-catchment benchmark with both solvers and compare.
    
    Returns:
        Dict with 'vpmm2d' and 'diffwave' BenchmarkResults, with NSE computed.
    """
    results = {}
    
    # Run explicit diffusion wave first (serves as reference)
    dw_result = run_v_catchment_benchmark('diffwave', dx=dx, dy=dy, dt=dt)
    results['diffwave'] = dw_result
    
    # Run VPMM
    vpmm_result = run_v_catchment_benchmark('vpmm2d', dx=dx, dy=dy, dt=dt)
    results['vpmm2d'] = vpmm_result
    
    # Compute NSE of VPMM against explicit (on common time steps)
    if dw_result.hydrograph_q is not None and vpmm_result.hydrograph_q is not None:
        # Interpolate to common time array
        common_times = dw_result.hydrograph_time
        vpmm_interp = np.interp(common_times, vpmm_result.hydrograph_time, vpmm_result.hydrograph_q)
        
        nse = compute_nse(dw_result.hydrograph_q, vpmm_interp)
        vpmm_result.nse = nse
        
        # Peak error
        if float(np.max(dw_result.hydrograph_q)) > 0:
            vpmm_result.qpeak_error_pct = (
                (float(np.max(vpmm_result.hydrograph_q)) - float(np.max(dw_result.hydrograph_q)))
                / float(np.max(dw_result.hydrograph_q)) * 100.0
            )
        
        # Check acceptance
        vpmm_result.passed = (
            nse >= 0.97
            and abs(vpmm_result.evol_pct) <= 0.5
            and abs(vpmm_result.qpeak_error_pct) <= 2.0
        )
        
        vpmm_result.details['nse_vs_explicit'] = nse
    
    return results
