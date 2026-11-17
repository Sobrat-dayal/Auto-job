import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Workflow,
  Play,
  Pause,
  RotateCcw,
  XCircle,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Layers,
  ShieldCheck,
  PlusCircle,
  Eye,
  RefreshCw,
} from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleToolbar,
  ModuleTabs,
  ModuleLoadingState,
  ModuleEmptyState,
  ModuleErrorState,
} from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';
import type {
  DAGVisualizationData,
  OrchestrationStats,
  WorkflowResponse,
  WorkflowStepResponse,
  WorkflowSummary,
} from '@autonom/shared-types';

export const WorkflowsWorkspace: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const getInitialTab = (): string => {
    if (location.pathname.includes('/workflows/active')) return 'active';
    if (location.pathname.includes('/workflows/builder')) return 'builder';
    if (location.pathname.includes('/workflows/history')) return 'history';
    return 'all';
  };

  const [activeTab, setActiveTab] = React.useState<string>(getInitialTab());
  const [searchQuery, setSearchQuery] = React.useState('');
  const [workflows, setWorkflows] = React.useState<WorkflowSummary[]>([]);
  const [selectedWorkflowId, setSelectedWorkflowId] = React.useState<string | null>(null);
  const [selectedWorkflow, setSelectedWorkflow] = React.useState<WorkflowResponse | null>(null);
  const [dagData, setDagData] = React.useState<DAGVisualizationData | null>(null);
  const [selectedStep, setSelectedStep] = React.useState<WorkflowStepResponse | null>(null);
  const [stats, setStats] = React.useState<OrchestrationStats | null>(null);

  const [isLoading, setIsLoading] = React.useState(true);
  const [isRefreshing, setIsRefreshing] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  // New Workflow Form State
  const [newGoal, setNewGoal] = React.useState(
    'Analyze supplied job description, extract technical skills, summarize responsibilities, identify experience requirements, and produce a structured report'
  );
  const [newJobDescription, setNewJobDescription] = React.useState(
    'Senior AI Systems Engineer at TechCorp\n\nResponsibilities:\n- Design and implement multi-agent orchestration runtime\n- Build distributed task scheduling and DAG execution engines\n- Optimize local LLM inference on NVIDIA RTX hardware\n\nRequirements:\n- 5+ years experience with Python, Rust, and TypeScript\n- Proven background in autonomous AI agents, FastAPI, and React\n- BS or MS in Computer Science or equivalent'
  );
  const [isCreating, setIsCreating] = React.useState(false);

  React.useEffect(() => {
    setActiveTab(getInitialTab());
  }, [location.pathname]);

  const loadData = React.useCallback(async () => {
    setError(null);
    try {
      const [listRes, statsRes] = await Promise.all([
        apiClient.listWorkflows(),
        apiClient.getOrchestrationStats().catch(() => null),
      ]);
      setWorkflows(listRes);
      if (statsRes) setStats(statsRes);

      if (listRes.length > 0 && !selectedWorkflowId) {
        setSelectedWorkflowId(listRes[0].id);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to query workflows.');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [selectedWorkflowId]);

  React.useEffect(() => {
    loadData();
  }, [loadData]);

  // Load selected workflow details & DAG
  React.useEffect(() => {
    if (!selectedWorkflowId) {
      setSelectedWorkflow(null);
      setDagData(null);
      return;
    }

    let isMounted = true;
    const fetchWorkflow = async () => {
      try {
        const [wf, dag] = await Promise.all([
          apiClient.getWorkflow(selectedWorkflowId),
          apiClient.getWorkflowDag(selectedWorkflowId).catch(() => null),
        ]);
        if (isMounted) {
          setSelectedWorkflow(wf);
          setDagData(dag);
        }
      } catch (err: unknown) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to load workflow details.');
        }
      }
    };

    fetchWorkflow();
    const timer = setInterval(fetchWorkflow, 3000);
    return () => {
      isMounted = false;
      clearInterval(timer);
    };
  }, [selectedWorkflowId]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === 'all') navigate('/workflows/all');
    else navigate(`/workflows/${tabId}`);
  };

  const handleCreateWorkflow = async (executeImmediately: boolean) => {
    if (!newGoal.trim()) return;
    setIsCreating(true);
    setError(null);
    try {
      const created = await apiClient.createWorkflow({
        goal: newGoal.trim(),
        constraints: newJobDescription.trim() ? { job_description: newJobDescription.trim() } : {},
        priority: 'high',
      });
      if (executeImmediately) {
        await apiClient.startWorkflow(created.id, true);
      }
      setSelectedWorkflowId(created.id);
      setActiveTab('all');
      await loadData();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create workflow.');
    } finally {
      setIsCreating(false);
    }
  };

  const handleStartWorkflow = async (id: string) => {
    try {
      await apiClient.startWorkflow(id, true);
      const updated = await apiClient.getWorkflow(id);
      setSelectedWorkflow(updated);
      await loadData();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to start workflow.');
    }
  };

  const handlePauseWorkflow = async (id: string) => {
    try {
      await apiClient.pauseWorkflow(id);
      const updated = await apiClient.getWorkflow(id);
      setSelectedWorkflow(updated);
      await loadData();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to pause workflow.');
    }
  };

  const handleResumeWorkflow = async (id: string) => {
    try {
      await apiClient.resumeWorkflow(id);
      const updated = await apiClient.getWorkflow(id);
      setSelectedWorkflow(updated);
      await loadData();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to resume workflow.');
    }
  };

  const handleCancelWorkflow = async (id: string) => {
    try {
      await apiClient.cancelWorkflow(id);
      const updated = await apiClient.getWorkflow(id);
      setSelectedWorkflow(updated);
      await loadData();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to cancel workflow.');
    }
  };

  const handleReplanWorkflow = async (id: string) => {
    try {
      await apiClient.replanWorkflow(id, { reason: 'Dynamic manual replanning requested by user.' });
      const updated = await apiClient.getWorkflow(id);
      setSelectedWorkflow(updated);
      await loadData();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to replan workflow.');
    }
  };

  const filteredWorkflows = workflows.filter((w) => {
    const matchesSearch =
      w.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      w.goal.toLowerCase().includes(searchQuery.toLowerCase()) ||
      w.id.toLowerCase().includes(searchQuery.toLowerCase());

    if (activeTab === 'active') {
      return (
        matchesSearch &&
        ['running', 'queued', 'planning', 'plan_ready', 'recovering', 'verifying'].includes(w.status)
      );
    }
    if (activeTab === 'history') {
      return matchesSearch && ['completed', 'failed', 'cancelled', 'partially_completed'].includes(w.status);
    }
    return matchesSearch;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge className="bg-emerald-600/20 text-emerald-400 border-emerald-500/30">Completed</Badge>;
      case 'running':
        return <Badge className="bg-amber-600/20 text-amber-400 border-amber-500/30 animate-pulse">Running</Badge>;
      case 'planning':
      case 'plan_ready':
        return <Badge className="bg-blue-600/20 text-blue-400 border-blue-500/30">Plan Ready</Badge>;
      case 'paused':
        return <Badge className="bg-zinc-600/20 text-zinc-400 border-zinc-500/30">Paused</Badge>;
      case 'failed':
        return <Badge className="bg-rose-600/20 text-rose-400 border-rose-500/30">Failed</Badge>;
      case 'cancelled':
        return <Badge className="bg-zinc-600/20 text-zinc-400 border-zinc-500/30">Cancelled</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getStepStatusIndicator = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-emerald-400" />;
      case 'running':
        return <RefreshCw className="h-4 w-4 text-amber-400 animate-spin" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-rose-400" />;
      case 'blocked':
        return <AlertTriangle className="h-4 w-4 text-purple-400" />;
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  return (
    <ModulePage>
      <ModuleHeader
        title="Workflows Workspace"
        description="Autonomous multi-agent goal planning, DAG visualization, dynamic execution, and multi-layer verification."
        icon={Workflow}
        stageTag="Stage 12 Multi-Agent Orchestrator"
        badgeLabel={stats ? `${stats.completed_workflows} Completed` : undefined}
        actions={
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setIsRefreshing(true);
                loadData();
              }}
              disabled={isRefreshing}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button
              size="sm"
              className="bg-primary hover:bg-primary/90 text-primary-foreground"
              onClick={() => setActiveTab('builder')}
            >
              <PlusCircle className="h-4 w-4 mr-2" />
              New Goal
            </Button>
          </div>
        }
      />

      <ModuleToolbar
        searchPlaceholder="Search workflows by title, goal, or id..."
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />

      <ModuleTabs
        tabs={[
          { id: 'all', label: 'All Workflows', badge: workflows.length },
          {
            id: 'active',
            label: 'Active & Running',
            badge: workflows.filter((w) => ['running', 'queued', 'planning', 'plan_ready'].includes(w.status)).length,
          },
          { id: 'builder', label: 'Goal & Plan Builder' },
          {
            id: 'history',
            label: 'History & Logs',
            badge: workflows.filter((w) => ['completed', 'failed', 'cancelled'].includes(w.status)).length,
          },
        ]}
        activeTab={activeTab}
        onTabChange={handleTabChange}
      />

      {error && (
        <div className="mb-4">
          <ModuleErrorState title="Orchestration Runtime Alert" message={error} onRetry={loadData} />
        </div>
      )}

      {/* BUILDER TAB */}
      {activeTab === 'builder' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <Card className="border-border/60 bg-card/60 backdrop-blur">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Workflow className="h-5 w-5 text-primary" />
                  Define Autonomous Goal
                </CardTitle>
                <CardDescription>
                  Enter a high-level directive. The Planning Agent will decompose it into a validated dependency DAG.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Goal Statement</label>
                  <Input
                    value={newGoal}
                    onChange={(e) => setNewGoal(e.target.value)}
                    placeholder="e.g. Analyze job description and extract requirements..."
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Target Context / Document Text</label>
                  <textarea
                    rows={8}
                    value={newJobDescription}
                    onChange={(e) => setNewJobDescription(e.target.value)}
                    placeholder="Paste job description, requirements, or code..."
                    className="w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono"
                  />
                </div>
                <div className="flex gap-3 pt-2">
                  <Button
                    className="bg-primary hover:bg-primary/90 text-primary-foreground"
                    onClick={() => handleCreateWorkflow(true)}
                    disabled={isCreating || !newGoal.trim()}
                  >
                    <Play className="h-4 w-4 mr-2" />
                    {isCreating ? 'Planning & Starting...' : 'Plan & Run Autonomous Workflow'}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleCreateWorkflow(false)}
                    disabled={isCreating || !newGoal.trim()}
                  >
                    <Layers className="h-4 w-4 mr-2" />
                    Plan Only (Review DAG)
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          <div>
            <Card className="border-border/60 bg-card/40 backdrop-blur">
              <CardHeader>
                <CardTitle className="text-sm font-semibold">Active Coordination Core</CardTitle>
                <CardDescription>Multi-Agent Runtime Engine (Stage 12)</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex justify-between items-center p-2 rounded bg-muted/40">
                  <span className="font-medium">Supervisor Agent</span>
                  <Badge variant="outline" className="text-emerald-400 border-emerald-500/30">Active</Badge>
                </div>
                <div className="flex justify-between items-center p-2 rounded bg-muted/40">
                  <span className="font-medium">Planning Agent</span>
                  <Badge variant="outline" className="text-emerald-400 border-emerald-500/30">DAG Cycle Check</Badge>
                </div>
                <div className="flex justify-between items-center p-2 rounded bg-muted/40">
                  <span className="font-medium">Task Router Agent</span>
                  <Badge variant="outline" className="text-emerald-400 border-emerald-500/30">Explainable</Badge>
                </div>
                <div className="flex justify-between items-center p-2 rounded bg-muted/40">
                  <span className="font-medium">Verification Agent</span>
                  <Badge variant="outline" className="text-emerald-400 border-emerald-500/30">Deterministic + AI</Badge>
                </div>
                <div className="flex justify-between items-center p-2 rounded bg-muted/40">
                  <span className="font-medium">Recovery Agent</span>
                  <Badge variant="outline" className="text-emerald-400 border-emerald-500/30">13 Categories</Badge>
                </div>
                <div className="pt-2 text-xs text-muted-foreground border-t border-border/40">
                  Hardware Guardrail: Single-active local LLM slot enforced for RTX 4050 6GB; deterministic steps execute concurrently.
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* WORKFLOWS LIST & DETAIL VIEW */}
      {activeTab !== 'builder' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Workflow List */}
          <div className="lg:col-span-4 space-y-3">
            {isLoading ? (
              <ModuleLoadingState rows={3} layout="simple" />
            ) : filteredWorkflows.length === 0 ? (
              <ModuleEmptyState
                title="No Workflows Found"
                description={searchQuery ? 'No workflows match your search query.' : 'Create an autonomous goal to start.'}
                actionLabel="Create Goal"
                onAction={() => setActiveTab('builder')}
              />
            ) : (
              filteredWorkflows.map((w) => {
                const isSelected = w.id === selectedWorkflowId;
                const progressPct = w.total_steps > 0 ? Math.round((w.completed_steps / w.total_steps) * 100) : 0;
                return (
                  <Card
                    key={w.id}
                    onClick={() => setSelectedWorkflowId(w.id)}
                    className={`cursor-pointer transition-all border ${
                      isSelected
                        ? 'border-primary/80 bg-primary/5 shadow-md'
                        : 'border-border/60 hover:border-primary/40 bg-card/60'
                    }`}
                  >
                    <CardHeader className="p-4 pb-2">
                      <div className="flex justify-between items-start gap-2">
                        <CardTitle className="text-sm font-semibold truncate leading-tight">{w.title}</CardTitle>
                        {getStatusBadge(w.status)}
                      </div>
                      <CardDescription className="text-xs line-clamp-2 mt-1">{w.goal}</CardDescription>
                    </CardHeader>
                    <CardContent className="p-4 pt-1 space-y-2">
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>
                          {w.completed_steps}/{w.total_steps} steps
                        </span>
                        <span>{progressPct}%</span>
                      </div>
                      <Progress value={progressPct} className="h-1.5" />
                    </CardContent>
                  </Card>
                );
              })
            )}
          </div>

          {/* Right Column: Workflow Detail & Interactive DAG */}
          <div className="lg:col-span-8 space-y-4">
            {selectedWorkflow ? (
              <div className="space-y-4">
                {/* Control Header Card */}
                <Card className="border-border/60 bg-card/70 backdrop-blur">
                  <CardHeader className="p-5 pb-3">
                    <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <h2 className="text-lg font-bold">{selectedWorkflow.title}</h2>
                          {getStatusBadge(selectedWorkflow.status)}
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">ID: {selectedWorkflow.id}</p>
                      </div>
                      {/* Operational Controls */}
                      <div className="flex gap-2">
                        {['created', 'plan_ready', 'paused'].includes(selectedWorkflow.status) && (
                          <Button
                            size="sm"
                            className="bg-emerald-600 hover:bg-emerald-500 text-white"
                            onClick={() =>
                              selectedWorkflow.status === 'paused'
                                ? handleResumeWorkflow(selectedWorkflow.id)
                                : handleStartWorkflow(selectedWorkflow.id)
                            }
                          >
                            <Play className="h-4 w-4 mr-1" />
                            {selectedWorkflow.status === 'paused' ? 'Resume' : 'Start'}
                          </Button>
                        )}
                        {selectedWorkflow.status === 'running' && (
                          <Button
                            size="sm"
                            variant="outline"
                            className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10"
                            onClick={() => handlePauseWorkflow(selectedWorkflow.id)}
                          >
                            <Pause className="h-4 w-4 mr-1" />
                            Pause
                          </Button>
                        )}
                        {['running', 'queued', 'paused', 'plan_ready'].includes(selectedWorkflow.status) && (
                          <Button
                            size="sm"
                            variant="outline"
                            className="border-rose-500/40 text-rose-400 hover:bg-rose-500/10"
                            onClick={() => handleCancelWorkflow(selectedWorkflow.id)}
                          >
                            <XCircle className="h-4 w-4 mr-1" />
                            Cancel
                          </Button>
                        )}
                        {['failed', 'partially_completed'].includes(selectedWorkflow.status) && (
                          <Button
                            size="sm"
                            variant="outline"
                            className="border-primary/40 text-primary hover:bg-primary/10"
                            onClick={() => handleReplanWorkflow(selectedWorkflow.id)}
                          >
                            <RotateCcw className="h-4 w-4 mr-1" />
                            Replan
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="p-5 pt-0 space-y-3">
                    <p className="text-sm bg-muted/30 p-2.5 rounded border border-border/40 font-mono text-xs">
                      {selectedWorkflow.goal}
                    </p>
                  </CardContent>
                </Card>

                {/* Interactive DAG Visualizer */}
                <Card className="border-border/60 bg-card/60 backdrop-blur">
                  <CardHeader className="p-4 pb-2">
                    <CardTitle className="text-sm font-semibold flex items-center gap-2">
                      <Layers className="h-4 w-4 text-primary" />
                      Execution Plan DAG (Topological Stages)
                    </CardTitle>
                    <CardDescription className="text-xs">
                      Independent nodes within a stage execute concurrently; dependent stages wait for upstream completion.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="p-4">
                    {dagData && dagData.stages && dagData.stages.length > 0 ? (
                      <div className="space-y-4">
                        {dagData.stages.map((stageStepIds, stageIndex) => (
                          <div key={stageIndex} className="relative">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                Stage {stageIndex}
                              </span>
                              <div className="h-px flex-1 bg-border/60" />
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                              {stageStepIds.map((stepId) => {
                                const stepDetail = selectedWorkflow.steps.find((s) => s.step_id === stepId);
                                const isStepSelected = selectedStep?.step_id === stepId;
                                return (
                                  <div
                                    key={stepId}
                                    onClick={() => stepDetail && setSelectedStep(stepDetail)}
                                    className={`p-3 rounded-lg border cursor-pointer transition-all ${
                                      isStepSelected
                                        ? 'border-primary ring-1 ring-primary bg-primary/10'
                                        : 'border-border/60 hover:border-primary/40 bg-card/80'
                                    }`}
                                  >
                                    <div className="flex items-start justify-between gap-1 mb-1">
                                      <span className="text-xs font-mono font-medium truncate">
                                        {stepDetail ? stepDetail.title : stepId}
                                      </span>
                                      {stepDetail && getStepStatusIndicator(stepDetail.status)}
                                    </div>
                                    <div className="flex flex-wrap gap-1 mt-2">
                                      <Badge variant="outline" className="text-[10px] px-1.5 py-0 font-mono">
                                        {stepDetail?.capability_id || 'step'}
                                      </Badge>
                                      {stepDetail?.assigned_agent_id && (
                                        <Badge
                                          variant="outline"
                                          className="text-[10px] px-1.5 py-0 bg-primary/10 text-primary border-primary/20"
                                        >
                                          {stepDetail.assigned_agent_id}
                                        </Badge>
                                      )}
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-sm text-muted-foreground">
                        No DAG stages generated yet.
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Step Inspector Drawer / Panel */}
                {selectedStep && (
                  <Card className="border-border/60 bg-card/80 backdrop-blur">
                    <CardHeader className="p-4 pb-2 flex flex-row items-center justify-between">
                      <div>
                        <CardTitle className="text-sm font-semibold flex items-center gap-2">
                          <Eye className="h-4 w-4 text-primary" />
                          Step Inspector: {selectedStep.title}
                        </CardTitle>
                        <CardDescription className="text-xs font-mono">
                          ID: {selectedStep.step_id} | Capability: {selectedStep.capability_id}
                        </CardDescription>
                      </div>
                      <Button variant="ghost" size="sm" onClick={() => setSelectedStep(null)}>
                        ✕
                      </Button>
                    </CardHeader>
                    <CardContent className="p-4 space-y-4">
                      {/* Verification Status */}
                      <div className="flex items-center gap-2 p-2 rounded bg-muted/40 text-xs">
                        <ShieldCheck className="h-4 w-4 text-primary" />
                        <span className="font-semibold">Verification Audit:</span>
                        <Badge
                          variant="outline"
                          className={
                            selectedStep.verification_status === 'pass'
                              ? 'text-emerald-400 border-emerald-500/30'
                              : 'text-amber-400 border-amber-500/30'
                          }
                        >
                          {selectedStep.verification_status || 'Pending'}
                        </Badge>
                      </div>

                      {/* Output Result */}
                      {selectedStep.output_result && (
                        <div className="space-y-1">
                          <label className="text-xs font-semibold text-muted-foreground">Output Artifact</label>
                          {selectedStep.output_result.transformed_data?.report_markdown ? (
                            <div className="p-3 rounded bg-zinc-950/80 border border-border/50 text-xs font-mono whitespace-pre-wrap max-h-60 overflow-y-auto">
                              {selectedStep.output_result.transformed_data.report_markdown}
                            </div>
                          ) : (
                            <pre className="p-3 rounded bg-zinc-950/80 border border-border/50 text-xs font-mono max-h-60 overflow-y-auto">
                              {JSON.stringify(selectedStep.output_result, null, 2)}
                            </pre>
                          )}
                        </div>
                      )}

                      {/* Error Info if any */}
                      {selectedStep.error_info && (
                        <div className="p-3 rounded bg-rose-950/30 border border-rose-500/40 text-rose-300 text-xs font-mono">
                          <p className="font-semibold">Error Details:</p>
                          <pre>{JSON.stringify(selectedStep.error_info, null, 2)}</pre>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}
              </div>
            ) : (
              <ModuleEmptyState
                title="Select a Workflow"
                description="Choose a workflow from the list to inspect its execution plan, interactive DAG, and step outputs."
              />
            )}
          </div>
        </div>
      )}
    </ModulePage>
  );
};

export default WorkflowsWorkspace;
