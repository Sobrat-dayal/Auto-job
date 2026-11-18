/**
 * Vitest Integration Suite for Stage 25 Career Preferences, Job Eligibility & Autonomous Policy Workspace.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RecruitmentPolicyWorkspace } from '@/features/recruitment/policy/RecruitmentPolicyWorkspace';
import { apiClient } from '@/lib/api-client';
import type {
  CareerStrategy,
  RecruitmentBudget,
  AutonomyStatusResponse,
  StandingGrantRecord,
  ReviewQueueItem,
  RecruitmentDecision,
  PolicySimulationResponse,
} from '@autonom/shared-types';

describe('Recruitment Policy & Career Preference Intelligence (Stage 25)', () => {
  let queryClient: QueryClient;

  const mockStrategy: CareerStrategy = {
    id: 'strat_backend_01',
    owner_id: 'default_user',
    title: 'Backend & Distributed Systems Focus',
    description: 'Targeting mid-to-senior backend engineering roles in distributed systems.',
    is_active: true,
    target_roles: [
      {
        title: 'Backend Software Engineer',
        role_family: 'backend',
        seniority: 'mid_level',
        keywords: ['backend', 'distributed', 'python', 'fastapi'],
        excluded_keywords: ['frontend', 'sales', 'intern'],
        is_primary: true,
        priority_weight: 1.0,
      },
    ],
    seniority: {
      target_levels: ['mid_level', 'senior'],
      strict_enforcement: true,
    },
    employment_types: ['full_time'],
    work_arrangement: {
      allowed_arrangements: ['remote', 'hybrid'],
      preferred_arrangement: 'remote',
      strict_enforcement: true,
    },
    geography: {
      preferred_countries: ['United States', 'Canada'],
      preferred_states_provinces: [],
      preferred_cities: ['San Francisco', 'Seattle'],
      excluded_countries: [],
      excluded_states_provinces: [],
      excluded_cities: ['Dallas'],
      relocation: 'not_willing',
      allowed_timezones: ['UTC-8', 'UTC-5'],
      max_timezone_offset_hours: 3,
      strict_enforcement: true,
    },
    compensation: {
      target_amount: 140000,
      hard_floor_amount: 110000,
      currency: 'USD',
      unit: 'annual',
      undisclosed_handling: 'require_review',
      equity_required: false,
      benefits_required: [],
      strict_enforcement: true,
    },
    employers: {
      allowlist_mode: 'no_allowlist',
      allowed_employers: [],
      blocked_employers: [
        {
          name: 'Restricted Corp',
          domain: 'restrictedcorp.com',
          reason: 'Current employer confidentiality',
          blocked_at: '2026-01-01T00:00:00Z',
        },
      ],
      blocked_industries: ['gambling', 'tobacco'],
      blocked_parent_companies: [],
      target_company_sizes: ['growth', 'enterprise'],
      require_review_on_ambiguous: true,
    },
    sources: {
      allowed_job_boards: ['LinkedIn', 'Wellfound'],
      blocked_job_boards: ['SpamBoard'],
      allow_direct_employer_sites: true,
      allow_third_party_recruiters: false,
      allow_sponsored_listings: false,
      require_review_on_unknown_source: true,
    },
    eligibility_rules: {
      enforce_degree_requirements: true,
      allow_enrolled_for_future_grads: true,
      enforce_work_authorization: true,
      enforce_minimum_experience: true,
      enforce_required_certifications: true,
      minimum_skill_match_percentage: 60.0,
      require_evidenced_skills: false,
    },
    max_posting_age_days: 30,
    autonomy_mode: 'mode_2_prepare_and_review',
    version: 1,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  };

  const mockBudget: RecruitmentBudget = {
    daily_application_limit: 10,
    weekly_application_limit: 50,
    monthly_application_limit: 150,
    daily_applications_count: 2,
    weekly_applications_count: 8,
    monthly_applications_count: 24,
    active_reservations_count: 1,
    daily_discovery_limit: 100,
    daily_preparations_limit: 25,
    daily_discoveries_count: 15,
    daily_preparations_count: 4,
    last_daily_reset: '2026-01-01T00:00:00Z',
    last_weekly_reset: '2026-01-01T00:00:00Z',
    last_monthly_reset: '2026-01-01T00:00:00Z',
  };

  const mockAutonomyStatus: AutonomyStatusResponse = {
    active_autonomy_mode: 'mode_2_prepare_and_review',
    active_strategy_id: 'strat_backend_01',
    active_strategy_title: 'Backend & Distributed Systems Focus',
    standing_grants_count: 1,
    pending_review_queue_count: 0,
    capabilities: {
      can_discover: true,
      can_evaluate: true,
      can_prepare: true,
      can_submit_autonomously: false,
    },
  };

  const mockStandingGrants: StandingGrantRecord[] = [
    {
      id: 'grant_01',
      owner_id: 'default_user',
      grantee_role: 'application_agent',
      scope: 'prepare_application',
      max_actions_per_day: 5,
      actions_taken_today: 1,
      conditions: {},
      issued_at: '2026-01-01T00:00:00Z',
      is_revoked: false,
    },
  ];

  const mockReviewQueue: ReviewQueueItem[] = [];

  const mockDecisions: RecruitmentDecision[] = [
    {
      id: 'dec_01',
      job_id: 'job_stripe_01',
      job_title: 'Backend Software Engineer',
      employer_name: 'Stripe',
      decision: 'proceed',
      precedence_level: 10,
      primary_rationale: 'Job strictly satisfies all hard requirements and achieves strong soft affinity.',
      reasons: ['Role family matches', 'Compensation meets target'],
      violations: [],
      review_triggers: [],
      soft_preference_score: 92.5,
      compensation_match_status: 'meets_or_exceeds',
      normalized_annual_salary: 155000,
      recommended_action: 'Proceed with resume tailoring and screening answer preparation.',
      evaluated_at: '2026-01-01T00:00:00Z',
    },
  ];

  const mockSimResponse: PolicySimulationResponse = {
    synthetic_job: {
      title: 'Senior Backend Engineer',
      employer_name: 'TechCorp Global',
    },
    decision: {
      id: 'sim_dec_01',
      job_id: 'synthetic_job_sim',
      job_title: 'Senior Backend Engineer',
      employer_name: 'TechCorp Global',
      decision: 'proceed',
      precedence_level: 10,
      primary_rationale: 'Level 10: Opportunity satisfies all hard invariants and scored 88.0 affinity.',
      reasons: ['Backend match', 'Salary above floor'],
      violations: [],
      review_triggers: [],
      soft_preference_score: 88.0,
      compensation_match_status: 'meets_or_exceeds',
      normalized_annual_salary: 135000,
      recommended_action: 'Prepare application draft under Mode 2 review.',
      evaluated_at: '2026-01-01T00:00:00Z',
      eligibility_assessment: {
        job_id: 'synthetic_job_sim',
        outcome: 'eligible',
        overall_score: 90.0,
        education_matched: true,
        experience_years_required: 4,
        experience_years_verified: 5,
        experience_matched: true,
        skills_required_count: 4,
        skills_matched_count: 4,
        skills_evidenced_count: 3,
        skill_match_percentage: 100.0,
        missing_critical_skills: [],
        certifications_matched: true,
        work_authorization_valid: true,
        evaluated_at: '2026-01-01T00:00:00Z',
      },
    },
    simulated_at: '2026-01-01T00:00:00Z',
  };

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false, gcTime: 0 },
      },
    });

    vi.spyOn(apiClient, 'listCareerStrategies').mockResolvedValue([mockStrategy]);
    vi.spyOn(apiClient, 'getAutonomyStatus').mockResolvedValue(mockAutonomyStatus);
    vi.spyOn(apiClient, 'getRecruitmentBudget').mockResolvedValue(mockBudget);
    vi.spyOn(apiClient, 'listStandingGrants').mockResolvedValue(mockStandingGrants);
    vi.spyOn(apiClient, 'listReviewQueue').mockResolvedValue(mockReviewQueue);
    vi.spyOn(apiClient, 'listPolicyDecisions').mockResolvedValue(mockDecisions);
    vi.spyOn(apiClient, 'simulatePolicy').mockResolvedValue(mockSimResponse);
    vi.spyOn(apiClient, 'activateCareerStrategy').mockResolvedValue(mockStrategy);
    vi.spyOn(apiClient, 'createCareerStrategy').mockResolvedValue(mockStrategy);
    vi.spyOn(apiClient, 'updateCareerStrategy').mockResolvedValue(mockStrategy);
    vi.spyOn(apiClient, 'updateRecruitmentBudget').mockResolvedValue(mockBudget);
  });

  const renderWorkspace = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <RecruitmentPolicyWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

  it('renders the workspace with active strategy and overview cards', async () => {
    renderWorkspace();

    expect(
      screen.getByText(/Career Preferences, Eligibility Rules & Policy Engine/i)
    ).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Backend & Distributed Systems Focus')).toBeInTheDocument();
      expect(screen.getByText('Mode 2: Prepare & Review (Default)')).toBeInTheDocument();
      expect(screen.getByText('2 / 10')).toBeInTheDocument();
      expect(screen.getByText('1 Blocked')).toBeInTheDocument();
    });
  });

  it('displays recent policy decisions and audit trail on overview', async () => {
    renderWorkspace();

    await waitFor(() => {
      expect(screen.getByText('Stripe')).toBeInTheDocument();
      expect(screen.getByText(/Level 10 Precedence/i)).toBeInTheDocument();
    });
  });

  it('switches to Target Roles tab and displays configured roles', async () => {
    renderWorkspace();

    const rolesTabBtn = screen.getByRole('tab', { name: /Target Roles/i });
    fireEvent.click(rolesTabBtn);

    await waitFor(() => {
      expect(screen.getByText(/Target Roles & Specialization Taxonomy/i)).toBeInTheDocument();
      expect(screen.getByText('Backend Software Engineer')).toBeInTheDocument();
      expect(screen.getByText('PRIMARY')).toBeInTheDocument();
    });
  });

  it('switches to Locations tab and shows work arrangement options', async () => {
    renderWorkspace();

    const locTabBtn = screen.getByRole('tab', { name: /Locations/i });
    fireEvent.click(locTabBtn);

    await waitFor(() => {
      expect(screen.getByText(/Location, Remote Work & Time Zone Policies/i)).toBeInTheDocument();
      expect(screen.getByText(/Allowed Work Arrangements/i)).toBeInTheDocument();
      expect(screen.getByText(/Target Countries/i)).toBeInTheDocument();
    });
  });

  it('switches to Compensation tab and verifies salary floor settings', async () => {
    renderWorkspace();

    const compTabBtn = screen.getByRole('tab', { name: /Compensation/i });
    fireEvent.click(compTabBtn);

    await waitFor(() => {
      expect(screen.getByText(/Compensation Policies & Salary Floor Guard/i)).toBeInTheDocument();
      expect(screen.getByText(/Base Compensation Parameters/i)).toBeInTheDocument();
      expect(screen.getByText(/Undisclosed Salary Handling Policy/i)).toBeInTheDocument();
    });
  });

  it('switches to Employers tab and shows blocked company items', async () => {
    renderWorkspace();

    const empTabBtn = screen.getByRole('tab', { name: /Employers/i });
    fireEvent.click(empTabBtn);

    await waitFor(() => {
      expect(screen.getByText(/Employer Blocklists, Allowlists/i)).toBeInTheDocument();
      expect(screen.getByText('Restricted Corp')).toBeInTheDocument();
      expect(screen.getByText(/Current employer confidentiality/i)).toBeInTheDocument();
    });
  });

  it('switches to Precedence tab and visualizes 10-level hierarchy', async () => {
    renderWorkspace();

    const precTabBtn = screen.getByRole('tab', { name: /Precedence/i });
    fireEvent.click(precTabBtn);

    await waitFor(() => {
      expect(screen.getByText(/10-Level Precedence Hierarchy/i)).toBeInTheDocument();
      expect(screen.getByText(/Level 1: Emergency Stop Engaged/i)).toBeInTheDocument();
      expect(screen.getByText(/Level 6: Employer Blocklists/i)).toBeInTheDocument();
      expect(screen.getByText(/Level 10: Soft Preference Scoring/i)).toBeInTheDocument();
    });
  });

  it('switches to Budgets tab and displays multi-agent limits', async () => {
    renderWorkspace();

    const budTabBtn = screen.getByRole('tab', { name: /Budgets/i });
    fireEvent.click(budTabBtn);

    await waitFor(() => {
      expect(screen.getByText(/Multi-Agent Application Budgets/i)).toBeInTheDocument();
      expect(screen.getByText('2 / 10')).toBeInTheDocument();
      expect(screen.getByText('8 / 50')).toBeInTheDocument();
      expect(screen.getByText('24 / 150')).toBeInTheDocument();
    });
  });

  it('runs the Policy Simulator and presents explainable verdict breakdown', async () => {
    renderWorkspace();

    const simTabBtn = screen.getByRole('tab', { name: /Simulator/i });
    fireEvent.click(simTabBtn);

    await waitFor(() => {
      expect(screen.getByText(/Zero-Side-Effect Policy Sandbox/i)).toBeInTheDocument();
    });

    const runBtn = screen.getByRole('button', { name: /Run Policy Simulation/i });
    fireEvent.click(runBtn);

    await waitFor(() => {
      expect(apiClient.simulatePolicy).toHaveBeenCalled();
      expect(screen.getByText(/Evaluated under Precedence Level 10/i)).toBeInTheDocument();
      expect(screen.getByText(/Factual Qualification Assessment/i)).toBeInTheDocument();
      expect(screen.getByText(/88.0 \/ 100/i)).toBeInTheDocument();
    });
  });
});
