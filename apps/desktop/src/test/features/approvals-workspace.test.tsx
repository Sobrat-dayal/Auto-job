import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { ApprovalsWorkspace } from '@/features/security/ApprovalsWorkspace';
import { apiClient } from '@/lib/api-client';

describe('ApprovalsWorkspace (Stage 14)', () => {
  beforeEach(() => {
    vi.spyOn(apiClient, 'listApprovals').mockResolvedValue([
      {
        id: 'appr_test_1',
        capability_id: 'recruitment_submit_application',
        action: 'recruitment_submit_application',
        agent_id: 'application_agent',
        workflow_id: 'wf_recruitment_101',
        step_id: 'step_submit',
        parameters_digest: 'a1b2c3d4e5f678901234567890abcdef',
        parameters_payload: { job_id: 'job_senior_dev', portal: 'greenhouse' },
        resource_type: 'workflow',
        risk_level: 'high',
        reason: 'Requires user confirmation before sending live application',
        approval_mode: 'one_time',
        status: 'pending',
        requested_at: new Date().toISOString(),
        expires_at: new Date(Date.now() + 3600000).toISOString(),
      },
    ]);

    vi.spyOn(apiClient, 'listPolicies').mockResolvedValue([
      {
        id: 'pol_external_submission_approval',
        name: 'External Job Application Submission Gate',
        description: 'Requires explicit human approval before submitting live job applications.',
        version: 1,
        is_enabled: true,
        is_system: true,
        subject_scope: '*',
        category_scope: 'recruitment',
        action_scope: ['recruitment_submit_application'],
        resource_scope: { unrestricted: true },
        effect: 'require_approval',
        conditions: { max_risk_level: 'critical' },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ]);

    vi.spyOn(apiClient, 'listGrants').mockResolvedValue([
      {
        id: 'grant_auto_skills',
        name: 'Standing Skill Matching Grant',
        description: 'Allows continuous skill parsing',
        grant_type: 'standing',
        subject_id: 'recruitment_agent',
        allowed_categories: ['recruitment'],
        allowed_capabilities: ['recruitment_match_skills'],
        resource_scope: { unrestricted: true },
        max_uses: 100,
        use_count: 12,
        granted_by: 'user',
        granted_at: new Date().toISOString(),
        is_active: true,
        is_revoked: false,
      },
    ]);

    vi.spyOn(apiClient, 'listSecurityAuditLogs').mockResolvedValue([
      {
        id: 'aud_1',
        actor_id: 'recruitment_agent',
        actor_type: 'agent',
        capability_id: 'recruitment_match_skills',
        action: 'recruitment_match_skills',
        parameters_digest: 'fedcba9876543210',
        outcome: 'allow',
        reason_code: 'READ_ONLY_BASELINE',
        risk_level: 'low',
        explanation: 'Operation permitted under low-risk read-only system baseline',
        timestamp: new Date().toISOString(),
      },
    ]);

    vi.spyOn(apiClient, 'getEmergencyStopStatus').mockResolvedValue({
      is_active: false,
      is_paused: false,
      active_operations_aborted: 0,
      pending_approvals_frozen: 0,
    });
  });

  it('renders pending approval requests with risk badge and details', async () => {
    render(
      <MemoryRouter>
        <ApprovalsWorkspace />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Authorization & Approvals Engine')).toBeInTheDocument();
      expect(screen.getByText('recruitment_submit_application')).toBeInTheDocument();
      expect(screen.getByText(/Requires user confirmation before sending live application/i)).toBeInTheDocument();
      expect(screen.getByText('High Risk')).toBeInTheDocument();
    });
  });

  it('triggers approveRequest when user clicks Approve (One-Time)', async () => {
    const approveSpy = vi.spyOn(apiClient, 'approveRequest').mockResolvedValue({
      id: 'appr_test_1',
      capability_id: 'recruitment_submit_application',
      action: 'recruitment_submit_application',
      parameters_digest: 'a1b2c3d4e5f678901234567890abcdef',
      parameters_payload: {},
      resource_type: 'workflow',
      risk_level: 'high',
      reason: 'Approved',
      approval_mode: 'one_time',
      status: 'approved',
      requested_at: new Date().toISOString(),
      expires_at: new Date().toISOString(),
      decided_at: new Date().toISOString(),
      decided_by: 'user',
    });

    render(
      <MemoryRouter>
        <ApprovalsWorkspace />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('recruitment_submit_application')).toBeInTheDocument();
    });

    const approveBtn = screen.getByText('Approve (One-Time)');
    fireEvent.click(approveBtn);

    await waitFor(() => {
      expect(approveSpy).toHaveBeenCalledWith('appr_test_1', expect.objectContaining({
        approval_mode: 'one_time',
      }));
    });
  });

  it('triggers denyRequest when user clicks Deny', async () => {
    const denySpy = vi.spyOn(apiClient, 'denyRequest').mockResolvedValue({
      id: 'appr_test_1',
      capability_id: 'recruitment_submit_application',
      action: 'recruitment_submit_application',
      parameters_digest: 'a1b2c3d4e5f678901234567890abcdef',
      parameters_payload: {},
      resource_type: 'workflow',
      risk_level: 'high',
      reason: 'Denied',
      approval_mode: 'one_time',
      status: 'denied',
      requested_at: new Date().toISOString(),
      expires_at: new Date().toISOString(),
    });

    render(
      <MemoryRouter>
        <ApprovalsWorkspace />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('recruitment_submit_application')).toBeInTheDocument();
    });

    const denyBtn = screen.getByText('Deny');
    fireEvent.click(denyBtn);

    await waitFor(() => {
      expect(denySpy).toHaveBeenCalledWith('appr_test_1', expect.objectContaining({
        reason: expect.any(String),
      }));
    });
  });

  it('switches to Security Policies tab and displays system baseline', async () => {
    render(
      <MemoryRouter>
        <ApprovalsWorkspace />
      </MemoryRouter>
    );

    const tab = await screen.findByRole('tab', { name: /Security Policies/i });
    expect(tab).toBeInTheDocument();
    fireEvent.click(tab);

    await waitFor(() => {
      expect(screen.getByText('External Job Application Submission Gate')).toBeInTheDocument();
      expect(screen.getByText('System Baseline')).toBeInTheDocument();
    });
  });

  it('switches to Standing Grants tab and displays active grants', async () => {
    render(
      <MemoryRouter>
        <ApprovalsWorkspace />
      </MemoryRouter>
    );

    const tab = await screen.findByRole('tab', { name: /Standing Grants/i });
    expect(tab).toBeInTheDocument();
    fireEvent.click(tab);

    await waitFor(() => {
      expect(screen.getByText('Standing Skill Matching Grant')).toBeInTheDocument();
      expect(screen.getByText(/Usage:/i)).toBeInTheDocument();
    });
  });

  it('opens and triggers Emergency Stop confirmation modal', async () => {
    const emergencySpy = vi.spyOn(apiClient, 'activateEmergencyStop').mockResolvedValue({
      is_active: true,
      is_paused: false,
      reason: 'Testing stop',
      active_operations_aborted: 1,
      pending_approvals_frozen: 1,
    });

    render(
      <MemoryRouter>
        <ApprovalsWorkspace />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Emergency Stop/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /Emergency Stop/i }));

    await waitFor(() => {
      expect(screen.getByText('Trigger Global Emergency Stop?')).toBeInTheDocument();
    });

    const confirmBtn = screen.getByText('ENGAGE EMERGENCY STOP');
    fireEvent.click(confirmBtn);

    await waitFor(() => {
      expect(emergencySpy).toHaveBeenCalled();
    });
  });
});
