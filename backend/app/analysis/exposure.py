import geopandas as gpd
from shapely.geometry import Polygon
import rasterio
from rasterio.mask import mask

def count_buildings_in_flood(flood_polygon: Polygon, osm_buildings_gdf: gpd.GeoDataFrame) -> int:
    """Counts the number of buildings intersecting the flood polygon."""
    # Ensure CRS match if needed. Assuming they match.
    intersecting = osm_buildings_gdf[osm_buildings_gdf.intersects(flood_polygon)]
    return len(intersecting)

def compute_road_length_in_flood(flood_polygon: Polygon, osm_roads_gdf: gpd.GeoDataFrame) -> float:
    """Computes total length of roads intersecting the flood polygon in kilometers."""
    intersecting = osm_roads_gdf[osm_roads_gdf.intersects(flood_polygon)]
    if intersecting.empty:
        return 0.0
    # Intersection might be a part of the road
    clipped = gpd.clip(intersecting, flood_polygon)
    # Assuming CRS is in meters, otherwise need to reproject
    total_length_m = clipped.length.sum()
    return total_length_m / 1000.0

def compute_population_in_flood(flood_polygon: Polygon, worldpop_raster_path: str) -> float:
    """Estimates population in flood polygon using a population raster."""
    try:
        with rasterio.open(worldpop_raster_path) as src:
            # We assume flood_polygon is in the same CRS as the raster
            out_image, _ = mask(src, [flood_polygon], crop=True, nodata=-9999)
            # Sum up valid population pixels
            valid_data = out_image[out_image != -9999]
            valid_data = valid_data[valid_data > 0]
            return float(valid_data.sum())
    except Exception:
        return 0.0

def compute_landcover_areas(flood_polygon: Polygon, landcover_raster_path: str, transform) -> dict:
    """Computes area of different landcover classes within flood polygon."""
    areas = {}
    try:
        with rasterio.open(landcover_raster_path) as src:
            out_image, _ = mask(src, [flood_polygon], crop=True, nodata=-9999)
            valid_data = out_image[0][out_image[0] != -9999]
            
            unique, counts = np.unique(valid_data, return_counts=True)
            # Assuming transform provides pixel size
            pixel_area = abs(src.transform[0] * src.transform[4])
            
            for cls, count in zip(unique, counts):
                areas[int(cls)] = float(count * pixel_area)
    except Exception:
        pass
    return areas
