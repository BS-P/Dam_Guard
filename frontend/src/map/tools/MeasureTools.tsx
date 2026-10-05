import { useState } from 'react';

export const MeasureTools = () => {
  const [activeTool, setActiveTool] = useState<'none' | 'distance' | 'area' | 'profile' | 'probe'>('none');

  const tools = [
    { id: 'distance', label: 'Distance', icon: '📏' },
    { id: 'area', label: 'Area', icon: '⬟' },
    { id: 'profile', label: 'Cross-Section', icon: '📈' },
    { id: 'probe', label: 'Point Probe', icon: '📍' },
  ];

  return (
    <div className="absolute left-4 top-20 bg-slate-900/90 p-1.5 rounded-md border border-slate-700 z-20 flex flex-col space-y-1 shadow-xl">
      {tools.map(t => (
        <button
          key={t.id}
          onClick={() => setActiveTool(activeTool === t.id ? 'none' : t.id as any)}
          className={`p-2 rounded text-xl transition-all ${
            activeTool === t.id 
              ? 'bg-orange-500/20 text-orange-400 border border-orange-500/50' 
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-transparent'
          }`}
          title={`Measure ${t.label}`}
        >
          {t.icon}
        </button>
      ))}
      {activeTool !== 'none' && (
        <div className="mt-2 text-[10px] text-orange-400 text-center w-full bg-slate-800 p-1 rounded break-words">
          Click map<br/>to measure
        </div>
      )}
    </div>
  );
};
