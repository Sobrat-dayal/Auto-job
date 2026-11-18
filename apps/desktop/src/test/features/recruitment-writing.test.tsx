/**
 * Vitest Integration Suite for Stage 24 Recruitment Writing & Application Answers Desktop Workspace.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RecruitmentWritingWorkspace } from '@/features/recruitment/writing/RecruitmentWritingWorkspace';
import { apiClient } from '@/lib/api-client';
import type {
  WritingOverviewStats,
  CoverLetterDocument,
  CoverLetterTemplateDefinition,
  ApplicationQuestionSet,
  AnswerLibraryEntry,
  MissingInformationItem,
  SensitiveDecisionItem,
  ConflictItem,
  ApplicationWritingPackage,
} from '@autonom/shared-types';

describe('Recruitment Writing & Application Intelligence (Stage 24)', () => {
  let queryClient: QueryClient;

  const mockStats: WritingOverviewStats = {
    total_cover_letters: 2,
    approved_cover_letters: 1,
    total_question_sets: 2,
    total_screening_questions: 7,
    approved_library_answers: 4,
    pending_reviews: 1,
    missing_info_count: 1,
    sensitive_decisions_count: 2,
    writing_packages_count: 1,
  };

  const mockCoverLetters: CoverLetterDocument[] = [
    {
      id: 'cl_01',
      owner_id: 'user_01',
      profile_id: 'prof_01',
      profile_snapshot_id: 'snap_01',
      title: 'Senior Software Engineer Cover Letter - Stripe',
      letter_type: 'role_specific',
      target_role: 'Senior Software Engineer',
      employer_name: 'Stripe',
      job_description_raw: 'Python and distributed systems expertise.',
      template_id: 'classic_professional',
      tone: 'professional',
      length_preference: 'standard',
      status: 'approved',
      current_version: 1,
      content_hash: 'hash_cl_01',
      blocks: [
        {
          id: 'blk_salutation',
          block_type: 'salutation',
          text: 'Dear Stripe Hiring Team,',
          ordering: 1,
          source_refs: [],
          word_count: 4,
          is_user_edited: false,
        },
        {
          id: 'blk_opening',
          block_type: 'opening',
          text: 'I am writing to express my strong enthusiasm for the Senior Software Engineer position at Stripe.',
          ordering: 2,
          source_refs: [
            {
              source_entity_id: 'exp_01',
              source_type: 'experience',
              verification_status: 'user_confirmed',
              attribution_text: 'Lead Infrastructure Architect',
            },
          ],
          word_count: 17,
          is_user_edited: false,
        },
      ],
      created_at: '2026-11-18T10:00:00Z',
      updated_at: '2026-11-18T12:00:00Z',
    },
  ];

  const mockTemplates: CoverLetterTemplateDefinition[] = [
    {
      id: 'classic_professional',
      name: 'Classic Professional',
      description: 'Traditional formal serif presentation with balanced margins.',
      category: 'General & Executive',
      version: '1.0.0',
      primary_font: 'Times New Roman',
      heading_font: 'Times New Roman Bold',
      base_font_size_pt: 11,
      heading_font_size_pt: 14,
      margin_top_in: 0.75,
      margin_bottom_in: 0.75,
      margin_left_in: 0.75,
      margin_right_in: 0.75,
      primary_color: '#1e293b',
      accent_color: '#3b82f6',
      text_color: '#0f172a',
      line_spacing: 1.15,
      layout_style: 'classic',
    },
  ];

  const mockQuestionSets: ApplicationQuestionSet[] = [
    {
      id: 'qs_01',
      owner_id: 'user_01',
      title: 'Stripe Engineering Screening',
      job_title: 'Senior Software Engineer',
      employer: 'Stripe',
      questions: [
        {
          id: 'q_01',
          set_id: 'qs_01',
          exact_question_text: 'How many years of experience do you have with Python?',
          normalized_question: 'how many years experience python',
          category: 'experience',
          answer_type: 'numeric',
          is_required: true,
          allowed_options: [],
          is_sensitive: false,
          requires_attestation: false,
          current_answer: {
            id: 'ans_01',
            question_id: 'q_01',
            profile_id: 'prof_01',
            profile_version: 1,
            answer_text: '6 years of verifiable Python engineering experience.',
            numeric_value: 6.0,
            selected_options: [],
            state: 'approved',
            freshness_status: 'fresh',
            source_refs: [
              {
                source_entity_id: 'skl_py',
                source_type: 'skill',
                verification_status: 'user_confirmed',
              },
            ],
            confidence_score: 0.95,
            is_user_overridden: false,
            validation_issues: [],
            created_at: '2026-11-18T10:00:00Z',
            updated_at: '2026-11-18T10:00:00Z',
          },
        },
      ],
      created_at: '2026-11-18T10:00:00Z',
      updated_at: '2026-11-18T10:00:00Z',
    },
  ];

  const mockLibraryEntries: AnswerLibraryEntry[] = [
    {
      id: 'lib_01',
      owner_id: 'user_01',
      title: 'Production Outage Handling (STAR)',
      category: 'behavioral',
      parameterized_template: 'During an outage at {employer}, I diagnosed network partition in {technology}.',
      sample_resolved_text: 'During an outage at Stripe, I diagnosed network partition in Kubernetes.',
      answer_type: 'paragraph',
      applicable_technologies: ['Kubernetes', 'Linux'],
      associated_project_ids: [],
      state: 'approved',
      version_number: 1,
      reuse_count: 3,
      created_at: '2026-11-18T10:00:00Z',
      updated_at: '2026-11-18T10:00:00Z',
    },
  ];

  const mockMissingItems: MissingInformationItem[] = [
    {
      id: 'mis_01',
      question_id: 'q_salary',
      question_text: 'What is your expected salary?',
      required_field: 'Target Compensation Base',
      field_description: 'Annual base compensation range in USD',
      is_mandatory: true,
      suggested_profile_destination: 'eligibility.target_compensation',
      resolved: false,
    },
  ];

  const mockSensitiveDecisions: SensitiveDecisionItem[] = [
    {
      id: 'sens_01',
      question_id: 'q_auth',
      question_text: 'Are you legally authorized to work in the United States?',
      category: 'work_authorization',
      allowed_choices: ['Yes', 'No'],
      is_voluntary: false,
      user_decision: 'Yes',
      attestation_accepted: true,
      decided_at: '2026-11-18T10:00:00Z',
    },
  ];

  const mockConflicts: ConflictItem[] = [
    {
      id: 'conf_01',
      title: 'Years of Experience Discrepancy',
      description: 'Profile recorded 6 years while candidate answer claims 8 years.',
      source_a: 'Applicant Profile Skill: Python',
      source_b: 'Application Screening Answer',
      claim_a_value: '6.0 years',
      claim_b_value: '8.0 years',
      resolved: false,
      resolution_note: 'Update profile or align answer with verified resume employment history.',
    },
  ];

  const mockPackages: ApplicationWritingPackage[] = [
    {
      id: 'pkg_01',
      owner_id: 'user_01',
      target_job_title: 'Senior Software Engineer',
      target_employer: 'Stripe',
      profile_snapshot_id: 'snap_01',
      cover_letter_id: 'cl_01',
      question_set_id: 'qs_01',
      status: 'ready_for_approval',
      version_number: 1,
      total_questions: 1,
      answered_questions: 1,
      pending_sensitive_decisions: 0,
      pending_attestations: 0,
      missing_information_count: 0,
      conflicts_count: 0,
      is_ready_for_approval: true,
      created_at: '2026-11-18T10:00:00Z',
      updated_at: '2026-11-18T10:00:00Z',
    },
  ];

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });

    vi.spyOn(apiClient, 'getWritingOverview').mockResolvedValue(mockStats);
    vi.spyOn(apiClient, 'listCoverLetters').mockResolvedValue(mockCoverLetters);
    vi.spyOn(apiClient, 'listCoverLetterTemplates').mockResolvedValue(mockTemplates);
    vi.spyOn(apiClient, 'listQuestionSets').mockResolvedValue(mockQuestionSets);
    vi.spyOn(apiClient, 'listAnswerLibrary').mockResolvedValue(mockLibraryEntries);
    vi.spyOn(apiClient, 'getMissingInformation').mockResolvedValue(mockMissingItems);
    vi.spyOn(apiClient, 'getSensitiveDecisions').mockResolvedValue(mockSensitiveDecisions);
    vi.spyOn(apiClient, 'getWritingConflicts').mockResolvedValue(mockConflicts);
    vi.spyOn(apiClient, 'listWritingPackages').mockResolvedValue(mockPackages);
    vi.spyOn(apiClient, 'validateCoverLetter').mockResolvedValue({
      is_valid: true,
      errors: [],
      warnings: [],
      total_words: 21,
      verified_facts_count: 1,
    });
  });

  const renderComponent = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <RecruitmentWritingWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

  it('renders recruitment writing workspace with overview stats and zero-hallucination badge', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Recruitment Writing & Application Intelligence')).toBeInTheDocument();
      expect(screen.getByText('Zero-Hallucination Enforced')).toBeInTheDocument();
    });

    // Check stats metrics cards
    expect(screen.getByText('Cover Letters')).toBeInTheDocument();
    expect(screen.getByText('Screening Q&A')).toBeInTheDocument();
    expect(screen.getByText('Answer Library')).toBeInTheDocument();
    expect(screen.getAllByText('Sensitive Decisions')[0]).toBeInTheDocument();
  });

  it('switches to Cover Letter Studio tab and displays generator inputs', async () => {
    renderComponent();

    const studioTab = screen.getByRole('tab', { name: /Cover Letter Studio/i });
    fireEvent.click(studioTab);

    await waitFor(() => {
      expect(screen.getByText('Letter Parameters')).toBeInTheDocument();
      expect(screen.getByText('Generate Grounded Cover Letter')).toBeInTheDocument();
      expect(screen.getByLabelText(/Target Role Title/i)).toBeInTheDocument();
    });
  });

  it('switches to My Letters tab and lists generated cover letters', async () => {
    renderComponent();

    const myLettersTab = screen.getByRole('tab', { name: /My Letters/i });
    fireEvent.click(myLettersTab);

    await waitFor(() => {
      expect(screen.getByText('Senior Software Engineer Cover Letter - Stripe')).toBeInTheDocument();
      expect(screen.getByText('Approved')).toBeInTheDocument();
    });
  });

  it('switches to Screening Q&A tab and renders parsed questions with verified answers', async () => {
    renderComponent();

    const screeningTab = screen.getByRole('tab', { name: /Screening Q&A/i });
    fireEvent.click(screeningTab);

    await waitFor(() => {
      expect(screen.getAllByText('Stripe Engineering Screening')[0]).toBeInTheDocument();
      expect(screen.getByText('How many years of experience do you have with Python?')).toBeInTheDocument();
      expect(screen.getByText('6 years of verifiable Python engineering experience.')).toBeInTheDocument();
      expect(screen.getByText(/Confidence: 95%/i)).toBeInTheDocument();
    });
  });

  it('switches to Answer Library tab and renders reusable parameterized templates', async () => {
    renderComponent();

    const libraryTab = screen.getByRole('tab', { name: /Answer Library/i });
    fireEvent.click(libraryTab);

    await waitFor(() => {
      expect(screen.getByText('Production Outage Handling (STAR)')).toBeInTheDocument();
      expect(screen.getByText(/During an outage at {employer}/i)).toBeInTheDocument();
      expect(screen.getByText('Fresh & Approved')).toBeInTheDocument();
    });
  });

  it('switches to Sensitive Decisions tab and verifies human election requirement', async () => {
    renderComponent();

    const sensitiveTab = screen.getByRole('tab', { name: /Sensitive Decisions/i });
    fireEvent.click(sensitiveTab);

    await waitFor(() => {
      expect(screen.getByText(/Strict Human Decision Guard/i)).toBeInTheDocument();
      expect(screen.getByText('Are you legally authorized to work in the United States?')).toBeInTheDocument();
      expect(screen.getByText('Sealed')).toBeInTheDocument();
    });
  });

  it('switches to Gaps & Conflicts tab and renders audit warnings', async () => {
    renderComponent();

    const gapsTab = screen.getByRole('tab', { name: /Gaps & Conflicts/i });
    fireEvent.click(gapsTab);

    await waitFor(() => {
      expect(screen.getByText('Factual Completeness & Contradiction Auditing')).toBeInTheDocument();
      expect(screen.getByText('Target Compensation Base')).toBeInTheDocument();
      expect(screen.getByText('Years of Experience Discrepancy')).toBeInTheDocument();
    });
  });

  it('switches to Application Packages tab and lists assembled submission package', async () => {
    renderComponent();

    const packagesTab = screen.getByRole('tab', { name: /Packages/i });
    fireEvent.click(packagesTab);

    await waitFor(() => {
      expect(screen.getByText('Application Submission Package Assembly')).toBeInTheDocument();
      expect(screen.getByText('Assemble Application Package')).toBeInTheDocument();
      expect(screen.getAllByText(/Senior Software Engineer at Stripe/i)[0]).toBeInTheDocument();
    });
  });
});
