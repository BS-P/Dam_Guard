export const LayerLegend = () => {
  return (
    <div className="absolute bottom-24 right-4 bg-slate-900/90 backdrop-blur-sm p-4 rounded-md border border-slate-700 shadow-xl z-20">
      <h4 className="text-xs font-bold text-slate-300 uppercase tracking-widest mb-3">Map Legend</h4>
      
      <div className="space-y-4">
        <div>
          <div className="text-[10px] text-slate-400 mb-1">Max Depth (m)</div>
          <div className="flex w-48 h-2 rounded overflow-hidden">
            <div className="flex-1 bg-[#ADD8E6]"></div>
            <div className="flex-1 bg-[#0000FF]"></div>
            <div className="flex-1 bg-[#FFFF00]"></div>
            <div className="flex-1 bg-[#FFA500]"></div>
            <div className="flex-1 bg-[#FF0000]"></div>
          </div>
          <div className="flex justify-between text-[9px] text-slate-500 mt-1 font-mono">
            <span>0</span>
            <span>0.5</span>
            <span>1.0</span>
            <span>2.0</span>
            <span>3.0+</span>
          </div>
        </div>

        <div>
          <div className="text-[10px] text-slate-400 mb-1 flex items-center justify-between">
            <span>Scale</span>
            <span>1 : 25,000</span>
          </div>
          <div className="border-b-2 border-l-2 border-r-2 border-slate-500 h-2 w-32 relative mt-2">
            <div className="absolute -top-4 text-[9px] text-slate-400 left-0">0</div>
            <div className="absolute -top-4 text-[9px] text-slate-400 right-0">1 km</div>
          </div>
        </div>
      </div>
    </div>
  );
};
