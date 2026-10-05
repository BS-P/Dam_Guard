"""
Reservoir routing for breach outflow hydrograph computation.

Couples the time-varying breach geometry with reservoir continuity (level-pool routing)
to produce Q(t), the outflow hydrograph through the breach.

The ODE: dS/dt = Q_in(t) - Q_out(t)
where Q_out is computed from broad-crested weir formula through the trapezoidal breach.

References:
    Standard level-pool reservoir routing methodology.
    Breach opening: linear growth from initiation to formation time t_f.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
from typing import Optional, List, Tuple
from dataclasses import dataclass
import math

from .parametric import (
    DamParameters, BreachParameters, BreachHydrograph, BreachMode
)


@dataclass 
class ReservoirConfig:
    """Configuration for reservoir routing."""
    dt_output: float = 60.0  # Output time step (s)
    simulation_duration_s: Optional[float] = None  # Total duration, auto if None
    cd_weir: float = 0.544  # Broad-crested weir coefficient
    cd_side: float = 0.432  # Side flow coefficient
    g: float = 9.81
    mass_tolerance_pct: float = 0.1  # Acceptable mass error (%)


def _interpolate_stage_storage(
    stage_storage: List[Tuple[float, float, float]]
) -> Tuple[interp1d, interp1d, interp1d]:
    """
    Create interpolation functions from stage-storage-area data.
    
    Args:
        stage_storage: List of (elevation_m, volume_m3, area_m2)
        
    Returns:
        (volume_from_elev, area_from_elev, elev_from_volume) interpolators
    """
    ss = np.array(sorted(stage_storage, key=lambda x: x[0]))
    elevations = ss[:, 0]
    volumes = ss[:, 1]
    areas = ss[:, 2]
    
    vol_from_elev = interp1d(elevations, volumes, kind='linear',
                              fill_value='extrapolate', bounds_error=False)
    area_from_elev = interp1d(elevations, areas, kind='linear',
                               fill_value='extrapolate', bounds_error=False)
    elev_from_vol = interp1d(volumes, elevations, kind='linear',
                              fill_value='extrapolate', bounds_error=False)
    
    return vol_from_elev, area_from_elev, elev_from_vol


def _default_stage_storage(dam: DamParameters) -> List[Tuple[float, float, float]]:
    """
    Generate approximate stage-storage curve from dam parameters.
    Assumes a trapezoidal/conical reservoir shape.
    """
    base_elev = dam.crest_elevation_m - dam.height_m
    n_points = 20
    elevations = np.linspace(base_elev, dam.crest_elevation_m, n_points)
    
    # Approximate: volume and area grow with depth^2.5 and depth^1.5
    max_depth = dam.height_m
    V_max = dam.reservoir_volume_m3
    A_max = dam.reservoir_area_m2
    
    depths = elevations - base_elev
    # Power-law approximation
    volumes = V_max * (depths / max_depth) ** 2.5
    areas = A_max * (depths / max_depth) ** 1.5
    
    # Ensure monotonicity
    volumes = np.maximum.accumulate(volumes)
    areas = np.maximum.accumulate(areas)
    
    return [(float(e), float(v), float(a)) for e, v, a in zip(elevations, volumes, areas)]


def compute_breach_hydrograph(
    dam: DamParameters,
    breach: BreachParameters,
    mode: BreachMode,
    inflow_m3s: Optional[np.ndarray] = None,
    inflow_time_s: Optional[np.ndarray] = None,
    config: Optional[ReservoirConfig] = None
) -> BreachHydrograph:
    """
    Compute the breach outflow hydrograph using level-pool reservoir routing.
    
    The breach opening grows linearly (trapezoidal shape) over the formation time.
    Outflow is computed using broad-crested weir hydraulics.
    
    Args:
        dam: Dam parameters
        breach: Computed breach parameters
        mode: Breach failure mode
        inflow_m3s: Upstream inflow discharge (m³/s), constant if None
        inflow_time_s: Time array for inflow (s)
        config: Reservoir routing configuration
        
    Returns:
        BreachHydrograph with Q(t), water levels, and mass conservation error
    """
    if config is None:
        config = ReservoirConfig()
    
    g = config.g
    Cd = config.cd_weir
    Cs = config.cd_side
    
    # Stage-storage relationship
    if dam.stage_storage and len(dam.stage_storage) >= 3:
        stage_storage = dam.stage_storage
    else:
        stage_storage = _default_stage_storage(dam)
    
    vol_from_elev, area_from_elev, elev_from_vol = _interpolate_stage_storage(stage_storage)
    
    # Breach geometry
    B_final = breach.bottom_width_m
    h_breach = breach.depth_m
    z = breach.side_slope
    t_f = breach.formation_time_s
    
    # Breach invert elevation (bottom of breach at full development)
    base_elev = dam.crest_elevation_m - dam.height_m
    breach_invert_final = base_elev  # Breach erodes to dam base
    breach_invert_initial = dam.crest_elevation_m  # Starts at crest
    
    # For piping, breach starts at a lower elevation
    if mode == BreachMode.PIPING:
        piping_start_elev = base_elev + dam.height_m * 0.3
        breach_invert_initial = piping_start_elev
    
    # Inflow function
    if inflow_m3s is not None and inflow_time_s is not None:
        inflow_func = interp1d(inflow_time_s, inflow_m3s, kind='linear',
                                fill_value=(inflow_m3s[0], inflow_m3s[-1]),
                                bounds_error=False)
    else:
        # Assume zero inflow (conservative for dam-break)
        inflow_func = lambda t: 0.0
    
    # Simulation duration
    if config.simulation_duration_s is not None:
        t_end = config.simulation_duration_s
    else:
        # Auto: 5x formation time, minimum 2 hours
        t_end = max(5.0 * t_f, 7200.0)
    
    # Initial conditions
    V0 = float(vol_from_elev(dam.water_level_m))
    initial_volume = V0
    
    # Sudden failure: breach opens instantly
    is_sudden = (mode == BreachMode.SUDDEN)
    
    def breach_geometry(t):
        """Return (bottom_width, invert_elevation) at time t."""
        if is_sudden:
            frac = 1.0
        else:
            frac = min(t / t_f, 1.0) if t_f > 0 else 1.0
        
        B_t = B_final * frac
        invert_t = breach_invert_initial + (breach_invert_final - breach_invert_initial) * frac
        return B_t, invert_t
    
    def outflow(t, V):
        """Compute outflow through breach at time t given reservoir volume V."""
        V = max(V, 0.0)
        h_water = float(elev_from_vol(V))  # Water surface elevation
        
        B_t, invert_t = breach_geometry(t)
        head = h_water - invert_t  # Head above breach invert
        
        if head <= 0 or B_t <= 0:
            return 0.0
        
        # Broad-crested weir: Q = Cd * B * sqrt(2g) * h^1.5 + Cs * z * sqrt(2g) * h^2.5
        sqrt_2g = math.sqrt(2.0 * g)
        Q_rect = Cd * B_t * sqrt_2g * (head ** 1.5)
        Q_tri = Cs * z * sqrt_2g * (head ** 2.5)
        
        return Q_rect + Q_tri
    
    def reservoir_ode(t, y):
        """ODE: dV/dt = Q_in - Q_out"""
        V = y[0]
        Q_in = float(inflow_func(t))
        Q_out = outflow(t, V)
        dVdt = Q_in - Q_out
        return [dVdt]
    
    # Solve ODE
    t_eval = np.arange(0, t_end + config.dt_output, config.dt_output)
    
    sol = solve_ivp(
        reservoir_ode,
        [0, t_end],
        [V0],
        method='RK45',
        t_eval=t_eval,
        max_step=min(config.dt_output, t_f / 20 if t_f > 0 else config.dt_output),
        rtol=1e-8,
        atol=1e-6
    )
    
    if not sol.success:
        raise RuntimeError(f"Reservoir routing failed: {sol.message}")
    
    # Extract results
    times = sol.t
    volumes = np.maximum(sol.y[0], 0.0)
    
    # Compute discharge, water levels, breach width at each time step
    discharges = np.zeros_like(times)
    water_levels = np.zeros_like(times)
    breach_widths = np.zeros_like(times)
    
    for i, (t, V) in enumerate(zip(times, volumes)):
        discharges[i] = outflow(t, V)
        water_levels[i] = float(elev_from_vol(V))
        B_t, _ = breach_geometry(t)
        breach_widths[i] = B_t
    
    # Peak discharge
    peak_idx = np.argmax(discharges)
    peak_Q = float(discharges[peak_idx])
    time_to_peak = float(times[peak_idx])
    
    # Mass conservation check
    total_outflow_vol = np.trapz(discharges, times)
    total_inflow_vol = np.trapz([float(inflow_func(t)) for t in times], times)
    volume_change = initial_volume - float(volumes[-1])
    expected_outflow = volume_change + total_inflow_vol
    
    if expected_outflow > 0:
        mass_error_pct = ((total_outflow_vol - expected_outflow) / expected_outflow) * 100.0
    else:
        mass_error_pct = 0.0
    
    return BreachHydrograph(
        time_s=times,
        discharge_m3s=discharges,
        water_level_m=water_levels,
        breach_width_m=breach_widths,
        peak_discharge_m3s=peak_Q,
        time_to_peak_s=time_to_peak,
        total_volume_m3=total_outflow_vol,
        mass_error_pct=mass_error_pct,
        method=breach.method,
        breach_params=breach
    )


def compute_blockage_release(
    blockage_volume_m3: float,
    lake_volume_m3: float,
    lake_area_m2: float,
    blockage_height_m: float,
    blockage_crest_elevation_m: float,
    lake_level_m: float,
    erosion_rate_m3_per_s: Optional[float] = None,
    config: Optional[ReservoirConfig] = None
) -> BreachHydrograph:
    """
    Compute release hydrograph from a natural dam / landslide-dammed lake.
    
    Uses progressive overtopping erosion of the blockage material.
    If erosion rate not specified, uses empirical estimate.
    """
    if config is None:
        config = ReservoirConfig()
    
    # Estimate formation time from blockage volume
    if erosion_rate_m3_per_s is None:
        # Empirical: Costa & Schuster (1988) - rough estimate
        erosion_rate_m3_per_s = blockage_volume_m3 / (3600 * 6)  # ~6 hours
    
    formation_time = blockage_volume_m3 / erosion_rate_m3_per_s
    
    # Create equivalent dam and breach parameters
    dam = DamParameters(
        height_m=blockage_height_m,
        crest_length_m=blockage_height_m * 4,  # Rough estimate
        crest_elevation_m=blockage_crest_elevation_m,
        reservoir_volume_m3=lake_volume_m3,
        reservoir_area_m2=lake_area_m2,
        water_level_m=lake_level_m,
        dam_type="earthfill"
    )
    
    breach = BreachParameters(
        average_width_m=blockage_height_m * 2,
        bottom_width_m=blockage_height_m,
        depth_m=blockage_height_m,
        formation_time_s=formation_time,
        side_slope=1.5,
        peak_outflow_m3s=0.0,  # Will be computed
        method="Blockage release (progressive erosion)",
        notes=f"Erosion rate: {erosion_rate_m3_per_s:.1f} m³/s"
    )
    
    return compute_breach_hydrograph(dam, breach, BreachMode.BLOCKAGE_RELEASE, config=config)
