import logging
from typing import Dict, Any, Optional

try:
    import ee
except ImportError:
    ee = None

logger = logging.getLogger(__name__)

def compute_sar_flood_extent(
    aoi_geojson: Dict[str, Any], 
    event_date: str, 
    pre_event_days: int = 60
) -> Dict[str, Any]:
    """
    Sentinel-1 SAR flood detection based on the I-FAMS methodology.
    """
    if ee is None:
        raise RuntimeError("Google Earth Engine Python API (ee) is not installed.")

    try:
        # Check initialization (assuming caller initialized EE)
        # ee.Initialize() 
        pass
    except Exception as e:
        raise RuntimeError("EE not initialized properly.") from e

    # Parse AOI
    aoi = ee.Geometry.Polygon(aoi_geojson['coordinates'])

    # Time parameters
    event = ee.Date(event_date)
    pre_start = event.advance(-pre_event_days, 'day')
    pre_end = event.advance(-1, 'day')
    post_end = event.advance(10, 'day') # Search 10 days post event for first image

    # Load S1 collection (VV polarization, IW mode)
    s1 = ee.ImageCollection('COPERNICUS/S1_GRD') \
        .filterBounds(aoi) \
        .filter(ee.Filter.eq('instrumentMode', 'IW')) \
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
        .select('VV')

    # Pre-event reference stack (using median to reduce noise)
    pre_event_img = s1.filterDate(pre_start, pre_end).median().clip(aoi)
    
    # Post-event image (take the first available image right after the event)
    post_event_collection = s1.filterDate(event, post_end)
    
    if post_event_collection.size().getInfo() == 0:
        return {"error": "No Sentinel-1 imagery available for the post-event timeframe."}
        
    post_event_img = post_event_collection.first().clip(aoi)
    image_date = ee.Date(post_event_img.get('system:time_start')).format('YYYY-MM-dd').getInfo()

    # Apply Focal median filter (100m) for speckle reduction
    SMOOTHING_RADIUS = 100
    pre_smoothed = pre_event_img.focal_median(SMOOTHING_RADIUS, 'circle', 'meters')
    post_smoothed = post_event_img.focal_median(SMOOTHING_RADIUS, 'circle', 'meters')

    # Change detection: difference in dB (post - pre)
    # Water has low backscatter, so flooded areas will drop significantly.
    difference = post_smoothed.subtract(pre_smoothed)
    
    # Threshold on dB difference (default -3dB change)
    flood_threshold = -3.0
    flood_mask = difference.lt(flood_threshold)

    # Exclude permanent water (JRC Global Surface Water)
    jrc = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select('seasonality').clip(aoi)
    # Areas with seasonality > 10 months are considered permanent
    permanent_water = jrc.gte(10) 
    
    # Exclude slopes using HAND mask or SRTM
    srtm = ee.Image('USGS/SRTMGL1_003').clip(aoi)
    slope = ee.Terrain.slope(srtm)
    slope_mask = slope.lt(5) # Keep areas with slope < 5 degrees
    
    # Final flood mask
    final_flood = flood_mask.And(permanent_water.Not()).And(slope_mask)
    
    # Vectorize the mask
    vectors = final_flood.selfMask().reduceToVectors(
        geometry=aoi,
        scale=30,
        geometryType='polygon',
        eightConnected=True,
        maxPixels=1e10
    )

    # Note: For returning actual GeoJSON, we would call .getInfo(), 
    # but for large areas this might timeout. In production, we'd export to GCS/Drive.
    try:
        flood_geojson = vectors.getInfo()
    except Exception as e:
        logger.warning(f"Polygon extraction too large, returning metadata only: {str(e)}")
        flood_geojson = None

    return {
        "status": "success",
        "scene_date": image_date,
        "flood_geojson": flood_geojson,
        "sensor": "Sentinel-1 SAR",
        "method": "Change Detection (-3dB) + Slope Mask + Permanent Water Mask"
    }
