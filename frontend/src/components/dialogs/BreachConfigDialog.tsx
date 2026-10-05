import { HydrographChart } from '../charts/HydrographChart';
import { ModelOutputLabel } from '../DataLabels';

export const BreachConfigDialog = () => {

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-5xl bg-slate-900 border border-slate-700 shadow-2xl shadow-orange-900/20 rounded-lg overflow-hidden flex flex-col h-[80vh]">
        <div className="p-4 border-b border-slate-700 bg-slate-800/50 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-slate-200">Breach Configuration</h2>
          <button className="text-slate-400 hover:text-white">&times;</button>
        </div>
        
        <div className="flex flex-1 overflow-hidden">
          {/* Left Panel - Configuration */}
          <div className="w-1/3 border-r border-slate-700 p-4 overflow-y-auto space-y-6">
            <section>
              <h3 className="text-sm font-medium text-cyan-400 mb-3 uppercase tracking-wider">Dam Parameters</h3>
              <div className="space-y-3">
                {['Height (m)', 'Crest Length (m)', 'Crest Elev (m)', 'Reservoir Vol (m³)', 'Water Level (m)'].map(label => (
                  <div key={label} className="flex justify-between items-center">
                    <label className="text-xs text-slate-300">{label}</label>
                    <input type="number" className="w-24 bg-slate-800 border border-slate-600 rounded p-1 text-sm text-right text-white" />
                  </div>
                ))}
              </div>
            </section>
            
            <section>
              <h3 className="text-sm font-medium text-orange-400 mb-3 uppercase tracking-wider">Breach Model</h3>
              <div className="space-y-3">
                <div className="space-y-1">
                  <label className="text-xs text-slate-300">Failure Mode</label>
                  <select className="w-full bg-slate-800 border border-slate-600 rounded p-1.5 text-sm text-white">
                    <option>Overtopping</option>
                    <option>Piping</option>
                    <option>Sudden Failure</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-xs text-slate-300">Methodology</label>
                  <select className="w-full bg-slate-800 border border-slate-600 rounded p-1.5 text-sm text-white">
                    <option>Froehlich (2008)</option>
                    <option>Von Thun & Gillette (1990)</option>
                    <option>MacDonald & Langridge-Monopolis</option>
                    <option>User Defined</option>
                  </select>
                </div>
              </div>
            </section>
            
            <button className="w-full py-2 bg-orange-600 hover:bg-orange-500 text-white rounded text-sm transition-colors font-medium mt-4">
              Compute Breach Hydrograph
            </button>
          </div>
          
          {/* Right Panel - Results */}
          <div className="flex-1 p-6 bg-slate-900/50 flex flex-col">
            <div className="mb-4">
              <ModelOutputLabel solver="Froehlich Empirical" />
            </div>
            
            <div className="flex-1 mb-6">
              <HydrographChart data={[
                { time_s: 0, discharge_m3s: 0, breach_width_m: 0 },
                { time_s: 3600, discharge_m3s: 15000, breach_width_m: 20 },
                { time_s: 7200, discharge_m3s: 45000, breach_width_m: 55 },
                { time_s: 10800, discharge_m3s: 22000, breach_width_m: 60 },
                { time_s: 14400, discharge_m3s: 5000, breach_width_m: 60 }
              ]} />
            </div>
            
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-slate-800 p-3 rounded border border-slate-700">
                <div className="text-xs text-slate-400">Peak Discharge</div>
                <div className="text-lg text-orange-400 font-mono">45,000 <span className="text-xs">m³/s</span></div>
              </div>
              <div className="bg-slate-800 p-3 rounded border border-slate-700">
                <div className="text-xs text-slate-400">Time to Peak</div>
                <div className="text-lg text-orange-400 font-mono">2.0 <span className="text-xs">hrs</span></div>
              </div>
              <div className="bg-slate-800 p-3 rounded border border-slate-700">
                <div className="text-xs text-slate-400">Final Width</div>
                <div className="text-lg text-orange-400 font-mono">60.0 <span className="text-xs">m</span></div>
              </div>
              <div className="bg-slate-800 p-3 rounded border border-slate-700">
                <div className="text-xs text-slate-400">Mass Error</div>
                <div className="text-lg text-green-400 font-mono">+0.02 <span className="text-xs">%</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
