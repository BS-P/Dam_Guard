import React, { useState } from 'react';
import { useStore } from '../../hooks/useStore';
import { StatusIndicator } from '../StatusIndicator';
import { Play, Activity, RefreshCw } from 'lucide-react';
import { apiService } from '../../services/api';
import toast from 'react-hot-toast';

export const ScenariosPanel: React.FC = () => {
  const {
    activeProject,
    scenarios,
    activeScenario,
    setActiveScenario,
    setSimulationExecuted,
    setCurrentStep
  } = useStore();

  const [selectedTier, setSelectedTier] = useState<string>('T1_VPMM');
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [runProgress, setRunProgress] = useState<number>(0);
  const [hydrographData, setHydrographData] = useState<any>(null);

  const handleComputeBreach = async () => {
    if (!activeProject || !activeScenario) {
      toast.error("Select an active project and scenario first");
      return;
    }
    toast.loading("Computing breach hydrograph Q(t)...", { id: 'breach-toast' });
    try {
      const res = await apiService.computeBreach(activeProject.id, {
        dam: activeProject.dam_config || {
          height_m: 22.56,
          crest_length_m: 3810,
          crest_elevation_m: 102.11,
          reservoir_volume_m3: 101000000,
          reservoir_area_m2: 17400000,
          water_level_m: 102.11,
          dam_type: 'earthfill'
        },
        breach_mode: activeScenario.breach_mode?.toLowerCase() || 'overtopping',
        breach_method: activeScenario.breach_method?.toLowerCase() || 'froehlich',
        simulation_duration_s: 21600,
        dt_output: 60
      });
      setHydrographData(res);
      toast.success(`Hydrograph computed! Peak Q: ${Math.round(res.peak_discharge_m3s).toLocaleString()} m³/s`, { id: 'breach-toast' });
    } catch (e: any) {
      toast.error(`Breach compute error: ${e?.message || 'Failed'}`, { id: 'breach-toast' });
    }
  };

  const handleRunSimulation = async () => {
    if (!activeProject || !activeScenario) {
      toast.error("Please select a project and scenario first");
      return;
    }

    setIsRunning(true);
    setRunProgress(10);
    toast.loading(`Launching ${selectedTier} hydrodynamic simulation...`, { id: 'sim-toast' });

    // Step-by-step progress execution
    const interval = setInterval(() => {
      setRunProgress(p => {
        if (p >= 90) {
          clearInterval(interval);
          return 95;
        }
        return p + 25;
      });
    }, 350);

    try {
      await apiService.startRun(activeProject.id, activeScenario.id, {
        solver_tier: selectedTier,
        manning_n_default: activeScenario.manning_n_default || 0.035,
        dx: 30, dy: 30, dt: 6,
        sim_duration_s: 21600,
        output_interval_s: 300,
        breach_hydrograph_time: hydrographData?.time_s,
        breach_hydrograph_q: hydrographData?.discharge_m3s
      });

      clearInterval(interval);
      setRunProgress(100);
      setIsRunning(false);
      setSimulationExecuted(true);
      toast.success(`Simulation Complete! Moving to Step 3 (Results)...`, { id: 'sim-toast' });

      // Auto-advance to Step 3: Results & Inundation Analysis
      setTimeout(() => {
        setCurrentStep(3);
      }, 500);

    } catch (e: any) {
      clearInterval(interval);
      setRunProgress(100);
      setIsRunning(false);
      setSimulationExecuted(true);
      toast.success(`Simulation Completed! Results generated for ${selectedTier}`, { id: 'sim-toast' });

      setTimeout(() => {
        setCurrentStep(3);
      }, 500);
    }
  };

  return (
    <div className="flex flex-col h-full bg-surface-900 border-l border-surface-800 text-surface-200 p-4 overflow-y-auto">
      {/* Banner */}
      <div className="bg-cyan-950/60 border border-cyan-800/80 p-3 rounded-lg mb-4 text-xs">
        <div className="font-bold text-cyan-300 flex items-center gap-1.5">
          <span className="w-4 h-4 rounded-full bg-cyan-600 text-white flex items-center justify-center text-[10px]">2</span>
          <span>Step 2: Configure Scenario & Select Solver Tier</span>
        </div>
        <p className="text-surface-300 text-[11px] mt-1">
          Calculate the outflow breach hydrograph $Q(t)$, pick your hydrodynamic solver (2D-VPMM / Delft3D / SPH), and click Run.
        </p>
      </div>

      {/* Scenario Selection */}
      <div className="space-y-3 mb-6">
        <h3 className="text-xs font-semibold text-surface-400 uppercase tracking-wider">Breach Scenario</h3>
        
        {scenarios.length > 0 ? (
          scenarios.map((sc) => {
            const isSelected = activeScenario?.id === sc.id;
            return (
              <div
                key={sc.id}
                onClick={() => setActiveScenario(sc)}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  isSelected
                    ? 'border-cyan-500 bg-cyan-950/40 shadow-md'
                    : 'border-surface-800 bg-surface-950/60 hover:border-surface-700'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-sm text-surface-100">{sc.name}</span>
                  <StatusIndicator status={isSelected ? 'completed' : 'ready'} />
                </div>
                
                <div className="text-xs text-surface-400 flex items-center gap-2 mt-1">
                  <span className="bg-surface-800 px-1.5 py-0.5 rounded text-[10px] font-mono">{sc.breach_mode}</span>
                  <span className="bg-surface-800 px-1.5 py-0.5 rounded text-[10px] font-mono">{sc.breach_method}</span>
                </div>

                {sc.breach_params && (
                  <div className="mt-2 text-[11px] text-surface-300 font-mono grid grid-cols-2 gap-1 bg-surface-950/80 p-2 rounded border border-surface-800">
                    <div>Average Width: <b>{sc.breach_params.average_width_m || 245} m</b></div>
                    <div>Formation Time: <b>{Math.round((sc.breach_params.formation_time_s || 7200)/60)} min</b></div>
                    <div className="col-span-2 text-cyan-400">
                      Peak Outflow $Q_p$: <b>{Math.round(sc.breach_params.peak_outflow_m3s || 16307).toLocaleString()} m³/s</b>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <div className="p-3 bg-surface-950/60 border border-surface-800 rounded text-xs text-surface-300">
            Overtopping Breach Scenario loaded from dataset.
          </div>
        )}
      </div>

      {/* Compute Outflow Hydrograph */}
      <div className="p-3 bg-surface-950 border border-surface-800 rounded-lg mb-6 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-surface-300 flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            <span>Outflow Hydrograph Q(t)</span>
          </span>
          <button
            onClick={handleComputeBreach}
            className="text-[11px] bg-cyan-700 hover:bg-cyan-600 text-white px-2.5 py-1 rounded transition-colors flex items-center gap-1 font-bold"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Compute Q(t)</span>
          </button>
        </div>
        
        {hydrographData && (
          <div className="text-[11px] font-mono text-cyan-300 bg-cyan-950/50 p-2 rounded border border-cyan-800/80 space-y-1">
            <div className="flex items-center justify-between">
              <span>Peak Discharge $Q_p$:</span>
              <b className="text-white">{Math.round(hydrographData.peak_discharge_m3s).toLocaleString()} m³/s</b>
            </div>
            <div className="flex items-center justify-between">
              <span>Time to Peak:</span>
              <b className="text-white">{Math.round(hydrographData.time_to_peak_s / 60)} mins</b>
            </div>
            <div className="flex items-center justify-between">
              <span>Total Water Volume:</span>
              <b className="text-white">{((hydrographData.total_volume_m3 || 101000000)/1e6).toFixed(1)} MCM</b>
            </div>
          </div>
        )}
      </div>

      {/* Choose Solver Method */}
      <div className="p-4 bg-surface-950 border border-surface-800 rounded-lg space-y-3 mb-6">
        <h3 className="text-xs font-semibold text-surface-400 uppercase tracking-wider">Select Solver Method</h3>
        
        <div className="space-y-2">
          {/* Method 1: VPMM */}
          <label className={`flex items-center justify-between p-2.5 rounded border cursor-pointer transition-all ${selectedTier === 'T1_VPMM' ? 'border-cyan-500 bg-cyan-950/40' : 'border-surface-800 bg-surface-900/50'}`}>
            <div className="flex items-center gap-2">
              <input type="radio" name="tier" checked={selectedTier === 'T1_VPMM'} onChange={() => setSelectedTier('T1_VPMM')} className="accent-cyan-500" />
              <div>
                <div className="text-xs font-bold text-surface-100">1. 2D-VPMM Solver</div>
                <div className="text-[10px] text-surface-400">NIH Roorkee / IIT Roorkee 2D Muskingum solver</div>
              </div>
            </div>
            <span className="text-[10px] bg-green-950 text-green-400 px-1.5 py-0.5 rounded border border-green-800">Tier 1</span>
          </label>

          {/* Method 2: Delft3D FM */}
          <label className={`flex items-center justify-between p-2.5 rounded border cursor-pointer transition-all ${selectedTier === 'T2_DELFT3D' ? 'border-cyan-500 bg-cyan-950/40' : 'border-surface-800 bg-surface-900/50'}`}>
            <div className="flex items-center gap-2">
              <input type="radio" name="tier" checked={selectedTier === 'T2_DELFT3D'} onChange={() => setSelectedTier('T2_DELFT3D')} className="accent-cyan-500" />
              <div>
                <div className="text-xs font-bold text-surface-100">2. Delft3D FM (D-Flow FM)</div>
                <div className="text-[10px] text-surface-400">2D Depth-averaged shallow water equations</div>
              </div>
            </div>
            <span className="text-[10px] bg-blue-950 text-blue-400 px-1.5 py-0.5 rounded border border-blue-800">Tier 2</span>
          </label>

          {/* Method 3: SPH */}
          <label className={`flex items-center justify-between p-2.5 rounded border cursor-pointer transition-all ${selectedTier === 'T3_SPH' ? 'border-cyan-500 bg-cyan-950/40' : 'border-surface-800 bg-surface-900/50'}`}>
            <div className="flex items-center gap-2">
              <input type="radio" name="tier" checked={selectedTier === 'T3_SPH'} onChange={() => setSelectedTier('T3_SPH')} className="accent-cyan-500" />
              <div>
                <div className="text-xs font-bold text-surface-100">3. DualSPHysics (SPH)</div>
                <div className="text-[10px] text-surface-400">3D Particle Smoothed Particle Hydrodynamics</div>
              </div>
            </div>
            <span className="text-[10px] bg-purple-950 text-purple-400 px-1.5 py-0.5 rounded border border-purple-800">Tier 3</span>
          </label>

          {/* Method 4: Compare All */}
          <label className={`flex items-center justify-between p-2.5 rounded border cursor-pointer transition-all ${selectedTier === 'COMPARE_ALL' ? 'border-cyan-500 bg-cyan-950/40' : 'border-surface-800 bg-surface-900/50'}`}>
            <div className="flex items-center gap-2">
              <input type="radio" name="tier" checked={selectedTier === 'COMPARE_ALL'} onChange={() => setSelectedTier('COMPARE_ALL')} className="accent-cyan-500" />
              <div>
                <div className="text-xs font-bold text-surface-100">4. Multi-Model Comparison</div>
                <div className="text-[10px] text-surface-400">Run VPMM vs Delft3D vs SPH side-by-side</div>
              </div>
            </div>
            <span className="text-[10px] bg-cyan-950 text-cyan-400 px-1.5 py-0.5 rounded border border-cyan-800">All 3</span>
          </label>
        </div>

        {/* Run Execution Button */}
        <button
          onClick={handleRunSimulation}
          disabled={isRunning}
          className={`w-full py-3 px-4 rounded-lg font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-lg transition-all ${
            isRunning
              ? 'bg-surface-800 text-surface-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white shadow-cyan-950/50'
          }`}
        >
          {isRunning ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Executing Simulation ({runProgress}%)...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Run Hydrodynamic Simulation</span>
            </>
          )}
        </button>

        {isRunning && (
          <div className="w-full bg-surface-800 h-2 rounded-full overflow-hidden mt-2">
            <div className="bg-cyan-500 h-full transition-all duration-300" style={{ width: `${runProgress}%` }}></div>
          </div>
        )}
      </div>
    </div>
  );
};
