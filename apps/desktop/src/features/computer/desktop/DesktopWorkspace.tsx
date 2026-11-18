import * as React from 'react';
import {
  Monitor,
  Cpu,
  Layers,
  Sparkles,
  Activity,
  CheckSquare,
  Wrench,
} from 'lucide-react';
import { DesktopOverviewTab } from './DesktopOverviewTab';
import { DesktopApplicationsTab } from './DesktopApplicationsTab';
import { DesktopWindowsTab } from './DesktopWindowsTab';
import { DesktopUITreeTab } from './DesktopUITreeTab';
import { DesktopActionsTab } from './DesktopActionsTab';
import { DesktopTasksTab } from './DesktopTasksTab';
import { DesktopDiagnosticsTab } from './DesktopDiagnosticsTab';

export const DesktopWorkspace: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = React.useState<string>('overview');
  const [inspectTargetRef, setInspectTargetRef] = React.useState<string | undefined>(undefined);

  const subTabs = [
    { id: 'overview', label: 'Overview', icon: Monitor },
    { id: 'apps', label: 'Applications', icon: Cpu },
    { id: 'windows', label: 'Windows', icon: Layers },
    { id: 'tree', label: 'UI Tree Inspector', icon: Sparkles },
    { id: 'actions', label: 'Action History', icon: Activity },
    { id: 'tasks', label: 'Tasks', icon: CheckSquare },
    { id: 'diagnostics', label: 'Diagnostics', icon: Wrench },
  ];

  const handleSelectWindowForTree = (windowRef: string) => {
    setInspectTargetRef(windowRef);
    setActiveSubTab('tree');
  };

  return (
    <div className="space-y-6">
      {/* Sub-tab Navigation */}
      <div className="flex border-b border-border/60 gap-1 overflow-x-auto">
        {subTabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeSubTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id)}
              className={`flex items-center gap-2 px-3.5 py-2 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
                isActive
                  ? 'border-cyan-500 text-cyan-400 bg-cyan-500/10'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:bg-muted/30'
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Panels */}
      {activeSubTab === 'overview' && <DesktopOverviewTab />}
      {activeSubTab === 'apps' && <DesktopApplicationsTab />}
      {activeSubTab === 'windows' && <DesktopWindowsTab onSelectWindowForTree={handleSelectWindowForTree} />}
      {activeSubTab === 'tree' && <DesktopUITreeTab initialWindowRef={inspectTargetRef} />}
      {activeSubTab === 'actions' && <DesktopActionsTab />}
      {activeSubTab === 'tasks' && <DesktopTasksTab />}
      {activeSubTab === 'diagnostics' && <DesktopDiagnosticsTab />}
    </div>
  );
};
