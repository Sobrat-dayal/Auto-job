/**
 * Stage 22: GitHub Integration & Technical Portfolio Intelligence Shared Types.
 */

export type GitHubConnectionMode =
  | 'public_only'
  | 'authorized_app'
  | 'personal_access_token'
  | 'manual_url';

export type GitHubConnectionStatus =
  | 'connected'
  | 'not_connected'
  | 'expired'
  | 'revoked'
  | 'rate_limited'
  | 'error';

export type GitHubRepoVisibility = 'public' | 'private' | 'internal';

export type GitHubSyncStatus =
  | 'not_synced'
  | 'queued'
  | 'syncing'
  | 'completed'
  | 'partially_completed'
  | 'rate_limited'
  | 'authentication_required'
  | 'permission_denied'
  | 'repository_unavailable'
  | 'failed'
  | 'cancelled';

export type GitHubTechCategory =
  | 'programming_language'
  | 'framework'
  | 'library'
  | 'database'
  | 'orm'
  | 'testing'
  | 'build_tool'
  | 'package_manager'
  | 'ci_cd'
  | 'cloud'
  | 'containerization'
  | 'ai_ml'
  | 'other';

export type GitHubDetectionConfidence =
  | 'detected'
  | 'strongly_supported'
  | 'weak_signal'
  | 'uncertain';

export type GitHubArchitectureType =
  | 'monorepo'
  | 'microservices'
  | 'frontend_only'
  | 'backend_api'
  | 'cli_tool'
  | 'library_package'
  | 'fullstack_application'
  | 'data_pipeline'
  | 'other';

export type GitHubAttributionLevel =
  | 'repository_associated'
  | 'account_attributed_activity'
  | 'commit_author_evidence'
  | 'contribution_evidence'
  | 'applicant_confirmed_contribution'
  | 'independently_corroborated';

export type GitHubCandidateStatus = 'awaiting_review' | 'confirmed' | 'rejected';

export interface GitHubConnection {
  id: string;
  login: string;
  github_id?: number | null;
  name?: string | null;
  email?: string | null;
  avatar_url?: string | null;
  mode: GitHubConnectionMode;
  status: GitHubConnectionStatus;
  scopes: string[];
  can_access_private: boolean;
  public_repos_count: number;
  total_private_repos_count: number;
  followers_count: number;
  following_count: number;
  connected_at: string;
  last_validated_at?: string | null;
  error_message?: string | null;
  profile_id?: string | null;
}

export interface RepositoryMetadata {
  id: string;
  github_repo_id?: number | null;
  owner: string;
  name: string;
  full_name: string;
  html_url: string;
  description?: string | null;
  visibility: GitHubRepoVisibility;
  is_fork: boolean;
  parent_repo?: string | null;
  is_archived: boolean;
  is_disabled: boolean;
  default_branch: string;
  default_branch_commit_sha?: string | null;
  primary_language?: string | null;
  languages: Record<string, number>;
  topics: string[];
  stars_count: number;
  forks_count: number;
  open_issues_count: number;
  size_kb: number;
  created_at?: string | null;
  pushed_at?: string | null;
  connection_id?: string | null;
  is_selected: boolean;
  allow_source_inspection: boolean;
  sync_status: GitHubSyncStatus;
  last_synced_at?: string | null;
}

export interface SourceTreeEntry {
  path: string;
  mode: string;
  type: 'blob' | 'tree';
  sha: string;
  size?: number | null;
  url?: string | null;
}

export interface FileContentSnippet {
  path: string;
  size_bytes: number;
  is_truncated: boolean;
  sha: string;
  content: string;
  is_redacted: boolean;
  redactions_count: number;
}

export interface TechnologyFinding {
  name: string;
  category: GitHubTechCategory;
  version?: string | null;
  confidence: GitHubDetectionConfidence;
  evidence_source: string;
  repo_id: string;
  file_path?: string | null;
  details?: Record<string, any>;
}

export interface RepositoryArchitecture {
  repo_id: string;
  architecture_type: GitHubArchitectureType;
  entrypoints: string[];
  modules: string[];
  package_managers: string[];
  has_docker: boolean;
  has_ci: boolean;
  has_tests: boolean;
  confidence: GitHubDetectionConfidence;
  details?: Record<string, any>;
}

export interface CommitEvidence {
  commit_sha: string;
  message: string;
  author_name: string;
  author_email: string;
  author_login?: string | null;
  committer_name?: string | null;
  committed_date: string;
  repo_id: string;
  is_merge: boolean;
  is_applicant: boolean;
  attribution_level: GitHubAttributionLevel;
}

export interface PullRequestEvidence {
  pr_number: number;
  title: string;
  author_login: string;
  state: string;
  merged_at?: string | null;
  created_at: string;
  repo_id: string;
  additions: number;
  deletions: number;
  changed_files: number;
  is_applicant: boolean;
  attribution_level: GitHubAttributionLevel;
}

export interface ContributionFinding {
  repo_id: string;
  repo_name: string;
  summary: string;
  attribution_level: GitHubAttributionLevel;
  total_commits_found: number;
  applicant_commits_count: number;
  pull_requests_count: number;
  evidence_refs: string[];
}

export interface CandidateSkill {
  id: string;
  name: string;
  category: GitHubTechCategory;
  version?: string | null;
  proficiency_hint: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  evidence_repo_id: string;
  evidence_repo_name: string;
  evidence_file_path?: string | null;
  confidence: GitHubDetectionConfidence;
  status: GitHubCandidateStatus;
  user_note?: string | null;
  created_at: string;
}

export interface CandidateProject {
  id: string;
  title: string;
  description: string;
  repo_id: string;
  repo_name: string;
  repo_url: string;
  technologies: string[];
  architecture_type: GitHubArchitectureType;
  stars: number;
  is_fork: boolean;
  status: GitHubCandidateStatus;
  user_note?: string | null;
  created_at: string;
}

export interface SyncJobRecord {
  job_id: string;
  repo_id: string;
  repo_name: string;
  status: GitHubSyncStatus;
  started_at: string;
  completed_at?: string | null;
  files_analyzed: number;
  bytes_analyzed: number;
  api_calls_made: number;
  error_message?: string | null;
}

export interface GitHubDiagnostics {
  total_connections: number;
  active_connection_user?: string | null;
  total_discovered_repositories: number;
  total_selected_repositories: number;
  total_analyzed_repositories: number;
  rate_limit_remaining: number;
  rate_limit_limit: number;
  pending_skill_candidates: number;
  pending_project_candidates: number;
  confirmed_claims_count: number;
  cached_etag_entries: number;
  sync_error_count: number;
}

export interface GitHubStatusSummary {
  status: string;
  total_connections: number;
  active_user?: string | null;
  total_discovered_repositories: number;
  total_selected_repositories: number;
  total_analyzed_repositories: number;
  rate_limit: {
    remaining: number;
    limit: number;
  };
  review_queue: {
    pending_skills: number;
    pending_projects: number;
    confirmed_claims: number;
  };
  cache_entries: number;
  errors: number;
}

export interface ConnectGitHubRequest {
  username: string;
  mode?: GitHubConnectionMode;
  access_token?: string | null;
  profile_id?: string;
}

export interface ManualRepoRequest {
  url: string;
  connection_id?: string | null;
}

export interface SelectRepoRequest {
  allow_source_inspection?: boolean;
}

export interface ConfirmCandidateRequest {
  profile_id?: string;
  modified_data?: Record<string, any> | null;
}
