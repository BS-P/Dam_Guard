import numpy as np
import geopandas as gpd
from rasterio.features import shapes
from shapely.geometry import shape

def compute_arrival_time(depth_timeseries: np.ndarray, times: list, threshold: float = 0.1) -> np.ndarray:
    """
    Computes the arrival time (time of first exceedance of threshold).
    depth_timeseries shape: (time_steps, rows, cols)
    times: list of time values corresponding to time_steps
    """
    arrival_array = np.full(depth_timeseries.shape[1:], np.nan)
    
    for t_idx, t_val in enumerate(times):
        # Find pixels where depth exceeds threshold for the first time
        mask = (depth_timeseries[t_idx] >= threshold) & np.isnan(arrival_array)
        arrival_array[mask] = t_val
        
    return arrival_array

def compute_duration(depth_timeseries: np.ndarray, times: list, threshold: float = 0.1) -> np.ndarray:
    """
    Computes the total duration depth is above threshold.
    """
    # Assuming times are evenly spaced, or we calculate dt for each step
    duration_array = np.zeros(depth_timeseries.shape[1:])
    
    for i in range(1, len(times)):
        dt = times[i] - times[i-1]
        mask = depth_timeseries[i] >= threshold
        duration_array[mask] += dt
        
    return duration_array

def arrival_time_contours(arrival_array: np.ndarray, transform, crs: str, intervals: list) -> gpd.GeoDataFrame:
    """
    Creates contour polygons for arrival times.
    """
    # For simplicity, we bin the arrival times into intervals and convert to polygons
    binned_array = np.zeros(arrival_array.shape, dtype='int32')
    
    for i, interval in enumerate(intervals):
        if i == 0:
            mask = arrival_array <= interval
        else:
            mask = (arrival_array > intervals[i-1]) & (arrival_array <= interval)
        binned_array[mask] = i + 1
        
    results = []
    mask = binned_array > 0
    
    for geom, val in shapes(binned_array, mask=mask, transform=transform):
        interval_idx = int(val) - 1
        results.append({
            'geometry': shape(geom),
            'arrival_time_max': intervals[interval_idx]
        })
        
    gdf = gpd.GeoDataFrame(results, crs=crs) if results else gpd.GeoDataFrame(columns=['geometry', 'arrival_time_max'], crs=crs)
    return gdf
