/**
 * Stage 29: Applicant-to-Job Matching and Opportunity Prioritization Workspace.
 * Master Desktop Workspace Container.
 */

import * as React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Trophy,
  ListOrdered,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ShieldAlert,
  GitCompare,
  Sliders,
  Sparkles,
  HelpCircle,
  FileCheck,
  Search,
  RefreshCw,
  Layers,
  Play,
} from 'lucide-react';
import { ModulePage, ModuleHeader, ModuleTabs } from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';
import type {
  MatchingOutcome,
  SimulationRequest,
  SimulationResponse,
} from '@autonom/shared-types';

export const JobMatchingWorkspace: React.FC = () => {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = React.useState<string>('overview');
  const [selectedEvaluationId, setSelectedEvaluationId] = React.useState<string | null>(null);
  const [searchQuery, setSearchQuery] = React.useState<string>('');
  const [comparisonJobIds, setComparisonJobIds] = React.useState<string[]>([]);

  // Simulation form states
  const [simScenarioName, setSimScenarioName] = React.useState<string>('Add Skills & Authorization');
  const [simHypoSkills, setSimHypoSkills] = React.useState<string>('Kubernetes, Go');
  const [simHypoMinSalary, setSimHypoMinSalary] = React.useState<string>('');
  const [simHypoConfirmAuth, setSimHypoConfirmAuth] = React.useState<boolean>(true);
  const [simulationResult, setSimulationResult] = React.useState<SimulationResponse | null>(null);

  // Queries
  const { refetch: refetchRankings } = useQuery({
    queryKey: ['matchingStatus'],
    queryFn: () => apiClient.getMatchingStatus(),
  });

  const { data: rankingsData, refetch: refetchRankingsData } = useQuery({
    queryKey: ['opportunityRankings'],
    queryFn: () => apiClient.getOpportunityRankings(),
  });

  const { data: evaluationsData, refetch: refetchEvaluations } = useQuery({
    queryKey: ['matchEvaluations'],
    queryFn: () => apiClient.listMatchResults(),
  });

  const { data: reviewQueueData, refetch: refetchReviewQueue } = useQuery({
    queryKey: ['matchingReviewQueue'],
    queryFn: () => apiClient.getMatchingReviewQueue(),
  });

  const { data: rubricsData } = useQuery({
    queryKey: ['matchingRubrics'],
    queryFn: () => apiClient.listMatchingRubrics(),
  });

  // Selected Evaluation Query
  const selectedEvaluation = React.useMemo(() => {
    if (!evaluationsData) return null;
    if (selectedEvaluationId) {
      return evaluationsData.find((e) => e.id === selectedEvaluationId) || evaluationsData[0] || null;
    }
    return evaluationsData[0] || null;
  }, [evaluationsData, selectedEvaluationId]);

  // Mutations
  const generateRankingsMutation = useMutation({
    mutationFn: () => apiClient.generateRankings(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunityRankings'] });
      queryClient.invalidateQueries({ queryKey: ['matchEvaluations'] });
    },
  });

  const resolveReviewMutation = useMutation({
    mutationFn: ({ id, notes, decision }: { id: string; notes: string; decision: string }) =>
      apiClient.resolveMatchingReviewItem(id, notes, decision),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matchingReviewQueue'] });
    },
  });

  const simulationMutation = useMutation({
    mutationFn: (req: SimulationRequest) => apiClient.simulateMatchingScenario(req),
    onSuccess: (data) => {
      setSimulationResult(data);
    },
  });

  const handleRunSimulation = () => {
    if (!selectedEvaluation) return;
    const skills = simHypoSkills.split(',').map((s) => s.trim()).filter(Boolean);
    const minSalary = simHypoMinSalary ? parseFloat(simHypoMinSalary) : null;
    simulationMutation.mutate({
      evaluation_id: selectedEvaluation.id,
      scenario_name: simScenarioName,
      hypothetical_skills: skills,
      hypothetical_min_salary: minSalary,
      hypothetical_confirm_work_auth: simHypoConfirmAuth,
    });
  };

  // Filtered Ranked Opportunities
  const rankedItems = rankingsData?.items || [];
  const overview = rankingsData?.overview;

  const filteredRankedItems = React.useMemo(() => {
    if (!searchQuery.trim()) return rankedItems;
    const q = searchQuery.toLowerCase();
    return rankedItems.filter(
      (item) =>
        item.job_title.toLowerCase().includes(q) ||
        item.company_name.toLowerCase().includes(q) ||
        (item.location && item.location.toLowerCase().includes(q))
    );
  }, [rankedItems, searchQuery]);

  const toggleCompareJob = (jobId: string) => {
    setComparisonJobIds((prev) =>
      prev.includes(jobId) ? prev.filter((id) => id !== jobId) : prev.length < 4 ? [...prev, jobId] : prev
    );
  };

  const getOutcomeBadge = (outcome: MatchingOutcome | string) => {
    switch (outcome) {
      case 'eligible_and_aligned':
        return <Badge className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Eligible & Aligned</Badge>;
      case 'conditionally_eligible':
        return <Badge className="bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">Conditionally Eligible</Badge>;
      case 'eligible_but_lower_priority':
        return <Badge className="bg-blue-500/20 text-blue-400 border border-blue-500/30">Lower Priority</Badge>;
      case 'requires_applicant_review':
        return <Badge className="bg-amber-500/20 text-amber-400 border border-amber-500/30">Review Required</Badge>;
      case 'missing_critical_information':
        return <Badge className="bg-orange-500/20 text-orange-400 border border-orange-500/30">Missing Info</Badge>;
      case 'known_requirement_not_met':
        return <Badge className="bg-rose-500/20 text-rose-400 border border-rose-500/30">Requirements Unmet</Badge>;
      case 'rejected_by_hard_policy':
        return <Badge className="bg-red-500/20 text-red-400 border border-red-500/30">Hard Policy Excluded</Badge>;
      case 'job_unavailable':
        return <Badge className="bg-slate-500/20 text-slate-400 border border-slate-500/30">Unavailable</Badge>;
      default:
        return <Badge className="bg-slate-700 text-slate-300">Not Evaluated</Badge>;
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Trophy },
    { id: 'rankings', label: 'Ranked Opportunities', icon: ListOrdered },
    { id: 'details', label: 'Match Details', icon: FileCheck },
    { id: 'matrix', label: 'Qualification Matrix', icon: Layers },
    { id: 'gaps', label: 'Skill Gap Explorer', icon: AlertTriangle },
    { id: 'relevance', label: 'Relevance Explanations', icon: Sliders },
    { id: 'comparison', label: `Comparison (${comparisonJobIds.length})`, icon: GitCompare },
    { id: 'simulation', label: 'What-If Simulator', icon: Sparkles },
    { id: 'review_queue', label: `Review Queue (${reviewQueueData?.length || 0})`, icon: HelpCircle },
    { id: 'settings', label: 'Rubric & Settings', icon: Sliders },
  ];

  return (
    <ModulePage>
      <ModuleHeader
        title="Job Matching & Prioritization Engine"
        description="Stage 29 — Evidence-based qualification evaluation, career policy scoring, and explainable ranking"
      >
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              refetchRankings();
              refetchRankingsData();
              refetchEvaluations();
              refetchReviewQueue();
            }}
            className="border-[#1e293b] bg-[#0f172a] text-slate-300 hover:text-white"
          >
            <RefreshCw className="mr-1 h-3.5 w-3.5" />
            Refresh
          </Button>
          <Button
            size="sm"
            disabled={generateRankingsMutation.isPending}
            onClick={() => generateRankingsMutation.mutate()}
            className="bg-blue-600 hover:bg-blue-500 text-white font-medium"
          >
            <Play className="mr-1 h-3.5 w-3.5" />
            Recalculate Rankings
          </Button>
        </div>
      </ModuleHeader>

      <div className="border-b border-slate-800 bg-slate-950/60 px-6">
        <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      <div className="p-6 space-y-6">
        {/* =========================================================================
            TAB 1: OVERVIEW DASHBOARD
           ========================================================================= */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
              <div className="p-4 rounded-lg bg-[#0f172a] border border-[#1e293b]">
                <div className="text-xs text-slate-400 font-medium">Total Evaluated</div>
                <div className="mt-1 text-2xl font-bold text-white">{overview?.total_evaluated || 0}</div>
                <div className="mt-1 text-[11px] text-slate-500">Current vacancies</div>
              </div>
              <div className="p-4 rounded-lg bg-[#0f172a] border border-emerald-500/20">
                <div className="text-xs text-emerald-400 font-medium">Eligible & Aligned</div>
                <div className="mt-1 text-2xl font-bold text-emerald-300">{overview?.eligible_and_aligned || 0}</div>
                <div className="mt-1 text-[11px] text-emerald-500">Ready for prep</div>
              </div>
              <div className="p-4 rounded-lg bg-[#0f172a] border border-cyan-500/20">
                <div className="text-xs text-cyan-400 font-medium">Conditionally Eligible</div>
                <div className="mt-1 text-2xl font-bold text-cyan-300">{overview?.conditionally_eligible || 0}</div>
                <div className="mt-1 text-[11px] text-cyan-500">Via practical waiver</div>
              </div>
              <div className="p-4 rounded-lg bg-[#0f172a] border border-amber-500/20">
                <div className="text-xs text-amber-400 font-medium">Requires Review</div>
                <div className="mt-1 text-2xl font-bold text-amber-300">{overview?.requires_review || 0}</div>
                <div className="mt-1 text-[11px] text-amber-500">Unknown facts</div>
              </div>
              <div className="p-4 rounded-lg bg-[#0f172a] border border-rose-500/20">
                <div className="text-xs text-rose-400 font-medium">Unmet Mandatory</div>
                <div className="mt-1 text-2xl font-bold text-rose-300">{overview?.known_unmet || 0}</div>
                <div className="mt-1 text-[11px] text-rose-500">Missing reqs</div>
              </div>
              <div className="p-4 rounded-lg bg-[#0f172a] border border-red-500/20">
                <div className="text-xs text-red-400 font-medium">Policy Excluded</div>
                <div className="mt-1 text-2xl font-bold text-red-300">{overview?.hard_policy_excluded || 0}</div>
                <div className="mt-1 text-[11px] text-red-500">Blocklist/floors</div>
              </div>
              <div className="p-4 rounded-lg bg-[#0f172a] border border-blue-500/20">
                <div className="text-xs text-blue-400 font-medium">Avg Relevance</div>
                <div className="mt-1 text-2xl font-bold text-blue-300">{overview?.average_relevance_index || 0}%</div>
                <div className="mt-1 text-[11px] text-blue-500">Deterministic index</div>
              </div>
            </div>

            {/* Quick Actions & Top Opportunities */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 p-5 rounded-lg bg-[#0f172a] border border-[#1e293b]">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <Trophy className="h-4 w-4 text-cyan-400" />
                    Top Ranked Recommended Opportunities
                  </h3>
                  <Button variant="ghost" size="sm" onClick={() => setActiveTab('rankings')} className="text-xs text-cyan-400">
                    View All Rankings →
                  </Button>
                </div>
                {rankedItems.length === 0 ? (
                  <div className="py-8 text-center text-sm text-slate-400">
                    No evaluated vacancies found. Click &quot;Recalculate Rankings&quot; to evaluate discovered jobs.
                  </div>
                ) : (
                  <div className="divide-y divide-[#1e293b]">
                    {rankedItems.slice(0, 5).map((job) => (
                      <div key={job.evaluation_id} className="py-3 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-6 text-center font-bold text-slate-400 text-sm">#{job.rank}</div>
                          <div>
                            <div className="text-sm font-medium text-white">{job.job_title}</div>
                            <div className="text-xs text-slate-400 flex items-center gap-2">
                              <span>{job.company_name}</span>
                              <span>•</span>
                              <span>{job.location || 'Remote'}</span>
                              <span>•</span>
                              <span>{job.work_arrangement || 'Standard'}</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          {getOutcomeBadge(job.eligibility_outcome)}
                          <div className="text-right">
                            <div className="text-sm font-bold text-cyan-400">{job.relevance_index.toFixed(1)}/100</div>
                            <div className="text-[10px] text-slate-500">Relevance</div>
                          </div>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setSelectedEvaluationId(job.evaluation_id);
                              setActiveTab('details');
                            }}
                            className="border-[#1e293b] text-xs"
                          >
                            Inspect
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Guardrails and Privacy Info */}
              <div className="p-5 rounded-lg bg-[#0f172a] border border-[#1e293b] space-y-4">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <ShieldAlert className="h-4 w-4 text-emerald-400" />
                  Matching Intelligence Guardrails
                </h3>
                <div className="space-y-3 text-xs text-slate-300">
                  <div className="p-2.5 rounded bg-[#0a0f1d] border border-[#1e293b]">
                    <div className="font-medium text-emerald-400">Zero Synthetic Guessing</div>
                    <div className="mt-0.5 text-slate-400">
                      Unrecorded salaries, unconfirmed work authorization, and unevidenced skills remain strictly uninvented.
                    </div>
                  </div>
                  <div className="p-2.5 rounded bg-[#0a0f1d] border border-[#1e293b]">
                    <div className="font-medium text-cyan-400">Hard Constraint Precedence</div>
                    <div className="mt-0.5 text-slate-400">
                      High relevance scores never bypass employer blocklists, salary floors, or geographic bans.
                    </div>
                  </div>
                  <div className="p-2.5 rounded bg-[#0a0f1d] border border-[#1e293b]">
                    <div className="font-medium text-blue-400">Protected Attributes Protected</div>
                    <div className="mt-0.5 text-slate-400">
                      Demographic assumptions, race, gender, and school fame are completely excluded from scoring.
                    </div>
                  </div>
                  <div className="p-2.5 rounded bg-[#0a0f1d] border border-[#1e293b]">
                    <div className="font-medium text-amber-400">No Auto-Submission Authority</div>
                    <div className="mt-0.5 text-slate-400">
                      An &quot;Eligible & Aligned&quot; outcome approves downstream preparation only. Live application submissions remain prohibited.
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            TAB 2: RANKED OPPORTUNITIES TABLE
           ========================================================================= */}
        {activeTab === 'rankings' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between gap-4">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                <Input
                  placeholder="Filter by role, employer, or location..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 bg-[#0f172a] border-[#1e293b] text-white"
                />
              </div>
              <div className="text-xs text-slate-400">
                Showing {filteredRankedItems.length} of {rankedItems.length} opportunities
              </div>
            </div>

            <div className="overflow-x-auto rounded-lg border border-[#1e293b] bg-[#0f172a]">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#0a0f1d] border-b border-[#1e293b] text-slate-400 uppercase tracking-wider text-[10px]">
                  <tr>
                    <th className="py-3 px-3 w-12 text-center">Rank</th>
                    <th className="py-3 px-4">Opportunity</th>
                    <th className="py-3 px-3">Location & Type</th>
                    <th className="py-3 px-3">Eligibility State</th>
                    <th className="py-3 px-3 text-center">Mandatory</th>
                    <th className="py-3 px-3 text-center">Preferred</th>
                    <th className="py-3 px-3 text-center">Gaps</th>
                    <th className="py-3 px-3 text-right">Relevance</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e293b] text-slate-300">
                  {filteredRankedItems.map((job) => (
                    <tr key={job.evaluation_id} className="hover:bg-[#131f37] transition-colors">
                      <td className="py-3 px-3 text-center font-bold text-slate-400">#{job.rank}</td>
                      <td className="py-3 px-4">
                        <div className="font-semibold text-white">{job.job_title}</div>
                        <div className="text-[11px] text-slate-400">{job.company_name}</div>
                      </td>
                      <td className="py-3 px-3">
                        <div>{job.location || 'Remote'}</div>
                        <div className="text-[11px] text-slate-500">{job.work_arrangement || 'Onsite'}</div>
                      </td>
                      <td className="py-3 px-3">{getOutcomeBadge(job.eligibility_outcome)}</td>
                      <td className="py-3 px-3 text-center font-mono">
                        {Math.round(job.mandatory_coverage_ratio * 100)}%
                      </td>
                      <td className="py-3 px-3 text-center font-mono text-slate-400">
                        {Math.round(job.preferred_coverage_ratio * 100)}%
                      </td>
                      <td className="py-3 px-3 text-center">
                        {job.critical_gaps_count > 0 ? (
                          <span className="text-rose-400 font-bold">{job.critical_gaps_count} blocking</span>
                        ) : (
                          <span className="text-emerald-400 font-medium">None</span>
                        )}
                      </td>
                      <td className="py-3 px-3 text-right font-mono font-bold text-cyan-400">
                        {job.relevance_index.toFixed(1)}/100
                      </td>
                      <td className="py-3 px-4 text-right space-x-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => toggleCompareJob(job.canonical_job_id)}
                          className={`text-xs ${comparisonJobIds.includes(job.canonical_job_id) ? 'text-cyan-400' : 'text-slate-400'}`}
                        >
                          {comparisonJobIds.includes(job.canonical_job_id) ? 'Selected' : 'Compare'}
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setSelectedEvaluationId(job.evaluation_id);
                            setActiveTab('details');
                          }}
                          className="border-[#1e293b] text-xs hover:text-white"
                        >
                          Inspect
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* =========================================================================
            TAB 3: MATCH DETAILS & ELIGIBILITY INSPECTOR
           ========================================================================= */}
        {activeTab === 'details' && selectedEvaluation && (
          <div className="space-y-6">
            {/* Header info */}
            <div className="p-5 rounded-lg bg-[#0f172a] border border-[#1e293b] flex items-center justify-between">
              <div>
                <div className="flex items-center gap-3">
                  <h2 className="text-lg font-bold text-white">{selectedEvaluation.job_title}</h2>
                  {getOutcomeBadge(selectedEvaluation.eligibility_outcome)}
                </div>
                <div className="mt-1 text-sm text-slate-400 flex items-center gap-3">
                  <span>{selectedEvaluation.company_name}</span>
                  <span>•</span>
                  <span>{selectedEvaluation.job_location || 'Remote'}</span>
                  <span>•</span>
                  <span>{selectedEvaluation.work_arrangement || 'Standard'}</span>
                  <span>•</span>
                  <span className="font-mono text-cyan-400">ID: {selectedEvaluation.canonical_job_id.slice(0, 12)}</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-mono font-bold text-cyan-400">{selectedEvaluation.relevance_index.toFixed(1)}/100</div>
                <div className="text-xs text-slate-400">Deterministic Relevance Index</div>
              </div>
            </div>

            {/* Eligibility Conditions Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 rounded-lg bg-[#0f172a] border border-[#1e293b]">
                <div className="text-xs text-slate-400 font-medium">Work Authorization</div>
                <div className="mt-1 text-sm font-semibold text-white">
                  {selectedEvaluation.eligibility_detail.work_authorization_status}
                </div>
                <div className="mt-1 text-[11px] text-slate-500">Legal permission check</div>
              </div>
              <div className="p-4 rounded-lg bg-[#0f172a] border border-[#1e293b]">
                <div className="text-xs text-slate-400 font-medium">Visa Sponsorship</div>
                <div className="mt-1 text-sm font-semibold text-white">
                  {selectedEvaluation.eligibility_detail.sponsorship_status}
                </div>
                <div className="mt-1 text-[11px] text-slate-500">Employer offer vs need</div>
              </div>
              <div className="p-4 rounded-lg bg-[#0f172a] border border-[#1e293b]">
                <div className="text-xs text-slate-400 font-medium">Remote Jurisdiction</div>
                <div className="mt-1 text-sm font-semibold text-white">
                  {selectedEvaluation.eligibility_detail.remote_compatibility}
                </div>
                <div className="mt-1 text-[11px] text-slate-500">Allowed country regions</div>
              </div>
              <div className="p-4 rounded-lg bg-[#0f172a] border border-[#1e293b]">
                <div className="text-xs text-slate-400 font-medium">Employer Restrictions</div>
                <div className="mt-1 text-sm font-semibold text-white">
                  {selectedEvaluation.eligibility_detail.employer_restriction_status}
                </div>
                <div className="mt-1 text-[11px] text-slate-500">Career policy blocklist</div>
              </div>
            </div>

            {/* Summary Explanation */}
            <div className="p-5 rounded-lg bg-[#0f172a] border border-[#1e293b] space-y-2">
              <h3 className="text-sm font-semibold text-white">Evaluation Synthesis</h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                {selectedEvaluation.summary_explanation}
              </p>
              {!selectedEvaluation.hard_policy_passed && (
                <div className="mt-3 p-3 rounded bg-red-500/10 border border-red-500/30 text-xs text-red-300">
                  <div className="font-semibold">Hard Policy Violation:</div>
                  <div>{selectedEvaluation.hard_policy_reason}</div>
                </div>
              )}
            </div>

            {/* Quick Actions */}
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setActiveTab('matrix')}
                className="border-[#1e293b] text-xs"
              >
                Inspect Qualification Matrix →
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setActiveTab('gaps')}
                className="border-[#1e293b] text-xs text-amber-400"
              >
                Inspect Qualification Gaps ({selectedEvaluation.gaps.length}) →
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setActiveTab('simulation')}
                className="border-[#1e293b] text-xs text-cyan-400"
              >
                Simulate What-If Adjustments →
              </Button>
            </div>
          </div>
        )}

        {/* =========================================================================
            TAB 4: QUALIFICATION MATRIX
           ========================================================================= */}
        {activeTab === 'matrix' && selectedEvaluation && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">
                Requirement-by-Requirement Evidence Matrix — {selectedEvaluation.job_title}
              </h3>
              <div className="text-xs text-slate-400 font-mono">
                Mandatory: {Math.round(selectedEvaluation.mandatory_coverage_ratio * 100)}% | Preferred: {Math.round(selectedEvaluation.preferred_coverage_ratio * 100)}%
              </div>
            </div>

            <div className="overflow-x-auto rounded-lg border border-[#1e293b] bg-[#0f172a]">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#0a0f1d] border-b border-[#1e293b] text-slate-400 uppercase tracking-wider text-[10px]">
                  <tr>
                    <th className="py-3 px-4">Requirement</th>
                    <th className="py-3 px-3">Category</th>
                    <th className="py-3 px-3">Match State</th>
                    <th className="py-3 px-4">Applicant Evidence Snippet</th>
                    <th className="py-3 px-4">Explanation</th>
                    <th className="py-3 px-3 text-center">Satisfied</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e293b] text-slate-300">
                  {selectedEvaluation.requirement_results.map((r, i) => (
                    <tr key={i} className="hover:bg-[#131f37] transition-colors">
                      <td className="py-3 px-4 font-medium text-white">{r.name}</td>
                      <td className="py-3 px-3">
                        <span className={`capitalize ${r.category === 'mandatory' ? 'text-rose-400 font-bold' : 'text-slate-400'}`}>
                          {r.category}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <Badge variant="outline" className="text-[10px] border-[#1e293b]">
                          {r.match_category.replace(/_/g, ' ')}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                        {r.applicant_evidence_snippet || <span className="text-slate-600">None</span>}
                      </td>
                      <td className="py-3 px-4 text-slate-300 max-w-md">{r.explanation}</td>
                      <td className="py-3 px-3 text-center">
                        {r.is_satisfied ? (
                          <CheckCircle2 className="h-4 w-4 text-emerald-400 inline" />
                        ) : (
                          <XCircle className="h-4 w-4 text-rose-400 inline" />
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Logical Groups Breakdown */}
            {selectedEvaluation.group_results.length > 0 && (
              <div className="p-5 rounded-lg bg-[#0f172a] border border-[#1e293b] space-y-3">
                <h4 className="text-xs font-semibold text-white uppercase tracking-wider">
                  Logical Boolean Groups (AND / OR / AtLeastN)
                </h4>
                <div className="space-y-2">
                  {selectedEvaluation.group_results.map((g, idx) => (
                    <div key={idx} className="p-3 rounded bg-[#0a0f1d] border border-[#1e293b] flex items-center justify-between">
                      <div className="text-xs">
                        <span className="font-mono font-bold text-cyan-400 mr-2">[{g.operator}]</span>
                        <span className="text-slate-300">{g.explanation}</span>
                      </div>
                      <Badge className={g.is_satisfied ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}>
                        {g.is_satisfied ? 'Group Satisfied' : 'Group Unmet'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* =========================================================================
            TAB 5: SKILL GAP EXPLORER
           ========================================================================= */}
        {activeTab === 'gaps' && selectedEvaluation && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">
                Qualification Gaps & Grounded Remediation Suggestions
              </h3>
              <div className="text-xs text-slate-400">
                {selectedEvaluation.gaps.length} gaps identified
              </div>
            </div>

            {selectedEvaluation.gaps.length === 0 ? (
              <div className="p-8 text-center bg-[#0f172a] rounded-lg border border-[#1e293b] text-slate-400 text-sm">
                No qualification gaps detected! Applicant satisfies all known requirements.
              </div>
            ) : (
              <div className="space-y-3">
                {selectedEvaluation.gaps.map((gap) => (
                  <div key={gap.id} className="p-4 rounded-lg bg-[#0f172a] border border-[#1e293b] space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-bold text-white">{gap.skill_or_qualification}</span>
                        <Badge
                          className={`text-[10px] ${
                            gap.severity === 'blocking'
                              ? 'bg-red-500/20 text-red-400 border-red-500/30'
                              : gap.severity === 'critical_review'
                              ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                              : 'bg-blue-500/20 text-blue-400 border-blue-500/30'
                          }`}
                        >
                          {gap.severity.toUpperCase()}
                        </Badge>
                        <span className="text-xs text-slate-400 font-mono">({gap.gap_type.replace(/_/g, ' ')})</span>
                      </div>
                    </div>
                    <div className="text-xs text-slate-300">{gap.description}</div>
                    <div className="mt-2 p-2.5 rounded bg-[#0a0f1d] border border-cyan-500/20 text-xs text-cyan-300">
                      <span className="font-semibold text-cyan-400">Actionable Remediation: </span>
                      {gap.remediation_suggestion}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* =========================================================================
            TAB 6: RELEVANCE EXPLANATIONS & SCORE COMPONENTS
           ========================================================================= */}
        {activeTab === 'relevance' && selectedEvaluation && (
          <div className="space-y-6">
            <div className="p-5 rounded-lg bg-[#0f172a] border border-[#1e293b] flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-white">Explainable Relevance Index Breakdown</h3>
                <p className="text-xs text-slate-400">
                  Transparent weighted scoring formula across 8 observed dimensions (0–100 scale).
                </p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-mono font-bold text-cyan-400">{selectedEvaluation.relevance_index.toFixed(1)}/100</div>
                <div className="text-[10px] text-slate-500">Internal rubric alignment</div>
              </div>
            </div>

            <div className="overflow-x-auto rounded-lg border border-[#1e293b] bg-[#0f172a]">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#0a0f1d] border-b border-[#1e293b] text-slate-400 uppercase tracking-wider text-[10px]">
                  <tr>
                    <th className="py-3 px-4">Evaluation Dimension</th>
                    <th className="py-3 px-3 text-center">Weight</th>
                    <th className="py-3 px-3 text-center">Raw Score</th>
                    <th className="py-3 px-3 text-center">Weighted Score</th>
                    <th className="py-3 px-4">Deterministic Explanation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e293b] text-slate-300">
                  {selectedEvaluation.score_breakdown.dimensions.map((dim) => (
                    <tr key={dim.dimension_id} className="hover:bg-[#131f37] transition-colors">
                      <td className="py-3 px-4 font-medium text-white">{dim.name}</td>
                      <td className="py-3 px-3 text-center font-mono">{(dim.weight * 100).toFixed(0)}%</td>
                      <td className="py-3 px-3 text-center font-mono text-cyan-400">{(dim.raw_score * 100).toFixed(0)}%</td>
                      <td className="py-3 px-3 text-center font-mono font-bold text-white">
                        {(dim.weighted_score * 100).toFixed(1)}
                      </td>
                      <td className="py-3 px-4 text-slate-300">{dim.explanation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Counterfactuals */}
            {selectedEvaluation.counterfactuals.length > 0 && (
              <div className="p-5 rounded-lg bg-[#0f172a] border border-[#1e293b] space-y-3">
                <h4 className="text-xs font-semibold text-white uppercase tracking-wider flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-cyan-400" />
                  Counterfactual Scenarios (&quot;What would change this outcome?&quot;)
                </h4>
                <div className="space-y-2">
                  {selectedEvaluation.counterfactuals.map((cf, i) => (
                    <div key={i} className="p-3 rounded bg-[#0a0f1d] border border-[#1e293b] flex items-center justify-between">
                      <div className="text-xs space-y-1">
                        <div className="font-semibold text-cyan-300">{cf.scenario_name}</div>
                        <div className="text-slate-400">{cf.impact_summary}</div>
                      </div>
                      <div className="text-right text-xs">
                        <span className="text-slate-400 line-through mr-2">{cf.current_state}</span>
                        <span className="text-emerald-400 font-bold">→ {cf.simulated_state}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* =========================================================================
            TAB 7: JOB COMPARISON MATRIX
           ========================================================================= */}
        {activeTab === 'comparison' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-white">Candidate Opportunities Side-by-Side Comparison</h3>
                <p className="text-xs text-slate-400">Select up to 4 opportunities from the rankings table to compare.</p>
              </div>
              {comparisonJobIds.length > 0 && (
                <Button size="sm" variant="outline" onClick={() => setComparisonJobIds([])} className="text-xs">
                  Clear Selected
                </Button>
              )}
            </div>

            {comparisonJobIds.length === 0 ? (
              <div className="p-12 text-center bg-[#0f172a] rounded-lg border border-[#1e293b] text-slate-400 text-sm">
                No opportunities selected for comparison. Go to &quot;Ranked Opportunities&quot; and click &quot;Compare&quot;.
              </div>
            ) : (
              <div className="overflow-x-auto rounded-lg border border-[#1e293b] bg-[#0f172a]">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#0a0f1d] border-b border-[#1e293b] text-slate-400">
                    <tr>
                      <th className="py-3 px-4 w-48">Attribute</th>
                      {comparisonJobIds.map((jid) => {
                        const ev = evaluationsData?.find((e) => e.canonical_job_id === jid);
                        return (
                          <th key={jid} className="py-3 px-4 min-w-[200px]">
                            <div className="font-bold text-white text-sm">{ev?.job_title || jid.slice(0, 8)}</div>
                            <div className="text-[11px] text-slate-400">{ev?.company_name}</div>
                          </th>
                        );
                      })}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1e293b] text-slate-300">
                    <tr>
                      <td className="py-3 px-4 font-medium text-slate-400">Eligibility Outcome</td>
                      {comparisonJobIds.map((jid) => {
                        const ev = evaluationsData?.find((e) => e.canonical_job_id === jid);
                        return <td key={jid} className="py-3 px-4">{ev ? getOutcomeBadge(ev.eligibility_outcome) : '-'}</td>;
                      })}
                    </tr>
                    <tr>
                      <td className="py-3 px-4 font-medium text-slate-400">Relevance Index</td>
                      {comparisonJobIds.map((jid) => {
                        const ev = evaluationsData?.find((e) => e.canonical_job_id === jid);
                        return <td key={jid} className="py-3 px-4 font-mono font-bold text-cyan-400">{ev?.relevance_index.toFixed(1)}/100</td>;
                      })}
                    </tr>
                    <tr>
                      <td className="py-3 px-4 font-medium text-slate-400">Mandatory Coverage</td>
                      {comparisonJobIds.map((jid) => {
                        const ev = evaluationsData?.find((e) => e.canonical_job_id === jid);
                        return <td key={jid} className="py-3 px-4 font-mono">{ev ? `${Math.round(ev.mandatory_coverage_ratio * 100)}%` : '-'}</td>;
                      })}
                    </tr>
                    <tr>
                      <td className="py-3 px-4 font-medium text-slate-400">Preferred Coverage</td>
                      {comparisonJobIds.map((jid) => {
                        const ev = evaluationsData?.find((e) => e.canonical_job_id === jid);
                        return <td key={jid} className="py-3 px-4 font-mono">{ev ? `${Math.round(ev.preferred_coverage_ratio * 100)}%` : '-'}</td>;
                      })}
                    </tr>
                    <tr>
                      <td className="py-3 px-4 font-medium text-slate-400">Work Arrangement</td>
                      {comparisonJobIds.map((jid) => {
                        const ev = evaluationsData?.find((e) => e.canonical_job_id === jid);
                        return <td key={jid} className="py-3 px-4">{ev?.work_arrangement || 'Onsite'}</td>;
                      })}
                    </tr>
                    <tr>
                      <td className="py-3 px-4 font-medium text-slate-400">Compensation Match</td>
                      {comparisonJobIds.map((jid) => {
                        const ev = evaluationsData?.find((e) => e.canonical_job_id === jid);
                        return <td key={jid} className="py-3 px-4 font-mono">{ev?.eligibility_detail.compensation_compatibility || 'Undisclosed'}</td>;
                      })}
                    </tr>
                    <tr>
                      <td className="py-3 px-4 font-medium text-slate-400">Critical Gaps Count</td>
                      {comparisonJobIds.map((jid) => {
                        const ev = evaluationsData?.find((e) => e.canonical_job_id === jid);
                        const cnt = ev ? ev.gaps.filter((g) => g.severity === 'blocking').length : 0;
                        return <td key={jid} className="py-3 px-4 font-mono text-rose-400 font-bold">{cnt}</td>;
                      })}
                    </tr>
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* =========================================================================
            TAB 8: WHAT-IF SIMULATOR
           ========================================================================= */}
        {activeTab === 'simulation' && (
          <div className="space-y-6">
            <div className="p-5 rounded-lg bg-[#0f172a] border border-[#1e293b]">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-cyan-400" />
                Hypothetical Scenario Simulator (Section 91, Required Test 154)
              </h3>
              <p className="mt-1 text-xs text-slate-400">
                Simulate how hypothetical skills, compensation preferences, or work authorization adjustments would impact
                eligibility and ranking, without mutating your actual profile or active policies.
              </p>
            </div>

            {selectedEvaluation ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Inputs */}
                <div className="p-5 rounded-lg bg-[#0f172a] border border-[#1e293b] space-y-4">
                  <div className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">
                    Target Job: {selectedEvaluation.job_title} ({selectedEvaluation.company_name})
                  </div>

                  <div className="space-y-3">
                    <div>
                      <label className="text-xs text-slate-300 font-medium">Scenario Name</label>
                      <Input
                        value={simScenarioName}
                        onChange={(e) => setSimScenarioName(e.target.value)}
                        className="mt-1 bg-[#0a0f1d] border-[#1e293b] text-white text-xs"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-slate-300 font-medium">Hypothetical Skills (comma-separated)</label>
                      <Input
                        value={simHypoSkills}
                        onChange={(e) => setSimHypoSkills(e.target.value)}
                        placeholder="e.g. Kubernetes, Go, Terraform"
                        className="mt-1 bg-[#0a0f1d] border-[#1e293b] text-white text-xs"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-slate-300 font-medium">Hypothetical Minimum Annual Salary ($)</label>
                      <Input
                        value={simHypoMinSalary}
                        onChange={(e) => setSimHypoMinSalary(e.target.value)}
                        placeholder="e.g. 120000"
                        className="mt-1 bg-[#0a0f1d] border-[#1e293b] text-white text-xs"
                      />
                    </div>
                    <div className="flex items-center gap-2 pt-2">
                      <input
                        type="checkbox"
                        id="confirmAuthCheck"
                        checked={simHypoConfirmAuth}
                        onChange={(e) => setSimHypoConfirmAuth(e.target.checked)}
                        className="rounded border-[#1e293b]"
                      />
                      <label htmlFor="confirmAuthCheck" className="text-xs text-slate-300">
                        Simulate explicitly confirmed US/Global work authorization
                      </label>
                    </div>
                  </div>

                  <Button
                    onClick={handleRunSimulation}
                    disabled={simulationMutation.isPending}
                    className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs mt-4"
                  >
                    <Play className="mr-1.5 h-3.5 w-3.5" />
                    Run Hypothetical Simulation
                  </Button>
                </div>

                {/* Outputs */}
                <div className="p-5 rounded-lg bg-[#0f172a] border border-[#1e293b] space-y-4">
                  <div className="text-xs font-semibold text-white uppercase tracking-wider">
                    Simulation Comparison Results
                  </div>

                  {!simulationResult ? (
                    <div className="py-16 text-center text-xs text-slate-500">
                      Configure adjustments on the left and click &quot;Run Hypothetical Simulation&quot;.
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="p-4 rounded bg-[#0a0f1d] border border-cyan-500/30">
                        <div className="text-xs text-slate-400">Simulation Summary:</div>
                        <div className="mt-1 text-xs text-cyan-300 font-medium">{simulationResult.diff_explanation}</div>
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div className="p-3 rounded bg-[#0a0f1d] border border-[#1e293b]">
                          <div className="text-[10px] text-slate-400">Original Relevance</div>
                          <div className="text-xl font-mono font-bold text-slate-300">{simulationResult.original_relevance_index.toFixed(1)}/100</div>
                          <div className="text-[10px] text-slate-500">{simulationResult.original_eligibility}</div>
                        </div>
                        <div className="p-3 rounded bg-[#0a0f1d] border border-emerald-500/30">
                          <div className="text-[10px] text-emerald-400">Simulated Relevance</div>
                          <div className="text-xl font-mono font-bold text-emerald-300">{simulationResult.simulated_relevance_index.toFixed(1)}/100</div>
                          <div className="text-[10px] text-emerald-500">{simulationResult.simulated_eligibility}</div>
                        </div>
                      </div>

                      {simulationResult.dimension_diffs.length > 0 && (
                        <div className="space-y-2">
                          <div className="text-xs text-slate-400 font-medium">Dimension Score Shifts:</div>
                          {simulationResult.dimension_diffs.map((diff, i) => (
                            <div key={i} className="p-2 rounded bg-[#0a0f1d] text-xs flex justify-between">
                              <span className="text-slate-300">{diff.name}</span>
                              <span className="font-mono text-emerald-400">
                                +{(diff.diff * 100).toFixed(1)}%
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-slate-500 bg-[#0f172a] rounded-lg border border-[#1e293b]">
                Select an opportunity first to run What-If simulations.
              </div>
            )}
          </div>
        )}

        {/* =========================================================================
            TAB 9: REVIEW QUEUE
           ========================================================================= */}
        {activeTab === 'review_queue' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-white">Matching Human Review Queue (Section 123)</h3>
                <p className="text-xs text-slate-400">
                  Items flagged for uncertainty, unverified mandatory qualifications, or ambiguous alternatives.
                </p>
              </div>
              <div className="text-xs text-slate-400">{reviewQueueData?.length || 0} pending items</div>
            </div>

            {!reviewQueueData || reviewQueueData.length === 0 ? (
              <div className="p-12 text-center bg-[#0f172a] rounded-lg border border-[#1e293b] text-slate-400 text-sm">
                No items pending review. All evaluations have resolved eligibility.
              </div>
            ) : (
              <div className="space-y-3">
                {reviewQueueData.map((item: any) => (
                  <div key={item.id} className="p-4 rounded-lg bg-[#0f172a] border border-[#1e293b] flex items-center justify-between">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <Badge className="bg-amber-500/20 text-amber-400 text-[10px] border border-amber-500/30">
                          {item.review_type.replace(/_/g, ' ').toUpperCase()}
                        </Badge>
                        <span className="text-xs font-mono text-slate-400">ID: {item.id}</span>
                      </div>
                      <div className="text-xs text-slate-300 max-w-2xl">{item.trigger_reason}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          resolveReviewMutation.mutate({
                            id: item.id,
                            notes: 'Manually verified by user',
                            decision: 'resolved',
                          })
                        }
                        className="text-xs border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10"
                      >
                        Resolve
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          resolveReviewMutation.mutate({
                            id: item.id,
                            notes: 'Deferred for later investigation',
                            decision: 'deferred',
                          })
                        }
                        className="text-xs border-[#1e293b] text-slate-400"
                      >
                        Defer
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* =========================================================================
            TAB 10: RUBRIC & SETTINGS
           ========================================================================= */}
        {activeTab === 'settings' && (
          <div className="space-y-6">
            <div className="p-5 rounded-lg bg-[#0f172a] border border-[#1e293b]">
              <h3 className="text-sm font-semibold text-white">Active Ranking Rubric Configuration</h3>
              <p className="text-xs text-slate-400">
                Transparent weights determining relevance scores. Soft weights cannot override mandatory eligibility or hard policy exclusions.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {rubricsData && rubricsData.length > 0 ? (
                rubricsData.map((rubric) => (
                  <div key={rubric.id} className="p-4 rounded-lg bg-[#0f172a] border border-[#1e293b] space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="font-semibold text-white text-sm">{rubric.name}</div>
                      {rubric.is_default && <Badge className="bg-cyan-500/20 text-cyan-400 text-[10px]">Active Default</Badge>}
                    </div>
                    <div className="text-xs text-slate-400">{rubric.description}</div>
                    <div className="pt-2 border-t border-[#1e293b] space-y-1.5">
                      {Object.entries(rubric.weights).map(([k, w]) => (
                        <div key={k} className="flex justify-between text-xs">
                          <span className="text-slate-300 capitalize">{k.replace(/_/g, ' ')}</span>
                          <span className="font-mono text-cyan-400">{(w * 100).toFixed(0)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-6 text-xs text-slate-400 bg-[#0f172a] rounded-lg border border-[#1e293b]">
                  Loading active rubric configurations...
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </ModulePage>
  );
};
