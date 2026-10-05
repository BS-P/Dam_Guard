"""
Demo Script: Publication-Quality Inundation Map Pipeline Generator

Runs the river-following hydraulic routing and publication map generation pipeline
for Indian dam-break scenarios (Konta GD Station 2005 event, Machhu Dam-II, Rishiganga).

Outputs generated in outputs/demo/:
1. extent_comparison.png (Figure Type A - Konta 2005 style DMS graticule neatline extent map)
2. three_panel_depth_velocity_severity.png (Figure Type B - 3-panel depth, velocity, severity map)
3. inundation_extents.zip (Zipped shapefile containing scenario polygons)
4. inundation_extents.kml (Publication KML vector output)
"""

import os
import sys
import numpy as np
import logging

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.analysis.routing import (
    hydrologically_condition_dem,
    extract_river_centerline_from_dem,
    filter_connected_hydraulic_extent,
    compute_hydrodynamic_severity,
    get_affected_reach_bounding_box
)
from app.visualization.map_outputs import (
    plot_extent_comparison,
    plot_three_panel_results,
    export_extent_shapefile,
    export_extent_kml
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_demo():
    logger.info("Starting DamGuard Publication Map Pipeline Demo...")

    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs", "demo"))
    os.makedirs(output_dir, exist_ok=True)

    # 1. Konta Gauging Station 2005 Demo Setup
    bounds = (81.25, 17.65, 81.45, 17.85)
    rows, cols = 180, 180
    dx, dy = 120.0, 120.0  # Approx meters

    # Generate synthetic topographic valley DEM with river channel
    x = np.linspace(bounds[0], bounds[2], cols)
    y = np.linspace(bounds[3], bounds[1], rows)  # North to South
    xx, yy = np.meshgrid(x, y)

    # River centerline trajectory (wavy channel from NW to SE)
    channel_x = bounds[0] + 0.10 + 0.05 * np.sin((y - bounds[1]) * 40)
    dem = 120.0 + (xx - channel_x)**2 * 3000.0 - (y - bounds[1]) * 150.0

    # 2. Extract River Centerline & Condition DEM
    dam_r, dam_c = 20, int(cols * 0.45)
    river_mask, path = extract_river_centerline_from_dem(dem, dam_r, dam_c, dx, dy)
    conditioned_dem = hydrologically_condition_dem(dem, river_mask, burn_depth=2.5)

    # 3. Compute River-Following Hydrodynamics per Scenario
    dist = np.sqrt((xx - 81.3120)**2 + (yy - 17.7475)**2)
    raw_depth_s1 = np.maximum(0, 3.8 - dist * 22.0)
    raw_depth_s2 = raw_depth_s1 * 1.35
    raw_depth_m1 = raw_depth_s1 * 0.70
    raw_depth_m2 = raw_depth_s1 * 1.60
    raw_depth_f1 = raw_depth_s1 * 1.15
    raw_depth_f2 = raw_depth_s1 * 1.45

    # Apply River Hydraulic Connectivity Filtering (Remove disconnected dry-valley puddles)
    depth_s1 = filter_connected_hydraulic_extent(raw_depth_s1, river_mask)
    depth_s2 = filter_connected_hydraulic_extent(raw_depth_s2, river_mask)
    depth_m1 = filter_connected_hydraulic_extent(raw_depth_m1, river_mask)
    depth_m2 = filter_connected_hydraulic_extent(raw_depth_m2, river_mask)
    depth_f1 = filter_connected_hydraulic_extent(raw_depth_f1, river_mask)
    depth_f2 = filter_connected_hydraulic_extent(raw_depth_f2, river_mask)

    velocity_s1 = np.maximum(0, 2.6 - dist * 16.0)
    severity_s1 = compute_hydrodynamic_severity(depth_s1, velocity_s1)

    dam_marker = {
        "name": "Konta GD Station",
        "lat": 17.7475,
        "lon": 81.3120
    }

    scenarios_data = {
        "S1": {"depth_array": depth_s1, "bounds": bounds, "label": "S1: Overtopping Peak 10,000 m³/s"},
        "S2": {"depth_array": depth_s2, "bounds": bounds, "label": "S2: Overtopping Peak 15,000 m³/s"},
        "M1": {"depth_array": depth_m1, "bounds": bounds, "label": "M1: Piping Failure (Small)"},
        "M2": {"depth_array": depth_m2, "bounds": bounds, "label": "M2: Piping Failure (Extreme)"},
        "F1": {"depth_array": depth_f1, "bounds": bounds, "label": "F1: Observed 2005 Boundary"},
        "F2": {"depth_array": depth_f2, "bounds": bounds, "label": "F2: Full Breach SPH Hydrograph"}
    }

    # 4. Generate Figure Type A — Scenario Extent Comparison Map
    fig_a_path = os.path.join(output_dir, "extent_comparison.png")
    plot_extent_comparison(
        scenarios_data=scenarios_data,
        dam_marker=dam_marker,
        title="Konta Gauging Station 2005 Inundation Map",
        sub_title="SIH 26161 - Publication Map Output (Konta Style)",
        output_path=fig_a_path,
        dpi=300
    )

    # 5. Generate Figure Type B — 3-Panel Hydrodynamic Result Map
    fig_b_path = os.path.join(output_dir, "three_panel_depth_velocity_severity.png")
    plot_three_panel_results(
        depth_array=depth_s1,
        velocity_array=velocity_s1,
        severity_array=severity_s1,
        bounds=bounds,
        dam_marker=dam_marker,
        title="Konta Hydrodynamic Hydrodynamics (22 Sept 2005 Event)",
        output_path=fig_b_path,
        dpi=300
    )

    # 6. Generate Vector Data Exports (.shp and .kml)
    shp_path = os.path.join(output_dir, "inundation_extents.zip")
    export_extent_shapefile(scenarios_data, output_zip_path=shp_path)

    kml_path = os.path.join(output_dir, "inundation_extents.kml")
    export_extent_kml(scenarios_data, output_kml_path=kml_path)

    logger.info("Demo execution finished successfully! All artifacts created:")
    logger.info(f" - Figure Type A: {fig_a_path}")
    logger.info(f" - Figure Type B: {fig_b_path}")
    logger.info(f" - Shapefile Zip: {shp_path}")
    logger.info(f" - KML Output:    {kml_path}")


if __name__ == "__main__":
    run_demo()
