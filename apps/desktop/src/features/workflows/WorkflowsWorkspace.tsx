import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Workflow, Play, Eye, Layers } from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleToolbar,
  ModuleTabs,
  ModuleUnavailableState,
  ModuleDetailPanel,
  ModuleLoadingState,
  ModuleEmptyState,
  ModuleErrorState,
} from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { apiClient } from '@/lib/api-client';
import type { TaskResponse } from '@autonom/shared-types';

export const WorkflowsWorkspace: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const getInitialTab = (): string => {
    if (location.pathname.includes('/workflows/active')) return 'active';
    if (location.pathname.includes('/workflows/builder')) return 'builder';
    if (location.pathname.includes('/workflows/scheduled')) return 'scheduled';
    if (location.pathname.includes('/workflows/history')) return 'history';
    return 'all';
  };

  const [activeTab, setActiveTab] = React.useState<string>(getInitialTab());
  const [searchQuery, setSearchQuery] = React.useState('');
  const [selectedTask, setSelectedTask] = React.useState<TaskResponse | null>(null);

  const [tasks, setTasks] = React.useState<TaskResponse[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [isRefreshing, setIsRefreshing] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [isDispatching, setIsDispatching] = React.useState(false);

  React.useEffect(() => {
    setActiveTab(getInitialTab());
  }, [location.pathname]);

  const loadData = React.useCallback(async () => {
    setError(null);
    try {
      const res = await apiClient.listTasks();
      setTasks(res.tasks);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to query tasks.');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  React.useEffect(() => {
    loadData();
  }, [loadData]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === 'all') navigate('/workflows/all');
    else navigate(`/workflows/${tabId}`);
  };

  const handleDispatchTask = async () => {
    setIsDispatching(true);
    try {
      await apiClient.createTask({
        task_type: 'system_health_check',
        priority: 'high',
        payload: { initiated_from: 'workflows_workspace' },
      });
      await loadData();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Task dispatch failed.');
    } finally {
      setIsDispatching(false);
    }
  };

  const handleCancelTask = async (taskId: string) => {
    try {
      await apiClient.cancelTask(taskId);
      await loadData();
      if (selectedTask?.task_id === taskId) {
        setSelectedTask(null);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Task cancellation failed.');
    }
  };

  const filteredTasks = tasks.filter((t) => {
    const matchesSearch =
      t.task_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.task_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (t.message && t.message.toLowerCase().includes(searchQuery.toLowerCase()));

    if (activeTab === 'active') {
      return matchesSearch && (t.state === 'running' || t.state === 'queued');
    }
    if (activeTab === 'history') {
      return (
        matchesSearch &&
        (t.state === 'completed' || t.state === 'failed' || t.state === 'cancelled')
      );
    }
    return matchesSearch;
  });

  const getStatusBadge = (state: string) => {
    switch (state) {
      case 'completed':
        return <Badge variant="success">Completed</Badge>;
      case 'running':
        return (
          <Badge variant="cyan" pulse>
            Running
          </Badge>
        );
      case 'queued':
      case 'planning':
        return <Badge variant="warning">Queued</Badge>;
      case 'failed':
        return <Badge variant="error">Failed</Badge>;
      case 'cancelled':
        return <Badge variant="inactive">Cancelled</Badge>;
      default:
        return <Badge variant="neutral">{state}</Badge>;
    }
  };

  const tabs = [
    { id: 'all', label: 'All Tasks & Workflows', badge: tasks.length },
    {
      id: 'active',
      label: 'Active & Executing',
      badge: tasks.filter((t) => t.state === 'running' || t.state === 'queued').length,
    },
    { id: 'builder', label: 'Visual DAG Builder' },
    { id: 'scheduled', label: 'Cron Schedules', badge: 0 },
    { id: 'history', label: 'Execution Logs' },
  ];

  return (
    <ModulePage
      isDetailOpen={!!selectedTask}
      detailPanel={
        selectedTask ? (
          <ModuleDetailPanel
            title={selectedTask.task_type}
            subtitle={selectedTask.task_id}
            onClose={() => setSelectedTask(null)}
            actions={
              selectedTask.state === 'running' || selectedTask.state === 'queued' ? (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => handleCancelTask(selectedTask.task_id)}
                  className="h-8 text-xs"
                >
                  Cancel Task
                </Button>
              ) : null
            }
          >
            <div className="space-y-5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Current State
                </span>
                {getStatusBadge(selectedTask.state)}
              </div>

              <div>
                <div className="flex justify-between text-xs text-muted-foreground mb-1.5">
                  <span>Progress</span>
                  <span className="font-mono">
                    {Math.round((selectedTask.progress ?? 0) * 100)}%
                  </span>
                </div>
                <Progress value={(selectedTask.progress ?? 0) * 100} className="h-2" />
                {selectedTask.message && (
                  <p className="mt-1 text-xs text-muted-foreground italic">
                    {selectedTask.message}
                  </p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="rounded-lg border border-border/40 bg-background/50 p-2.5">
                  <span className="text-[10px] text-muted-foreground uppercase font-semibold">
                    Priority
                  </span>
                  <p className="mt-0.5 font-semibold font-mono text-foreground uppercase">
                    {selectedTask.priority}
                  </p>
                </div>
                <div className="rounded-lg border border-border/40 bg-background/50 p-2.5">
                  <span className="text-[10px] text-muted-foreground uppercase font-semibold">
                    ID
                  </span>
                  <p className="mt-0.5 font-semibold font-mono text-foreground truncate">
                    {selectedTask.task_id.substring(0, 8)}
                  </p>
                </div>
              </div>

              {selectedTask.error && (
                <div className="rounded-lg border border-status-error/30 bg-status-error/10 p-3">
                  <span className="text-[11px] font-semibold text-status-error uppercase">
                    Error Summary
                  </span>
                  <pre className="mt-1 text-[11px] text-status-error whitespace-pre-wrap font-mono">
                    {selectedTask.error}
                  </pre>
                </div>
              )}

              <div className="border-t border-border/40 pt-3 text-[11px] text-muted-foreground font-mono space-y-1">
                <div>Created: {new Date(selectedTask.created_at).toLocaleString()}</div>
                {selectedTask.started_at && (
                  <div>Started: {new Date(selectedTask.started_at).toLocaleString()}</div>
                )}
                {selectedTask.completed_at && (
                  <div>Finished: {new Date(selectedTask.completed_at).toLocaleString()}</div>
                )}
              </div>
            </div>
          </ModuleDetailPanel>
        ) : null
      }
    >
      <ModuleHeader
        title="Workflows & Task Orchestration"
        description="Persistent task execution engine, cooperative cancellation, DAG scheduling, and worker dispatch."
        icon={Workflow}
        stageTag="Stage 03 Foundation / Stage 45 Planned"
        badgeLabel={`${tasks.length} Durable Tasks`}
        badgeVariant="outline"
        actions={
          <Button
            size="sm"
            onClick={handleDispatchTask}
            disabled={isDispatching}
            className="text-xs gap-1.5"
          >
            <Play className="h-3.5 w-3.5" />
            Dispatch Diagnostic Task
          </Button>
        }
      />

      <ModuleUnavailableState
        moduleName="Visual DAG Builder & Advanced Workflow Automation"
        stageTag="Stage 45"
        stageName="Visual Orchestration & MCP Workflows"
        description="Complex multi-agent DAG canvas authoring, conditional branch triggers, and MCP tool workflows will activate in Stage 45. The underlying Stage 03 durable task execution manager and SQLite persistence engine are live below."
        plannedCapabilities={[
          'Drag-and-drop node graph DAG editor (Stage 45)',
          'Declarative JSON workflow templates (Stage 45)',
          'Cron-based recurrent scheduling engine (Stage 45)',
          'Cooperative task cancellation & state machine rollbacks (Active)',
        ]}
      />

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={handleTabChange} />

      <ModuleToolbar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        searchPlaceholder="Filter tasks by ID, message, or handler type..."
        onRefresh={() => {
          setIsRefreshing(true);
          loadData();
        }}
        isRefreshing={isRefreshing}
      />

      {error ? (
        <ModuleErrorState
          title="Could not query tasks"
          message={error}
          onRetry={loadData}
          isRetrying={isRefreshing}
        />
      ) : isLoading ? (
        <ModuleLoadingState rows={4} layout="table" />
      ) : activeTab === 'builder' ? (
        <Card className="border-border/60 bg-card/60">
          <CardHeader>
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Layers className="h-4 w-4 text-primary" />
              Visual DAG Workflow Canvas
            </CardTitle>
            <CardDescription className="text-xs">
              Interactive flowchart for multi-agent tasks and conditional branches
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="relative aspect-video w-full overflow-hidden rounded-lg border border-dashed border-border/80 bg-background/50 flex flex-col items-center justify-center p-8 text-center">
              <Workflow className="h-10 w-10 text-primary/60" />
              <h4 className="mt-3 text-sm font-semibold text-foreground">
                Visual Workflow Designer Scheduled for Stage 45
              </h4>
              <p className="mt-1 max-w-sm text-xs text-muted-foreground">
                Node-based graph builder connecting 24 autonomous agents with MCP tools and triggers
                will render here.
              </p>
            </div>
          </CardContent>
        </Card>
      ) : filteredTasks.length === 0 ? (
        <ModuleEmptyState
          icon={Workflow}
          title="No tasks in this view"
          description="Click 'Dispatch Diagnostic Task' above to execute a real asynchronous task on the backend worker pool."
          actionLabel="Dispatch Diagnostic Task"
          onAction={handleDispatchTask}
        />
      ) : (
        <div className="space-y-3">
          {filteredTasks.map((t) => (
            <Card
              key={t.task_id}
              className={`cursor-pointer border border-border/60 bg-card/60 transition-all hover:border-primary/50 hover:bg-card/90 ${
                selectedTask?.task_id === t.task_id ? 'ring-2 ring-primary border-primary' : ''
              }`}
              onClick={() => setSelectedTask(t)}
            >
              <CardContent className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="space-y-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h4 className="truncate text-sm font-semibold text-foreground">
                      {t.task_type}
                    </h4>
                    {getStatusBadge(t.state)}
                  </div>
                  <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground font-mono">
                    <span>ID: {t.task_id}</span>
                    <span>Priority: {t.priority}</span>
                    <span>Created: {new Date(t.created_at).toLocaleTimeString()}</span>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0 self-end sm:self-center">
                  <div className="w-24 text-right">
                    <span className="text-xs font-mono text-muted-foreground">
                      {Math.round((t.progress ?? 0) * 100)}%
                    </span>
                    <Progress value={(t.progress ?? 0) * 100} className="h-1.5 mt-1" />
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 gap-1 text-xs text-muted-foreground hover:text-foreground"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedTask(t);
                    }}
                  >
                    <Eye className="h-3.5 w-3.5" />
                    Inspect
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </ModulePage>
  );
};

export default WorkflowsWorkspace;
