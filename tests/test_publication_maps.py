"""
Unit tests for Publication Map Module & River Connectivity Pipeline.
"""

import os
import sys
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.analysis.routing import (
    filter_connected_hydraulic_extent,
    compute_hydrodynamic_severity,
    hydrologically_condition_dem,
    get_affected_reach_bounding_box
)
from app.visualization.map_outputs import (
    decimal_to_dms,
    plot_extent_comparison,
    plot_three_panel_results
)


def test_decimal_to_dms():
    """Verify degrees to DMS conversion for lat/lon graticules."""
    assert decimal_to_dms(81.30, is_lat=False) == "81°18'0\"E"
    assert decimal_to_dms(17.75, is_lat=True) == "17°45'0\"N"
    assert decimal_to_dms(-12.50, is_lat=True) == "12°30'0\"S"


def test_hydraulic_connected_component_filtering():
    """Verify that disconnected dry-valley puddles are masked out."""
    raw_depth = np.zeros((10, 10))
    # River channel connected flood
    raw_depth[0:5, 2] = 1.5
    # Disconnected puddle in dry valley
    raw_depth[7:9, 8] = 2.0

    seed_mask = np.zeros((10, 10), dtype=bool)
    seed_mask[0, 2] = True  # Dam breach seed at channel head

    filtered = filter_connected_hydraulic_extent(raw_depth, seed_mask, min_depth_threshold=0.1)

    # Connected river flood should be retained
    assert np.all(filtered[0:5, 2] == 1.5)
    # Disconnected puddle must be zeroed out
    assert np.all(filtered[7:9, 8] == 0.0)


def test_hydrodynamic_severity_calculation():
    """Verify severity index = depth x velocity."""
    depth = np.array([[1.0, 2.0], [0.5, 0.0]])
    velocity = np.array([[2.0, 1.5], [1.0, 3.0]])

    severity = compute_hydrodynamic_severity(depth, velocity)
    expected = np.array([[2.0, 3.0], [0.5, 0.0]])

    np.testing.assert_allclose(severity, expected)


def test_dem_conditioning():
    """Verify river channel burning lowers elevation along channel."""
    dem = np.ones((5, 5)) * 100.0
    river_mask = np.zeros((5, 5), dtype=bool)
    river_mask[2, :] = True

    conditioned = hydrologically_condition_dem(dem, river_mask, burn_depth=3.0, fill_sinks=False)
    assert np.all(conditioned[2, :] == 97.0)
    assert np.all(conditioned[0, :] == 100.0)


def test_figure_rendering_without_error(tmp_path):
    """Verify error-free generation of Figure Type A and Type B maps."""
    bounds = (81.25, 17.65, 81.45, 17.85)
    depth = np.ones((30, 30)) * 1.5
    velocity = np.ones((30, 30)) * 0.8
    severity = depth * velocity

    scenarios = {
        "S1": {"depth_array": depth, "bounds": bounds, "label": "S1 Test"}
    }
    dam_marker = {"name": "Test GD Station", "lat": 17.75, "lon": 81.35}

    out_a = os.path.join(tmp_path, "test_fig_a.png")
    out_b = os.path.join(tmp_path, "test_fig_b.png")

    fig_a_res = plot_extent_comparison(scenarios, dam_marker, output_path=out_a)
    fig_b_res = plot_three_panel_results(depth, velocity, severity, bounds, dam_marker, output_path=out_b)

    assert os.path.exists(fig_a_res)
    assert os.path.exists(fig_b_res)
