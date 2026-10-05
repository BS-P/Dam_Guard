export const FloodLayer = () => {
  
  return (
    <div className="absolute top-4 right-4 bg-slate-900/80 p-3 rounded border border-slate-700 z-10 w-48 shadow-lg">
      <h3 className="text-xs text-cyan-400 font-bold mb-2 uppercase">Flood Depth Layer</h3>
      <div className="space-y-3">
        <div>
          <label className="text-[10px] text-slate-400 block mb-1">Opacity</label>
          <input type="range" min="0" max="100" defaultValue="80" className="w-full accent-cyan-500" />
        </div>
        <div className="h-2 w-full rounded bg-gradient-to-r from-transparent via-blue-500 to-red-500"></div>
        <div className="flex justify-between text-[10px] text-slate-400 font-mono">
          <span>0m</span>
          <span>&gt;3m</span>
        </div>
      </div>
    </div>
  );
};
