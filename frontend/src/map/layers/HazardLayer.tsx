export const HazardLayer = () => {
  // Returns UI configuration for the Hazard Polygons Layer.
  // Renders H1(green) to H5(dark red).
  
  return (
    <div className="absolute top-32 right-4 bg-slate-900/80 p-3 rounded border border-slate-700 z-10 w-48 shadow-lg">
      <h3 className="text-xs text-orange-400 font-bold mb-2 uppercase">Hazard Class</h3>
      <div className="space-y-1.5">
        {[
          { id: 'H5', color: 'bg-red-800', label: 'Extreme' },
          { id: 'H4', color: 'bg-red-500', label: 'High' },
          { id: 'H3', color: 'bg-orange-500', label: 'Significant' },
          { id: 'H2', color: 'bg-yellow-400', label: 'Moderate' },
          { id: 'H1', color: 'bg-green-500', label: 'Low' },
        ].map(cls => (
          <div key={cls.id} className="flex items-center space-x-2 text-xs text-slate-300">
            <div className={`w-3 h-3 rounded-sm ${cls.color} border border-slate-700`}></div>
            <span className="font-mono">{cls.id}</span>
            <span className="text-slate-500">- {cls.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
