/**
 * Tab: Discovery Tasks & Execution Monitor (Stage 26).
 * Real-time monitoring of asynchronous discovery runs, snapshot statuses, and errors.
 */

import * as React from 'react';
import { RefreshCw, XCircle, AlertTriangle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type { DiscoveryTaskRecord } from '@autonom/shared-types';

interface DiscoveryTasksTabProps {
  tasks: DiscoveryTaskRecord[];
  onRefresh: () => void;
}

export const DiscoveryTasksTab: React.FC<DiscoveryTasksTabProps> = ({ tasks, onRefresh }) => {
  const [cancellingId, setCancellingId] = React.useState<string | null>(null);

  const handleCancel = async (taskId: string) => {
    try {
      setCancellingId(taskId);
      await apiClient.cancelDiscoveryTask(taskId);
      onRefresh();
    } catch (err: any) {
      alert(`Failed to cancel task: ${err.message}`);
    } finally {
      setCancellingId(null);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold">Discovery Execution Tasks</h3>
          <p className="text-sm text-muted-foreground">
            Audit asynchronous crawling tasks, bounded concurrent workers, and provider sync errors.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={onRefresh}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh Tasks
        </Button>
      </div>

      {tasks.length === 0 ? (
        <Card className="border">
          <CardContent className="py-12 text-center text-sm text-muted-foreground">
            No discovery tasks executed yet. Start one from the Search & Discover tab.
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {tasks.map((task) => {
            const isTerminal = ['completed', 'failed', 'cancelled', 'partially_completed'].includes(task.status);
            return (
              <Card key={task.id} className="border">
                <CardContent className="p-4 space-y-2 text-xs">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm font-mono">{task.id}</span>
                        <Badge
                          variant="outline"
                          className={`text-[10px] capitalize ${
                            task.status === 'completed'
                              ? 'text-emerald-600 border-emerald-300'
                              : task.status === 'running'
                              ? 'text-blue-600 border-blue-300'
                              : task.status === 'failed'
                              ? 'text-rose-600 border-rose-300'
                              : 'text-amber-600 border-amber-300'
                          }`}
                        >
                          {task.status.replace(/_/g, ' ')}
                        </Badge>
                      </div>
                      <div className="text-muted-foreground mt-0.5">
                        Started: {new Date(task.started_at).toLocaleTimeString()}{' '}
                        {task.completed_at ? `• Completed: ${new Date(task.completed_at).toLocaleTimeString()}` : ''}
                      </div>
                    </div>

                    {!isTerminal && (
                      <Button
                        variant="destructive"
                        size="sm"
                        className="h-7 text-xs"
                        disabled={cancellingId === task.id}
                        onClick={() => handleCancel(task.id)}
                      >
                        <XCircle className="w-3.5 h-3.5 mr-1" />
                        Cancel Task
                      </Button>
                    )}
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 py-1 text-muted-foreground">
                    <div>
                      <span className="font-medium text-foreground">Target Sources:</span> {task.selected_sources.length}
                    </div>
                    <div>
                      <span className="font-medium text-foreground">Postings Found:</span> {task.total_postings_found}
                    </div>
                    <div>
                      <span className="font-medium text-foreground">New Postings:</span> {task.new_postings_count}
                    </div>
                    <div>
                      <span className="font-medium text-foreground">Errors:</span> {task.errors.length}
                    </div>
                  </div>

                  {task.errors.length > 0 && (
                    <div className="p-2.5 rounded bg-rose-950/20 border border-rose-900/50 space-y-1 text-rose-300">
                      <div className="font-medium flex items-center gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5" />
                        Provider Errors ({task.errors.length}):
                      </div>
                      <ul className="list-disc list-inside space-y-0.5 font-mono text-[11px]">
                        {task.errors.map((err, idx) => (
                          <li key={idx} className="truncate">
                            {err}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};
