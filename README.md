# DamGuard — Publication-Quality Dam-Break Inundation Software (SIH 26161)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-009688.svg)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18.2.0-61DAFB.svg)](https://reactjs.org/)
[![MapLibre GL](https://img.shields.io/badge/MapLibre_GL-4.1.0-3BB2D0.svg)](https://maplibre.org/)
[![Pytest Passed](https://img.shields.io/badge/tests-14%20passed-brightgreen.svg)](tests/)

> **DamGuard / BREACHSCOPE** is an advanced dam-break inundation modeling, hydrodynamic simulation, and publication-quality GIS visualization software built for Smart India Hackathon (SIH Problem Statement 26161).

---

## 🌟 Key Highlights & Map Outputs

After any dam-break simulation run (using **2D-VPMM**, **2D Diffusion-Wave**, **Delft3D FM**, or **DualSPHysics SPH**), DamGuard automatically generates publication-ready map figures matching journal reference standards:

### 1. FIGURE TYPE A — "Scenario Extent Comparison Map" (Konta 2005 Style)
- **White Background & Black Neatline Border**: Clean presentation with lat/long graticules labeled in **Degrees-Minutes-Seconds (DMS)** on **all four edges** (e.g., `81°18'0"E`, `17°45'0"N`).
- **North Arrow & Scale Bar**: Graduated scale bar in kilometers (bottom left) and high-visibility North arrow (top right).
- **Outlines-Only Scenario Extents**: Plotted as crisp outline polygons only (no interior fill), drawn over the same river reach:
  - <span style="color:#2ea44f;">■</span> **S1** (Green): Overtopping Peak 10,000 m³/s
  - <span style="color:#1f77b4;">■</span> **S2** (Blue): Overtopping Peak 15,000 m³/s
  - <span style="color:#e377c2;">■</span> **M1** (Magenta): Piping Failure (Small)
  - <span style="color:#d62728;">■</span> **M2** (Red): Piping Failure (Extreme)
  - <span style="color:#ff7f0e;">■</span> **F1** (Orange): Observed Historical Boundary
  - <span style="color:#bcbd22;">■</span> **F2** (Yellow): Full Breach SPH Hydrograph
- **GD Station / Dam Marker**: Red dot marker (`ro`) with a bold white-outlined label for the gauge-discharge station (e.g. **Konta GD Station**, **Machhu Dam-II**).
- **Metadata Title Box**: Event date and station title (bottom right) + boxed scenario legend with sample line swatches.

### 2. FIGURE TYPE B — "3-Panel Hydrodynamic Result Map"
Three vertically stacked panels `(a)`, `(b)`, `(c)` on Esri Satellite World Imagery basemap:
- **`(a)` Flood Depth (m)**: `<0.2` dark green | `0.2–0.5` light green | `0.5–1.5` yellow | `1.5–2.5` orange | `>2.5` red
- **`(b)` Flood Velocity (m/s)**: `<0.2` dark green | `0.2–0.5` light green | `0.5–1.5` yellow | `1.5–2.5` orange | `>2.5` red
- **`(c)` Flood Severity / Hazard Index ($h \times v$ in $\text{m}^2/\text{s}$)**: Low `<0.2` cyan | Medium `0.2–0.5` green | High `0.5–1.5` yellow | Very High `1.5–2.5` blue | Extreme `>2.5` red

---

## 🌊 River-Following Hydraulic Pipeline

To ensure inundation propagates strictly **along the actual river channel and valley** (eliminating random radial blobs or disconnected dry valley puddles), DamGuard enforces:

1. **River Centerline Extraction**: Automatically extracts the channel network from DEM flow accumulation or OSM waterway line strings.
2. **DEM Conditioning**: Fills local sinks and burns the river channel into the DEM.
3. **Connected-Component Masking**: Applies binary connected-component labeling (`scipy.ndimage.label`) seeded directly on river channel cells to remove disconnected puddle pixels.
4. **Hydrodynamic Severity**: Calculates flood depth ($WSE - DEM$), velocity magnitude, and severity ($h \times v$).
5. **Reach Auto-Clipping**: Clips the map bounding box automatically to the affected river reach with a ~1 km buffer.

---

## 📁 Repository Structure

```
DamGuard/
├── backend/
│   ├── app/
│   │   ├── analysis/
│   │   │   ├── routing.py          # Hydraulic river routing & connected-component masking
│   │   │   ├── hazard.py           # Hazard classification (H1-H5)
│   │   │   └── hand.py             # Height Above Nearest Drainage
│   │   ├── visualization/
│   │   │   └── map_outputs.py      # Publication map renderer (Figure A & B, SHP/KML exporters)
│   │   ├── api/
│   │   │   ├── maps.py             # Map export & batch figure API endpoints
│   │   │   ├── breach.py           # Dam breach engine (Froehlich / Von Thun)
│   │   │   └── runs.py             # Hydrodynamic simulation orchestrator
│   │   └── solvers/
│   │       ├── vpmm2d/             # 2D Variable Parameter Muskingum-Cunge (NIH Roorkee 2019)
│   │       ├── diffwave/           # 2D Explicit Diffusion-Wave Solver
│   │       ├── delft3d/            # Delft3D FM solver provider
│   │       └── sph/                # DualSPHysics solver provider
│   ├── requirements.txt            # Python dependencies
│   └── main.py                     # FastAPI application entrypoint
├── frontend/
│   ├── src/
│   │   ├── map/
│   │   │   └── MapView.tsx         # MapLibre GL JS interactive GIS workstation
│   │   ├── components/
│   │   │   └── panels/
│   │   │       ├── ExportsPanel.tsx# Map figure generator & download panel
│   │   │       ├── ResultsPanel.tsx# Analytical results panel
│   │   │       └── ScenariosPanel.tsx# Scenario manager & solver selector
│   │   └── hooks/
│   │       └── useStore.ts         # Zustand state store with organic river contours
│   └── package.json                # Frontend dependencies
├── scripts/
│   ├── run_demo_publication_maps.py# Pipeline generator script for Konta / Machhu demo maps
│   └── generate_exact_river_contours.py
├── tests/
│   ├── test_publication_maps.py    # Unit tests for map renderer & connectivity
│   └── test_core.py                # Unit tests for breach engine & solvers
├── outputs/
│   └── demo/                       # Generated publication PNGs, PDFs, Shapefiles & KMLs
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 2. Backend Setup & Launch
```bash
# Navigate to project root
cd DamGuard

# Install Python dependencies
pip install -r backend/requirements.txt

# Start FastAPI backend server
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Backend API interactive documentation will be available at `http://localhost:8000/docs`.

### 3. Frontend Setup & Launch
```bash
# Navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Start Vite React workstation
npm run dev -- --port 5174
```
Access the interactive GIS workstation at `http://localhost:5174`.

### 4. Deploy to Vercel and Render

The React frontend is configured for Vercel, while the FastAPI/GIS backend runs as a separate Render web service. The Render free service uses ephemeral storage: database contents, uploads, and generated outputs can be lost when the service restarts or redeploys.

1. In Render, create a Blueprint from this GitHub repository and deploy the `damguard-api` service defined in `render.yaml`. Copy the service's public URL after it is live.
2. In Vercel, import this GitHub repository. The root `vercel.json` installs and builds the frontend from `frontend/`.
3. In Vercel's project settings, add `VITE_API_URL` for the Production, Preview, and Development environments. Set it to the Render URL followed by `/api`, for example `https://damguard-api.onrender.com/api`, then redeploy.
4. Check the backend at `https://<your-render-service>.onrender.com/api/health` and open the Vercel deployment.

The Render free service may sleep when idle, so the first API request after inactivity can take longer. Vercel hosts only the frontend; it does not run the simulation backend.

---

## 🔬 Running Demo & Verification Tests

### Run Demo Publication Map Pipeline
Generate publication map outputs (`extent_comparison.png`, `three_panel_depth_velocity_severity.png`, `.shp`, `.kml`) saved to `outputs/demo/`:
```bash
python scripts/run_demo_publication_maps.py
```

### Run Unit Tests
```bash
$env:PYTHONPATH="backend"
python -m pytest tests/ -v
```

---

## 🌐 API Reference — Map Outputs

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/maps/{run_id}?type=extent\|three_panel` | `GET` | Generates and returns publication map figure image (PNG). |
| `/api/maps/{run_id}/download?type=...&format=png\|pdf\|svg\|shp\|kml` | `GET` | Downloads publication maps in high-res PNG, vector PDF, SVG, Shapefile ZIP, or KML format. |
| `/api/maps/batch-extent` | `POST` | Batch generates multi-scenario comparison maps overlaying `S1`, `S2`, `M1`, `M2`, `F1`, `F2`. |

---

## 📜 Scientific References & Citations

1. **NIH Roorkee (2019)**: *Development of 2D Variable Parameter Muskingum-Cunge (2D-VPMM) Method for Flood Routing*, National Institute of Hydrology, Roorkee.
2. **Froehlich, D. C. (2008)**: *Embankment Dam Breach Parameters and Their Uncertainties*, Journal of Hydraulic Engineering, ASCE, 134(12), 1708-1721.
3. **Von Thun, J. L., & Gillette, D. R. (1990)**: *Guidance on Breach Parameters*, U.S. Bureau of Reclamation, Denver, Colorado.
4. **Nobre, A. D., et al. (2011)**: *HAND model: a novel terrain descriptor for grid-based hydrological modeling*, Journal of Hydrology, 400(3-4), 520-529.

---

## 📄 License
This project is licensed under the **MIT License**.
