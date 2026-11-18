import * as React from 'react';
import { Send, Ban, RefreshCw, Terminal } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';
import type { DesktopTaskResponse } from '@autonom/shared-types';

export const DesktopTasksTab: React.FC = () => {
  const [tasks, setTasks] = React.useState<DesktopTaskResponse[]>([]);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [goal, setGoal] = React.useState<string>('');
  const [targetApp, setTargetApp] = React.useState<string>('notepad.exe');
  const [submitting, setSubmitting] = React.useState<boolean>(false);

  const fetchTasks = React.useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiClient.listDesktopTasks();
      setTasks(data);
    } catch (err) {
      console.error('Failed to list desktop tasks:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goal.trim()) return;

    try {
      setSubmitting(true);
      await apiClient.submitDesktopTask({
        goal: goal.trim(),
        target_app: targetApp,
      });
      setGoal('');
      fetchTasks();
    } catch (err) {
      console.error('Failed to submit desktop task:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = async (taskId: string) => {
    try {
      await apiClient.cancelDesktopTask(taskId);
      fetchTasks();
    } catch (err) {
      console.error('Failed to cancel task:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Task Submission Builder */}
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold">Autonomous Desktop Task Dispatch</CardTitle>
          <CardDescription>
            Submit an autonomous goal for the Windows Computer Agent and Structural UI Agent.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex flex-col gap-3 sm:flex-row">
              <div className="relative flex-1">
                <Terminal className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="e.g., Open Notepad, type verified test content, and verify the editor value..."
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  className="pl-9 text-xs bg-background/50 h-9"
                />
              </div>

              <select
                value={targetApp}
                onChange={(e) => setTargetApp(e.target.value)}
                className="h-9 rounded-md border border-border/80 bg-background/50 px-3 text-xs font-mono text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              >
                <option value="notepad.exe">Notepad (notepad.exe)</option>
                <option value="calc.exe">Calculator (calc.exe)</option>
                <option value="explorer.exe">File Explorer (explorer.exe)</option>
                <option value="powershell.exe">PowerShell (powershell.exe)</option>
              </select>

              <Button
                type="submit"
                disabled={submitting || !goal.trim()}
                className="gap-2 h-9 px-4 text-xs bg-cyan-600 hover:bg-cyan-500 font-medium"
              >
                <Send className="h-3.5 w-3.5" />
                Dispatch Task
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Tasks Queue Table */}
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-semibold">Desktop Tasks Queue</CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchTasks}
              disabled={loading}
              className="gap-1.5 text-xs h-8"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-border/60 bg-muted/30 text-muted-foreground font-mono uppercase text-[10px]">
                <tr>
                  <th className="py-2.5 px-3">Task ID</th>
                  <th className="py-2.5 px-3">Goal Directive</th>
                  <th className="py-2.5 px-3">Target Application</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Progress</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40 font-mono">
                {tasks.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-muted-foreground">
                      No desktop tasks currently queued.
                    </td>
                  </tr>
                ) : (
                  tasks.map((task) => (
                    <tr key={task.task_id} className="hover:bg-muted/20 transition-colors">
                      <td className="py-2.5 px-3 text-cyan-400 font-medium">{task.task_id}</td>
                      <td className="py-2.5 px-3 font-sans font-medium text-foreground max-w-[260px] truncate" title={task.goal}>
                        {task.goal}
                      </td>
                      <td className="py-2.5 px-3 text-muted-foreground">{task.target_app || 'System'}</td>
                      <td className="py-2.5 px-3">
                        <Badge
                          variant={task.status === 'completed' ? 'success' : task.status === 'failed' ? 'error' : 'neutral'}
                          className="text-[10px]"
                        >
                          {task.status}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3 text-muted-foreground">
                        Step {task.current_step}/{task.total_steps}
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        {task.status === 'pending' || task.status === 'running' ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleCancel(task.task_id)}
                            className="h-6 gap-1 px-2 text-[10px] text-rose-400 hover:text-rose-300"
                          >
                            <Ban className="h-2.5 w-2.5" />
                            Cancel
                          </Button>
                        ) : null}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
