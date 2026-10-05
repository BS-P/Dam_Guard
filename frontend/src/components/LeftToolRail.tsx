import React from 'react';
import { 
  MousePointer2, Crosshair, Ruler, Square, GitBranch, 
  Activity, BarChart2, Users, Route,
  MapPin, Minus, Pentagon, Building, Shield, StickyNote,
  Maximize, Box, RefreshCw
} from 'lucide-react';
import { useStore } from '../hooks/useStore';
import clsx from 'clsx';

export const LeftToolRail: React.FC = () => {
  const { activeTool, setActiveTool } = useStore();

  const ToolGroup = ({ title, children }: { title: string, children: React.ReactNode }) => (
    <div className="flex flex-col items-center py-2 border-b border-surface-700/50 w-full">
      <span className="text-[9px] font-mono tracking-wider text-surface-500 mb-2">{title}</span>
      {children}
    </div>
  );

  const ToolBtn = ({ id, icon: Icon, title }: { id: string, icon: any, title: string }) => (
    <button
      onClick={() => setActiveTool(activeTool === id ? null : id)}
      className={clsx(
        "p-2.5 mb-1 rounded-lg transition-all duration-200 group relative",
        activeTool === id 
          ? "bg-primary/20 text-primary shadow-[inset_0_0_0_1px_rgba(6,182,212,0.5)]" 
          : "text-surface-400 hover:bg-surface-800 hover:text-surface-100"
      )}
      title={title}
    >
      <Icon className="w-4 h-4" strokeWidth={activeTool === id ? 2.5 : 2} />
    </button>
  );

  return (
    <div className="w-14 glass-panel flex flex-col items-center py-2 z-10 overflow-y-auto">
      <ToolGroup title="INSPECT">
        <ToolBtn id="inspect" icon={MousePointer2} title="Inspect Feature" />
        <ToolBtn id="crosshair" icon={Crosshair} title="Point Query" />
      </ToolGroup>

      <ToolGroup title="MEASURE">
        <ToolBtn id="measure_distance" icon={Ruler} title="Measure Distance" />
        <ToolBtn id="measure_area" icon={Square} title="Measure Area" />
        <ToolBtn id="cross_section" icon={GitBranch} title="Cross Section Profile" />
      </ToolGroup>

      <ToolGroup title="ANALYZE">
        <ToolBtn id="timeseries" icon={Activity} title="Time Series Extraction" />
        <ToolBtn id="statistics" icon={BarChart2} title="Zonal Statistics" />
        <ToolBtn id="population" icon={Users} title="Population at Risk" />
        <ToolBtn id="evacuation" icon={Route} title="Evacuation Routing" />
      </ToolGroup>

      <ToolGroup title="ANNOTATE">
        <ToolBtn id="annotate_marker" icon={MapPin} title="Add Marker" />
        <ToolBtn id="annotate_line" icon={Minus} title="Draw Line" />
        <ToolBtn id="annotate_polygon" icon={Pentagon} title="Draw Polygon" />
        <ToolBtn id="annotate_infrastructure" icon={Building} title="Mark Infrastructure" />
        <ToolBtn id="annotate_safezone" icon={Shield} title="Mark Safe Zone" />
        <ToolBtn id="annotate_note" icon={StickyNote} title="Add Text Note" />
      </ToolGroup>

      <ToolGroup title="VIEW">
        <ToolBtn id="view_fit" icon={Maximize} title="Fit to Data" />
        <ToolBtn id="view_3d" icon={Box} title="Toggle 3D View" />
        <ToolBtn id="view_sync" icon={RefreshCw} title="Sync Views" />
      </ToolGroup>
    </div>
  );
};
