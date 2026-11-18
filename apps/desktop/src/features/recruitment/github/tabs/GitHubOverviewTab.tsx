/**
 * GitHub Overview Tab: Status summary, connection health, rate-limit meter, and review stats.
 */

import * as React from 'react';
import {
  Github,
  GitBranch,
  ShieldCheck,
  Clock,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  RefreshCw,
  FolderGit2,
  Lock,
  Globe,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type {
  GitHubConnection,
  GitHubStatusSummary,
  RepositoryMetadata,
  CandidateSkill,
  CandidateProject,
} from '@autonom/shared-types';

interface GitHubOverviewTabProps {
  status: GitHubStatusSummary | null;
  connections: GitHubConnection[];
  repositories: RepositoryMetadata[];
  skillCandidates: CandidateSkill[];
  projectCandidates: CandidateProject[];
  onNavigateTab: (tabId: string) => void;
  onRefresh: () => void;
}

export const GitHubOverviewTab: React.FC<GitHubOverviewTabProps> = ({
  status,
  connections,
  repositories,
  skillCandidates,
  projectCandidates,
  onNavigateTab,
  onRefresh,
}) => {
  const activeConn = connections.length > 0 ? connections[0] : null;
  const selectedRepos = repositories.filter((r) => r.is_selected);
  const completedRepos = repositories.filter((r) => r.sync_status === 'completed');
  const pendingSkillsCount = skillCandidates.filter((s) => s.status === 'awaiting_review').length;
  const pendingProjectsCount = projectCandidates.filter((p) => p.status === 'awaiting_review').length;

  const rateLimitPercent = status?.rate_limit
    ? Math.round((status.rate_limit.remaining / Math.max(status.rate_limit.limit, 1)) * 100)
    : 100;

  return (
    <div className="space-y-6">
      {/* Top Banner / Hero Card */}
      <div className="rounded-xl border border-border/80 bg-gradient-to-r from-card/90 via-card to-primary/5 p-6 shadow-sm">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="h-14 w-14 rounded-2xl bg-primary/10 text-primary flex items-center justify-center border border-primary/20 shadow-inner">
              <Github className="h-7 w-7" />
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h2 className="text-xl font-bold tracking-tight">GitHub & Technical Portfolio Intelligence</h2>
                {activeConn ? (
                  <Badge variant="outline" className="bg-emerald-500/10 text-emerald-500 border-emerald-500/30 gap-1">
                    <CheckCircle2 className="h-3 w-3" /> Connected as @{activeConn.login}
                  </Badge>
                ) : (
                  <Badge variant="outline" className="bg-amber-500/10 text-amber-500 border-amber-500/30 gap-1">
                    <AlertCircle className="h-3 w-3" /> Not Connected
                  </Badge>
                )}
              </div>
              <p className="text-sm text-muted-foreground mt-1 max-w-2xl">
                Inspect authentic repository source code, identify production technology stacks, attribute verified commits and pull requests, and promote evidence-backed skills to the applicant profile.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={onRefresh} className="gap-1.5">
              <RefreshCw className="h-3.5 w-3.5" /> Refresh Status
            </Button>
            {!activeConn ? (
              <Button variant="primary" size="sm" onClick={() => onNavigateTab('connections')} className="gap-1.5">
                <Github className="h-3.5 w-3.5" /> Connect Account
              </Button>
            ) : (
              <Button variant="primary" size="sm" onClick={() => onNavigateTab('candidates')} className="gap-1.5">
                Review Candidates ({pendingSkillsCount + pendingProjectsCount})
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Discovered Repositories */}
        <Card className="hover:border-primary/40 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Discovered Repos
            </CardTitle>
            <FolderGit2 className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{repositories.length}</div>
            <p className="text-xs text-muted-foreground mt-1 flex items-center justify-between">
              <span>{selectedRepos.length} selected for analysis</span>
              <button
                onClick={() => onNavigateTab('repositories')}
                className="text-primary hover:underline inline-flex items-center text-[11px]"
              >
                Manage <ArrowRight className="h-3 w-3 ml-0.5" />
              </button>
            </p>
          </CardContent>
        </Card>

        {/* Analyzed Architecture & Code */}
        <Card className="hover:border-primary/40 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Analyzed Repos
            </CardTitle>
            <GitBranch className="h-4 w-4 text-status-success" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-status-success">{completedRepos.length}</div>
            <p className="text-xs text-muted-foreground mt-1 flex items-center justify-between">
              <span>Full AST & manifest scans</span>
              <button
                onClick={() => onNavigateTab('tech-stack')}
                className="text-primary hover:underline inline-flex items-center text-[11px]"
              >
                Tech Stack <ArrowRight className="h-3 w-3 ml-0.5" />
              </button>
            </p>
          </CardContent>
        </Card>

        {/* Candidate Skills Queue */}
        <Card className="hover:border-primary/40 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Pending Candidates
            </CardTitle>
            <ShieldCheck className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">
              {pendingSkillsCount + pendingProjectsCount}
            </div>
            <p className="text-xs text-muted-foreground mt-1 flex items-center justify-between">
              <span>{pendingSkillsCount} skills · {pendingProjectsCount} projects</span>
              <button
                onClick={() => onNavigateTab('candidates')}
                className="text-primary hover:underline inline-flex items-center text-[11px]"
              >
                Review <ArrowRight className="h-3 w-3 ml-0.5" />
              </button>
            </p>
          </CardContent>
        </Card>

        {/* Rate Limit Budget */}
        <Card className="hover:border-primary/40 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              API Rate Limit
            </CardTitle>
            <Clock className="h-4 w-4 text-cyan" />
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-bold">
                {status?.rate_limit ? status.rate_limit.remaining : 5000}
              </span>
              <span className="text-xs text-muted-foreground">
                / {status?.rate_limit ? status.rate_limit.limit : 5000}
              </span>
            </div>
            <div className="w-full bg-secondary h-1.5 rounded-full overflow-hidden mt-2">
              <div
                className={`h-full rounded-full transition-all ${
                  rateLimitPercent > 50 ? 'bg-primary' : rateLimitPercent > 20 ? 'bg-status-warning' : 'bg-status-error'
                }`}
                style={{ width: `${Math.min(100, Math.max(2, rateLimitPercent))}%` }}
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Two Column Layout: Active Connection & Recent Repositories */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Account Details & Security */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Github className="h-4 w-4 text-primary" /> Active Connection
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {activeConn ? (
              <>
                <div className="flex items-center gap-3 p-3 bg-secondary/30 rounded-lg border border-border/50">
                  {activeConn.avatar_url ? (
                    <img
                      src={activeConn.avatar_url}
                      alt={activeConn.login}
                      className="h-10 w-10 rounded-full border border-border"
                    />
                  ) : (
                    <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold">
                      {activeConn.login.slice(0, 2).toUpperCase()}
                    </div>
                  )}
                  <div className="overflow-hidden">
                    <p className="font-semibold text-sm truncate">{activeConn.name || activeConn.login}</p>
                    <p className="text-xs text-muted-foreground truncate">@{activeConn.login}</p>
                  </div>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-border/50">
                    <span className="text-muted-foreground">Connection Mode</span>
                    <Badge variant="neutral" className="text-[11px] capitalize">
                      {activeConn.mode.replace('_', ' ')}
                    </Badge>
                  </div>
                  <div className="flex justify-between py-1 border-b border-border/50">
                    <span className="text-muted-foreground">Private Repos</span>
                    <span className="font-medium flex items-center gap-1">
                      {activeConn.can_access_private ? (
                        <>
                          <Lock className="h-3 w-3 text-status-success" /> Authorized
                        </>
                      ) : (
                        <>
                          <Globe className="h-3 w-3 text-muted-foreground" /> Public Only
                        </>
                      )}
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-border/50">
                    <span className="text-muted-foreground">Public Repositories</span>
                    <span className="font-medium">{activeConn.public_repos_count}</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-muted-foreground">Vault Protection</span>
                    <Badge variant="outline" className="text-[10px] text-status-success border-status-success/30">
                      DPAPI Encrypted
                    </Badge>
                  </div>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  className="w-full mt-2"
                  onClick={() => onNavigateTab('connections')}
                >
                  Manage Connection
                </Button>
              </>
            ) : (
              <div className="text-center py-6 space-y-3">
                <Github className="h-10 w-10 text-muted-foreground/40 mx-auto" />
                <p className="text-xs text-muted-foreground">No GitHub account connected yet.</p>
                <Button variant="primary" size="sm" onClick={() => onNavigateTab('connections')} className="gap-1.5">
                  <Github className="h-3.5 w-3.5" /> Connect Now
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Right Column: Selected & Analyzed Repositories Preview */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <FolderGit2 className="h-4 w-4 text-primary" /> Monitored Repositories ({selectedRepos.length})
            </CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onNavigateTab('repositories')}
              className="text-xs text-primary hover:underline h-7"
            >
              View All ({repositories.length})
            </Button>
          </CardHeader>
          <CardContent>
            {selectedRepos.length > 0 ? (
              <div className="space-y-2.5">
                {selectedRepos.slice(0, 5).map((repo) => (
                  <div
                    key={repo.id}
                    className="flex items-center justify-between p-3 rounded-lg border border-border/60 hover:border-border transition-colors bg-card/60"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm hover:text-primary transition-colors cursor-pointer">
                          {repo.full_name}
                        </span>
                        {repo.is_fork && (
                          <Badge variant="outline" className="text-[10px] py-0">
                            Fork
                          </Badge>
                        )}
                        <Badge
                          variant="neutral"
                          className={`text-[10px] py-0 ${
                            repo.sync_status === 'completed'
                              ? 'bg-status-success/10 text-status-success'
                              : repo.sync_status === 'syncing'
                              ? 'bg-cyan/10 text-cyan animate-pulse'
                              : 'bg-muted text-muted-foreground'
                          }`}
                        >
                          {repo.sync_status}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground line-clamp-1">
                        {repo.description || 'No description provided.'}
                      </p>
                    </div>
                    <div className="text-right text-xs text-muted-foreground flex items-center gap-3">
                      {repo.primary_language && (
                        <span className="inline-flex items-center gap-1 font-medium text-foreground">
                          <span className="h-2 w-2 rounded-full bg-primary" />
                          {repo.primary_language}
                        </span>
                      )}
                      <span>★ {repo.stars_count}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 space-y-2">
                <FolderGit2 className="h-8 w-8 text-muted-foreground/40 mx-auto" />
                <p className="text-xs text-muted-foreground">
                  No repositories selected for intelligence extraction.
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onNavigateTab('repositories')}
                  className="mt-2"
                >
                  Select Repositories
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
