import * as React from 'react';
import {
  Activity,
  Camera,
  Eye,
  LayoutGrid,
  ListTodo,
  MousePointer,
} from 'lucide-react';
import { ModuleTabs } from '@/components/module';
import { VisualOverviewTab } from './VisualOverviewTab';
import { VisualCaptureTab } from './VisualCaptureTab';
import { VisualGroundingTab } from './VisualGroundingTab';
import { VisualActionsTab } from './VisualActionsTab';
import { VisualTasksTab } from './VisualTasksTab';
import { VisualDiagnosticsTab } from './VisualDiagnosticsTab';

export const VisualWorkspace: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = React.useState<string>('overview');

  const subTabs = [
    { id: 'overview', label: 'Overview & Console', icon: LayoutGrid },
    { id: 'capture', label: 'Screen Perception & Capture', icon: Camera },
    { id: 'grounding', label: 'Visual Grounding & OCR', icon: Eye },
    { id: 'actions', label: 'Actions & Verification', icon: MousePointer },
    { id: 'tasks', label: 'Visual Tasks', icon: ListTodo },
    { id: 'diagnostics', label: 'Diagnostics & Recovery', icon: Activity },
  ];

  return (
    <div className="space-y-6">
      <ModuleTabs
        tabs={subTabs}
        activeTab={activeSubTab}
        onTabChange={setActiveSubTab}
      />

      <div className="mt-4">
        {activeSubTab === 'overview' && (
          <VisualOverviewTab onNavigateTab={setActiveSubTab} />
        )}
        {activeSubTab === 'capture' && <VisualCaptureTab />}
        {activeSubTab === 'grounding' && <VisualGroundingTab />}
        {activeSubTab === 'actions' && <VisualActionsTab />}
        {activeSubTab === 'tasks' && <VisualTasksTab />}
        {activeSubTab === 'diagnostics' && <VisualDiagnosticsTab />}
      </div>
    </div>
  );
};
