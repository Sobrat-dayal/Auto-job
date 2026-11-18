import * as React from 'react';
import {
  Play,
  CheckCircle2,
  AlertCircle,
  Pause,
  ShieldCheck,
  Terminal,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type {
  ProcedureExecution,
  PreflightReport,
  ReplayMode,
} from '@autonom/shared-types';

interface ReplayInspectorTabProps {
  procedureId?: string;
  version?: number;
}

export const ReplayInspectorTab: React.FC<ReplayInspectorTabProps> = ({
  procedureId: initialProcId,
  version: initialVersion,
}) => {
  const [procedureId, setProcedureId] = React.useState<string>(initialProcId || '');
  const [version, setVersion] = React.useState<number>(initialVersion || 1);
  const [mode, setMode] = React.useState<ReplayMode>('automatic_authorized');
  const [argsJson, setArgsJson] = React.useState<string>('{}');
  const [currentExecution, setCurrentExecution] = React.useState<ProcedureExecution | null>(null);
  const [preflight, setPreflight] = React.useState<PreflightReport | null>(null);
  const [isRunning, setIsRunning] = React.useState<boolean>(false);
  const [statusMessage, setStatusMessage] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (initialProcId) setProcedureId(initialProcId);
    if (initialVersion) setVersion(initialVersion);
  }, [initialProcId, initialVersion]);

  const handleRunPreflight = async () => {
    if (!procedureId) return;
    setStatusMessage(null);
    try {
      let parsedArgs = {};
      try {
        parsedArgs = JSON.parse(argsJson);
      } catch {
        /* fallback empty */
      }
      const report = await apiClient.preflightProcedure(procedureId, parsedArgs, version);
      setPreflight(report);
      setStatusMessage(
        report.can_execute
          ? 'Preflight check passed: Adapters ready, permissions verified.'
          : `Preflight failed: ${report.issues.join(', ')}`
      );
    } catch (err: any) {
      setStatusMessage(`Preflight error: ${err.message}`);
    }
  };

  const handleExecute = async () => {
    if (!procedureId) return;
    setIsRunning(true);
    setStatusMessage(null);
    try {
      let parsedArgs = {};
      try {
        parsedArgs = JSON.parse(argsJson);
      } catch (e: any) {
        setStatusMessage(`JSON argument parsing error: ${e.message}`);
        setIsRunning(false);
        return;
      }
      const execution = await apiClient.executeProcedure(procedureId, parsedArgs, version, mode);
      setCurrentExecution(execution);
      setStatusMessage(
        execution.status === 'completed'
          ? `Execution ${execution.execution_id} completed successfully in ${execution.execution_time_ms}ms.`
          : `Execution status: ${execution.status} - ${execution.error_message || ''}`
      );
    } catch (err: any) {
      setStatusMessage(`Execution failed: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="replay-inspector-tab">
      {/* Execution Launch Configuration */}
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <Play className="h-4 w-4 text-emerald-400" />
                State-Aware Procedure Replay Engine
              </CardTitle>
              <CardDescription className="text-xs">
                Executes compiled procedures with live UI target re-resolution, precondition checks, and automatic checkpointing.
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="destructive"
                size="sm"
                onClick={() => apiClient.activateHybridKillswitch('Operator abort')}
                className="h-8 text-xs font-mono font-medium gap-1"
                data-testid="emergency-stop-btn"
              >
                <Pause className="h-3 w-3" />
                Emergency Stop (Pause/Break)
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-300">Procedure ID</label>
              <Input
                value={procedureId}
                onChange={(e) => setProcedureId(e.target.value)}
                placeholder="proc_..."
                className="h-8 text-xs bg-slate-900/60 font-mono"
                data-testid="replay-procedure-id-input"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-300">Version</label>
              <Input
                type="number"
                value={version}
                onChange={(e) => setVersion(parseInt(e.target.value) || 1)}
                className="h-8 text-xs bg-slate-900/60 font-mono"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-300">Replay Mode</label>
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value as ReplayMode)}
                className="w-full h-8 text-xs rounded border border-slate-700 bg-slate-900/60 text-slate-200 px-2 font-mono"
                data-testid="replay-mode-select"
              >
                <option value="automatic_authorized">automatic_authorized</option>
                <option value="step_by_step">step_by_step</option>
                <option value="dry_run">dry_run</option>
              </select>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-300">Runtime Arguments (JSON)</label>
              <Input
                value={argsJson}
                onChange={(e) => setArgsJson(e.target.value)}
                placeholder='{"query": "Autonom"}'
                className="h-8 text-xs bg-slate-900/60 font-mono"
                data-testid="replay-arguments-input"
              />
            </div>
          </div>

          <div className="flex items-center gap-2 pt-1 border-t border-slate-800">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRunPreflight}
              className="h-8 text-xs gap-1.5"
              data-testid="replay-preflight-btn"
            >
              <ShieldCheck className="h-3.5 w-3.5 text-blue-400" />
              Verify Preflight
            </Button>
            <Button
              size="sm"
              onClick={handleExecute}
              disabled={isRunning || !procedureId}
              className="h-8 text-xs gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-medium"
              data-testid="start-replay-btn"
            >
              <Play className="h-3.5 w-3.5 fill-current" />
              Execute Procedure
            </Button>
          </div>

          {/* Preflight Summary Banner */}
          {preflight && (
            <div
              className={`p-3 rounded border text-xs space-y-1 ${
                preflight.can_execute
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                  : 'bg-red-500/10 border-red-500/30 text-red-300'
              }`}
            >
              <div className="font-semibold flex items-center gap-2">
                {preflight.can_execute ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-red-400" />
                )}
                Preflight Status: {preflight.can_execute ? 'All Checks Passed' : 'Blocked by Safety Checks'}
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[11px] pt-1">
                <div>Adapters Ready: {preflight.adapters_ready ? 'Yes' : 'No'}</div>
                <div>Emergency Stop Active: {preflight.emergency_stop_active ? 'YES' : 'No'}</div>
                <div>Session Locked: {preflight.session_locked ? 'YES' : 'No'}</div>
                <div>Required Adapters: {preflight.required_adapters.join(', ') || 'None'}</div>
              </div>
              {preflight.issues.length > 0 && (
                <div className="pt-1 text-[11px] font-mono">
                  Issues: {preflight.issues.join(' | ')}
                </div>
              )}
            </div>
          )}

          {statusMessage && (
            <div className="text-xs p-2 rounded bg-slate-800/80 border border-slate-700 text-slate-300 font-mono">
              {statusMessage}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Live Execution Results & Step Progression */}
      {currentExecution && (
        <Card className="border-border/60 bg-card/60">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-sm font-semibold flex items-center gap-2">
                  <Terminal className="h-4 w-4 text-blue-400" />
                  Execution Result: <span className="font-mono">{currentExecution.execution_id}</span>
                </CardTitle>
                <CardDescription className="text-xs">
                  Procedure: <span className="font-mono text-slate-300">{currentExecution.procedure_id} v{currentExecution.version}</span> • Mode: <span className="font-mono text-slate-300">{currentExecution.mode}</span>
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Badge
                  variant="outline"
                  className={`font-mono text-xs uppercase ${
                    currentExecution.status === 'completed'
                      ? 'border-emerald-500/40 text-emerald-400 bg-emerald-500/10'
                      : currentExecution.status === 'failed'
                      ? 'border-red-500/40 text-red-400 bg-red-500/10'
                      : 'border-blue-500/40 text-blue-400'
                  }`}
                  data-testid="execution-status-badge"
                >
                  {currentExecution.status}
                </Badge>
                <span className="font-mono text-xs text-slate-400">
                  {currentExecution.execution_time_ms}ms
                </span>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Step Completion Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              <div className="p-2.5 rounded bg-slate-900/50 border border-slate-800">
                <span className="text-slate-400">Completed Steps</span>
                <div className="text-base font-bold font-mono text-emerald-400 mt-0.5">
                  {currentExecution.completed_steps.length} / {currentExecution.total_steps}
                </div>
              </div>
              <div className="p-2.5 rounded bg-slate-900/50 border border-slate-800">
                <span className="text-slate-400">Preserved Checkpoints</span>
                <div className="text-base font-bold font-mono text-blue-400 mt-0.5">
                  {currentExecution.checkpoints.length}
                </div>
              </div>
              <div className="p-2.5 rounded bg-slate-900/50 border border-slate-800">
                <span className="text-slate-400">External Side Effects</span>
                <div className="text-base font-bold font-mono text-amber-400 mt-0.5">
                  {currentExecution.side_effects.length}
                </div>
              </div>
            </div>

            {/* Completed Steps Sequence */}
            <div className="space-y-1.5">
              <div className="text-xs font-semibold text-slate-300">Executed Step Sequence:</div>
              <div className="space-y-1">
                {currentExecution.completed_steps.map((stepId, idx) => (
                  <div
                    key={stepId}
                    className="flex items-center justify-between p-2 rounded bg-slate-900/40 border border-slate-800 text-xs font-mono"
                  >
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                      <span className="text-slate-300">Step {idx + 1}: {stepId}</span>
                    </div>
                    <Badge variant="outline" className="text-[10px] text-emerald-400 border-emerald-500/30">
                      RESOLVED & VERIFIED
                    </Badge>
                  </div>
                ))}
              </div>
            </div>

            {currentExecution.error_message && (
              <div className="p-2.5 rounded bg-red-500/10 border border-red-500/30 text-red-300 text-xs font-mono">
                Error: {currentExecution.error_message}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};
