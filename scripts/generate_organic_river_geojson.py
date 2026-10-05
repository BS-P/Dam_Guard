"""
Script to generate organic, river-conforming flood inundation GeoJSON polygons
for all 4 DamGuard demo datasets (Machhu-II, Konta, Rishiganga, Hirakud).
"""

import json
import numpy as np
from shapely.geometry import LineString, Polygon, MultiPolygon, mapping
from shapely.ops import unary_union

def generate_river_contours(river_coords, buffer_widths):
    """
    Given a list of (lon, lat) centerline coords and a list of buffer widths (in degrees),
    generates smooth organic polygons tracing along the river path.
    """
    line = LineString(river_coords)
    features = []

    # Map depth classes & scenario labels
    classes = [
        {"class": "lt02", "label": "< 0.2m (M1 Piping)", "width_factor": 0.35},
        {"class": "02to05", "label": "0.2 - 0.5m (S1 Overtopping)", "width_factor": 0.55},
        {"class": "05to15", "label": "0.5 - 1.5m (F1 Observed)", "width_factor": 0.75},
        {"class": "15to25", "label": "1.5 - 2.5m (F2 SPH Surge)", "width_factor": 0.90},
        {"class": "gt25", "label": "2.5 - 4.0m (M2 Extreme)", "width_factor": 1.10},
        {"class": "gt5", "label": "> 4.0m (S2 Catastrophic)", "width_factor": 1.30}
    ]

    base_buf = buffer_widths["base_deg"]

    for item in classes:
        buf_dist = base_buf * item["width_factor"]
        poly = line.buffer(buf_dist, cap_style=2, join_style=1)
        
        features.append({
            "type": "Feature",
            "properties": {
                "depth_class": item["class"],
                "label": item["label"]
            },
            "geometry": mapping(poly)
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }


def main():
    # 1. Machhu Dam-II River Path (Morbi, Gujarat)
    machhu_river = [
        [70.8303, 22.8384],
        [70.8350, 22.8280],
        [70.8370, 22.8173],
        [70.8250, 22.8080],
        [70.8080, 22.8180],
        [70.7880, 22.8400],
        [70.7650, 22.8650],
        [70.7400, 22.8900],
        [70.7100, 22.9200],
        [70.6800, 22.9500]
    ]

    # 2. Konta Sabari River Path (Chhattisgarh / AP border)
    konta_river = [
        [81.3850, 17.8100],
        [81.3720, 17.7750],
        [81.3500, 17.7600],
        [81.3120, 17.7475],
        [81.2850, 17.7200],
        [81.2650, 17.6850],
        [81.2500, 17.6400],
        [81.2400, 17.6050]
    ]

    # 3. Rishiganga River Path (Uttarakhand)
    rishiganga_river = [
        [79.7420, 30.4900],
        [79.7150, 30.4980],
        [79.6920, 30.5050],
        [79.6650, 30.5180],
        [79.6450, 30.5250],
        [79.6100, 30.5380],
        [79.5900, 30.5450]
    ]

    # 4. Hirakud Mahanadi River Path (Odisha)
    hirakud_river = [
        [83.8700, 21.5300],
        [83.8950, 21.5050],
        [83.9200, 21.4800],
        [83.9600, 21.4600],
        [84.0200, 21.4100],
        [84.1000, 21.3600],
        [84.2000, 21.3200]
    ]

    machhu_geojson = generate_river_contours(machhu_river, {"base_deg": 0.012})
    konta_geojson = generate_river_contours(konta_river, {"base_deg": 0.015})
    rishi_geojson = generate_river_contours(rishiganga_river, {"base_deg": 0.008})
    hirakud_geojson = generate_river_contours(hirakud_river, {"base_deg": 0.018})

    with open("machhu_exact_geojson.json", "w") as f:
        json.dump(machhu_geojson, f, indent=2)

    with open("konta_exact_geojson.json", "w") as f:
        json.dump(konta_geojson, f, indent=2)

    all_geojson = {
        "proj-machhu-1979": machhu_geojson,
        "proj-konta-2005": konta_geojson,
        "proj-rishiganga-2021": rishi_geojson,
        "proj-hirakud-cwc": hirakud_geojson
    }

    with open("all_scenarios_geojson.json", "w") as f:
        json.dump(all_geojson, f, indent=2)

    print("Organic river GeoJSON contours generated successfully!")

if __name__ == "__main__":
    main()
