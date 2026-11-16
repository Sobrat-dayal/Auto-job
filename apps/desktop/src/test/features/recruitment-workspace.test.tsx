import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { RecruitmentWorkspace } from '@/features/recruitment/RecruitmentWorkspace';
import { apiClient } from '@/lib/api-client';

describe('RecruitmentWorkspace', () => {
  beforeEach(() => {
    vi.spyOn(apiClient, 'listJobs').mockResolvedValue({
      items: [
        {
          id: 'job-1',
          source_id: 'src-1',
          external_id: 'gh-101',
          company: 'Acme Robotics',
          title: 'Staff Systems Architect',
          location: 'Remote',
          employment_type: 'Full-time',
          work_arrangement: 'remote',
          salary_range: '$200k - $250k',
          description: 'Autonomous systems architect role.',
          requirements: 'Rust, TypeScript, Python',
          application_url: 'https://acme.example.com/apply/101',
          discovered_at: new Date().toISOString(),
          last_verified_at: null,
          status: 'active',
        },
      ],
      total: 1,
      limit: 50,
      offset: 0,
    });

    vi.spyOn(apiClient, 'listApplications').mockResolvedValue({
      items: [],
      total: 0,
      limit: 50,
      offset: 0,
    });
  });

  it('renders header, roadmap attribution, and genuine job listings', async () => {
    render(
      <MemoryRouter initialEntries={['/recruitment/discovery']}>
        <RecruitmentWorkspace />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      'Jobs & Application Pipeline'
    );
    expect(screen.getByText('Scheduled for Stage 26 & 31')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Staff Systems Architect')).toBeInTheDocument();
      expect(screen.getByText('Acme Robotics')).toBeInTheDocument();
      expect(screen.getByText('$200k - $250k')).toBeInTheDocument();
    });
  });

  it('opens job detail inspector when clicking a listing', async () => {
    render(
      <MemoryRouter initialEntries={['/recruitment/discovery']}>
        <RecruitmentWorkspace />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Staff Systems Architect')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Staff Systems Architect'));

    await waitFor(() => {
      expect(screen.getByRole('complementary', { name: /detail inspector/i })).toBeInTheDocument();
      expect(screen.getByText('Salary Compensation')).toBeInTheDocument();
      expect(screen.getByText('Autonomous systems architect role.')).toBeInTheDocument();
    });
  });
});
