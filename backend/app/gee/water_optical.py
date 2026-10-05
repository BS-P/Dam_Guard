import logging
from typing import Dict, Any

try:
    import ee
except ImportError:
    ee = None

logger = logging.getLogger(__name__)

def compute_optical_flood_extent(
    aoi_geojson: Dict[str, Any], 
    event_date: str
) -> Dict[str, Any]:
    """
    Optical water mapping using Sentinel-2 imagery.
    """
    if ee is None:
        raise RuntimeError("Google Earth Engine Python API (ee) is not installed.")

    aoi = ee.Geometry.Polygon(aoi_geojson['coordinates'])
    
    event = ee.Date(event_date)
    # Search for an image within a 7-day window after the event
    end_date = event.advance(7, 'day')

    # Load Sentinel-2 L2A collection
    s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(aoi) \
        .filterDate(event, end_date)
        
    if s2.size().getInfo() == 0:
        return {"error": "No Sentinel-2 imagery available for the post-event timeframe."}

    # Pick the least cloudy image
    img = s2.sort('CLOUDY_PIXEL_PERCENTAGE').first().clip(aoi)
    image_date = ee.Date(img.get('system:time_start')).format('YYYY-MM-dd').getInfo()

    # Cloud masking using QA60 band
    qa = img.select('QA60')
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
    img = img.updateMask(mask)

    # Compute MNDWI = (Green - SWIR) / (Green + SWIR)
    # S2 bands: Green = B3, SWIR = B11
    mndwi = img.normalizedDifference(['B3', 'B11']).rename('MNDWI')

    # Compute NDWI = (Green - NIR) / (Green + NIR) 
    # S2 bands: Green = B3, NIR = B8
    ndwi = img.normalizedDifference(['B3', 'B8']).rename('NDWI')

    # Threshold MNDWI > 0.1 for water candidates
    water_mask = mndwi.gt(0.1)

    # ESA WorldCover permanent water exclusion (Class 80 is Water)
    worldcover = ee.ImageCollection("ESA/WorldCover/v100").first().clip(aoi)
    permanent_water = worldcover.select('Map').eq(80)

    # Flood = Water candidate AND NOT Permanent Water
    flood_mask = water_mask.And(permanent_water.Not())

    # Vectorize
    vectors = flood_mask.selfMask().reduceToVectors(
        geometry=aoi,
        scale=10,
        geometryType='polygon',
        eightConnected=True,
        maxPixels=1e10
    )

    try:
        flood_geojson = vectors.getInfo()
    except Exception as e:
        logger.warning(f"Polygon extraction too large: {str(e)}")
        flood_geojson = None

    return {
        "status": "success",
        "scene_date": image_date,
        "flood_geojson": flood_geojson,
        "sensor": "Sentinel-2 MSI",
        "method": "MNDWI > 0.1 with Cloud Mask and ESA Permanent Water Exclusion"
    }
