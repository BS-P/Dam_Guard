import numpy as np
from scipy.ndimage import binary_dilation, distance_transform_edt, uniform_filter

def compute_fwdet_depth(
    flood_extent_mask: np.ndarray, 
    dem_array: np.ndarray, 
    transform=None, 
    cell_size: float = 30.0
) -> np.ndarray:
    """
    FwDET (Flood Water Depth Estimation Tool) implementation.
    Algorithm based on Cohen et al. (2019, 2022).
    
    Args:
        flood_extent_mask (np.ndarray): 2D boolean array where True indicates flooded pixels.
        dem_array (np.ndarray): 2D array of DEM elevations.
        cell_size (float): Spatial resolution of the raster.
        
    Returns:
        np.ndarray: Estimated water depth array.
    """
    if flood_extent_mask.shape != dem_array.shape:
        raise ValueError("Flood mask and DEM must have the same shape.")

    # 1. Rasterize flood extent boundary
    # Boundary pixels are flooded pixels adjacent to non-flooded pixels
    flooded = flood_extent_mask.astype(bool)
    dilated = binary_dilation(flooded, border_value=0)
    boundary_mask = dilated & ~flooded

    # 2. Extract DEM elevation values at boundary pixels
    # Create an array of boundary elevations, initialized to NaN
    boundary_elevations = np.full_like(dem_array, np.nan, dtype=np.float32)
    boundary_elevations[boundary_mask] = dem_array[boundary_mask]

    # 3 & 4. Propagate boundary elevations inward (Nearest Neighbor approximation for Cost Allocation)
    # We use distance_transform_edt which gives distance and indices of nearest boundary pixel
    # In FwDET, this is typically cost-allocation, but euclidean nearest is the core approximation.
    
    # Invert boundary mask for distance transform (0 at boundary, 1 elsewhere)
    inv_boundary = ~boundary_mask
    
    # Compute indices of nearest boundary pixel for every pixel
    distances, indices = distance_transform_edt(inv_boundary, return_indices=True)
    
    # Propagated water surface elevation (WSE)
    propagated_wse = np.full_like(dem_array, np.nan, dtype=np.float32)
    
    # Apply propagated WSE only where flooded
    y_indices, x_indices = indices[0][flooded], indices[1][flooded]
    propagated_wse[flooded] = dem_array[y_indices, x_indices]
    
    # 5. Apply focal smoothing to reduce terrain noise (3x3 mean filter)
    # Replace NaNs with 0 temporarily for smoothing or mask them
    wse_filled = np.nan_to_num(propagated_wse, nan=0.0)
    smoothed_wse = uniform_filter(wse_filled, size=3)
    
    # Only keep smoothed WSE inside the flood mask
    final_wse = np.where(flooded, smoothed_wse, np.nan)
    
    # 6. Depth = propagated_boundary_elevation - ground_elevation
    depth = final_wse - dem_array
    
    # 7. Clip to >= 0 (no negative depths)
    depth = np.clip(depth, 0, None)
    
    # Return depth map, masked outside flood extent
    depth[~flooded] = np.nan
    return depth
