from typing import AsyncGenerator
import json
import uuid
import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import select
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    # Seed CWC Demo Projects if database is empty
    async with async_session_maker() as session:
        from app.models.project import Project, Dataset
        from app.models.dam import DamProfile
        from app.models.scenario import Scenario
        from app.models.run import SimulationRun
        from app.models.measurement import Measurement
        from app.models.annotation import Annotation

        result = await session.execute(select(Project))
        existing_projects = result.scalars().all()

        if not existing_projects:
            # PROJECT 1: Machhu Dam-II (Morbi, Gujarat) - CWC Historical Dataset
            p1_id = "proj-machhu-1979"
            p1 = Project(
                id=p1_id,
                name="Machhu Dam-II Failure (Morbi, Gujarat)",
                description="CWC / NIH Historical Dataset — August 11, 1979 Overtopping Failure. High-hazard breach hydrograph (16,307 m³/s) and downstream flood routing.",
                aoi_geojson={
                    "type": "Polygon",
                    "coordinates": [[[70.70, 22.70], [70.95, 22.70], [70.95, 22.90], [70.70, 22.90], [70.70, 22.70]]]
                },
                crs="EPSG:4326",
                status="ACTIVE",
                dam_config={
                    "name": "Machhu Dam-II",
                    "lat": 22.8384,
                    "lon": 70.8303,
                    "height_m": 22.56,
                    "crest_length_m": 3810,
                    "reservoir_volume_m3": 101000000,
                    "spillway_capacity_m3s": 5663
                }
            )
            session.add(p1)

            # Datasets for P1
            d1_1 = Dataset(
                id=str(uuid.uuid4()),
                project_id=p1_id,
                name="Copernicus GLO-30 DEM (Morbi Reach)",
                type="DEM",
                source="Copernicus Open Access",
                license="COP-DEM-GLO-30-F",
                file_path="data/demo/machhu_dem.tif",
                crs="EPSG:4326",
                resolution_m=30.0,
                is_demo=True
            )
            d1_2 = Dataset(
                id=str(uuid.uuid4()),
                project_id=p1_id,
                name="OpenStreetMap Land Cover & Buildings",
                type="LANDCOVER",
                source="OpenStreetMap contributors",
                license="ODbL 1.0",
                file_path="data/demo/machhu_osm.geojson",
                crs="EPSG:4326",
                resolution_m=10.0,
                is_demo=True
            )
            session.add_all([d1_1, d1_2])

            # Scenarios for P1
            s1_1 = Scenario(
                id="scen-machhu-overtop",
                project_id=p1_id,
                name="Historical Overtopping Breach (Froehlich 2008)",
                breach_mode="OVERTOPPING",
                breach_method="FROEHLICH",
                breach_params={
                    "average_width_m": 245.0,
                    "bottom_width_m": 195.0,
                    "depth_m": 22.56,
                    "formation_time_s": 7200.0,
                    "side_slope": 0.7,
                    "peak_outflow_m3s": 16307.0
                },
                initial_water_level_m=102.11,
                manning_n_default=0.035
            )
            s1_2 = Scenario(
                id="scen-machhu-sudden",
                project_id=p1_id,
                name="Instantaneous Failure (Worst Case)",
                breach_mode="SUDDEN",
                breach_method="USER_DEFINED",
                breach_params={
                    "average_width_m": 350.0,
                    "depth_m": 22.56,
                    "formation_time_s": 300.0,
                    "peak_outflow_m3s": 24500.0
                },
                initial_water_level_m=102.11,
                manning_n_default=0.035
            )
            session.add_all([s1_1, s1_2])

            # Pre-computed Runs for P1
            r1_1 = SimulationRun(
                id="run-machhu-vpmm",
                scenario_id="scen-machhu-overtop",
                project_id=p1_id,
                solver_tier="T1_VPMM",
                status="COMPLETED",
                grid_dx_m=30.0,
                grid_dy_m=30.0,
                dt_s=6.0,
                runtime_seconds=14.2,
                peak_depth_m=8.45,
                peak_velocity_ms=4.82,
                inundated_area_km2=68.4,
                mass_error_pct=0.24,
                cells_per_second=142000,
                output_dir="outputs/runs/run-machhu-vpmm"
            )
            r1_2 = SimulationRun(
                id="run-machhu-diffwave",
                scenario_id="scen-machhu-overtop",
                project_id=p1_id,
                solver_tier="T1_DIFFWAVE",
                status="COMPLETED",
                grid_dx_m=30.0,
                grid_dy_m=30.0,
                dt_s=3.0,
                runtime_seconds=28.5,
                peak_depth_m=8.62,
                peak_velocity_ms=4.15,
                inundated_area_km2=66.1,
                mass_error_pct=0.28,
                cells_per_second=85000,
                output_dir="outputs/runs/run-machhu-diffwave"
            )
            session.add_all([r1_1, r1_2])

            # Annotations for P1
            a1_1 = Annotation(
                id=str(uuid.uuid4()),
                project_id=p1_id,
                type="DAM",
                name="Machhu Dam-II Crest",
                geometry_geojson={"type": "Point", "coordinates": [70.8303, 22.8384]},
                properties_json={"height_m": 22.56, "status": "Failed 1979"},
                notes="Primary breach location during 1979 flood event"
            )
            a1_2 = Annotation(
                id=str(uuid.uuid4()),
                project_id=p1_id,
                type="VILLAGE",
                name="Morbi Downstream Township",
                geometry_geojson={"type": "Point", "coordinates": [70.8370, 22.8173]},
                properties_json={"population": 45000, "warning_lead_time": "1.5 hours"},
                notes="Township flooded by 4-6m water wave within 90 minutes of breach"
            )
            session.add_all([a1_1, a1_2])

            # PROJECT 2: Rishiganga Valley (Uttarakhand, 2021) - CWC / Avalanche Blockage Dataset
            p2_id = "proj-rishiganga-2021"
            p2 = Project(
                id=p2_id,
                name="Rishiganga Avalanche & Debris Blockage (Uttarakhand)",
                description="CWC / ISRO Dataset — Feb 7, 2021 Rock-Ice Avalanche & Landslide Dam Release in Dhauliganga Valley.",
                aoi_geojson={
                    "type": "Polygon",
                    "coordinates": [[[79.55, 30.30], [79.85, 30.30], [79.85, 30.50], [79.55, 30.50], [79.55, 30.30]]]
                },
                crs="EPSG:4326",
                status="ACTIVE",
                dam_config={
                    "name": "Rishiganga Debris Dam",
                    "lat": 30.4000,
                    "lon": 79.7300,
                    "height_m": 60.0,
                    "reservoir_volume_m3": 27000000
                }
            )
            session.add(p2)

            # Datasets for P2
            d2_1 = Dataset(
                id=str(uuid.uuid4()),
                project_id=p2_id,
                name="Copernicus GLO-30 DEM (Chamoli Valley)",
                type="DEM",
                source="Copernicus Open Access",
                license="COP-DEM-GLO-30-F",
                file_path="data/demo/rishiganga_dem.tif",
                crs="EPSG:4326",
                resolution_m=30.0,
                is_demo=True
            )
            d2_2 = Dataset(
                id=str(uuid.uuid4()),
                project_id=p2_id,
                name="Sentinel-1 SAR Observed Flood Extent (Feb 2021)",
                type="OBSERVED_FLOOD",
                source="ESA Sentinel-1 C-band SAR",
                license="Copernicus Sentinel data 2021",
                file_path="data/demo/rishiganga_sar.tif",
                crs="EPSG:4326",
                resolution_m=10.0,
                is_demo=True
            )
            session.add_all([d2_1, d2_2])

            # Scenarios for P2
            s2_1 = Scenario(
                id="scen-rishi-blockage",
                project_id=p2_id,
                name="Debris Dam Progressive Erosion",
                breach_mode="BLOCKAGE_RELEASE",
                breach_method="USER_DEFINED",
                breach_params={
                    "average_width_m": 120.0,
                    "depth_m": 60.0,
                    "formation_time_s": 5400.0,
                    "peak_outflow_m3s": 15000.0
                },
                initial_water_level_m=2150.0,
                manning_n_default=0.045
            )
            session.add(s2_1)

            # Pre-computed Run for P2
            r2_1 = SimulationRun(
                id="run-rishi-vpmm",
                scenario_id="scen-rishi-blockage",
                project_id=p2_id,
                solver_tier="T1_VPMM",
                status="COMPLETED",
                grid_dx_m=30.0,
                grid_dy_m=30.0,
                dt_s=5.0,
                runtime_seconds=18.4,
                peak_depth_m=12.3,
                peak_velocity_ms=8.5,
                inundated_area_km2=24.2,
                mass_error_pct=0.31,
                cells_per_second=110000,
                output_dir="outputs/runs/run-rishi-vpmm"
            )
            session.add(r2_1)

            # PROJECT 3: Hirakud Dam (Mahanadi River, Odisha) - CWC Major Reservoir
            p3_id = "proj-hirakud-cwc"
            p3 = Project(
                id=p3_id,
                name="Hirakud Dam Reservoir & Mahanadi Basin (Odisha)",
                description="CWC Major Dam Dataset — World's longest earthen dam (55km total). Spillway capacity 42,450 m³/s, Reservoir storage 5,896 MCM.",
                aoi_geojson={
                    "type": "Polygon",
                    "coordinates": [[[83.50, 21.30], [84.10, 21.30], [84.10, 21.70], [83.50, 21.70], [83.50, 21.30]]]
                },
                crs="EPSG:4326",
                status="ACTIVE",
                dam_config={
                    "name": "Hirakud Dam",
                    "lat": 21.5200,
                    "lon": 83.8700,
                    "height_m": 59.0,
                    "crest_length_m": 4801,
                    "reservoir_volume_m3": 5896000000,
                    "spillway_capacity_m3s": 42450
                }
            )
            session.add(p3)

            # PROJECT 4: Mullaperiyar & Idukki Dam Complex (Periyar River, Kerala) - CWC High Risk Complex
            p4_id = "proj-idukki-cwc"
            p4 = Project(
                id=p4_id,
                name="Mullaperiyar & Idukki Dam Cascade (Kerala)",
                description="CWC High-Hazard Cascade Dataset — Multi-dam cascade risk modelling (120yr masonry Mullaperiyar upstream of double-curvature arch Idukki Dam).",
                aoi_geojson={
                    "type": "Polygon",
                    "coordinates": [[[76.80, 9.60], [77.20, 9.60], [77.20, 10.00], [76.80, 10.00], [76.80, 9.60]]]
                },
                crs="EPSG:4326",
                status="ACTIVE",
                dam_config={
                    "name": "Idukki Arch Dam",
                    "lat": 9.8420,
                    "lon": 76.9760,
                    "height_m": 168.9,
                    "crest_length_m": 365,
                    "reservoir_volume_m3": 1996000000
                }
            )
            session.add(p4)

            await session.commit()
            print("DB successfully initialized and seeded with 4 CWC Dam-Break Datasets.")
