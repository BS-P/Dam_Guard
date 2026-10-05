import geopandas as gpd
from ..geospatial.vector_io import write_geojson

def export_inundation_geojson(hazard_gdf: gpd.GeoDataFrame, output_path: str) -> str:
    """Exports hazard GeoDataFrame to GeoJSON."""
    return write_geojson(hazard_gdf, output_path)
