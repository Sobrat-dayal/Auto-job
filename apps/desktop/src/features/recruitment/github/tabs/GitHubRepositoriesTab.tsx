/**
 * GitHub Repositories Tab: Discover, filter, select, and analyze repositories.
 */

import * as React from 'react';
import {
  FolderGit2,
  Search,
  Plus,
  RefreshCw,
  GitFork,
  Star,
  Play,
  Check,
  Lock,
  Globe,
  ExternalLink,
  ChevronRight,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import type {
  RepositoryMetadata,
  ManualRepoRequest,
} from '@autonom/shared-types';

interface GitHubRepositoriesTabProps {
  repositories: RepositoryMetadata[];
  onSelectRepo: (repoId: string, allowSource: boolean) => Promise<void>;
  onDeselectRepo: (repoId: string) => Promise<void>;
  onAnalyzeRepo: (repoId: string) => Promise<void>;
  onAddManualRepo: (payload: ManualRepoRequest) => Promise<void>;
  onDiscoverRepos: () => Promise<void>;
  onInspectDetail: (repo: RepositoryMetadata) => void;
  isLoading: boolean;
}

export const GitHubRepositoriesTab: React.FC<GitHubRepositoriesTabProps> = ({
  repositories,
  onSelectRepo,
  onDeselectRepo,
  onAnalyzeRepo,
  onAddManualRepo,
  onDiscoverRepos,
  onInspectDetail,
  isLoading,
}) => {
  const [searchTerm, setSearchTerm] = React.useState('');
  const [onlySelected, setOnlySelected] = React.useState(false);
  const [hideForks, setHideForks] = React.useState(false);
  const [manualUrl, setManualUrl] = React.useState('');
  const [isAddingManual, setIsAddingManual] = React.useState(false);
  const [analyzingIds, setAnalyzingIds] = React.useState<Record<string, boolean>>({});

  const filteredRepos = React.useMemo(() => {
    return repositories.filter((repo) => {
      if (onlySelected && !repo.is_selected) return false;
      if (hideForks && repo.is_fork) return false;
      if (searchTerm) {
        const query = searchTerm.toLowerCase();
        const matchesName = repo.name.toLowerCase().includes(query);
        const matchesOwner = repo.owner.toLowerCase().includes(query);
        const matchesLang = (repo.primary_language || '').toLowerCase().includes(query);
        const matchesDesc = (repo.description || '').toLowerCase().includes(query);
        const matchesTopic = repo.topics.some((t) => t.toLowerCase().includes(query));
        return matchesName || matchesOwner || matchesLang || matchesDesc || matchesTopic;
      }
      return true;
    });
  }, [repositories, onlySelected, hideForks, searchTerm]);

  const handleAddManual = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualUrl.trim()) return;
    try {
      setIsAddingManual(true);
      await onAddManualRepo({ url: manualUrl.trim() });
      setManualUrl('');
    } finally {
      setIsAddingManual(false);
    }
  };

  const handleAnalyze = async (repoId: string) => {
    try {
      setAnalyzingIds((prev) => ({ ...prev, [repoId]: true }));
      await onAnalyzeRepo(repoId);
    } finally {
      setAnalyzingIds((prev) => ({ ...prev, [repoId]: false }));
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Action Bar */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md">
          <Search className="h-4 w-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
          <Input
            placeholder="Search by repo, language, topic, or description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 text-xs"
          />
        </div>

        {/* Filter Toggles & Actions */}
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant={onlySelected ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setOnlySelected(!onlySelected)}
            className="text-xs h-8"
          >
            {onlySelected ? 'Showing Selected' : 'Show All'}
          </Button>

          <Button
            variant={hideForks ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setHideForks(!hideForks)}
            className="text-xs h-8"
          >
            {hideForks ? 'Forks Hidden' : 'Hide Forks'}
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={onDiscoverRepos}
            disabled={isLoading}
            className="text-xs h-8 gap-1.5"
          >
            <RefreshCw className={`h-3 w-3 ${isLoading ? 'animate-spin' : ''}`} />
            Sync Repos
          </Button>
        </div>
      </div>

      {/* Manual URL Ingestion Card */}
      <Card className="border-border/70 bg-card/60">
        <CardContent className="pt-4 pb-4">
          <form onSubmit={handleAddManual} className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <div className="flex-1">
              <Input
                placeholder="Ingest any public repository: https://github.com/owner/repository"
                value={manualUrl}
                onChange={(e) => setManualUrl(e.target.value)}
                disabled={isAddingManual}
                className="text-xs"
              />
            </div>
            <Button type="submit" size="sm" variant="primary" disabled={isAddingManual || !manualUrl.trim()} className="text-xs gap-1.5 shrink-0">
              <Plus className="h-3.5 w-3.5" /> Add Manual Repository
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Repository Listing Table / Cards */}
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs text-muted-foreground px-1">
          <span>Found {filteredRepos.length} repositories</span>
          <span>{repositories.filter((r) => r.is_selected).length} selected for portfolio intelligence</span>
        </div>

        {filteredRepos.length > 0 ? (
          <div className="space-y-2.5">
            {filteredRepos.map((repo) => {
              const isAnalyzing = analyzingIds[repo.id];

              return (
                <Card
                  key={repo.id}
                  className={`border-border/70 hover:border-border transition-all ${
                    repo.is_selected ? 'bg-card' : 'bg-card/40 opacity-90'
                  }`}
                >
                  <CardContent className="p-4">
                    <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                      {/* Left: Metadata & Links */}
                      <div className="space-y-1.5 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <button
                            onClick={() => onInspectDetail(repo)}
                            className="font-bold text-sm hover:text-primary transition-colors text-left flex items-center gap-1"
                          >
                            {repo.full_name}
                            <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
                          </button>

                          <a
                            href={repo.html_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-muted-foreground hover:text-foreground inline-flex items-center"
                          >
                            <ExternalLink className="h-3 w-3" />
                          </a>

                          {repo.visibility === 'private' ? (
                            <Badge variant="outline" className="text-[10px] text-status-warning border-status-warning/30 gap-1 py-0">
                              <Lock className="h-2.5 w-2.5" /> Private
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="text-[10px] text-muted-foreground gap-1 py-0">
                              <Globe className="h-2.5 w-2.5" /> Public
                            </Badge>
                          )}

                          {repo.is_fork && (
                            <Badge variant="neutral" className="text-[10px] gap-1 py-0">
                              <GitFork className="h-2.5 w-2.5" /> Fork
                            </Badge>
                          )}

                          <Badge
                            variant="neutral"
                            className={`text-[10px] py-0 ${
                              repo.sync_status === 'completed'
                                ? 'bg-status-success/10 text-status-success'
                                : repo.sync_status === 'syncing'
                                ? 'bg-cyan/10 text-cyan animate-pulse'
                                : repo.sync_status === 'failed'
                                ? 'bg-status-error/10 text-status-error'
                                : 'bg-muted text-muted-foreground'
                            }`}
                          >
                            {repo.sync_status}
                          </Badge>
                        </div>

                        <p className="text-xs text-muted-foreground line-clamp-2 max-w-3xl">
                          {repo.description || 'No description provided.'}
                        </p>

                        {/* Topics & Tech Tags */}
                        {repo.topics.length > 0 && (
                          <div className="flex flex-wrap gap-1 pt-1">
                            {repo.topics.slice(0, 6).map((topic) => (
                              <Badge key={topic} variant="outline" className="text-[10px] py-0 px-1.5 bg-secondary/20">
                                #{topic}
                              </Badge>
                            ))}
                            {repo.topics.length > 6 && (
                              <span className="text-[10px] text-muted-foreground">+{repo.topics.length - 6} more</span>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Right: Metrics & Selection Controls */}
                      <div className="flex items-center gap-4 shrink-0">
                        {/* Language & Stars */}
                        <div className="text-right text-xs space-y-0.5 min-w-[90px]">
                          {repo.primary_language && (
                            <div className="font-semibold flex items-center justify-end gap-1.5">
                              <span className="h-2 w-2 rounded-full bg-primary" />
                              {repo.primary_language}
                            </div>
                          )}
                          <div className="text-muted-foreground flex items-center justify-end gap-1">
                            <Star className="h-3 w-3 text-status-warning fill-status-warning" />
                            <span>{repo.stars_count}</span>
                            {repo.forks_count > 0 && (
                              <>
                                <span className="mx-1">·</span>
                                <span>{repo.forks_count} forks</span>
                              </>
                            )}
                          </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex items-center gap-2">
                          {repo.is_selected ? (
                            <>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleAnalyze(repo.id)}
                                disabled={isAnalyzing || repo.sync_status === 'syncing'}
                                className="text-xs gap-1.5 h-8 text-primary border-primary/30 hover:bg-primary/10"
                              >
                                <Play className={`h-3 w-3 ${isAnalyzing ? 'animate-spin' : ''}`} />
                                {isAnalyzing ? 'Analyzing...' : 'Run Analysis'}
                              </Button>

                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => onDeselectRepo(repo.id)}
                                className="text-xs h-8 text-muted-foreground hover:text-foreground"
                              >
                                Deselect
                              </Button>
                            </>
                          ) : (
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() => onSelectRepo(repo.id, true)}
                              className="text-xs gap-1.5 h-8"
                            >
                              <Check className="h-3 w-3" /> Select for Scan
                            </Button>
                          )}

                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onInspectDetail(repo)}
                            className="text-xs h-8"
                          >
                            Details
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        ) : (
          <div className="p-8 border border-dashed border-border rounded-xl text-center space-y-2">
            <FolderGit2 className="h-8 w-8 text-muted-foreground/40 mx-auto" />
            <p className="text-sm font-medium">No matching repositories found.</p>
            <p className="text-xs text-muted-foreground">
              Try adjusting your search query or sync new repositories from your connected account.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
