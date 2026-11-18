/**
 * GitHub Diagnostics Tab: Subsystem telemetry, rate limit tracking, sync jobs history, and cache metrics.
 */

import * as React from 'react';
import {
  Activity,
  Clock,
  Database,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type {
  GitHubDiagnostics,
  SyncJobRecord,
} from '@autonom/shared-types';

interface GitHubDiagnosticsTabProps {
  diagnostics: GitHubDiagnostics | null;
  syncJobs: SyncJobRecord[];
  onRefresh: () => void;
  isLoading: boolean;
}

export const GitHubDiagnosticsTab: React.FC<GitHubDiagnosticsTabProps> = ({
  diagnostics,
  syncJobs,
  onRefresh,
  isLoading,
}) => {
  return (
    <div className="space-y-6">
      {/* Top Action Bar */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold tracking-tight">GitHub Subsystem Diagnostics</h3>
          <p className="text-xs text-muted-foreground">
            Live telemetry on API quota consumption, ETag cache status, and background sync job execution history.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={onRefresh} disabled={isLoading} className="text-xs gap-1.5 h-8">
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} /> Refresh Telemetry
        </Button>
      </div>

      {/* Diagnostics Overview Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Rate Limit Remaining
            </CardTitle>
            <Clock className="h-4 w-4 text-cyan" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {diagnostics?.rate_limit_remaining ?? 5000}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Limit: {diagnostics?.rate_limit_limit ?? 5000} requests/hr
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              ETag Cached Entries
            </CardTitle>
            <Database className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{diagnostics?.cached_etag_entries ?? 0}</div>
            <p className="text-xs text-muted-foreground mt-1">304 Not Modified optimization</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Analyzed Repos
            </CardTitle>
            <CheckCircle2 className="h-4 w-4 text-status-success" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-status-success">
              {diagnostics?.total_analyzed_repositories ?? 0}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Of {diagnostics?.total_selected_repositories ?? 0} selected
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Sync Errors
            </CardTitle>
            <AlertTriangle className="h-4 w-4 text-status-warning" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-status-warning">
              {diagnostics?.sync_error_count ?? 0}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Failed analysis jobs</p>
          </CardContent>
        </Card>
      </div>

      {/* Sync Jobs Execution History Table */}
      <Card className="border-border/80">
        <CardHeader>
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <Activity className="h-4 w-4 text-primary" /> Analysis & Sync Execution History ({syncJobs.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {syncJobs.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead>
                  <tr className="border-b border-border/60 text-muted-foreground">
                    <th className="py-2 px-3 font-semibold">Job ID</th>
                    <th className="py-2 px-3 font-semibold">Repository</th>
                    <th className="py-2 px-3 font-semibold">Status</th>
                    <th className="py-2 px-3 font-semibold">Files</th>
                    <th className="py-2 px-3 font-semibold">Data Size</th>
                    <th className="py-2 px-3 font-semibold">API Calls</th>
                    <th className="py-2 px-3 font-semibold">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/40">
                  {syncJobs.map((job) => (
                    <tr key={job.job_id} className="hover:bg-secondary/20 transition-colors">
                      <td className="py-2.5 px-3 font-mono font-medium text-foreground">
                        {job.job_id}
                      </td>
                      <td className="py-2.5 px-3 font-semibold">{job.repo_name}</td>
                      <td className="py-2.5 px-3">
                        <Badge
                          variant="neutral"
                          className={`text-[10px] py-0 capitalize ${
                            job.status === 'completed'
                              ? 'bg-status-success/10 text-status-success'
                              : job.status === 'syncing'
                              ? 'bg-cyan/10 text-cyan animate-pulse'
                              : job.status === 'failed'
                              ? 'bg-status-error/10 text-status-error'
                              : 'bg-muted text-muted-foreground'
                          }`}
                        >
                          {job.status}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3">{job.files_analyzed}</td>
                      <td className="py-2.5 px-3">
                        {(job.bytes_analyzed / 1024).toFixed(1)} KB
                      </td>
                      <td className="py-2.5 px-3">{job.api_calls_made}</td>
                      <td className="py-2.5 px-3 text-muted-foreground">
                        {new Date(job.started_at).toLocaleTimeString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center text-xs text-muted-foreground">
              No analysis jobs have run yet. Select a repository and click Run Analysis.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
