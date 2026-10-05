import math
from typing import Dict, Any

class BreachHydrograph:
    def __init__(self, time_s: list, discharge_cms: list):
        self.time = time_s
        self.discharge = discharge_cms

def compute_blockage_release(params: Dict[str, Any]) -> BreachHydrograph:
    """
    River blockage / landslide dam release hydrograph generator.
    Utilizes empirical relations for formation time and peak discharge,
    particularly referencing Costa & Schuster (1988) and similar empirical models.
    
    Args:
        params (Dict): Dictionary containing:
            - dam_height (float): Height of the blockage [m]
            - lake_volume (float): Volume of water trapped behind blockage [m^3]
            - dt (float): Time step for hydrograph [s]
            
    Returns:
        BreachHydrograph object with time and discharge arrays.
    """
    H = params.get('dam_height', 10.0)      # meters
    V = params.get('lake_volume', 1e6)      # cubic meters
    dt = params.get('dt', 60.0)             # seconds
    
    # Costa and Schuster (1988) peak discharge for landslide dams:
    # Qp = 0.0158 * (V * H)**0.60
    # where V is in m3, H in m. Result Qp in m3/s.
    Qp = 0.0158 * (V * H)**0.60
    
    # Formation Time (Time to peak)
    # Empirical relation: Tf (hours) ~ roughly proportional to V/Qp
    # For a triangular or simplified hydrograph, time base Tb = 2 * V / Qp (to conserve mass)
    Tb_seconds = (2.0 * V) / Qp
    
    # Time to peak (tp) is often assumed to be ~ 1/3 of total base time for landslide dams
    tp = Tb_seconds / 3.0
    
    time_series = []
    q_series = []
    
    t = 0.0
    while t <= Tb_seconds:
        time_series.append(t)
        
        if t <= tp:
            # Rising limb
            q = Qp * (t / tp)
        else:
            # Falling limb
            q = Qp * (1.0 - ((t - tp) / (Tb_seconds - tp)))
            
        q_series.append(max(0.0, q))
        t += dt
        
    return BreachHydrograph(time_series, q_series)
