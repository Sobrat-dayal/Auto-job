import * as React from 'react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useBackendHealth } from '@/hooks/use-backend-health';
import { useDashboardOverview, useDashboardTasks, useLiveEventStream } from '@/hooks/use-dashboard';
import { PageContainer } from '@/components/layout/PageContainer';
import { DashboardHeader } from './DashboardHeader';
import { DashboardKpiGrid } from './DashboardKpiGrid';
import { AgentOperationsPanel } from './AgentOperationsPanel';
import { JobDiscoveryOverview } from './JobDiscoveryOverview';
import { ApplicationPipeline } from './ApplicationPipeline';
import { LiveTaskQueue } from './LiveTaskQueue';
import { ActivityFeed } from './ActivityFeed';
import { ProductivityChart } from './ProductivityChart';
import { SystemHealthPanel } from './SystemHealthPanel';
import { PendingActionsPanel } from './PendingActionsPanel';
import { QuickActions } from './QuickActions';

export const DashboardView: React.FC = () => {
  const navigate = useNavigate();
  const { connectionStatus } = useBackendHealth();
  const isConnected = connectionStatus === 'connected';

  // Real-time Overview & Tasks data via TanStack Query
  const {
    data: overview,
    isLoading: isOverviewLoading,
    isFetching: isOverviewFetching,
    refetch: refetchOverview,
    dataUpdatedAt,
  } = useDashboardOverview();

  const {
    data: tasks = [],
    isLoading: isTasksLoading,
    refetch: refetchTasks,
  } = useDashboardTasks();

  // SSE Live Event Streaming
  const { events, status: streamStatus, clearEvents } = useLiveEventStream(100);

  // State for Live Task Queue filter tab
  const [taskFilter, setTaskFilter] = useState<string>('all');

  // Unified Refresh
  const handleRefresh = React.useCallback(() => {
    refetchOverview();
    refetchTasks();
  }, [refetchOverview, refetchTasks]);

  // Task filter selection (e.g. from KPI cards)
  const handleSelectFilter = (filter: string) => {
    setTaskFilter(filter.toLowerCase());
    // Smooth scroll to task queue
    const queueElement = document.getElementById('live-task-queue-section');
    if (queueElement) {
      queueElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  };

  const failedTasks = React.useMemo(() => {
    return tasks.filter((t) => t.state === 'failed');
  }, [tasks]);

  return (
    <PageContainer className="space-y-6">
      {/* 1. Header & Live System Status */}
      <DashboardHeader
        overview={overview}
        isLoading={isOverviewLoading}
        isFetching={isOverviewFetching}
        isConnected={isConnected}
        onRefresh={handleRefresh}
        lastUpdated={dataUpdatedAt ? new Date(dataUpdatedAt) : undefined}
      />

      {/* 2. Key Performance Indicators (KPIs) */}
      <DashboardKpiGrid
        overview={overview}
        isLoading={isOverviewLoading}
        isConnected={isConnected}
        onSelectTaskFilter={handleSelectFilter}
        onNavigateToRecruitment={() => navigate('/recruitment')}
      />

      {/* 3. Autonomous Agent Fleet & Worker Pool */}
      <AgentOperationsPanel
        agents={overview?.agents || []}
        workers={overview?.workers}
        isConnected={isConnected}
        onInspectAgent={(agentId) => navigate(`/agents?id=${agentId}`)}
        onNavigateToDiagnostics={() => navigate('/diagnostics')}
      />

      {/* 4. Recruitment Pipeline Overview (Job Discovery & 10-Stage Pipeline) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <JobDiscoveryOverview
          recruitment={overview?.recruitment}
          isConnected={isConnected}
          onNavigateToRecruitment={() => navigate('/recruitment')}
        />
        <ApplicationPipeline
          recruitment={overview?.recruitment}
          isConnected={isConnected}
          onNavigateToApplications={() => navigate('/applications')}
        />
      </div>

      {/* 5. Live Task Execution Queue & Real-Time Activity Feed */}
      <div id="live-task-queue-section" className="grid grid-cols-1 xl:grid-cols-12 gap-4">
        <div className="xl:col-span-7">
          <LiveTaskQueue
            tasks={tasks}
            isLoading={isTasksLoading}
            onRefresh={refetchTasks}
            activeFilter={taskFilter}
            onFilterChange={setTaskFilter}
            onNavigateToDiagnostics={() => navigate('/diagnostics')}
          />
        </div>
        <div className="xl:col-span-5">
          <ActivityFeed
            events={events}
            streamStatus={streamStatus}
            onClear={clearEvents}
            onSelectTask={(_taskId) => {
              // Could open detail or highlight task
            }}
          />
        </div>
      </div>

      {/* 6. Operational Analytics, Subsystem Health & Pending Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <ProductivityChart />
        <SystemHealthPanel
          overview={overview}
          isConnected={isConnected}
          onNavigateToDiagnostics={() => navigate('/diagnostics')}
          onNavigateToDesktop={() => navigate('/desktop-diagnostics')}
          onNavigateToStorage={() => navigate('/storage')}
        />
        <PendingActionsPanel
          failedTasks={failedTasks}
          onSelectTask={(_taskId) => {
            setTaskFilter('failed');
            const queueElement = document.getElementById('live-task-queue-section');
            if (queueElement) {
              queueElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
          }}
          onNavigateToDiagnostics={() => navigate('/diagnostics')}
        />
      </div>

      {/* 7. Quick Operations & Direct Task Dispatch */}
      <QuickActions
        onRefresh={handleRefresh}
        onNavigate={(path) => navigate(path)}
        onTaskDispatched={() => {
          refetchTasks();
          refetchOverview();
        }}
      />
    </PageContainer>
  );
};
