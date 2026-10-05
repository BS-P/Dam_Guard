"""
Parametric dam breach models.

Implements Froehlich (2008), Von Thun & Gillette (1990), MacDonald & Langridge-Monopolis (1984),
and user-defined breach parameter estimation.

References:
    Froehlich, D.C. (2008). "Embankment Dam Breach Parameters and Their Uncertainties."
        Journal of Hydraulic Engineering, 134(12), 1708-1721.
    Von Thun, J.L. & Gillette, D.R. (1990). "Guidance on Breach Parameters."
        Internal Document, USBR.
    MacDonald, T.C. & Langridge-Monopolis, J. (1984). "Breaching Characteristics of Dam Failures."
        J. Hydraulic Eng., 110(5).
"""
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Tuple
import math


class BreachMode(str, Enum):
    OVERTOPPING = "overtopping"
    PIPING = "piping"
    SUDDEN = "sudden"
    BLOCKAGE_RELEASE = "blockage_release"
    CUSTOM = "custom"


class BreachMethod(str, Enum):
    FROEHLICH = "froehlich"
    VON_THUN_GILLETTE = "von_thun_gillette"
    MACDONALD = "macdonald"
    USER_DEFINED = "user_defined"


@dataclass
class DamParameters:
    """Dam parameters for breach modelling."""
    height_m: float  # Dam height (m)
    crest_length_m: float  # Dam crest length (m)
    crest_elevation_m: float  # Dam crest elevation (m a.s.l.)
    reservoir_volume_m3: float  # Reservoir volume at failure (m³)
    reservoir_area_m2: float  # Reservoir surface area at failure (m²)
    water_level_m: float  # Water level at failure (m a.s.l.)
    # Stage-storage: list of (elevation_m, volume_m3, area_m2)
    stage_storage: Optional[List[Tuple[float, float, float]]] = None
    dam_type: str = "earthfill"  # earthfill, concrete_gravity, concrete_arch, rockfill


@dataclass
class BreachParameters:
    """Computed breach parameters."""
    average_width_m: float
    bottom_width_m: float
    depth_m: float  # Breach depth
    formation_time_s: float
    side_slope: float  # z:1 (H:V)
    peak_outflow_m3s: float
    method: str
    is_estimated: bool = True
    notes: str = ""


@dataclass
class BreachHydrograph:
    """Breach outflow hydrograph Q(t)."""
    time_s: np.ndarray  # Time array (s)
    discharge_m3s: np.ndarray  # Discharge array (m³/s)
    water_level_m: np.ndarray  # Reservoir water level over time (m)
    breach_width_m: np.ndarray  # Breach width over time (m)
    peak_discharge_m3s: float
    time_to_peak_s: float
    total_volume_m3: float
    mass_error_pct: float  # Mass conservation error (%)
    method: str
    breach_params: BreachParameters


def froehlich_breach_params(dam: DamParameters, mode: BreachMode) -> BreachParameters:
    """
    Compute breach parameters using Froehlich (2008) empirical relations.
    
    Froehlich, D.C. (2008). J. Hydraulic Engineering, 134(12), 1708-1721.
    
    B_avg = 0.27 * k_o * V_w^0.32 * h_b^0.04
    t_f = 63.2 * sqrt(V_w / (g * h_b^2))
    Q_p = 0.607 * V_w^0.295 * h_w^1.24  (Froehlich 1995)
    """
    g = 9.81
    V_w = dam.reservoir_volume_m3
    h_b = dam.height_m  # Breach height ≈ dam height
    h_w = dam.water_level_m - (dam.crest_elevation_m - dam.height_m)  # Head above breach invert
    
    if h_w <= 0:
        h_w = dam.height_m * 0.9  # Fallback
    
    # Overtopping / piping factor
    k_o = 1.3 if mode == BreachMode.OVERTOPPING else 1.0
    
    # Average breach width (m)
    B_avg = 0.27 * k_o * (V_w ** 0.32) * (h_b ** 0.04)
    
    # Breach formation time (s)
    t_f = 63.2 * math.sqrt(V_w / (g * h_b ** 2))
    
    # Side slopes
    z = 0.7 if mode == BreachMode.OVERTOPPING else 1.0
    
    # Bottom width
    B_bottom = B_avg - z * h_b
    if B_bottom < 0:
        B_bottom = B_avg * 0.5
        z = (B_avg - B_bottom) / h_b if h_b > 0 else 0.7
    
    # Peak outflow (Froehlich 1995)
    Q_p = 0.607 * (V_w ** 0.295) * (h_w ** 1.24)
    
    return BreachParameters(
        average_width_m=B_avg,
        bottom_width_m=B_bottom,
        depth_m=h_b,
        formation_time_s=t_f,
        side_slope=z,
        peak_outflow_m3s=Q_p,
        method="Froehlich (2008)",
        notes=f"k_o={k_o}, mode={mode.value}"
    )


def von_thun_gillette_breach_params(dam: DamParameters, mode: BreachMode,
                                      erodibility: str = "moderate") -> BreachParameters:
    """
    Compute breach parameters using Von Thun & Gillette (1990).
    
    B_avg = 2.5 * h_w + C_b
    t_f depends on erodibility classification.
    """
    h_w = dam.water_level_m - (dam.crest_elevation_m - dam.height_m)
    if h_w <= 0:
        h_w = dam.height_m * 0.9
    
    V_w = dam.reservoir_volume_m3
    
    # C_b based on reservoir volume
    if V_w < 1.23e6:
        C_b = 6.1
    elif V_w < 6.17e6:
        C_b = 18.3
    elif V_w < 12.3e6:
        C_b = 42.7
    else:
        C_b = 54.9
    
    B_avg = 2.5 * h_w + C_b
    
    # Formation time (hours -> seconds)
    if erodibility == "highly_erodible":
        t_f_hr = 0.015 * h_w
    elif erodibility == "erosion_resistant":
        t_f_hr = 0.020 * h_w + 0.25  # Resistant formulation
    else:  # moderate
        t_f_hr = 0.015 * h_w + 0.1
    
    t_f = t_f_hr * 3600.0  # Convert to seconds
    
    z = 0.5  # Typical side slope for Von Thun-Gillette
    h_b = dam.height_m
    B_bottom = B_avg - z * h_b
    if B_bottom < 0:
        B_bottom = B_avg * 0.5
    
    # Estimate peak outflow using Froehlich (1995) formula as it's commonly paired
    Q_p = 0.607 * (V_w ** 0.295) * (h_w ** 1.24)
    
    return BreachParameters(
        average_width_m=B_avg,
        bottom_width_m=B_bottom,
        depth_m=h_b,
        formation_time_s=t_f,
        side_slope=z,
        peak_outflow_m3s=Q_p,
        method="Von Thun & Gillette (1990)",
        notes=f"C_b={C_b}, erodibility={erodibility}"
    )


def macdonald_breach_params(dam: DamParameters, mode: BreachMode) -> BreachParameters:
    """
    Compute breach parameters using MacDonald & Langridge-Monopolis (1984).
    
    V_er = 0.0261 * (V_w * h_w)^0.769
    t_f = 0.0179 * V_er^0.364  (hours)
    """
    h_w = dam.water_level_m - (dam.crest_elevation_m - dam.height_m)
    if h_w <= 0:
        h_w = dam.height_m * 0.9
    
    V_w = dam.reservoir_volume_m3
    
    # Eroded volume (m³)
    V_er = 0.0261 * ((V_w * h_w) ** 0.769)
    
    # Formation time (hours)
    t_f_hr = 0.0179 * (V_er ** 0.364)
    t_f = t_f_hr * 3600.0
    
    # Estimate breach width from eroded volume and dam geometry
    h_b = dam.height_m
    z = 1.0
    # V_er ≈ h_b * B_avg * dam_width_at_base / 3 (approximate trapezoidal prism)
    dam_base_width = dam.height_m * 3  # Rough estimate
    B_avg = V_er / (h_b * dam_base_width / 2) if h_b > 0 and dam_base_width > 0 else 50.0
    B_avg = max(B_avg, 10.0)
    
    B_bottom = B_avg - z * h_b
    if B_bottom < 0:
        B_bottom = B_avg * 0.5
    
    Q_p = 0.607 * (V_w ** 0.295) * (h_w ** 1.24)
    
    return BreachParameters(
        average_width_m=B_avg,
        bottom_width_m=B_bottom,
        depth_m=h_b,
        formation_time_s=t_f,
        side_slope=z,
        peak_outflow_m3s=Q_p,
        method="MacDonald & Langridge-Monopolis (1984)",
        notes=f"V_er={V_er:.0f} m³"
    )


def compute_breach_params(dam: DamParameters, mode: BreachMode,
                           method: BreachMethod,
                           user_params: Optional[dict] = None) -> BreachParameters:
    """Compute breach parameters using the selected method."""
    if method == BreachMethod.FROEHLICH:
        return froehlich_breach_params(dam, mode)
    elif method == BreachMethod.VON_THUN_GILLETTE:
        return von_thun_gillette_breach_params(dam, mode)
    elif method == BreachMethod.MACDONALD:
        return macdonald_breach_params(dam, mode)
    elif method == BreachMethod.USER_DEFINED:
        if user_params is None:
            raise ValueError("User-defined breach requires explicit parameters")
        return BreachParameters(
            average_width_m=user_params["average_width_m"],
            bottom_width_m=user_params.get("bottom_width_m", user_params["average_width_m"] * 0.8),
            depth_m=user_params["depth_m"],
            formation_time_s=user_params["formation_time_s"],
            side_slope=user_params.get("side_slope", 1.0),
            peak_outflow_m3s=user_params.get("peak_outflow_m3s", 0.0),  # Will be computed
            method="User-defined",
            notes="Parameters specified by user"
        )
    else:
        raise ValueError(f"Unknown breach method: {method}")
