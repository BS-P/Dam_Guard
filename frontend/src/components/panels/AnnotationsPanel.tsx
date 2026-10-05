import { useState } from 'react';

export const AnnotationsPanel = () => {
  const [annotations, setAnnotations] = useState([
    { id: 1, name: 'Critical Infrastructure', type: 'polygon', visible: true, notes: 'Hospital and power substation' },
    { id: 2, name: 'Evacuation Route A', type: 'line', visible: true, notes: 'Primary route out of hazard zone' },
    { id: 3, name: 'Warning Siren 4', type: 'marker', visible: false, notes: 'Needs maintenance check' },
  ]);

  return (
    <div className="flex flex-col h-full bg-slate-900/90 backdrop-blur-md border-r border-slate-700 w-80 text-slate-200 p-4">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-semibold text-blue-400 tracking-wide">Annotations</h2>
        <button className="bg-blue-600 hover:bg-blue-500 text-white text-xs px-2 py-1 rounded transition-colors">
          + Add
        </button>
      </div>

      <div className="mb-4">
        <select className="w-full bg-slate-800 border border-slate-600 rounded p-1.5 text-sm text-white focus:outline-none">
          <option value="all">All Types</option>
          <option value="marker">Markers</option>
          <option value="line">Lines</option>
          <option value="polygon">Polygons</option>
        </select>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2">
        {annotations.map(ann => (
          <div key={ann.id} className="p-3 bg-slate-800 rounded border border-slate-700 group flex flex-col">
            <div className="flex justify-between items-start">
              <div className="flex items-center space-x-2 cursor-pointer hover:text-blue-300 transition-colors flex-1">
                <span className="w-3 h-3 rounded-sm bg-blue-500/50 border border-blue-500 flex-shrink-0"></span>
                <span className="text-sm font-medium truncate">{ann.name}</span>
              </div>
              <div className="flex items-center space-x-2">
                <button 
                  onClick={() => setAnnotations(anns => anns.map(a => a.id === ann.id ? { ...a, visible: !a.visible } : a))}
                  className={`text-xs ${ann.visible ? 'text-green-400' : 'text-slate-500'}`}
                >
                  {ann.visible ? '👁' : '👁‍🗨'}
                </button>
                <button className="text-slate-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity">
                  &times;
                </button>
              </div>
            </div>
            <div className="mt-2 text-xs text-slate-400 italic">
              {ann.notes}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
