import { Activity, Database, Cloud, ChevronRight, Check, Sun, Moon } from 'lucide-react';
import { useStore } from '../hooks/useStore';
import clsx from 'clsx';

export const TopBar: React.FC = () => {
  const {
    activeProject,
    currentStep,
    setCurrentStep,
    simulationExecuted,
    themeMode,
    toggleThemeMode
  } = useStore();

  return (
    <div className="h-12 bg-surface-950 border-b border-surface-800 flex items-center justify-between px-4 z-50 text-surface-200">
      {/* Brand & Project Title */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-cyan-400" />
          <span className="font-bold tracking-widest text-white text-sm">BREACHSCOPE</span>
        </div>
        
        <div className="h-4 w-px bg-surface-800"></div>
        
        <div className="text-xs font-semibold">
          {activeProject ? (
            <span className="text-cyan-300 bg-cyan-950/60 px-2 py-1 rounded border border-cyan-800">
              {activeProject.name}
            </span>
          ) : (
            <span className="text-surface-500 italic">No Project Loaded</span>
          )}
        </div>
      </div>

      {/* Guided Step-by-Step Workflow Stepper */}
      <div className="flex items-center space-x-2 bg-surface-900 px-3 py-1 rounded-lg border border-surface-800 text-xs">
        {/* Step 1 */}
        <button
          onClick={() => setCurrentStep(1)}
          className={clsx(
            "flex items-center space-x-1.5 px-2.5 py-1 rounded transition-all font-semibold",
            currentStep === 1
              ? "bg-cyan-600 text-white shadow-md shadow-cyan-950/50"
              : activeProject
              ? "text-cyan-400 hover:bg-surface-800"
              : "text-surface-400 hover:text-white"
          )}
        >
          {activeProject ? <Check className="w-3.5 h-3.5 text-green-400" /> : <span className="w-4 h-4 rounded-full bg-surface-800 flex items-center justify-center text-[10px]">1</span>}
          <span>Step 1: Input Dataset</span>
        </button>

        <ChevronRight className="w-3.5 h-3.5 text-surface-600" />

        {/* Step 2 */}
        <button
          onClick={() => setCurrentStep(2)}
          className={clsx(
            "flex items-center space-x-1.5 px-2.5 py-1 rounded transition-all font-semibold",
            currentStep === 2
              ? "bg-cyan-600 text-white shadow-md shadow-cyan-950/50"
              : simulationExecuted
              ? "text-cyan-400 hover:bg-surface-800"
              : "text-surface-400 hover:text-white"
          )}
        >
          {simulationExecuted ? <Check className="w-3.5 h-3.5 text-green-400" /> : <span className="w-4 h-4 rounded-full bg-surface-800 flex items-center justify-center text-[10px]">2</span>}
          <span>Step 2: Solver & Scenario</span>
        </button>

        <ChevronRight className="w-3.5 h-3.5 text-surface-600" />

        {/* Step 3 */}
        <button
          onClick={() => setCurrentStep(3)}
          className={clsx(
            "flex items-center space-x-1.5 px-2.5 py-1 rounded transition-all font-semibold",
            currentStep === 3
              ? "bg-cyan-600 text-white shadow-md shadow-cyan-950/50"
              : simulationExecuted
              ? "text-cyan-400 hover:bg-surface-800"
              : "text-surface-400 hover:text-white opacity-60"
          )}
        >
          <span className="w-4 h-4 rounded-full bg-surface-800 flex items-center justify-center text-[10px]">3</span>
          <span>Step 3: Results & Inundation</span>
        </button>
      </div>

      {/* System Status & Theme Switcher */}
      <div className="flex items-center space-x-4">
        {/* Light / Dark Mode Toggle Button */}
        <button
          onClick={toggleThemeMode}
          className="flex items-center space-x-1.5 px-3 py-1 rounded-md bg-surface-900 hover:bg-surface-800 border border-surface-700 text-xs font-semibold text-surface-200 transition-all shadow-sm cursor-pointer"
          title="Switch Light / Dark Mode"
        >
          {themeMode === 'dark' ? (
            <>
              <Sun className="w-3.5 h-3.5 text-yellow-400" />
              <span className="text-yellow-300">Light Mode</span>
            </>
          ) : (
            <>
              <Moon className="w-3.5 h-3.5 text-cyan-500" />
              <span className="text-cyan-600 font-bold">Dark Mode</span>
            </>
          )}
        </button>

        <div className="h-4 w-px bg-surface-800"></div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          <div className="flex items-center space-x-1.5" title="Database: Ready">
            <Database className="w-3.5 h-3.5 text-cyan-400" />
            <div className="w-2 h-2 rounded-full bg-green-400" />
          </div>
          <div className="flex items-center space-x-1.5" title="GEE Sentinel Connection: Ready">
            <Cloud className="w-3.5 h-3.5 text-cyan-400" />
            <div className="w-2 h-2 rounded-full bg-green-400" />
          </div>
          <div className="flex items-center space-x-1.5" title="2D-VPMM Compute Engine: Ready">
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            <div className="w-2 h-2 rounded-full bg-green-400" />
          </div>
        </div>
      </div>
    </div>
  );
};
