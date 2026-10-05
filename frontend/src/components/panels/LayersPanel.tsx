import React from 'react';
import { useStore } from '../../hooks/useStore';
import { Layers, Eye, EyeOff, SlidersHorizontal } from 'lucide-react';
import clsx from 'clsx';

export const LayersPanel: React.FC = () => {
  const { resultLayers, toggleLayerVisibility, setLayerOpacity } = useStore();

  if (resultLayers.length === 0) {
    return (
      <div className="p-6 flex flex-col items-center justify-center h-full text-surface-500 space-y-4">
        <Layers className="w-12 h-12 opacity-50" />
        <p className="text-center text-sm">No layers available. Run a simulation to generate map layers.</p>
      </div>
    );
  }

  return (
    <div className="p-2 space-y-2">
      {resultLayers.map(layer => (
        <div key={layer.id} className="bg-surface-800/50 rounded-lg p-3 border border-surface-700/50">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <button 
                onClick={() => toggleLayerVisibility(layer.id)}
                className="text-surface-400 hover:text-white transition-colors"
              >
                {layer.visible ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4 opacity-50" />}
              </button>
              <span className={clsx("text-sm font-medium", !layer.visible && "text-surface-500")}>
                {layer.name}
              </span>
            </div>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-surface-700 text-surface-300 uppercase tracking-wider font-mono">
              {layer.type}
            </span>
          </div>
          
          {layer.visible && (
            <div className="flex items-center space-x-3 mt-3 pl-6">
              <SlidersHorizontal className="w-3 h-3 text-surface-500" />
              <input 
                type="range" 
                min="0" 
                max="100" 
                value={layer.opacity * 100} 
                onChange={(e) => setLayerOpacity(layer.id, parseInt(e.target.value) / 100)}
                className="w-full accent-primary h-1 bg-surface-700 rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-xs font-mono text-surface-400 w-8 text-right">
                {Math.round(layer.opacity * 100)}%
              </span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
