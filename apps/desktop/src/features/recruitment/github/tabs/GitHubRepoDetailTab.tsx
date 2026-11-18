/**
 * GitHub Repo Detail Tab: Deep dive into a specific repository.
 * Visualizes language byte breakdown, architectural type, entrypoints, CI/Docker flags, and file tree.
 */

import * as React from 'react';
import {
  FolderGit2,
  Layers,
  FileCode,
  Shield,
  Play,
  ExternalLink,
  Lock,
  Globe,
  Terminal,
  FileText,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type {
  RepositoryMetadata,
  RepositoryArchitecture,
  TechnologyFinding,
  SourceTreeEntry,
  FileContentSnippet,
} from '@autonom/shared-types';

interface GitHubRepoDetailTabProps {
  repo: RepositoryMetadata | null;
  architecture: RepositoryArchitecture | null;
  technologies: TechnologyFinding[];
  treeEntries: SourceTreeEntry[];
  selectedFile: FileContentSnippet | null;
  onFetchFile: (path: string) => Promise<void>;
  onAnalyzeRepo: (repoId: string) => Promise<void>;
  onBackToList: () => void;
  isLoading: boolean;
}

export const GitHubRepoDetailTab: React.FC<GitHubRepoDetailTabProps> = ({
  repo,
  architecture,
  technologies,
  treeEntries,
  selectedFile,
  onFetchFile,
  onAnalyzeRepo,
  onBackToList,
  isLoading,
}) => {
  const [activeFilePath, setActiveFilePath] = React.useState<string | null>(null);

  if (!repo) {
    return (
      <div className="p-12 text-center space-y-3">
        <FolderGit2 className="h-10 w-10 text-muted-foreground/40 mx-auto" />
        <p className="text-sm text-muted-foreground">Select a repository from the Repositories tab to view detailed architecture.</p>
        <Button size="sm" variant="primary" onClick={onBackToList}>
          Go to Repositories
        </Button>
      </div>
    );
  }

  // Calculate language distribution percentages
  const totalLangBytes = Object.values(repo.languages || {}).reduce((a, b) => a + b, 0);
  const languageStats = Object.entries(repo.languages || {}).map(([lang, bytes]) => ({
    name: lang,
    bytes,
    percent: totalLangBytes > 0 ? Math.round((bytes / totalLangBytes) * 100) : 0,
  })).sort((a, b) => b.bytes - a.bytes);

  const handleSelectFile = async (path: string) => {
    setActiveFilePath(path);
    await onFetchFile(path);
  };

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="rounded-xl border border-border/80 bg-card p-6 shadow-sm">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" onClick={onBackToList} className="h-7 px-2 text-xs">
                ← Repositories
              </Button>
              <span className="text-muted-foreground">/</span>
              <h2 className="text-lg font-bold tracking-tight">{repo.full_name}</h2>
              <a
                href={repo.html_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-foreground"
              >
                <ExternalLink className="h-3.5 w-3.5" />
              </a>
              {repo.visibility === 'private' ? (
                <Badge variant="outline" className="text-xs text-status-warning border-status-warning/30 gap-1 py-0">
                  <Lock className="h-3 w-3" /> Private
                </Badge>
              ) : (
                <Badge variant="outline" className="text-xs text-muted-foreground gap-1 py-0">
                  <Globe className="h-3 w-3" /> Public
                </Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground max-w-3xl">
              {repo.description || 'No description provided.'}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="primary"
              size="sm"
              onClick={() => onAnalyzeRepo(repo.id)}
              disabled={isLoading || repo.sync_status === 'syncing'}
              className="gap-1.5 text-xs"
            >
              <Play className="h-3.5 w-3.5" />
              {repo.sync_status === 'syncing' ? 'Analyzing...' : 'Run Full Analysis'}
            </Button>
          </div>
        </div>
      </div>

      {/* Two Column Grid: Architecture & Language Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Architecture & Structural Characteristics */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Layers className="h-4 w-4 text-primary" /> Architecture Classification
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {architecture ? (
              <>
                <div className="p-3 bg-secondary/30 rounded-lg border border-border/50 space-y-1">
                  <span className="text-[11px] text-muted-foreground uppercase tracking-wider font-semibold">
                    Detected Pattern
                  </span>
                  <div className="flex items-center gap-2">
                    <Badge variant="primary" className="text-xs capitalize">
                      {architecture.architecture_type.replace('_', ' ')}
                    </Badge>
                    <Badge variant="outline" className="text-[10px] text-status-success border-status-success/30">
                      {architecture.confidence}
                    </Badge>
                  </div>
                </div>

                {/* Capability Flags */}
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-border/50">
                    <span className="text-muted-foreground">CI/CD Pipelines</span>
                    <span className="font-medium">
                      {architecture.has_ci ? (
                        <span className="text-status-success">Configured (GitHub Actions)</span>
                      ) : (
                        <span className="text-muted-foreground">None detected</span>
                      )}
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-border/50">
                    <span className="text-muted-foreground">Containerization</span>
                    <span className="font-medium">
                      {architecture.has_docker ? (
                        <span className="text-status-success">Dockerfile Present</span>
                      ) : (
                        <span className="text-muted-foreground">None detected</span>
                      )}
                    </span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-border/50">
                    <span className="text-muted-foreground">Automated Tests</span>
                    <span className="font-medium">
                      {architecture.has_tests ? (
                        <span className="text-status-success">Test Suites Present</span>
                      ) : (
                        <span className="text-muted-foreground">None detected</span>
                      )}
                    </span>
                  </div>
                </div>

                {/* Entrypoints */}
                {architecture.entrypoints.length > 0 && (
                  <div>
                    <span className="text-[11px] text-muted-foreground font-semibold block mb-1">
                      Identified Application Entrypoints:
                    </span>
                    <div className="space-y-1">
                      {architecture.entrypoints.map((ep) => (
                        <div
                          key={ep}
                          className="flex items-center gap-1.5 font-mono text-[11px] p-1.5 rounded bg-secondary/40"
                        >
                          <Terminal className="h-3 w-3 text-primary shrink-0" />
                          <span className="truncate">{ep}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-6 space-y-2">
                <Layers className="h-8 w-8 text-muted-foreground/40 mx-auto" />
                <p className="text-xs text-muted-foreground">Architecture not analyzed yet.</p>
                <Button size="sm" variant="outline" onClick={() => onAnalyzeRepo(repo.id)} className="text-xs">
                  Run Analysis
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Right Column: Language Byte Breakdown & Dependencies */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <FileCode className="h-4 w-4 text-primary" /> Language Distribution & Technologies
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Language Progress Bar */}
            {languageStats.length > 0 ? (
              <div className="space-y-3">
                <div className="flex h-3 w-full rounded-full overflow-hidden bg-secondary">
                  {languageStats.map((item, idx) => {
                    const colors = ['bg-primary', 'bg-cyan', 'bg-status-success', 'bg-status-warning', 'bg-purple-500', 'bg-status-error'];
                    return (
                      <div
                        key={item.name}
                        className={`${colors[idx % colors.length]} transition-all`}
                        style={{ width: `${Math.max(1, item.percent)}%` }}
                        title={`${item.name}: ${item.percent}% (${(item.bytes / 1024).toFixed(1)} KB)`}
                      />
                    );
                  })}
                </div>

                <div className="flex flex-wrap gap-3 text-xs">
                  {languageStats.map((item, idx) => {
                    const dotColors = ['bg-primary', 'bg-cyan', 'bg-status-success', 'bg-status-warning', 'bg-purple-500', 'bg-status-error'];
                    return (
                      <div key={item.name} className="flex items-center gap-1.5">
                        <span className={`h-2.5 w-2.5 rounded-full ${dotColors[idx % dotColors.length]}`} />
                        <span className="font-semibold">{item.name}</span>
                        <span className="text-muted-foreground">
                          {item.percent}% ({(item.bytes / 1024).toFixed(1)} KB)
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">No language telemetry available.</p>
            )}

            {/* Extracted Technologies for this Repo */}
            <div className="pt-3 border-t border-border/60">
              <span className="text-xs font-semibold block mb-2">Detected Technologies ({technologies.length})</span>
              {technologies.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {technologies.map((tech) => (
                    <div
                      key={`${tech.name}-${tech.category}`}
                      className="p-2 rounded-lg border border-border/50 bg-secondary/20 flex items-center justify-between text-xs"
                    >
                      <div className="space-y-0.5">
                        <div className="font-medium flex items-center gap-1.5">
                          {tech.name}
                          {tech.version && (
                            <span className="text-[10px] font-mono text-muted-foreground">v{tech.version}</span>
                          )}
                        </div>
                        <span className="text-[10px] text-muted-foreground capitalize">
                          {tech.category.replace('_', ' ')}
                        </span>
                      </div>
                      <Badge variant="outline" className="text-[10px] py-0">
                        {tech.confidence}
                      </Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-muted-foreground">Run analysis to extract frameworks and dependencies.</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Source Tree & Redacted Snippet Inspector */}
      <Card className="border-border/80">
        <CardHeader>
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <FileText className="h-4 w-4 text-primary" /> Source Tree & Safe Code Inspector
          </CardTitle>
          <CardDescription className="text-xs">
            Browse discovered repository manifests and source code. All file contents are screened through SecretRedactor to scrub sensitive tokens prior to presentation.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* File List */}
            <div className="lg:col-span-1 border border-border/60 rounded-lg p-2 max-h-96 overflow-y-auto space-y-1 bg-secondary/10">
              <div className="text-[11px] font-semibold text-muted-foreground px-2 py-1">
                Discovered Files ({treeEntries.length})
              </div>
              {treeEntries.length > 0 ? (
                treeEntries.map((entry) => (
                  <button
                    key={entry.path}
                    onClick={() => handleSelectFile(entry.path)}
                    className={`w-full text-left px-2.5 py-1.5 rounded text-xs font-mono truncate flex items-center gap-2 transition-colors ${
                      activeFilePath === entry.path
                        ? 'bg-primary text-primary-foreground font-semibold'
                        : 'hover:bg-secondary/40 text-foreground'
                    }`}
                  >
                    <FileCode className="h-3 w-3 shrink-0" />
                    <span className="truncate">{entry.path}</span>
                  </button>
                ))
              ) : (
                <p className="text-xs text-muted-foreground p-3 text-center">
                  Tree entries not loaded. Run analysis to fetch Git Tree.
                </p>
              )}
            </div>

            {/* Redacted File Content Viewer */}
            <div className="lg:col-span-2 border border-border/60 rounded-lg p-3 bg-secondary/20 min-h-[300px] flex flex-col">
              {selectedFile ? (
                <div className="space-y-2 flex-1 flex flex-col">
                  <div className="flex items-center justify-between pb-2 border-b border-border/60 text-xs">
                    <span className="font-mono font-semibold">{selectedFile.path}</span>
                    <div className="flex items-center gap-2">
                      {selectedFile.is_redacted && (
                        <Badge variant="outline" className="text-[10px] text-status-success border-status-success/30 gap-1">
                          <Shield className="h-3 w-3" /> {selectedFile.redactions_count} Secret(s) Redacted
                        </Badge>
                      )}
                      <span className="text-muted-foreground text-[11px]">
                        {(selectedFile.size_bytes / 1024).toFixed(1)} KB
                      </span>
                    </div>
                  </div>
                  <pre className="flex-1 font-mono text-[11px] bg-background/80 p-3 rounded border border-border/50 overflow-x-auto whitespace-pre leading-relaxed">
                    {selectedFile.content}
                  </pre>
                </div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground p-6 text-center space-y-2">
                  <FileText className="h-8 w-8 text-muted-foreground/30" />
                  <p className="text-xs">Select any file from the tree to inspect redacted content.</p>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
