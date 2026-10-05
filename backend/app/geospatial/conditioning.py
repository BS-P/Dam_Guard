"""
DEM conditioning module.

Fills depressions, enforces minimum slopes, and prepares DEMs for hydrodynamic simulation.
Uses WhiteboxTools (MIT license) for depression filling when available,
falls back to a simpler priority-flood fill implementation.

Reference:
    Barnes, R., Lehman, C., Mulla, D. (2014). "Priority-Flood: An Optimal Depression-Filling
    and Watershed-Labeling Algorithm for Digital Elevation Models." Computers & Geosciences.
"""
import numpy as np
import os
import logging
from typing import Optional, Tuple
from dataclasses import dataclass

try:
    import whitebox
    HAS_WHITEBOX = True
except ImportError:
    HAS_WHITEBOX = False

try:
    from numba import njit, prange
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

logger = logging.getLogger(__name__)


@dataclass
class ConditioningResult:
    """Results of DEM conditioning."""
    output_path: str
    n_filled_cells: int
    max_fill_depth_m: float
    mean_fill_depth_m: float
    method: str
    smin_applied: float


def condition_dem_whitebox(
    input_path: str,
    output_path: str,
    flat_increment: float = 0.0001,
    max_depth: Optional[float] = None
) -> ConditioningResult:
    """
    Condition DEM using WhiteboxTools breach/fill depressions.
    
    Uses breach-depressions-least-cost approach (preferred over simple filling
    for hydrodynamic applications as it preserves more natural drainage).
    """
    if not HAS_WHITEBOX:
        raise ImportError("WhiteboxTools not available. Install with: pip install whitebox")
    
    wbt = whitebox.WhiteboxTools()
    wbt.set_verbose_mode(False)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Breach depressions (preferred for hydro modeling)
    try:
        wbt.breach_depressions_least_cost(
            input_path,
            output_path,
            dist=10,
            max_cost=None,
            min_dist=True,
            flat_increment=flat_increment
        )
        method = "WhiteboxTools breach_depressions_least_cost"
    except Exception:
        # Fallback to simple fill
        wbt.fill_depressions(input_path, output_path, flat_increment=flat_increment)
        method = "WhiteboxTools fill_depressions"
    
    # Compute fill statistics
    try:
        import rasterio
        with rasterio.open(input_path) as src_orig:
            dem_orig = src_orig.read(1).astype(np.float64)
        with rasterio.open(output_path) as src_filled:
            dem_filled = src_filled.read(1).astype(np.float64)
        
        diff = dem_filled - dem_orig
        filled_mask = diff > 1e-6
        n_filled = int(np.sum(filled_mask))
        max_fill = float(np.max(diff)) if n_filled > 0 else 0.0
        mean_fill = float(np.mean(diff[filled_mask])) if n_filled > 0 else 0.0
    except Exception:
        n_filled, max_fill, mean_fill = 0, 0.0, 0.0
    
    return ConditioningResult(
        output_path=output_path,
        n_filled_cells=n_filled,
        max_fill_depth_m=max_fill,
        mean_fill_depth_m=mean_fill,
        method=method,
        smin_applied=flat_increment
    )


def _priority_flood_fill(dem: np.ndarray, nodata: float = -9999.0) -> np.ndarray:
    """
    Simple priority-flood depression filling algorithm.
    
    Based on: Barnes et al. (2014) - Priority-Flood algorithm.
    This is a fallback when WhiteboxTools is not available.
    """
    import heapq
    
    nrows, ncols = dem.shape
    filled = dem.copy()
    visited = np.zeros_like(dem, dtype=bool)
    
    # Priority queue: (elevation, row, col)
    pq = []
    
    # Initialize with boundary cells
    for i in range(nrows):
        for j in [0, ncols - 1]:
            if dem[i, j] != nodata:
                heapq.heappush(pq, (dem[i, j], i, j))
                visited[i, j] = True
    for j in range(1, ncols - 1):
        for i in [0, nrows - 1]:
            if dem[i, j] != nodata:
                heapq.heappush(pq, (dem[i, j], i, j))
                visited[i, j] = True
    
    # 8-connected neighbors
    neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    
    while pq:
        elev, i, j = heapq.heappop(pq)
        
        for di, dj in neighbors:
            ni, nj = i + di, j + dj
            if 0 <= ni < nrows and 0 <= nj < ncols and not visited[ni, nj]:
                visited[ni, nj] = True
                if dem[ni, nj] != nodata:
                    new_elev = max(dem[ni, nj], elev)
                    filled[ni, nj] = new_elev
                    heapq.heappush(pq, (new_elev, ni, nj))
    
    return filled


def condition_dem_fallback(
    input_path: str,
    output_path: str,
    s_min: float = 1e-5
) -> ConditioningResult:
    """
    Condition DEM using built-in priority flood fill (when WhiteboxTools unavailable).
    """
    import rasterio
    
    with rasterio.open(input_path) as src:
        dem = src.read(1).astype(np.float64)
        nodata = src.nodata if src.nodata is not None else -9999.0
        profile = src.profile.copy()
    
    # Fill depressions
    filled = _priority_flood_fill(dem, nodata)
    
    # Compute statistics
    diff = filled - dem
    valid_mask = (dem != nodata) & (filled != nodata)
    filled_mask = valid_mask & (diff > 1e-6)
    n_filled = int(np.sum(filled_mask))
    max_fill = float(np.max(diff[filled_mask])) if n_filled > 0 else 0.0
    mean_fill = float(np.mean(diff[filled_mask])) if n_filled > 0 else 0.0
    
    # Write output
    profile.update(dtype='float64')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(filled, 1)
    
    return ConditioningResult(
        output_path=output_path,
        n_filled_cells=n_filled,
        max_fill_depth_m=max_fill,
        mean_fill_depth_m=mean_fill,
        method="Built-in priority flood fill (Barnes et al. 2014)",
        smin_applied=s_min
    )


def condition_dem(
    input_path: str,
    output_path: str,
    s_min: float = 1e-5,
    prefer_whitebox: bool = True
) -> ConditioningResult:
    """
    Condition DEM for hydrodynamic simulation.
    
    Uses WhiteboxTools if available, otherwise falls back to built-in algorithm.
    
    Args:
        input_path: Path to input DEM GeoTIFF
        output_path: Path for output conditioned DEM
        s_min: Minimum slope to enforce
        prefer_whitebox: Whether to prefer WhiteboxTools
        
    Returns:
        ConditioningResult with statistics
    """
    if prefer_whitebox and HAS_WHITEBOX:
        logger.info("Conditioning DEM with WhiteboxTools")
        return condition_dem_whitebox(input_path, output_path, flat_increment=s_min)
    else:
        logger.info("Conditioning DEM with built-in priority flood fill")
        return condition_dem_fallback(input_path, output_path, s_min)


def enforce_minimum_slope(
    dem: np.ndarray,
    dx: float,
    dy: float,
    s_min: float = 1e-5
) -> np.ndarray:
    """
    Enforce minimum slope on DEM for numerical stability.
    
    Slightly adjusts elevations to ensure no cell has zero gradient
    in both x and y directions simultaneously.
    """
    nrows, ncols = dem.shape
    adjusted = dem.copy()
    
    for i in range(1, nrows):
        for j in range(1, ncols):
            if np.isnan(adjusted[i, j]):
                continue
            
            # Check slopes
            sx = abs(adjusted[i, j - 1] - adjusted[i, j]) / dx if j > 0 and not np.isnan(adjusted[i, j - 1]) else s_min
            sy = abs(adjusted[i - 1, j] - adjusted[i, j]) / dy if i > 0 and not np.isnan(adjusted[i - 1, j]) else s_min
            
            # If both slopes are below minimum, apply small increment
            if sx < s_min and sy < s_min:
                # Lower current cell slightly to create minimum slope
                min_neighbor = min(
                    adjusted[i, j - 1] if j > 0 and not np.isnan(adjusted[i, j - 1]) else adjusted[i, j],
                    adjusted[i - 1, j] if i > 0 and not np.isnan(adjusted[i - 1, j]) else adjusted[i, j]
                )
                adjusted[i, j] = min(adjusted[i, j], min_neighbor - s_min * min(dx, dy))
    
    return adjusted
