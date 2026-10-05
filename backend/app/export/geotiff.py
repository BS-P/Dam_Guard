import os
from ..geospatial.raster_io import create_cog

def export_result_geotiff(run_result: str, layer_name: str, output_path: str) -> str:
    """
    Exports a simulation result layer as a Cloud Optimized GeoTIFF (COG).
    """
    # Assuming run_result is a path to a directory or a source TIFF
    # For this implementation, we assume run_result points to a valid GeoTIFF
    if not os.path.exists(run_result):
        raise FileNotFoundError(f"Source file not found: {run_result}")
    
    # In a real scenario, layer_name might dictate which band or file to pick
    # We will just convert the source to COG
    return create_cog(run_result, output_path)
