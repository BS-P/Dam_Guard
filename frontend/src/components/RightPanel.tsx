import React from 'react';
import { useStore } from '../hooks/useStore';
import clsx from 'clsx';
import { ResultsPanel } from './panels/ResultsPanel';
import { LayersPanel } from './panels/LayersPanel';
import { ProjectPanel } from './panels/ProjectPanel';
import { ScenariosPanel } from './panels/ScenariosPanel';
import { ValidationPanel } from './panels/ValidationPanel';
import { ExportsPanel } from './panels/ExportsPanel';

const tabs = [
  { id: 'project', label: 'Project' },
  { id: 'scenarios', label: 'Scenarios' },
  { id: 'results', label: 'Results' },
  { id: 'layers', label: 'Layers' },
  { id: 'validation', label: 'Validation' },
  { id: 'exports', label: 'Exports' },
];

export const RightPanel: React.FC = () => {
  const { rightPanelTab, setRightPanelTab } = useStore();

  const renderContent = () => {
    switch (rightPanelTab) {
      case 'project': return <ProjectPanel />;
      case 'scenarios': return <ScenariosPanel />;
      case 'results': return <ResultsPanel />;
      case 'layers': return <LayersPanel />;
      case 'validation': return <ValidationPanel />;
      case 'exports': return <ExportsPanel />;
      default: return <ResultsPanel />;
    }
  };

  return (
    <div className="w-[390px] bg-surface-900 border-l border-surface-800 flex flex-col z-10">
      {/* Tabs */}
      <div className="flex items-center overflow-x-auto no-scrollbar border-b border-surface-800 p-2 space-x-1 shrink-0 bg-surface-950/80">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setRightPanelTab(tab.id)}
            className={clsx(
              "px-3 py-1.5 text-xs font-semibold rounded-md transition-colors whitespace-nowrap",
              rightPanelTab === tab.id
                ? "bg-cyan-600 text-white shadow-md shadow-cyan-950/50"
                : "text-surface-400 hover:text-surface-200 hover:bg-surface-800/60"
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {renderContent()}
      </div>
    </div>
  );
};
