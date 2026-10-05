import os
import geopandas as gpd
from ..geospatial.vector_io import write_shapefile

def export_inundation_shapefile(hazard_gdf: gpd.GeoDataFrame, output_dir: str, run_id: str) -> str:
    """
    Exports inundation polygons to a zipped shapefile.
    Includes attributes: hazard_class, depth_range, max_velocity, arrival_time_min, model_tier, run_id
    """
    if hazard_gdf.empty:
        raise ValueError("Hazard GeoDataFrame is empty.")
        
    # Ensure required columns exist, fill with defaults if not
    required_cols = ['hazard_class', 'depth_range', 'max_velocity', 'arrival_time_min', 'model_tier']
    for col in required_cols:
        if col not in hazard_gdf.columns:
            hazard_gdf[col] = 'Unknown'
            
    hazard_gdf['run_id'] = run_id
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"inundation_{run_id}.zip")
    
    return write_shapefile(hazard_gdf, output_path)
