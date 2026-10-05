import os
from ..export.geotiff import export_result_geotiff
from ..export.shapefile import export_inundation_shapefile
from ..export.geojson import export_inundation_geojson

def export_results(project_id: str, run_id: str, format: str, output_dir: str) -> str:
    """
    Orchestrates the export process based on format.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Mock data for export
    mock_run_result = "dummy_result.tif"
    
    if format.lower() == 'geotiff':
        output_path = os.path.join(output_dir, f"{run_id}.tif")
        # return export_result_geotiff(mock_run_result, "depth", output_path)
        return output_path # Mock return
        
    elif format.lower() == 'shapefile':
        import geopandas as gpd
        dummy_gdf = gpd.GeoDataFrame()
        return export_inundation_shapefile(dummy_gdf, output_dir, run_id)
        
    elif format.lower() == 'geojson':
        output_path = os.path.join(output_dir, f"{run_id}.geojson")
        import geopandas as gpd
        dummy_gdf = gpd.GeoDataFrame()
        return export_inundation_geojson(dummy_gdf, output_path)
        
    else:
        raise ValueError(f"Unsupported format: {format}")
