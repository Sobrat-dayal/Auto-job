import * as React from 'react';
import {
  Circle,
  BookOpen,
  Sliders,
  Play,
  Database,
  RotateCcw,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { RecordingStudioTab } from './RecordingStudioTab';
import { ProcedureLibraryTab } from './ProcedureLibraryTab';
import { ProcedureEditorTab } from './ProcedureEditorTab';
import { ReplayInspectorTab } from './ReplayInspectorTab';
import { CheckpointTimelineTab } from './CheckpointTimelineTab';
import { RecoveryCenterTab } from './RecoveryCenterTab';
import { apiClient } from '@/lib/api-client';
import type { ReusableProcedure, ReliabilityDiagnosticsInfo } from '@autonom/shared-types';

export const WorkflowReliabilityWorkspace: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = React.useState<string>('studio');
  const [selectedProcedure, setSelectedProcedure] = React.useState<ReusableProcedure | null>(null);
  const [replayTarget, setReplayTarget] = React.useState<{ id: string; version: number } | null>(null);
  const [diagnostics, setDiagnostics] = React.useState<ReliabilityDiagnosticsInfo | null>(null);

  const loadDiagnostics = React.useCallback(async () => {
    try {
      const diag = await apiClient.getReliabilityDiagnostics();
      setDiagnostics(diag);
    } catch (err: any) {
      console.error('Failed to load reliability diagnostics:', err);
    }
  }, []);

  React.useEffect(() => {
    loadDiagnostics();
    const interval = setInterval(loadDiagnostics, 5000);
    return () => clearInterval(interval);
  }, [loadDiagnostics]);

  const handleCompileProcedureFromSession = async (sessionId: string) => {
    try {
      const proc = await apiClient.compileProcedure({
        session_id: sessionId,
        name: `Procedure from Session ${sessionId.slice(0, 8)}`,
        parameterize_inputs: true,
      });
      setSelectedProcedure(proc);
      setActiveSubTab('editor');
    } catch (err: any) {
      console.error('Failed to compile procedure:', err);
    }
  };

  const handleSelectProcedure = (proc: ReusableProcedure) => {
    setSelectedProcedure(proc);
    setActiveSubTab('editor');
  };

  const handleRunProcedure = (procedureId: string, version: number) => {
    setReplayTarget({ id: procedureId, version });
    setActiveSubTab('replay');
  };

  const subTabs = [
    { id: 'studio', label: 'Action Recording', icon: Circle },
    { id: 'library', label: 'Procedure Library', icon: BookOpen },
    { id: 'editor', label: 'Procedure Editor', icon: Sliders },
    { id: 'replay', label: 'State-Aware Replay', icon: Play },
    { id: 'checkpoints', label: 'Checkpoints & State', icon: Database },
    { id: 'recovery', label: 'Crash Recovery', icon: RotateCcw },
  ];

  return (
    <div className="space-y-6" data-testid="workflow-reliability-workspace">
      {/* Top Diagnostics KPI Summary Bar */}
      {diagnostics && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <Card className="border-border/60 bg-card/60">
            <CardContent className="p-3">
              <span className="text-[11px] text-slate-400">Recording Sessions</span>
              <div className="text-base font-bold font-mono text-slate-100 mt-0.5">
                {diagnostics.active_recording_sessions} active
              </div>
            </CardContent>
          </Card>
          <Card className="border-border/60 bg-card/60">
            <CardContent className="p-3">
              <span className="text-[11px] text-slate-400">Procedures</span>
              <div className="text-base font-bold font-mono text-blue-400 mt-0.5">
                {diagnostics.total_registered_procedures} registered
              </div>
            </CardContent>
          </Card>
          <Card className="border-border/60 bg-card/60">
            <CardContent className="p-3">
              <span className="text-[11px] text-slate-400">Active Replays</span>
              <div className="text-base font-bold font-mono text-emerald-400 mt-0.5">
                {diagnostics.active_executions}
              </div>
            </CardContent>
          </Card>
          <Card className="border-border/60 bg-card/60">
            <CardContent className="p-3">
              <span className="text-[11px] text-slate-400">Durable Checkpoints</span>
              <div className="text-base font-bold font-mono text-cyan-400 mt-0.5">
                {diagnostics.total_checkpoints_preserved}
              </div>
            </CardContent>
          </Card>
          <Card className="border-border/60 bg-card/60">
            <CardContent className="p-3">
              <span className="text-[11px] text-slate-400">Side Effects Tracked</span>
              <div className="text-base font-bold font-mono text-purple-400 mt-0.5">
                {diagnostics.tracked_side_effects_count}
              </div>
            </CardContent>
          </Card>
          <Card className="border-border/60 bg-card/60">
            <CardContent className="p-3">
              <span className="text-[11px] text-slate-400">Killswitch State</span>
              <div className="text-base font-bold font-mono text-emerald-400 mt-0.5">
                {diagnostics.emergency_stop_triggered ? 'TRIGGERED' : 'ARMED / IDLE'}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Sub-tab Navigation */}
      <div className="flex border-b border-slate-800 space-x-1 overflow-x-auto">
        {subTabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeSubTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id)}
              className={`flex items-center gap-2 border-b-2 px-3.5 py-2 text-xs font-medium transition-colors whitespace-nowrap ${
                isActive
                  ? 'border-blue-500 text-blue-400 bg-blue-500/5'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
              }`}
              data-testid={`reliability-subtab-${tab.id}`}
            >
              <Icon className="h-3.5 w-3.5" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Active Sub-tab View */}
      {activeSubTab === 'studio' && (
        <RecordingStudioTab onCompileProcedure={handleCompileProcedureFromSession} />
      )}
      {activeSubTab === 'library' && (
        <ProcedureLibraryTab
          onSelectProcedure={handleSelectProcedure}
          onRunProcedure={handleRunProcedure}
        />
      )}
      {activeSubTab === 'editor' && (
        <ProcedureEditorTab
          procedure={selectedProcedure}
          onProcedureUpdated={setSelectedProcedure}
        />
      )}
      {activeSubTab === 'replay' && (
        <ReplayInspectorTab
          procedureId={replayTarget?.id}
          version={replayTarget?.version}
        />
      )}
      {activeSubTab === 'checkpoints' && <CheckpointTimelineTab />}
      {activeSubTab === 'recovery' && <RecoveryCenterTab />}
    </div>
  );
};
