import * as React from 'react';
import { Activity, Compass, Cpu, Layers, ListTodo, Monitor } from 'lucide-react';
import { HybridOverviewTab } from './HybridOverviewTab';
import { CapabilityMatrixTab } from './CapabilityMatrixTab';
import { RoutingInspectorTab } from './RoutingInspectorTab';
import { UnifiedSessionsTab } from './UnifiedSessionsTab';
import { HybridTasksTab } from './HybridTasksTab';
import { HybridDiagnosticsTab } from './HybridDiagnosticsTab';

export const HybridWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState<string>('overview');

  const tabs = [
    { id: 'overview', label: 'Hybrid Overview', icon: Monitor },
    { id: 'matrix', label: 'Capability Matrix', icon: Layers },
    { id: 'routing', label: 'Routing Inspector', icon: Compass },
    { id: 'sessions', label: 'Unified Sessions', icon: Cpu },
    { id: 'tasks', label: 'Hybrid Tasks', icon: ListTodo },
    { id: 'diagnostics', label: 'Diagnostics & Audit', icon: Activity },
  ];

  return (
    <div className="space-y-6">
      {/* Sub-tab Navigation */}
      <div className="flex border-b border-slate-800 space-x-1">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 border-b-2 px-3.5 py-2 text-xs font-medium transition-colors ${
                isActive
                  ? 'border-blue-500 text-blue-400 bg-blue-500/5'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && <HybridOverviewTab />}
      {activeTab === 'matrix' && <CapabilityMatrixTab />}
      {activeTab === 'routing' && <RoutingInspectorTab />}
      {activeTab === 'sessions' && <UnifiedSessionsTab />}
      {activeTab === 'tasks' && <HybridTasksTab />}
      {activeTab === 'diagnostics' && <HybridDiagnosticsTab />}
    </div>
  );
};
