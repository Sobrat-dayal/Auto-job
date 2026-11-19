/**
 * Stage 26: Multi-Source Job Discovery Engine.
 * Master Desktop Workspace Container.
 */

import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Compass,
  Radio,
  Building2,
  Search,
  Briefcase,
  PlusCircle,
  Clock,
  Activity,
  Sliders,
} from 'lucide-react';
import { ModulePage, ModuleHeader, ModuleTabs } from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type {
  DiscoveryOverviewStats,
  JobSourceConfig,
  ConnectorManifest,
  EmployerCareerSource,
  JobSourceObservation,
  DiscoveryTaskRecord,
  JobSourceHealth,
  DiscoverySettingsConfig,
} from '@autonom/shared-types';

import { DiscoveryOverviewTab } from './tabs/DiscoveryOverviewTab';
import { SourcesManagerTab } from './tabs/SourcesManagerTab';
import { EmployerSourcesTab } from './tabs/EmployerSourcesTab';
import { SearchAndDiscoverTab } from './tabs/SearchAndDiscoverTab';
import { DiscoveredJobsTab } from './tabs/DiscoveredJobsTab';
import { JobImportTab } from './tabs/JobImportTab';
import { DiscoveryTasksTab } from './tabs/DiscoveryTasksTab';
import { SourceHealthTab } from './tabs/SourceHealthTab';
import { DiscoverySettingsTab } from './tabs/DiscoverySettingsTab';

export const JobDiscoveryWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState<string>('overview');

  // 1. Fetch Overview Stats
  const { data: stats = null, refetch: refetchStats } = useQuery<DiscoveryOverviewStats>({
    queryKey: ['discovery-overview-stats'],
    queryFn: () => apiClient.getDiscoveryOverview(),
    refetchInterval: 15000,
  });

  // 2. Fetch Sources
  const { data: sources = [], refetch: refetchSources } = useQuery<JobSourceConfig[]>({
    queryKey: ['discovery-sources-list'],
    queryFn: () => apiClient.listJobSources(),
  });

  // 3. Fetch Connectors
  const { data: connectors = [] } = useQuery<ConnectorManifest[]>({
    queryKey: ['discovery-connectors-manifests'],
    queryFn: () => apiClient.listDiscoveryConnectors(),
  });

  // 4. Fetch Employer Career Sources
  const { data: employers = [], refetch: refetchEmployers } = useQuery<EmployerCareerSource[]>({
    queryKey: ['discovery-employer-sources'],
    queryFn: () => apiClient.listEmployerCareerSources(),
  });

  // 5. Fetch Observed Postings
  const { data: postings = [], refetch: refetchPostings } = useQuery<JobSourceObservation[]>({
    queryKey: ['discovery-postings-list'],
    queryFn: () => apiClient.listJobObservations({ limit: 200 }),
    refetchInterval: 20000,
  });

  // 6. Fetch Tasks
  const { data: tasks = [], refetch: refetchTasks } = useQuery<DiscoveryTaskRecord[]>({
    queryKey: ['discovery-tasks-list'],
    queryFn: () => apiClient.listDiscoveryTasks(50),
    refetchInterval: 5000,
  });

  // 7. Fetch Health
  const { data: diagnostics = null, refetch: refetchDiagnostics } = useQuery<Record<string, any>>({
    queryKey: ['discovery-diagnostics'],
    queryFn: () => apiClient.getDiscoveryDiagnostics(),
    refetchInterval: 15000,
  });

  const healthList: JobSourceHealth[] = diagnostics?.source_health || [];

  // 8. Fetch Settings
  const { data: settings = null, refetch: refetchSettings } = useQuery<DiscoverySettingsConfig>({
    queryKey: ['discovery-settings'],
    queryFn: () => apiClient.getDiscoverySettings(),
  });

  const refreshAll = () => {
    refetchStats();
    refetchSources();
    refetchEmployers();
    refetchPostings();
    refetchTasks();
    refetchDiagnostics();
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Compass },
    { id: 'sources', label: 'Job Sources', icon: Radio, badge: sources.length },
    { id: 'employers', label: 'Employer Portals', icon: Building2, badge: employers.length },
    { id: 'search', label: 'Search & Discover', icon: Search },
    { id: 'jobs', label: 'Discovered Jobs', icon: Briefcase, badge: postings.length },
    { id: 'import', label: 'Single Job Import', icon: PlusCircle },
    { id: 'tasks', label: 'Tasks Monitor', icon: Clock, badge: tasks.filter((t) => t.status === 'running').length || undefined },
    { id: 'health', label: 'Health & Telemetry', icon: Activity },
    { id: 'settings', label: 'Settings', icon: Sliders },
  ];

  return (
    <ModulePage>
      <ModuleHeader
        title="Multi-Source Job Discovery Engine"
        description="Official ATS APIs (Greenhouse, Lever, Ashby, USAJOBS), employer career sites, structured feeds, and URL imports."
        icon={Compass}
        actions={
          <div className="flex items-center gap-2">
            <Badge variant="neutral" className="text-xs bg-emerald-950/20 text-emerald-400 border-emerald-800">
              Stage 26 Active
            </Badge>
            <Badge variant="neutral" className="text-xs">
              {sources.filter((s) => s.is_enabled).length} Active Sources
            </Badge>
          </div>
        }
      />

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="mt-6">
        {activeTab === 'overview' && (
          <DiscoveryOverviewTab
            stats={stats}
            sources={sources}
            recentPostings={postings}
            onTriggerSearch={() => setActiveTab('search')}
            onNavigateTab={(tabId) => setActiveTab(tabId)}
          />
        )}

        {activeTab === 'sources' && (
          <SourcesManagerTab
            sources={sources}
            connectors={connectors}
            onRefreshList={refreshAll}
          />
        )}

        {activeTab === 'employers' && (
          <EmployerSourcesTab
            employers={employers}
            onRefresh={refetchEmployers}
          />
        )}

        {activeTab === 'search' && (
          <SearchAndDiscoverTab
            sources={sources}
            onTaskLaunched={() => {
              refreshAll();
              setActiveTab('tasks');
            }}
          />
        )}

        {activeTab === 'jobs' && (
          <DiscoveredJobsTab
            postings={postings}
            sources={sources}
          />
        )}

        {activeTab === 'import' && (
          <JobImportTab
            onImportSuccess={() => {
              refreshAll();
              setActiveTab('jobs');
            }}
          />
        )}

        {activeTab === 'tasks' && (
          <DiscoveryTasksTab
            tasks={tasks}
            onRefresh={refetchTasks}
          />
        )}

        {activeTab === 'health' && (
          <SourceHealthTab
            healthList={healthList}
            sources={sources}
            onRefresh={refetchDiagnostics}
          />
        )}

        {activeTab === 'settings' && (
          <DiscoverySettingsTab
            settings={settings}
            onRefresh={refetchSettings}
          />
        )}
      </div>
    </ModulePage>
  );
};
