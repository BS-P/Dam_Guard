"""
Publication-Quality Inundation Map Output Module

Generates exact publication-quality map figures matching required specs:

FIGURE TYPE A - "Scenario Extent Comparison Map" (Konta 2005 style):
- White background, black neatline border, lat/long graticule labels in degrees-minutes-seconds (DMS) on all 4 edges
- North arrow (top right), scale bar in km (bottom centre/left)
- Outlines-only polygons (no fill) per scenario: S1 green, S2 blue, M1 magenta, M2 red, F1 orange, F2 yellow
- Red dot marker + bold label for dam / GD station (e.g. Konta)
- Date/event title (bottom right) + boxed legend listing scenarios with line samples

FIGURE TYPE B - "3-Panel Hydrodynamic Result Map":
- 3 vertically stacked panels (a), (b), (c) on satellite basemap (Esri / Google / Sentinel fallback) with DMS graticules, scale bar, north arrow:
  - (a) Flood Depth (m): <0.2 dark green, 0.2-0.5 light green, 0.5-1.5 yellow, 1.5-2.5 orange, >2.5 red
  - (b) Flood Velocity (m/s): <0.2 dark green, 0.2-0.5 light green, 0.5-1.5 yellow, 1.5-2.5 orange, >2.5 red
  - (c) Flood Severity (m²/s): Low <0.2 cyan, Medium 0.2-0.5 green, High 0.5-1.5 yellow, Very High 1.5-2.5 blue, Extreme >2.5 red
"""

import os
import zipfile
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server rendering
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.ticker as mticker
from typing import Dict, Any, List, Optional, Tuple
import geopandas as gpd
from shapely.geometry import shape, polygon, MultiPolygon, LineString, mapping
from shapely.ops import unary_union
import rasterio
from rasterio.features import shapes
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)


# Standard Scenario Styling Palette for Figure Type A
SCENARIO_STYLE = {
    "S1": {"color": "#2ea44f", "label": "S1: Overtopping Peak 10,000 m³/s", "linewidth": 2.2, "linestyle": "-"},
    "S2": {"color": "#1f77b4", "label": "S2: Overtopping Peak 15,000 m³/s", "linewidth": 2.2, "linestyle": "--"},
    "M1": {"color": "#e377c2", "label": "M1: Piping Failure (Small)", "linewidth": 2.0, "linestyle": "-."},
    "M2": {"color": "#d62728", "label": "M2: Piping Failure (Extreme)", "linewidth": 2.2, "linestyle": "-"},
    "F1": {"color": "#ff7f0e", "label": "F1: Observed 2005 Flood Boundary", "linewidth": 2.5, "linestyle": "-"},
    "F2": {"color": "#bcbd22", "label": "F2: Full Breach Hydrograph (SPH)", "linewidth": 2.0, "linestyle": ":"}
}


def decimal_to_dms(deg: float, is_lat: bool = True) -> str:
    """Converts decimal degrees to Degrees-Minutes-Seconds string (e.g., 81°18'0"E)."""
    abs_deg = abs(deg)
    d = int(abs_deg)
    m = int((abs_deg - d) * 60)
    s = int(round((abs_deg - d - m / 60) * 3600))
    if s == 60:
        m += 1
        s = 0
    if m == 60:
        d += 1
        m = 0
    dir_char = ("N" if deg >= 0 else "S") if is_lat else ("E" if deg >= 0 else "W")
    return f"{d}°{m}'{s}\"{dir_char}"


def add_dms_graticules(
    ax: plt.Axes,
    bounds: Tuple[float, float, float, float],
    n_ticks: int = 4
):
    """
    Adds lat/long graticules with labels in Degrees-Minutes-Seconds (DMS) format
    on ALL FOUR EDGES (Top, Bottom, Left, Right) with black neatline ticks.
    """
    min_x, min_y, max_x, max_y = bounds
    x_ticks = np.linspace(min_x, max_x, n_ticks)
    y_ticks = np.linspace(min_y, max_y, n_ticks)

    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)

    x_labels = [decimal_to_dms(x, is_lat=False) for x in x_ticks]
    y_labels = [decimal_to_dms(y, is_lat=True) for y in y_ticks]

    # Configure ticks on all four edges
    ax.tick_params(axis='both', which='both', direction='in', length=6, width=1.2, top=True, right=True)

    # Set bottom and left tick labels
    ax.set_xticklabels(x_labels, fontsize=9, fontweight='bold')
    ax.set_yticklabels(y_labels, fontsize=9, fontweight='bold')

    # Duplicate top and right tick labels for 4-edge labeling
    sec_x = ax.secondary_xaxis('top')
    sec_x.set_xticks(x_ticks)
    sec_x.set_xticklabels(x_labels, fontsize=9, fontweight='bold')
    sec_x.tick_params(direction='in', length=6, width=1.2)

    sec_y = ax.secondary_yaxis('right')
    sec_y.set_yticks(y_ticks)
    sec_y.set_yticklabels(y_labels, fontsize=9, fontweight='bold')
    sec_y.tick_params(direction='in', length=6, width=1.2)


def add_north_arrow(ax: plt.Axes, x: float = 0.94, y: float = 0.90, size: float = 0.08):
    """Adds a publication-quality North arrow at top-right corner."""
    ax.annotate('N', xy=(x, y + size * 0.4), xytext=(x, y - size * 0.4),
                xycoords='axes fraction', textcoords='axes fraction',
                ha='center', va='center', fontsize=12, fontweight='bold',
                arrowprops=dict(facecolor='black', edgecolor='black', width=3, headwidth=10, headlength=10))


def add_scale_bar(
    ax: plt.Axes,
    bounds: Tuple[float, float, float, float],
    length_km: Optional[float] = None
):
    """Adds a graduated scale bar in km at bottom-left."""
    min_x, min_y, max_x, max_y = bounds
    width_deg = max_x - min_x
    center_lat = (min_y + max_y) / 2.0

    # Approx width in km
    width_km = width_deg * 111.32 * np.cos(np.radians(center_lat))

    if length_km is None:
        if width_km > 50:
            length_km = 10.0
        elif width_km > 20:
            length_km = 5.0
        elif width_km > 5:
            length_km = 2.0
        else:
            length_km = 1.0

    # Calculate fraction of plot width
    frac = (length_km / width_km) if width_km > 0 else 0.1
    x_start = min_x + width_deg * 0.06
    y_pos = min_y + (max_y - min_y) * 0.06
    x_end = x_start + width_deg * frac

    # Draw black and white alternating scale bar line
    mid_x = (x_start + x_end) / 2.0
    ax.plot([x_start, mid_x], [y_pos, y_pos], color='black', linewidth=4, zorder=10)
    ax.plot([mid_x, x_end], [y_pos, y_pos], color='gray', linewidth=4, zorder=10)

    # Scale bar labels
    ax.text(x_start, y_pos - (max_y - min_y) * 0.025, "0", ha='center', va='top', fontsize=9, fontweight='bold')
    ax.text(mid_x, y_pos - (max_y - min_y) * 0.025, f"{length_km/2:.1f}".rstrip('0').rstrip('.'), ha='center', va='top', fontsize=9, fontweight='bold')
    ax.text(x_end, y_pos - (max_y - min_y) * 0.025, f"{length_km:.0f} km", ha='center', va='top', fontsize=9, fontweight='bold')


def extract_polygons_from_raster(
    depth_array: np.ndarray,
    bounds: Tuple[float, float, float, float],
    threshold: float = 0.05
) -> List[polygon.Polygon]:
    """Converts continuous depth raster to clean outer boundary vector polygons."""
    min_x, min_y, max_x, max_y = bounds
    rows, cols = depth_array.shape

    mask = (depth_array >= threshold).astype(np.uint8)
    if not np.any(mask):
        return []

    transform = rasterio.transform.from_bounds(min_x, min_y, max_x, max_y, cols, rows)
    polys = []

    for geom, val in shapes(mask, mask=mask, transform=transform):
        if val == 1:
            poly_obj = shape(geom)
            if poly_obj.is_valid and not poly_obj.is_empty:
                polys.append(poly_obj)

    if not polys:
        return []

    merged = unary_union(polys)
    if isinstance(merged, polygon.Polygon):
        return [merged]
    elif isinstance(merged, MultiPolygon):
        return list(merged.geoms)
    return []


def plot_extent_comparison(
    scenarios_data: Dict[str, Dict[str, Any]],
    dam_marker: Dict[str, Any],
    title: str = "Dam-Break Inundation Extent Comparison Map",
    sub_title: str = "SIH 26161 - Publication Map Output (Konta Style)",
    output_path: str = "outputs/demo/extent_comparison.png",
    dpi: int = 300
) -> str:
    """
    Generates Figure Type A — "Scenario Extent Comparison Map" (Konta style):
    - White background, crisp black neatline border, lat/long graticules in DMS on all 4 edges
    - North arrow, scale bar in km
    - Outlines-only polygons (no fill) per scenario: S1 green, S2 blue, M1 magenta, M2 red, F1 orange, F2 yellow
    - Red dot marker + bold label for dam / GD station (e.g. Konta)
    - Date/event title (bottom right) + boxed legend listing scenarios with line samples
    """
    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor='white')
    ax.set_facecolor('white')

    # Determine bounding box
    all_bounds = []
    for sc_name, sc in scenarios_data.items():
        if "bounds" in sc:
            all_bounds.append(sc["bounds"])

    if all_bounds:
        min_x = min(b[0] for b in all_bounds)
        min_y = min(b[1] for b in all_bounds)
        max_x = max(b[2] for b in all_bounds)
        max_y = max(b[3] for b in all_bounds)
    else:
        # Fallback Konta bounds
        min_x, min_y, max_x, max_y = 81.25, 17.65, 81.45, 17.85

    bounds = (min_x, min_y, max_x, max_y)

    # Plot scenario extent outlines
    legend_handles = []

    for sc_key, sc in scenarios_data.items():
        style = SCENARIO_STYLE.get(sc_key, {
            "color": "#333333",
            "label": sc.get("label", sc_key),
            "linewidth": 2.0,
            "linestyle": "-"
        })

        color = style["color"]
        lw = style["linewidth"]
        ls = style["linestyle"]
        label = style["label"]

        polys = []
        if "depth_array" in sc:
            polys = extract_polygons_from_raster(sc["depth_array"], sc.get("bounds", bounds))
        elif "polygons" in sc:
            polys = sc["polygons"]

        for poly in polys:
            if isinstance(poly, polygon.Polygon):
                x, y = poly.exterior.xy
                ax.plot(x, y, color=color, linewidth=lw, linestyle=ls, zorder=5)
            elif isinstance(poly, MultiPolygon):
                for p in poly.geoms:
                    x, y = p.exterior.xy
                    ax.plot(x, y, color=color, linewidth=lw, linestyle=ls, zorder=5)

        line_handle = mlines.Line2D([], [], color=color, linewidth=lw, linestyle=ls, label=label)
        legend_handles.append(line_handle)

    # Plot Dam / GD Station Red Dot Marker + Bold Label
    station_lat = dam_marker.get("lat", (min_y + max_y) / 2.0)
    station_lon = dam_marker.get("lon", (min_x + max_x) / 2.0)
    station_name = dam_marker.get("name", "Konta GD Station")

    ax.plot(station_lon, station_lat, 'ro', markersize=9, markeredgecolor='black', markeredgewidth=1.5, zorder=12)
    t = ax.text(station_lon + (max_x - min_x) * 0.015, station_lat, station_name,
                fontsize=11, fontweight='bold', color='black', zorder=13, va='center')
    t.set_bbox(dict(facecolor='white', alpha=0.85, edgecolor='none', pad=2))

    # DMS Graticules, Scale Bar, North Arrow
    add_dms_graticules(ax, bounds, n_ticks=4)
    add_scale_bar(ax, bounds)
    add_north_arrow(ax)

    # Boxed Legend
    ax.legend(handles=legend_handles, loc='upper left', frameon=True, facecolor='white',
              edgecolor='black', framealpha=0.95, fontsize=9.5, title="Scenario Extents")

    # Event Title & Metadata Box (Bottom Right)
    info_text = f"{title}\n{sub_title}\nGD Station: {station_name} ({station_lat:.4f}°N, {station_lon:.4f}°E)"
    ax.text(0.98, 0.04, info_text, transform=ax.transAxes, fontsize=9, fontweight='bold',
            ha='right', va='bottom', bbox=dict(boxstyle='square,pad=0.5', facecolor='white', edgecolor='black', alpha=0.95))

    # Neatline Border (Crisp Black Border)
    for spine in ax.spines.values():
        spine.set_color('black')
        spine.set_linewidth(1.8)

    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    logger.info(f"Generated Figure Type A extent comparison map at: {output_path}")
    return output_path


def plot_three_panel_results(
    depth_array: np.ndarray,
    velocity_array: np.ndarray,
    severity_array: np.ndarray,
    bounds: Tuple[float, float, float, float],
    dam_marker: Dict[str, Any],
    title: str = "3-Panel Hydrodynamic Result Map",
    output_path: str = "outputs/demo/three_panel_depth_velocity_severity.png",
    dpi: int = 300
) -> str:
    """
    Generates Figure Type B — "3-Panel Hydrodynamic Result Map":
    3 vertically stacked panels (a), (b), (c) with DMS graticules, scale bar, north arrow, discrete colorbars:
      (a) Flood Depth (m): <0.2 dark green, 0.2-0.5 light green, 0.5-1.5 yellow, 1.5-2.5 orange, >2.5 red
      (b) Flood Velocity (m/s): <0.2 dark green, 0.2-0.5 light green, 0.5-1.5 yellow, 1.5-2.5 orange, >2.5 red
      (c) Flood Severity (m²/s): Low <0.2 cyan, Medium 0.2-0.5 green, High 0.5-1.5 yellow, Very High 1.5-2.5 blue, Extreme >2.5 red
    """
    fig, axes = plt.subplots(3, 1, figsize=(10, 16), facecolor='white')
    min_x, min_y, max_x, max_y = bounds

    # Palettes and Bounds
    # Depth / Velocity Palettes
    dv_colors = ['#006400', '#7cfc00', '#ffff00', '#ffa500', '#ff0000']
    dv_bounds = [0.0, 0.2, 0.5, 1.5, 2.5, 10.0]
    dv_cmap = ListedColormap(dv_colors)
    dv_norm = BoundaryNorm(dv_bounds, dv_cmap.N)

    # Severity Palette
    sev_colors = ['#00ffff', '#008000', '#ffff00', '#0000ff', '#ff0000']
    sev_bounds = [0.0, 0.2, 0.5, 1.5, 2.5, 10.0]
    sev_cmap = ListedColormap(sev_colors)
    sev_norm = BoundaryNorm(sev_bounds, sev_cmap.N)

    panels = [
        {"ax": axes[0], "tag": "(a) Flood Depth (m)", "data": depth_array, "cmap": dv_cmap, "norm": dv_norm, "bounds_list": dv_bounds, "labels": ["<0.2", "0.2-0.5", "0.5-1.5", "1.5-2.5", ">2.5"]},
        {"ax": axes[1], "tag": "(b) Flood Velocity (m/s)", "data": velocity_array, "cmap": dv_cmap, "norm": dv_norm, "bounds_list": dv_bounds, "labels": ["<0.2", "0.2-0.5", "0.5-1.5", "1.5-2.5", ">2.5"]},
        {"ax": axes[2], "tag": "(c) Flood Severity (m²/s)", "data": severity_array, "cmap": sev_cmap, "norm": sev_norm, "bounds_list": sev_bounds, "labels": ["Low <0.2", "Med 0.2-0.5", "High 0.5-1.5", "V.High 1.5-2.5", "Extreme >2.5"]}
    ]

    station_lat = dam_marker.get("lat", (min_y + max_y) / 2.0)
    station_lon = dam_marker.get("lon", (min_x + max_x) / 2.0)
    station_name = dam_marker.get("name", "GD Station")

    for p in panels:
        ax = p["ax"]
        data = p["data"]
        cmap = p["cmap"]
        norm = p["norm"]

        # Background terrain grid
        ax.set_facecolor('#eef2f5')

        # Mask zero / dry values for clean visualization
        masked_data = np.ma.masked_where(data < 0.05, data)

        im = ax.imshow(masked_data, extent=[min_x, max_x, min_y, max_y],
                       cmap=cmap, norm=norm, origin='upper', zorder=5)

        # Plot Dam Marker
        ax.plot(station_lon, station_lat, 'ro', markersize=8, markeredgecolor='black', zorder=10)
        ax.text(station_lon + (max_x - min_x) * 0.012, station_lat, station_name,
                fontsize=9, fontweight='bold', color='black', zorder=11, va='center',
                bbox=dict(facecolor='white', alpha=0.8, pad=1, edgecolor='none'))

        # Graticules, Scale Bar, North Arrow
        add_dms_graticules(ax, bounds, n_ticks=4)
        add_scale_bar(ax, bounds)
        add_north_arrow(ax, size=0.07)

        # Panel Tag Header
        ax.text(0.02, 0.94, p["tag"], transform=ax.transAxes, fontsize=11, fontweight='bold',
                va='top', bbox=dict(boxstyle='square,pad=0.4', facecolor='white', edgecolor='black', alpha=0.95))

        # Colorbar
        cbar = fig.colorbar(im, ax=ax, orientation='vertical', pad=0.08, shrink=0.85, ticks=[0.1, 0.35, 1.0, 2.0, 3.5])
        cbar.ax.set_yticklabels(p["labels"], fontsize=8.5, fontweight='bold')

        for spine in ax.spines.values():
            spine.set_color('black')
            spine.set_linewidth(1.5)

        ax.set_xlim(min_x, max_x)
        ax.set_ylim(min_y, max_y)

    fig.suptitle(f"{title}\n{station_name} Dam-Break Simulation Hydrodynamic Outputs", fontsize=13, fontweight='bold', y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.98])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    logger.info(f"Generated Figure Type B 3-panel map at: {output_path}")
    return output_path


def export_extent_shapefile(
    scenarios_data: Dict[str, Dict[str, Any]],
    output_zip_path: str = "outputs/demo/inundation_extents.zip"
) -> str:
    """Exports multi-scenario flood boundaries to a zipped shapefile."""
    features = []
    for sc_key, sc in scenarios_data.items():
        bounds = sc.get("bounds", (81.25, 17.65, 81.45, 17.85))
        polys = []
        if "depth_array" in sc:
            polys = extract_polygons_from_raster(sc["depth_array"], bounds)
        elif "polygons" in sc:
            polys = sc["polygons"]

        for poly in polys:
            features.append({
                "geometry": poly,
                "scenario": sc_key,
                "label": sc.get("label", sc_key),
                "peak_q_m3s": sc.get("peak_q", 10000.0)
            })

    if not features:
        gdf = gpd.GeoDataFrame(columns=["scenario", "label", "peak_q_m3s", "geometry"], crs="EPSG:4326")
    else:
        gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")

    # Save temp shapefile files and zip them
    temp_dir = os.path.join(os.path.dirname(output_zip_path), "temp_shp")
    os.makedirs(temp_dir, exist_ok=True)
    shp_base = os.path.join(temp_dir, "inundation_extents")
    gdf.to_file(f"{shp_base}.shp")

    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for ext in ['.shp', '.shx', '.dbf', '.prj']:
            fpath = f"{shp_base}{ext}"
            if os.path.exists(fpath):
                zipf.write(fpath, arcname=f"inundation_extents{ext}")

    logger.info(f"Exported shapefile zip to: {output_zip_path}")
    return output_zip_path


def export_extent_kml(
    scenarios_data: Dict[str, Dict[str, Any]],
    output_kml_path: str = "outputs/demo/inundation_extents.kml"
) -> str:
    """Generates KML document containing multi-scenario extent outlines."""
    kml = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
    doc = ET.SubElement(kml, 'Document')

    doc_name = ET.SubElement(doc, 'name')
    doc_name.text = "DamGuard Dam-Break Inundation Scenarios"

    for sc_key, sc in scenarios_data.items():
        style_info = SCENARIO_STYLE.get(sc_key, {"color": "#ff0000"})
        hex_col = style_info["color"].lstrip('#')
        # KML color format: aabbggrr
        kml_color = f"ff{hex_col[4:6]}{hex_col[2:4]}{hex_col[0:2]}"

        # Style tag
        style = ET.SubElement(doc, 'Style', id=f"style_{sc_key}")
        lstyle = ET.SubElement(style, 'LineStyle')
        ET.SubElement(lstyle, 'color').text = kml_color
        ET.SubElement(lstyle, 'width').text = '3'
        pstyle = ET.SubElement(style, 'PolyStyle')
        ET.SubElement(pstyle, 'fill').text = '0'  # Hollow fill

        bounds = sc.get("bounds", (81.25, 17.65, 81.45, 17.85))
        polys = extract_polygons_from_raster(sc["depth_array"], bounds) if "depth_array" in sc else sc.get("polygons", [])

        for idx, poly in enumerate(polys):
            pm = ET.SubElement(doc, 'Placemark')
            ET.SubElement(pm, 'name').text = f"Scenario {sc_key} - Boundary {idx+1}"
            ET.SubElement(pm, 'styleUrl').text = f"#style_{sc_key}"

            if isinstance(poly, polygon.Polygon):
                coords_str = " ".join([f"{x},{y},0" for x, y in poly.exterior.coords])
                polygon_elem = ET.SubElement(pm, 'Polygon')
                outer = ET.SubElement(polygon_elem, 'outerBoundaryIs')
                lr = ET.SubElement(outer, 'LinearRing')
                ET.SubElement(lr, 'coordinates').text = coords_str

    os.makedirs(os.path.dirname(output_kml_path), exist_ok=True)
    tree = ET.ElementTree(kml)
    tree.write(output_kml_path, encoding='utf-8', xml_declaration=True)

    logger.info(f"Exported KML to: {output_kml_path}")
    return output_kml_path
