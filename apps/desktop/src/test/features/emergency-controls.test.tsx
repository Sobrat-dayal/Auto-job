import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { TooltipProvider } from '@/components/ui/tooltip';
import { DashboardHeader } from '@/features/dashboard/DashboardHeader';
import { PendingActionsPanel } from '@/features/dashboard/PendingActionsPanel';
import { apiClient } from '@/lib/api-client';

describe('Emergency Controls & Pending Actions (Stage 14)', () => {
  beforeEach(() => {
    vi.spyOn(apiClient, 'getEmergencyStopStatus').mockResolvedValue({
      is_active: false,
      is_paused: false,
      active_operations_aborted: 0,
      pending_approvals_frozen: 0,
    });

    vi.spyOn(apiClient, 'listApprovals').mockResolvedValue([
      {
        id: 'appr_critical_delete',
        capability_id: 'fs_delete_directory',
        action: 'fs_delete_directory',
        agent_id: 'coding_agent',
        workflow_id: 'wf_clean_1',
        step_id: 'step_del',
        parameters_digest: 'digest1234567890abcdef',
        parameters_payload: { path: '/tmp/old_builds' },
        resource_type: 'filesystem',
        risk_level: 'critical',
        reason: 'Requires operator confirmation to delete directory',
        approval_mode: 'one_time',
        status: 'pending',
        requested_at: new Date().toISOString(),
        expires_at: new Date(Date.now() + 3600000).toISOString(),
      },
    ]);
  });

  it('renders Emergency Stop button in DashboardHeader and toggles stop state', async () => {
    const activateSpy = vi.spyOn(apiClient, 'activateEmergencyStop').mockResolvedValue({
      is_active: true,
      is_paused: false,
      reason: 'Operator manual stop from Command Center',
      active_operations_aborted: 1,
      pending_approvals_frozen: 1,
    });

    render(
      <MemoryRouter>
        <TooltipProvider>
          <DashboardHeader
            isLoading={false}
            isFetching={false}
            isConnected={true}
            onRefresh={() => {}}
          />
        </TooltipProvider>
      </MemoryRouter>
    );

    const stopBtn = await screen.findByRole('button', { name: /Emergency Stop/i });
    expect(stopBtn).toBeInTheDocument();

    fireEvent.click(stopBtn);

    await waitFor(() => {
      expect(activateSpy).toHaveBeenCalledWith('Operator manual stop from Command Center');
    });
  });

  it('renders Pause button in DashboardHeader and toggles automation pause', async () => {
    const pauseSpy = vi.spyOn(apiClient, 'pauseAutomation').mockResolvedValue({
      is_active: false,
      is_paused: true,
      reason: 'Operator pause from Command Center',
      active_operations_aborted: 0,
      pending_approvals_frozen: 0,
    });

    render(
      <MemoryRouter>
        <TooltipProvider>
          <DashboardHeader
            isLoading={false}
            isFetching={false}
            isConnected={true}
            onRefresh={() => {}}
          />
        </TooltipProvider>
      </MemoryRouter>
    );

    const pauseBtn = await screen.findByRole('button', { name: /Pause/i });
    expect(pauseBtn).toBeInTheDocument();

    fireEvent.click(pauseBtn);

    await waitFor(() => {
      expect(pauseSpy).toHaveBeenCalledWith('Operator pause from Command Center');
    });
  });

  it('renders pending approval requests in PendingActionsPanel with review link', async () => {
    render(
      <MemoryRouter>
        <PendingActionsPanel failedTasks={[]} />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Action Items & Authorization Gates')).toBeInTheDocument();
      expect(screen.getByText(/fs_delete_directory/i)).toBeInTheDocument();
      expect(screen.getByText(/critical/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Review Approvals/i })).toBeInTheDocument();
    });
  });
});
