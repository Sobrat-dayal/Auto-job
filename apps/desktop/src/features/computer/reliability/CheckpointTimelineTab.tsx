import * as React from 'react';
import {
  Database,
  CheckCircle2,
  Clock,
  Fingerprint,
  RefreshCw,
  FileCode,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type { ExecutionCheckpoint, ProcedureExecution } from '@autonom/shared-types';

export const CheckpointTimelineTab: React.FC = () => {
  const [executions, setExecutions] = React.useState<ProcedureExecution[]>([]);
  const [selectedExecutionId, setSelectedExecutionId] = React.useState<string>('');
  const [checkpoints, setCheckpoints] = React.useState<ExecutionCheckpoint[]>([]);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);

  const loadExecutions = React.useCallback(async () => {
    setIsLoading(true);
    try {
      const list = await apiClient.listExecutions(undefined, 30);
      setExecutions(list);
      if (list.length > 0 && !selectedExecutionId) {
        setSelectedExecutionId(list[0].execution_id);
        const cpList = await apiClient.listExecutionCheckpoints(list[0].execution_id);
        setCheckpoints(cpList);
      }
    } catch (err: any) {
      console.error('Failed to load executions:', err);
    } finally {
      setIsLoading(false);
    }
  }, [selectedExecutionId]);

  React.useEffect(() => {
    loadExecutions();
  }, [loadExecutions]);

  const handleSelectExecution = async (execId: string) => {
    setSelectedExecutionId(execId);
    try {
      const cpList = await apiClient.listExecutionCheckpoints(execId);
      setCheckpoints(cpList);
    } catch (err: any) {
      console.error('Failed to load checkpoints:', err);
    }
  };

  return (
    <div className="space-y-6" data-testid="checkpoint-timeline-tab">
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <Database className="h-4 w-4 text-cyan-400" />
                Persistent Execution Checkpoints & State Fingerprints
              </CardTitle>
              <CardDescription className="text-xs">
                Lightweight, tamper-evident checkpoints with SHA-256 integrity validation and environment state fingerprints.
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={loadExecutions}
              disabled={isLoading}
              className="h-8 gap-1 text-xs"
            >
              <RefreshCw className={`h-3 w-3 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row items-center gap-3">
            <div className="w-full sm:w-80">
              <select
                value={selectedExecutionId}
                onChange={(e) => handleSelectExecution(e.target.value)}
                className="w-full h-8 text-xs rounded border border-slate-700 bg-slate-900/60 text-slate-200 px-2 font-mono"
                data-testid="execution-select-checkpoints"
              >
                {executions.map((ex) => (
                  <option key={ex.execution_id} value={ex.execution_id}>
                    {ex.execution_id} ({ex.status}) - {ex.procedure_id}
                  </option>
                ))}
              </select>
            </div>
            <div className="text-xs text-slate-400 font-mono">
              Total checkpoints for execution: <strong className="text-slate-200">{checkpoints.length}</strong>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Checkpoints Timeline */}
      <div className="space-y-3">
        {checkpoints.length === 0 ? (
          <Card className="border-border/60 bg-card/60">
            <CardContent className="py-12 text-center text-slate-400 text-xs">
              No checkpoints recorded for the selected execution.
            </CardContent>
          </Card>
        ) : (
          checkpoints.map((cp) => (
            <Card
              key={cp.checkpoint_id}
              className="border-border/60 bg-card/60"
              data-testid={`checkpoint-card-${cp.step_index}`}
            >
              <CardContent className="p-4 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-2.5">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="font-mono text-xs bg-slate-800/80 text-cyan-400">
                      Step #{cp.step_index}
                    </Badge>
                    <span className="font-semibold text-xs text-slate-200">
                      Checkpoint: <span className="font-mono">{cp.checkpoint_id}</span>
                    </span>
                    <Badge variant="outline" className="text-[10px] uppercase font-mono">
                      {cp.checkpoint_type}
                    </Badge>
                    {cp.can_resume ? (
                      <Badge variant="outline" className="border-emerald-500/30 text-emerald-400 text-[10px] flex items-center gap-1">
                        <CheckCircle2 className="h-2.5 w-2.5" /> Resume Eligible
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="border-slate-700 text-slate-400 text-[10px]">
                        Historical
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2 font-mono text-[11px] text-slate-400">
                    <Clock className="h-3 w-3 text-slate-500" />
                    {new Date(cp.timestamp).toLocaleTimeString()}
                    <span className="text-emerald-400 border border-emerald-500/30 rounded px-1 py-0.2">
                      SHA-256: {cp.integrity_hash.slice(0, 12)}...
                    </span>
                  </div>
                </div>

                {/* State Fingerprint Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  <div className="p-2.5 rounded bg-slate-900/50 border border-slate-800 space-y-1 font-mono text-[11px]">
                    <div className="text-slate-400 font-sans font-medium text-xs flex items-center gap-1.5">
                      <Fingerprint className="h-3.5 w-3.5 text-blue-400" />
                      State Fingerprint:
                    </div>
                    <div>Window: <span className="text-slate-200">{cp.state_fingerprint.active_window_title || 'N/A'}</span></div>
                    <div>Process: <span className="text-slate-200">{cp.state_fingerprint.active_process_name || 'N/A'}</span></div>
                    {cp.state_fingerprint.browser_url && (
                      <div>URL: <span className="text-blue-400">{cp.state_fingerprint.browser_url}</span></div>
                    )}
                    {cp.state_fingerprint.focused_element_id && (
                      <div>Focused: <span className="text-slate-300">{cp.state_fingerprint.focused_element_id}</span></div>
                    )}
                  </div>

                  <div className="p-2.5 rounded bg-slate-900/50 border border-slate-800 space-y-1 font-mono text-[11px]">
                    <div className="text-slate-400 font-sans font-medium text-xs flex items-center gap-1.5">
                      <FileCode className="h-3.5 w-3.5 text-purple-400" />
                      Scope Variables Snapshot:
                    </div>
                    <pre className="text-slate-300 overflow-x-auto whitespace-pre-wrap max-h-24">
                      {JSON.stringify(cp.scope_variables, null, 2)}
                    </pre>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};
