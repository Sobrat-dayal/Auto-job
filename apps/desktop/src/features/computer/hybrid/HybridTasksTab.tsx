import * as React from 'react';
import { CheckCircle, Play, RefreshCw, XCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import {
  HybridActionType,
  HybridTaskRequest,
  HybridTaskResponse,
  InteractionMethod,
} from '@autonom/shared-types';

export const HybridTasksTab: React.FC = () => {
  const [instruction, setInstruction] = React.useState<string>('Click the submit application button');
  const [targetHint, setTargetHint] = React.useState<string>('button#submit-application');
  const [actionType, setActionType] = React.useState<HybridActionType>('click');
  const [preferredMethod, setPreferredMethod] = React.useState<string>('auto');

  const [tasks, setTasks] = React.useState<HybridTaskResponse[]>([]);
  const [selectedTask, setSelectedTask] = React.useState<HybridTaskResponse | null>(null);
  const [loading, setLoading] = React.useState<boolean>(false);
  const [submitting, setSubmitting] = React.useState<boolean>(false);

  const loadTasks = React.useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.listHybridTasks(30);
      setTasks(res);
      setSelectedTask((prev) => prev || (res.length > 0 ? res[res.length - 1] : null));
    } catch (err) {
      console.error('Failed to load hybrid tasks:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const handleSubmitTask = async () => {
    if (!instruction.trim()) return;
    setSubmitting(true);
    try {
      const pref = preferredMethod === 'auto' ? undefined : (preferredMethod as InteractionMethod);
      const req: HybridTaskRequest = {
        instruction,
        action_type: actionType,
        preferred_method: pref,
        allow_fallback: true,
      };

      const newResp = await apiClient.submitHybridTask(req);
      setTasks((prev) => [...prev, newResp]);
      setSelectedTask(newResp);
    } catch (err) {
      console.error('Task submission failed:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Submission Card */}
      <Card className="border-slate-800 bg-slate-900/40">
        <CardHeader>
          <CardTitle className="text-base text-slate-100 flex items-center justify-between">
            <span>Dispatch Hybrid Computer Task</span>
            <Button
              variant="outline"
              size="sm"
              onClick={loadTasks}
              disabled={loading}
              className="border-slate-700 bg-slate-800 text-slate-200"
            >
              <RefreshCw className={`mr-2 h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </CardTitle>
          <CardDescription className="text-xs text-slate-400">
            Dispatches autonomous tasks with deterministic method routing, verification, and context-aware fallback.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">Natural Language Instruction</label>
              <Input
                value={instruction}
                onChange={(e) => setInstruction(e.target.value)}
                placeholder="e.g. Click submit button or Type name into form"
                className="h-8 border-slate-700 bg-slate-800 text-xs text-slate-200"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">Target Hint / Locator</label>
              <Input
                value={targetHint}
                onChange={(e) => setTargetHint(e.target.value)}
                placeholder="button#submit or Window Title"
                className="h-8 border-slate-700 bg-slate-800 text-xs text-slate-200"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">Action Type</label>
              <select
                value={actionType}
                onChange={(e) => setActionType(e.target.value as HybridActionType)}
                className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:border-blue-500 focus:outline-none"
              >
                <option value="click">Click Element</option>
                <option value="enter_text">Enter Text / Fill</option>
                <option value="navigate">Navigate URL</option>
                <option value="scroll">Scroll Content</option>
                <option value="submit">Submit Application</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">Method Routing Policy</label>
              <select
                value={preferredMethod}
                onChange={(e) => setPreferredMethod(e.target.value)}
                className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:border-blue-500 focus:outline-none"
              >
                <option value="auto">Auto (Deterministic Routing & Fallback)</option>
                <option value="BROWSER_DOM">Prefer BROWSER_DOM</option>
                <option value="WINDOWS_UIA">Prefer WINDOWS_UIA</option>
                <option value="WINDOWS_WIN32">Prefer WINDOWS_WIN32</option>
                <option value="VISUAL_GROUNDING">Prefer VISUAL_GROUNDING</option>
              </select>
            </div>
          </div>

          <Button
            onClick={handleSubmitTask}
            disabled={submitting || !instruction.trim()}
            className="w-full bg-blue-600 hover:bg-blue-500 text-xs font-semibold"
          >
            <Play className="mr-2 h-3.5 w-3.5" />
            {submitting ? 'Executing Task...' : 'Execute Hybrid Task'}
          </Button>
        </CardContent>
      </Card>

      {/* Task History and Timeline Split View */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Task List */}
        <Card className="border-slate-800 bg-slate-900/40">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold text-slate-200">Execution History</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-xs">
            {tasks.length > 0 ? (
              tasks.slice().reverse().map((t) => (
                <div
                  key={t.task_id}
                  onClick={() => setSelectedTask(t)}
                  className={`cursor-pointer rounded-lg border p-3 transition-colors ${
                    selectedTask?.task_id === t.task_id
                      ? 'border-blue-500/60 bg-blue-950/20'
                      : 'border-slate-800 bg-slate-950/40 hover:bg-slate-900/60'
                  }`}
                >
                  <div className="flex items-center justify-between font-mono text-[11px] mb-1">
                    <span className="font-semibold text-slate-200 truncate max-w-[200px]">{t.instruction}</span>
                    <Badge
                      variant="outline"
                      className={`text-[10px] ${
                        t.status === 'completed'
                          ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
                          : t.status === 'executing'
                          ? 'border-blue-500/30 bg-blue-500/10 text-blue-400'
                          : 'border-red-500/30 bg-red-500/10 text-red-400'
                      }`}
                    >
                      {t.status}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span className="font-mono text-slate-300">Method: {t.selected_method || 'Unset'}</span>
                    <span>Attempts: {t.attempts.length || 1}</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-slate-500 text-center py-8">No tasks recorded yet.</p>
            )}
          </CardContent>
        </Card>

        {/* Selected Task Details & Timeline */}
        <Card className="border-slate-800 bg-slate-900/40">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold text-slate-200">Task Timeline & Fallback Log</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-xs">
            {selectedTask ? (
              <div className="space-y-4">
                <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3 space-y-1">
                  <div className="flex justify-between font-mono text-[11px]">
                    <span className="text-slate-400">Task ID: {selectedTask.task_id}</span>
                    <span className="text-slate-300">{new Date(selectedTask.created_at).toLocaleTimeString()}</span>
                  </div>
                  <p className="font-semibold text-slate-200">{selectedTask.instruction}</p>
                </div>

                <div className="space-y-2">
                  <span className="font-semibold text-slate-300">Execution Attempts:</span>
                  <div className="space-y-2">
                    {selectedTask.attempts.map((att, idx) => (
                      <div key={idx} className="flex items-start gap-2 rounded border border-slate-800/80 bg-slate-900/60 p-2.5">
                        {att.success ? (
                          <CheckCircle className="h-4 w-4 text-emerald-400 mt-0.5" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-400 mt-0.5" />
                        )}
                        <div className="flex-1 space-y-0.5">
                          <div className="flex justify-between font-mono text-[11px]">
                            <span className="font-bold text-slate-200">
                              Step {att.step}: {att.method}
                            </span>
                            <span className="text-slate-400">{att.duration_ms} ms</span>
                          </div>
                          <p className="text-[11px] text-slate-400">
                            Verification: <span className="font-mono text-slate-300">{att.verification}</span>
                          </p>
                          {att.error && <p className="text-[11px] text-red-400">{att.error}</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-slate-500 text-center py-8">Select a task to view execution details.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
