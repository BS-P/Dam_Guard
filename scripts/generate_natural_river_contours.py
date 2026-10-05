"""
Generates realistic, natural river-conforming flood polygons with varying width
along real river curves for all DamGuard projects.
"""

import json
import numpy as np
from shapely.geometry import LineString, Polygon, MultiPolygon, mapping

def decimal_to_dms(deg, is_lat=True):
    abs_deg = abs(deg)
    d = int(abs_deg)
    m = int((abs_deg - d) * 60)
    s = int(round(((abs_deg - d) * 60 - m) * 60))
    if s == 60:
        m += 1
        s = 0
    if m == 60:
        d += 1
        m = 0
    dir_char = ("N" if deg >= 0 else "S") if is_lat else ("E" if deg >= 0 else "W")
    return f"{d}°{m}'{s}\"{dir_char}"

def create_natural_flood_geometry(centerline_points, scenario_configs):
    """
    Creates organic flood polygons by constructing offset curves along the river centerline
    with realistic width variations at each waypoint.
    """
    pts = np.array(centerline_points)
    n = len(pts)
    
    # Calculate tangent vectors and normals at each waypoint
    normals = []
    for i in range(n):
        if i == 0:
            dx, dy = pts[1] - pts[0]
        elif i == n - 1:
            dx, dy = pts[-1] - pts[-2]
        else:
            dx, dy = pts[i+1] - pts[i-1]
        
        length = np.hypot(dx, dy)
        if length == 0:
            nx, ny = 0, 1
        else:
            # Perpendicular normal (-dy, dx)
            nx, ny = -dy / length, dx / length
        normals.append((nx, ny))
    
    normals = np.array(normals)

    features = []

    for sc in scenario_configs:
        key = sc["key"]
        label = sc["label"]
        depth_class = sc["depth_class"]
        width_scale = sc["width_scale"] # Base width multiplier in degrees
        
        # Left boundary coords
        left_pts = []
        right_pts = []

        for i in range(n):
            # Width expands downstream and fluctuates at bends
            w = width_scale * (0.005 + 0.008 * (i / max(1, n-1)) + 0.003 * np.sin(i * 1.5))
            
            lx = pts[i, 0] + normals[i, 0] * w
            ly = pts[i, 1] + normals[i, 1] * w
            rx = pts[i, 0] - normals[i, 0] * w
            ry = pts[i, 1] - normals[i, 1] * w
            
            left_pts.append([lx, ly])
            right_pts.append([rx, ry])

        # Combine into closed polygon (left downstream + right upstream)
        poly_coords = left_pts + right_pts[::-1] + [left_pts[0]]
        poly_geom = Polygon(poly_coords)
        
        if poly_geom.is_valid and not poly_geom.is_empty:
            features.append({
                "type": "Feature",
                "properties": {
                    "depth_class": depth_class,
                    "label": label,
                    "scenario": key
                },
                "geometry": mapping(poly_geom)
            })

    return {
        "type": "FeatureCollection",
        "features": features
    }


def main():
    scenarios = [
        {"key": "M1", "depth_class": "lt02", "label": "M1: Piping Failure (Small)", "width_scale": 0.4},
        {"key": "S1", "depth_class": "02to05", "label": "S1: Overtopping Peak 10,000 m³/s", "width_scale": 0.65},
        {"key": "F1", "depth_class": "05to15", "label": "F1: Observed Flood Boundary", "width_scale": 0.90},
        {"key": "F2", "depth_class": "15to25", "label": "F2: Full Breach Hydrograph (SPH)", "width_scale": 1.15},
        {"key": "M2", "depth_class": "gt25", "label": "M2: Piping Failure (Extreme)", "width_scale": 1.40},
        {"key": "S2", "depth_class": "gt5", "label": "S2: Overtopping Peak 15,000 m³/s", "width_scale": 1.65}
    ]

    # 1. Machhu Dam-II (Morbi, Gujarat) - Real Machhu River Course
    machhu_river = [
        [70.8303, 22.8384],  # Machhu Dam-II
        [70.8335, 22.8290],
        [70.8370, 22.8173],  # Morbi Town
        [70.8320, 22.8090],
        [70.8210, 22.8040],  # Lalpar
        [70.8080, 22.8150],
        [70.7920, 22.8350],
        [70.7720, 22.8600],
        [70.7480, 22.8850],
        [70.7200, 22.9150],
        [70.6900, 22.9450],
        [70.6600, 22.9700]   # Maliya
    ]

    # 2. Konta GD Station (Chhattisgarh / AP) - Sabari / Kolab River Course
    konta_river = [
        [81.4100, 17.8150],
        [81.3910, 17.8033],
        [81.3750, 17.7800],
        [81.3520, 17.7610],
        [81.3120, 17.7475],  # Konta GD Station
        [81.2880, 17.7250],
        [81.2680, 17.6900],
        [81.2520, 17.6450],
        [81.2410, 17.6080]   # Godavari confluence
    ]

    # 3. Rishiganga / Dhauliganga (Uttarakhand)
    rishiganga_river = [
        [79.7420, 30.4900],  # Rishiganga site
        [79.7200, 30.4960],
        [79.6920, 30.5050],  # Raini Village
        [79.6650, 30.5180],
        [79.6450, 30.5250],  # Tapovan
        [79.6100, 30.5380],
        [79.5850, 30.5480]   # Joshimath
    ]

    # 4. Hirakud Mahanadi River (Odisha)
    hirakud_river = [
        [83.8700, 21.5300],  # Hirakud Dam
        [83.8950, 21.5050],
        [83.9200, 21.4800],
        [83.9600, 21.4600],  # Sambalpur
        [84.0200, 21.4100],
        [84.1000, 21.3600],
        [84.2000, 21.3200]
    ]

    all_geojson = {
        "proj-machhu-1979": create_natural_flood_geometry(machhu_river, scenarios),
        "proj-konta-2005": create_natural_flood_geometry(konta_river, scenarios),
        "proj-rishiganga-2021": create_natural_flood_geometry(rishiganga_river, scenarios),
        "proj-hirakud-cwc": create_natural_flood_geometry(hirakud_river, scenarios)
    }

    with open("all_scenarios_geojson.json", "w") as f:
        json.dump(all_geojson, f, indent=2)

    print("Natural river flood contours generated!")

if __name__ == "__main__":
    main()
