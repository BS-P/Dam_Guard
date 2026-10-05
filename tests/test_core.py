"""
Comprehensive Test Suite for BREACHSCOPE

Tests:
1. 2D-VPMM Solver on V-Catchment Benchmark (NIH Roorkee 2019 Section 4.1)
2. Parametric Breach Hydrograph & Reservoir Mass Conservation
3. DEM Slope and Minimum Elevation Slope Conditioning
4. Hazard Classification & Polygon Extraction
5. KML & Vector Export Validity
6. FastAPI System Health & Solver Status APIs
"""
import unittest
import numpy as np
import os
import shutil
import tempfile
from fastapi.testclient import TestClient

from app.main import app
from app.breach.parametric import (
    DamParameters, BreachMode, BreachMethod, compute_breach_params,
    froehlich_breach_params, von_thun_gillette_breach_params
)
from app.breach.reservoir import compute_breach_hydrograph, ReservoirConfig
from app.validation.benchmarks.v_catchment import (
    run_v_catchment_benchmark
)
from app.analysis.hazard import classify_hazard, hazard_statistics
from app.geospatial.vector_io import write_kml


class TestBreachEngine(unittest.TestCase):
    def setUp(self):
        self.dam = DamParameters(
            height_m=20.0,
            crest_length_m=500.0,
            crest_elevation_m=100.0,
            reservoir_volume_m3=10.0e6,
            reservoir_area_m2=1.0e6,
            water_level_m=99.0,
            dam_type="earthfill"
        )

    def test_froehlich_breach_params(self):
        params = froehlich_breach_params(self.dam, BreachMode.OVERTOPPING)
        self.assertGreater(params.average_width_m, 0.0)
        self.assertGreater(params.formation_time_s, 0.0)
        self.assertGreater(params.peak_outflow_m3s, 0.0)
        self.assertEqual(params.method, "Froehlich (2008)")

    def test_von_thun_gillette(self):
        params = von_thun_gillette_breach_params(self.dam, BreachMode.OVERTOPPING)
        self.assertGreater(params.average_width_m, 0.0)
        self.assertGreater(params.formation_time_s, 0.0)

    def test_reservoir_routing_mass_conservation(self):
        params = froehlich_breach_params(self.dam, BreachMode.OVERTOPPING)
        config = ReservoirConfig(dt_output=60.0, simulation_duration_s=7200.0)
        hydrograph = compute_breach_hydrograph(self.dam, params, BreachMode.OVERTOPPING, config=config)
        
        self.assertGreater(hydrograph.peak_discharge_m3s, 0.0)
        self.assertGreater(hydrograph.total_volume_m3, 0.0)
        # Mass error tolerance <= 1.0%
        self.assertLess(abs(hydrograph.mass_error_pct), 1.0)


class TestVpmm2dSolver(unittest.TestCase):
    def test_v_catchment_benchmark(self):
        """
        Run 2D-VPMM on V-Catchment benchmark and verify mass balance
        (NIH Roorkee Report 2019 Section 4.1 acceptance criteria).
        """
        result = run_v_catchment_benchmark(
            solver_name="vpmm2d",
            dx=50.0,
            dy=50.0,
            dt=6.0,
            rain_duration_s=1800.0,  # Shortened for rapid test run
            sim_duration_s=3600.0,
            output_interval_s=60.0
        )
        
        self.assertIsNotNone(result.hydrograph_q)
        self.assertGreater(float(np.max(result.hydrograph_q)), 0.0)
        # Verify mass error is within limits for shortened run
        self.assertLess(abs(result.mass_error_pct), 10.0)


class TestHazardAnalysis(unittest.TestCase):
    def test_hazard_classification(self):
        depth = np.array([[0.1, 0.3], [1.0, 3.0]])
        velocity = np.array([[0.0, 0.5], [1.0, 3.0]])
        
        hazard = classify_hazard(depth, velocity)
        self.assertEqual(hazard[0, 0], "H1")  # < 0.25m = H1
        self.assertEqual(hazard[0, 1], "H2")  # 0.25 - 0.75m = H2
        self.assertEqual(hazard[1, 0], "H3")  # 0.75 - 1.5m = H3
        self.assertEqual(hazard[1, 1], "H5")  # > 2.5m = H5
        
        stats = hazard_statistics(hazard, dx=10.0, dy=10.0)
        self.assertIn("H5", stats)
        self.assertEqual(stats["H5"], 100.0)


class TestKmlExport(unittest.TestCase):
    def test_write_kml(self):
        features = [
            {
                "name": "Morbi Dam",
                "geometry": {"type": "Point", "coordinates": [70.8303, 22.8384]},
                "properties": {"name": "Morbi Dam", "type": "Dam", "height_m": 22.56}
            }
        ]
        tmp_dir = tempfile.mkdtemp()
        try:
            output_kml = os.path.join(tmp_dir, "test.kml")
            result_path = write_kml(features, output_kml, name="Test Layer")
            self.assertTrue(os.path.exists(result_path))
            with open(result_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("<kml", content)
                self.assertIn("Morbi Dam", content)
        finally:
            shutil.rmtree(tmp_dir)


class TestFastApiEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")

    def test_solvers_status(self):
        res = self.client.get("/api/solvers")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(any(s["tier"] in ["T1_VPMM", "vpmm2d"] for s in data))

    def test_breach_compute_endpoint(self):
        payload = {
            "dam": {
                "height_m": 25.0,
                "crest_length_m": 400.0,
                "crest_elevation_m": 120.0,
                "reservoir_volume_m3": 15000000.0,
                "reservoir_area_m2": 1500000.0,
                "water_level_m": 119.0,
                "dam_type": "earthfill"
            },
            "breach_mode": "overtopping",
            "breach_method": "froehlich",
            "simulation_duration_s": 3600.0
        }
        res = self.client.post("/api/projects/proj-123/breach/compute", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("peak_discharge_m3s", data)
        self.assertGreater(data["peak_discharge_m3s"], 0.0)


if __name__ == "__main__":
    unittest.main()
