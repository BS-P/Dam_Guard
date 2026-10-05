export const WarningsPanel = () => {
  const warnings = [
    { id: 1, severity: 'error', source: 'Validity Mask', message: 'Water surface elevation exceeds DEM bounds near boundary edge.' },
    { id: 2, severity: 'warning', source: 'Solver (T2)', message: 'Delft3D solver unavailable. Falling back to T1 VPMM.' },
    { id: 3, severity: 'info', source: 'Data Loading', message: 'Using Copernicus GLO-30 DEM. Local high-res DEM not found.' },
  ];

  const severityStyles = {
    error: 'border-red-500/50 bg-red-900/10 text-red-400',
    warning: 'border-orange-500/50 bg-orange-900/10 text-orange-400',
    info: 'border-blue-500/50 bg-blue-900/10 text-blue-400',
  };

  return (
    <div className="flex flex-col h-full bg-slate-900/90 backdrop-blur-md border-r border-slate-700 w-80 text-slate-200 p-4">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-semibold text-red-400 tracking-wide flex items-center gap-2">
          System Alerts
          <span className="bg-red-500 text-white text-[10px] px-1.5 py-0.5 rounded-full font-bold">1</span>
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3">
        {warnings.map(w => (
          <div key={w.id} className={`p-3 rounded border cursor-pointer hover:opacity-80 transition-opacity ${severityStyles[w.severity as keyof typeof severityStyles]}`}>
            <div className="text-xs font-bold uppercase tracking-wider mb-1 flex items-center space-x-1">
              <span>{w.source}</span>
            </div>
            <div className="text-sm">
              {w.message}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
