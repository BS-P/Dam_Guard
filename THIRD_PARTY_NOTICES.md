# THIRD_PARTY_NOTICES.md — BREACHSCOPE Dependency and Data License Registry

> Last updated: 2026-10-04

## Software Dependencies

| Dependency | Version | License | Purpose | Source | Integration |
|---|---|---|---|---|---|
| FastAPI | >=0.104.0 | MIT | Backend API framework | github.com/fastapi/fastapi | pip dependency |
| Uvicorn | >=0.24.0 | BSD-3-Clause | ASGI server | github.com/encode/uvicorn | pip dependency |
| SQLAlchemy | >=2.0.23 | MIT | Database ORM | github.com/sqlalchemy/sqlalchemy | pip dependency |
| Pydantic | >=2.5.0 | MIT | Data validation | github.com/pydantic/pydantic | pip dependency |
| NumPy | >=1.26.0 | BSD-3-Clause | Numerical computing | github.com/numpy/numpy | pip dependency |
| SciPy | >=1.11.0 | BSD-3-Clause | Scientific computing, ODE solvers | github.com/scipy/scipy | pip dependency |
| Numba | >=0.58.0 | BSD-2-Clause | JIT compilation for solver kernels | github.com/numba/numba | pip dependency |
| rasterio | >=1.3.9 | BSD-3-Clause | Raster I/O | github.com/rasterio/rasterio | pip dependency |
| Fiona | >=1.9.5 | BSD-3-Clause | Vector data I/O | github.com/Toblerity/Fiona | pip dependency |
| GeoPandas | >=0.14.0 | BSD-3-Clause | Geospatial dataframes | github.com/geopandas/geopandas | pip dependency |
| Shapely | >=2.0.2 | BSD-3-Clause | Geometric operations | github.com/shapely/shapely | pip dependency |
| pyproj | >=3.6.1 | MIT | Coordinate transformations | github.com/pyproj4/pyproj | pip dependency |
| GDAL | >=3.7.0 | MIT/X-style | Geospatial data abstraction | github.com/OSGeo/gdal | pip/conda dependency |
| WhiteboxTools | >=2.3.0 | MIT | DEM conditioning (depression filling, flow direction) | github.com/jblindsay/whitebox-tools | pip dependency (CLI tool) |
| TiTiler | >=0.18.0 | MIT | Cloud-Optimized GeoTIFF tile server | github.com/developmentseed/titiler | pip dependency |
| rio-tiler | >=6.2.0 | BSD-3-Clause | Raster tile reader | github.com/cogeotiff/rio-tiler | pip dependency |
| HYDROLIB-core | >=0.7.0 | MIT | Delft3D FM model configuration | github.com/Deltares/HYDROLIB-core | pip dependency |
| MeshKernelPy | >=3.0.0 | MIT (wrapper) | Grid generation for Delft3D FM | github.com/Deltares/MeshKernelPy | pip dependency |
| osmnx | >=1.7.0 | MIT | OpenStreetMap network extraction | github.com/gboeing/osmnx | pip dependency |
| Matplotlib | >=3.8.0 | PSF-based | Plot generation | github.com/matplotlib/matplotlib | pip dependency |
| Celery | >=5.3.0 | BSD-3-Clause | Task queue | github.com/celery/celery | pip dependency |
| ReportLab | >=4.0.0 | BSD-3-Clause | PDF report generation | reportlab.com | pip dependency |
| httpx | >=0.25.0 | BSD-3-Clause | HTTP client | github.com/encode/httpx | pip dependency |
| netCDF4 | >=1.6.5 | MIT | NetCDF file I/O | github.com/Unidata/netcdf4-python | pip dependency |
| xarray | >=2023.10.0 | Apache-2.0 | Multi-dimensional arrays | github.com/pydata/xarray | pip dependency |
| rioxarray | >=0.15.0 | Apache-2.0 | Rasterio xarray extension | github.com/corteva/rioxarray | pip dependency |
| React | ^18.2.0 | MIT | Frontend UI framework | github.com/facebook/react | npm dependency |
| MapLibre GL JS | ^4.1.0 | BSD-3-Clause | Map rendering | github.com/maplibre/maplibre-gl-js | npm dependency |
| deck.gl | ^9.0.0 | MIT | Large data geospatial visualization | github.com/visgl/deck.gl | npm dependency |
| Recharts | ^2.10.0 | MIT | React charting | github.com/recharts/recharts | npm dependency |
| Zustand | ^4.4.0 | MIT | React state management | github.com/pmndrs/zustand | npm dependency |
| Tailwind CSS | ^3.4.0 | MIT | Utility-first CSS | github.com/tailwindlabs/tailwindcss | npm dependency |
| Three.js | ^2.0.0 | MIT | 3D rendering (optional) | github.com/mrdoob/three.js | npm dependency |
| Turf.js | ^7.0.0 | MIT | Client-side geospatial analysis | github.com/Turfjs/turf | npm dependency |
| Lucide React | ^0.294.0 | ISC | Icon library | github.com/lucide-icons/lucide | npm dependency |
| Vite | ^5.0.0 | MIT | Frontend build tool | github.com/vitejs/vite | npm devDependency |
| TypeScript | ^5.3.0 | Apache-2.0 | Type system | github.com/microsoft/TypeScript | npm devDependency |

## External Solvers (Executed as Separate Processes)

| Solver | License | Integration | Notes |
|---|---|---|---|
| Delft3D FM (D-Flow FM) | AGPL-3.0 / GPL-3.0 | Executed as **external CLI process** via subprocess. No source code copied. Config files written using HYDROLIB-core (MIT). Output read via netCDF4/xarray. | AGPL/GPL contamination avoided through process isolation. Delft3D must be installed separately by the user. |
| DualSPHysics | LGPL-2.1 | Executed as **external CLI process** via subprocess. No source code copied. Output read from VTK/CSV files. | LGPL contamination avoided through process isolation. DualSPHysics must be installed separately by the user. |
| ANUGA | Apache-2.0 | Available as pip dependency (fallback solver). | Fully permissive. Can be imported directly. |

## Excluded Dependencies

| Package | License | Reason for Exclusion |
|---|---|---|
| RichDEM | **GPL-3.0** (strong copyleft) | In-process Python import would make entire project GPL-3.0. Replaced with WhiteboxTools (MIT). |
| simplekml | LGPL-3.0 | Replaced with custom KML writer using xml.etree.ElementTree to avoid LGPL. |
| Redis Server | RSALv2 / SSPLv1 (non-OSI, source-available) | Using in-process task queue fallback or recommending Valkey (BSD-3-Clause) as drop-in replacement. |

## Data Sources and Licenses

| Data Source | License | Attribution Required | Share-Alike | Required Attribution Text |
|---|---|---|---|---|
| Copernicus GLO-30 DEM | Copernicus Open Access | **Yes** | No | "Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved." |
| ESA WorldCover 10m | CC BY 4.0 | **Yes** | No | "© ESA WorldCover project / Contains modified Copernicus data" |
| WorldPop | CC BY 4.0 | **Yes** | No | "Source: WorldPop (www.worldpop.org) — [specific dataset DOI]" |
| OpenStreetMap | ODbL 1.0 (data), CC BY-SA 2.0 (tiles) | **Yes** | Yes (derivative databases) | "© OpenStreetMap contributors" |
| JRC Global Surface Water | Copernicus Open Access | **Yes** | No | "Source: EC JRC/Google. Cite: Pekel et al., Nature 540 (2016)" |
| Sentinel-1 / Sentinel-2 | EU Copernicus Open Access | **Yes** | No | "Copernicus Sentinel data [Year]" or "Contains modified Copernicus Sentinel data [Year]" |
| Landsat | Public Domain (US Gov) | Recommended | No | "USGS/NASA Landsat" |
| Google Earth Engine | GCP Terms of Service | **Yes** | Platform terms | Free for non-commercial/academic use. Commercial requires paid GCP subscription. |
| CartoDB Basemap Tiles | CC BY 3.0 | **Yes** | No | "© CARTO, © OpenStreetMap contributors" |

## 2D-VPMM Method Attribution

The 2D Variable Parameter Muskingum-Cunge Method (2D-VPMM) is implemented independently from published equations. The method is described in:

1. Perumal, M. & Price, R.K. (2013). "A fully mass conservative variable parameter McCarthy–Muskingum method." *J. Hydrology*, 502, 89–102.
2. Kale, R.V. & Perumal, M. (2014). Derivation of 2D diffusion wave equation from 2D Saint-Venant equations.
3. Shakya, N.M. (2015). PhD Thesis, IIT Roorkee.
4. NIH Roorkee (2019). "Flood Inundation Modelling Using 2D-VPMM" by R.V. Kale, M. Perumal et al. Report No. 50.

> **Recommendation**: The team should confirm institutional permission with the NIH/IIT Roorkee authors before any public release of this implementation.

## Legal Summary

This project contains:
- **Original code** developed specifically for BREACHSCOPE
- **Permissively-licensed dependencies** (MIT, BSD, Apache-2.0) used as standard package dependencies
- **Copyleft solvers** (Delft3D FM: AGPL/GPL, DualSPHysics: LGPL) executed as **isolated external processes** — no source code copied, no in-process linking
- **Open data** used with proper attribution as required by their respective licenses

No unauthorized copying of restrictive source code has been performed.
