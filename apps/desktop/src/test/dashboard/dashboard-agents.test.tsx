import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TooltipProvider } from '@/components/ui/tooltip';
import { AgentOperationsPanel } from '@/features/dashboard/AgentOperationsPanel';
import type { AgentOperationStatus } from '@/types/dashboard';

const mockAgents: AgentOperationStatus[] = [
  {
    id: 'agent-discovery',
    name: 'Job Discovery Agent',
    role: 'Scouting & Feed Scraping',
    status: 'unavailable',
    target_stage: 'Stage 26',
    is_available: false,
    successful_tasks: 0,
    failed_tasks: 0,
    message: 'Autonomous job scraping scheduled for activation in Stage 26.',
  },
  {
    id: 'agent-tailor',
    name: 'Application Tailor Agent',
    role: 'Resume Customization',
    status: 'unavailable',
    target_stage: 'Stage 30',
    is_available: false,
    successful_tasks: 0,
    failed_tasks: 0,
    message: 'Resume & cover letter generator scheduled for Stage 30.',
  },
  {
    id: 'agent-swarm-lead',
    name: 'Supervisor Swarm Lead',
    role: 'Workflow Orchestration',
    status: 'unavailable',
    target_stage: 'Stage 12',
    is_available: false,
    successful_tasks: 0,
    failed_tasks: 0,
    message: 'Multi-agent supervisor swarm orchestrator scheduled for Stage 12.',
  },
];

describe('AgentOperationsPanel Component', () => {
  it('renders 3 prominent agent cards with honest roadmap release badges', () => {
    render(
      <TooltipProvider>
        <AgentOperationsPanel
          agents={mockAgents}
          workers={{ active: 0, total: 4, idle: 4, max_capacity: 4 }}
          isConnected={true}
        />
      </TooltipProvider>
    );

    expect(screen.getByText('Job Discovery Agent')).toBeInTheDocument();
    expect(screen.getByText('Application Tailor Agent')).toBeInTheDocument();
    expect(screen.getByText('Supervisor Swarm Lead')).toBeInTheDocument();

    // Target Stage badges
    expect(screen.getByText('UNAVAILABLE (Stage 26)')).toBeInTheDocument();
    expect(screen.getByText('UNAVAILABLE (Stage 30)')).toBeInTheDocument();
    expect(screen.getByText('UNAVAILABLE (Stage 12)')).toBeInTheDocument();
  });

  it('renders the 4th distinct card for real background worker threads', () => {
    render(
      <TooltipProvider>
        <AgentOperationsPanel
          agents={mockAgents}
          workers={{ active: 2, total: 4, idle: 2, max_capacity: 4 }}
          isConnected={true}
        />
      </TooltipProvider>
    );

    expect(screen.getByText('Worker Thread Pool')).toBeInTheDocument();
    expect(screen.getByText('2 active / 4 total')).toBeInTheDocument();
    expect(screen.getByText('Stage 03 Background Executor')).toBeInTheDocument();
    expect(screen.getByText('ONLINE')).toBeInTheDocument();
  });

  it('triggers inspect agent callback when clicking info button', () => {
    const onInspect = vi.fn();
    render(
      <TooltipProvider>
        <AgentOperationsPanel
          agents={mockAgents}
          workers={{ active: 0, total: 4, idle: 4, max_capacity: 4 }}
          isConnected={true}
          onInspectAgent={onInspect}
        />
      </TooltipProvider>
    );

    const infoButtons = screen.getAllByRole('button', { name: /Info/i });
    expect(infoButtons.length).toBe(3);
    fireEvent.click(infoButtons[0]);
    expect(onInspect).toHaveBeenCalledWith('agent-discovery');
  });
});
