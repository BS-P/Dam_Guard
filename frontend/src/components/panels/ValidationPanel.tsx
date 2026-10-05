export const ValidationPanel = () => {
  return (
    <div className="flex flex-col h-full bg-slate-900/90 backdrop-blur-md border-l border-slate-700 w-96 text-slate-200 p-4 overflow-y-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-semibold text-green-400 tracking-wide">Validation</h2>
        <button className="bg-slate-700 hover:bg-slate-600 text-white text-xs px-3 py-1.5 rounded transition-colors">
          Run Validation
        </button>
      </div>

      <div className="space-y-6">
        <section>
          <h3 className="text-sm text-slate-400 mb-3 font-medium uppercase">Benchmark Results (V-Catchment)</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-800 p-3 rounded border border-slate-700">
              <div className="text-xs text-slate-400 mb-1">NSE</div>
              <div className="text-lg text-green-400 font-mono">0.992</div>
            </div>
            <div className="bg-slate-800 p-3 rounded border border-slate-700">
              <div className="text-xs text-slate-400 mb-1">Mass Error</div>
              <div className="text-lg text-green-400 font-mono">&lt; 0.1%</div>
            </div>
          </div>
        </section>

        <section>
          <h3 className="text-sm text-slate-400 mb-3 font-medium uppercase">Extent Metrics vs Observed</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-800 p-2 rounded border border-slate-700">
              <div className="text-xs text-slate-400">Hit Rate (H)</div>
              <div className="text-md font-mono">87.4%</div>
            </div>
            <div className="bg-slate-800 p-2 rounded border border-slate-700">
              <div className="text-xs text-slate-400">FAR</div>
              <div className="text-md font-mono">12.1%</div>
            </div>
            <div className="bg-slate-800 p-2 rounded border border-slate-700">
              <div className="text-xs text-slate-400">CSI</div>
              <div className="text-md font-mono">78.5%</div>
            </div>
            <div className="bg-slate-800 p-2 rounded border border-slate-700">
              <div className="text-xs text-slate-400">F1 Score</div>
              <div className="text-md font-mono">0.86</div>
            </div>
          </div>
        </section>

        <section>
          <h3 className="text-sm text-slate-400 mb-3 font-medium uppercase">Cross-Tier Comparison</h3>
          <div className="overflow-x-auto border border-slate-700 rounded">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-800 border-b border-slate-700">
                <tr>
                  <th className="p-2">Metric</th>
                  <th className="p-2 text-cyan-400">T1 VPMM</th>
                  <th className="p-2 text-slate-400">T2 Delft3D</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700 font-mono">
                <tr>
                  <td className="p-2 bg-slate-800/50">Peak Depth</td>
                  <td className="p-2">14.2m</td>
                  <td className="p-2 text-slate-500">Not eval</td>
                </tr>
                <tr>
                  <td className="p-2 bg-slate-800/50">Arrival Time</td>
                  <td className="p-2">45m</td>
                  <td className="p-2 text-slate-500">Not eval</td>
                </tr>
                <tr>
                  <td className="p-2 bg-slate-800/50">Runtime</td>
                  <td className="p-2 text-green-400">12s</td>
                  <td className="p-2 text-slate-500">Not eval</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
};
