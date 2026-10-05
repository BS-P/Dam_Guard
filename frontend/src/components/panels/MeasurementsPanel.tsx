export const MeasurementsPanel = () => {
  const measurements = [
    { id: 1, type: 'distance', name: 'River Reach 1', value: '4.2 km' },
    { id: 2, type: 'area', name: 'Impact Zone Alpha', value: '12.5 km²' },
    { id: 3, type: 'point', name: 'City Center Probe', value: 'Max Depth: 4.1m' },
  ];

  return (
    <div className="flex flex-col h-full bg-slate-900/90 backdrop-blur-md border-r border-slate-700 w-80 text-slate-200 p-4">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-semibold text-orange-400 tracking-wide">Measurements</h2>
      </div>

      {measurements.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-slate-500 text-sm text-center p-4">
          No measurements. Use the Measure tools in the left rail.
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto space-y-2">
          {measurements.map(m => (
            <div key={m.id} className="p-3 bg-slate-800 rounded border border-slate-700 hover:border-orange-500/50 cursor-pointer group">
              <div className="flex justify-between items-start">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-orange-500"></div>
                  <span className="text-sm font-medium">{m.name}</span>
                </div>
                <button className="text-slate-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity">
                  &times;
                </button>
              </div>
              <div className="mt-1 ml-4 text-xs text-slate-400 font-mono">
                {m.value}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
