import os
import csv
import json

def validate_geotiff(filepath: str) -> tuple[bool, str]:
    """Validates if a file is a readable GeoTIFF."""
    if not os.path.exists(filepath):
        return False, "File does not exist."
    if not filepath.lower().endswith(('.tif', '.tiff')):
        return False, "Not a TIFF file extension."
    try:
        import rasterio
        with rasterio.open(filepath) as src:
            _ = src.meta
        return True, "Valid GeoTIFF."
    except Exception as e:
        return False, str(e)

def validate_csv(filepath: str, required_columns: list) -> tuple[bool, str]:
    """Validates a CSV file for required columns."""
    if not os.path.exists(filepath):
        return False, "File does not exist."
    try:
        with open(filepath, 'r', newline='') as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if headers is None:
                return False, "Empty CSV file."
            missing = [col for col in required_columns if col not in headers]
            if missing:
                return False, f"Missing columns: {', '.join(missing)}"
        return True, "Valid CSV."
    except Exception as e:
        return False, str(e)

def validate_geojson(geojson_str: str) -> tuple[bool, str]:
    """Validates a GeoJSON string."""
    try:
        data = json.loads(geojson_str)
        if data.get('type') not in ['FeatureCollection', 'Feature', 'Geometry']:
            return False, "Invalid GeoJSON type."
        return True, "Valid GeoJSON."
    except json.JSONDecodeError as e:
        return False, f"JSON Decode Error: {e}"

def validate_bounds(bounds: list) -> tuple[bool, str]:
    """Validates bounding box coordinates [minx, miny, maxx, maxy]."""
    if len(bounds) != 4:
        return False, "Bounds must have 4 elements."
    minx, miny, maxx, maxy = bounds
    if minx >= maxx or miny >= maxy:
        return False, "Invalid bounds dimensions."
    if not (-180 <= minx <= 180 and -180 <= maxx <= 180):
        return False, "Longitude out of range."
    if not (-90 <= miny <= 90 and -90 <= maxy <= 90):
        return False, "Latitude out of range."
    return True, "Valid bounds."
