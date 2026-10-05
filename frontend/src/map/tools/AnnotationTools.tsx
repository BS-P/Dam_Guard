import { useState } from 'react';

export const AnnotationTools = () => {
  const [activeDraw, setActiveDraw] = useState<'none' | 'marker' | 'line' | 'polygon'>('none');

  return (
    <div className="absolute left-4 top-64 bg-slate-900/90 p-1.5 rounded-md border border-slate-700 z-20 flex flex-col space-y-1 shadow-xl">
      <div className="text-[10px] font-bold text-blue-400 text-center mb-1 uppercase tracking-wider">Draw</div>
      {[
        { id: 'marker', icon: '📌' },
        { id: 'line', icon: '〰' },
        { id: 'polygon', icon: '⬡' },
      ].map(t => (
        <button
          key={t.id}
          onClick={() => setActiveDraw(activeDraw === t.id ? 'none' : t.id as any)}
          className={`p-2 rounded text-xl transition-all ${
            activeDraw === t.id 
              ? 'bg-blue-500/20 text-blue-400 border border-blue-500/50' 
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-transparent'
          }`}
          title={`Draw ${t.id}`}
        >
          {t.icon}
        </button>
      ))}
    </div>
  );
};
