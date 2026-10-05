import { useStore } from '../hooks/useStore';
import { Navigation, Clock } from 'lucide-react';

export const BottomStatusBar: React.FC = () => {
  const { mouseCoords, mouseElevation, activeRun } = useStore();

  return (
    <div className="h-7 bg-surface-950 border-t border-surface-800 flex items-center justify-between px-3 text-[10px] font-mono text-surface-400 z-50">
      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-2">
          <Navigation className="w-3 h-3" />
          <span>
            {mouseCoords 
              ? `Lat: ${mouseCoords[1].toFixed(5)}° Lon: ${mouseCoords[0].toFixed(5)}°` 
              : 'Lat: --.-----° Lon: --.-----°'}
          </span>
        </div>
        
        <div>
          Elev: {mouseElevation !== null ? `${mouseElevation.toFixed(2)}m` : '--.--m'}
        </div>

        <div>
          CRS: EPSG:4326
        </div>
      </div>

      <div className="flex items-center space-x-6">
        {activeRun && activeRun.status === 'running' && (
          <div className="flex items-center space-x-2 text-measurement">
            <Clock className="w-3 h-3 animate-spin" />
            <span>Simulating T: +{activeRun.progress}%</span>
          </div>
        )}
        
        <div className="flex items-center space-x-1">
          <span className="w-2 h-2 rounded-full bg-success"></span>
          <span>API Connected</span>
        </div>
      </div>
    </div>
  );
};
