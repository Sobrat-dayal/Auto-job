/**
 * Vitest Integration Suite for Stage 29 Applicant-to-Job Matching Workspace.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { JobMatchingWorkspace } from '@/features/recruitment/matching/JobMatchingWorkspace';
import { apiClient } from '@/lib/api-client';
import type {
  JobMatchEvaluation,
  RankedOpportunityItem,
  RankingOverview,
  RubricConfig,
  SimulationResponse,
} from '@autonom/shared-types';

describe('Applicant-to-Job Matching Desktop Workspace (Stage 29)', () => {
  let queryClient: QueryClient;

  const mockEvaluation: JobMatchEvaluation = {
    id: 'eval-1',
    profile_id: 'prof-1',
    canonical_job_id: 'job-1',
    job_title: 'Senior Backend Engineer',
    company_name: 'Acme Cloud Corp',
    job_location: 'San Francisco, CA',
    employment_type: 'Full-Time',
    work_arrangement: 'Remote',
    career_strategy_id: 'strat-1',
    rubric_id: 'rubric_default_v1',
    version: 1,
    is_current: true,
    status: 'completed',
    eligibility_outcome: 'eligible_and_aligned',
    relevance_index: 92.5,
    mandatory_coverage_ratio: 1.0,
    preferred_coverage_ratio: 0.8,
    evidence_completeness_ratio: 0.95,
    ranking_uncertainty_ratio: 0.05,
    application_readiness: 'ready_for_preparation',
    hard_policy_passed: true,
    hard_policy_reason: null,
    summary_explanation: 'Applicant satisfies all mandatory qualifications and has strong Python/Postgres alignment.',
    requirement_results: [
      {
        requirement_id: 'req-1',
        name: 'Python',
        category: 'mandatory',
        match_category: 'directly_satisfied',
        applicant_claim_ref: 'claim-1',
        applicant_evidence_snippet: '5 years professional Python experience',
        job_evidence_snippet: '5+ years Python required',
        confidence: 1.0,
        explanation: 'Directly verified from employment history.',
        is_satisfied: true,
      },
      {
        requirement_id: 'req-2',
        name: 'Kubernetes',
        category: 'preferred',
        match_category: 'partially_supported',
        applicant_claim_ref: null,
        applicant_evidence_snippet: 'Used in 1 personal project',
        job_evidence_snippet: 'Kubernetes preferred',
        confidence: 0.8,
        explanation: 'Personal project usage evidenced.',
        is_satisfied: true,
      },
    ],
    group_results: [
      {
        group_id: 'grp-1',
        operator: 'AND',
        target_count: 1,
        satisfied_count: 1,
        is_satisfied: true,
        is_unknown: false,
        explanation: 'Mandatory technical requirements met.',
      },
    ],
    skill_details: [
      {
        skill_name: 'Python',
        canonical_name: 'python',
        category: 'technical',
        priority: 'MANDATORY',
        required_years: 5.0,
        applicant_years: 5.0,
        applicant_proficiency: 'advanced',
        match_status: 'directly_satisfied',
        is_alias_match: false,
        is_related_match: false,
        explanation: 'Direct match.',
      },
    ],
    education_detail: {
      degree_level: 'Bachelor',
      field_of_study: 'Computer Science',
      applicant_degree: 'B.S. in Computer Science',
      applicant_field: 'Computer Science',
      applicant_status: 'completed',
      status_compatible: true,
      field_compatible: true,
      match_status: 'directly_satisfied',
      explanation: 'Holds completed B.S. in Computer Science.',
    },
    experience_detail: {
      required_min_years: 5.0,
      required_max_years: null,
      required_domain: 'Backend Engineering',
      calculated_professional_years: 5.2,
      total_calendar_months_non_overlapping: 62,
      has_overlapping_roles: false,
      internship_months: 6,
      academic_project_count: 3,
      match_status: 'directly_satisfied',
      explanation: '5.2 years of non-overlapping professional experience.',
    },
    eligibility_detail: {
      work_authorization_status: 'directly_satisfied',
      sponsorship_status: 'directly_satisfied',
      remote_compatibility: 'directly_satisfied',
      location_compatibility: 'directly_satisfied',
      relocation_compatibility: 'acceptable',
      compensation_compatibility: '100%',
      employer_restriction_status: 'allowed',
      hard_policy_passed: true,
      hard_policy_reason: null,
      explanation: 'All eligibility checks passed.',
    },
    score_breakdown: {
      relevance_index: 92.5,
      total_weight_observed: 1.0,
      dimensions: [
        {
          dimension_id: 'qualification_alignment',
          name: 'Mandatory Qualifications',
          raw_score: 1.0,
          weight: 0.25,
          weighted_score: 0.25,
          max_possible_weighted_score: 0.25,
          is_observed: true,
          explanation: '100% mandatory qualifications satisfied.',
        },
        {
          dimension_id: 'preferred_skills',
          name: 'Preferred Skills',
          raw_score: 0.8,
          weight: 0.15,
          weighted_score: 0.12,
          max_possible_weighted_score: 0.15,
          is_observed: true,
          explanation: '80% preferred skills satisfied.',
        },
      ],
      missing_dimensions: [],
      formula_explanation: 'Normalized weighted average.',
    },
    gaps: [
      {
        id: 'gap-1',
        requirement_id: 'req-2',
        skill_or_qualification: 'Kubernetes',
        gap_type: 'missing_preferred_skill',
        severity: 'moderate',
        description: 'Preferred skill has limited tenure in profile.',
        remediation_suggestion: 'Document production Kubernetes deployments in project portfolio.',
      },
    ],
    missing_information: [],
    review_requests: [],
    counterfactuals: [
      {
        scenario_name: 'Add AWS Certification',
        hypothetical_change: 'Add certified AWS Solutions Architect credential',
        current_state: 'Eligible & Aligned',
        simulated_state: 'High Priority Match',
        impact_summary: 'Would increase cloud alignment score by 8%.',
      },
    ],
    evaluated_at: '2026-03-30T12:00:00Z',
    updated_at: '2026-03-30T12:00:00Z',
  };

  const mockRankedItem: RankedOpportunityItem = {
    rank: 1,
    evaluation_id: 'eval-1',
    canonical_job_id: 'job-1',
    job_title: 'Senior Backend Engineer',
    company_name: 'Acme Cloud Corp',
    location: 'San Francisco, CA',
    work_arrangement: 'Remote',
    employment_type: 'Full-Time',
    eligibility_outcome: 'eligible_and_aligned',
    relevance_index: 92.5,
    mandatory_coverage_ratio: 1.0,
    preferred_coverage_ratio: 0.8,
    critical_gaps_count: 0,
    unknowns_count: 0,
    application_readiness: 'ready_for_preparation',
    posting_discovered_at: '2026-03-29T10:00:00Z',
    last_evaluated_at: '2026-03-30T12:00:00Z',
  };

  const mockOverview: RankingOverview = {
    total_evaluated: 1,
    eligible_and_aligned: 1,
    conditionally_eligible: 0,
    requires_review: 0,
    known_unmet: 0,
    hard_policy_excluded: 0,
    average_relevance_index: 92.5,
    latest_evaluation_at: '2026-03-30T12:00:00Z',
  };

  const mockRubric: RubricConfig = {
    id: 'rubric_default_v1',
    version: 1,
    name: 'Standard AUTONOM Recruitment Rubric',
    description: 'Balanced scoring across mandatory qualifications, location, and salary.',
    is_default: true,
    weights: {
      qualification_alignment: 0.25,
      preferred_skills: 0.15,
      compensation: 0.10,
    },
    missing_data_policy: 'conservative',
  };

  const mockSimulationResponse: SimulationResponse = {
    simulation_id: 'sim-1',
    evaluation_id: 'eval-1',
    scenario_name: 'Add Skills & Authorization',
    original_relevance_index: 92.5,
    simulated_relevance_index: 98.0,
    original_eligibility: 'eligible_and_aligned',
    simulated_eligibility: 'eligible_and_aligned',
    diff_explanation: "Simulated scenario: Relevance changed from 92.5 to 98.0 (+5.5 pts).",
    dimension_diffs: [
      {
        dimension_id: 'preferred_skills',
        name: 'Preferred Skills',
        before_score: 0.8,
        after_score: 1.0,
        diff: 0.2,
      },
    ],
    remaining_gaps: [],
  };

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    vi.spyOn(apiClient, 'getMatchingStatus').mockResolvedValue({ status: 'operational' });
    vi.spyOn(apiClient, 'getOpportunityRankings').mockResolvedValue({
      items: [mockRankedItem],
      overview: mockOverview,
    });
    vi.spyOn(apiClient, 'listMatchResults').mockResolvedValue([mockEvaluation]);
    vi.spyOn(apiClient, 'getMatchingReviewQueue').mockResolvedValue([]);
    vi.spyOn(apiClient, 'listMatchingRubrics').mockResolvedValue([mockRubric]);
    vi.spyOn(apiClient, 'simulateMatchingScenario').mockResolvedValue(mockSimulationResponse);
  });

  const renderComponent = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <JobMatchingWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

  it('renders overview dashboard with KPI metrics and top recommended opportunities', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Job Matching & Prioritization Engine')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getAllByText('Senior Backend Engineer').length).toBeGreaterThanOrEqual(1);
    });

    // Check KPI metrics
    expect(screen.getByText('Total Evaluated')).toBeInTheDocument();
    expect(screen.getAllByText('Eligible & Aligned').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Acme Cloud Corp').length).toBeGreaterThanOrEqual(1);
  });

  it('renders Ranked Opportunities table with deterministic ranking metrics', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Job Matching & Prioritization Engine')).toBeInTheDocument();
    });

    const rankingsTab = screen.getByRole('tab', { name: /Ranked Opportunities/i });
    fireEvent.click(rankingsTab);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Filter by role, employer, or location...')).toBeInTheDocument();
    });

    expect(screen.getByText('#1')).toBeInTheDocument();
    expect(screen.getByText('92.5/100')).toBeInTheDocument();
  });

  it('inspects Match Details and Qualification Matrix', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Job Matching & Prioritization Engine')).toBeInTheDocument();
    });

    const matrixTab = screen.getByRole('tab', { name: /Qualification Matrix/i });
    fireEvent.click(matrixTab);

    await waitFor(() => {
      expect(screen.getByText(/Requirement-by-Requirement Evidence Matrix/i)).toBeInTheDocument();
    });

    expect(screen.getByText('Python')).toBeInTheDocument();
    expect(screen.getByText('5 years professional Python experience')).toBeInTheDocument();
  });

  it('displays Skill Gap Explorer with grounded remediation suggestions', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Job Matching & Prioritization Engine')).toBeInTheDocument();
    });

    const gapsTab = screen.getByRole('tab', { name: /Skill Gap Explorer/i });
    fireEvent.click(gapsTab);

    await waitFor(() => {
      expect(screen.getByText(/Qualification Gaps & Grounded Remediation Suggestions/i)).toBeInTheDocument();
    });

    expect(screen.getByText('Kubernetes')).toBeInTheDocument();
    expect(screen.getByText(/Document production Kubernetes deployments/i)).toBeInTheDocument();
  });

  it('executes What-If Simulator and displays simulation score diffs', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Job Matching & Prioritization Engine')).toBeInTheDocument();
    });

    const simTab = screen.getByRole('tab', { name: /What-If Simulator/i });
    fireEvent.click(simTab);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Run Hypothetical Simulation/i })).toBeInTheDocument();
    });

    const runBtn = screen.getByRole('button', { name: /Run Hypothetical Simulation/i });
    fireEvent.click(runBtn);

    await waitFor(() => {
      expect(screen.getByText(/Simulated scenario: Relevance changed from 92.5 to 98.0/i)).toBeInTheDocument();
    });

    expect(screen.getByText('98.0/100')).toBeInTheDocument();
  });
});
