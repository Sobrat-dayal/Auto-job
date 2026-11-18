/**
 * Stage 22: GitHub & Technical Portfolio Intelligence Workspace.
 * Integrates GitHub account connectivity, repository discovery, code intelligence,
 * technology stack classification, commit attribution, and applicant profile candidate review.
 */

import * as React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Github,
  GitBranch,
  Layers,
  Cpu,
  FolderGit2,
  ShieldCheck,
  CheckCircle2,
  Sparkles,
  Activity,
  Key,
} from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleTabs,
} from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type {
  GitHubConnection,
  GitHubStatusSummary,
  GitHubDiagnostics,
  RepositoryMetadata,
  TechnologyFinding,
  RepositoryArchitecture,
  CommitEvidence,
  PullRequestEvidence,
  ContributionFinding,
  CandidateSkill,
  CandidateProject,
  SyncJobRecord,
  SourceTreeEntry,
  FileContentSnippet,
  ConnectGitHubRequest,
  ManualRepoRequest,
  ConfirmCandidateRequest,
} from '@autonom/shared-types';

import { GitHubOverviewTab } from './tabs/GitHubOverviewTab';
import { GitHubConnectionsTab } from './tabs/GitHubConnectionsTab';
import { GitHubRepositoriesTab } from './tabs/GitHubRepositoriesTab';
import { GitHubRepoDetailTab } from './tabs/GitHubRepoDetailTab';
import { GitHubTechStackTab } from './tabs/GitHubTechStackTab';
import { GitHubContributionsTab } from './tabs/GitHubContributionsTab';
import { GitHubEvidenceTab } from './tabs/GitHubEvidenceTab';
import { GitHubCandidatesTab } from './tabs/GitHubCandidatesTab';
import { GitHubDiagnosticsTab } from './tabs/GitHubDiagnosticsTab';

export const GitHubPortfolioWorkspace: React.FC = () => {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = React.useState<string>('overview');
  const [selectedRepo, setSelectedRepo] = React.useState<RepositoryMetadata | null>(null);
  const [selectedFile, setSelectedFile] = React.useState<FileContentSnippet | null>(null);

  // 1. Fetch High-Level Status
  const {
    data: statusSummary = null,
    isLoading: statusLoading,
    refetch: refetchStatus,
  } = useQuery<GitHubStatusSummary>({
    queryKey: ['github-status'],
    queryFn: () => apiClient.getGitHubStatus(),
  });

  // 2. Fetch Connected Accounts
  const {
    data: connections = [],
    refetch: refetchConnections,
  } = useQuery<GitHubConnection[]>({
    queryKey: ['github-connections'],
    queryFn: () => apiClient.listGitHubConnections(),
  });

  // 3. Fetch Discovered Repositories
  const {
    data: repositories = [],
    isLoading: reposLoading,
    refetch: refetchRepos,
  } = useQuery<RepositoryMetadata[]>({
    queryKey: ['github-repositories'],
    queryFn: () => apiClient.listGitHubRepositories(),
  });

  // 4. Fetch Candidate Skills
  const {
    data: skillCandidates = [],
    refetch: refetchSkills,
  } = useQuery<CandidateSkill[]>({
    queryKey: ['github-skill-candidates'],
    queryFn: () => apiClient.listGitHubSkillCandidates(),
  });

  // 5. Fetch Candidate Projects
  const {
    data: projectCandidates = [],
    refetch: refetchProjects,
  } = useQuery<CandidateProject[]>({
    queryKey: ['github-project-candidates'],
    queryFn: () => apiClient.listGitHubProjectCandidates(),
  });

  // 6. Fetch Diagnostics & Sync Jobs
  const {
    data: diagnostics = null,
    refetch: refetchDiagnostics,
  } = useQuery<GitHubDiagnostics>({
    queryKey: ['github-diagnostics'],
    queryFn: () => apiClient.getGitHubDiagnostics(),
  });

  const {
    data: syncJobs = [],
    refetch: refetchSyncJobs,
  } = useQuery<SyncJobRecord[]>({
    queryKey: ['github-sync-jobs'],
    queryFn: () => apiClient.listGitHubAnalysisJobs(),
  });

  // Selected Repo Specific Queries
  const activeRepoId = selectedRepo?.id || (repositories.length > 0 ? repositories[0].id : null);

  const { data: repoTechs = [] } = useQuery<TechnologyFinding[]>({
    queryKey: ['github-repo-techs', activeRepoId],
    queryFn: () => (activeRepoId ? apiClient.getGitHubRepositoryTechnologies(activeRepoId) : Promise.resolve([])),
    enabled: !!activeRepoId,
  });

  const { data: repoArch = null } = useQuery<RepositoryArchitecture | null>({
    queryKey: ['github-repo-arch', activeRepoId],
    queryFn: () => (activeRepoId ? apiClient.getGitHubRepositoryArchitecture(activeRepoId) : Promise.resolve(null)),
    enabled: !!activeRepoId,
  });

  const { data: repoCommits = [] } = useQuery<CommitEvidence[]>({
    queryKey: ['github-repo-commits', activeRepoId],
    queryFn: () => (activeRepoId ? apiClient.getGitHubRepositoryCommits(activeRepoId) : Promise.resolve([])),
    enabled: !!activeRepoId,
  });

  const { data: repoPRs = [] } = useQuery<PullRequestEvidence[]>({
    queryKey: ['github-repo-prs', activeRepoId],
    queryFn: () => (activeRepoId ? apiClient.getGitHubRepositoryPullRequests(activeRepoId) : Promise.resolve([])),
    enabled: !!activeRepoId,
  });

  const { data: repoContributions = [] } = useQuery<ContributionFinding[]>({
    queryKey: ['github-repo-contributions', activeRepoId],
    queryFn: () => (activeRepoId ? apiClient.getGitHubRepositoryContributions(activeRepoId) : Promise.resolve([])),
    enabled: !!activeRepoId,
  });

  const { data: treeEntries = [] } = useQuery<SourceTreeEntry[]>({
    queryKey: ['github-repo-tree', activeRepoId],
    queryFn: () => (activeRepoId ? apiClient.getGitHubRepositoryTree(activeRepoId) : Promise.resolve([])),
    enabled: !!activeRepoId,
  });

  // Mutations
  const connectMutation = useMutation({
    mutationFn: (payload: ConnectGitHubRequest) => apiClient.connectGitHubAccount(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['github-connections'] });
      queryClient.invalidateQueries({ queryKey: ['github-repositories'] });
      queryClient.invalidateQueries({ queryKey: ['github-status'] });
    },
  });

  const disconnectMutation = useMutation({
    mutationFn: (connectionId: string) => apiClient.disconnectGitHubAccount(connectionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['github-connections'] });
      queryClient.invalidateQueries({ queryKey: ['github-repositories'] });
      queryClient.invalidateQueries({ queryKey: ['github-status'] });
    },
  });

  const selectMutation = useMutation({
    mutationFn: ({ repoId, allowSource }: { repoId: string; allowSource: boolean }) =>
      apiClient.selectGitHubRepository(repoId, { allow_source_inspection: allowSource }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['github-repositories'] });
      queryClient.invalidateQueries({ queryKey: ['github-status'] });
    },
  });

  const deselectMutation = useMutation({
    mutationFn: (repoId: string) => apiClient.deselectGitHubRepository(repoId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['github-repositories'] });
      queryClient.invalidateQueries({ queryKey: ['github-status'] });
    },
  });

  const analyzeMutation = useMutation({
    mutationFn: (repoId: string) => apiClient.triggerGitHubRepositoryAnalysis(repoId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['github-repositories'] });
      queryClient.invalidateQueries({ queryKey: ['github-skill-candidates'] });
      queryClient.invalidateQueries({ queryKey: ['github-project-candidates'] });
      queryClient.invalidateQueries({ queryKey: ['github-sync-jobs'] });
      queryClient.invalidateQueries({ queryKey: ['github-status'] });
      queryClient.invalidateQueries({ queryKey: ['github-repo-techs'] });
      queryClient.invalidateQueries({ queryKey: ['github-repo-arch'] });
      queryClient.invalidateQueries({ queryKey: ['github-repo-commits'] });
      queryClient.invalidateQueries({ queryKey: ['github-repo-contributions'] });
    },
  });

  const manualRepoMutation = useMutation({
    mutationFn: (payload: ManualRepoRequest) => apiClient.addManualGitHubRepository(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['github-repositories'] });
      queryClient.invalidateQueries({ queryKey: ['github-status'] });
    },
  });

  const confirmSkillMutation = useMutation({
    mutationFn: ({ candidateId, payload }: { candidateId: string; payload?: ConfirmCandidateRequest }) =>
      apiClient.confirmGitHubSkillCandidate(candidateId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['github-skill-candidates'] });
      queryClient.invalidateQueries({ queryKey: ['github-status'] });
    },
  });

  const confirmProjectMutation = useMutation({
    mutationFn: ({ candidateId, payload }: { candidateId: string; payload?: ConfirmCandidateRequest }) =>
      apiClient.confirmGitHubProjectCandidate(candidateId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['github-project-candidates'] });
      queryClient.invalidateQueries({ queryKey: ['github-status'] });
    },
  });

  const rejectCandidateMutation = useMutation({
    mutationFn: (candidateId: string) => apiClient.rejectGitHubCandidate(candidateId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['github-skill-candidates'] });
      queryClient.invalidateQueries({ queryKey: ['github-project-candidates'] });
      queryClient.invalidateQueries({ queryKey: ['github-status'] });
    },
  });

  // Callbacks
  const handleRefreshAll = () => {
    refetchStatus();
    refetchConnections();
    refetchRepos();
    refetchSkills();
    refetchProjects();
    refetchDiagnostics();
    refetchSyncJobs();
  };

  const handleInspectDetail = (repo: RepositoryMetadata) => {
    setSelectedRepo(repo);
    setActiveTab('repo-detail');
  };

  const handleFetchFile = async (path: string) => {
    if (!activeRepoId) return;
    const file = await apiClient.getGitHubRepositoryFile(activeRepoId, path);
    setSelectedFile(file);
  };

  const handleDiscoverRepos = async () => {
    if (connections.length > 0) {
      await apiClient.discoverGitHubRepositories(connections[0].id);
      queryClient.invalidateQueries({ queryKey: ['github-repositories'] });
    }
  };

  const pendingReviewCount =
    skillCandidates.filter((s) => s.status === 'awaiting_review').length +
    projectCandidates.filter((p) => p.status === 'awaiting_review').length;

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Github },
    { id: 'connections', label: 'Connections', icon: Key },
    { id: 'repositories', label: `Repositories (${repositories.length})`, icon: FolderGit2 },
    { id: 'repo-detail', label: 'Repository Architecture', icon: Layers },
    { id: 'tech-stack', label: 'Tech Stack', icon: Cpu },
    { id: 'contributions', label: 'Contributions', icon: GitBranch },
    { id: 'evidence', label: 'Evidence & Secrets', icon: ShieldCheck },
    {
      id: 'candidates',
      label: `Review Queue (${pendingReviewCount})`,
      icon: Sparkles,
      badge: pendingReviewCount > 0 ? String(pendingReviewCount) : undefined,
    },
    { id: 'diagnostics', label: 'Diagnostics', icon: Activity },
  ];

  return (
    <ModulePage>
      <ModuleHeader
        title="GitHub & Technical Portfolio Intelligence"
        description="Stage 22: Safe repository discovery, AST/manifest analysis, technology classification, cryptographically verified commit attribution, and human-in-the-loop skill candidate promotion."
        actions={
          <div className="flex items-center gap-2">
            {connections.length > 0 && (
              <Badge variant="outline" className="bg-emerald-500/10 text-emerald-500 border-emerald-500/30 gap-1 text-xs">
                <CheckCircle2 className="h-3 w-3" /> Connected: @{connections[0].login}
              </Badge>
            )}
            <Badge variant="neutral" className="text-xs">
              Stage 22 of 50
            </Badge>
          </div>
        }
      />

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="flex-1 p-6 overflow-y-auto">
        {activeTab === 'overview' && (
          <GitHubOverviewTab
            status={statusSummary}
            connections={connections}
            repositories={repositories}
            skillCandidates={skillCandidates}
            projectCandidates={projectCandidates}
            onNavigateTab={setActiveTab}
            onRefresh={handleRefreshAll}
          />
        )}

        {activeTab === 'connections' && (
          <GitHubConnectionsTab
            connections={connections}
            onConnect={async (payload) => {
              await connectMutation.mutateAsync(payload);
            }}
            onDisconnect={async (connectionId) => {
              await disconnectMutation.mutateAsync(connectionId);
            }}
            isLoading={connectMutation.isPending || disconnectMutation.isPending}
          />
        )}

        {activeTab === 'repositories' && (
          <GitHubRepositoriesTab
            repositories={repositories}
            onSelectRepo={async (repoId, allowSource) => {
              await selectMutation.mutateAsync({ repoId, allowSource });
            }}
            onDeselectRepo={async (repoId) => {
              await deselectMutation.mutateAsync(repoId);
            }}
            onAnalyzeRepo={async (repoId) => {
              await analyzeMutation.mutateAsync(repoId);
            }}
            onAddManualRepo={async (payload) => {
              await manualRepoMutation.mutateAsync(payload);
            }}
            onDiscoverRepos={handleDiscoverRepos}
            onInspectDetail={handleInspectDetail}
            isLoading={reposLoading || selectMutation.isPending || analyzeMutation.isPending}
          />
        )}

        {activeTab === 'repo-detail' && (
          <GitHubRepoDetailTab
            repo={selectedRepo || (repositories.length > 0 ? repositories[0] : null)}
            architecture={repoArch}
            technologies={repoTechs}
            treeEntries={treeEntries}
            selectedFile={selectedFile}
            onFetchFile={handleFetchFile}
            onAnalyzeRepo={async (repoId) => {
              await analyzeMutation.mutateAsync(repoId);
            }}
            onBackToList={() => setActiveTab('repositories')}
            isLoading={analyzeMutation.isPending}
          />
        )}

        {activeTab === 'tech-stack' && (
          <GitHubTechStackTab
            technologies={repoTechs}
          />
        )}

        {activeTab === 'contributions' && (
          <GitHubContributionsTab
            commits={repoCommits}
            pullRequests={repoPRs}
            contributions={repoContributions}
          />
        )}

        {activeTab === 'evidence' && (
          <GitHubEvidenceTab
            technologies={repoTechs}
            commits={repoCommits}
            skillCandidates={skillCandidates}
          />
        )}

        {activeTab === 'candidates' && (
          <GitHubCandidatesTab
            skillCandidates={skillCandidates}
            projectCandidates={projectCandidates}
            onConfirmSkill={async (candidateId, payload) => {
              await confirmSkillMutation.mutateAsync({ candidateId, payload });
            }}
            onConfirmProject={async (candidateId, payload) => {
              await confirmProjectMutation.mutateAsync({ candidateId, payload });
            }}
            onRejectCandidate={async (candidateId) => {
              await rejectCandidateMutation.mutateAsync(candidateId);
            }}
            isLoading={
              confirmSkillMutation.isPending ||
              confirmProjectMutation.isPending ||
              rejectCandidateMutation.isPending
            }
          />
        )}

        {activeTab === 'diagnostics' && (
          <GitHubDiagnosticsTab
            diagnostics={diagnostics}
            syncJobs={syncJobs}
            onRefresh={handleRefreshAll}
            isLoading={statusLoading}
          />
        )}
      </div>
    </ModulePage>
  );
};

export default GitHubPortfolioWorkspace;
