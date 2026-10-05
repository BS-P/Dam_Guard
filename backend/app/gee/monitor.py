import logging
from typing import Dict, Any, List

try:
    import ee
except ImportError:
    ee = None

logger = logging.getLogger(__name__)

def check_new_scenes(aoi_geojson: Dict[str, Any], last_check_date: str) -> List[str]:
    """
    Check for new Sentinel-1 or Sentinel-2 scenes since `last_check_date`.
    """
    if ee is None:
        raise RuntimeError("EE API not available.")

    aoi = ee.Geometry.Polygon(aoi_geojson['coordinates'])
    start_date = ee.Date(last_check_date)
    end_date = ee.Date(ee.Date(None).millis()) # Now

    s1 = ee.ImageCollection('COPERNICUS/S1_GRD') \
        .filterBounds(aoi) \
        .filterDate(start_date, end_date)
        
    s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(aoi) \
        .filterDate(start_date, end_date)

    s1_ids = s1.aggregate_array('system:index').getInfo()
    s2_ids = s2.aggregate_array('system:index').getInfo()

    return {
        "sentinel-1": s1_ids,
        "sentinel-2": s2_ids
    }

def get_flood_timeline(aoi_geojson: Dict[str, Any], start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Generates a flood extent area over time (time series) using thresholding.
    """
    if ee is None:
        raise RuntimeError("EE API not available.")

    aoi = ee.Geometry.Polygon(aoi_geojson['coordinates'])
    
    # We will compute the flood area for each Sentinel-1 scene in the time window
    s1 = ee.ImageCollection('COPERNICUS/S1_GRD') \
        .filterBounds(aoi) \
        .filter(ee.Filter.eq('instrumentMode', 'IW')) \
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
        .filterDate(start_date, end_date) \
        .select('VV')

    # Reference pre-event baseline (assumed up to start_date)
    baseline_start = ee.Date(start_date).advance(-60, 'day')
    baseline = ee.ImageCollection('COPERNICUS/S1_GRD') \
        .filterBounds(aoi) \
        .filterDate(baseline_start, ee.Date(start_date)) \
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
        .select('VV') \
        .median()

    def calc_area(image):
        img_smoothed = image.focal_median(100, 'circle', 'meters')
        base_smoothed = baseline.focal_median(100, 'circle', 'meters')
        
        diff = img_smoothed.subtract(base_smoothed)
        flood_mask = diff.lt(-3.0) # -3dB drop
        
        area_img = flood_mask.multiply(ee.Image.pixelArea())
        stats = area_img.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=aoi,
            scale=30,
            maxPixels=1e9
        )
        return ee.Feature(None, {
            'date': image.get('system:time_start'),
            'flood_area_sqm': stats.get('VV') # The band name is inherited
        })

    areas_fc = ee.FeatureCollection(s1.map(calc_area))
    results = areas_fc.getInfo()['features']
    
    timeline = []
    for f in results:
        props = f['properties']
        if props.get('flood_area_sqm') is not None:
            # Convert timestamp to ISO date string
            date_str = ee.Date(props['date']).format('YYYY-MM-dd HH:mm:ss').getInfo()
            timeline.append({
                "date": date_str,
                "flood_area_km2": props['flood_area_sqm'] / 1e6
            })
            
    return timeline
