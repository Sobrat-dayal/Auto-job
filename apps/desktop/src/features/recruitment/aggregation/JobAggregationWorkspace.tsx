/**
 * Stage 27: Multi-Source Job Aggregation & Canonical Database Engine.
 * Master Desktop Workspace Container.
 */

import * as React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Layers,
  Building2,
  GitMerge,
  Split,
  AlertTriangle,
  History,
  CheckCircle2,
  RefreshCw,
  Search,
  Sliders,
  ExternalLink,
  ShieldCheck,
  Eye,
  Briefcase,
  MapPin,
  Sparkles,
  Link as LinkIcon,
  Check,
  X,
  UserCheck,
  ArrowRight,
  Database,
} from 'lucide-react';
import { ModulePage, ModuleHeader, ModuleTabs } from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { apiClient } from '@/lib/api-client';
import type {
  AggregationOverviewStats,
  AggregationDiagnosticsReport,
  CanonicalJobRecord,
  CanonicalEmployerRecord,
  DuplicateCandidateRecord,
  AggregationSettingsConfig,
  DuplicateAction,
  MergePreviewResponse,
  SplitPreviewResponse,
} from '@autonom/shared-types';

export const JobAggregationWorkspace: React.FC = () => {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = React.useState<string>('overview');

  // Filters & Selected State
  const [jobSearch, setJobSearch] = React.useState<string>('');
  const [jobStatusFilter, setJobStatusFilter] = React.useState<string>('');
  const [selectedJobId, setSelectedJobId] = React.useState<string | null>(null);

  const [employerSearch, setEmployerSearch] = React.useState<string>('');
  const [rawEmployerInput, setRawEmployerInput] = React.useState<string>('');
  const [employerTestUrl, setEmployerTestUrl] = React.useState<string>('');
  const [resolvedEmployerPreview, setResolvedEmployerPreview] = React.useState<CanonicalEmployerRecord | null>(null);

  // Merge & Split interactive state
  const [survivingMergeId, setSurvivingMergeId] = React.useState<string>('');
  const [supersededMergeId, setSupersededMergeId] = React.useState<string>('');
  const [mergePreview, setMergePreview] = React.useState<MergePreviewResponse | null>(null);

  const [splitJobId, setSplitJobId] = React.useState<string>('');
  const [splitPreview, setSplitPreview] = React.useState<SplitPreviewResponse | null>(null);
  const [selectedSplitSourceIds, setSelectedSplitSourceIds] = React.useState<string[]>([]);

  // 1. Overview Stats Query
  const { data: stats, refetch: refetchStats } = useQuery<AggregationOverviewStats>({
    queryKey: ['aggregation-status'],
    queryFn: () => apiClient.getAggregationStatus(),
    refetchInterval: 15000,
  });

  // 2. Diagnostics Query
  const { data: diagnostics } = useQuery<AggregationDiagnosticsReport>({
    queryKey: ['aggregation-diagnostics'],
    queryFn: () => apiClient.getAggregationDiagnostics(),
  });

  // 3. Canonical Jobs Query
  const { data: canonicalJobs = [], isLoading: loadingJobs, refetch: refetchJobs } = useQuery<CanonicalJobRecord[]>({
    queryKey: ['canonical-jobs', jobSearch, jobStatusFilter],
    queryFn: () =>
      apiClient.listCanonicalJobs({
        query: jobSearch.trim() || undefined,
        status: jobStatusFilter || undefined,
        limit: 50,
      }),
  });

  // 4. Selected Job Detailed Query
  const { data: inspectedJob, refetch: refetchInspectedJob } = useQuery<CanonicalJobRecord | null>({
    queryKey: ['canonical-job-detail', selectedJobId],
    queryFn: () => (selectedJobId ? apiClient.getCanonicalJob(selectedJobId) : Promise.resolve(null)),
    enabled: !!selectedJobId,
  });

  // 5. Selected Job History Query
  const { data: jobHistory = [] } = useQuery<Array<Record<string, any>>>({
    queryKey: ['canonical-job-history', selectedJobId],
    queryFn: () => (selectedJobId ? apiClient.getCanonicalJobHistory(selectedJobId) : Promise.resolve([])),
    enabled: !!selectedJobId,
  });

  // 6. Canonical Employers Query
  const { data: employers = [], isLoading: loadingEmployers, refetch: refetchEmployers } = useQuery<CanonicalEmployerRecord[]>({
    queryKey: ['canonical-employers', employerSearch],
    queryFn: () =>
      apiClient.listCanonicalEmployers({
        query: employerSearch.trim() || undefined,
        limit: 50,
      }),
  });

  // 7. Duplicate Candidates Queue Query
  const { data: duplicateQueue = [], isLoading: loadingDuplicates, refetch: refetchDuplicates } = useQuery<DuplicateCandidateRecord[]>({
    queryKey: ['duplicate-candidates'],
    queryFn: () => apiClient.listDuplicateCandidates(),
  });

  // 8. Global Field Conflicts Query
  const { data: fieldConflicts = [], refetch: refetchConflicts } = useQuery<Array<Record<string, any>>>({
    queryKey: ['global-field-conflicts'],
    queryFn: () => apiClient.listGlobalFieldConflicts(true),
  });

  // 9. Aggregation Tasks Query
  const { data: tasks = [], refetch: refetchTasks } = useQuery<Array<Record<string, any>>>({
    queryKey: ['aggregation-tasks'],
    queryFn: () => apiClient.listAggregationTasks(25),
  });

  // 10. Aggregation Settings Query
  const { data: settings, refetch: refetchSettings } = useQuery<AggregationSettingsConfig>({
    queryKey: ['aggregation-settings'],
    queryFn: () => apiClient.getAggregationSettings(),
  });

  // Mutations
  const syncMutation = useMutation({
    mutationFn: () => apiClient.syncFromDiscovery(100),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['aggregation-status'] });
      queryClient.invalidateQueries({ queryKey: ['canonical-jobs'] });
      queryClient.invalidateQueries({ queryKey: ['aggregation-tasks'] });
    },
  });

  const reviewDecisionMutation = useMutation({
    mutationFn: (vars: { id: string; decision: DuplicateAction; reason: string }) =>
      apiClient.submitDuplicateReview(vars.id, vars.decision, vars.reason),
    onSuccess: () => {
      refetchDuplicates();
      refetchStats();
      refetchJobs();
    },
  });

  const previewMergeMutation = useMutation({
    mutationFn: () => apiClient.previewMergeJobs(survivingMergeId, supersededMergeId),
    onSuccess: (res) => setMergePreview(res),
  });

  const executeMergeMutation = useMutation({
    mutationFn: () => apiClient.executeMergeJobs(survivingMergeId, supersededMergeId),
    onSuccess: () => {
      setMergePreview(null);
      setSurvivingMergeId('');
      setSupersededMergeId('');
      refetchJobs();
      refetchStats();
    },
  });

  const previewSplitMutation = useMutation({
    mutationFn: () => apiClient.previewSplitJob(splitJobId),
    onSuccess: (res) => setSplitPreview(res),
  });

  const executeSplitMutation = useMutation({
    mutationFn: () => apiClient.executeSplitJob(splitJobId, selectedSplitSourceIds),
    onSuccess: () => {
      setSplitPreview(null);
      setSplitJobId('');
      setSelectedSplitSourceIds([]);
      refetchJobs();
      refetchStats();
    },
  });

  const resolveConflictMutation = useMutation({
    mutationFn: (vars: { conflictId: string; chosenValue: any; note: string }) =>
      apiClient.resolveFieldConflict(vars.conflictId, vars.chosenValue, vars.note),
    onSuccess: () => {
      refetchConflicts();
      refetchStats();
      if (selectedJobId) refetchInspectedJob();
    },
  });

  const resolveEmployerMutation = useMutation({
    mutationFn: () =>
      apiClient.resolveEmployer({
        raw_name: rawEmployerInput,
        source_url: employerTestUrl || undefined,
      }),
    onSuccess: (emp) => setResolvedEmployerPreview(emp),
  });

  const updateSettingsMutation = useMutation({
    mutationFn: (newSettings: AggregationSettingsConfig) => apiClient.updateAggregationSettings(newSettings),
    onSuccess: () => refetchSettings(),
  });

  const tabs = [
    { id: 'overview', label: 'Overview & Telemetry', icon: Layers },
    { id: 'jobs', label: `Canonical Jobs (${canonicalJobs.length})`, icon: Briefcase },
    { id: 'employers', label: `Employers (${employers.length})`, icon: Building2 },
    { id: 'duplicate-review', label: `Review Queue (${duplicateQueue.length})`, icon: UserCheck },
    { id: 'merge-split', label: 'Merge & Split Ops', icon: GitMerge },
    { id: 'conflicts', label: `Field Conflicts (${fieldConflicts.length})`, icon: AlertTriangle },
    { id: 'tasks', label: 'Aggregation Tasks', icon: History },
    { id: 'settings', label: 'Aggregation Policy', icon: Sliders },
  ];

  return (
    <ModulePage>
      <ModuleHeader
        title="Multi-Source Job Aggregation & Canonical Database"
        description="Stage 27: Cross-source vacancy reconciliation, employer entity resolution, duplicate detection, field-level conflict tracking, and transactional merge/split history."
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                refetchStats();
                refetchJobs();
                refetchDuplicates();
                refetchEmployers();
              }}
            >
              <RefreshCw className="w-4 h-4 mr-1" />
              Refresh
            </Button>
            <Button
              variant="primary"
              size="sm"
              disabled={syncMutation.isPending}
              onClick={() => syncMutation.mutate()}
            >
              <Database className="w-4 h-4 mr-1" />
              {syncMutation.isPending ? 'Syncing...' : 'Sync from Discovery'}
            </Button>
          </div>
        }
      />

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="p-6 space-y-6">
        {/* ========================================================================= */}
        {/* TAB 1: OVERVIEW & TELEMETRY                                               */}
        {/* ========================================================================= */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardDescription>Canonical Jobs</CardDescription>
                  <CardTitle className="text-3xl font-bold flex items-center justify-between">
                    {stats?.total_canonical_jobs ?? 0}
                    <Briefcase className="w-6 h-6 text-primary opacity-60" />
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-xs text-muted-foreground">
                  <span className="font-semibold text-foreground">{stats?.multi_source_canonical_jobs ?? 0}</span> multi-source linked
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardDescription>Source Observations</CardDescription>
                  <CardTitle className="text-3xl font-bold flex items-center justify-between">
                    {stats?.total_source_observations ?? 0}
                    <Layers className="w-6 h-6 text-primary opacity-60" />
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-xs text-muted-foreground">
                  Aggregated across Stage 26 connectors
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardDescription>Pending Duplicate Reviews</CardDescription>
                  <CardTitle className="text-3xl font-bold flex items-center justify-between">
                    {stats?.pending_duplicate_reviews ?? 0}
                    <UserCheck className="w-6 h-6 text-amber-500 opacity-80" />
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-xs text-muted-foreground">
                  <span className="font-semibold text-emerald-500">{stats?.confirmed_duplicate_merges ?? 0}</span> auto-merged
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardDescription>Active Field Conflicts</CardDescription>
                  <CardTitle className="text-3xl font-bold flex items-center justify-between">
                    {stats?.active_field_conflicts ?? 0}
                    <AlertTriangle className="w-6 h-6 text-rose-500 opacity-80" />
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-xs text-muted-foreground">
                  Salary range or workplace discrepancies
                </CardContent>
              </Card>
            </div>

            {/* Architecture Telemetry & Engine Health */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-500" />
                  Canonical Aggregation Engine Status
                </CardTitle>
                <CardDescription>
                  Autonomous entity resolution & duplicate scoring pipeline diagnostics.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 rounded-lg bg-muted/40 border">
                  <div>
                    <div className="text-xs text-muted-foreground">Database Connected</div>
                    <div className="text-sm font-semibold flex items-center gap-1.5 mt-0.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-500" />
                      {diagnostics?.database_connected ? 'Active (SQLite WAL)' : 'Disconnected'}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-muted-foreground">Resolved Employers</div>
                    <div className="text-sm font-semibold mt-0.5">
                      {diagnostics?.canonical_employers_count ?? employers.length}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-muted-foreground">Auto-Merge Policy</div>
                    <div className="text-sm font-semibold mt-0.5 text-primary">
                      {settings?.auto_merge_enabled ? `Threshold ≥ ${((settings.min_similarity_for_auto_merge || 0.92) * 100).toFixed(0)}%` : 'Disabled'}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-muted-foreground">Requisition Constraint</div>
                    <div className="text-sm font-semibold mt-0.5">
                      {settings?.require_same_requisition ? 'Enforced' : 'Relaxed'}
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2">
                  <div className="text-sm text-muted-foreground">
                    Canonical data infrastructure operates on local SQLite instance with zero automated application submissions.
                  </div>
                  <Button variant="outline" size="sm" onClick={() => setActiveTab('canonical-jobs')}>
                    Browse Canonical Postings
                    <ArrowRight className="w-4 h-4 ml-1.5" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 2: CANONICAL JOBS DIRECTORY                                           */}
        {/* ========================================================================= */}
        {activeTab === 'jobs' && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
              <div className="relative w-full sm:w-96">
                <Search className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search title, requisition, or location..."
                  className="pl-9"
                  value={jobSearch}
                  onChange={(e) => setJobSearch(e.target.value)}
                />
              </div>
              <div className="flex items-center gap-2 w-full sm:w-auto">
                <select
                  className="border rounded-md px-3 py-1.5 text-sm bg-background"
                  value={jobStatusFilter}
                  onChange={(e) => setJobStatusFilter(e.target.value)}
                >
                  <option value="">All Statuses</option>
                  <option value="active">Active</option>
                  <option value="possibly_active">Possibly Active</option>
                  <option value="closed">Closed / Expired</option>
                </select>
                <Button variant="outline" size="sm" onClick={() => refetchJobs()}>
                  <RefreshCw className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {loadingJobs ? (
              <div className="p-12 text-center text-muted-foreground">Loading canonical job records...</div>
            ) : canonicalJobs.length === 0 ? (
              <Card className="p-12 text-center">
                <Briefcase className="w-12 h-12 mx-auto text-muted-foreground opacity-40 mb-3" />
                <h3 className="text-base font-semibold">No Canonical Jobs Found</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Run "Sync from Discovery" or ingest observations from Stage 26 job discovery connectors.
                </p>
                <Button className="mt-4" size="sm" onClick={() => syncMutation.mutate()} disabled={syncMutation.isPending}>
                  Sync Discovered Postings
                </Button>
              </Card>
            ) : (
              <div className="grid grid-cols-1 gap-3">
                {canonicalJobs.map((job) => (
                  <Card key={job.id} className="hover:border-primary/50 transition-colors">
                    <CardContent className="p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                      <div className="space-y-1.5">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-semibold text-base">{job.display_title}</span>
                          <Badge variant="outline" className="text-xs">
                            {job.employer_name}
                          </Badge>
                          {job.requisition_id && (
                            <Badge variant="neutral" className="font-mono text-xs">
                              REQ: {job.requisition_id}
                            </Badge>
                          )}
                          <Badge
                            className={
                              job.status === 'active'
                                ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20'
                                : 'bg-muted text-muted-foreground'
                            }
                          >
                            {job.status}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            v{job.version}
                          </Badge>
                        </div>

                        <div className="flex items-center gap-4 text-xs text-muted-foreground flex-wrap">
                          {job.location_summary && (
                            <span className="flex items-center gap-1">
                              <MapPin className="w-3.5 h-3.5" />
                              {job.location_summary}
                            </span>
                          )}
                          {job.work_arrangement && (
                            <span className="capitalize">Mode: {job.work_arrangement}</span>
                          )}
                          {job.compensation_summary && (
                            <span className="text-foreground font-medium">{job.compensation_summary}</span>
                          )}
                          <span className="flex items-center gap-1 text-primary font-medium">
                            <LinkIcon className="w-3.5 h-3.5" />
                            {job.source_count} {job.source_count === 1 ? 'source' : 'sources linked'}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 w-full md:w-auto justify-end">
                        {job.primary_url && (
                          <a
                            href={job.primary_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-muted-foreground hover:text-foreground inline-flex items-center gap-1 p-2"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedJobId(job.id);
                            setActiveTab('job-details');
                          }}
                        >
                          <Eye className="w-4 h-4 mr-1.5" />
                          Inspect Details
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 3: JOB DETAILS & PROVENANCE INSPECTOR                                 */}
        {/* ========================================================================= */}
        {activeTab === 'job-details' && (
          <div className="space-y-6">
            {!inspectedJob ? (
              <Card className="p-8 text-center text-muted-foreground">
                <p>Select a job from the Canonical Jobs tab to inspect its full provenance and history.</p>
                <Button className="mt-3" variant="outline" size="sm" onClick={() => setActiveTab('jobs')}>
                  Go to Canonical Jobs
                </Button>
              </Card>
            ) : (
              <div className="space-y-6">
                <div className="flex items-center justify-between border-b pb-4">
                  <div>
                    <h2 className="text-xl font-bold">{inspectedJob.display_title}</h2>
                    <p className="text-sm text-muted-foreground mt-0.5">
                      Canonical ID: <code className="font-mono text-xs">{inspectedJob.id}</code> | Employer:{' '}
                      <span className="font-semibold text-foreground">{inspectedJob.employer_name}</span>
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => setActiveTab('jobs')}>
                      Back to Directory
                    </Button>
                  </div>
                </div>

                {/* Linked Sources Provenance */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <LinkIcon className="w-4 h-4 text-primary" />
                      Associated Source Observations ({inspectedJob.sources?.length ?? 0})
                    </CardTitle>
                    <CardDescription>
                      Individual job board and career page listings merged into this canonical entity.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {inspectedJob.sources?.map((source) => (
                      <div
                        key={source.id}
                        className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-3 rounded-lg border bg-muted/20 gap-3"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <Badge variant="neutral" className="capitalize">
                              {source.provider}
                            </Badge>
                            <span className="font-mono text-xs text-muted-foreground">
                              Posting ID: {source.native_posting_id}
                            </span>
                            {source.is_primary && (
                              <Badge className="bg-primary/10 text-primary border-primary/20 text-xs">Primary</Badge>
                            )}
                          </div>
                          <div className="text-xs text-muted-foreground truncate max-w-xl">
                            {source.original_url}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <a
                            href={source.original_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-1.5 text-muted-foreground hover:text-foreground"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {/* Version History */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <History className="w-4 h-4 text-primary" />
                      Immutable Revision History (v{inspectedJob.version})
                    </CardTitle>
                    <CardDescription>Audit snapshots recorded on every merge, split, or field reconciliation.</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {jobHistory.length === 0 ? (
                      <div className="text-xs text-muted-foreground">No historical revisions recorded yet.</div>
                    ) : (
                      <div className="space-y-2">
                        {jobHistory.map((rev) => (
                          <div key={rev.id} className="p-3 rounded-lg border text-xs space-y-1">
                            <div className="flex items-center justify-between font-semibold">
                              <span>Version #{rev.version_number}</span>
                              <span className="text-muted-foreground font-normal">{rev.created_at}</span>
                            </div>
                            <div className="text-muted-foreground">{rev.change_summary}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 4: CANONICAL EMPLOYERS DIRECTORY                                      */}
        {/* ========================================================================= */}
        {activeTab === 'employers' && (
          <div className="space-y-6">
            {/* On-Demand Identity Resolver Tool */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-500" />
                  Interactive Employer Identity Resolver
                </CardTitle>
                <CardDescription>
                  Simulate Stage 27 5-stage identity resolution (ATS token match, legal suffix normalization, domain verification, and staffing agency classification).
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-semibold text-muted-foreground">Raw Employer Name</label>
                    <Input
                      placeholder="e.g. Stripe, Inc. or Robert Half"
                      value={rawEmployerInput}
                      onChange={(e) => setRawEmployerInput(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-muted-foreground">Source or Careers URL (Optional)</label>
                    <Input
                      placeholder="e.g. https://stripe.com/jobs or boards.greenhouse.io/stripe"
                      value={employerTestUrl}
                      onChange={(e) => setEmployerTestUrl(e.target.value)}
                    />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <Button
                    size="sm"
                    disabled={!rawEmployerInput.trim() || resolveEmployerMutation.isPending}
                    onClick={() => resolveEmployerMutation.mutate()}
                  >
                    {resolveEmployerMutation.isPending ? 'Resolving...' : 'Resolve Employer Identity'}
                  </Button>
                </div>

                {resolvedEmployerPreview && (
                  <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 space-y-2 mt-3">
                    <div className="text-xs font-semibold text-emerald-600">Resolved Canonical Employer:</div>
                    <div className="text-sm font-bold">{resolvedEmployerPreview.name}</div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-muted-foreground pt-1">
                      <div>Organization Type: <span className="font-semibold text-foreground">{resolvedEmployerPreview.organization_type}</span></div>
                      <div>Identity Status: <span className="font-semibold text-foreground">{resolvedEmployerPreview.identity_status}</span></div>
                      <div>Primary Domain: <span className="font-semibold text-foreground">{resolvedEmployerPreview.primary_domain || 'N/A'}</span></div>
                      <div>Confidence Score: <span className="font-semibold text-emerald-600">{(resolvedEmployerPreview.confidence_score * 100).toFixed(0)}%</span></div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Employers List */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-base">Registered Canonical Employers</h3>
                <Input
                  placeholder="Filter employers..."
                  className="w-64 text-xs"
                  value={employerSearch}
                  onChange={(e) => setEmployerSearch(e.target.value)}
                />
              </div>

              {loadingEmployers ? (
                <div className="p-8 text-center text-muted-foreground">Loading employers...</div>
              ) : employers.length === 0 ? (
                <div className="p-8 text-center text-muted-foreground border rounded-lg">No employers registered yet.</div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {employers.map((emp) => (
                    <Card key={emp.id} className="p-4 space-y-2">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="font-bold text-sm">{emp.name}</div>
                          {emp.legal_name && <div className="text-xs text-muted-foreground">{emp.legal_name}</div>}
                        </div>
                        <Badge variant="outline" className="capitalize text-xs">
                          {emp.organization_type.replace('_', ' ')}
                        </Badge>
                      </div>
                      <div className="text-xs text-muted-foreground space-y-1">
                        <div>Domain: <span className="font-mono text-foreground">{emp.primary_domain || 'Unverified'}</span></div>
                        <div>Aliases: <span className="font-semibold text-foreground">{emp.aliases?.length ?? 0}</span> registered</div>
                        <div>Verified Boards: <span className="font-semibold text-foreground">{emp.provider_boards?.length ?? 0}</span></div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 5: DUPLICATE REVIEW QUEUE                                             */}
        {/* ========================================================================= */}
        {activeTab === 'duplicate-review' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold">Human Duplicate Review Queue</h3>
                <p className="text-xs text-muted-foreground">
                  Ambiguous or high-confidence pairs requiring human confirmation before merging.
                </p>
              </div>
              <Button variant="outline" size="sm" onClick={() => refetchDuplicates()}>
                <RefreshCw className="w-4 h-4 mr-1.5" />
                Refresh Queue
              </Button>
            </div>

            {loadingDuplicates ? (
              <div className="p-12 text-center text-muted-foreground">Loading duplicate candidates...</div>
            ) : duplicateQueue.length === 0 ? (
              <Card className="p-12 text-center">
                <CheckCircle2 className="w-12 h-12 mx-auto text-emerald-500 opacity-60 mb-3" />
                <h3 className="text-base font-semibold">Review Queue is Clear</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  All duplicate candidates have been evaluated or auto-merged according to policy thresholds.
                </p>
              </Card>
            ) : (
              <div className="space-y-4">
                {duplicateQueue.map((cand) => (
                  <Card key={cand.id} className="p-4 space-y-4">
                    <div className="flex items-center justify-between border-b pb-2">
                      <div className="flex items-center gap-2">
                        <Badge className="bg-amber-500/10 text-amber-600 border-amber-500/20">
                          Similarity: {(cand.similarity_score * 100).toFixed(1)}%
                        </Badge>
                        <Badge variant="outline" className="capitalize">
                          Recommended: {cand.recommended_action}
                        </Badge>
                      </div>
                      <span className="text-xs text-muted-foreground">{cand.created_at}</span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-3 rounded-lg border bg-muted/10 space-y-1">
                        <div className="text-xs font-semibold text-muted-foreground">Job A (Surviving Candidate)</div>
                        <div className="font-mono text-xs">{cand.left_job_id}</div>
                      </div>
                      <div className="p-3 rounded-lg border bg-muted/10 space-y-1">
                        <div className="text-xs font-semibold text-muted-foreground">Job B (Duplicate Candidate)</div>
                        <div className="font-mono text-xs">{cand.right_job_id}</div>
                      </div>
                    </div>

                    <div className="flex items-center justify-end gap-2 pt-2 border-t">
                      <Button
                        size="sm"
                        variant="primary"
                        disabled={reviewDecisionMutation.isPending}
                        onClick={() =>
                          reviewDecisionMutation.mutate({
                            id: cand.id,
                            decision: 'merge',
                            reason: 'User approved duplicate merge',
                          })
                        }
                      >
                        <Check className="w-4 h-4 mr-1.5" />
                        Confirm & Merge
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        disabled={reviewDecisionMutation.isPending}
                        onClick={() =>
                          reviewDecisionMutation.mutate({
                            id: cand.id,
                            decision: 'keep_separate',
                            reason: 'Confirmed distinct roles',
                          })
                        }
                      >
                        <X className="w-4 h-4 mr-1.5" />
                        Keep Separate
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        disabled={reviewDecisionMutation.isPending}
                        onClick={() =>
                          reviewDecisionMutation.mutate({
                            id: cand.id,
                            decision: 'mark_related',
                            reason: 'Related roles under same company',
                          })
                        }
                      >
                        Mark Related
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 6: MERGE & SPLIT OPERATIONS CENTER                                    */}
        {/* ========================================================================= */}
        {activeTab === 'merge-split' && (
          <div className="space-y-8">
            {/* Merge Section */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <GitMerge className="w-5 h-5 text-primary" />
                  Transactional Canonical Job Merge
                </CardTitle>
                <CardDescription>
                  Merge an erroneous duplicate job into a surviving canonical job with atomic alias supersession and audit history.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-semibold text-muted-foreground">Surviving Job ID (absorbs sources)</label>
                    <Input
                      placeholder="e.g. cjob_12345678"
                      value={survivingMergeId}
                      onChange={(e) => setSurvivingMergeId(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-muted-foreground">Superseded Job ID (will be closed)</label>
                    <Input
                      placeholder="e.g. cjob_87654321"
                      value={supersededMergeId}
                      onChange={(e) => setSupersededMergeId(e.target.value)}
                    />
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={!survivingMergeId || !supersededMergeId || previewMergeMutation.isPending}
                    onClick={() => previewMergeMutation.mutate()}
                  >
                    Preview Merge Impact
                  </Button>
                  {mergePreview && (
                    <Button
                      size="sm"
                      variant="destructive"
                      disabled={executeMergeMutation.isPending}
                      onClick={() => executeMergeMutation.mutate()}
                    >
                      Execute Atomic Merge
                    </Button>
                  )}
                </div>

                {mergePreview && (
                  <div className="p-4 rounded-lg bg-muted/30 border space-y-2 text-xs">
                    <div className="font-semibold text-foreground text-sm">Merge Safety Preview:</div>
                    <div>Safe to Merge: <span className={mergePreview.is_safe_to_merge ? 'text-emerald-500 font-bold' : 'text-rose-500 font-bold'}>{mergePreview.is_safe_to_merge ? 'YES' : 'CONFLICTS DETECTED'}</span></div>
                    <div>Resulting Source Count: {mergePreview.resulting_source_count}</div>
                    <div>Sources to Transfer: {mergePreview.source_links_to_transfer.length}</div>
                    {mergePreview.warnings.length > 0 && (
                      <div className="text-amber-500 font-medium">Warnings: {mergePreview.warnings.join(', ')}</div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Split Section */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <Split className="w-5 h-5 text-indigo-500" />
                  Transactional Canonical Job Split / Unmerge
                </CardTitle>
                <CardDescription>
                  Reverse an incorrect merge by detaching specific source links into a newly created canonical job identity.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-end gap-2">
                  <div className="flex-1">
                    <label className="text-xs font-semibold text-muted-foreground">Original Job ID to Split</label>
                    <Input
                      placeholder="e.g. cjob_12345678"
                      value={splitJobId}
                      onChange={(e) => setSplitJobId(e.target.value)}
                    />
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={!splitJobId || previewSplitMutation.isPending}
                    onClick={() => previewSplitMutation.mutate()}
                  >
                    Load Attached Sources
                  </Button>
                </div>

                {splitPreview && (
                  <div className="space-y-3 pt-2">
                    <div className="text-xs font-semibold text-muted-foreground">Select sources to detach into a new job:</div>
                    <div className="space-y-2">
                      {splitPreview.source_links.map((link) => (
                        <label
                          key={link.id}
                          className="flex items-center gap-3 p-3 rounded-lg border bg-muted/20 cursor-pointer"
                        >
                          <input
                            type="checkbox"
                            checked={selectedSplitSourceIds.includes(link.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedSplitSourceIds([...selectedSplitSourceIds, link.id]);
                              } else {
                                setSelectedSplitSourceIds(selectedSplitSourceIds.filter((id) => id !== link.id));
                              }
                            }}
                          />
                          <div className="text-xs space-y-0.5">
                            <span className="font-semibold text-foreground capitalize">{link.provider}</span> |{' '}
                            <span className="font-mono text-muted-foreground">ID: {link.native_posting_id}</span>
                            <div className="text-muted-foreground truncate max-w-lg">{link.original_url}</div>
                          </div>
                        </label>
                      ))}
                    </div>

                    <Button
                      size="sm"
                      variant="destructive"
                      disabled={selectedSplitSourceIds.length === 0 || executeSplitMutation.isPending}
                      onClick={() => executeSplitMutation.mutate()}
                    >
                      Execute Split ({selectedSplitSourceIds.length} sources)
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 7: GLOBAL FIELD CONFLICTS                                             */}
        {/* ========================================================================= */}
        {activeTab === 'conflicts' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold">Field Discrepancy & Conflict Resolver</h3>
                <p className="text-xs text-muted-foreground">
                  Inconsistencies detected across sources (e.g. differing salary ranges, remote policies, or titles).
                </p>
              </div>
              <Button variant="outline" size="sm" onClick={() => refetchConflicts()}>
                <RefreshCw className="w-4 h-4 mr-1.5" />
                Refresh Conflicts
              </Button>
            </div>

            {fieldConflicts.length === 0 ? (
              <Card className="p-12 text-center">
                <CheckCircle2 className="w-12 h-12 mx-auto text-emerald-500 opacity-60 mb-3" />
                <h3 className="text-base font-semibold">Zero Unresolved Field Conflicts</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  All multi-source field values are consistent or have been automatically reconciled by source authority weights.
                </p>
              </Card>
            ) : (
              <div className="space-y-3">
                {fieldConflicts.map((conf) => (
                  <Card key={conf.id} className="p-4 space-y-3">
                    <div className="flex items-center justify-between border-b pb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="error" className="capitalize">
                          {conf.field_name} Conflict
                        </Badge>
                        <span className="text-xs font-mono text-muted-foreground">Job: {conf.canonical_job_id}</span>
                      </div>
                      <Badge variant="outline" className="text-xs capitalize">
                        {conf.status}
                      </Badge>
                    </div>

                    <div className="p-3 rounded-lg bg-muted/20 border text-xs">
                      <div className="font-semibold text-muted-foreground mb-1">Conflicting Source Values:</div>
                      <pre className="font-mono text-xs overflow-x-auto">
                        {JSON.stringify(conf.source_values, null, 2)}
                      </pre>
                    </div>

                    <div className="flex items-center justify-end gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        disabled={resolveConflictMutation.isPending}
                        onClick={() => {
                          const values = Object.values(conf.source_values || {});
                          const chosen = values[0] || 'Default value';
                          resolveConflictMutation.mutate({
                            conflictId: conf.id,
                            chosenValue: chosen,
                            note: 'Chosen via desktop UI',
                          });
                        }}
                      >
                        Accept Authoritative Value
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 8: TASKS & AUDIT LOGS                                                 */}
        {/* ========================================================================= */}
        {activeTab === 'tasks' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold">Aggregation Tasks History</h3>
                <p className="text-xs text-muted-foreground">Execution history of batch ingestion and duplicate sweeps.</p>
              </div>
              <Button variant="outline" size="sm" onClick={() => refetchTasks()}>
                <RefreshCw className="w-4 h-4 mr-1.5" />
                Refresh
              </Button>
            </div>

            {tasks.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground border rounded-lg">No tasks recorded yet.</div>
            ) : (
              <div className="space-y-2">
                {tasks.map((t) => (
                  <Card key={t.id} className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-semibold">{t.id}</span>
                        <Badge variant="outline" className="capitalize">
                          {t.task_type}
                        </Badge>
                        <Badge
                          className={
                            t.status === 'completed'
                              ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20'
                              : 'bg-amber-500/10 text-amber-600 border-amber-500/20'
                          }
                        >
                          {t.status}
                        </Badge>
                      </div>
                      <span className="text-xs text-muted-foreground">{t.created_at}</span>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 9: AGGREGATION POLICY & SETTINGS                                      */}
        {/* ========================================================================= */}
        {activeTab === 'settings' && (
          <div className="space-y-6 max-w-2xl">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Aggregation Policy Configuration</CardTitle>
                <CardDescription>
                  Tune duplicate similarity thresholds, requisition constraints, and auto-merge behaviors.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between py-2 border-b">
                  <div>
                    <div className="font-semibold text-sm">Automatic Merging</div>
                    <div className="text-xs text-muted-foreground">
                      Automatically combine exact requisition or high-confidence matches without manual intervention.
                    </div>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings?.auto_merge_enabled ?? true}
                    onChange={(e) => {
                      if (settings) {
                        updateSettingsMutation.mutate({ ...settings, auto_merge_enabled: e.target.checked });
                      }
                    }}
                  />
                </div>

                <div className="flex items-center justify-between py-2 border-b">
                  <div>
                    <div className="font-semibold text-sm">Enforce Identical Requisition ID</div>
                    <div className="text-xs text-muted-foreground">
                      Strictly prohibit merging vacancies under the same company that possess differing requisition IDs.
                    </div>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings?.require_same_requisition ?? true}
                    onChange={(e) => {
                      if (settings) {
                        updateSettingsMutation.mutate({ ...settings, require_same_requisition: e.target.checked });
                      }
                    }}
                  />
                </div>

                <div className="space-y-1.5 py-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-semibold">Minimum Auto-Merge Similarity</span>
                    <span className="font-mono text-primary font-bold">
                      {(((settings?.min_similarity_for_auto_merge ?? 0.92)) * 100).toFixed(0)}%
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0.80"
                    max="0.99"
                    step="0.01"
                    className="w-full cursor-pointer"
                    value={settings?.min_similarity_for_auto_merge ?? 0.92}
                    onChange={(e) => {
                      if (settings) {
                        updateSettingsMutation.mutate({
                          ...settings,
                          min_similarity_for_auto_merge: parseFloat(e.target.value),
                        });
                      }
                    }}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </ModulePage>
  );
};
