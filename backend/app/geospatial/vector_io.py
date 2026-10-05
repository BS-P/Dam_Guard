import geopandas as gpd
import json
import xml.etree.ElementTree as ET
import zipfile
import os
from shapely.geometry import Point, LineString, Polygon

def write_shapefile(gdf: gpd.GeoDataFrame, output_path: str) -> str:
    """Writes a GeoDataFrame to a zipped shapefile."""
    temp_dir = output_path.replace('.zip', '')
    os.makedirs(temp_dir, exist_ok=True)
    base_name = os.path.basename(temp_dir)
    shp_path = os.path.join(temp_dir, f"{base_name}.shp")
    gdf.to_file(shp_path)
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.startswith(base_name):
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, arcname=file)
                    
    # Clean up temp dir files could be done here
    return output_path

def write_kml(features, output_path: str, name: str) -> str:
    """Writes features to a KML file using xml.etree.ElementTree."""
    kml_ns = "http://www.opengis.net/kml/2.2"
    ET.register_namespace('', kml_ns)
    kml = ET.Element('kml', xmlns=kml_ns)
    doc = ET.SubElement(kml, 'Document')
    name_el = ET.SubElement(doc, 'name')
    name_el.text = name

    # Define styles for hazard classes
    styles = {
        'H1': 'ff00ff00', # Green
        'H2': 'ff00ffff', # Yellow
        'H3': 'ff00aaff', # Orange
        'H4': 'ff0000ff', # Red
        'H5': 'ff0000aa'  # Dark Red
    }
    
    for cls, color in styles.items():
        style = ET.SubElement(doc, 'Style', id=f"style_{cls}")
        polystyle = ET.SubElement(style, 'PolyStyle')
        color_el = ET.SubElement(polystyle, 'color')
        color_el.text = color

    for feature in features:
        pm = ET.SubElement(doc, 'Placemark')
        geom = feature.get('geometry')
        props = feature.get('properties', {})
        
        name_prop = props.get('name', 'Feature')
        pm_name = ET.SubElement(pm, 'name')
        pm_name.text = str(name_prop)
        
        desc = ET.SubElement(pm, 'description')
        desc.text = str(props.get('description', ''))
        
        hz_class = props.get('hazard_class', 'H1')
        styleurl = ET.SubElement(pm, 'styleUrl')
        styleurl.text = f"#style_{hz_class}"
        
        ext_data = ET.SubElement(pm, 'ExtendedData')
        for k, v in props.items():
            data = ET.SubElement(ext_data, 'Data', name=k)
            val = ET.SubElement(data, 'value')
            val.text = str(v)
            
        if geom['type'] == 'Polygon':
            poly = ET.SubElement(pm, 'Polygon')
            outer = ET.SubElement(poly, 'outerBoundaryIs')
            linering = ET.SubElement(outer, 'LinearRing')
            coords = ET.SubElement(linering, 'coordinates')
            coords_str = " ".join([f"{c[0]},{c[1]}" for c in geom['coordinates'][0]])
            coords.text = coords_str
            
        elif geom['type'] == 'Point':
            pt = ET.SubElement(pm, 'Point')
            coords = ET.SubElement(pt, 'coordinates')
            coords.text = f"{geom['coordinates'][0]},{geom['coordinates'][1]}"
            
        elif geom['type'] == 'LineString':
            ls = ET.SubElement(pm, 'LineString')
            coords = ET.SubElement(ls, 'coordinates')
            coords_str = " ".join([f"{c[0]},{c[1]}" for c in geom['coordinates']])
            coords.text = coords_str

    tree = ET.ElementTree(kml)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    return output_path

def write_geojson(gdf_or_features, output_path: str) -> str:
    """Writes a GeoDataFrame or list of features to a GeoJSON file."""
    if isinstance(gdf_or_features, gpd.GeoDataFrame):
        gdf_or_features.to_file(output_path, driver="GeoJSON")
    else:
        feature_collection = {
            "type": "FeatureCollection",
            "features": gdf_or_features
        }
        with open(output_path, 'w') as f:
            json.dump(feature_collection, f)
    return output_path

def read_vector(path: str) -> gpd.GeoDataFrame:
    """Reads a vector file into a GeoDataFrame."""
    return gpd.read_file(path)
