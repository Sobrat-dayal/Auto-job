import * as React from 'react';
import {
  RotateCcw,
  AlertTriangle,
  CheckCircle2,
  Shield,
  History,
  RefreshCw,
  FileCheck2,
  Zap,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type {
  ProcedureExecution,
  RecoveryPlan,
} from '@autonom/shared-types';

export const RecoveryCenterTab: React.FC = () => {
  const [interruptedExecutions, setInterruptedExecutions] = React.useState<ProcedureExecution[]>([]);
  const [selectedExecution, setSelectedExecution] = React.useState<ProcedureExecution | null>(null);
  const [recoveryPlan, setRecoveryPlan] = React.useState<RecoveryPlan | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [isResuming, setIsResuming] = React.useState<boolean>(false);
  const [statusMessage, setStatusMessage] = React.useState<string | null>(null);

  const loadInterrupted = React.useCallback(async () => {
    setIsLoading(true);
    try {
      const all = await apiClient.listExecutions(undefined, 50);
      const candidates = all.filter(
        (ex) => ex.status === 'failed' || ex.status === 'paused' || ex.status === 'aborted'
      );
      setInterruptedExecutions(candidates);
      if (candidates.length > 0 && !selectedExecution) {
        handleSelectExecution(candidates[0]);
      }
    } catch (err: any) {
      console.error('Failed to load interrupted executions:', err);
    } finally {
      setIsLoading(false);
    }
  }, [selectedExecution]);

  React.useEffect(() => {
    loadInterrupted();
  }, [loadInterrupted]);

  const handleSelectExecution = async (exec: ProcedureExecution) => {
    setSelectedExecution(exec);
    try {
      const plan = await apiClient.getRecoveryPlan(exec.execution_id);
      setRecoveryPlan(plan);
    } catch (err: any) {
      console.error('Failed to load recovery plan:', err);
      setRecoveryPlan(null);
    }
  };

  const handleResume = async () => {
    if (!selectedExecution) return;
    setIsResuming(true);
    setStatusMessage(null);
    try {
      const resumed = await apiClient.resumeExecution(selectedExecution.execution_id);
      setSelectedExecution(resumed);
      setStatusMessage(
        resumed.status === 'completed'
          ? `Execution ${resumed.execution_id} successfully resumed and finished in ${resumed.execution_time_ms}ms!`
          : `Resumed execution status: ${resumed.status}`
      );
      await loadInterrupted();
    } catch (err: any) {
      setStatusMessage(`Resume error: ${err.message}`);
    } finally {
      setIsResuming(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="recovery-center-tab">
      {/* Header Banner */}
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <RotateCcw className="h-4 w-4 text-amber-400" />
                Autonomous Crash Recovery & Side-Effect Reconciliation
              </CardTitle>
              <CardDescription className="text-xs">
                Inspects crashed or interrupted procedure executions, verifies external side effects to prevent duplicate operations, and safely resumes from verified checkpoints.
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={loadInterrupted}
              disabled={isLoading}
              className="h-8 gap-1 text-xs"
            >
              <RefreshCw className={`h-3 w-3 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-xs text-slate-300 font-mono">
            Interrupted / recoverable executions identified: <strong className="text-amber-400">{interruptedExecutions.length}</strong>
          </div>
          {statusMessage && (
            <div className="mt-3 text-xs p-2 rounded bg-slate-800/80 border border-slate-700 text-slate-300 font-mono">
              {statusMessage}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Grid: Interrupted Executions & Recovery Plan */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Interrupted List */}
        <Card className="border-border/60 bg-card/60">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <History className="h-4 w-4 text-blue-400" />
              Interrupted Executions
            </CardTitle>
            <CardDescription className="text-xs">
              Select an execution to view its automated recovery plan.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {interruptedExecutions.length === 0 ? (
              <div className="text-center py-8 text-slate-400 text-xs">
                No interrupted or crashed executions found. All workflows completed cleanly.
              </div>
            ) : (
              <div className="space-y-2">
                {interruptedExecutions.map((ex) => (
                  <div
                    key={ex.execution_id}
                    onClick={() => handleSelectExecution(ex)}
                    className={`p-3 rounded border text-xs cursor-pointer transition-colors ${
                      selectedExecution?.execution_id === ex.execution_id
                        ? 'border-blue-500 bg-blue-500/10'
                        : 'border-slate-800 bg-slate-900/40 hover:border-slate-700'
                    }`}
                    data-testid={`interrupted-item-${ex.execution_id}`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-200">{ex.procedure_id}</span>
                      <Badge
                        variant="outline"
                        className={`font-mono text-[10px] uppercase ${
                          ex.status === 'failed' ? 'border-red-500/40 text-red-400' : 'border-amber-500/40 text-amber-400'
                        }`}
                      >
                        {ex.status}
                      </Badge>
                    </div>
                    <div className="text-slate-400 text-[11px] font-mono mt-1">
                      ID: {ex.execution_id.slice(0, 16)}...
                    </div>
                    <div className="flex items-center gap-3 text-[11px] text-slate-500 mt-1">
                      <span>Completed: {ex.completed_steps.length}/{ex.total_steps}</span>
                      <span>Checkpoints: {ex.checkpoints.length}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recovery Plan & Ledger Inspector */}
        <Card className="border-border/60 bg-card/60 lg:col-span-2">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-sm font-semibold flex items-center gap-2">
                  <Shield className="h-4 w-4 text-emerald-400" />
                  Deterministic Recovery Plan
                </CardTitle>
                <CardDescription className="text-xs">
                  Reconciled against durable checkpoints and side-effect idempotency ledger.
                </CardDescription>
              </div>
              {recoveryPlan && recoveryPlan.can_resume && (
                <Button
                  size="sm"
                  onClick={handleResume}
                  disabled={isResuming}
                  className="gap-1.5 h-8 text-xs bg-emerald-600 hover:bg-emerald-700 text-white font-medium"
                  data-testid="resume-execution-btn"
                >
                  <Zap className="h-3 w-3 fill-current" />
                  Resume Safely from Step #{recoveryPlan.resume_step_index}
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {!selectedExecution ? (
              <div className="text-center py-8 text-slate-400 text-xs">
                Select an interrupted execution to inspect its recovery plan.
              </div>
            ) : !recoveryPlan ? (
              <div className="text-center py-8 text-slate-400 text-xs">
                Generating automated recovery plan for {selectedExecution.execution_id}...
              </div>
            ) : (
              <div className="space-y-4 text-xs">
                {/* Status banner */}
                <div
                  className={`p-3 rounded border space-y-1 ${
                    recoveryPlan.can_resume
                      ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                      : 'bg-red-500/10 border-red-500/30 text-red-300'
                  }`}
                >
                  <div className="font-semibold flex items-center gap-2">
                    {recoveryPlan.can_resume ? (
                      <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                    ) : (
                      <AlertTriangle className="h-4 w-4 text-red-400" />
                    )}
                    Recovery Classification: <span className="font-mono">{recoveryPlan.classification}</span>
                  </div>
                  <div className="text-[11px] font-sans text-slate-300 pt-1">
                    {recoveryPlan.rationale}
                  </div>
                </div>

                {/* Plan details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="p-3 rounded bg-slate-900/50 border border-slate-800 space-y-1 font-mono text-[11px]">
                    <span className="text-slate-400 font-sans font-medium text-xs">Skipped Steps (Already Verified):</span>
                    {recoveryPlan.actions_to_skip.length === 0 ? (
                      <div className="text-slate-500 italic">None</div>
                    ) : (
                      <ul className="list-disc pl-4 space-y-0.5 text-emerald-400">
                        {recoveryPlan.actions_to_skip.map((s, i) => (
                          <li key={i}>{s}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                  <div className="p-3 rounded bg-slate-900/50 border border-slate-800 space-y-1 font-mono text-[11px]">
                    <span className="text-slate-400 font-sans font-medium text-xs">Steps to Execute on Resume:</span>
                    {recoveryPlan.actions_to_reexecute.length === 0 ? (
                      <div className="text-slate-500 italic">None</div>
                    ) : (
                      <ul className="list-disc pl-4 space-y-0.5 text-blue-400">
                        {recoveryPlan.actions_to_reexecute.map((s, i) => (
                          <li key={i}>{s}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>

                {/* External Side-Effect Ledger for this execution */}
                <div className="space-y-2 pt-2 border-t border-slate-800">
                  <div className="font-semibold text-slate-300 flex items-center gap-2">
                    <FileCheck2 className="h-4 w-4 text-cyan-400" />
                    External Side-Effect Ledger ({selectedExecution.side_effects.length} records)
                  </div>
                  {selectedExecution.side_effects.length === 0 ? (
                    <div className="text-slate-500 italic text-[11px]">
                      No external non-idempotent side effects were executed prior to interruption.
                    </div>
                  ) : (
                    <div className="space-y-1.5 max-h-48 overflow-y-auto">
                      {selectedExecution.side_effects.map((se) => (
                        <div
                          key={se.effect_id}
                          className="flex items-center justify-between p-2 rounded bg-slate-950 border border-slate-800 text-[11px] font-mono"
                        >
                          <div className="flex items-center gap-2">
                            <span className="text-slate-400">[{se.target_system}]</span>
                            <span className="font-semibold text-slate-200">{se.operation}</span>
                            <Badge
                              variant="outline"
                              className={`text-[9px] uppercase ${
                                se.outcome === 'confirmed'
                                  ? 'text-emerald-400 border-emerald-500/30'
                                  : 'text-amber-400 border-amber-500/30'
                              }`}
                            >
                              {se.outcome}
                            </Badge>
                          </div>
                          <span className="text-slate-500 text-[10px]">
                            Hash: {se.intent_hash.slice(0, 10)}...
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
