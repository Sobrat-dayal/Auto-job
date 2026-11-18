/**
 * GitHub Contributions Tab: Shows verified commit evidence, pull requests, author vs committer attribution, and bot filtering.
 */

import * as React from 'react';
import {
  GitCommit,
  GitPullRequest,
  UserCheck,
  Search,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import type {
  CommitEvidence,
  PullRequestEvidence,
  ContributionFinding,
  GitHubAttributionLevel,
} from '@autonom/shared-types';

interface GitHubContributionsTabProps {
  commits: CommitEvidence[];
  pullRequests: PullRequestEvidence[];
  contributions: ContributionFinding[];
}

const ATTRIBUTION_BADGES: Record<GitHubAttributionLevel, { label: string; className: string }> = {
  independently_corroborated: { label: 'Independently Corroborated', className: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/30' },
  applicant_confirmed_contribution: { label: 'Applicant Confirmed', className: 'bg-blue-500/10 text-blue-500 border-blue-500/30' },
  commit_author_evidence: { label: 'Commit Author Verified', className: 'bg-primary/10 text-primary border-primary/30' },
  contribution_evidence: { label: 'Contribution Evidence', className: 'bg-purple-500/10 text-purple-500 border-purple-500/30' },
  account_attributed_activity: { label: 'Account Attributed', className: 'bg-amber-500/10 text-amber-500 border-amber-500/30' },
  repository_associated: { label: 'Repository Associated', className: 'bg-muted text-muted-foreground border-border' },
};

export const GitHubContributionsTab: React.FC<GitHubContributionsTabProps> = ({
  commits,
  pullRequests,
  contributions,
}) => {
  const [viewMode, setViewMode] = React.useState<'commits' | 'pull_requests' | 'summary'>('summary');
  const [searchTerm, setSearchTerm] = React.useState('');

  const applicantCommits = commits.filter((c) => c.is_applicant);
  const applicantPRs = pullRequests.filter((pr) => pr.is_applicant);

  const filteredCommits = React.useMemo(() => {
    return commits.filter((c) => {
      if (searchTerm) {
        const query = searchTerm.toLowerCase();
        return (
          c.message.toLowerCase().includes(query) ||
          c.commit_sha.toLowerCase().includes(query) ||
          c.author_name.toLowerCase().includes(query)
        );
      }
      return true;
    });
  }, [commits, searchTerm]);

  const filteredPRs = React.useMemo(() => {
    return pullRequests.filter((pr) => {
      if (searchTerm) {
        const query = searchTerm.toLowerCase();
        return pr.title.toLowerCase().includes(query) || String(pr.pr_number).includes(query);
      }
      return true;
    });
  }, [pullRequests, searchTerm]);

  return (
    <div className="space-y-6">
      {/* Top Navigation & Metrics */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Button
            variant={viewMode === 'summary' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setViewMode('summary')}
            className="text-xs h-8"
          >
            Attribution Summary ({contributions.length})
          </Button>
          <Button
            variant={viewMode === 'commits' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setViewMode('commits')}
            className="text-xs h-8 gap-1.5"
          >
            <GitCommit className="h-3.5 w-3.5" />
            Verified Commits ({applicantCommits.length})
          </Button>
          <Button
            variant={viewMode === 'pull_requests' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setViewMode('pull_requests')}
            className="text-xs h-8 gap-1.5"
          >
            <GitPullRequest className="h-3.5 w-3.5" />
            Pull Requests ({applicantPRs.length})
          </Button>
        </div>

        <div className="relative max-w-xs">
          <Search className="h-4 w-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
          <Input
            placeholder="Search commits or PRs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 text-xs h-8"
          />
        </div>
      </div>

      {/* View Mode 1: Summary Findings */}
      {viewMode === 'summary' && (
        <div className="space-y-3">
          {contributions.length > 0 ? (
            contributions.map((item) => {
              const badgeInfo = ATTRIBUTION_BADGES[item.attribution_level] || ATTRIBUTION_BADGES.repository_associated;

              return (
                <Card key={item.repo_id} className="border-border/70">
                  <CardContent className="p-4 space-y-2">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-sm">{item.repo_name}</span>
                        <Badge variant="outline" className={`text-[10px] ${badgeInfo.className}`}>
                          {badgeInfo.label}
                        </Badge>
                      </div>
                      <div className="text-xs text-muted-foreground flex items-center gap-3">
                        <span>{item.applicant_commits_count} applicant commits</span>
                        <span>{item.pull_requests_count} PRs</span>
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground">{item.summary}</p>
                  </CardContent>
                </Card>
              );
            })
          ) : (
            <div className="p-8 border border-dashed border-border rounded-xl text-center space-y-2">
              <UserCheck className="h-8 w-8 text-muted-foreground/40 mx-auto" />
              <p className="text-sm font-medium">No contribution summaries generated yet.</p>
              <p className="text-xs text-muted-foreground">
                Run analysis on your selected repositories to attribute commits and contributions.
              </p>
            </div>
          )}
        </div>
      )}

      {/* View Mode 2: Commits List */}
      {viewMode === 'commits' && (
        <div className="space-y-2.5">
          {filteredCommits.length > 0 ? (
            filteredCommits.map((c) => {
              const badgeInfo = ATTRIBUTION_BADGES[c.attribution_level] || ATTRIBUTION_BADGES.repository_associated;

              return (
                <div
                  key={c.commit_sha}
                  className="p-3 rounded-lg border border-border/70 bg-card hover:border-border transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <GitCommit className="h-3.5 w-3.5 text-primary shrink-0" />
                      <span className="font-mono font-semibold text-primary">
                        {c.commit_sha.slice(0, 7)}
                      </span>
                      <span className="font-medium line-clamp-1">{c.message}</span>
                      {c.is_merge && (
                        <Badge variant="neutral" className="text-[10px] py-0">
                          Merge
                        </Badge>
                      )}
                    </div>
                    <div className="text-muted-foreground text-[11px] flex items-center gap-3">
                      <span>Authored by: <strong className="text-foreground">{c.author_name}</strong></span>
                      {c.author_login && <span>(@{c.author_login})</span>}
                      <span>·</span>
                      <span>{new Date(c.committed_date).toLocaleDateString()}</span>
                    </div>
                  </div>

                  <Badge variant="outline" className={`text-[10px] shrink-0 ${badgeInfo.className}`}>
                    {badgeInfo.label}
                  </Badge>
                </div>
              );
            })
          ) : (
            <div className="p-8 border border-dashed border-border rounded-xl text-center space-y-2">
              <GitCommit className="h-8 w-8 text-muted-foreground/40 mx-auto" />
              <p className="text-sm font-medium">No commits available in the current selection.</p>
            </div>
          )}
        </div>
      )}

      {/* View Mode 3: Pull Requests */}
      {viewMode === 'pull_requests' && (
        <div className="space-y-2.5">
          {filteredPRs.length > 0 ? (
            filteredPRs.map((pr) => {
              const badgeInfo = ATTRIBUTION_BADGES[pr.attribution_level] || ATTRIBUTION_BADGES.repository_associated;

              return (
                <div
                  key={`${pr.repo_id}-${pr.pr_number}`}
                  className="p-3 rounded-lg border border-border/70 bg-card hover:border-border transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <GitPullRequest className="h-3.5 w-3.5 text-purple-500 shrink-0" />
                      <span className="font-mono font-semibold">#{pr.pr_number}</span>
                      <span className="font-medium line-clamp-1">{pr.title}</span>
                      <Badge
                        variant="neutral"
                        className={`text-[10px] py-0 capitalize ${
                          pr.state === 'closed' && pr.merged_at
                            ? 'bg-purple-500/10 text-purple-500'
                            : pr.state === 'open'
                            ? 'bg-emerald-500/10 text-emerald-500'
                            : 'bg-muted text-muted-foreground'
                        }`}
                      >
                        {pr.state === 'closed' && pr.merged_at ? 'Merged' : pr.state}
                      </Badge>
                    </div>
                    <div className="text-muted-foreground text-[11px] flex items-center gap-3">
                      <span>By: @{pr.author_login}</span>
                      <span>·</span>
                      <span className="text-status-success">+{pr.additions}</span>
                      <span className="text-status-error">-{pr.deletions}</span>
                      <span>in {pr.changed_files} files</span>
                    </div>
                  </div>

                  <Badge variant="outline" className={`text-[10px] shrink-0 ${badgeInfo.className}`}>
                    {badgeInfo.label}
                  </Badge>
                </div>
              );
            })
          ) : (
            <div className="p-8 border border-dashed border-border rounded-xl text-center space-y-2">
              <GitPullRequest className="h-8 w-8 text-muted-foreground/40 mx-auto" />
              <p className="text-sm font-medium">No pull requests found.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
