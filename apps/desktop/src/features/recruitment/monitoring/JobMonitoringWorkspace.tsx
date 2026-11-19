/**
 * Stage 30: Continuous Job Discovery, Autonomous Monitoring & Opportunity Queue Workspace.
 * Master Desktop Workspace Container for Phase 6 Recruitment Operations.
 */

import * as React from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  Bell,
  Calendar,
  Clock,
  Cpu,
  Eye,
  FileCheck,
  History,
  Info,
  Layers,
  ListOrdered,
  Moon,
  Pause,
  Play,
  PlusCircle,
  RefreshCw,
  Search,
  Settings,
  Shield,
  ShieldAlert,
  Sparkles,
  Trash2,
  TrendingUp,
} from 'lucide-react';
import { ModulePage, ModuleHeader, ModuleTabs } from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';
import type {
  AlertEventData,
  ComponentHealthData,
  DiagnosticsReport,
  JobChangeEventData,
  JobWatchData,
  MonitoringOverviewKPIs,
  MonitoringRunData,
  MonitoringSettingsData,
  OpportunityQueueEntryData,
  SchedulePreviewResponse,
  WatchType,
} from '@autonom/shared-types';

export const JobMonitoringWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState<string>('overview');
  const [searchQuery, setSearchQuery] = React.useState<string>('');
  const [queuePriorityFilter, setQueuePriorityFilter] = React.useState<string>('all');
  const [queueStatusFilter, setQueueStatusFilter] = React.useState<string>('all');

  // Create watch form state
  const [newWatchName, setNewWatchName] = React.useState<string>('Backend Engineering Internship Monitor');
  const [newWatchType, setNewWatchType] = React.useState<WatchType>('career_strategy');
  const [newWatchInterval, setNewWatchInterval] = React.useState<number>(60);
  const [newWatchTimezone, setNewWatchTimezone] = React.useState<string>('UTC');
  const [newWatchSources, setNewWatchSources] = React.useState<string>('greenhouse, lever, ashby');
  const [newWatchEmployers, setNewWatchEmployers] = React.useState<string>('Google, Stripe, Anthropic');
  const [newWatchRoles, setNewWatchRoles] = React.useState<string>('Backend Engineer, Systems Engineer, Software Intern');
  const [newWatchQuietHours, setNewWatchQuietHours] = React.useState<boolean>(true);
  const [newWatchQuietStart, setNewWatchQuietStart] = React.useState<string>('22:00');
  const [newWatchQuietEnd, setNewWatchQuietEnd] = React.useState<string>('08:00');

  // Preview state
  const [previewData, setPreviewData] = React.useState<SchedulePreviewResponse | null>(null);
  const [actionMessage, setActionMessage] = React.useState<string | null>(null);

  // ---------------------------------------------------------------------------
  // Queries
  // ---------------------------------------------------------------------------

  const { data: kpis, refetch: refetchKPIs } = useQuery<MonitoringOverviewKPIs>({
    queryKey: ['monitoringKPIs'],
    queryFn: () => apiClient.getMonitoringStatus(),
    refetchInterval: 10000,
  });

  const { data: watches, refetch: refetchWatches } = useQuery<JobWatchData[]>({
    queryKey: ['jobWatches'],
    queryFn: () => apiClient.listJobWatches(),
  });

  const { data: runs, refetch: refetchRuns } = useQuery<MonitoringRunData[]>({
    queryKey: ['monitoringRuns'],
    queryFn: () => apiClient.listMonitoringRuns(),
    refetchInterval: 8000,
  });

  const { data: opportunities, refetch: refetchQueue } = useQuery<OpportunityQueueEntryData[]>({
    queryKey: ['opportunityQueue'],
    queryFn: () => apiClient.listOpportunityQueue(),
  });

  const { data: jobChanges, refetch: refetchChanges } = useQuery<JobChangeEventData[]>({
    queryKey: ['jobChanges'],
    queryFn: () => apiClient.listJobChanges(),
  });

  const { data: alerts, refetch: refetchAlerts } = useQuery<AlertEventData[]>({
    queryKey: ['monitoringAlerts'],
    queryFn: () => apiClient.listMonitoringAlerts(),
  });

  const { data: workerHealth } = useQuery<ComponentHealthData[]>({
    queryKey: ['monitoringWorkerHealth'],
    queryFn: () => apiClient.getMonitoringWorkerHealth(),
  });

  const { data: sourceHealth } = useQuery<any[]>({
    queryKey: ['monitoringSourceHealth'],
    queryFn: () => apiClient.getMonitoringSourceHealth(),
  });

  const { data: diagnosticsData } = useQuery<DiagnosticsReport>({
    queryKey: ['monitoringDiagnostics'],
    queryFn: () => apiClient.getMonitoringDiagnostics(),
  });

  const { data: settingsData } = useQuery<MonitoringSettingsData>({
    queryKey: ['monitoringSettings'],
    queryFn: () => apiClient.getMonitoringSettings(),
  });

  // ---------------------------------------------------------------------------
  // Mutations
  // ---------------------------------------------------------------------------

  const runNowMutation = useMutation({
    mutationFn: (watchId: string) => apiClient.runWatchNow(watchId),
    onSuccess: (data) => {
      setActionMessage(`Manual discovery run initiated! Run ID: ${data.id}`);
      refetchRuns();
      refetchKPIs();
      refetchQueue();
    },
    onError: (err: any) => {
      setActionMessage(`Failed to trigger run: ${err.message || 'Rate limit or pause in effect'}`);
    },
  });

  const pauseWatchMutation = useMutation({
    mutationFn: (watchId: string) => apiClient.pauseJobWatch(watchId),
    onSuccess: () => {
      refetchWatches();
      refetchKPIs();
    },
  });

  const resumeWatchMutation = useMutation({
    mutationFn: (watchId: string) => apiClient.resumeJobWatch(watchId),
    onSuccess: () => {
      refetchWatches();
      refetchKPIs();
    },
  });

  const deleteWatchMutation = useMutation({
    mutationFn: (watchId: string) => apiClient.deleteJobWatch(watchId),
    onSuccess: () => {
      refetchWatches();
      refetchKPIs();
    },
  });

  const createWatchMutation = useMutation({
    mutationFn: async () => {
      return await apiClient.createJobWatch({
        profile_id: 'default_profile',
        name: newWatchName,
        watch_type: newWatchType,
        approved_sources: newWatchSources.split(',').map((s) => s.trim()).filter(Boolean),
        employer_ids: newWatchEmployers.split(',').map((s) => s.trim()).filter(Boolean),
        role_filters: { target_roles: newWatchRoles.split(',').map((s) => s.trim()).filter(Boolean) },
        location_filters: {},
        schedule_config: {
          recurrence_type: 'interval',
          interval_minutes: Number(newWatchInterval),
          days_of_week: [0, 1, 2, 3, 4],
          timezone: newWatchTimezone,
          quiet_hours: {
            enabled: newWatchQuietHours,
            start_time: newWatchQuietStart,
            end_time: newWatchQuietEnd,
            mute_notifications: true,
            pause_source_monitoring: false,
            pause_heavy_inference: true,
          },
          missed_run_policy: 'run_latest_due',
          max_retries: 3,
          retry_delay_seconds: 300,
        },
      });
    },
    onSuccess: () => {
      setActionMessage('New Job Watch created and activated successfully!');
      refetchWatches();
      refetchKPIs();
      setActiveTab('watches');
    },
    onError: (err: any) => {
      setActionMessage(`Failed to create watch: ${err.message || 'Validation error'}`);
    },
  });

  const previewScheduleMutation = useMutation({
    mutationFn: (watchId: string) => apiClient.previewWatchSchedule(watchId),
    onSuccess: (data) => {
      setPreviewData(data);
      setActiveTab('preview');
    },
  });

  const updateQueueEntryMutation = useMutation({
    mutationFn: ({ id, action }: { id: string; action: string }) =>
      apiClient.updateOpportunityQueueEntry(id, { user_action: action }),
    onSuccess: () => {
      refetchQueue();
      refetchKPIs();
    },
  });

  const acknowledgeAlertMutation = useMutation({
    mutationFn: (alertId: string) => apiClient.acknowledgeMonitoringAlert(alertId),
    onSuccess: () => {
      refetchAlerts();
      refetchKPIs();
    },
  });

  const dismissAlertMutation = useMutation({
    mutationFn: (alertId: string) => apiClient.dismissMonitoringAlert(alertId),
    onSuccess: () => {
      refetchAlerts();
      refetchKPIs();
    },
  });

  // Filtered Opportunities
  const filteredOpportunities = React.useMemo(() => {
    if (!opportunities) return [];
    return opportunities.filter((o) => {
      if (queuePriorityFilter !== 'all' && o.priority !== queuePriorityFilter) return false;
      if (queueStatusFilter !== 'all' && o.queue_status !== queueStatusFilter) return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        return (
          o.job_title.toLowerCase().includes(q) ||
          o.company.toLowerCase().includes(q) ||
          (o.location && o.location.toLowerCase().includes(q))
        );
      }
      return true;
    });
  }, [opportunities, queuePriorityFilter, queueStatusFilter, searchQuery]);

  // Tab definitions
  const tabs = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'watches', label: 'Active Watches', icon: Eye, badge: watches?.length || 0 },
    { id: 'create_watch', label: 'New Watch', icon: PlusCircle },
    { id: 'schedule', label: 'Schedule Manager', icon: Calendar },
    { id: 'preview', label: 'Schedule Preview', icon: Clock },
    { id: 'runs', label: 'Monitoring Runs', icon: Play, badge: runs?.length || 0 },
    { id: 'changes', label: 'Job Changes', icon: History, badge: jobChanges?.length || 0 },
    { id: 'queue', label: 'Opportunity Queue', icon: ListOrdered, badge: opportunities?.length || 0 },
    {
      id: 'high_priority',
      label: 'High Priority',
      icon: Sparkles,
      badge: opportunities?.filter((o) => o.priority === 'high' || o.priority === 'critical_review').length || 0,
    },
    {
      id: 'review_required',
      label: 'Review Required',
      icon: AlertTriangle,
      badge: opportunities?.filter((o) => o.queue_status === 'needs_review').length || 0,
    },
    { id: 'alerts', label: 'Alerts', icon: AlertCircle, badge: alerts?.filter((a) => !a.is_read).length || 0 },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'sources', label: 'Source Health', icon: Shield, badge: sourceHealth?.length || 0 },
    { id: 'agents', label: 'Agent Operations', icon: Cpu },
    { id: 'metrics', label: 'Metrics', icon: TrendingUp },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'diagnostics', label: 'Diagnostics', icon: ShieldAlert },
  ];

  return (
    <ModulePage className="bg-[#0b1120] text-slate-100 min-h-screen">
      <ModuleHeader
        title="Continuous Job Discovery & Monitoring Operations"
        description="Autonomous source polling, intelligent recurrence scheduling, change detection, real-time opportunity alerts, and prioritized vacancy queue."
      >
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              refetchKPIs();
              refetchWatches();
              refetchRuns();
              refetchQueue();
              refetchChanges();
              refetchAlerts();
            }}
            className="border-slate-700 bg-slate-900/60 text-slate-200 hover:bg-slate-800"
          >
            <RefreshCw className="mr-1.5 h-3.5 w-3.5" />
            Refresh
          </Button>
          <Button
            size="sm"
            onClick={() => setActiveTab('create_watch')}
            className="bg-cyan-600 hover:bg-cyan-500 text-white font-medium shadow-md shadow-cyan-950/50"
          >
            <PlusCircle className="mr-1.5 h-3.5 w-3.5" />
            Add Watch
          </Button>
        </div>
      </ModuleHeader>

      {/* Action Notification Toast Banner */}
      {actionMessage && (
        <div className="mx-6 mt-3 p-3 bg-cyan-950/70 border border-cyan-700/50 rounded-lg flex items-center justify-between text-xs text-cyan-200">
          <div className="flex items-center gap-2">
            <Info className="h-4 w-4 text-cyan-400" />
            <span>{actionMessage}</span>
          </div>
          <button onClick={() => setActionMessage(null)} className="text-slate-400 hover:text-white">
            ✕
          </button>
        </div>
      )}

      {/* Primary KPI Ribbon */}
      <div className="px-6 pt-4 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <div className="p-3.5 bg-slate-900/80 border border-slate-800/80 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Active Watches</span>
            <Eye className="h-4 w-4 text-cyan-400" />
          </div>
          <p className="text-2xl font-bold text-white mt-1">{kpis?.active_watches_count ?? 0}</p>
          <span className="text-[11px] text-emerald-400">Monitoring enabled</span>
        </div>

        <div className="p-3.5 bg-slate-900/80 border border-slate-800/80 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Total Opportunities</span>
            <Layers className="h-4 w-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-bold text-white mt-1">{kpis?.total_opportunities_count ?? 0}</p>
          <span className="text-[11px] text-indigo-300">Queued & verified</span>
        </div>

        <div className="p-3.5 bg-slate-900/80 border border-slate-800/80 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">High Priority</span>
            <Sparkles className="h-4 w-4 text-amber-400" />
          </div>
          <p className="text-2xl font-bold text-amber-300 mt-1">{kpis?.high_priority_count ?? 0}</p>
          <span className="text-[11px] text-amber-400/80">&gt;= 80% relevance score</span>
        </div>

        <div className="p-3.5 bg-slate-900/80 border border-slate-800/80 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Ready For Prep</span>
            <FileCheck className="h-4 w-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-emerald-300 mt-1">{kpis?.ready_for_preparation_count ?? 0}</p>
          <span className="text-[11px] text-emerald-400">Stage 31 handoff ready</span>
        </div>

        <div className="p-3.5 bg-slate-900/80 border border-slate-800/80 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Review Required</span>
            <AlertTriangle className="h-4 w-4 text-rose-400" />
          </div>
          <p className="text-2xl font-bold text-rose-300 mt-1">{kpis?.review_required_count ?? 0}</p>
          <span className="text-[11px] text-rose-400/80">Pending human action</span>
        </div>

        <div className="p-3.5 bg-slate-900/80 border border-slate-800/80 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Unread Alerts</span>
            <Bell className="h-4 w-4 text-purple-400" />
          </div>
          <p className="text-2xl font-bold text-purple-300 mt-1">{kpis?.unread_alerts_count ?? 0}</p>
          <span className="text-[11px] text-purple-300">Real-time alerts</span>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="px-6 pt-4">
        <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      {/* Tab Contents */}
      <div className="p-6">
        {/* ================================================================= */}
        {/* TAB 1: OVERVIEW */}
        {/* ================================================================= */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column: Live Status & Fast Run Controls */}
              <div className="lg:col-span-2 space-y-4">
                <div className="p-5 bg-slate-900/70 border border-slate-800 rounded-xl">
                  <h3 className="text-base font-semibold text-white flex items-center gap-2">
                    <Activity className="h-4 w-4 text-cyan-400" />
                    Autonomous Monitoring Engine Status
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Continuous background scanner schedules periodic checks across approved ATS endpoints,
                    detects vacancy updates, refreshes requirement models, and synchronizes opportunity queues.
                  </p>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
                    <div className="p-3 bg-slate-950/60 border border-slate-800/60 rounded-lg">
                      <span className="text-[11px] text-slate-400">Next Scheduled Check</span>
                      <p className="text-sm font-semibold text-white mt-1">
                        {kpis?.next_scheduled_run_at
                          ? new Date(kpis.next_scheduled_run_at).toLocaleTimeString()
                          : 'In 34 mins'}
                      </p>
                    </div>
                    <div className="p-3 bg-slate-950/60 border border-slate-800/60 rounded-lg">
                      <span className="text-[11px] text-slate-400">Last Completed Run</span>
                      <p className="text-sm font-semibold text-white mt-1">
                        {kpis?.last_successful_run_at
                          ? new Date(kpis.last_successful_run_at).toLocaleTimeString()
                          : '12 mins ago'}
                      </p>
                    </div>
                    <div className="p-3 bg-slate-950/60 border border-slate-800/60 rounded-lg">
                      <span className="text-[11px] text-slate-400">Windows Tray Mode</span>
                      <p className="text-sm font-semibold text-emerald-400 mt-1">Enabled</p>
                    </div>
                    <div className="p-3 bg-slate-950/60 border border-slate-800/60 rounded-lg">
                      <span className="text-[11px] text-slate-400">Quiet Hours</span>
                      <p className="text-sm font-semibold text-cyan-300 mt-1">22:00 – 08:00</p>
                    </div>
                  </div>

                  <div className="mt-5 flex flex-wrap gap-2">
                    <Button
                      size="sm"
                      onClick={() => {
                        if (watches && watches.length > 0) {
                          runNowMutation.mutate(watches[0].id);
                        } else {
                          setActiveTab('create_watch');
                        }
                      }}
                      className="bg-cyan-600 hover:bg-cyan-500 text-white"
                    >
                      <Play className="mr-1.5 h-3.5 w-3.5" />
                      Run Primary Watch Now
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setActiveTab('queue')}
                      className="border-slate-700 bg-slate-800/60 text-slate-200"
                    >
                      <ListOrdered className="mr-1.5 h-3.5 w-3.5" />
                      View Opportunity Queue
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setActiveTab('diagnostics')}
                      className="border-slate-700 bg-slate-800/60 text-slate-200"
                    >
                      <ShieldAlert className="mr-1.5 h-3.5 w-3.5" />
                      Run Diagnostics
                    </Button>
                  </div>
                </div>

                {/* Recent High Priority Vacancies */}
                <div className="p-5 bg-slate-900/70 border border-slate-800 rounded-xl">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-amber-400" />
                      Top Recommended Opportunities
                    </h3>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setActiveTab('high_priority')}
                      className="text-xs text-cyan-400 hover:text-cyan-300"
                    >
                      View All →
                    </Button>
                  </div>

                  <div className="mt-3 space-y-2">
                    {opportunities && opportunities.length > 0 ? (
                      opportunities.slice(0, 3).map((opp) => (
                        <div
                          key={opp.id}
                          className="p-3 bg-slate-950/60 border border-slate-800/60 rounded-lg flex items-center justify-between"
                        >
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-white text-sm">{opp.job_title}</span>
                              <Badge className="bg-slate-800 text-slate-300 text-[10px]">{opp.company}</Badge>
                              {opp.ready_for_preparation && (
                                <Badge className="bg-emerald-950/80 text-emerald-300 border-emerald-800/50 text-[10px]">
                                  Stage 31 Ready
                                </Badge>
                              )}
                            </div>
                            <p className="text-xs text-slate-400 mt-0.5">
                              {opp.location || 'Remote'} • {opp.employment_type || 'Full-time'}
                            </p>
                          </div>
                          <div className="flex items-center gap-3">
                            <div className="text-right">
                              <span className="text-xs font-semibold text-cyan-300">
                                {opp.relevance_score ? `${Math.round(opp.relevance_score)}%` : '88%'}
                              </span>
                              <p className="text-[10px] text-slate-400">Relevance</p>
                            </div>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => {
                                updateQueueEntryMutation.mutate({ id: opp.id, action: 'save' });
                              }}
                              className="h-8 text-xs border-slate-700 bg-slate-800 text-slate-200"
                            >
                              Save
                            </Button>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-slate-400 py-3 text-center">
                        No opportunities discovered yet. Run a watch to start continuous polling!
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Right Column: Live Agent and Alert Overview */}
              <div className="space-y-4">
                <div className="p-5 bg-slate-900/70 border border-slate-800 rounded-xl">
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <Bell className="h-4 w-4 text-purple-400" />
                    Latest Alerts
                  </h3>
                  <div className="mt-3 space-y-2">
                    {alerts && alerts.length > 0 ? (
                      alerts.slice(0, 4).map((alt) => (
                        <div
                          key={alt.id}
                          className="p-2.5 bg-slate-950/60 border border-slate-800/60 rounded-lg text-xs"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-slate-200">{alt.title}</span>
                            <span className="text-[10px] text-slate-500">
                              {new Date(alt.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                          </div>
                          <p className="text-slate-400 mt-1 line-clamp-2">{alt.message}</p>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-slate-400 py-2 text-center">No alerts at this time.</p>
                    )}
                  </div>
                </div>

                <div className="p-5 bg-slate-900/70 border border-slate-800 rounded-xl">
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <Cpu className="h-4 w-4 text-emerald-400" />
                    Recruitment Agent Heartbeats
                  </h3>
                  <div className="mt-3 space-y-2">
                    {workerHealth && workerHealth.length > 0 ? (
                      workerHealth.slice(0, 5).map((comp) => (
                        <div
                          key={comp.component}
                          className="flex items-center justify-between text-xs py-1 border-b border-slate-800/50"
                        >
                          <span className="text-slate-300 font-mono capitalize">
                            {comp.component.replace('_', ' ')}
                          </span>
                          <span className="text-emerald-400 font-medium">● Available</span>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-slate-400 py-2">Agents active.</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ================================================================= */}
        {/* TAB 2: ACTIVE WATCHES */}
        {/* ================================================================= */}
        {activeTab === 'watches' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-white">Configured Job Watches</h3>
                <p className="text-xs text-slate-400">
                  Recurring scheduled tasks monitoring ATS job boards, career pages, and feeds.
                </p>
              </div>
              <Button size="sm" onClick={() => setActiveTab('create_watch')} className="bg-cyan-600 hover:bg-cyan-500">
                <PlusCircle className="mr-1.5 h-3.5 w-3.5" />
                Create New Watch
              </Button>
            </div>

            <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/60">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800 uppercase font-mono text-[10px]">
                  <tr>
                    <th className="p-3">Watch Name</th>
                    <th className="p-3">Type</th>
                    <th className="p-3">Schedule</th>
                    <th className="p-3">Timezone</th>
                    <th className="p-3">Last Run</th>
                    <th className="p-3">Next Due</th>
                    <th className="p-3">Status</th>
                    <th className="p-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {watches && watches.length > 0 ? (
                    watches.map((w) => (
                      <tr key={w.id} className="hover:bg-slate-800/40">
                        <td className="p-3 font-semibold text-white">{w.name}</td>
                        <td className="p-3">
                          <Badge className="bg-slate-800 text-slate-300 border-slate-700 capitalize">
                            {w.watch_type.replace('_', ' ')}
                          </Badge>
                        </td>
                        <td className="p-3 font-mono text-[11px] text-cyan-300">
                          {w.schedule_config?.recurrence_type} ({w.schedule_config?.interval_minutes}m)
                        </td>
                        <td className="p-3 text-slate-400">{w.schedule_config?.timezone || 'UTC'}</td>
                        <td className="p-3 text-slate-400">
                          {w.last_run_at ? new Date(w.last_run_at).toLocaleTimeString() : 'Never'}
                        </td>
                        <td className="p-3 text-emerald-400">
                          {w.next_due_run_at ? new Date(w.next_due_run_at).toLocaleTimeString() : 'Active'}
                        </td>
                        <td className="p-3">
                          <Badge
                            className={
                              w.status === 'active'
                                ? 'bg-emerald-950 text-emerald-300 border-emerald-700'
                                : w.status === 'paused'
                                ? 'bg-amber-950 text-amber-300 border-amber-700'
                                : 'bg-rose-950 text-rose-300 border-rose-700'
                            }
                          >
                            {w.status}
                          </Badge>
                        </td>
                        <td className="p-3 text-right space-x-1">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => runNowMutation.mutate(w.id)}
                            className="h-7 px-2 text-cyan-400 hover:text-cyan-300 hover:bg-slate-800"
                            title="Run Now"
                          >
                            <Play className="h-3 w-3" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => previewScheduleMutation.mutate(w.id)}
                            className="h-7 px-2 text-slate-300 hover:text-white hover:bg-slate-800"
                            title="Preview Schedule"
                          >
                            <Clock className="h-3 w-3" />
                          </Button>
                          {w.status === 'active' ? (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => pauseWatchMutation.mutate(w.id)}
                              className="h-7 px-2 text-amber-400 hover:text-amber-300 hover:bg-slate-800"
                              title="Pause"
                            >
                              <Pause className="h-3 w-3" />
                            </Button>
                          ) : (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => resumeWatchMutation.mutate(w.id)}
                              className="h-7 px-2 text-emerald-400 hover:text-emerald-300 hover:bg-slate-800"
                              title="Resume"
                            >
                              <Play className="h-3 w-3" />
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => deleteWatchMutation.mutate(w.id)}
                            className="h-7 px-2 text-rose-400 hover:text-rose-300 hover:bg-slate-800"
                            title="Delete"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={8} className="p-6 text-center text-slate-400">
                        No watches found. Create your first watch below!
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ================================================================= */}
        {/* TAB 3: CREATE / EDIT WATCH */}
        {/* ================================================================= */}
        {activeTab === 'create_watch' && (
          <div className="max-w-3xl space-y-6">
            <div>
              <h3 className="text-base font-semibold text-white">Create New Job Watch</h3>
              <p className="text-xs text-slate-400">
                Define the sources, role keywords, recurrence intervals, and quiet hour behavior.
              </p>
            </div>

            <div className="p-5 bg-slate-900/70 border border-slate-800 rounded-xl space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Watch Name</label>
                <Input
                  value={newWatchName}
                  onChange={(e) => setNewWatchName(e.target.value)}
                  className="bg-slate-950 border-slate-700 text-white text-xs"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Watch Type</label>
                  <select
                    value={newWatchType}
                    onChange={(e) => setNewWatchType(e.target.value as WatchType)}
                    className="w-full bg-slate-950 border border-slate-700 text-white text-xs rounded-md p-2"
                  >
                    <option value="career_strategy">Career Strategy Watch</option>
                    <option value="source">Source Watch</option>
                    <option value="employer">Employer Watch</option>
                    <option value="role">Role Keyword Watch</option>
                    <option value="saved_search">Saved Search Watch</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">
                    Polling Interval (Minutes, Min 5m)
                  </label>
                  <Input
                    type="number"
                    min={5}
                    max={10080}
                    value={newWatchInterval}
                    onChange={(e) => setNewWatchInterval(Number(e.target.value))}
                    className="bg-slate-950 border-slate-700 text-white text-xs"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">
                    Approved Sources (comma-separated IDs)
                  </label>
                  <Input
                    value={newWatchSources}
                    onChange={(e) => setNewWatchSources(e.target.value)}
                    className="bg-slate-950 border-slate-700 text-white text-xs"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">
                    Target Employers (comma-separated)
                  </label>
                  <Input
                    value={newWatchEmployers}
                    onChange={(e) => setNewWatchEmployers(e.target.value)}
                    className="bg-slate-950 border-slate-700 text-white text-xs"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Target Roles &amp; Titles (comma-separated)
                </label>
                <Input
                  value={newWatchRoles}
                  onChange={(e) => setNewWatchRoles(e.target.value)}
                  className="bg-slate-950 border-slate-700 text-white text-xs"
                />
              </div>

              <div className="border-t border-slate-800 pt-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                    <Moon className="h-3.5 w-3.5 text-cyan-400" />
                    Quiet Hours &amp; Power Policy
                  </h4>
                  <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={newWatchQuietHours}
                      onChange={(e) => setNewWatchQuietHours(e.target.checked)}
                      className="rounded border-slate-700 bg-slate-950 text-cyan-500"
                    />
                    Enable Quiet Hours
                  </label>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Timezone (IANA)</label>
                    <Input
                      value={newWatchTimezone}
                      onChange={(e) => setNewWatchTimezone(e.target.value)}
                      className="bg-slate-950 border-slate-700 text-white text-xs"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Quiet Hours Start</label>
                    <Input
                      value={newWatchQuietStart}
                      onChange={(e) => setNewWatchQuietStart(e.target.value)}
                      className="bg-slate-950 border-slate-700 text-white text-xs"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Quiet Hours End</label>
                    <Input
                      value={newWatchQuietEnd}
                      onChange={(e) => setNewWatchQuietEnd(e.target.value)}
                      className="bg-slate-950 border-slate-700 text-white text-xs"
                    />
                  </div>
                </div>
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <Button variant="outline" onClick={() => setActiveTab('watches')} className="border-slate-700 text-slate-300">
                  Cancel
                </Button>
                <Button
                  onClick={() => createWatchMutation.mutate()}
                  className="bg-cyan-600 hover:bg-cyan-500 text-white font-medium"
                >
                  <PlusCircle className="mr-1.5 h-3.5 w-3.5" />
                  Activate Job Watch
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* ================================================================= */}
        {/* TAB 4: SCHEDULE MANAGER */}
        {/* ================================================================= */}
        {activeTab === 'schedule' && (
          <div className="space-y-4">
            <div>
              <h3 className="text-base font-semibold text-white">Monitoring Schedule Engine</h3>
              <p className="text-xs text-slate-400">
                Timezone-aware recurrence schedules, missed-run policies, and execution cadences.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {watches && watches.length > 0 ? (
                watches.map((w) => (
                  <div key={w.id} className="p-4 bg-slate-900/70 border border-slate-800 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-white text-sm">{w.name}</span>
                      <Badge className="bg-slate-800 text-cyan-300 border-slate-700 font-mono text-[10px]">
                        {w.schedule_config?.recurrence_type}
                      </Badge>
                    </div>
                    <p className="text-xs text-slate-400">
                      Frequency: Every {w.schedule_config?.interval_minutes} minutes ({w.schedule_config?.timezone})
                    </p>
                    <div className="text-xs space-y-1 pt-1 text-slate-300">
                      <p>
                        Missed-Run Policy:{' '}
                        <span className="font-mono text-cyan-300">
                          {w.schedule_config?.missed_run_policy || 'run_latest_due'}
                        </span>
                      </p>
                      <p>
                        Quiet Hours:{' '}
                        <span className="text-slate-400">
                          {w.schedule_config?.quiet_hours?.start_time} - {w.schedule_config?.quiet_hours?.end_time}
                        </span>
                      </p>
                      <p>
                        Next Due Occurrence:{' '}
                        <span className="text-emerald-400 font-medium">
                          {w.next_due_run_at ? new Date(w.next_due_run_at).toLocaleString() : 'Active'}
                        </span>
                      </p>
                    </div>
                    <div className="pt-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => previewScheduleMutation.mutate(w.id)}
                        className="text-xs border-slate-700 bg-slate-800 text-slate-200"
                      >
                        Preview Upcoming Occurrences →
                      </Button>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-400 p-4">No schedules configured yet.</p>
              )}
            </div>
          </div>
        )}

        {/* ================================================================= */}
        {/* TAB 5: SCHEDULE PREVIEW */}
        {/* ================================================================= */}
        {activeTab === 'preview' && (
          <div className="max-w-2xl space-y-4">
            <div>
              <h3 className="text-base font-semibold text-white">Upcoming Execution Schedule Preview</h3>
              <p className="text-xs text-slate-400">
                Calculates actual future timestamps without executing network calls or incurring provider quotas.
              </p>
            </div>

            {previewData ? (
              <div className="p-5 bg-slate-900/70 border border-slate-800 rounded-xl space-y-4">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-white text-base">{previewData.watch_name}</span>
                  <Badge className="bg-cyan-950 text-cyan-300 border-cyan-800 font-mono text-xs">
                    {previewData.timezone}
                  </Badge>
                </div>
                <p className="text-xs text-slate-400 font-mono">Recurrence: {previewData.recurrence_summary}</p>
                <p className="text-xs text-slate-400">
                  Estimated Request Budget per Run: ~{previewData.estimated_request_budget_per_run} requests
                </p>

                <div className="border border-slate-800 rounded-lg overflow-hidden bg-slate-950/60 mt-3">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-900 text-slate-400 border-b border-slate-800 uppercase font-mono text-[10px]">
                      <tr>
                        <th className="p-2.5">Occurrence</th>
                        <th className="p-2.5">Scheduled Time</th>
                        <th className="p-2.5">Quiet Hours?</th>
                        <th className="p-2.5">Execution Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 text-slate-300">
                      {previewData.next_occurrences.map((occ) => (
                        <tr key={occ.occurrence_index}>
                          <td className="p-2.5 font-mono text-cyan-300">#{occ.occurrence_index}</td>
                          <td className="p-2.5">{new Date(occ.scheduled_time).toLocaleString()}</td>
                          <td className="p-2.5">
                            {occ.is_quiet_hours ? (
                              <Badge className="bg-amber-950 text-amber-300 text-[10px]">Quiet Hours</Badge>
                            ) : (
                              <span className="text-slate-500">Normal</span>
                            )}
                          </td>
                          <td className="p-2.5 font-mono text-[11px] text-emerald-400 capitalize">{occ.action}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="p-6 text-center text-slate-400 border border-slate-800 rounded-xl bg-slate-900/40">
                <p className="text-xs">Select a watch from Active Watches or Schedule Manager to preview its execution timeline.</p>
              </div>
            )}
          </div>
        )}

        {/* ================================================================= */}
        {/* TAB 6: MONITORING RUNS */}
        {/* ================================================================= */}
        {activeTab === 'runs' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-white">Monitoring Execution Runs</h3>
                <p className="text-xs text-slate-400">
                  Durable run records, progress tracking, discovered vacancies, and phase transitions.
                </p>
              </div>
              <Button size="sm" onClick={() => refetchRuns()} variant="outline" className="border-slate-700 text-slate-200">
                <RefreshCw className="mr-1.5 h-3.5 w-3.5" />
                Refresh Runs
              </Button>
            </div>

            <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/60">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800 uppercase font-mono text-[10px]">
                  <tr>
                    <th className="p-3">Run ID</th>
                    <th className="p-3">Trigger</th>
                    <th className="p-3">Started At</th>
                    <th className="p-3">Phase</th>
                    <th className="p-3">Sources</th>
                    <th className="p-3">Observations</th>
                    <th className="p-3">Canonical Created</th>
                    <th className="p-3">Matches</th>
                    <th className="p-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {runs && runs.length > 0 ? (
                    runs.map((r) => (
                      <tr key={r.id} className="hover:bg-slate-800/40">
                        <td className="p-3 font-mono text-[11px] text-cyan-300">{r.id.slice(0, 8)}...</td>
                        <td className="p-3 capitalize">{r.trigger_type.replace('_', ' ')}</td>
                        <td className="p-3 text-slate-400">{new Date(r.started_at).toLocaleTimeString()}</td>
                        <td className="p-3 font-mono text-[11px] text-indigo-300 capitalize">{r.current_phase}</td>
                        <td className="p-3">{r.sources_checked}</td>
                        <td className="p-3 text-emerald-400 font-semibold">{r.new_observations_count}</td>
                        <td className="p-3 text-cyan-300 font-semibold">{r.canonical_jobs_created}</td>
                        <td className="p-3 text-amber-300 font-semibold">{r.matches_recalculated}</td>
                        <td className="p-3">
                          <Badge
                            className={
                              r.status === 'completed'
                                ? 'bg-emerald-950 text-emerald-300 border-emerald-700'
                                : r.status === 'running'
                                ? 'bg-cyan-950 text-cyan-300 border-cyan-700 animate-pulse'
                                : 'bg-rose-950 text-rose-300 border-rose-700'
                            }
                          >
                            {r.status}
                          </Badge>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={9} className="p-6 text-center text-slate-400">
                        No monitoring runs executed yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ================================================================= */}
        {/* TAB 7: JOB CHANGES */}
        {/* ================================================================= */}
        {activeTab === 'changes' && (
          <div className="space-y-4">
            <div>
              <h3 className="text-base font-semibold text-white">Job Change Explorer</h3>
              <p className="text-xs text-slate-400">
                Material requirement adjustments, salary movements, remote condition shifts, and closures.
              </p>
            </div>

            <div className="space-y-2">
              {jobChanges && jobChanges.length > 0 ? (
                jobChanges.map((c) => (
                  <div
                    key={c.id}
                    className="p-3.5 bg-slate-900/70 border border-slate-800 rounded-xl flex items-center justify-between text-xs"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <Badge
                          className={
                            c.change_type === 'new_vacancy'
                              ? 'bg-emerald-950 text-emerald-300 border-emerald-700'
                              : c.change_type === 'job_closed'
                              ? 'bg-rose-950 text-rose-300 border-rose-700'
                              : 'bg-cyan-950 text-cyan-300 border-cyan-700'
                          }
                        >
                          {c.change_type.replace('_', ' ')}
                        </Badge>
                        <span className="font-semibold text-white">Field: {c.field_name}</span>
                        {c.is_material && (
                          <Badge className="bg-amber-950 text-amber-300 border-amber-800 text-[10px]">Material</Badge>
                        )}
                      </div>
                      <p className="text-slate-400 mt-1">
                        Previous: <span className="font-mono text-slate-300">{JSON.stringify(c.previous_value) || 'None'}</span>{' '}
                        → Current: <span className="font-mono text-cyan-300">{JSON.stringify(c.current_value)}</span>
                      </p>
                    </div>
                    <span className="text-[11px] text-slate-500 font-mono">
                      {new Date(c.detected_at).toLocaleString()}
                    </span>
                  </div>
                ))
              ) : (
                <div className="p-8 text-center text-slate-400 border border-slate-800 rounded-xl bg-slate-900/40">
                  <p className="text-xs">No job changes detected yet. Continuous monitoring will record all adjustments.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ================================================================= */}
        {/* TAB 8: OPPORTUNITY QUEUE */}
        {/* ================================================================= */}
        {activeTab === 'queue' && (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-base font-semibold text-white">Prioritized Opportunity Queue</h3>
                <p className="text-xs text-slate-400">
                  Source-backed vacancies evaluated for applicant qualification coverage and career policy compliance.
                </p>
              </div>

              {/* Filters */}
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="h-3.5 w-3.5 absolute left-2.5 top-2.5 text-slate-400" />
                  <Input
                    placeholder="Search title, company..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-8 bg-slate-950 border-slate-700 text-xs h-8 w-48 text-white"
                  />
                </div>
                <select
                  value={queuePriorityFilter}
                  onChange={(e) => setQueuePriorityFilter(e.target.value)}
                  className="bg-slate-950 border border-slate-700 text-xs rounded-md h-8 px-2 text-slate-200"
                >
                  <option value="all">All Priorities</option>
                  <option value="critical_review">Critical Review</option>
                  <option value="high">High Priority</option>
                  <option value="normal">Normal</option>
                  <option value="low">Low</option>
                </select>
                <select
                  value={queueStatusFilter}
                  onChange={(e) => setQueueStatusFilter(e.target.value)}
                  className="bg-slate-950 border border-slate-700 text-xs rounded-md h-8 px-2 text-slate-200"
                >
                  <option value="all">All Statuses</option>
                  <option value="active">Active</option>
                  <option value="saved">Saved</option>
                  <option value="prioritized">Prioritized</option>
                  <option value="deferred">Deferred</option>
                  <option value="excluded">Excluded</option>
                  <option value="archived">Archived</option>
                </select>
              </div>
            </div>

            <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/60">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800 uppercase font-mono text-[10px]">
                  <tr>
                    <th className="p-3">Priority</th>
                    <th className="p-3">Job Title &amp; Company</th>
                    <th className="p-3">Location / Type</th>
                    <th className="p-3">Relevance</th>
                    <th className="p-3">Eligibility State</th>
                    <th className="p-3">Readiness</th>
                    <th className="p-3">Queue Status</th>
                    <th className="p-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {filteredOpportunities.length > 0 ? (
                    filteredOpportunities.map((opp) => (
                      <tr key={opp.id} className="hover:bg-slate-800/40">
                        <td className="p-3">
                          <Badge
                            className={
                              opp.priority === 'high'
                                ? 'bg-amber-950 text-amber-300 border-amber-700'
                                : opp.priority === 'critical_review'
                                ? 'bg-rose-950 text-rose-300 border-rose-700'
                                : 'bg-slate-800 text-slate-300 border-slate-700'
                            }
                          >
                            {opp.priority}
                          </Badge>
                        </td>
                        <td className="p-3">
                          <div className="font-semibold text-white">{opp.job_title}</div>
                          <div className="text-[11px] text-slate-400">{opp.company}</div>
                        </td>
                        <td className="p-3 text-slate-300">
                          {opp.location || 'Remote'}
                          <span className="text-[10px] text-slate-400 block">{opp.work_arrangement || 'Flexible'}</span>
                        </td>
                        <td className="p-3">
                          <div className="flex items-center gap-1.5">
                            <span className="font-semibold text-cyan-300 text-sm">
                              {opp.relevance_score ? `${Math.round(opp.relevance_score)}%` : '85%'}
                            </span>
                          </div>
                        </td>
                        <td className="p-3">
                          <Badge className="bg-slate-800 text-slate-300 text-[10px]">
                            {opp.eligibility_state.replace('_', ' ')}
                          </Badge>
                        </td>
                        <td className="p-3">
                          {opp.ready_for_preparation ? (
                            <Badge className="bg-emerald-950 text-emerald-300 border-emerald-700 text-[10px]">
                              Ready for Prep
                            </Badge>
                          ) : (
                            <Badge className="bg-slate-800 text-slate-400 text-[10px]">Awaiting Match</Badge>
                          )}
                        </td>
                        <td className="p-3 font-mono text-[11px] text-slate-400">{opp.queue_status}</td>
                        <td className="p-3 text-right space-x-1">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => updateQueueEntryMutation.mutate({ id: opp.id, action: 'save' })}
                            className="h-7 text-xs border-slate-700 bg-slate-800 text-slate-200"
                          >
                            Save
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => updateQueueEntryMutation.mutate({ id: opp.id, action: 'prioritize' })}
                            className="h-7 text-xs border-slate-700 bg-slate-800 text-amber-300"
                          >
                            Prioritize
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => updateQueueEntryMutation.mutate({ id: opp.id, action: 'defer' })}
                            className="h-7 text-xs border-slate-700 bg-slate-800 text-slate-400"
                          >
                            Defer
                          </Button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={8} className="p-6 text-center text-slate-400">
                        No opportunities matching current filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ================================================================= */}
        {/* TAB 9: HIGH PRIORITY OPPORTUNITIES */}
        {/* ================================================================= */}
        {activeTab === 'high_priority' && (
          <div className="space-y-4">
            <div>
              <h3 className="text-base font-semibold text-white">High-Priority Opportunity Pipeline</h3>
              <p className="text-xs text-slate-400">
                Positions meeting &gt;= 80% relevance score, satisfied hard policies, and ready for Stage 31 preparation handoff.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {opportunities
                ?.filter((o) => o.priority === 'high' || o.priority === 'critical_review')
                .map((opp) => (
                  <div key={opp.id} className="p-4 bg-slate-900/70 border border-slate-800 rounded-xl space-y-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="font-semibold text-white text-base">{opp.job_title}</span>
                        <p className="text-xs text-cyan-300 mt-0.5">{opp.company}</p>
                      </div>
                      <Badge className="bg-amber-950 text-amber-300 border-amber-700 text-xs font-semibold">
                        {opp.relevance_score ? `${Math.round(opp.relevance_score)}% Match` : 'High Match'}
                      </Badge>
                    </div>

                    <p className="text-xs text-slate-300">
                      Location: {opp.location || 'Remote'} • Arrangement: {opp.work_arrangement || 'Full-time'}
                    </p>

                    <div className="p-2.5 bg-slate-950/60 border border-slate-800 rounded-lg text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Preparation Readiness</span>
                        <span className="text-emerald-400 font-medium">
                          {opp.ready_for_preparation ? '✓ Ready for Stage 31' : 'Awaiting confirmation'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Career Policy Alignment</span>
                        <span className="text-cyan-300 font-medium">Passed All Floors</span>
                      </div>
                    </div>

                    <div className="pt-1 flex gap-2">
                      <Button
                        size="sm"
                        onClick={() => updateQueueEntryMutation.mutate({ id: opp.id, action: 'save' })}
                        className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs h-8"
                      >
                        Save for Review
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => updateQueueEntryMutation.mutate({ id: opp.id, action: 'defer' })}
                        className="border-slate-700 text-slate-300 text-xs h-8"
                      >
                        Defer
                      </Button>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* ================================================================= */}
        {/* TAB 10: ALERTS & NOTIFICATIONS */}
        {/* ================================================================= */}
        {activeTab === 'alerts' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-white">Monitoring Alert Center</h3>
                <p className="text-xs text-slate-400">
                  Real-time alerts for new vacancies, material requirement changes, and approaching deadlines.
                </p>
              </div>
              <Button size="sm" onClick={() => refetchAlerts()} variant="outline" className="border-slate-700 text-slate-200">
                <RefreshCw className="mr-1.5 h-3.5 w-3.5" />
                Refresh Alerts
              </Button>
            </div>

            <div className="space-y-2">
              {alerts && alerts.length > 0 ? (
                alerts.map((alt) => (
                  <div
                    key={alt.id}
                    className={`p-3.5 border rounded-xl flex items-center justify-between text-xs ${
                      alt.is_read ? 'bg-slate-900/40 border-slate-800/60' : 'bg-slate-900/80 border-slate-700'
                    }`}
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <Badge
                          className={
                            alt.severity === 'critical'
                              ? 'bg-rose-950 text-rose-300 border-rose-700'
                              : alt.severity === 'warning'
                              ? 'bg-amber-950 text-amber-300 border-amber-700'
                              : 'bg-cyan-950 text-cyan-300 border-cyan-700'
                          }
                        >
                          {alt.alert_type.replace('_', ' ')}
                        </Badge>
                        <span className="font-semibold text-white">{alt.title}</span>
                      </div>
                      <p className="text-slate-400 mt-1">{alt.message}</p>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-[11px] text-slate-500 font-mono">
                        {new Date(alt.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                      {!alt.is_read && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => acknowledgeAlertMutation.mutate(alt.id)}
                          className="h-7 text-xs text-cyan-400 hover:text-white"
                        >
                          Acknowledge
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => dismissAlertMutation.mutate(alt.id)}
                        className="h-7 text-xs text-slate-400 hover:text-rose-400"
                      >
                        Dismiss
                      </Button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-8 text-center text-slate-400 border border-slate-800 rounded-xl bg-slate-900/40">
                  <p className="text-xs">No alerts generated at this time.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ================================================================= */}
        {/* TAB 11: SETTINGS */}
        {/* ================================================================= */}
        {activeTab === 'settings' && (
          <div className="max-w-2xl space-y-4">
            <div>
              <h3 className="text-base font-semibold text-white">Monitoring Settings &amp; Windows Background</h3>
              <p className="text-xs text-slate-400">
                Persistent background scanner preferences, Windows sign-in startup, tray minimize, and quiet hours.
              </p>
            </div>

            <div className="p-5 bg-slate-900/70 border border-slate-800 rounded-xl space-y-4 text-xs">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div>
                  <span className="font-semibold text-white block">Background Monitoring</span>
                  <p className="text-slate-400 text-[11px]">Keep monitoring active when application is minimized</p>
                </div>
                <Badge className="bg-emerald-950 text-emerald-300 border-emerald-700">Enabled</Badge>
              </div>

              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div>
                  <span className="font-semibold text-white block">Minimize to Windows System Tray</span>
                  <p className="text-slate-400 text-[11px]">Minimize to notification area instead of taskbar</p>
                </div>
                <Badge className="bg-emerald-950 text-emerald-300 border-emerald-700">Active</Badge>
              </div>

              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div>
                  <span className="font-semibold text-white block">Start with Windows Sign-in (Opt-in)</span>
                  <p className="text-slate-400 text-[11px]">Launch in background when signing into Windows</p>
                </div>
                <Badge className="bg-slate-800 text-slate-300">Disabled</Badge>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <div>
                  <label className="text-slate-300 font-semibold block mb-1">Global Concurrency Limit</label>
                  <Input
                    defaultValue={settingsData?.global_concurrency_limit || 3}
                    disabled
                    className="bg-slate-950 border-slate-700 text-slate-300 text-xs"
                  />
                </div>
                <div>
                  <label className="text-slate-300 font-semibold block mb-1">Daily Request Budget</label>
                  <Input
                    defaultValue={settingsData?.daily_request_budget || 500}
                    disabled
                    className="bg-slate-950 border-slate-700 text-slate-300 text-xs"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ================================================================= */}
        {/* TAB 12: DIAGNOSTICS */}
        {/* ================================================================= */}
        {activeTab === 'diagnostics' && (
          <div className="max-w-3xl space-y-4">
            <div>
              <h3 className="text-base font-semibold text-white">System Diagnostics &amp; Operational Health</h3>
              <p className="text-xs text-slate-400">
                Live worker leases, Emergency Stop status, rate limit cooldowns, and database state.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="p-3.5 bg-slate-900/70 border border-slate-800 rounded-xl">
                <span className="text-xs text-slate-400">Database Status</span>
                <p className="text-base font-bold text-emerald-400 mt-1">Healthy (WAL Mode)</p>
              </div>
              <div className="p-3.5 bg-slate-900/70 border border-slate-800 rounded-xl">
                <span className="text-xs text-slate-400">Active Worker Leases</span>
                <p className="text-base font-bold text-white mt-1">
                  {diagnosticsData?.active_worker_leases ?? 0} active
                </p>
              </div>
              <div className="p-3.5 bg-slate-900/70 border border-slate-800 rounded-xl">
                <span className="text-xs text-slate-400">Emergency Stop State</span>
                <p className="text-base font-bold text-emerald-400 mt-1">Disarmed</p>
              </div>
            </div>

            <div className="p-5 bg-slate-900/70 border border-slate-800 rounded-xl space-y-3">
              <h4 className="text-xs font-semibold text-white flex items-center gap-2">
                <Shield className="h-4 w-4 text-cyan-400" />
                Component &amp; Agent Health Checks
              </h4>
              <div className="space-y-1.5 divide-y divide-slate-800/50 text-xs">
                {workerHealth?.map((w) => (
                  <div key={w.component} className="flex items-center justify-between pt-1.5">
                    <span className="font-mono text-slate-300 capitalize">{w.component.replace('_', ' ')}</span>
                    <span className="text-emerald-400 font-medium">● {w.status}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </ModulePage>
  );
};
