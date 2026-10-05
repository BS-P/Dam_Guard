import geopandas as gpd
import rasterio
from rasterio.sample import sample_gen

def depth_damage_curve(depth_m: float, building_type: str = 'residential') -> float:
    """
    Returns damage ratio (0-1) for a given depth based on generic curves.
    Inspired by JRC 2017 global depth-damage curves.
    Label everything as ESTIMATED.
    """
    if depth_m <= 0:
        return 0.0
    
    # Simplified piecewise linear curves
    if building_type == 'residential':
        if depth_m < 0.5:
            return 0.2 * (depth_m / 0.5)
        elif depth_m < 1.0:
            return 0.2 + 0.2 * ((depth_m - 0.5) / 0.5)
        elif depth_m < 2.0:
            return 0.4 + 0.3 * ((depth_m - 1.0) / 1.0)
        elif depth_m < 3.0:
            return 0.7 + 0.2 * ((depth_m - 2.0) / 1.0)
        else:
            return min(1.0, 0.9 + 0.1 * ((depth_m - 3.0) / 1.0))
    else: # Commercial/Industrial etc.
        if depth_m < 1.0:
            return 0.3 * (depth_m / 1.0)
        elif depth_m < 3.0:
            return 0.3 + 0.5 * ((depth_m - 1.0) / 2.0)
        else:
            return min(1.0, 0.8 + 0.2 * ((depth_m - 3.0) / 1.0))

def estimate_building_damage(buildings_gdf: gpd.GeoDataFrame, depth_raster_path: str, cost_per_building: float = None) -> dict:
    """
    Estimates building damage by sampling depth at building locations.
    """
    if cost_per_building is None:
        cost_per_building = 100000.0 # Arbitrary default
        
    centroids = buildings_gdf.geometry.centroid
    coords = [(pt.x, pt.y) for pt in centroids]
    
    total_damage_ratio = 0.0
    count = 0
    
    try:
        with rasterio.open(depth_raster_path) as src:
            for val in src.sample(coords):
                depth = val[0]
                if depth > 0 and depth != src.nodata:
                    ratio = depth_damage_curve(depth)
                    total_damage_ratio += ratio
                    count += 1
    except Exception as e:
        print(f"Error sampling depth raster: {e}")
        
    estimated_monetary_loss = total_damage_ratio * cost_per_building
    
    return {
        "status": "ESTIMATED",
        "buildings_affected": count,
        "total_damage_ratio_sum": total_damage_ratio,
        "estimated_monetary_loss": estimated_monetary_loss,
        "note": "Uses estimated JRC 2017 global depth-damage curves."
    }
