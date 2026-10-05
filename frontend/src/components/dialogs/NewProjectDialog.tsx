export const NewProjectDialog = () => {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-700 shadow-2xl shadow-cyan-900/20 rounded-lg overflow-hidden flex flex-col">
        <div className="p-4 border-b border-slate-700 bg-slate-800/50 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-slate-200">Create New Project</h2>
          <button className="text-slate-400 hover:text-white">&times;</button>
        </div>
        
        <div className="p-6 space-y-5 flex-1 overflow-y-auto text-slate-300">
          <div className="space-y-1">
            <label className="text-sm font-medium text-cyan-400">Project Name</label>
            <input type="text" className="w-full bg-slate-800 border border-slate-600 rounded p-2 text-white focus:border-cyan-500 focus:outline-none" placeholder="e.g., Bhakra Dam Simulation" />
          </div>
          
          <div className="space-y-1">
            <label className="text-sm font-medium text-cyan-400">Description</label>
            <textarea className="w-full bg-slate-800 border border-slate-600 rounded p-2 text-white focus:border-cyan-500 focus:outline-none h-20" placeholder="Project details..."></textarea>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-sm font-medium text-cyan-400">Coordinate Reference System</label>
              <select className="w-full bg-slate-800 border border-slate-600 rounded p-2 text-white focus:border-cyan-500 focus:outline-none">
                <option>EPSG:4326 (WGS 84)</option>
                <option>EPSG:3857 (Web Mercator)</option>
              </select>
            </div>
            
            <div className="space-y-1">
              <label className="text-sm font-medium text-cyan-400">DEM Source</label>
              <select className="w-full bg-slate-800 border border-slate-600 rounded p-2 text-white focus:border-cyan-500 focus:outline-none">
                <option>Copernicus GLO-30</option>
                <option>SRTM 30m</option>
                <option>Upload Custom DEM</option>
              </select>
            </div>
          </div>
          
          <div className="p-4 border border-slate-700 bg-slate-800/30 rounded-md">
            <h3 className="text-sm font-medium text-orange-400 mb-3">Area of Interest (AOI)</h3>
            <p className="text-xs text-slate-400 mb-3">Draw on map or enter bounding box coordinates.</p>
            <div className="flex gap-2">
              <input type="text" placeholder="Min Lon" className="w-full bg-slate-800 border border-slate-600 rounded p-1.5 text-sm" />
              <input type="text" placeholder="Min Lat" className="w-full bg-slate-800 border border-slate-600 rounded p-1.5 text-sm" />
              <input type="text" placeholder="Max Lon" className="w-full bg-slate-800 border border-slate-600 rounded p-1.5 text-sm" />
              <input type="text" placeholder="Max Lat" className="w-full bg-slate-800 border border-slate-600 rounded p-1.5 text-sm" />
            </div>
          </div>
        </div>
        
        <div className="p-4 border-t border-slate-700 bg-slate-800/50 flex justify-end space-x-3">
          <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded text-sm transition-colors">Cancel</button>
          <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-sm transition-colors font-medium">Create Project</button>
        </div>
      </div>
    </div>
  );
};
