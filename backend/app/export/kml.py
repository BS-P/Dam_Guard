import geopandas as gpd
import json
from ..geospatial.vector_io import write_kml

def export_inundation_kml(hazard_gdf: gpd.GeoDataFrame, settlements_gdf: gpd.GeoDataFrame, evacuation_routes: list, output_path: str) -> str:
    """
    Exports to KML using the custom XML KML writer.
    Styles polygons by hazard class.
    Includes settlement placemarks and evacuation route lines.
    """
    features = []
    
    # Process hazard polygons
    if not hazard_gdf.empty:
        hazard_json = json.loads(hazard_gdf.to_json())
        for f in hazard_json.get('features', []):
            f['properties']['name'] = f"Hazard {f['properties'].get('hazard_class', '')}"
            features.append(f)
            
    # Process settlements
    if settlements_gdf is not None and not settlements_gdf.empty:
        settle_json = json.loads(settlements_gdf.to_json())
        for f in settle_json.get('features', []):
            f['properties']['name'] = f['properties'].get('name', 'Settlement')
            features.append(f)
            
    # Process evacuation routes (assuming they are dicts with route_geometry)
    if evacuation_routes:
        for i, route in enumerate(evacuation_routes):
            geom = route.get('route_geometry')
            if geom:
                feature = {
                    'type': 'Feature',
                    'geometry': geom.__geo_interface__,
                    'properties': {
                        'name': f'Evacuation Route {i+1}',
                        'distance_m': route.get('distance_m', 0)
                    }
                }
                features.append(feature)
                
    return write_kml(features, output_path, name="Inundation Analysis")
