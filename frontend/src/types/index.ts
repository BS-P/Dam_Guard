export type SolverTier = 'T1_VPMM' | 'T1_DIFFWAVE' | 'T2_DELFT3D' | 'T3_SPH' | 'COUPLED' | 'EXTERNAL' | string;

export type RunStatus = 'PENDING' | 'QUEUED' | 'RUNNING' | 'POSTPROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED' | string;

export type BreachMode = 'OVERTOPPING' | 'PIPING' | 'SUDDEN' | 'BLOCKAGE_RELEASE' | 'USER_DEFINED' | string;

export type BreachMethod = 'FROEHLICH' | 'VON_THUN_GILLETTE' | 'MACDONALD' | 'USER_DEFINED' | string;

export type DatasetType = 'DEM' | 'LAND_COVER' | 'BUILDINGS' | 'ROADS' | 'POPULATION' | 'IMAGERY' | 'HYDROLOGY' | 'OBSERVED_FLOOD' | 'OTHER' | string;

export type MeasurementType = 'DISTANCE' | 'AREA' | 'ELEVATION' | 'CROSS_SECTION' | 'POINT_PROBE' | 'TIME_SERIES' | string;

export type AnnotationType = 'MARKER' | 'LINE' | 'POLYGON' | 'TEXT' | 'DAM' | 'BREACH_POINT' | 'VILLAGE' | 'CRITICAL_FACILITY' | string;

export interface DamConfig {
  name?: string;
  lat?: number;
  lon?: number;
  height_m?: number;
  crest_length_m?: number;
  crest_elevation_m?: number;
  reservoir_volume_m3?: number;
  reservoir_area_m2?: number;
  spillway_capacity_m3s?: number;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  aoi_geojson?: any;
  crs?: string;
  status?: string;
  dam_config?: DamConfig;
  breach_config?: any;
  created_at: string;
  updated_at?: string;
}

export interface Dataset {
  id: string;
  project_id: string;
  name: string;
  type: DatasetType;
  path?: string;
  source?: string;
  license?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface DamProfile {
  id: string;
  project_id: string;
  name: string;
  location?: [number, number];
  height_m?: number;
  crest_length_m?: number;
  volume_m3?: number;
  type?: string;
}

export interface BreachParams {
  average_width_m?: number;
  bottom_width_m?: number;
  depth_m?: number;
  formation_time_s?: number;
  side_slope?: number;
  peak_outflow_m3s?: number;
}

export interface Scenario {
  id: string;
  project_id: string;
  name: string;
  description?: string;
  breach_mode: BreachMode;
  breach_method: BreachMethod;
  breach_params?: BreachParams;
  initial_water_level_m?: number;
  pool_elevation_m?: number;
  inflow_cms?: number;
  manning_n_default?: number;
  created_at: string;
}

export interface SimulationRun {
  id: string;
  scenario_id: string;
  project_id?: string;
  tier: SolverTier;
  solver_tier?: SolverTier;
  status: RunStatus;
  progress?: number;
  start_time?: string;
  end_time?: string;
  error_message?: string;
  result_paths?: Record<string, string>;
  metrics?: Record<string, any>;
}

export interface Measurement {
  id: string;
  project_id: string;
  name: string;
  type: MeasurementType;
  geometry?: any;
  geometry_geojson?: any;
  properties?: Record<string, any>;
  results_json?: Record<string, any>;
  created_at: string;
}

export interface Annotation {
  id: string;
  project_id: string;
  name: string;
  type: AnnotationType;
  geometry?: any;
  geometry_geojson?: any;
  properties?: Record<string, any>;
  created_at: string;
}

export interface SolverStatus {
  name?: string;
  tier: SolverTier;
  installed?: boolean;
  available?: boolean;
  active_runs?: number;
  version?: string;
  details?: Record<string, any>;
}

export interface HealthStatus {
  status: 'healthy' | 'ok' | 'degraded' | 'down';
  version: string;
  services: {
    database: string;
    earth_engine: string;
    compute: string;
  };
}

export interface ResultLayer {
  id: string;
  run_id?: string;
  name: string;
  type: 'raster' | 'vector' | 'depth' | 'velocity' | 'arrival_time' | 'hazard' | string;
  url?: string;
  visible: boolean;
  opacity: number;
  min_value?: number;
  max_value?: number;
  color_map?: string;
  legendUrl?: string;
}
