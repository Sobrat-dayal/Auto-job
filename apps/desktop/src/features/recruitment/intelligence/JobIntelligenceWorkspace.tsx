/**
 * Stage 28: Job Requirement Intelligence Engine.
 * Master Desktop Workspace Container.
 */

import * as React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  BrainCircuit,
  ListFilter,
  CheckCircle2,
  AlertTriangle,
  GitBranch,
  Code,
  GraduationCap,
  Clock,
  Building2,
  DollarSign,
  ShieldCheck,
  Calendar,
  FileSearch,
  Activity,
  Search,
  RefreshCw,
} from 'lucide-react';
import { ModulePage, ModuleHeader, ModuleTabs } from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';
import type {
  JobIntelligenceReviewItem,
  ReviewStatus,
} from '@autonom/shared-types';

export const JobIntelligenceWorkspace: React.FC = () => {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = React.useState<string>('overview');
  const [selectedJobId, setSelectedJobId] = React.useState<string | null>(null);
  const [searchQuery, setSearchQuery] = React.useState<string>('');
  const [reqCategoryFilter, setReqCategoryFilter] = React.useState<string>('ALL');

  // Queries
  const { data: statusData } = useQuery({
    queryKey: ['job-intelligence', 'status'],
    queryFn: () => apiClient.getIntelligenceStatus(),
  });

  const { data: jobsList = [], refetch: refetchJobs } = useQuery({
    queryKey: ['job-intelligence', 'jobs'],
    queryFn: () => apiClient.listAnalyzedJobs(),
  });

  const { data: reviewQueue = [], refetch: refetchReviews } = useQuery<JobIntelligenceReviewItem[]>({
    queryKey: ['job-intelligence', 'review-queue'],
    queryFn: () => apiClient.getReviewQueue(),
  });

  // Selected job query
  const effectiveJobId = selectedJobId || (jobsList.length > 0 ? jobsList[0].canonical_job_id : null);
  const { data: currentJob } = useQuery({
    queryKey: ['job-intelligence', 'job', effectiveJobId],
    queryFn: () => (effectiveJobId ? apiClient.getJobIntelligence(effectiveJobId) : null),
    enabled: !!effectiveJobId,
  });

  // Trigger analysis mutation
  const analyzeMutation = useMutation({
    mutationFn: (jobId: string) => apiClient.analyzeJob(jobId, true, false),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job-intelligence'] });
    },
  });

  // Resolve review mutation
  const resolveMutation = useMutation({
    mutationFn: ({ id, decision }: { id: string; decision: ReviewStatus }) =>
      apiClient.resolveReviewItem(id, decision),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job-intelligence'] });
    },
  });

  const filteredJobs = jobsList.filter((j) =>
    j.job_title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    j.canonical_job_id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BrainCircuit },
    { id: 'jobs', label: 'Analyzed Jobs', icon: ListFilter },
    { id: 'requirements', label: 'Requirements Explorer', icon: CheckCircle2 },
    { id: 'logic_tree', label: 'Logic Explorer', icon: GitBranch },
    { id: 'skills', label: 'Technology Stack', icon: Code },
    { id: 'education_exp', label: 'Education & Exp', icon: GraduationCap },
    { id: 'employment', label: 'Employment Conditions', icon: Building2 },
    { id: 'compensation', label: 'Compensation', icon: DollarSign },
    { id: 'eligibility', label: 'Work Authorization', icon: ShieldCheck },
    { id: 'deadlines', label: 'Deadlines & Instructions', icon: Calendar },
    { id: 'evidence', label: 'Evidence Inspector', icon: FileSearch },
    { id: 'conflicts', label: 'Conflict Review', icon: AlertTriangle },
    { id: 'review_queue', label: 'Review Queue', icon: Clock },
    { id: 'diagnostics', label: 'Diagnostics', icon: Activity },
  ];

  return (
    <ModulePage>
      <ModuleHeader
        title="Job Requirement Intelligence"
        description="Structured requirement extraction, logical semantics, NLP understanding, evidence provenance, and multi-source conflict reconciliation."
      >
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="border-cyan-500/40 text-cyan-400 bg-cyan-950/20">
            Engine v1.0.0
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              refetchJobs();
              refetchReviews();
            }}
            className="border-slate-700 hover:bg-slate-800"
          >
            <RefreshCw className="w-4 h-4 mr-1 text-slate-400" />
            Refresh
          </Button>
        </div>
      </ModuleHeader>

      <div className="border-b border-slate-800 bg-slate-950/60 px-6">
        <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      <div className="p-6 space-y-6">
        {/* TAB 1: OVERVIEW */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="p-4 rounded-lg bg-slate-900/80 border border-slate-800">
                <span className="text-xs font-medium text-slate-400">Total Analyzed Postings</span>
                <div className="text-2xl font-bold text-slate-100 mt-1">
                  {jobsList.length}
                </div>
                <span className="text-xs text-cyan-400 mt-1 block">Full provenance tracking active</span>
              </div>
              <div className="p-4 rounded-lg bg-slate-900/80 border border-slate-800">
                <span className="text-xs font-medium text-slate-400">Pending Review Items</span>
                <div className="text-2xl font-bold text-amber-400 mt-1">
                  {reviewQueue.length}
                </div>
                <span className="text-xs text-slate-500 mt-1 block">Ambiguous or conflicting spans</span>
              </div>
              <div className="p-4 rounded-lg bg-slate-900/80 border border-slate-800">
                <span className="text-xs font-medium text-slate-400">Deterministic Rule Engine</span>
                <div className="text-2xl font-bold text-emerald-400 mt-1">Active</div>
                <span className="text-xs text-slate-500 mt-1 block">100% offline fallback ready</span>
              </div>
              <div className="p-4 rounded-lg bg-slate-900/80 border border-slate-800">
                <span className="text-xs font-medium text-slate-400">Stage 11 AI Fallback</span>
                <div className="text-2xl font-bold text-blue-400 mt-1">Enabled</div>
                <span className="text-xs text-slate-500 mt-1 block">Zero hallucination quote verification</span>
              </div>
            </div>

            <div className="p-5 rounded-lg bg-slate-900/60 border border-slate-800 space-y-4">
              <h3 className="text-sm font-semibold text-slate-200">Recent Analyzed Postings</h3>
              {jobsList.length === 0 ? (
                <div className="text-sm text-slate-500 py-6 text-center">
                  No job postings analyzed yet. Discover jobs via Multi-Source Discovery to begin intelligence extraction.
                </div>
              ) : (
                <div className="divide-y divide-slate-800/60">
                  {jobsList.slice(0, 5).map((job) => (
                    <div
                      key={job.id}
                      onClick={() => {
                        setSelectedJobId(job.canonical_job_id);
                        setActiveTab('requirements');
                      }}
                      className="py-3 flex items-center justify-between hover:bg-slate-800/30 px-2 rounded cursor-pointer transition-colors"
                    >
                      <div>
                        <div className="text-sm font-medium text-slate-200">{job.job_title}</div>
                        <div className="text-xs text-slate-500">
                          ID: {job.canonical_job_id} • Status: {job.analysis_status} • Conf: {(job.overall_confidence * 100).toFixed(0)}%
                        </div>
                      </div>
                      <Badge variant="outline" className="border-slate-700 text-slate-400">
                        {job.mandatory_requirements.length} Mandatory Reqs
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 2: ANALYZED JOBS LIST */}
        {activeTab === 'jobs' && (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="relative flex-1">
                <Search className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
                <Input
                  placeholder="Search by job title or ID..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 bg-slate-900 border-slate-800 text-slate-200"
                />
              </div>
            </div>

            <div className="border border-slate-800 rounded-lg overflow-hidden bg-slate-900/60">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-950 text-xs text-slate-400 uppercase border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3">Job Title</th>
                    <th className="px-4 py-3">Canonical ID</th>
                    <th className="px-4 py-3">Analysis Status</th>
                    <th className="px-4 py-3">Mandatory Reqs</th>
                    <th className="px-4 py-3">Confidence</th>
                    <th className="px-4 py-3">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredJobs.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                        No analyzed jobs matching search criteria.
                      </td>
                    </tr>
                  ) : (
                    filteredJobs.map((j) => (
                      <tr key={j.id} className="hover:bg-slate-800/40">
                        <td className="px-4 py-3 font-medium text-slate-200">{j.job_title}</td>
                        <td className="px-4 py-3 font-mono text-xs text-slate-400">{j.canonical_job_id}</td>
                        <td className="px-4 py-3">
                          <Badge variant="outline" className="border-cyan-500/30 text-cyan-400">
                            {j.analysis_status}
                          </Badge>
                        </td>
                        <td className="px-4 py-3">{j.mandatory_requirements.length}</td>
                        <td className="px-4 py-3 font-mono text-xs">{(j.overall_confidence * 100).toFixed(0)}%</td>
                        <td className="px-4 py-3 flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSelectedJobId(j.canonical_job_id);
                              setActiveTab('requirements');
                            }}
                            className="border-slate-700 hover:bg-slate-800 text-xs"
                          >
                            Inspect
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            disabled={analyzeMutation.isPending}
                            onClick={() => analyzeMutation.mutate(j.canonical_job_id)}
                            className="border-slate-700 hover:bg-slate-800 text-xs"
                          >
                            Reanalyze
                          </Button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 3: REQUIREMENTS EXPLORER */}
        {activeTab === 'requirements' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-slate-200">
                  {currentJob ? currentJob.job_title : 'Select a Job to Inspect'}
                </h3>
                <span className="text-xs text-slate-500">
                  {currentJob ? `Canonical ID: ${currentJob.canonical_job_id}` : 'Select an analyzed job from the Jobs tab.'}
                </span>
              </div>
              <div className="flex gap-2">
                {['ALL', 'Mandatory', 'Preferred', 'Conditional'].map((cat) => (
                  <Button
                    key={cat}
                    variant={reqCategoryFilter === cat ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => setReqCategoryFilter(cat)}
                    className="text-xs"
                  >
                    {cat}
                  </Button>
                ))}
              </div>
            </div>

            {currentJob && (
              <div className="border border-slate-800 rounded-lg overflow-hidden bg-slate-900/60">
                <table className="w-full text-left text-sm text-slate-300">
                  <thead className="bg-slate-950 text-xs text-slate-400 uppercase border-b border-slate-800">
                    <tr>
                      <th className="px-4 py-3">Requirement</th>
                      <th className="px-4 py-3">Category</th>
                      <th className="px-4 py-3">Type</th>
                      <th className="px-4 py-3">Normalized Value</th>
                      <th className="px-4 py-3">Min Years</th>
                      <th className="px-4 py-3">Confidence</th>
                      <th className="px-4 py-3">Provenance Evidence</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {(currentJob.mandatory_requirements.concat(currentJob.preferred_requirements, currentJob.conditional_requirements))
                      .filter((r) => reqCategoryFilter === 'ALL' || r.category === reqCategoryFilter)
                      .map((req) => (
                        <tr key={req.id} className="hover:bg-slate-800/30">
                          <td className="px-4 py-3 font-medium text-slate-200">{req.name}</td>
                          <td className="px-4 py-3">
                            <Badge
                              variant="outline"
                              className={
                                req.category === 'Mandatory'
                                  ? 'border-emerald-500/40 text-emerald-400 bg-emerald-950/20'
                                  : 'border-blue-500/40 text-blue-400 bg-blue-950/20'
                              }
                            >
                              {req.category}
                            </Badge>
                          </td>
                          <td className="px-4 py-3 text-xs text-slate-400">{req.qualification_type}</td>
                          <td className="px-4 py-3 font-mono text-xs text-cyan-400">{req.normalized_value}</td>
                          <td className="px-4 py-3 text-xs">{req.min_years ? `${req.min_years} yrs` : '—'}</td>
                          <td className="px-4 py-3 text-xs text-slate-400">
                            {req.confidence.replace('_', ' ')}
                          </td>
                          <td className="px-4 py-3 text-xs text-slate-400 max-w-xs truncate" title={req.raw_text}>
                            {req.raw_text}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* TAB 4: LOGIC TREE EXPLORER */}
        {activeTab === 'logic_tree' && (
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">
              Logical Requirement Relationships & Groupings
            </h3>
            {currentJob?.requirement_groups && currentJob.requirement_groups.length > 0 ? (
              <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-3 font-mono text-sm">
                {currentJob.requirement_groups.map((grp) => (
                  <div key={grp.id} className="p-3 bg-slate-950/80 rounded border border-slate-800 space-y-2">
                    <div className="flex items-center gap-2">
                      <span className="text-cyan-400 font-bold">[{grp.operator}]</span>
                      <span className="text-slate-300">{grp.description || 'Requirement Node'}</span>
                      {grp.min_count && (
                        <Badge variant="outline" className="border-amber-500/40 text-amber-400">
                          Min Count: {grp.min_count}
                        </Badge>
                      )}
                    </div>
                    <div className="pl-6 space-y-1 text-xs text-slate-400">
                      {grp.requirement_ids?.map((rid) => {
                        const matched = currentJob.mandatory_requirements.find((r) => r.id === rid);
                        return (
                          <div key={rid} className="flex items-center gap-2">
                            <span className="text-slate-600">├──</span>
                            <span className="text-slate-200">{matched ? matched.name : rid}</span>
                            {matched && <span className="text-slate-500">({matched.qualification_type})</span>}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-slate-500 p-6 text-center border border-slate-800 rounded-lg">
                No complex logical groups detected. Requirements operate as direct conjunctions.
              </div>
            )}
          </div>
        )}

        {/* TAB 5: TECHNOLOGY STACK */}
        {activeTab === 'skills' && (
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Normalized Technical Skills</h3>
            {currentJob?.skills && currentJob.skills.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {currentJob.skills.map((skill, i) => (
                  <div key={i} className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-200">{skill.name}</span>
                      <Badge
                        variant="outline"
                        className={
                          skill.is_mandatory
                            ? 'border-emerald-500/40 text-emerald-400'
                            : 'border-blue-500/40 text-blue-400'
                        }
                      >
                        {skill.is_mandatory ? 'Mandatory' : 'Preferred'}
                      </Badge>
                    </div>
                    <div className="text-xs text-slate-400">Category: {skill.category}</div>
                    {skill.min_years && (
                      <div className="text-xs text-cyan-400">Minimum: {skill.min_years} years experience</div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-slate-500 p-6 text-center border border-slate-800 rounded-lg">
                No technical skills extracted for this job posting.
              </div>
            )}
          </div>
        )}

        {/* TAB 6: EDUCATION & EXPERIENCE */}
        {activeTab === 'education_exp' && (
          <div className="space-y-6">
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-slate-200">Education Requirements</h3>
              {currentJob?.education && currentJob.education.length > 0 ? (
                <div className="space-y-3">
                  {currentJob.education.map((edu, i) => (
                    <div key={i} className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-2">
                      <div className="flex items-center gap-3">
                        <span className="font-medium text-slate-200">{edu.degree_level.replace('_', ' ')} Degree</span>
                        <Badge variant="outline" className="border-slate-700 text-slate-400">
                          {edu.degree_status}
                        </Badge>
                      </div>
                      <div className="text-xs text-slate-400">
                        Fields of Study: {edu.fields_of_study.join(', ') || 'Any relevant technical discipline'}
                      </div>
                      {edu.alternative_experience_years && (
                        <div className="text-xs text-cyan-400">
                          Alternative Practical Experience: {edu.alternative_experience_years} years accepted
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-slate-500 p-4 border border-slate-800 rounded-lg">
                  No explicit formal degree required or disclosed.
                </div>
              )}
            </div>

            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-slate-200">Experience Requirements</h3>
              {currentJob?.experience && currentJob.experience.length > 0 ? (
                <div className="space-y-3">
                  {currentJob.experience.map((exp, i) => (
                    <div key={i} className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-1">
                      <div className="text-sm font-medium text-slate-200">
                        {exp.minimum_years ? `${exp.minimum_years}+ Years` : 'Experience Specified'}
                      </div>
                      <div className="text-xs text-slate-400">
                        Domain Focus: {exp.domain_categories.join(', ')}
                      </div>
                      <div className="text-xs text-slate-500 italic">"{exp.raw_text}"</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-slate-500 p-4 border border-slate-800 rounded-lg">
                  No minimum years of experience specified.
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 7: EMPLOYMENT CONDITIONS */}
        {activeTab === 'employment' && currentJob && (
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Employment and Workplace Conditions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-2">
                <span className="text-xs text-slate-500">Workplace Arrangement</span>
                <div className="text-base font-semibold text-slate-200">
                  {currentJob.employment_conditions.workplace_type.replace('_', ' ')}
                </div>
              </div>
              <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-2">
                <span className="text-xs text-slate-500">Employment Type</span>
                <div className="text-base font-semibold text-slate-200">
                  {currentJob.employment_conditions.employment_type.replace('_', ' ')}
                </div>
              </div>
              <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-2">
                <span className="text-xs text-slate-500">Hybrid Office Days</span>
                <div className="text-base font-semibold text-slate-200">
                  {currentJob.employment_conditions.office_days_per_week !== null
                    ? `${currentJob.employment_conditions.office_days_per_week} days/week`
                    : 'Not applicable'}
                </div>
              </div>
              <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-2">
                <span className="text-xs text-slate-500">Business Travel Requirement</span>
                <div className="text-base font-semibold text-slate-200">
                  {currentJob.employment_conditions.travel_percentage !== null
                    ? `${currentJob.employment_conditions.travel_percentage}% travel`
                    : 'No regular travel indicated'}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 8: COMPENSATION */}
        {activeTab === 'compensation' && currentJob && (
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Compensation Intelligence</h3>
            <div className="p-5 rounded-lg bg-slate-900/60 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs text-slate-500">Base Salary Range</span>
                  <div className="text-2xl font-bold text-slate-100">
                    {currentJob.compensation.is_disclosed
                      ? `${currentJob.compensation.currency} $${currentJob.compensation.base_min?.toLocaleString()} - $${currentJob.compensation.base_max?.toLocaleString()} / ${currentJob.compensation.pay_period.toLowerCase()}`
                      : 'Undisclosed by Employer'}
                  </div>
                </div>
                <Badge
                  variant="outline"
                  className={
                    currentJob.compensation.is_disclosed
                      ? 'border-emerald-500/40 text-emerald-400'
                      : 'border-slate-700 text-slate-500'
                  }
                >
                  {currentJob.compensation.is_disclosed ? 'Disclosed in Source' : 'Undisclosed'}
                </Badge>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-2 border-t border-slate-800">
                <div>
                  <span className="text-xs text-slate-500">Bonus Eligible</span>
                  <div className="text-sm text-slate-300 font-medium">
                    {currentJob.compensation.has_bonus ? 'Yes' : 'Not indicated'}
                  </div>
                </div>
                <div>
                  <span className="text-xs text-slate-500">Equity Grant</span>
                  <div className="text-sm text-slate-300 font-medium">
                    {currentJob.compensation.has_equity ? 'Yes' : 'Not indicated'}
                  </div>
                </div>
              </div>

              {currentJob.compensation.benefits.length > 0 && (
                <div className="pt-2 border-t border-slate-800">
                  <span className="text-xs text-slate-500 block mb-2">Identified Benefits & Perks</span>
                  <div className="flex flex-wrap gap-2">
                    {currentJob.compensation.benefits.map((b, i) => (
                      <Badge key={i} variant="outline" className="border-slate-700 text-slate-300">
                        {b}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 9: WORK AUTHORIZATION */}
        {activeTab === 'eligibility' && currentJob && (
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Work Authorization and Legal Eligibility</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-2">
                <span className="text-xs text-slate-500">Valid Work Authorization Required</span>
                <div className="text-base font-semibold text-slate-200">
                  {currentJob.eligibility.work_authorization_required ? 'Yes, Required' : 'Not Specified'}
                </div>
              </div>
              <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-2">
                <span className="text-xs text-slate-500">Visa Sponsorship</span>
                <div className="text-base font-semibold text-slate-200">
                  {currentJob.eligibility.visa_sponsorship_refused
                    ? 'Refused / Not Available'
                    : currentJob.eligibility.visa_sponsorship_offered
                    ? 'Available'
                    : 'Undisclosed'}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 10: DEADLINES & INSTRUCTIONS */}
        {activeTab === 'deadlines' && currentJob && (
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Application Deadlines and Instructions</h3>
            <div className="p-5 rounded-lg bg-slate-900/60 border border-slate-800 space-y-3">
              <div>
                <span className="text-xs text-slate-500">Application Deadline</span>
                <div className="text-base font-medium text-slate-200">
                  {currentJob.application_instructions.deadline_utc
                    ? new Date(currentJob.application_instructions.deadline_utc).toLocaleDateString()
                    : currentJob.application_instructions.is_rolling
                    ? 'Rolling Admissions / Open Until Filled'
                    : 'No explicit deadline specified'}
                </div>
              </div>
              <div>
                <span className="text-xs text-slate-500">Required Application Documents</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {currentJob.application_instructions.required_documents.length > 0 ? (
                    currentJob.application_instructions.required_documents.map((doc, i) => (
                      <Badge key={i} variant="outline" className="border-slate-700 text-slate-300">
                        {doc}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-xs text-slate-500">Standard application materials</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 11: EVIDENCE INSPECTOR */}
        {activeTab === 'evidence' && currentJob && (
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Evidence Provenance Inspector</h3>
            <div className="border border-slate-800 rounded-lg overflow-hidden bg-slate-900/60">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-950 text-xs text-slate-400 uppercase border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3">Section</th>
                    <th className="px-4 py-3">Supporting Text Span</th>
                    <th className="px-4 py-3">Char Offsets</th>
                    <th className="px-4 py-3">Quote Hash</th>
                    <th className="px-4 py-3">Verification</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {currentJob.mandatory_requirements.flatMap((r) => r.evidence).map((ev) => (
                    <tr key={ev.id} className="hover:bg-slate-800/30">
                      <td className="px-4 py-3 text-xs text-cyan-400 font-mono">{ev.section_name}</td>
                      <td className="px-4 py-3 text-xs text-slate-200">{ev.supporting_text}</td>
                      <td className="px-4 py-3 font-mono text-xs text-slate-400">
                        [{ev.start_char}:{ev.end_char}]
                      </td>
                      <td className="px-4 py-3 font-mono text-xs text-slate-500 truncate max-w-xs">
                        {ev.quote_hash.slice(0, 16)}...
                      </td>
                      <td className="px-4 py-3">
                        <Badge
                          variant="outline"
                          className={
                            ev.verified_in_source
                              ? 'border-emerald-500/40 text-emerald-400'
                              : 'border-amber-500/40 text-amber-400'
                          }
                        >
                          {ev.verified_in_source ? 'Verified' : 'Unverified'}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 12: CONFLICT REVIEW */}
        {activeTab === 'conflicts' && (
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Multi-Source Requirement Conflicts</h3>
            {currentJob?.conflicts && currentJob.conflicts.length > 0 ? (
              <div className="space-y-3">
                {currentJob.conflicts.map((conf) => (
                  <div key={conf.id} className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-amber-400">Conflict: {conf.conflict_type}</span>
                      <Badge variant="outline" className="border-amber-500/40 text-amber-400">
                        Pending Resolution
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-xs">
                      <div className="p-3 bg-slate-950 rounded border border-slate-800">
                        <span className="text-slate-500 block mb-1">Source A Statement:</span>
                        <div className="text-slate-300">{conf.source_a_text}</div>
                      </div>
                      <div className="p-3 bg-slate-950 rounded border border-slate-800">
                        <span className="text-slate-500 block mb-1">Source B Statement:</span>
                        <div className="text-slate-300">{conf.source_b_text}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-slate-500 p-6 text-center border border-slate-800 rounded-lg">
                No active source conflicts detected for this posting.
              </div>
            )}
          </div>
        )}

        {/* TAB 13: HUMAN REVIEW QUEUE */}
        {activeTab === 'review_queue' && (
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Human Review & Ambiguity Resolution Queue</h3>
            {reviewQueue.length === 0 ? (
              <div className="text-sm text-slate-500 p-6 text-center border border-slate-800 rounded-lg">
                The review queue is currently empty. All job requirements have verified high-confidence interpretations.
              </div>
            ) : (
              <div className="space-y-3">
                {reviewQueue.map((item) => (
                  <div key={item.id} className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                    <div>
                      <div className="text-sm font-medium text-slate-200">{item.review_type}</div>
                      <div className="text-xs text-slate-400 mt-1">{item.reason}</div>
                      <div className="text-xs text-slate-500 mt-1">Intelligence ID: {item.intelligence_id}</div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={resolveMutation.isPending}
                        onClick={() => resolveMutation.mutate({ id: item.id, decision: 'APPROVED' })}
                        className="border-emerald-600 hover:bg-emerald-950/30 text-emerald-400 text-xs"
                      >
                        Approve
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={resolveMutation.isPending}
                        onClick={() => resolveMutation.mutate({ id: item.id, decision: 'REJECTED' })}
                        className="border-red-600 hover:bg-red-950/30 text-red-400 text-xs"
                      >
                        Reject
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 14: DIAGNOSTICS */}
        {activeTab === 'diagnostics' && (
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Operational Diagnostics</h3>
            <pre className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-400 overflow-x-auto">
              {JSON.stringify(statusData || { status: 'loading' }, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </ModulePage>
  );
};
