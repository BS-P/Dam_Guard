import { useState } from 'react';

export const CompareView = () => {
  const [mode, setMode] = useState<'off' | 'split' | 'swipe'>('off');

  if (mode === 'off') {
    return (
      <button 
        onClick={() => setMode('split')}
        className="absolute top-4 left-1/2 -translate-x-1/2 bg-slate-900/90 text-slate-300 px-4 py-1.5 rounded-full border border-slate-700 text-xs font-medium hover:bg-slate-800 transition-colors shadow-lg z-20"
      >
        Compare Mode
      </button>
    );
  }

  return (
    <>
      <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-slate-900/90 rounded-full border border-slate-700 p-1 flex items-center shadow-lg z-20">
        <button 
          onClick={() => setMode('split')}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${mode === 'split' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
        >
          Side-by-Side
        </button>
        <button 
          onClick={() => setMode('swipe')}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${mode === 'swipe' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
        >
          Swipe
        </button>
        <div className="w-px h-4 bg-slate-600 mx-2"></div>
        <button 
          onClick={() => setMode('off')}
          className="px-2 py-1 text-slate-400 hover:text-red-400 transition-colors"
        >
          &times;
        </button>
      </div>

      {mode === 'swipe' && (
        <div className="absolute inset-0 pointer-events-none z-10 flex items-center justify-center">
          <div className="w-1 h-full bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.8)] relative pointer-events-auto cursor-ew-resize">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-12 bg-cyan-600 rounded-sm flex items-center justify-center border border-cyan-400">
              <div className="flex space-x-1">
                <div className="w-0.5 h-6 bg-white/50"></div>
                <div className="w-0.5 h-6 bg-white/50"></div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {mode === 'split' && (
        <div className="absolute top-0 bottom-0 left-1/2 w-1 bg-slate-800 z-10"></div>
      )}
    </>
  );
};
