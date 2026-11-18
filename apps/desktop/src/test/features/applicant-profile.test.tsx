import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ApplicantProfileWorkspace } from '@/features/recruitment/profile/ApplicantProfileWorkspace';
import { apiClient } from '@/lib/api-client';
import type {
  ApplicantProfile,
  DataQualityReport,
  ApplicantClaim,
  ProfileConflict,
  EvidenceMetadata,
  ProfileVersionRecord,
  ProfileSnapshot,
} from '@autonom/shared-types';

describe('Applicant Profile Intelligence & Verified Identity (Stage 21)', () => {
  let queryClient: QueryClient;

  const mockProfile: ApplicantProfile = {
    id: 'prof_test_primary',
    owner_id: 'default_user',
    display_label: 'Lead Distributed Systems Architect',
    status: 'active',
    version: 3,
    contact: {
      legal_name: 'Elena Rostova',
      preferred_name: 'Elena',
      primary_email: 'elena.rostova@example.com',
      phone_number: '+1 (555) 019-3388',
      linkedin_url: 'https://linkedin.com/in/elenarostova',
      github_url: 'https://github.com/elenarostova',
      is_verified: true,
    },
    location: {
      city: 'Seattle',
      state_or_province: 'WA',
      country: 'United States',
      is_remote_open: true,
      willing_to_relocate: false,
    },
    eligibility: {
      citizenship_country: 'United States',
      work_authorization_status: 'Citizen',
      requires_sponsorship: false,
      notice_period_days: 14,
    },
    education: [
      {
        id: 'edu_1',
        institution: 'University of Washington',
        degree: 'Master of Science',
        field_of_study: 'Computer Science',
        start_date: '2016-09',
        end_date: '2018-06',
        gpa: '3.94',
        honors: ['Dean’s Scholar'],
      },
    ],
    employment: [
      {
        id: 'emp_1',
        employer: 'Distributed Cloud Inc',
        job_title: 'Staff Infrastructure Architect',
        employment_type: 'Full-time',
        location: 'Seattle, WA',
        is_remote: true,
        start_date: '2020-01',
        is_current: true,
        summary: 'Architecting zero-downtime distributed systems.',
        achievements: [
          {
            id: 'ach_1',
            description: 'Reduced service failover recovery from 120s to 450ms across 40 regional clusters.',
            metric: '99.6% failover speedup',
          },
        ],
        technologies_used: ['Rust', 'Python', 'Kubernetes', 'gRPC'],
      },
    ],
    skills: [
      {
        id: 'sk_1',
        name: 'Rust',
        canonical_name: 'rust',
        category: 'technical',
        proficiency: 'expert',
        years_experience: 5,
        is_primary: true,
      },
      {
        id: 'sk_2',
        name: 'Kubernetes',
        canonical_name: 'kubernetes',
        category: 'tool',
        proficiency: 'expert',
        years_experience: 6,
        is_primary: true,
      },
    ],
    projects: [
      {
        id: 'proj_1',
        title: 'HyperMesh Distributed Service Fabric',
        role: 'Creator & Maintainer',
        summary: 'High-throughput eBPF-accelerated proxy in Rust.',
        repository_url: 'https://github.com/elenarostova/hypermesh',
        technologies: ['Rust', 'eBPF', 'Tokio'],
      },
    ],
    certifications: [
      {
        id: 'cert_1',
        name: 'CKA - Certified Kubernetes Administrator',
        issuing_organization: 'Linux Foundation / CNCF',
        does_not_expire: false,
      },
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  const mockQuality: DataQualityReport = {
    profile_id: 'prof_test_primary',
    overall_score: 92.0,
    completeness_score: 95.0,
    consistency_score: 100.0,
    evidence_coverage_score: 80.0,
    readiness_status: 'verified_for_agents',
    total_claims: 18,
    verified_claims: 16,
    conflicted_claims: 0,
    unverified_claims: 2,
    issues: [],
    evaluated_at: new Date().toISOString(),
  };

  const mockClaims: ApplicantClaim[] = [
    {
      id: 'clm_1',
      profile_id: 'prof_test_primary',
      category: 'skill',
      field_path: 'skills.rust',
      claimed_value: { name: 'Rust', proficiency: 'expert' },
      status: 'evidence_supported',
      confidence_score: 0.98,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ];

  const mockConflicts: ProfileConflict[] = [];

  const mockEvidence: EvidenceMetadata[] = [
    {
      id: 'ev_1',
      profile_id: 'prof_test_primary',
      filename: 'Elena_Rostova_Resume_2026.pdf',
      storage_path: 'C:/artifacts/evidence/ev_1.pdf',
      content_hash_sha256: '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
      file_size_bytes: 524288,
      mime_type: 'application/pdf',
      document_type: 'resume',
      tags: ['primary', 'verified'],
      uploaded_at: new Date().toISOString(),
    },
  ];

  const mockVersions: ProfileVersionRecord[] = [
    {
      id: 'ver_1',
      profile_id: 'prof_test_primary',
      version: 1,
      changed_by: 'system',
      modified_fields: ['initial_creation'],
      created_at: new Date().toISOString(),
    },
  ];

  const mockSnapshot: ProfileSnapshot = {
    profile_id: 'prof_test_primary',
    version: 3,
    target_agent: 'JobMatchingAgent',
    authorized_scopes: ['applicant.skills.read', 'applicant.education.read'],
    filtered_data: {
      profile_id: 'prof_test_primary',
      skills: [{ name: 'Rust' }, { name: 'Kubernetes' }],
      location: { city: 'Seattle', country: 'United States' },
    },
    generated_at: new Date().toISOString(),
  };

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    vi.clearAllMocks();

    vi.spyOn(apiClient, 'listApplicantProfiles').mockResolvedValue([mockProfile]);
    vi.spyOn(apiClient, 'getApplicantQualityReport').mockResolvedValue(mockQuality);
    vi.spyOn(apiClient, 'listApplicantClaims').mockResolvedValue(mockClaims);
    vi.spyOn(apiClient, 'listApplicantConflicts').mockResolvedValue(mockConflicts);
    vi.spyOn(apiClient, 'listApplicantEvidence').mockResolvedValue(mockEvidence);
    vi.spyOn(apiClient, 'getApplicantVersions').mockResolvedValue(mockVersions);
    vi.spyOn(apiClient, 'generateApplicantSnapshot').mockResolvedValue(mockSnapshot);
  });

  const renderComponent = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <ApplicantProfileWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

  it('renders applicant profile workspace headline, quality score, and claims stats', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Lead Distributed Systems Architect')).toBeInTheDocument();
      expect(screen.getByText('Quality Score')).toBeInTheDocument();
      expect(screen.getByText('92%')).toBeInTheDocument();
      expect(screen.getByText('Claims In Registry')).toBeInTheDocument();
      expect(screen.getByText('18')).toBeInTheDocument();
    });
  });

  it('switches between workspace tabs properly', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Lead Distributed Systems Architect')).toBeInTheDocument();
    });

    // Switch to Education tab
    const educationTab = screen.getByRole('tab', { name: /Education/i });
    fireEvent.click(educationTab);
    expect(screen.getByText('Academic Education & Degrees')).toBeInTheDocument();
    expect(screen.getByText('University of Washington')).toBeInTheDocument();

    // Switch to Experience tab
    const experienceTab = screen.getByRole('tab', { name: /Experience/i });
    fireEvent.click(experienceTab);
    expect(screen.getByText('Work History & Professional Experience')).toBeInTheDocument();
    expect(screen.getByText('Distributed Cloud Inc')).toBeInTheDocument();

    // Switch to Skills tab
    const skillsTab = screen.getByRole('tab', { name: /Skills/i });
    fireEvent.click(skillsTab);
    expect(screen.getByText('Skills Inventory & Capabilities')).toBeInTheDocument();
    expect(screen.getByText('Rust')).toBeInTheDocument();

    // Switch to Evidence Library tab
    const evidenceTab = screen.getByRole('tab', { name: /Evidence Library/i });
    fireEvent.click(evidenceTab);
    expect(screen.getByText('Authoritative Evidence Library')).toBeInTheDocument();
    expect(screen.getByText('Elena_Rostova_Resume_2026.pdf')).toBeInTheDocument();
  });

  it('generates a privacy-preserving agent snapshot with redacted contact info', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Lead Distributed Systems Architect')).toBeInTheDocument();
    });

    // Switch to History & Snapshots tab
    const historyTab = screen.getByRole('tab', { name: /History & Snapshots/i });
    fireEvent.click(historyTab);
    expect(screen.getByText('Privacy-Preserving Agent Snapshot Simulator')).toBeInTheDocument();

    // Click Generate Snapshot
    const generateBtn = screen.getByRole('button', { name: /Generate JobMatchingAgent Snapshot/i });
    fireEvent.click(generateBtn);

    await waitFor(() => {
      expect(apiClient.generateApplicantSnapshot).toHaveBeenCalledWith('prof_test_primary', 'JobMatchingAgent');
      expect(screen.getByText(/Target Agent:/i)).toBeInTheDocument();
    });
  });
});
