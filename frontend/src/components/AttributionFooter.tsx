export const AttributionFooter = () => {
  return (
    <div className="absolute bottom-0 right-0 z-50 px-3 py-1 bg-black/60 backdrop-blur-sm border-t border-l border-slate-800 text-[10px] text-slate-400 flex items-center space-x-3 pointer-events-none rounded-tl-md">
      <span>&copy; {new Date().getFullYear()} BREACHSCOPE</span>
      <span>Data: Copernicus, OSM, WorldPop, JRC, Sentinel</span>
      <span className="text-cyan-500/80">Powered by 2D-VPMM</span>
    </div>
  );
};
