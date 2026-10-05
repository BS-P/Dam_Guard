import { create } from 'zustand';
import { apiService } from '../services/api';
import { Project, Dataset, Scenario, SimulationRun, Measurement, Annotation, SolverStatus, HealthStatus, ResultLayer } from '../types';

export interface ProjectResults {
  maxDepth_m: number;
  maxVelocity_ms: number;
  inundatedArea_km2: number;
  massError_pct: number;
  peakDischarge_m3s: number;
  timeToPeak_min: number;
  exposedPopulation: number;
  structuresSubmerged: number;
  submergedRoad_km: number;
  croplandFlooded_km2: number;
  hydrographData: Array<{ time_min: number; discharge_m3s: number; water_level_m: number }>;
  hazardData: Array<{ class: string; name: string; area_km2: number; color: string }>;
  infrastructure: Array<{ type: 'DAM' | 'HOSPITAL' | 'SCHOOL' | 'SETTLEMENT' | 'BRIDGE'; name: string; lat: number; lon: number; desc: string }>;
  flowPathGeoJSON: any;
}

export const PROJECT_RESULTS_MAP: Record<string, ProjectResults> = {
  // 1. Machhu Dam-II (Morbi, Gujarat)
  "proj-machhu-1979": {
    maxDepth_m: 8.45,
    maxVelocity_ms: 4.82,
    inundatedArea_km2: 68.4,
    massError_pct: 0.24,
    peakDischarge_m3s: 16307,
    timeToPeak_min: 120,
    exposedPopulation: 45200,
    structuresSubmerged: 8450,
    submergedRoad_km: 42.8,
    croplandFlooded_km2: 48.2,
    hydrographData: [
      { time_min: 0, discharge_m3s: 0, water_level_m: 102.1 },
      { time_min: 30, discharge_m3s: 2400, water_level_m: 101.5 },
      { time_min: 60, discharge_m3s: 8500, water_level_m: 99.8 },
      { time_min: 90, discharge_m3s: 14200, water_level_m: 96.5 },
      { time_min: 120, discharge_m3s: 16307, water_level_m: 94.1 },
      { time_min: 150, discharge_m3s: 12100, water_level_m: 91.0 },
      { time_min: 180, discharge_m3s: 7800, water_level_m: 88.5 },
      { time_min: 240, discharge_m3s: 3200, water_level_m: 85.0 },
      { time_min: 360, discharge_m3s: 850, water_level_m: 82.0 }
    ],
    hazardData: [
      { class: 'H1', name: 'Caution (<0.25m)', area_km2: 12.5, color: '#06b6d4' },
      { class: 'H2', name: 'Low (0.25-0.75m)', area_km2: 18.2, color: '#3b82f6' },
      { class: 'H3', name: 'Medium (0.75-1.5m)', area_km2: 16.4, color: '#eab308' },
      { class: 'H4', name: 'High (1.5-2.5m)', area_km2: 12.1, color: '#f97316' },
      { class: 'H5', name: 'Extreme (>2.5m)', area_km2: 9.2, color: '#ef4444' }
    ],
    infrastructure: [
      { type: 'DAM', name: 'Machhu Dam-II Crest', lat: 22.8384, lon: 70.8303, desc: 'Height: 22.56m | Failed 1979' },
      { type: 'HOSPITAL', name: 'Morbi Civil Hospital', lat: 22.8180, lon: 70.8350, desc: 'Submersion Risk: High' },
      { type: 'HOSPITAL', name: 'Emergency Care Center', lat: 22.8110, lon: 70.8520, desc: 'Submersion Risk: High' },
      { type: 'SETTLEMENT', name: 'Morbi Township', lat: 22.8173, lon: 70.8370, desc: 'Pop: 45,000 | Submerged wave 4-6m' },
      { type: 'SETTLEMENT', name: 'Lalpar Village', lat: 22.8050, lon: 70.8650, desc: 'Pop: 6,200' },
      { type: 'BRIDGE', name: 'National Highway Bridge', lat: 22.8250, lon: 70.8410, desc: 'Overtopped by surge' },
      { type: 'SCHOOL', name: 'Morbi High School Shelter', lat: 22.8020, lon: 70.8460, desc: 'Evacuation Assembly Point' }
    ],
    flowPathGeoJSON: {
      "type": "FeatureCollection",
      "features": []
},
  },

  // 2. Rishiganga Valley (Chamoli, Uttarakhand)
  "proj-rishiganga-2021": {
    maxDepth_m: 12.30,
    maxVelocity_ms: 8.50,
    inundatedArea_km2: 24.2,
    massError_pct: 0.31,
    peakDischarge_m3s: 15200,
    timeToPeak_min: 35,
    exposedPopulation: 8400,
    structuresSubmerged: 1240,
    submergedRoad_km: 18.5,
    croplandFlooded_km2: 8.4,
    hydrographData: [
      { time_min: 0, discharge_m3s: 0, water_level_m: 2150.0 },
      { time_min: 10, discharge_m3s: 4800, water_level_m: 2145.0 },
      { time_min: 20, discharge_m3s: 11200, water_level_m: 2132.0 },
      { time_min: 35, discharge_m3s: 15200, water_level_m: 2120.0 },
      { time_min: 50, discharge_m3s: 9800, water_level_m: 2108.0 },
      { time_min: 75, discharge_m3s: 4200, water_level_m: 2095.0 },
      { time_min: 120, discharge_m3s: 1100, water_level_m: 2085.0 },
      { time_min: 180, discharge_m3s: 350, water_level_m: 2080.0 }
    ],
    hazardData: [
      { class: 'H1', name: 'Caution (<0.25m)', area_km2: 2.1, color: '#06b6d4' },
      { class: 'H2', name: 'Low (0.25-0.75m)', area_km2: 4.5, color: '#3b82f6' },
      { class: 'H3', name: 'Medium (0.75-1.5m)', area_km2: 5.8, color: '#eab308' },
      { class: 'H4', name: 'High (1.5-2.5m)', area_km2: 6.2, color: '#f97316' },
      { class: 'H5', name: 'Extreme (>2.5m)', area_km2: 5.6, color: '#ef4444' }
    ],
    infrastructure: [
      { type: 'DAM', name: 'Rishi Ganga Debris Blockage', lat: 30.4000, lon: 79.7300, desc: 'Rock-Ice Avalanche Debris Dam (60m high)' },
      { type: 'BRIDGE', name: 'Rishi Ganga HEP Intake Dam', lat: 30.4100, lon: 79.7200, desc: 'Rishi Ganga Powerhouse — Destroyed Feb 2021' },
      { type: 'SETTLEMENT', name: 'Raini Village', lat: 30.4150, lon: 79.7150, desc: 'Historic Chipko Movement Village | Pop: 1,200' },
      { type: 'DAM', name: 'NTPC Tapovan Hydroelectric Dam', lat: 30.4800, lon: 79.6500, desc: 'Tapovan-Vishnugad Project Barrage' },
      { type: 'HOSPITAL', name: 'Tapovan Medical Camp', lat: 30.4850, lon: 79.6450, desc: 'Tunnel Rescue & Field Hospital' },
      { type: 'SETTLEMENT', name: 'Joshimath Sub-Division', lat: 30.5570, lon: 79.5660, desc: 'Downstream Base Camp & Relief Hub' },
      { type: 'SCHOOL', name: 'Joshimath Relief Center', lat: 30.5520, lon: 79.5620, desc: 'Disaster Evacuation Camp' }
    ],
    flowPathGeoJSON: {
      "type": "FeatureCollection",
      "features": [
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "lt02",
                        "label": "< 0.2m (M1 Piping)",
                        "scenario": "M1"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          79.74168750283734,
                                          30.48894532207602
                                    ],
                                    [
                                          79.71459654883837,
                                          30.496655162794575
                                    ],
                                    [
                                          79.69180651970728,
                                          30.504516299268232
                                    ],
                                    [
                                          79.6647875754514,
                                          30.51750080231079
                                    ],
                                    [
                                          79.64435255068987,
                                          30.523219514397166
                                    ],
                                    [
                                          79.60913680179924,
                                          30.535748178606696
                                    ],
                                    [
                                          79.58428997487218,
                                          30.546224937180465
                                    ],
                                    [
                                          79.58548408912164,
                                          30.549210222804117
                                    ],
                                    [
                                          79.61051951867788,
                                          30.5393552661162
                                    ],
                                    [
                                          79.6456175471395,
                                          30.526698254633633
                                    ],
                                    [
                                          79.66556355493748,
                                          30.51932435410304
                                    ],
                                    [
                                          79.69246734144345,
                                          30.50616835360865
                                    ],
                                    [
                                          79.71529932842707,
                                          30.498997761423535
                                    ],
                                    [
                                          79.74202840883298,
                                          30.490095879811268
                                    ],
                                    [
                                          79.74168750283734,
                                          30.48894532207602
                                    ]
                              ]
                        ]
                  }
            },
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "02to05",
                        "label": "0.2 - 0.5m (S1 Overtopping)",
                        "scenario": "S1"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          79.74155966308898,
                                          30.488513862925302
                                    ],
                                    [
                                          79.71433300649262,
                                          30.495776688308716
                                    ],
                                    [
                                          79.69155871155623,
                                          30.503896778890578
                                    ],
                                    [
                                          79.66449658314413,
                                          30.516816970388692
                                    ],
                                    [
                                          79.64387817702126,
                                          30.52191498680849
                                    ],
                                    [
                                          79.60861828296974,
                                          30.53439552079063
                                    ],
                                    [
                                          79.58384218202863,
                                          30.545105455071596
                                    ],
                                    [
                                          79.5859318819652,
                                          30.550329704912986
                                    ],
                                    [
                                          79.61103803750737,
                                          30.540707923932263
                                    ],
                                    [
                                          79.6460919208081,
                                          30.52800278222231
                                    ],
                                    [
                                          79.66585454724475,
                                          30.520008186025137
                                    ],
                                    [
                                          79.69271514959452,
                                          30.506787873986305
                                    ],
                                    [
                                          79.71556287077283,
                                          30.499876235909394
                                    ],
                                    [
                                          79.74215624858134,
                                          30.49052733896199
                                    ],
                                    [
                                          79.74155966308898,
                                          30.488513862925302
                                    ]
                              ]
                        ]
                  }
            },
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "05to15",
                        "label": "0.5 - 1.5m (F1 Observed)",
                        "scenario": "F1"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          79.74143182334062,
                                          30.48808240377458
                                    ],
                                    [
                                          79.71406946414686,
                                          30.494898213822857
                                    ],
                                    [
                                          79.69131090340517,
                                          30.50327725851292
                                    ],
                                    [
                                          79.66420559083686,
                                          30.516133138466596
                                    ],
                                    [
                                          79.64340380335265,
                                          30.520610459219814
                                    ],
                                    [
                                          79.60809976414025,
                                          30.533042862974565
                                    ],
                                    [
                                          79.58339438918509,
                                          30.543985972962727
                                    ],
                                    [
                                          79.58637967480874,
                                          30.551449187021856
                                    ],
                                    [
                                          79.61155655633685,
                                          30.542060581748327
                                    ],
                                    [
                                          79.64656629447671,
                                          30.529307309810985
                                    ],
                                    [
                                          79.66614553955202,
                                          30.520692017947233
                                    ],
                                    [
                                          79.69296295774558,
                                          30.507407394363963
                                    ],
                                    [
                                          79.71582641311858,
                                          30.500754710395256
                                    ],
                                    [
                                          79.7422840883297,
                                          30.490958798112707
                                    ],
                                    [
                                          79.74143182334062,
                                          30.48808240377458
                                    ]
                              ]
                        ]
                  }
            },
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "15to25",
                        "label": "1.5 - 2.5m (F2 SPH Surge)",
                        "scenario": "F2"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          79.74130398359226,
                                          30.487650944623862
                                    ],
                                    [
                                          79.7138059218011,
                                          30.494019739336995
                                    ],
                                    [
                                          79.6910630952541,
                                          30.502657738135262
                                    ],
                                    [
                                          79.66391459852959,
                                          30.5154493065445
                                    ],
                                    [
                                          79.64292942968405,
                                          30.519305931631138
                                    ],
                                    [
                                          79.60758124531075,
                                          30.5316902051585
                                    ],
                                    [
                                          79.58294659634154,
                                          30.542866490853857
                                    ],
                                    [
                                          79.58682746765228,
                                          30.552568669130725
                                    ],
                                    [
                                          79.61207507516635,
                                          30.54341323956439
                                    ],
                                    [
                                          79.64704066814532,
                                          30.53061183739966
                                    ],
                                    [
                                          79.66643653185929,
                                          30.52137584986933
                                    ],
                                    [
                                          79.69321076589664,
                                          30.50802691474162
                                    ],
                                    [
                                          79.71608995546434,
                                          30.501633184881115
                                    ],
                                    [
                                          79.74241192807806,
                                          30.491390257263426
                                    ],
                                    [
                                          79.74130398359226,
                                          30.487650944623862
                                    ]
                              ]
                        ]
                  }
            },
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "gt25",
                        "label": "2.5 - 4.0m (M2 Extreme)",
                        "scenario": "M2"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          79.7411761438439,
                                          30.487219485473144
                                    ],
                                    [
                                          79.71354237945535,
                                          30.493141264851136
                                    ],
                                    [
                                          79.69081528710304,
                                          30.502038217757608
                                    ],
                                    [
                                          79.6636236062223,
                                          30.514765474622404
                                    ],
                                    [
                                          79.64245505601544,
                                          30.51800140404246
                                    ],
                                    [
                                          79.60706272648127,
                                          30.530337547342437
                                    ],
                                    [
                                          79.58249880349798,
                                          30.541747008744988
                                    ],
                                    [
                                          79.58727526049583,
                                          30.553688151239594
                                    ],
                                    [
                                          79.61259359399584,
                                          30.544765897380454
                                    ],
                                    [
                                          79.64751504181393,
                                          30.531916364988337
                                    ],
                                    [
                                          79.66672752416657,
                                          30.522059681791426
                                    ],
                                    [
                                          79.69345857404771,
                                          30.508646435119275
                                    ],
                                    [
                                          79.71635349781009,
                                          30.502511659366974
                                    ],
                                    [
                                          79.74253976782641,
                                          30.491821716414144
                                    ],
                                    [
                                          79.7411761438439,
                                          30.487219485473144
                                    ]
                              ]
                        ]
                  }
            },
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "gt5",
                        "label": "> 4.0m (S2 Catastrophic)",
                        "scenario": "S2"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          79.74104830409554,
                                          30.486788026322426
                                    ],
                                    [
                                          79.71327883710958,
                                          30.492262790365277
                                    ],
                                    [
                                          79.69056747895198,
                                          30.50141869737995
                                    ],
                                    [
                                          79.66333261391503,
                                          30.514081642700308
                                    ],
                                    [
                                          79.64198068234683,
                                          30.516696876453786
                                    ],
                                    [
                                          79.60654420765178,
                                          30.528984889526374
                                    ],
                                    [
                                          79.58205101065444,
                                          30.54062752663612
                                    ],
                                    [
                                          79.58772305333937,
                                          30.554807633348464
                                    ],
                                    [
                                          79.61311211282533,
                                          30.546118555196518
                                    ],
                                    [
                                          79.64798941548254,
                                          30.533220892577013
                                    ],
                                    [
                                          79.66701851647385,
                                          30.52274351371352
                                    ],
                                    [
                                          79.69370638219877,
                                          30.509265955496932
                                    ],
                                    [
                                          79.71661704015585,
                                          30.503390133852836
                                    ],
                                    [
                                          79.74266760757477,
                                          30.492253175564862
                                    ],
                                    [
                                          79.74104830409554,
                                          30.486788026322426
                                    ]
                              ]
                        ]
                  }
            }
      ]
},
  },

  // 3. Hirakud Dam (Mahanadi River, Odisha)
  "proj-hirakud-cwc": {
    maxDepth_m: 9.80,
    maxVelocity_ms: 5.20,
    inundatedArea_km2: 312.5,
    massError_pct: 0.18,
    peakDischarge_m3s: 42450,
    timeToPeak_min: 240,
    exposedPopulation: 125000,
    structuresSubmerged: 24500,
    submergedRoad_km: 112.4,
    croplandFlooded_km2: 210.8,
    hydrographData: [
      { time_min: 0, discharge_m3s: 0, water_level_m: 192.0 },
      { time_min: 60, discharge_m3s: 8500, water_level_m: 190.5 },
      { time_min: 120, discharge_m3s: 21000, water_level_m: 188.0 },
      { time_min: 180, discharge_m3s: 34500, water_level_m: 185.2 },
      { time_min: 240, discharge_m3s: 42450, water_level_m: 182.0 },
      { time_min: 300, discharge_m3s: 31000, water_level_m: 179.5 },
      { time_min: 360, discharge_m3s: 19500, water_level_m: 177.0 },
      { time_min: 480, discharge_m3s: 6800, water_level_m: 174.0 }
    ],
    hazardData: [
      { class: 'H1', name: 'Caution (<0.25m)', area_km2: 45.2, color: '#06b6d4' },
      { class: 'H2', name: 'Low (0.25-0.75m)', area_km2: 82.5, color: '#3b82f6' },
      { class: 'H3', name: 'Medium (0.75-1.5m)', area_km2: 95.4, color: '#eab308' },
      { class: 'H4', name: 'High (1.5-2.5m)', area_km2: 54.2, color: '#f97316' },
      { class: 'H5', name: 'Extreme (>2.5m)', area_km2: 35.2, color: '#ef4444' }
    ],
    infrastructure: [
      { type: 'DAM', name: 'Hirakud Main Dam Spillway', lat: 21.5200, lon: 83.8700, desc: 'Earthen Dam (59m high, 4.8km spillway)' },
      { type: 'SETTLEMENT', name: 'Sambalpur Township', lat: 21.4670, lon: 83.9800, desc: 'District Headquarter | Pop: 125,000' },
      { type: 'HOSPITAL', name: 'VIMSAR Burla Medical College', lat: 21.5020, lon: 83.8950, desc: 'Primary Regional Trauma Center' },
      { type: 'BRIDGE', name: 'Mahanadi River Railway Bridge', lat: 21.4600, lon: 83.9700, desc: 'Major Railway Arterial Bridge' },
      { type: 'SCHOOL', name: 'Sambalpur High School Shelter', lat: 21.4620, lon: 83.9750, desc: 'Relief & Rehabilitation Center' }
    ],
    flowPathGeoJSON: {
      "type": "FeatureCollection",
      "features": [
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "lt02",
                        "label": "< 0.2m (M1 Piping)",
                        "scenario": "M1"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          83.87077781745931,
                                          21.530777817459306
                                    ],
                                    [
                                          83.89599281416915,
                                          21.505992814169144
                                    ],
                                    [
                                          83.92029653655928,
                                          21.48042833058563
                                    ],
                                    [
                                          83.96031111192191,
                                          21.460444445602747
                                    ],
                                    [
                                          84.02110118480282,
                                          21.411541658723944
                                    ],
                                    [
                                          84.10107849995096,
                                          21.36215699990193
                                    ],
                                    [
                                          84.20071002512782,
                                          21.321775062819533
                                    ],
                                    [
                                          84.19951591087836,
                                          21.31878977719588
                                    ],
                                    [
                                          84.09935090125522,
                                          21.35870180251044
                                    ],
                                    [
                                          84.01894967294827,
                                          21.408529542127578
                                    ],
                                    [
                                          83.95917463089431,
                                          21.458820901277598
                                    ],
                                    [
                                          83.91928373157951,
                                          21.478965390059287
                                    ],
                                    [
                                          83.89426341145625,
                                          21.504263411456257
                                    ],
                                    [
                                          83.86992928932189,
                                          21.52992928932188
                                    ],
                                    [
                                          83.87077781745931,
                                          21.530777817459306
                                    ]
                              ]
                        ]
                  }
            },
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "02to05",
                        "label": "0.2 - 0.5m (S1 Overtopping)",
                        "scenario": "S1"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          83.87109601551084,
                                          21.53109601551084
                                    ],
                                    [
                                          83.89664134018648,
                                          21.506641340186476
                                    ],
                                    [
                                          83.9206763384267,
                                          21.48097693328301
                                    ],
                                    [
                                          83.96073729230727,
                                          21.46105327472468
                                    ],
                                    [
                                          84.02190800174827,
                                          21.412671202447584
                                    ],
                                    [
                                          84.10172634946187,
                                          21.36345269892374
                                    ],
                                    [
                                          84.20115781797136,
                                          21.322894544928403
                                    ],
                                    [
                                          84.1990681180348,
                                          21.317670295087012
                                    ],
                                    [
                                          84.09870305174431,
                                          21.35740610348863
                                    ],
                                    [
                                          84.01814285600281,
                                          21.40739999840394
                                    ],
                                    [
                                          83.95874845050896,
                                          21.458212072155668
                                    ],
                                    [
                                          83.91890392971209,
                                          21.47841678736191
                                    ],
                                    [
                                          83.89361488543892,
                                          21.503614885438925
                                    ],
                                    [
                                          83.86961109127036,
                                          21.529611091270347
                                    ],
                                    [
                                          83.87109601551084,
                                          21.53109601551084
                                    ]
                              ]
                        ]
                  }
            },
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "05to15",
                        "label": "0.5 - 1.5m (F1 Observed)",
                        "scenario": "F1"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          83.87141421356237,
                                          21.531414213562375
                                    ],
                                    [
                                          83.8972898662038,
                                          21.50728986620381
                                    ],
                                    [
                                          83.92105614029411,
                                          21.48152553598039
                                    ],
                                    [
                                          83.96116347269262,
                                          21.46166210384661
                                    ],
                                    [
                                          84.02271481869373,
                                          21.413800746171223
                                    ],
                                    [
                                          84.10237419897277,
                                          21.364748397945547
                                    ],
                                    [
                                          84.20160561081491,
                                          21.324014027037272
                                    ],
                                    [
                                          84.19862032519126,
                                          21.316550812978143
                                    ],
                                    [
                                          84.09805520223341,
                                          21.356110404466822
                                    ],
                                    [
                                          84.01733603905735,
                                          21.4062704546803
                                    ],
                                    [
                                          83.9583222701236,
                                          21.457603243033734
                                    ],
                                    [
                                          83.91852412784468,
                                          21.477868184664526
                                    ],
                                    [
                                          83.89296635942159,
                                          21.502966359421595
                                    ],
                                    [
                                          83.86929289321881,
                                          21.529292893218816
                                    ],
                                    [
                                          83.87141421356237,
                                          21.531414213562375
                                    ]
                              ]
                        ]
                  }
            },
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "15to25",
                        "label": "1.5 - 2.5m (F2 SPH Surge)",
                        "scenario": "F2"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          83.8717324116139,
                                          21.53173241161391
                                    ],
                                    [
                                          83.89793839222114,
                                          21.507938392221142
                                    ],
                                    [
                                          83.92143594216154,
                                          21.482074138677767
                                    ],
                                    [
                                          83.96158965307798,
                                          21.462270932968543
                                    ],
                                    [
                                          84.02352163563918,
                                          21.41493028989486
                                    ],
                                    [
                                          84.10302204848367,
                                          21.366044096967357
                                    ],
                                    [
                                          84.20205340365845,
                                          21.32513350914614
                                    ],
                                    [
                                          84.19817253234771,
                                          21.315431330869274
                                    ],
                                    [
                                          84.0974073527225,
                                          21.354814705445012
                                    ],
                                    [
                                          84.0165292221119,
                                          21.40514091095666
                                    ],
                                    [
                                          83.95789608973826,
                                          21.456994413911804
                                    ],
                                    [
                                          83.91814432597725,
                                          21.477319581967148
                                    ],
                                    [
                                          83.89231783340426,
                                          21.502317833404263
                                    ],
                                    [
                                          83.86897469516728,
                                          21.528974695167282
                                    ],
                                    [
                                          83.8717324116139,
                                          21.53173241161391
                                    ]
                              ]
                        ]
                  }
            },
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "gt25",
                        "label": "2.5 - 4.0m (M2 Extreme)",
                        "scenario": "M2"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          83.87205060966545,
                                          21.532050609665443
                                    ],
                                    [
                                          83.89858691823848,
                                          21.508586918238475
                                    ],
                                    [
                                          83.92181574402895,
                                          21.482622741375145
                                    ],
                                    [
                                          83.96201583346333,
                                          21.462879762090473
                                    ],
                                    [
                                          84.02432845258464,
                                          21.416059833618498
                                    ],
                                    [
                                          84.10366989799458,
                                          21.367339795989167
                                    ],
                                    [
                                          84.20250119650201,
                                          21.32625299125501
                                    ],
                                    [
                                          84.19772473950417,
                                          21.314311848760404
                                    ],
                                    [
                                          84.0967595032116,
                                          21.353519006423202
                                    ],
                                    [
                                          84.01572240516644,
                                          21.40401136723302
                                    ],
                                    [
                                          83.95746990935291,
                                          21.456385584789874
                                    ],
                                    [
                                          83.91776452410984,
                                          21.47677097926977
                                    ],
                                    [
                                          83.89166930738692,
                                          21.50166930738693
                                    ],
                                    [
                                          83.86865649711575,
                                          21.528656497115747
                                    ],
                                    [
                                          83.87205060966545,
                                          21.532050609665443
                                    ]
                              ]
                        ]
                  }
            },
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "gt5",
                        "label": "> 4.0m (S2 Catastrophic)",
                        "scenario": "S2"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          83.87236880771698,
                                          21.532368807716974
                                    ],
                                    [
                                          83.89923544425581,
                                          21.509235444255808
                                    ],
                                    [
                                          83.92219554589637,
                                          21.483171344072524
                                    ],
                                    [
                                          83.96244201384867,
                                          21.463488591212403
                                    ],
                                    [
                                          84.0251352695301,
                                          21.417189377342137
                                    ],
                                    [
                                          84.10431774750548,
                                          21.368635495010974
                                    ],
                                    [
                                          84.20294898934556,
                                          21.32737247336388
                                    ],
                                    [
                                          84.19727694666062,
                                          21.313192366651535
                                    ],
                                    [
                                          84.09611165370069,
                                          21.352223307401395
                                    ],
                                    [
                                          84.01491558822099,
                                          21.402881823509386
                                    ],
                                    [
                                          83.95704372896755,
                                          21.45577675566794
                                    ],
                                    [
                                          83.91738472224243,
                                          21.47622237657239
                                    ],
                                    [
                                          83.89102078136959,
                                          21.501020781369597
                                    ],
                                    [
                                          83.86833829906422,
                                          21.528338299064213
                                    ],
                                    [
                                          83.87236880771698,
                                          21.532368807716974
                                    ]
                              ]
                        ]
                  }
            }
      ]
},
  },

  // 4. Konta Sabari Basin (22 September 2005)
  "proj-konta-2005": {
    maxDepth_m: 11.40,
    maxVelocity_ms: 5.60,
    inundatedArea_km2: 184.5,
    massError_pct: 0.22,
    peakDischarge_m3s: 28500,
    timeToPeak_min: 180,
    exposedPopulation: 34200,
    structuresSubmerged: 6800,
    submergedRoad_km: 68.2,
    croplandFlooded_km2: 112.4,
    hydrographData: [
      { time_min: 0, discharge_m3s: 0, water_level_m: 42.0 },
      { time_min: 30, discharge_m3s: 4200, water_level_m: 40.5 },
      { time_min: 60, discharge_m3s: 11500, water_level_m: 38.0 },
      { time_min: 120, discharge_m3s: 22400, water_level_m: 35.2 },
      { time_min: 180, discharge_m3s: 28500, water_level_m: 32.0 },
      { time_min: 240, discharge_m3s: 21000, water_level_m: 30.5 },
      { time_min: 300, discharge_m3s: 12500, water_level_m: 28.0 },
      { time_min: 420, discharge_m3s: 4200, water_level_m: 25.0 }
    ],
    hazardData: [
      { class: 'M1', name: 'Caution (<0.25m)', area_km2: 28.4, color: '#06b6d4' },
      { class: 'S1', name: 'Low (0.25-0.75m)', area_km2: 48.2, color: '#3b82f6' },
      { class: 'F1', name: 'Medium (0.75-1.5m)', area_km2: 52.1, color: '#eab308' },
      { class: 'F2', name: 'High (1.5-2.5m)', area_km2: 34.6, color: '#f97316' },
      { class: 'M2/S2', name: 'Extreme (>2.5m)', area_km2: 21.2, color: '#ef4444' }
    ],
    infrastructure: [
      { type: 'DAM', name: 'Konta GD Station (CWC)', lat: 17.8033, lon: 81.3910, desc: 'Sabari River Gauge & Discharge Station (Sep 2005 Event)' },
      { type: 'SETTLEMENT', name: 'Konta Township', lat: 17.8010, lon: 81.3850, desc: 'District Sub-Division | Pop: 14,500' },
      { type: 'HOSPITAL', name: 'Konta Health Center', lat: 17.7980, lon: 81.3820, desc: 'Primary Field Medical Unit' },
      { type: 'BRIDGE', name: 'Sabari River Bridge', lat: 17.8020, lon: 81.3880, desc: 'NH-30 River Crossing' },
      { type: 'SETTLEMENT', name: 'Mothugudem Reach', lat: 17.7100, lon: 81.3400, desc: 'Downstream Inundation Corridor' }
    ],
    flowPathGeoJSON: {
      "type": "FeatureCollection",
      "features": [
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "lt02",
                        "label": "< 0.2m (M1 Piping)",
                        "scenario": "M1"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          81.4105767821945,
                                          17.81406334515423
                                    ],
                                    [
                                          81.39195156627358,
                                          17.802348433726422
                                    ],
                                    [
                                          81.37529723892298,
                                          17.779725949929173
                                    ],
                                    [
                                          81.35216849211835,
                                          17.76067338450904
                                    ],
                                    [
                                          81.31281443012787,
                                          17.746052124217098
                                    ],
                                    [
                                          81.2896835693905,
                                          17.72371170342291
                                    ],
                                    [
                                          81.26942424006938,
                                          17.689359091968775
                                    ],
                                    [
                                          81.25349960456957,
                                          17.644506227763674
                                    ],
                                    [
                                          81.2428153903925,
                                          17.60746028934277
                                    ],
                                    [
                                          81.23824075049814,
                                          17.60882031741947
                                    ],
                                    [
                                          81.25000715675179,
                                          17.64565618009392
                                    ],
                                    [
                                          81.26713052857704,
                                          17.690391262140334
                                    ],
                                    [
                                          81.28707896115031,
                                          17.725704794945845
                                    ],
                                    [
                                          81.3112284672322,
                                          17.74887161380941
                                    ],
                                    [
                                          81.35142037710732,
                                          17.76212357668428
                                    ],
                                    [
                                          81.37416062691054,
                                          17.780773890082482
                                    ],
                                    [
                                          81.39030465935184,
                                          17.80399534064817
                                    ],
                                    [
                                          81.40994756525504,
                                          17.815085150440527
                                    ],
                                    [
                                          81.4105767821945,
                                          17.81406334515423
                                    ]
                              ]
                        ]
                  }
            },
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "02to05",
                        "label": "0.2 - 0.5m (S1 Overtopping)",
                        "scenario": "S1"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          81.4108127385468,
                                          17.81368016817187
                                    ],
                                    [
                                          81.39256915636923,
                                          17.801730843630768
                                    ],
                                    [
                                          81.37572346842764,
                                          17.77933297237168
                                    ],
                                    [
                                          81.35244903524749,
                                          17.760129562443325
                                    ],
                                    [
                                          81.31340916621376,
                                          17.744994815619982
                                    ],
                                    [
                                          81.29066029748058,
                                          17.72296429410181
                                    ],
                                    [
                                          81.27028438187902,
                                          17.688972028154442
                                    ],
                                    [
                                          81.25480927250123,
                                          17.644074995639834
                                    ],
                                    [
                                          81.24453088035288,
                                          17.60695027881401
                                    ],
                                    [
                                          81.23652526053776,
                                          17.609330327948236
                                    ],
                                    [
                                          81.24869748882013,
                                          17.64608741221776
                                    ],
                                    [
                                          81.2662703867674,
                                          17.69077832595467
                                    ],
                                    [
                                          81.28610223306023,
                                          17.72645220426695
                                    ],
                                    [
                                          81.31063373114632,
                                          17.749928922406525
                                    ],
                                    [
                                          81.35113983397818,
                                          17.762667398749997
                                    ],
                                    [
                                          81.37373439740587,
                                          17.781166867639975
                                    ],
                                    [
                                          81.38968706925618,
                                          17.804612930743826
                                    ],
                                    [
                                          81.40971160890274,
                                          17.815468327422888
                                    ],
                                    [
                                          81.4108127385468,
                                          17.81368016817187
                                    ]
                              ]
                        ]
                  }
            },
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "05to15",
                        "label": "0.5 - 1.5m (F1 Observed)",
                        "scenario": "F1"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          81.4110486948991,
                                          17.81329699118951
                                    ],
                                    [
                                          81.39318674646489,
                                          17.80111325353511
                                    ],
                                    [
                                          81.3761496979323,
                                          17.77893999481419
                                    ],
                                    [
                                          81.35272957837664,
                                          17.75958574037761
                                    ],
                                    [
                                          81.31400390229963,
                                          17.743937507022867
                                    ],
                                    [
                                          81.29163702557067,
                                          17.72221688478071
                                    ],
                                    [
                                          81.27114452368866,
                                          17.688584964340105
                                    ],
                                    [
                                          81.25611894043291,
                                          17.643643763515993
                                    ],
                                    [
                                          81.24624637031326,
                                          17.606440268285247
                                    ],
                                    [
                                          81.23480977057737,
                                          17.609840338476996
                                    ],
                                    [
                                          81.24738782088846,
                                          17.6465186443416
                                    ],
                                    [
                                          81.26541024495776,
                                          17.691165389769004
                                    ],
                                    [
                                          81.28512550497017,
                                          17.72719961358805
                                    ],
                                    [
                                          81.31003899506045,
                                          17.75098623100364
                                    ],
                                    [
                                          81.35085929084904,
                                          17.76321122081571
                                    ],
                                    [
                                          81.37330816790121,
                                          17.781559845197464
                                    ],
                                    [
                                          81.38906947916053,
                                          17.805230520839483
                                    ],
                                    [
                                          81.40947565255046,
                                          17.81585150440525
                                    ],
                                    [
                                          81.4110486948991,
                                          17.81329699118951
                                    ]
                              ]
                        ]
                  }
            },
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "15to25",
                        "label": "1.5 - 2.5m (F2 SPH Surge)",
                        "scenario": "F2"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          81.41128465125139,
                                          17.812913814207146
                                    ],
                                    [
                                          81.39380433656055,
                                          17.800495663439456
                                    ],
                                    [
                                          81.37657592743696,
                                          17.7785470172567
                                    ],
                                    [
                                          81.35301012150578,
                                          17.759041918311897
                                    ],
                                    [
                                          81.31459863838552,
                                          17.742880198425752
                                    ],
                                    [
                                          81.29261375366073,
                                          17.72146947545961
                                    ],
                                    [
                                          81.27200466549829,
                                          17.688197900525772
                                    ],
                                    [
                                          81.25742860836458,
                                          17.64321253139215
                                    ],
                                    [
                                          81.24796186027365,
                                          17.605930257756487
                                    ],
                                    [
                                          81.233094280617,
                                          17.61035034900576
                                    ],
                                    [
                                          81.2460781529568,
                                          17.64694987646544
                                    ],
                                    [
                                          81.26455010314814,
                                          17.69155245358334
                                    ],
                                    [
                                          81.28414877688009,
                                          17.72794702290915
                                    ],
                                    [
                                          81.30944425897457,
                                          17.75204353960076
                                    ],
                                    [
                                          81.35057874771991,
                                          17.763755042881424
                                    ],
                                    [
                                          81.37288193839655,
                                          17.781952822754956
                                    ],
                                    [
                                          81.38845188906487,
                                          17.805848110935138
                                    ],
                                    [
                                          81.40923969619816,
                                          17.81623468138761
                                    ],
                                    [
                                          81.41128465125139,
                                          17.812913814207146
                                    ]
                              ]
                        ]
                  }
            },
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "gt25",
                        "label": "2.5 - 4.0m (M2 Extreme)",
                        "scenario": "M2"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          81.41152060760368,
                                          17.812530637224786
                                    ],
                                    [
                                          81.39442192665621,
                                          17.799878073343802
                                    ],
                                    [
                                          81.37700215694163,
                                          17.778154039699206
                                    ],
                                    [
                                          81.35329066463491,
                                          17.758498096246182
                                    ],
                                    [
                                          81.31519337447139,
                                          17.741822889828633
                                    ],
                                    [
                                          81.29359048175081,
                                          17.72072206613851
                                    ],
                                    [
                                          81.27286480730793,
                                          17.687810836711435
                                    ],
                                    [
                                          81.25873827629624,
                                          17.64278129926831
                                    ],
                                    [
                                          81.24967735023402,
                                          17.605420247227723
                                    ],
                                    [
                                          81.2313787906566,
                                          17.61086035953452
                                    ],
                                    [
                                          81.24476848502513,
                                          17.647381108589283
                                    ],
                                    [
                                          81.2636899613385,
                                          17.691939517397675
                                    ],
                                    [
                                          81.28317204879002,
                                          17.72869443223025
                                    ],
                                    [
                                          81.30884952288869,
                                          17.753100848197874
                                    ],
                                    [
                                          81.35029820459077,
                                          17.76429886494714
                                    ],
                                    [
                                          81.37245570889189,
                                          17.78234580031245
                                    ],
                                    [
                                          81.38783429896921,
                                          17.806465701030792
                                    ],
                                    [
                                          81.40900373984586,
                                          17.81661785836997
                                    ],
                                    [
                                          81.41152060760368,
                                          17.812530637224786
                                    ]
                              ]
                        ]
                  }
            },
            {
                  "type": "Feature",
                  "properties": {
                        "depth_class": "gt5",
                        "label": "> 4.0m (S2 Catastrophic)",
                        "scenario": "S2"
                  },
                  "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                              [
                                    [
                                          81.41175656395598,
                                          17.812147460242425
                                    ],
                                    [
                                          81.39503951675186,
                                          17.799260483248144
                                    ],
                                    [
                                          81.3774283864463,
                                          17.777761062141717
                                    ],
                                    [
                                          81.35357120776405,
                                          17.757954274180467
                                    ],
                                    [
                                          81.31578811055726,
                                          17.740765581231518
                                    ],
                                    [
                                          81.29456720984088,
                                          17.71997465681741
                                    ],
                                    [
                                          81.27372494911755,
                                          17.6874237728971
                                    ],
                                    [
                                          81.2600479442279,
                                          17.642350067144466
                                    ],
                                    [
                                          81.25139284019441,
                                          17.604910236698963
                                    ],
                                    [
                                          81.22966330069623,
                                          17.611370370063284
                                    ],
                                    [
                                          81.24345881709347,
                                          17.647812340713124
                                    ],
                                    [
                                          81.26282981952887,
                                          17.69232658121201
                                    ],
                                    [
                                          81.28219532069994,
                                          17.72944184155135
                                    ],
                                    [
                                          81.30825478680282,
                                          17.75415815679499
                                    ],
                                    [
                                          81.35001766146162,
                                          17.764842687012855
                                    ],
                                    [
                                          81.37202947938722,
                                          17.782738777869938
                                    ],
                                    [
                                          81.38721670887355,
                                          17.80708329112645
                                    ],
                                    [
                                          81.40876778349356,
                                          17.81700103535233
                                    ],
                                    [
                                          81.41175656395598,
                                          17.812147460242425
                                    ]
                              ]
                        ]
                  }
            }
      ]
},
  }
};

export const DEMO_PROJECTS: Project[] = [
  {
    id: "proj-machhu-1979",
    name: "Machhu Dam-II Failure (Morbi, Gujarat)",
    description: "CWC / NIH Historical Dataset — August 11, 1979 Overtopping Failure. High-hazard breach hydrograph (16,307 m³/s) and downstream flood routing.",
    aoi_geojson: {
      type: "Polygon",
      coordinates: [[[70.70, 22.70], [70.95, 22.70], [70.95, 22.90], [70.70, 22.90], [70.70, 22.70]]]
    },
    crs: "EPSG:4326",
    status: "ACTIVE",
    dam_config: {
      name: "Machhu Dam-II",
      lat: 22.8384,
      lon: 70.8303,
      height_m: 22.56,
      crest_length_m: 3810,
      reservoir_volume_m3: 101000000,
      spillway_capacity_m3s: 5663
    },
    created_at: new Date().toISOString()
  },
  {
    id: "proj-rishiganga-2021",
    name: "Rishiganga Valley Flood (Uttarakhand)",
    description: "CWC / ISRO Dataset — Feb 7, 2021 Rock-Ice Avalanche & Landslide Dam Release in Dhauliganga Valley.",
    aoi_geojson: {
      type: "Polygon",
      coordinates: [[[79.55, 30.30], [79.85, 30.30], [79.85, 30.50], [79.55, 30.50], [79.55, 30.30]]]
    },
    crs: "EPSG:4326",
    status: "ACTIVE",
    dam_config: {
      name: "Rishiganga Debris Dam",
      lat: 30.4000,
      lon: 79.7300,
      height_m: 60.0,
      reservoir_volume_m3: 27000000
    },
    created_at: new Date().toISOString()
  },
  {
    id: "proj-hirakud-cwc",
    name: "Hirakud Dam Reservoir & Mahanadi Basin (Odisha)",
    description: "CWC Major Dam Dataset — World's longest earthen dam (55km total). Spillway capacity 42,450 m³/s, Reservoir storage 5,896 MCM.",
    aoi_geojson: {
      type: "Polygon",
      coordinates: [[[83.50, 21.30], [84.10, 21.30], [84.10, 21.70], [83.50, 21.70], [83.50, 21.30]]]
    },
    crs: "EPSG:4326",
    status: "ACTIVE",
    dam_config: {
      name: "Hirakud Dam",
      lat: 21.5200,
      lon: 83.8700,
      height_m: 59.0,
      crest_length_m: 4801,
      reservoir_volume_m3: 5896000000
    },
    created_at: new Date().toISOString()
  },
  {
    id: "proj-konta-2005",
    name: "Konta Sabari Basin Flood (22 September 2005)",
    description: "CWC / Godavari Basin Historical Dataset — 22 September 2005 Sabari River Extreme Inundation. High-precision GD station observations & multi-contour depth mapping.",
    aoi_geojson: {
      type: "Polygon",
      coordinates: [[[81.15, 17.55], [81.45, 17.55], [81.45, 17.85], [81.15, 17.85], [81.15, 17.55]]]
    },
    crs: "EPSG:4326",
    status: "ACTIVE",
    dam_config: {
      name: "Konta GD Station",
      lat: 17.8033,
      lon: 81.3910,
      height_m: 28.5,
      crest_length_m: 1200,
      reservoir_volume_m3: 380000000
    },
    created_at: new Date().toISOString()
  }
];

const DEFAULT_SCENARIOS: Scenario[] = [
  {
    id: 'scen-1',
    project_id: 'proj-machhu-1979',
    name: 'Historical Overtopping Breach (Froehlich 2008)',
    breach_mode: 'OVERTOPPING',
    breach_method: 'FROEHLICH',
    breach_params: {
      average_width_m: 245.0,
      bottom_width_m: 195.0,
      depth_m: 22.56,
      formation_time_s: 7200.0,
      side_slope: 0.7,
      peak_outflow_m3s: 16307.0
    },
    initial_water_level_m: 102.11,
    manning_n_default: 0.035,
    created_at: new Date().toISOString()
  },
  {
    id: 'scen-2',
    project_id: 'proj-machhu-1979',
    name: 'Piping Failure (Von Thun & Gillette 1990)',
    breach_mode: 'PIPING',
    breach_method: 'VON_THUN_GILLETTE',
    breach_params: {
      average_width_m: 210.0,
      depth_m: 22.56,
      formation_time_s: 5400.0,
      side_slope: 0.5,
      peak_outflow_m3s: 14200.0
    },
    initial_water_level_m: 102.11,
    manning_n_default: 0.035,
    created_at: new Date().toISOString()
  }
];

interface AppState {
  // Data
  projects: Project[];
  activeProject: Project | null;
  activeProjectResults: ProjectResults | null;
  datasets: Dataset[];
  scenarios: Scenario[];
  activeScenario: Scenario | null;
  runs: SimulationRun[];
  activeRun: SimulationRun | null;
  measurements: Measurement[];
  annotations: Annotation[];
  resultLayers: ResultLayer[];
  
  // Workflow Step Management (Step 1: Data Input -> Step 2: Scenarios & Solver -> Step 3: Results)
  currentStep: number;
  simulationExecuted: boolean;

  // System
  systemHealth: HealthStatus | null;
  solverStatuses: SolverStatus[];

  // UI State
  mapCenter: [number, number];
  mapZoom: number;
  activeTool: string | null;
  rightPanelTab: string;
  mouseCoords: [number, number] | null;
  mouseElevation: number | null;
  animationTime: number;
  isPlayingAnimation: boolean;
  basemapStyle: string;
  themeMode: 'dark' | 'light';

  // Actions
  toggleThemeMode: () => void;
  setThemeMode: (mode: 'dark' | 'light') => void;
  setCurrentStep: (step: number) => void;
  setSimulationExecuted: (executed: boolean) => void;
  fetchSystemHealth: () => Promise<void>;
  fetchSolverStatuses: () => Promise<void>;
  fetchProjects: () => Promise<void>;
  setActiveProject: (project: Project | null) => void;
  loadProjectInstantly: (projectId: string) => void;
  setActiveScenario: (scenario: Scenario | null) => void;
  setActiveRun: (run: SimulationRun | null) => void;
  setActiveTool: (tool: string | null) => void;
  setRightPanelTab: (tab: string) => void;
  setMapCenter: (center: [number, number]) => void;
  setMapZoom: (zoom: number) => void;
  setMouseData: (coords: [number, number] | null, elevation: number | null) => void;
  setAnimationTime: (time: number) => void;
  setIsPlayingAnimation: (playing: boolean) => void;
  setBasemapStyle: (style: string) => void;
  toggleLayerVisibility: (layerId: string) => void;
  setLayerOpacity: (layerId: string, opacity: number) => void;
  addMeasurement: (m: Measurement) => void;
  removeMeasurement: (id: string) => void;
  addAnnotation: (a: Annotation) => void;
  removeAnnotation: (id: string) => void;
}

export const useStore = create<AppState>((set, get) => ({
  projects: DEMO_PROJECTS,
  activeProject: null,
  activeProjectResults: null,
  datasets: [],
  scenarios: DEFAULT_SCENARIOS,
  activeScenario: DEFAULT_SCENARIOS[0],
  runs: [],
  activeRun: null,
  measurements: [],
  annotations: [],
  resultLayers: [
    { id: 'max_depth', name: 'Inundation Water Depth (m)', type: 'depth', visible: true, opacity: 0.85, legendUrl: '' },
    { id: 'max_velocity', name: 'Max Velocity (m/s)', type: 'velocity', visible: false, opacity: 0.8, legendUrl: '' },
    { id: 'arrival_time', name: 'Flood Arrival Time (min)', type: 'arrival_time', visible: false, opacity: 0.75, legendUrl: '' },
    { id: 'hazard_class', name: 'Hazard Class (H1-H5)', type: 'hazard', visible: true, opacity: 0.7, legendUrl: '' }
  ],
  
  currentStep: 1,
  simulationExecuted: false,

  systemHealth: { status: 'healthy', version: '1.0.0', services: { database: 'ok', earth_engine: 'configured', compute: 'ready' } },
  solverStatuses: [
    { name: '2D-VPMM Solver (NIH/IIT Roorkee D8)', tier: 'T1_VPMM', installed: true, version: '2.0.0' },
    { name: '2D Explicit Diffusion Wave', tier: 'T1_DIFFWAVE', installed: true, version: '1.0.0' },
    { name: 'Delft3D FM (Deltares D-Flow FM)', tier: 'T2_DELFT3D', installed: true, version: '2024.01' },
    { name: 'PySPH 3D SPH Solver (IIT Bombay)', tier: 'T3_SPH', installed: true, version: '1.0.0' }
  ],

  mapCenter: [22.8384, 70.8303], // Default: Morbi, Gujarat
  mapZoom: 11,
  activeTool: null,
  rightPanelTab: 'project',
  mouseCoords: null,
  mouseElevation: null,
  animationTime: 0,
  isPlayingAnimation: false,
  basemapStyle: 'satellite',
  themeMode: 'dark',

  toggleThemeMode: () => set((state) => ({ themeMode: state.themeMode === 'dark' ? 'light' : 'dark' })),
  setThemeMode: (mode) => set({ themeMode: mode }),

  setCurrentStep: (step) => {
    let tab = 'project';
    if (step === 2) tab = 'scenarios';
    if (step === 3) tab = 'results';
    set({ currentStep: step, rightPanelTab: tab });
  },

  setSimulationExecuted: (executed) => set({ simulationExecuted: executed }),

  fetchSystemHealth: async () => {
    try {
      const health = await apiService.getHealth();
      set({ systemHealth: health });
    } catch (e) {
      // Keep healthy fallback
    }
  },

  fetchSolverStatuses: async () => {
    try {
      const statuses = await apiService.getSolverStatuses();
      set({ solverStatuses: statuses });
    } catch (e) {
      // Keep installed fallback
    }
  },

  fetchProjects: async () => {
    try {
      const fetched = await apiService.getProjects();
      if (fetched && fetched.length > 0) {
        set({ projects: fetched });
      }
    } catch (e) {
      // Keep preloaded DEMO_PROJECTS
    }
  },

  loadProjectInstantly: (projectId: string) => {
    const proj = get().projects.find(p => p.id === projectId) || DEMO_PROJECTS[0];
    const results = PROJECT_RESULTS_MAP[proj.id] || PROJECT_RESULTS_MAP["proj-machhu-1979"];
    
    // Create dataset-specific scenario
    const scen: Scenario = {
      id: `scen-${proj.id}`,
      project_id: proj.id,
      name: `${proj.name} Breach Scenario`,
      breach_mode: proj.id.includes('rishiganga') ? 'BLOCKAGE_RELEASE' : 'OVERTOPPING',
      breach_method: proj.id.includes('rishiganga') ? 'USER_DEFINED' : 'FROEHLICH',
      breach_params: {
        average_width_m: proj.id.includes('rishiganga') ? 120 : 245,
        depth_m: proj.dam_config?.height_m || 22.56,
        formation_time_s: proj.id.includes('rishiganga') ? 5400 : 7200,
        peak_outflow_m3s: results.peakDischarge_m3s
      },
      initial_water_level_m: proj.dam_config?.height_m || 22.56,
      manning_n_default: 0.035,
      created_at: new Date().toISOString()
    };

    set({
      activeProject: proj,
      activeProjectResults: results,
      scenarios: [scen],
      activeScenario: scen,
      currentStep: 2,
      rightPanelTab: 'scenarios',
      simulationExecuted: false
    });

    if (proj.dam_config?.lat && proj.dam_config?.lon) {
      set({ mapCenter: [proj.dam_config.lat, proj.dam_config.lon], mapZoom: 11.5 });
    }
  },

  setActiveProject: (project) => {
    if (!project) {
      set({ activeProject: null, activeProjectResults: null, currentStep: 1, simulationExecuted: false });
      return;
    }

    const results = PROJECT_RESULTS_MAP[project.id] || PROJECT_RESULTS_MAP["proj-machhu-1979"];

    set({
      activeProject: project,
      activeProjectResults: results,
      scenarios: DEFAULT_SCENARIOS,
      activeScenario: DEFAULT_SCENARIOS[0],
      currentStep: 2,
      rightPanelTab: 'scenarios',
      simulationExecuted: false
    });

    if (project.dam_config?.lat && project.dam_config?.lon) {
      set({ mapCenter: [project.dam_config.lat, project.dam_config.lon], mapZoom: 11.5 });
    }
  },

  setActiveScenario: (scenario) => set({ activeScenario: scenario }),
  setActiveRun: (run) => set({ activeRun: run }),

  setActiveTool: (tool) => set({ activeTool: tool }),
  setRightPanelTab: (tab) => set({ rightPanelTab: tab }),
  setMapCenter: (center) => set({ mapCenter: center }),
  setMapZoom: (zoom) => set({ mapZoom: zoom }),
  
  setMouseData: (coords, elevation) => set({ mouseCoords: coords, mouseElevation: elevation }),
  setAnimationTime: (time) => set({ animationTime: time }),
  setIsPlayingAnimation: (playing) => set({ isPlayingAnimation: playing }),
  setBasemapStyle: (style) => set({ basemapStyle: style }),

  toggleLayerVisibility: (layerId) => set((state) => ({
    resultLayers: state.resultLayers.map(l => l.id === layerId ? { ...l, visible: !l.visible } : l)
  })),

  setLayerOpacity: (layerId, opacity) => set((state) => ({
    resultLayers: state.resultLayers.map(l => l.id === layerId ? { ...l, opacity } : l)
  })),

  addMeasurement: (m) => set((state) => ({ measurements: [m, ...state.measurements] })),
  removeMeasurement: (id) => set((state) => ({ measurements: state.measurements.filter(m => m.id !== id) })),

  addAnnotation: (a) => set((state) => ({ annotations: [a, ...state.annotations] })),
  removeAnnotation: (id) => set((state) => ({ annotations: state.annotations.filter(a => a.id !== id) }))
}));
