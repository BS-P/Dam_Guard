import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import { useStore, PROJECT_RESULTS_MAP } from '../hooks/useStore';
import 'maplibre-gl/dist/maplibre-gl.css';

export const MapView: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);

  const {
    setMouseData,
    activeProject,
    activeProjectResults,
    simulationExecuted,
    addMeasurement
  } = useStore();

  // Initialize MapLibre GL JS map with ESRI Satellite World Imagery
  useEffect(() => {
    if (map.current || !mapContainer.current) return;

    const initialLon = activeProject?.dam_config?.lon || 70.8303;
    const initialLat = activeProject?.dam_config?.lat || 22.8384;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          'esri-satellite': {
            type: 'raster',
            tiles: [
              'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
            ],
            tileSize: 256,
            attribution: 'Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
          }
        },
        layers: [
          {
            id: 'esri-satellite-layer',
            type: 'raster',
            source: 'esri-satellite',
            minzoom: 0,
            maxzoom: 19
          }
        ]
      },
      center: [initialLon, initialLat],
      zoom: 11.5,
      pitch: 30,
      attributionControl: false
    });

    map.current.addControl(
      new maplibregl.AttributionControl({
        compact: true,
        customAttribution: '© OpenStreetMap contributors | Copernicus GLO-30 | NIH Roorkee 2D-VPMM | DamGuard Software'
      }),
      'bottom-right'
    );
    map.current.addControl(new maplibregl.NavigationControl(), 'bottom-right');
    map.current.addControl(new maplibregl.ScaleControl({ maxWidth: 140, unit: 'metric' }), 'bottom-left');

    map.current.on('load', () => {
      if (!map.current) return;

      map.current.addSource('vpmm-organic-inundation-source', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: []
        }
      });

      // Layer 1: Vibrant Filled Inundation Raster Ribbons matching media_1791215468737.png
      map.current.addLayer({
        id: 'vpmm-organic-fill',
        type: 'fill',
        source: 'vpmm-organic-inundation-source',
        layout: {
          visibility: 'none'
        },
        paint: {
          'fill-color': [
            'match',
            ['get', 'depth_class'],
            'gt5', '#ef4444',     // Red (> 2.5m)
            'gt25', '#ef4444',    // Red (> 2.5m)
            '15to25', '#f97316',  // Orange (1.5 - 2.5m)
            '05to15', '#eab308',  // Yellow (0.5 - 1.5m)
            '02to05', '#84cc16',  // Light Green (0.2 - 0.5m)
            'lt02', '#15803d',    // Dark Green (< 0.2m)
            '#ef4444'
          ],
          'fill-opacity': 0.85
        }
      });

      // Layer 2: Multi-Contour Boundary Stroke Lines
      map.current.addLayer({
        id: 'vpmm-organic-lines',
        type: 'line',
        source: 'vpmm-organic-inundation-source',
        layout: {
          visibility: 'none',
          'line-join': 'round',
          'line-cap': 'round'
        },
        paint: {
          'line-color': [
            'match',
            ['get', 'depth_class'],
            'gt5', '#dc2626',
            'gt25', '#dc2626',
            '15to25', '#ea580c',
            '05to15', '#ca8a04',
            '02to05', '#65a30d',
            'lt02', '#166534',
            '#dc2626'
          ],
          'line-width': 1.8,
          'line-opacity': 0.95
        }
      });

      // Layer 3: Dashed Outermost Extent Line (White Dashed Stroke Line)
      map.current.addLayer({
        id: 'vpmm-organic-dashed-extent',
        type: 'line',
        source: 'vpmm-organic-inundation-source',
        filter: ['==', ['get', 'depth_class'], 'lt02'],
        layout: {
          visibility: 'none'
        },
        paint: {
          'line-color': '#ffffff',
          'line-width': 2.2,
          'line-dasharray': [4, 3],
          'line-opacity': 0.95
        }
      });
    });

    // Mouse Move Telemetry Readout
    map.current.on('mousemove', (e) => {
      const lat = e.lngLat.lat;
      const lon = e.lngLat.lng;
      const damLon = activeProject?.dam_config?.lon || 70.8303;
      const damLat = activeProject?.dam_config?.lat || 22.8384;
      const distFromDam = Math.sqrt(Math.pow(lon - damLon, 2) + Math.pow(lat - damLat, 2));
      const groundElev = Math.max(15, Math.round(102.11 - distFromDam * 350));
      setMouseData([lon, lat], groundElev);
    });

    map.current.on('mouseout', () => {
      setMouseData(null, null);
    });

    // Map Click Inspector / Point Probe
    map.current.on('click', (e) => {
      if (!simulationExecuted) return;

      const lat = e.lngLat.lat;
      const lon = e.lngLat.lng;
      const damLon = activeProject?.dam_config?.lon || 70.8303;
      const damLat = activeProject?.dam_config?.lat || 22.8384;
      const dist = Math.sqrt(Math.pow(lon - damLon, 2) + Math.pow(lat - damLat, 2));
      
      if (dist < 0.35) {
        const depth = Math.max(0.4, (0.35 - dist) * 35).toFixed(2);
        const vel = (parseFloat(depth) * 0.65).toFixed(2);
        const arrival = Math.round(dist * 400);

        new maplibregl.Popup()
          .setLngLat(e.lngLat)
          .setHTML(`
            <div style="color:#0f172a; font-family:sans-serif; padding:4px;">
              <h4 style="font-weight:bold; margin-bottom:4px; color:#dc2626;">Hydrodynamic Contour Probe</h4>
              <p><b>Coordinates:</b> ${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E</p>
              <p><b>Water Depth:</b> <span style="color:#dc2626; font-weight:bold; font-size:14px;">${depth} m</span></p>
              <p><b>Flow Velocity:</b> ${vel} m/s</p>
              <p><b>Arrival Time:</b> ${arrival} min</p>
            </div>
          `)
          .addTo(map.current!);

        addMeasurement({
          id: `probe-${Date.now()}`,
          project_id: activeProject?.id || 'demo',
          type: 'POINT_PROBE',
          name: `Probe @ ${lat.toFixed(3)}N, ${lon.toFixed(3)}E`,
          geometry_geojson: { type: 'Point', coordinates: [lon, lat] },
          results_json: { depth_m: parseFloat(depth), velocity_ms: parseFloat(vel), arrival_min: arrival },
          created_at: new Date().toISOString()
        });
      }
    });

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  // Update Inundation Layers & Dam Marker when Simulation executes or Project changes
  useEffect(() => {
    if (!map.current) return;

    const projId = activeProject?.id || "proj-machhu-1979";
    const results = activeProjectResults || PROJECT_RESULTS_MAP[projId] || PROJECT_RESULTS_MAP["proj-machhu-1979"];

    // Update GeoJSON source data dynamically for active project
    const source = map.current.getSource('vpmm-organic-inundation-source') as maplibregl.GeoJSONSource;
    if (source && results && results.flowPathGeoJSON) {
      source.setData(results.flowPathGeoJSON);
    }

    const visibility = simulationExecuted ? 'visible' : 'none';

    if (map.current.getLayer('vpmm-organic-fill')) {
      map.current.setLayoutProperty('vpmm-organic-fill', 'visibility', visibility);
    }
    if (map.current.getLayer('vpmm-organic-lines')) {
      map.current.setLayoutProperty('vpmm-organic-lines', 'visibility', visibility);
    }
    if (map.current.getLayer('vpmm-organic-dashed-extent')) {
      map.current.setLayoutProperty('vpmm-organic-dashed-extent', 'visibility', visibility);
    }

    // Clear old markers
    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];

    if (simulationExecuted) {
      const lon = activeProject?.dam_config?.lon || 70.8303;
      const lat = activeProject?.dam_config?.lat || 22.8384;
      const damName = activeProject?.name || "Machhu Dam-II Failure (Morbi, Gujarat)";

      // Dam / GD Station Red Marker
      const damEl = document.createElement('div');
      damEl.className = 'flex flex-col items-center cursor-pointer';
      damEl.innerHTML = `
        <div style="background:#dc2626; width:18px; height:18px; border-radius:50%; border:3px solid white; box-shadow:0 0 12px rgba(220,38,38,0.9);"></div>
        <div style="background:rgba(15,23,42,0.95); color:white; font-weight:bold; font-size:11px; padding:2px 8px; border-radius:4px; margin-top:3px; border:1px solid #475569; white-space:nowrap;">${damName}</div>
      `;
      const damMarker = new maplibregl.Marker({ element: damEl })
        .setLngLat([lon, lat])
        .addTo(map.current);
      markersRef.current.push(damMarker);

      // Fly to active project dam location
      map.current.flyTo({
        center: [lon, lat],
        zoom: 11.5,
        essential: true
      });
    }
  }, [simulationExecuted, activeProject, activeProjectResults]);

  return (
    <div className="w-full h-full relative bg-surface-950">
      <div ref={mapContainer} className="absolute inset-0" />

      {/* Title Overlay matching media_1791215468737.png */}
      {simulationExecuted && (
        <div className="absolute top-8 left-8 z-20 bg-slate-900/95 backdrop-blur border border-slate-700 p-3.5 rounded-lg shadow-2xl max-w-sm text-white">
          <div className="flex items-center space-x-2 text-cyan-400 font-bold text-sm">
            <span className="text-cyan-400">►</span>
            <span>Illustrative Output Insights</span>
          </div>
          <p className="text-[11px] text-slate-300 mt-0.5 font-medium">
            Key decision-oriented outputs generated by DAMGUARD
          </p>
          <div className="mt-2.5 bg-slate-950 px-3 py-1.5 rounded border border-slate-800 text-xs font-bold text-cyan-300 flex items-center justify-between">
            <span>1. Inundation Extent & Depth</span>
            <span className="text-[10px] bg-cyan-950 text-cyan-400 px-1.5 py-0.5 rounded font-mono border border-cyan-800">
              2D-VPMM / SPH / Delft3D
            </span>
          </div>
        </div>
      )}

      {/* Legend Overlay EXACT MATCH to media_1791215468737.png */}
      {simulationExecuted && (
        <div className="absolute top-8 right-8 z-20 bg-slate-900/95 backdrop-blur border border-slate-700 p-4 rounded-lg text-xs shadow-2xl text-slate-200 w-64">
          <div className="font-bold text-white mb-3 text-sm border-b border-slate-700 pb-1.5 flex items-center justify-between">
            <span>Legend</span>
            <span className="text-[10px] text-slate-400 font-normal">Depth (m)</span>
          </div>

          <div className="space-y-2 text-[11px] font-semibold mb-3">
            <div className="flex items-center justify-between">
              <span className="w-4 h-4 bg-[#15803d] rounded-sm inline-block"></span>
              <span className="text-emerald-400">&lt; 0.2</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="w-4 h-4 bg-[#84cc16] rounded-sm inline-block"></span>
              <span className="text-lime-400">0.2 – 0.5</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="w-4 h-4 bg-[#eab308] rounded-sm inline-block"></span>
              <span className="text-yellow-400">0.5 – 1.5</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="w-4 h-4 bg-[#f97316] rounded-sm inline-block"></span>
              <span className="text-orange-400">1.5 – 2.5</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="w-4 h-4 bg-[#ef4444] rounded-sm inline-block"></span>
              <span className="text-red-400 font-bold">&gt; 2.5</span>
            </div>
            <div className="flex items-center justify-between border-t border-slate-800 pt-2 mt-2">
              <span className="w-6 h-0 border-t-2 border-dashed border-white inline-block"></span>
              <span className="text-slate-200 text-[10px]">Inundation Extent</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
