/**
 * Tab: Discovery Overview (Stage 26).
 * Shows high-level statistics across sources, observations, and health.
 */

import * as React from 'react';
import {
  Globe,
  Radio,
  Layers,
  CheckCircle2,
  Clock,
  Play,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { DiscoveryOverviewStats, JobSourceConfig, JobSourceObservation } from '@autonom/shared-types';

interface DiscoveryOverviewTabProps {
  stats: DiscoveryOverviewStats | null;
  sources: JobSourceConfig[];
  recentPostings: JobSourceObservation[];
  onTriggerSearch: () => void;
  onNavigateTab: (tabId: string) => void;
}

export const DiscoveryOverviewTab: React.FC<DiscoveryOverviewTabProps> = ({
  stats,
  sources,
  recentPostings,
  onTriggerSearch,
  onNavigateTab,
}) => {
  return (
    <div className="space-y-6">
      {/* Top Action Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-lg border bg-gradient-to-r from-blue-950/20 via-background to-background">
        <div>
          <h3 className="text-base font-semibold">Multi-Source Job Discovery Engine</h3>
          <p className="text-sm text-muted-foreground">
            Discover verified vacancies from official Greenhouse, Lever, Ashby, USAJOBS, and approved employer portals.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={() => onNavigateTab('sources')}>
            <Radio className="w-4 h-4 mr-2" />
            Manage Sources
          </Button>
          <Button size="sm" onClick={onTriggerSearch}>
            <Play className="w-4 h-4 mr-2" />
            Run Discovery
          </Button>
        </div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs uppercase tracking-wider font-semibold">Configured Sources</CardDescription>
            <CardTitle className="text-2xl font-bold flex items-center justify-between">
              <span>{stats?.total_sources ?? sources.length}</span>
              <Globe className="w-5 h-5 text-blue-500" />
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            {stats?.enabled_sources ?? sources.filter((s) => s.is_enabled).length} sources currently enabled
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs uppercase tracking-wider font-semibold">Observed Postings</CardDescription>
            <CardTitle className="text-2xl font-bold flex items-center justify-between">
              <span>{stats?.total_observations ?? recentPostings.length}</span>
              <Layers className="w-5 h-5 text-purple-500" />
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            {stats?.active_postings_count ?? recentPostings.filter((p) => p.availability === 'available').length} available vacancies
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs uppercase tracking-wider font-semibold">Healthy Providers</CardDescription>
            <CardTitle className="text-2xl font-bold flex items-center justify-between">
              <span>
                {Math.max(0, (stats?.total_sources ?? sources.length) - (stats?.failed_sources_count ?? 0))}
              </span>
              <CheckCircle2 className="w-5 h-5 text-emerald-500" />
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            {stats?.failed_sources_count ? `${stats.failed_sources_count} source(s) with errors` : 'All endpoints operational'}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs uppercase tracking-wider font-semibold">Active Tasks</CardDescription>
            <CardTitle className="text-2xl font-bold flex items-center justify-between">
              <span>{stats?.active_tasks_count ?? 0}</span>
              <Clock className="w-5 h-5 text-amber-500" />
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            Bounded background synchronization
          </CardContent>
        </Card>
      </div>

      {/* Connected Source Roster & Recent Observations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Connected Sources */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <div>
              <CardTitle className="text-sm font-semibold">Connected Job Sources</CardTitle>
              <CardDescription className="text-xs">Direct API connections & public boards</CardDescription>
            </div>
            <Button variant="ghost" size="sm" className="text-xs" onClick={() => onNavigateTab('sources')}>
              View All
            </Button>
          </CardHeader>
          <CardContent className="space-y-3">
            {sources.slice(0, 5).map((source) => (
              <div key={source.id} className="flex items-center justify-between p-3 rounded-md border text-sm">
                <div className="space-y-1">
                  <div className="font-medium flex items-center gap-2">
                    {source.name}
                    {source.is_enabled ? (
                      <Badge variant="outline" className="text-[10px] text-emerald-600 border-emerald-300">
                        Active
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-[10px] text-muted-foreground">
                        Disabled
                      </Badge>
                    )}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Provider: {source.connector_id} • Domain: {source.official_domain}
                  </div>
                </div>
                <Badge variant="neutral" className="capitalize text-xs">
                  {source.category.replace(/_/g, ' ')}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Recently Discovered Vacancies */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <div>
              <CardTitle className="text-sm font-semibold">Recently Discovered Opportunities</CardTitle>
              <CardDescription className="text-xs">Latest observed postings with Stage 25 policy pre-filter</CardDescription>
            </div>
            <Button variant="ghost" size="sm" className="text-xs" onClick={() => onNavigateTab('jobs')}>
              View All
            </Button>
          </CardHeader>
          <CardContent className="space-y-3">
            {recentPostings.length === 0 ? (
              <div className="text-center py-8 text-sm text-muted-foreground">
                No job postings observed yet. Run a discovery run to populate listings.
              </div>
            ) : (
              recentPostings.slice(0, 5).map((job) => (
                <div key={job.id} className="p-3 rounded-md border space-y-1 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="font-medium line-clamp-1">{job.title}</span>
                    <Badge
                      variant="outline"
                      className={`text-[10px] ${
                        job.prefilter_status === 'prefilter_accepted'
                          ? 'text-emerald-600 border-emerald-300'
                          : job.prefilter_status === 'prefilter_rejected'
                          ? 'text-rose-600 border-rose-300'
                          : 'text-amber-600 border-amber-300'
                      }`}
                    >
                      {job.prefilter_status.replace(/_/g, ' ')}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <span>{job.employer}</span>
                    <span>•</span>
                    <span>{job.location.city || (job.location.is_remote ? 'Remote' : 'Location Unspecified')}</span>
                    {job.compensation?.min_amount && (
                      <>
                        <span>•</span>
                        <span className="text-emerald-700 dark:text-emerald-400 font-medium">
                          ${(job.compensation.min_amount / 1000).toFixed(0)}k - ${(job.compensation.max_amount! / 1000).toFixed(0)}k
                        </span>
                      </>
                    )}
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
