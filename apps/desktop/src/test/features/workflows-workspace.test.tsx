import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { WorkflowsWorkspace } from '@/features/workflows/WorkflowsWorkspace';
import { apiClient } from '@/lib/api-client';

describe('WorkflowsWorkspace', () => {
  beforeEach(() => {
    vi.spyOn(apiClient, 'listWorkflows').mockResolvedValue([
      {
        id: 'wf_test_123',
        title: 'Autonomous Job Requirement Analysis',
        goal: 'Analyze supplied job description, extract technical skills, summarize responsibilities',
        status: 'running',
        priority: 'high',
        total_steps: 4,
        completed_steps: 2,
        failed_steps: 0,
        total_cost_usd: 0.002,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ]);

    vi.spyOn(apiClient, 'getOrchestrationStats').mockResolvedValue({
      total_workflows: 5,
      completed_workflows: 3,
      running_workflows: 1,
      paused_workflows: 1,
      failed_workflows: 0,
      completion_rate_percent: 60.0,
    });

    vi.spyOn(apiClient, 'getWorkflow').mockResolvedValue({
      id: 'wf_test_123',
      title: 'Autonomous Job Requirement Analysis',
      goal: 'Analyze supplied job description, extract technical skills, summarize responsibilities',
      status: 'running',
      priority: 'high',
      active_plan_id: 'plan_abc',
      active_plan: {
        workflow_id: 'wf_test_123',
        version: 1,
        goal: 'Analyze supplied job description',
        steps: [],
        success_criteria: ['All steps complete'],
        max_duration_seconds: 300,
        max_total_steps: 4,
        max_parallel_steps: 4,
      },
      steps: [
        {
          id: 's1',
          workflow_id: 'wf_test_123',
          plan_id: 'plan_abc',
          step_id: 'step_extract',
          title: 'Extract Skills & Requirements',
          description: 'Extract technical proficiencies',
          capability_id: 'structured_extract',
          assigned_agent_id: 'capability_worker',
          status: 'completed',
          dependencies: [],
          input_bindings: {},
          output_result: {
            extracted_data: { technical_skills: ['Python', 'Rust'] },
          },
          error_info: null,
          verification_status: 'pass',
          retry_count: 0,
          max_retries: 2,
          timeout_seconds: 60,
          started_at: new Date().toISOString(),
          completed_at: new Date().toISOString(),
          created_at: new Date().toISOString(),
        },
      ],
      context: {},
      constraints: {},
      total_steps: 4,
      completed_steps: 2,
      failed_steps: 0,
      total_cost_usd: 0.002,
      total_tokens: 450,
      error_message: null,
      created_at: new Date().toISOString(),
      started_at: new Date().toISOString(),
      completed_at: null,
      updated_at: new Date().toISOString(),
    });

    vi.spyOn(apiClient, 'getWorkflowDag').mockResolvedValue({
      steps: [
        {
          step_id: 'step_extract',
          title: 'Extract Skills & Requirements',
          capability_id: 'structured_extract',
          dependencies: [],
        },
      ],
      topological_order: ['step_extract'],
      stages: [['step_extract']],
    });

    vi.spyOn(apiClient, 'createWorkflow').mockResolvedValue({
      id: 'wf_new_999',
      title: 'New Planned Goal',
      goal: 'Custom Goal Statement',
      status: 'plan_ready',
      priority: 'high',
      active_plan_id: 'plan_new',
      active_plan: null,
      steps: [],
      context: {},
      constraints: {},
      total_steps: 2,
      completed_steps: 0,
      failed_steps: 0,
      total_cost_usd: 0,
      total_tokens: 0,
      error_message: null,
      created_at: new Date().toISOString(),
      started_at: null,
      completed_at: null,
      updated_at: new Date().toISOString(),
    });

    vi.spyOn(apiClient, 'startWorkflow').mockResolvedValue({} as any);
    vi.spyOn(apiClient, 'pauseWorkflow').mockResolvedValue({} as any);
  });

  it('renders workflows, statistics badge, and interactive DAG', async () => {
    render(
      <MemoryRouter initialEntries={['/workflows/all']}>
        <WorkflowsWorkspace />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Workflows Workspace');
    expect(screen.getByText('Stage 12 Multi-Agent Orchestrator')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getAllByText('Autonomous Job Requirement Analysis').length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('Stage 0')).toBeInTheDocument();
      expect(screen.getByText('Extract Skills & Requirements')).toBeInTheDocument();
    });
  });

  it('submits a new goal directive via builder tab', async () => {
    render(
      <MemoryRouter initialEntries={['/workflows/all']}>
        <WorkflowsWorkspace />
      </MemoryRouter>
    );

    const newGoalBtn = screen.getByRole('button', { name: /new goal/i });
    fireEvent.click(newGoalBtn);

    await waitFor(() => {
      expect(screen.getByText('Define Autonomous Goal')).toBeInTheDocument();
    });

    const runBtn = screen.getByRole('button', { name: /plan & run autonomous workflow/i });
    fireEvent.click(runBtn);

    await waitFor(() => {
      expect(apiClient.createWorkflow).toHaveBeenCalled();
      expect(apiClient.startWorkflow).toHaveBeenCalled();
    });
  });
});
