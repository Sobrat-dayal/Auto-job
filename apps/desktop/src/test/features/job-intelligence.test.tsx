/**
 * Vitest Integration Suite for Stage 28 Job Requirement Intelligence Workspace.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { JobIntelligenceWorkspace } from '@/features/recruitment/intelligence/JobIntelligenceWorkspace';
import { apiClient } from '@/lib/api-client';
import type {
  JobIntelligenceRecord,
  JobIntelligenceReviewItem,
} from '@autonom/shared-types';

describe('Job Requirement Intelligence Desktop Workspace (Stage 28)', () => {
  let queryClient: QueryClient;

  const mockJob: JobIntelligenceRecord = {
    id: 'intel-1',
    canonical_job_id: 'job-stripe-1',
    canonical_job_version: 1,
    description_hash: 'hash1234',
    extractor_version: '1.0.0',
    analysis_status: 'Completed',
    job_title: 'Staff Distributed Systems Engineer',
    role_family: 'Software Engineering',
    seniority: 'Staff',
    responsibilities: ['Build distributed consensus engine in Rust and Go.'],
    mandatory_requirements: [
      {
        id: 'req-1',
        category: 'Mandatory',
        qualification_type: 'TECHNICAL_SKILL',
        name: 'Python',
        normalized_value: 'python',
        raw_text: '5+ years experience with Python.',
        min_years: 5.0,
        is_negated: false,
        confidence: 'EXPLICIT_VERIFIED_SOURCE',
        confidence_score: 1.0,
        evidence: [
          {
            id: 'ev-1',
            section_name: 'MINIMUM_QUALIFICATIONS',
            supporting_text: '5+ years experience with Python.',
            start_char: 10,
            end_char: 42,
            quote_hash: 'hash-py',
            extraction_method: 'DETERMINISTIC_RULES',
            verified_in_source: true,
            created_at: '2026-03-30T10:00:00Z',
          },
        ],
        needs_review: false,
      },
    ],
    preferred_requirements: [
      {
        id: 'req-2',
        category: 'Preferred',
        qualification_type: 'TECHNICAL_SKILL',
        name: 'Kubernetes',
        normalized_value: 'kubernetes',
        raw_text: 'Experience with Kubernetes.',
        is_negated: false,
        confidence: 'EXPLICIT_VERIFIED_SOURCE',
        confidence_score: 1.0,
        evidence: [],
        needs_review: false,
      },
    ],
    optional_requirements: [],
    conditional_requirements: [],
    requirement_groups: [
      {
        id: 'grp-1',
        operator: 'AND',
        description: 'Minimum Requirements',
        requirement_ids: ['req-1'],
        child_group_ids: [],
      },
    ],
    skills: [
      {
        name: 'Python',
        normalized_name: 'python',
        category: 'PROGRAMMING_LANGUAGE',
        min_years: 5.0,
        is_mandatory: true,
      },
      {
        name: 'Kubernetes',
        normalized_name: 'kubernetes',
        category: 'CLOUD_DEVOPS',
        is_mandatory: false,
      },
    ],
    education: [
      {
        degree_level: 'BACHELOR',
        fields_of_study: ['Computer Science'],
        degree_status: 'COMPLETED',
        alternative_experience_years: 4.0,
        is_mandatory: true,
        raw_text: "Bachelor's degree or equivalent practical experience.",
        evidence: [],
      },
    ],
    experience: [
      {
        minimum_years: 5.0,
        maximum_years: null,
        domain_categories: ['Distributed Systems'],
        is_mandatory: true,
        raw_text: '5+ years experience.',
        evidence: [],
      },
    ],
    employment_conditions: {
      workplace_type: 'REMOTE_GLOBAL',
      primary_location: 'Remote',
      allowed_countries: [],
      office_days_per_week: null,
      travel_percentage: 0.0,
      working_hours: 'Flexible',
      employment_type: 'FULL_TIME',
      contract_duration: null,
      is_relocation_offered: null,
      evidence: [],
    },
    compensation: {
      base_min: 190000,
      base_max: 240000,
      currency: 'USD',
      pay_period: 'ANNUAL',
      has_bonus: true,
      bonus_details: '15% bonus',
      has_equity: true,
      equity_details: 'RSUs',
      benefits: ['Health Insurance', '401(k) / Retirement'],
      original_text: '$190,000 - $240,000 / year',
      is_disclosed: true,
      is_ambiguous: false,
      evidence: [],
    },
    eligibility: {
      work_authorization_required: true,
      visa_sponsorship_offered: true,
      visa_sponsorship_refused: false,
      citizenship_restrictions: [],
      security_clearance_required: null,
      is_ambiguous: false,
      evidence: [],
    },
    application_instructions: {
      deadline_utc: '2026-06-15T00:00:00Z',
      is_rolling: false,
      start_date_utc: null,
      application_url: 'https://stripe.com/jobs/1',
      required_documents: ['Resume / CV', 'Cover Letter'],
      instructions_text: 'Submit Resume and Cover Letter.',
      evidence: [],
    },
    conflicts: [],
    review_items: [],
    data_quality_warnings: [],
    overall_confidence: 0.98,
    review_status: 'NOT_NEEDED',
    created_at: '2026-03-30T10:00:00Z',
    updated_at: '2026-03-30T10:00:00Z',
  };

  const mockReviewItems: JobIntelligenceReviewItem[] = [
    {
      id: 'rev-item-1',
      intelligence_id: 'intel-1',
      review_type: 'AMBIGUOUS_REQUIREMENT',
      reason: 'AI flagged ambiguous requirement strength for manual verification',
      status: 'PENDING',
      created_at: '2026-03-30T10:00:00Z',
    },
  ];

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false, gcTime: 0 },
      },
    });
    vi.clearAllMocks();

    vi.spyOn(apiClient, 'getIntelligenceStatus').mockResolvedValue({
      total_records: 1,
      extractor_version: '1.0.0',
    });
    vi.spyOn(apiClient, 'listAnalyzedJobs').mockResolvedValue([mockJob]);
    vi.spyOn(apiClient, 'getJobIntelligence').mockResolvedValue(mockJob);
    vi.spyOn(apiClient, 'getReviewQueue').mockResolvedValue(mockReviewItems);
    vi.spyOn(apiClient, 'resolveReviewItem').mockResolvedValue({
      ...mockReviewItems[0],
      status: 'APPROVED',
    });
  });

  const renderComponent = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <JobIntelligenceWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

  it('renders Job Intelligence workspace overview and KPI metrics', async () => {
    renderComponent();

    expect(screen.getAllByText('Job Requirement Intelligence').length).toBeGreaterThanOrEqual(1);
    await waitFor(() => {
      expect(screen.getByText('Total Analyzed Postings')).toBeDefined();
      expect(screen.getByText('Pending Review Items')).toBeDefined();
      expect(screen.getAllByText('1').length).toBeGreaterThanOrEqual(1);
    });
  });

  it('navigates to Analyzed Jobs tab and renders table of postings', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Analyzed Jobs')).toBeDefined();
    });

    fireEvent.click(screen.getByText('Analyzed Jobs'));

    await waitFor(() => {
      expect(screen.getByText('Staff Distributed Systems Engineer')).toBeDefined();
      expect(screen.getByText('job-stripe-1')).toBeDefined();
      expect(screen.getByText('Completed')).toBeDefined();
    });
  });

  it('navigates to Requirements Explorer and renders mandatory and preferred items', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Analyzed Jobs')).toBeDefined();
    });

    fireEvent.click(screen.getByText('Analyzed Jobs'));

    await waitFor(() => {
      expect(screen.getByText('Inspect')).toBeDefined();
    });

    fireEvent.click(screen.getByText('Inspect'));

    await waitFor(() => {
      expect(screen.getByText('Staff Distributed Systems Engineer')).toBeDefined();
      expect(screen.getByText('Python')).toBeDefined();
      expect(screen.getAllByText('Mandatory').length).toBeGreaterThanOrEqual(1);
    });
  });

  it('navigates to Technology Stack and renders categorized skills', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Technology Stack')).toBeDefined();
    });

    fireEvent.click(screen.getByText('Technology Stack'));

    await waitFor(() => {
      expect(screen.getByText('Normalized Technical Skills')).toBeDefined();
      expect(screen.getByText('Python')).toBeDefined();
      expect(screen.getByText('Kubernetes')).toBeDefined();
      expect(screen.getByText('Category: PROGRAMMING_LANGUAGE')).toBeDefined();
    });
  });

  it('navigates to Review Queue and resolves pending items', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Review Queue')).toBeDefined();
    });

    fireEvent.click(screen.getByText('Review Queue'));

    await waitFor(() => {
      expect(screen.getByText('AMBIGUOUS_REQUIREMENT')).toBeDefined();
      expect(screen.getByText('Approve')).toBeDefined();
      expect(screen.getByText('Reject')).toBeDefined();
    });

    fireEvent.click(screen.getByText('Approve'));

    await waitFor(() => {
      expect(apiClient.resolveReviewItem).toHaveBeenCalledWith('rev-item-1', 'APPROVED');
    });
  });
});
