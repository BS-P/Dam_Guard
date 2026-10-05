import rasterio
from rasterio.windows import Window
from rasterio.features import rasterize
import numpy as np
import rasterstats
import subprocess

def read_raster(path: str, band: int = 1):
    """Reads a raster and returns data array and metadata."""
    with rasterio.open(path) as src:
        data = src.read(band)
        meta = src.meta.copy()
    return data, meta

def write_raster(path: str, data: np.ndarray, metadata: dict, compress: bool = True):
    """Writes a raster with optional compression."""
    if compress:
        metadata.update(compress='lzw')
    with rasterio.open(path, 'w', **metadata) as dst:
        dst.write(data, 1)

def create_cog(input_path: str, output_path: str) -> str:
    """Converts a GeoTIFF to Cloud Optimized GeoTIFF."""
    # We can use gdal_translate to create COG. Assumes GDAL is in path.
    cmd = [
        "gdal_translate",
        input_path,
        output_path,
        "-co", "COMPRESS=LZW",
        "-co", "TILED=YES",
        "-of", "COG"
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

def raster_point_value(path: str, lat: float, lon: float) -> float:
    """Samples a raster at a given lat, lon."""
    with rasterio.open(path) as src:
        # Assuming lat, lon are in the CRS of the raster. If not, crs.py will need to handle reprojection.
        # Here we just use the provided coordinates.
        gen = src.sample([(lon, lat)])
        val = next(gen)
        return float(val[0])

def raster_profile_along_line(path: str, coords_list: list) -> tuple:
    """Extracts a profile along a list of coordinates."""
    import math
    distances = []
    values = []
    cum_dist = 0.0
    
    with rasterio.open(path) as src:
        gen = src.sample(coords_list)
        for i, val in enumerate(gen):
            if i == 0:
                distances.append(0.0)
            else:
                x1, y1 = coords_list[i-1]
                x2, y2 = coords_list[i]
                dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                cum_dist += dist
                distances.append(cum_dist)
            values.append(float(val[0]))
            
    return distances, values

def raster_stats_in_polygon(path: str, polygon_geojson: dict) -> dict:
    """Calculates raster statistics within a polygon."""
    stats = rasterstats.zonal_stats(
        [polygon_geojson], 
        path, 
        stats="min max mean count",
        nodata=-9999
    )
    if stats:
        res = stats[0]
        # Custom logic for area above threshold could be added if threshold is passed.
        res['area_above_threshold'] = 0.0 # Placeholder
        return res
    return {}
