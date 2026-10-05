import { useEffect } from 'react'
import { TopBar } from './components/TopBar'
import { LeftToolRail } from './components/LeftToolRail'
import { RightPanel } from './components/RightPanel'
import { BottomStatusBar } from './components/BottomStatusBar'
import { MapView } from './map/MapView'
import { useStore } from './hooks/useStore'

function App() {
  const { fetchSystemHealth, fetchProjects, fetchSolverStatuses, themeMode } = useStore();

  useEffect(() => {
    fetchSystemHealth();
    fetchProjects();
    fetchSolverStatuses();
    
    const interval = setInterval(() => {
      fetchSystemHealth();
      fetchSolverStatuses();
    }, 10000);
    
    return () => clearInterval(interval);
  }, [fetchSystemHealth, fetchProjects, fetchSolverStatuses]);

  useEffect(() => {
    if (themeMode === 'light') {
      document.body.classList.add('light');
      document.body.classList.remove('dark');
    } else {
      document.body.classList.add('dark');
      document.body.classList.remove('light');
    }
  }, [themeMode]);

  return (
    <div className={`flex flex-col h-screen w-screen overflow-hidden font-sans transition-colors duration-200 ${themeMode === 'light' ? 'light bg-slate-100 text-slate-900' : 'dark bg-surface-950 text-surface-200'}`}>
      <TopBar />
      
      <div className="flex flex-1 overflow-hidden relative">
        <LeftToolRail />
        
        <div className="flex-1 relative z-0">
          <MapView />
        </div>
        
        <RightPanel />
      </div>
      
      <BottomStatusBar />
    </div>
  )
}

export default App
