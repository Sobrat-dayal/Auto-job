import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { DashboardKpiGrid } from '@/features/dashboard/DashboardKpiGrid';
import type { DashboardOverviewResponse } from '@/types/dashboard';

const mockOverview: DashboardOverviewResponse = {
  system_status: 'operational',
  uptime_seconds: 120,
  backend_connected: true,
  task_dispatch_status: 'active',
  ai_swarm_status: 'scheduled_stage_12',
  tasks_summary: {
    total: 10,
    running: 2,
    queued: 1,
    completed: 6,
    failed: 1,
    cancelled: 0,
  },
  recruitment: {
    jobs_discovered: 0,
    jobs_discovered_today: 0,
    active_listings: 0,
    applications_total: 0,
    applications_submitted: 0,
    pipeline_stages: {
      discovered: 0,
      evaluated: 0,
      matched: 0,
      queued: 0,
      preparing: 0,
      submitted: 0,
      recruiter_response: 0,
      interview: 0,
      offer: 0,
      rejected: 0,
    },
    automated_scouting_enabled: false,
    automated_scouting_message: 'Stage 26 Scheduled',
  },
  agents: [],
  workers: {
    active: 0,
    total: 4,
    idle: 4,
    max_capacity: 4,
  },
  pending_actions_count: 1,
  timestamp: new Date().toISOString(),
};

describe('DashboardKpiGrid Component', () => {
  it('renders loading skeleton when loading without data', () => {
    const { container } = render(<DashboardKpiGrid isLoading={true} isConnected={true} />);
    expect(container.querySelectorAll('.animate-pulse').length).toBeGreaterThan(0);
  });

  it('renders primary KPI cards with honest values and stage attribution', () => {
    render(<DashboardKpiGrid overview={mockOverview} isLoading={false} isConnected={true} />);

    // Primary KPI titles
    expect(screen.getByText('Running Tasks')).toBeInTheDocument();
    expect(screen.getByText('Queued Tasks')).toBeInTheDocument();
    expect(screen.getByText('Jobs Discovered')).toBeInTheDocument();
    expect(screen.getByText('Applications Submitted')).toBeInTheDocument();

    // Values from mockOverview
    expect(screen.getByText('2')).toBeInTheDocument(); // running
    expect(screen.getAllByText('1').length).toBeGreaterThanOrEqual(1); // queued / failed
    expect(screen.getAllByText('0').length).toBeGreaterThanOrEqual(2); // jobs & applications

    // Roadmap attribution badges
    expect(screen.getByText('Stage 26')).toBeInTheDocument();
    expect(screen.getByText('Stage 31')).toBeInTheDocument();
  });

  it('renders secondary operational metrics', () => {
    render(<DashboardKpiGrid overview={mockOverview} isLoading={false} isConnected={true} />);

    expect(screen.getByText('Completed Tasks')).toBeInTheDocument();
    expect(screen.getByText('6')).toBeInTheDocument();

    expect(screen.getByText('Failed Tasks')).toBeInTheDocument();

    expect(screen.getByText('Pending Approvals')).toBeInTheDocument();
    expect(screen.getByText('Stage 14')).toBeInTheDocument();

    expect(screen.getByText('Worker Threads')).toBeInTheDocument();
  });

  it('invokes task filter callback when clicking on task cards', () => {
    const onSelectFilter = vi.fn();
    render(
      <DashboardKpiGrid
        overview={mockOverview}
        isLoading={false}
        isConnected={true}
        onSelectTaskFilter={onSelectFilter}
      />
    );

    fireEvent.click(screen.getByText('Running Tasks'));
    expect(onSelectFilter).toHaveBeenCalledWith('running');

    fireEvent.click(screen.getByText('Queued Tasks'));
    expect(onSelectFilter).toHaveBeenCalledWith('queued');
  });
});
