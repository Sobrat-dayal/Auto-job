import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { AgentsWorkspace } from '@/features/agents/AgentsWorkspace';
import { apiClient } from '@/lib/api-client';

describe('AgentsWorkspace', () => {
  beforeEach(() => {
    vi.spyOn(apiClient, 'getWorkers').mockResolvedValue({
      total_workers: 4,
      active_workers: 2,
      idle_workers: 2,
      max_capacity: 4,
      workers: [],
    });
    vi.spyOn(apiClient, 'listTasks').mockResolvedValue({
      tasks: [],
      total: 0,
    });
  });

  it('renders header, worker pool stats, and cataloged agents', async () => {
    render(
      <MemoryRouter initialEntries={['/agents/all']}>
        <AgentsWorkspace />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Autonomous Agent Swarm');
    expect(screen.getByText('Stage 12 Planned')).toBeInTheDocument();
    expect(screen.getByText('Scheduled for Stage 12')).toBeInTheDocument();

    await waitFor(() => {
      expect(
        screen.getByText('Active Local Worker Pool (Stage 03 Foundation)')
      ).toBeInTheDocument();
      expect(screen.getByText('2 / 4 Active')).toBeInTheDocument();
      expect(screen.getByText('Supervisor Swarm Coordinator')).toBeInTheDocument();
      expect(screen.getByText('Job Discovery Scout')).toBeInTheDocument();
      expect(screen.getByText('Visual Grounding Agent')).toBeInTheDocument();
    });
  });

  it('filters agents by search term', async () => {
    render(
      <MemoryRouter initialEntries={['/agents/all']}>
        <AgentsWorkspace />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Supervisor Swarm Coordinator')).toBeInTheDocument();
    });

    const searchInput = screen.getByRole('searchbox');
    fireEvent.change(searchInput, { target: { value: 'Visual Grounding' } });

    expect(screen.getByText('Visual Grounding Agent')).toBeInTheDocument();
    expect(screen.queryByText('Supervisor Swarm Coordinator')).not.toBeInTheDocument();
  });

  it('opens detail inspector when clicking an agent card', async () => {
    render(
      <MemoryRouter initialEntries={['/agents/all']}>
        <AgentsWorkspace />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Supervisor Swarm Coordinator')).toBeInTheDocument();
    });

    const agentCard = screen.getByText('Supervisor Swarm Coordinator');
    fireEvent.click(agentCard);

    await waitFor(() => {
      expect(screen.getByRole('complementary', { name: /detail inspector/i })).toBeInTheDocument();
      expect(screen.getByText('Multi-Agent Orchestrator & Safety Gate')).toBeInTheDocument();
      expect(screen.getByText('Target AI Model')).toBeInTheDocument();
    });
  });
});
