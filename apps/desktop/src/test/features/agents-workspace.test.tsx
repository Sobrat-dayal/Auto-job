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
    expect(screen.getByText('Stage 12 Active')).toBeInTheDocument();
    expect(screen.getByText(/Stage 12 Operational/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(
        screen.getByText('Active Local Worker Pool (Stage 03 Foundation)')
      ).toBeInTheDocument();
      expect(screen.getByText('2 / 4 Active')).toBeInTheDocument();
      expect(screen.getByText('Supervisor Agent')).toBeInTheDocument();
      expect(screen.getByText('Planning Agent')).toBeInTheDocument();
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
      expect(screen.getByText('Supervisor Agent')).toBeInTheDocument();
    });

    const searchInput = screen.getByRole('searchbox');
    fireEvent.change(searchInput, { target: { value: 'Visual Grounding' } });

    expect(screen.getByText('Visual Grounding Agent')).toBeInTheDocument();
    expect(screen.queryByText('Supervisor Agent')).not.toBeInTheDocument();
  });

  it('opens detail inspector when clicking an agent card', async () => {
    render(
      <MemoryRouter initialEntries={['/agents/all']}>
        <AgentsWorkspace />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Supervisor Agent')).toBeInTheDocument();
    });

    const agentCard = screen.getByText('Supervisor Agent');
    fireEvent.click(agentCard);

    await waitFor(() => {
      expect(screen.getByRole('complementary', { name: /detail inspector/i })).toBeInTheDocument();
      expect(screen.getByText('Workflow Coordinator & Governance Master')).toBeInTheDocument();
      expect(screen.getByText('Target AI Model')).toBeInTheDocument();
    });
  });

  it('switches to Configuration tab and allows editing preferences', async () => {
    vi.spyOn(apiClient, 'getAgentConfiguration').mockResolvedValue({
      preferred_model: 'Unified AI Gateway / Router',
      concurrency_limit: 4,
      timeout_seconds: 120,
      temperature: 0.1,
    });
    vi.spyOn(apiClient, 'updateAgentConfiguration').mockResolvedValue({} as any);

    render(
      <MemoryRouter initialEntries={['/agents/all']}>
        <AgentsWorkspace />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Supervisor Agent')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Supervisor Agent'));

    await waitFor(() => {
      expect(screen.getByText('Configuration')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Configuration'));

    expect(screen.getByText('Save Configuration')).toBeInTheDocument();
  });

  it('runs diagnostic self-test in Diagnostics tab', async () => {
    vi.spyOn(apiClient, 'testAgent').mockResolvedValue({
      passed: true,
      details: 'Diagnostic check for Supervisor Agent: manifest valid, 4 capabilities declared.',
      duration_ms: 12,
      tested_at: new Date().toISOString(),
    });

    render(
      <MemoryRouter initialEntries={['/agents/all']}>
        <AgentsWorkspace />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Supervisor Agent')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Supervisor Agent'));

    await waitFor(() => {
      expect(screen.getByText('Diagnostics')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Diagnostics'));

    const runBtn = screen.getByText('Run Diagnostic Check');
    fireEvent.click(runBtn);

    await waitFor(() => {
      expect(screen.getByText('PASS')).toBeInTheDocument();
      expect(screen.getAllByText(/manifest valid/i).length).toBeGreaterThanOrEqual(1);
    });
  });
});
