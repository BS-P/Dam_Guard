"""
Hydraulic River Routing & Connected-Component Masking Module

Provides tools for:
1. River centerline extraction and hydrological DEM conditioning (sink filling, channel burning).
2. Connected-component flood propagation along river reaches.
3. Hydraulic connectivity filtering to eliminate non-hydraulically connected dry-valley puddles.
4. Depth (WSE - DEM), Velocity, and Severity (depth x velocity) calculation.
5. Auto-clipping bounding box to the affected reach with buffer.
"""

import numpy as np
import scipy.ndimage as ndimage
from typing import Tuple, Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


def hydrologically_condition_dem(
    dem: np.ndarray,
    river_mask: Optional[np.ndarray] = None,
    burn_depth: float = 2.0,
    fill_sinks: bool = True
) -> np.ndarray:
    """
    Conditions DEM by filling sinks and burning river channels to ensure continuous hydraulic flow.

    Args:
        dem: 2D numpy array of ground elevations (meters).
        river_mask: 2D boolean array indicating river channel cells (optional).
        burn_depth: Depth in meters to lower DEM along river channel cells.
        fill_sinks: If True, fill local depressions using iterative morphological reconstruction.

    Returns:
        Conditioned DEM array.
    """
    conditioned = dem.copy()

    # Step 1: Burn channel if river mask is provided
    if river_mask is not None and np.any(river_mask):
        conditioned[river_mask] = np.maximum(0, conditioned[river_mask] - burn_depth)

    # Step 2: Sink filling using grayscale reconstruction / iterative minimum propagation
    if fill_sinks:
        # Padded array to prevent edge artifacts
        marker = conditioned.copy()
        # Set inner cells to infinity for reconstruction
        marker[1:-1, 1:-1] = np.inf

        # Iterative dilation until convergence
        struct = ndimage.generate_binary_structure(2, 1)  # 4-connectivity
        for _ in range(500):  # Cap iterations for performance
            prev = marker.copy()
            marker = np.maximum(conditioned, ndimage.grey_erosion(marker, footprint=struct))
            if np.array_equal(marker, prev):
                break
        conditioned = marker

    return conditioned


def extract_river_centerline_from_dem(
    dem: np.ndarray,
    dam_row: int,
    dam_col: int,
    dx: float = 30.0,
    dy: float = 30.0,
    max_steps: int = 2000
) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
    """
    Extracts river centerline downstream from dam location by following steepest descent path on DEM.

    Args:
        dem: 2D elevation grid.
        dam_row, dam_col: Grid coordinates of dam structure / release seed.
        dx, dy: Cell resolution in meters.
        max_steps: Maximum path steps downstream.

    Returns:
        Tuple of (river_boolean_mask, list_of_(row,col)_coords).
    """
    rows, cols = dem.shape
    river_mask = np.zeros((rows, cols), dtype=bool)
    path = []

    curr_r, curr_c = dam_row, dam_col
    visited = set()

    for _ in range(max_steps):
        if curr_r < 0 or curr_r >= rows or curr_c < 0 or curr_c >= cols:
            break
        
        river_mask[curr_r, curr_c] = True
        path.append((curr_r, curr_c))
        visited.add((curr_r, curr_c))

        # Find neighbor with lowest elevation
        min_elev = dem[curr_r, curr_c]
        next_r, next_c = curr_r, curr_c

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = curr_r + dr, curr_c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    if (nr, nc) not in visited and dem[nr, nc] < min_elev:
                        min_elev = dem[nr, nc]
                        next_r, next_c = nr, nc

        if (next_r, next_c) == (curr_r, curr_c):
            # Trapped in local sink, step to any unvisited 8-neighbor
            stepped = False
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = curr_r + dr, curr_c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                        next_r, next_c = nr, nc
                        stepped = True
                        break
                if stepped:
                    break
            if not stepped:
                break

        curr_r, curr_c = next_r, next_c

    # Dilate slightly so channel has width
    struct = ndimage.generate_binary_structure(2, 1)
    river_mask = ndimage.binary_dilation(river_mask, structure=struct, iterations=1)

    return river_mask, path


def filter_connected_hydraulic_extent(
    raw_depth: np.ndarray,
    seed_mask: np.ndarray,
    min_depth_threshold: float = 0.05
) -> np.ndarray:
    """
    Enforces river-following hydraulic connectivity using binary connected-component labeling.
    Only inundated cells connected to the seed_mask (river channel / dam breach site) are retained.

    Args:
        raw_depth: 2D array of raw flood depths (m).
        seed_mask: 2D boolean array of river channel / breach seed cells.
        min_depth_threshold: Minimum water depth to consider as inundated (m).

    Returns:
        Filtered 2D depth array with disconnected dry-valley puddles zeroed out.
    """
    inundated = raw_depth >= min_depth_threshold

    # Label connected components (8-connectivity)
    structure = np.ones((3, 3), dtype=int)
    labeled_array, num_features = ndimage.label(inundated, structure=structure)

    if num_features == 0:
        return np.zeros_like(raw_depth)

    # Find component labels that overlap with the seed mask
    seed_labels = np.unique(labeled_array[seed_mask & (labeled_array > 0)])

    if len(seed_labels) == 0:
        # If seed mask didn't hit any inundated cell, pick highest depth seed cell
        valid_coords = np.argwhere(seed_mask)
        if len(valid_coords) > 0:
            # Expand search around seeds
            dilated_seed = ndimage.binary_dilation(seed_mask, iterations=3)
            seed_labels = np.unique(labeled_array[dilated_seed & (labeled_array > 0)])

    # Keep only pixels belonging to connected seed components
    connected_mask = np.isin(labeled_array, seed_labels)

    filtered_depth = np.where(connected_mask, raw_depth, 0.0)
    return filtered_depth


def compute_hydrodynamic_severity(
    depth: np.ndarray,
    velocity: np.ndarray
) -> np.ndarray:
    """
    Computes flood severity / hazard index as the product of depth and velocity:
    Severity (m²/s) = Depth (m) x Velocity (m/s)

    Args:
        depth: 2D depth array (m).
        velocity: 2D velocity magnitude array (m/s).

    Returns:
        2D severity array (m²/s).
    """
    return np.maximum(0.0, depth * velocity)


def get_affected_reach_bounding_box(
    depth_array: np.ndarray,
    dem_bounds: Tuple[float, float, float, float],
    buffer_km: float = 1.0,
    min_depth: float = 0.05
) -> Dict[str, float]:
    """
    Auto-clips bounding box around the affected river reach with a specified buffer in km.

    Args:
        depth_array: 2D array of flood depths.
        dem_bounds: (left/min_x, bottom/min_y, right/max_x, top/max_y) in CRS coords (e.g. WGS84 degrees or UTM meters).
        buffer_km: Buffer distance in kilometers.
        min_depth: Minimum depth threshold to define flood boundary.

    Returns:
        Dict with keys: min_x, min_y, max_x, max_y.
    """
    min_x, min_y, max_x, max_y = dem_bounds
    rows, cols = depth_array.shape

    inundated_indices = np.argwhere(depth_array >= min_depth)

    if len(inundated_indices) == 0:
        return {"min_x": min_x, "min_y": min_y, "max_x": max_x, "max_y": max_y}

    min_row, min_col = inundated_indices.min(axis=0)
    max_row, max_col = inundated_indices.max(axis=0)

    # Convert pixel coords to bounds
    res_x = (max_x - min_x) / cols
    res_y = (max_y - min_y) / rows

    # Coordinate calculation (top to bottom for row)
    clip_min_x = min_x + min_col * res_x
    clip_max_x = min_x + (max_col + 1) * res_x
    clip_max_y = max_y - min_row * res_y
    clip_min_y = max_y - (max_row + 1) * res_y

    # Convert buffer_km to degrees if geographic (approx 1 deg ~ 111 km)
    is_geographic = (abs(min_x) <= 180 and abs(max_x) <= 180 and abs(min_y) <= 90 and abs(max_y) <= 90)
    if is_geographic:
        buf_deg_x = buffer_km / (111.32 * np.cos(np.radians((clip_min_y + clip_max_y) / 2)))
        buf_deg_y = buffer_km / 111.32
        out_min_x = max(min_x, clip_min_x - buf_deg_x)
        out_max_x = min(max_x, clip_max_x + buf_deg_x)
        out_min_y = max(min_y, clip_min_y - buf_deg_y)
        out_max_y = min(max_y, clip_max_y + buf_deg_y)
    else:
        buf_m = buffer_km * 1000.0
        out_min_x = max(min_x, clip_min_x - buf_m)
        out_max_x = min(max_x, clip_max_x + buf_m)
        out_min_y = max(min_y, clip_min_y - buf_m)
        out_max_y = min(max_y, clip_max_y + buf_m)

    return {
        "min_x": out_min_x,
        "min_y": out_min_y,
        "max_x": out_max_x,
        "max_y": out_max_y
    }
