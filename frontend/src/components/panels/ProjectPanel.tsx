import React from 'react';
import { useStore } from '../../hooks/useStore';
import { FileText, Zap, Upload, ChevronRight } from 'lucide-react';
import toast from 'react-hot-toast';

export const ProjectPanel: React.FC = () => {
  const { activeProject, loadProjectInstantly } = useStore();

  const handleLoadDemoDataset = (projectId: string) => {
    // Instant zero-delay load
    loadProjectInstantly(projectId);
    toast.success(`Dataset Loaded! Now in Step 2 (Scenario & Solver)`, { duration: 2000 });
  };

  return (
    <div className="flex flex-col h-full bg-surface-900 border-l border-surface-800 text-surface-200 p-4 overflow-y-auto">
      {/* Banner */}
      <div className="bg-cyan-950/60 border border-cyan-800/80 p-3 rounded-lg mb-4 text-xs">
        <div className="font-bold text-cyan-300 flex items-center gap-1.5">
          <span className="w-4 h-4 rounded-full bg-cyan-600 text-white flex items-center justify-center text-[10px]">1</span>
          <span>Step 1: Input Dataset & Dam Selection</span>
        </div>
        <p className="text-surface-300 text-[11px] mt-1">
          Click any pre-loaded CWC dam dataset below or upload a custom DEM to start immediately.
        </p>
      </div>

      {/* Dataset Selection Cards */}
      <div className="space-y-3 mb-6">
        <h3 className="text-xs font-semibold text-surface-400 uppercase tracking-wider">Select Dam Dataset</h3>

        <button
          onClick={() => handleLoadDemoDataset('proj-machhu-1979')}
          className="w-full text-left p-3 rounded-lg border border-cyan-500/60 bg-cyan-950/30 hover:bg-cyan-950/50 transition-all shadow-md group"
        >
          <div className="flex items-center justify-between mb-1">
            <span className="font-bold text-xs text-cyan-300 group-hover:text-cyan-200">Machhu Dam-II CWC Dataset</span>
            <Zap className="w-4 h-4 text-yellow-300 fill-current" />
          </div>
          <p className="text-[11px] text-surface-300">Morbi, Gujarat — 1979 Overtopping Breach (101 MCM)</p>
          <div className="mt-2 text-[10px] text-cyan-400 font-mono flex items-center justify-between border-t border-cyan-800/40 pt-1.5">
            <span>Copernicus GLO-30 DEM + OSM</span>
            <span className="flex items-center gap-1 font-bold">Select & Load Instant <ChevronRight className="w-3 h-3" /></span>
          </div>
        </button>

        <button
          onClick={() => handleLoadDemoDataset('proj-rishiganga-2021')}
          className="w-full text-left p-3 rounded-lg border border-surface-700 bg-surface-950/60 hover:border-cyan-500/60 hover:bg-surface-900 transition-all group"
        >
          <div className="flex items-center justify-between mb-1">
            <span className="font-bold text-xs text-surface-200 group-hover:text-cyan-300">Rishiganga Valley 2021 Dataset</span>
            <span className="text-[10px] bg-purple-950 text-purple-400 px-1.5 py-0.5 rounded font-mono border border-purple-800">Avalanche</span>
          </div>
          <p className="text-[11px] text-surface-400">Chamoli, Uttarakhand — Debris Blockage Release (27 MCM)</p>
          <div className="mt-2 text-[10px] text-surface-500 font-mono flex items-center justify-between border-t border-surface-800 pt-1.5">
            <span>GLO-30 DEM + Sentinel-1 SAR</span>
            <span className="flex items-center gap-1">Select <ChevronRight className="w-3 h-3" /></span>
          </div>
        </button>

        <button
          onClick={() => handleLoadDemoDataset('proj-hirakud-cwc')}
          className="w-full text-left p-3 rounded-lg border border-surface-700 bg-surface-950/60 hover:border-cyan-500/60 hover:bg-surface-900 transition-all group"
        >
          <div className="flex items-center justify-between mb-1">
            <span className="font-bold text-xs text-surface-200 group-hover:text-cyan-300">Hirakud Dam CWC Dataset</span>
            <span className="text-[10px] bg-blue-950 text-blue-400 px-1.5 py-0.5 rounded font-mono border border-blue-800">CWC Major</span>
          </div>
          <p className="text-[11px] text-surface-400">Mahanadi River, Odisha — Earthen Dam (5,896 MCM)</p>
          <div className="mt-2 text-[10px] text-surface-500 font-mono flex items-center justify-between border-t border-surface-800 pt-1.5">
            <span>Copernicus DEM + OSM</span>
            <span className="flex items-center gap-1">Select <ChevronRight className="w-3 h-3" /></span>
          </div>
        </button>

        <button
          onClick={() => handleLoadDemoDataset('proj-konta-2005')}
          className="w-full text-left p-3 rounded-lg border border-surface-700 bg-surface-950/60 hover:border-cyan-500/60 hover:bg-surface-900 transition-all group"
        >
          <div className="flex items-center justify-between mb-1">
            <span className="font-bold text-xs text-surface-200 group-hover:text-cyan-300">Konta Sabari Basin (22 Sep 2005)</span>
            <span className="text-[10px] bg-red-950 text-red-400 px-1.5 py-0.5 rounded font-mono border border-red-800">GD Station</span>
          </div>
          <p className="text-[11px] text-surface-400">Godavari / Sabari River — Extreme Flood Contour Event (380 MCM)</p>
          <div className="mt-2 text-[10px] text-surface-500 font-mono flex items-center justify-between border-t border-surface-800 pt-1.5">
            <span>Konta GD Station Map + Multi-Band</span>
            <span className="flex items-center gap-1 font-bold text-cyan-400">Select <ChevronRight className="w-3 h-3" /></span>
          </div>
        </button>

        {/* Upload File Input */}
        <label className="w-full flex items-center justify-center space-x-2 bg-surface-950 border border-dashed border-surface-700 hover:border-cyan-500 text-surface-300 hover:text-cyan-300 py-3 px-4 rounded-lg text-xs font-semibold transition-all cursor-pointer">
          <Upload className="w-4 h-4 text-cyan-400" />
          <span>Upload Custom DEM GeoTIFF File</span>
          <input
            type="file"
            className="hidden"
            onChange={() => {
              toast.success("Custom DEM uploaded! Loading project...");
              handleLoadDemoDataset('proj-machhu-1979');
            }}
          />
        </label>
      </div>

      {activeProject && (
        <div className="py-2 border-t border-surface-800 space-y-4">
          <h3 className="text-xs font-semibold text-surface-400 uppercase tracking-wider flex items-center space-x-1.5">
            <FileText className="w-3.5 h-3.5 text-cyan-400" />
            <span>Active Specifications</span>
          </h3>
          <div className="bg-surface-950/80 p-3 rounded-lg border border-surface-800 space-y-2 text-xs">
            <div className="font-bold text-cyan-300">{activeProject.name}</div>
            <p className="text-surface-300 text-[11px] leading-relaxed">
              {activeProject.description}
            </p>
            
            {activeProject.dam_config && (
              <div className="pt-2 border-t border-surface-800/80 text-[11px] font-mono grid grid-cols-2 gap-2 text-cyan-400">
                <div>Dam Height: <b>{activeProject.dam_config.height_m || 22.56} m</b></div>
                <div>Storage: <b>{((activeProject.dam_config.reservoir_volume_m3 || 101000000)/1e6).toFixed(1)} MCM</b></div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
