import pyproj
from shapely.geometry import Polygon
import pyproj.geod
from shapely.ops import transform

def detect_utm_zone(lon: float, lat: float) -> str:
    """Detects UTM zone EPSG code for a given longitude and latitude."""
    zone_number = int((lon + 180) / 6) + 1
    hemisphere = '6' if lat >= 0 else '7'
    return f"EPSG:32{hemisphere}{zone_number:02d}"

def transform_coords(coords: list, from_crs: str, to_crs: str) -> list:
    """Transforms a list of (x,y) coordinates from one CRS to another."""
    transformer = pyproj.Transformer.from_crs(from_crs, to_crs, always_xy=True)
    transformed = [transformer.transform(x, y) for x, y in coords]
    return transformed

def geodesic_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Calculates geodesic distance between two points in meters."""
    geod = pyproj.Geod(ellps='WGS84')
    _, _, dist = geod.inv(lon1, lat1, lon2, lat2)
    return float(dist)

def geodesic_area(polygon_coords: list) -> float:
    """Calculates geodesic area of a polygon in square meters."""
    geod = pyproj.Geod(ellps='WGS84')
    poly = Polygon(polygon_coords)
    area, _ = geod.geometry_area_perimeter(poly)
    return abs(float(area))

def get_crs_info(crs_string: str) -> dict:
    """Gets basic information about a CRS."""
    crs = pyproj.CRS.from_string(crs_string)
    return {
        "name": crs.name,
        "is_geographic": crs.is_geographic,
        "is_projected": crs.is_projected,
        "units": getattr(crs.axis_info[0], 'unit_name', 'unknown') if crs.axis_info else 'unknown'
    }
