import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ResumePortfolioWorkspace } from '@/features/recruitment/resume/ResumePortfolioWorkspace';
import { apiClient } from '@/lib/api-client';
import type {
  ResumeDocument,
  ResumeOverviewStats,
  ResumeTemplateDefinition,
  ATSReadabilityReport,
  ExportArtifact,
  PortfolioDocument,
} from '@autonom/shared-types';

describe('Resume Intelligence Engine & Portfolio Builder (Stage 23)', () => {
  let queryClient: QueryClient;

  const mockStats: ResumeOverviewStats = {
    total_resumes: 3,
    draft_count: 2,
    approved_count: 1,
    master_resume_id: 'res_master_01',
    master_resume_title: 'Master Professional Resume',
    recent_resumes: [
      {
        id: 'res_master_01',
        title: 'Master Professional Resume',
        type: 'master',
        status: 'approved',
        updated_at: '2026-11-18T12:00:00Z',
      },
      {
        id: 'res_backend_02',
        title: 'Senior Backend Engineer Tailored',
        type: 'job_tailored',
        status: 'draft',
        updated_at: '2026-11-18T14:30:00Z',
      },
    ],
  };

  const mockResumes: ResumeDocument[] = [
    {
      id: 'res_master_01',
      owner_id: 'user_01',
      profile_id: 'prof_01',
      profile_snapshot_id: 'snap_01',
      title: 'Master Professional Resume',
      resume_type: 'master',
      target_role: 'Senior Software Engineer',
      job_ref: null,
      template_id: 'ats_classic',
      template_version: '1.0.0',
      status: 'approved',
      current_version: 1,
      locale: 'en_US',
      page_format: 'letter',
      max_pages: 1,
      header_contact: {
        full_name: 'Alex Mercer',
        email: 'alex.mercer@example.com',
        phone: '+1 (555) 019-2834',
        location: 'San Francisco, CA',
        github_url: 'https://github.com/alexmercer',
      },
      sections: [
        {
          id: 'sec_summary',
          section_type: 'summary',
          display_title: 'Professional Summary',
          ordering: 0,
          is_visible: true,
          source_references: [],
          validation_state: 'valid',
          entries: [
            {
              id: 'ent_sum_01',
              entry_type: 'summary',
              title: 'Summary',
              subtitle: null,
              organization: null,
              location: null,
              start_date: null,
              end_date: null,
              is_current: false,
              description: 'Senior Software Engineer with 6+ years building distributed cloud systems in Python and Rust.',
              bullet_points: [],
              tags: ['Python', 'Rust', 'Distributed Systems'],
              source_refs: [],
              metrics: {},
              is_visible: true,
              ordering: 0,
            },
          ],
        },
        {
          id: 'sec_experience',
          section_type: 'experience',
          display_title: 'Experience',
          ordering: 1,
          is_visible: true,
          source_references: [],
          validation_state: 'valid',
          entries: [
            {
              id: 'ent_exp_01',
              entry_type: 'experience',
              title: 'Senior Backend Engineer',
              subtitle: 'Core Platform',
              organization: 'CloudScale Inc.',
              location: 'San Francisco, CA',
              start_date: '2022-01-01',
              end_date: null,
              is_current: true,
              description: null,
              bullet_points: [
                'Architected high-throughput event processing pipeline handling 100k events/sec using FastAPI and Kafka.',
                'Reduced p99 query latency by 42% through PostgreSQL query index optimization and Redis caching layer.',
              ],
              tags: ['Python', 'FastAPI', 'PostgreSQL', 'Kafka'],
              source_refs: [],
              metrics: {},
              is_visible: true,
              ordering: 0,
            },
          ],
        },
      ],
      created_at: '2026-11-18T10:00:00Z',
      updated_at: '2026-11-18T12:00:00Z',
      approved_at: '2026-11-18T12:00:00Z',
    },
  ];

  const mockTemplates: ResumeTemplateDefinition[] = [
    {
      id: 'ats_classic',
      name: 'Classic ATS Single-Column',
      description: 'Maximum machine readability with single-column layout, standard sans fonts, and clear headings.',
      category: 'ats_classic',
      version: '1.0.0',
      supported_page_formats: ['letter', 'a4'],
      supported_sections: ['summary', 'experience', 'education', 'skills', 'projects'],
      primary_font: 'Helvetica',
      heading_font: 'Helvetica-Bold',
      base_font_size_pt: 10,
      heading_font_size_pt: 12,
      title_font_size_pt: 18,
      margin_top_in: 0.75,
      margin_bottom_in: 0.75,
      margin_left_in: 0.75,
      margin_right_in: 0.75,
      primary_color: '#1a1a1a',
      accent_color: '#2563eb',
      has_header_border: true,
      is_two_column: false,
      ats_friendly: true,
    },
    {
      id: 'technical_engineer',
      name: 'Technical Engineer',
      description: 'Optimized for software engineers and systems architects emphasizing GitHub projects and technical stack.',
      category: 'technical_engineer',
      version: '1.0.0',
      supported_page_formats: ['letter', 'a4'],
      supported_sections: ['summary', 'skills', 'experience', 'projects', 'education'],
      primary_font: 'Helvetica',
      heading_font: 'Helvetica-Bold',
      base_font_size_pt: 9.5,
      heading_font_size_pt: 11.5,
      title_font_size_pt: 16,
      margin_top_in: 0.6,
      margin_bottom_in: 0.6,
      margin_left_in: 0.6,
      margin_right_in: 0.6,
      primary_color: '#0f172a',
      accent_color: '#0891b2',
      has_header_border: true,
      is_two_column: false,
      ats_friendly: true,
    },
  ];

  const mockATSReport: ATSReadabilityReport = {
    overall_status: 'pass',
    passed_count: 7,
    warning_count: 0,
    error_count: 0,
    checks: [
      {
        check_name: 'Machine Readable Text',
        status: 'pass',
        observed_evidence: 'Document contains full standard Unicode text stream.',
        impact_explanation: 'ATS parsers can extract all text without OCR.',
        suggested_remediation: null,
      },
      {
        check_name: 'Standard Section Headings',
        status: 'pass',
        observed_evidence: 'Standard headings found: Experience, Summary.',
        impact_explanation: 'Sections correctly categorized by ATS engines.',
        suggested_remediation: null,
      },
    ],
    evaluated_at: '2026-11-18T12:00:00Z',
    document_id: 'res_master_01',
    format: 'ats_classic',
    notes: 'Document satisfies all ATS structural standards.',
  };

  const mockExports: ExportArtifact[] = [
    {
      export_id: 'exp_01',
      resume_id: 'res_master_01',
      version_id: 'ver_01',
      format: 'pdf',
      filename: 'Alex_Mercer_Resume.pdf',
      file_path: 'C:\\Users\\Sobrat Dayal\\.gemini\\antigravity\\brain\\exports\\Alex_Mercer_Resume.pdf',
      file_size_bytes: 45200,
      sha256_checksum: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      created_at: '2026-11-18T12:05:00Z',
      status: 'valid',
      validation_result: { text_length: 1200, is_selectable: true },
    },
  ];

  const mockPortfolios: PortfolioDocument[] = [
    {
      id: 'port_01',
      owner_id: 'user_01',
      profile_id: 'prof_01',
      title: 'Full Stack Engineering Portfolio',
      professional_intro: 'Lead Architect with proven track record in distributed streaming systems.',
      selected_skills: ['Python', 'FastAPI', 'Rust', 'Docker', 'PostgreSQL'],
      selected_projects: [
        {
          project_id: 'proj_01',
          title: 'Distributed Event Bus',
          summary: 'High-throughput publish-subscribe messaging kernel.',
          problem_addressed: 'Scalability bottleneck during flash traffic spikes.',
          tech_stack: ['Python', 'Rust', 'Kafka'],
          architecture_highlights: ['Zero-copy buffering', 'Actor-based concurrency'],
          individual_contribution: 'Designed core storage engine and Raft consensus layer.',
          deliverables: ['Production microservice', 'Architecture RFC'],
          repo_url: 'https://github.com/alexmercer/event-bus',
          demo_url: null,
          screenshot_path: null,
          attribution_level: 'creator',
          is_public_eligible: true,
          ordering: 0,
        },
      ],
      publications: [],
      certifications: [],
      public_contact: { email: 'alex@example.com' },
      template_id: 'portfolio_classic',
      created_at: '2026-11-18T10:00:00Z',
      updated_at: '2026-11-18T12:00:00Z',
      status: 'approved',
    },
  ];

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });

    vi.spyOn(apiClient, 'getResumesOverview').mockResolvedValue(mockStats);
    vi.spyOn(apiClient, 'listResumes').mockResolvedValue(mockResumes);
    vi.spyOn(apiClient, 'getResume').mockResolvedValue(mockResumes[0]);
    vi.spyOn(apiClient, 'listResumeTemplates').mockResolvedValue(mockTemplates);
    vi.spyOn(apiClient, 'getResumeATSReport').mockResolvedValue(mockATSReport);
    vi.spyOn(apiClient, 'getResumeValidation').mockResolvedValue({
      resume_id: 'res_master_01',
      issue_count: 0,
      issues: [],
      is_valid: true,
    });
    vi.spyOn(apiClient, 'getResumePreview').mockResolvedValue({
      resume_id: 'res_master_01',
      html: '<div class="resume-sheet"><h1>Alex Mercer</h1><p>Senior Software Engineer</p></div>',
    });
    vi.spyOn(apiClient, 'listResumeVersions').mockResolvedValue([
      {
        id: 'ver_01',
        resume_id: 'res_master_01',
        version_number: 1,
        content_hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        changelog: 'Initial approved master version',
        template_id: 'ats_classic',
        template_version: '1.0.0',
        profile_snapshot_id: 'snap_01',
        document_snapshot: mockResumes[0],
        actor_id: 'user',
        is_published: true,
        export_artifact_ids: [],
        created_at: '2026-11-18T12:00:00Z',
      },
    ]);
    vi.spyOn(apiClient, 'listResumeExports').mockResolvedValue(mockExports);
    vi.spyOn(apiClient, 'listPortfolios').mockResolvedValue(mockPortfolios);
  });

  it('renders Resume Intelligence workspace header and overview stats', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <ResumePortfolioWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(
      screen.getByText('Resume Intelligence Engine & Portfolio Builder')
    ).toBeInTheDocument();
    expect(screen.getByText('Stage 23 of 50')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Approved Versions')).toBeInTheDocument();
    });
  });

  it('navigates to My Resumes tab and displays document list', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <ResumePortfolioWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

    const resumesTab = screen.getByText(/My Resumes/i);
    fireEvent.click(resumesTab);

    await waitFor(() => {
      expect(screen.getAllByText('Master Professional Resume').length).toBeGreaterThan(0);
      expect(screen.getByText('master')).toBeInTheDocument();
    });
  });

  it('switches to Builder Wizard and shows creation form', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <ResumePortfolioWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

    const builderTab = screen.getByText('Builder Wizard');
    fireEvent.click(builderTab);

    expect(screen.getByText('Resume Title')).toBeInTheDocument();
    expect(screen.getByText('Resume Archetype')).toBeInTheDocument();
    expect(screen.getByText('Build Resume')).toBeInTheDocument();
  });

  it('switches to Job Tailoring and shows requirement match matrix with zero hallucination guarantee', async () => {
    vi.spyOn(apiClient, 'analyzeJobDescription').mockResolvedValue({
      id: 'job_01',
      owner_id: 'user_01',
      job_title: 'Backend Software Engineer',
      employer: 'TechCorp',
      raw_text: 'Requires Python and FastAPI',
      required_skills: ['Python', 'FastAPI'],
      preferred_skills: ['AWS'],
      experience_reqs: ['3+ years'],
      education_reqs: [],
      responsibilities: [],
      tech_stack: ['Python', 'FastAPI'],
      location: null,
      work_arrangement: null,
      source_url: null,
      extracted_at: '2026-11-18T12:00:00Z',
    });

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <ResumePortfolioWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

    const tailoringTab = screen.getByText('Job Tailoring');
    fireEvent.click(tailoringTab);

    expect(screen.getByText('Job Description Input')).toBeInTheDocument();
    expect(screen.getByText('Zero-Hallucination Tailoring Guarantee')).toBeInTheDocument();
  });

  it('switches to Templates tab and displays the standard templates', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <ResumePortfolioWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

    const templatesTab = screen.getByText(/Templates/i);
    fireEvent.click(templatesTab);

    await waitFor(() => {
      expect(screen.getByText('Classic ATS Single-Column')).toBeInTheDocument();
      expect(screen.getByText('Technical Engineer')).toBeInTheDocument();
    });
  });

  it('switches to ATS Readability tab and displays inspectable checks', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <ResumePortfolioWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Active: Master Professional Resume/i)).toBeInTheDocument();
    });

    const atsTab = screen.getByText('ATS Readability');
    fireEvent.click(atsTab);

    await waitFor(() => {
      expect(screen.getByText('Inspectable ATS Properties Checklist')).toBeInTheDocument();
      expect(screen.getByText('Machine Readable Text')).toBeInTheDocument();
      expect(screen.getByText('Standard Section Headings')).toBeInTheDocument();
    });
  });

  it('switches to Export Manager tab and shows artifacts ledger', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <ResumePortfolioWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Active: Master Professional Resume/i)).toBeInTheDocument();
    });

    const exportsTab = screen.getByText('Export Manager');
    fireEvent.click(exportsTab);

    await waitFor(() => {
      expect(screen.getByText('Document Export & Cryptographic Verification')).toBeInTheDocument();
      expect(screen.getByText('Alex_Mercer_Resume.pdf')).toBeInTheDocument();
      expect(screen.getByText('Compile & Verify PDF')).toBeInTheDocument();
      expect(screen.getByText('Compile & Verify DOCX')).toBeInTheDocument();
    });
  });

  it('switches to Portfolio Builder tab and shows privacy review controls', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <ResumePortfolioWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

    const portfolioTab = screen.getByText('Portfolio Builder');
    fireEvent.click(portfolioTab);

    await waitFor(() => {
      expect(screen.getByText('Professional Portfolios')).toBeInTheDocument();
      expect(screen.getByText('Privacy Review & Intellectual Property Safeguards')).toBeInTheDocument();
      expect(screen.getByText('Export Multi-Page PDF')).toBeInTheDocument();
      expect(screen.getByText('Export Standalone HTML')).toBeInTheDocument();
    });
  });
});
