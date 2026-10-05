import { useState } from 'react';

export const ExportsPanel = () => {
  const [exporting, setExporting] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState('png');
  const [selectedMapType, setSelectedMapType] = useState('extent');
  const [previewUrl, setPreviewUrl] = useState<string | null>('/api/maps/demo?type=extent');

  const handleGeneratePublicationMap = (mapType: string, format: string) => {
    setExporting(true);
    const downloadUrl = `http://localhost:8000/api/maps/demo/download?type=${mapType}&format=${format}`;
    
    setTimeout(() => {
      setExporting(false);
      window.open(downloadUrl, '_blank');
    }, 800);
  };

  return (
    <div className="flex flex-col h-full bg-slate-900/95 backdrop-blur-md border-r border-slate-700 w-96 text-slate-200 p-4 overflow-y-auto">
      <h2 className="text-lg font-semibold text-cyan-400 tracking-wide mb-4">Publication Map Outputs</h2>
      
      {/* Map Figure Generator Box */}
      <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 mb-6 space-y-4 shadow-lg">
        <div className="space-y-1">
          <label className="text-xs text-cyan-400 uppercase tracking-wider font-semibold">Figure Type</label>
          <select 
            value={selectedMapType}
            onChange={(e) => {
              setSelectedMapType(e.target.value);
              setPreviewUrl(`http://localhost:8000/api/maps/demo?type=${e.target.value}`);
            }}
            className="w-full bg-slate-900 border border-slate-600 rounded p-2 text-sm text-white focus:border-cyan-500 font-medium"
          >
            <option value="extent">Figure Type A – Scenario Extent Comparison (Konta Style)</option>
            <option value="three_panel">Figure Type B – 3-Panel Hydrodynamic Map (Depth/Vel/Sev)</option>
          </select>
        </div>

        <div className="space-y-1">
          <label className="text-xs text-slate-400 uppercase tracking-wider font-medium">Export Format</label>
          <select 
            value={selectedFormat}
            onChange={(e) => setSelectedFormat(e.target.value)}
            className="w-full bg-slate-900 border border-slate-600 rounded p-2 text-sm text-white focus:border-cyan-500"
          >
            <option value="png">High-Res PNG (300 DPI)</option>
            <option value="pdf">Vector PDF Report</option>
            <option value="svg">Editable Scalable Vector Graphics (SVG)</option>
            <option value="shp">GIS Shapefile (.shp zip)</option>
            <option value="kml">Google Earth KML Vector (.kml)</option>
          </select>
        </div>

        <button 
          onClick={() => handleGeneratePublicationMap(selectedMapType, selectedFormat)}
          disabled={exporting}
          className="w-full py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:bg-slate-700 disabled:text-slate-400 text-white rounded-md text-sm font-semibold shadow transition-all flex justify-center items-center gap-2"
        >
          {exporting ? (
            <>
              <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></span>
              Generating Publication Figure...
            </>
          ) : (
            'Generate & Download Map Output'
          )}
        </button>
      </div>

      {/* Map Output Preview Section */}
      <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 mb-6 space-y-3">
        <h3 className="text-xs text-cyan-400 uppercase tracking-wider font-semibold">Live Figure Preview</h3>
        <div className="w-full h-48 bg-slate-950 rounded border border-slate-700 flex items-center justify-center overflow-hidden relative group">
          {previewUrl ? (
            <img 
              src={previewUrl} 
              alt="Publication Map Preview" 
              className="w-full h-full object-contain"
              onError={() => setPreviewUrl(null)}
            />
          ) : (
            <div className="text-xs text-slate-500 text-center px-4">
              Konta 2005 Inundation Map Preview (Click Generate to View)
            </div>
          )}
        </div>
      </div>

      {/* Specification Reference Checklist */}
      <div className="bg-slate-800/80 p-3.5 rounded border border-slate-700/80 text-xs space-y-2 text-slate-300">
        <div className="font-semibold text-slate-200">Publication Compliance Checklist:</div>
        <div className="flex items-center gap-2 text-emerald-400">
          <span>✓</span> DMS Lat/Long Graticules (All 4 Edges)
        </div>
        <div className="flex items-center gap-2 text-emerald-400">
          <span>✓</span> North Arrow & Graduated Scale Bar (km)
        </div>
        <div className="flex items-center gap-2 text-emerald-400">
          <span>✓</span> Outlines-Only Polygons (S1, S2, M1, M2, F1, F2)
        </div>
        <div className="flex items-center gap-2 text-emerald-400">
          <span>✓</span> Red Dot GD Station Marker + Title Box
        </div>
        <div className="flex items-center gap-2 text-emerald-400">
          <span>✓</span> 3-Panel Depth, Velocity & Severity Palettes
        </div>
      </div>
    </div>
  );
};
