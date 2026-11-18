import * as React from 'react';
import {
  Clock,
  ListTodo,
  Play,
  RefreshCw,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';
import type {
  VisualTaskRequest,
  VisualTaskResponse,
} from '@autonom/shared-types';

export const VisualTasksTab: React.FC = () => {
  const [instruction, setInstruction] = React.useState('');
  const [tasks, setTasks] = React.useState<VisualTaskResponse[]>([]);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const fetchTasks = React.useCallback(async () => {
    try {
      const list = await apiClient.listVisualTasks();
      setTasks(list);
    } catch (err) {
      console.error('Failed to list visual tasks:', err);
    }
  }, []);

  React.useEffect(() => {
    fetchTasks();
    const interval = setInterval(fetchTasks, 3000);
    return () => clearInterval(interval);
  }, [fetchTasks]);

  const handleSubmitTask = async () => {
    if (!instruction.trim()) return;
    setIsSubmitting(true);
    try {
      const req: VisualTaskRequest = {
        instruction: instruction.trim(),
        display_index: 0,
      };
      await apiClient.submitVisualTask(req);
      setInstruction('');
      await fetchTasks();
    } catch (err) {
      console.error('Submit task failed:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="outline" className="border-emerald-500/40 text-emerald-400">Completed</Badge>;
      case 'failed':
        return <Badge variant="outline" className="border-rose-500/40 text-rose-400">Failed</Badge>;
      case 'acting':
      case 'grounding':
      case 'observing':
      case 'verifying':
        return <Badge variant="outline" className="border-cyan-500/40 text-cyan-400 animate-pulse">{status.toUpperCase()}</Badge>;
      default:
        return <Badge variant="outline" className="border-border text-muted-foreground">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Submit Task Card */}
      <Card className="border-border/60 bg-card/40">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <ListTodo className="h-5 w-5 text-indigo-400" />
            Visual Natural Language Computer Tasks
          </CardTitle>
          <CardDescription className="text-xs">
            Submit an instruction to observe the desktop, ground the requested element, dispatch verified mouse/keyboard interaction, and verify completion.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input
              placeholder="e.g. 'Click Start button', 'Locate Search and click', 'Find Notepad window'..."
              value={instruction}
              onChange={(e) => setInstruction(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSubmitTask()}
              className="text-xs font-mono"
            />
            <Button
              onClick={handleSubmitTask}
              disabled={isSubmitting || !instruction.trim()}
              className="gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs"
            >
              {isSubmitting ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
              Execute Task
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Task Queue List */}
      <Card className="border-border/60 bg-card/40">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              Visual Task Queue ({tasks.length})
            </CardTitle>
            <Button size="sm" variant="ghost" onClick={fetchTasks} className="h-7 text-xs">
              <RefreshCw className="h-3 w-3" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 font-mono text-xs">
            {tasks.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                No visual tasks submitted yet.
              </div>
            )}
            {tasks.map((t) => (
              <div key={t.task_id} className="p-3 rounded-lg border border-border bg-card/60 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getStatusBadge(t.status)}
                    <span className="font-semibold text-foreground text-sm font-sans">{t.instruction}</span>
                  </div>
                  <span className="text-[11px] text-muted-foreground">{t.task_id}</span>
                </div>
                {t.result_summary && (
                  <p className="text-xs text-foreground/80 font-mono bg-background/50 p-2 rounded border border-border/50">
                    {t.result_summary}
                  </p>
                )}
                {t.error_message && (
                  <p className="text-xs text-rose-400 font-mono bg-rose-500/10 p-2 rounded border border-rose-500/30">
                    {t.error_message}
                  </p>
                )}
                <div className="flex items-center justify-between text-[11px] text-muted-foreground pt-1">
                  <span>Steps: {t.steps_completed} / {t.total_steps}</span>
                  <span>Created: {new Date(t.created_at).toLocaleTimeString()}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
