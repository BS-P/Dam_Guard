import numpy as np
import geopandas as gpd
from rasterio.features import shapes
from shapely.geometry import shape

def classify_hazard(depth_array: np.ndarray, velocity_array: np.ndarray, thresholds: dict = None) -> np.ndarray:
    """
    Classifies hazard based on depth and velocity.
    Default thresholds: H1(<0.25m), H2(0.25-0.75m), H3(0.75-1.5m), H4(1.5-2.5m), H5(>2.5m or dv>7)
    """
    if thresholds is None:
        thresholds = {
            'H1': 0.25,
            'H2': 0.75,
            'H3': 1.5,
            'H4': 2.5
        }
    
    hazard = np.full(depth_array.shape, 'H0', dtype='<U2') # H0 for no hazard
    dv_product = depth_array * velocity_array
    
    # Apply conditions in order
    mask_h1 = (depth_array > 0) & (depth_array <= thresholds['H1'])
    mask_h2 = (depth_array > thresholds['H1']) & (depth_array <= thresholds['H2'])
    mask_h3 = (depth_array > thresholds['H2']) & (depth_array <= thresholds['H3'])
    mask_h4 = (depth_array > thresholds['H3']) & (depth_array <= thresholds['H4'])
    mask_h5 = (depth_array > thresholds['H4']) | (dv_product > 7.0)
    
    hazard[mask_h1] = 'H1'
    hazard[mask_h2] = 'H2'
    hazard[mask_h3] = 'H3'
    hazard[mask_h4] = 'H4'
    hazard[mask_h5] = 'H5'
    
    return hazard

def hazard_to_polygons(hazard_array: np.ndarray, transform, crs: str) -> gpd.GeoDataFrame:
    """Converts a hazard array to a GeoDataFrame of polygons."""
    # We map string classes to integers for rasterio.features.shapes
    mapping = {'H0': 0, 'H1': 1, 'H2': 2, 'H3': 3, 'H4': 4, 'H5': 5}
    rev_mapping = {v: k for k, v in mapping.items()}
    
    int_array = np.vectorize(mapping.get)(hazard_array).astype('int32')
    mask = int_array > 0
    
    results = []
    for geom, val in shapes(int_array, mask=mask, transform=transform):
        results.append({
            'geometry': shape(geom),
            'hazard_class': rev_mapping[int(val)]
        })
        
    gdf = gpd.GeoDataFrame(results, crs=crs) if results else gpd.GeoDataFrame(columns=['geometry', 'hazard_class'], crs=crs)
    return gdf

def hazard_statistics(hazard_array: np.ndarray, dx: float, dy: float) -> dict:
    """Computes area statistics per hazard class."""
    cell_area = abs(dx * dy)
    unique, counts = np.unique(hazard_array, return_counts=True)
    stats = {}
    for cls, count in zip(unique, counts):
        if cls != 'H0':
            stats[cls] = float(count * cell_area)
    return stats
