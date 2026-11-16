import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { WorkflowsWorkspace } from '@/features/workflows/WorkflowsWorkspace';
import { apiClient } from '@/lib/api-client';

describe('WorkflowsWorkspace', () => {
  beforeEach(() => {
    vi.spyOn(apiClient, 'listTasks').mockResolvedValue({
      tasks: [
        {
          task_id: 'task-abc-123',
          task_type: 'system_health_check',
          state: 'running',
          priority: 'high',
          progress: 0.65,
          message: 'Verifying SQLite database integrity...',
          created_at: new Date().toISOString(),
        },
      ],
      total: 1,
    });

    vi.spyOn(apiClient, 'createTask').mockResolvedValue({
      task_id: 'task-new-456',
      task_type: 'system_health_check',
      state: 'queued',
      priority: 'high',
      progress: 0.0,
      created_at: new Date().toISOString(),
    });
  });

  it('renders tasks and dispatches diagnostic task', async () => {
    render(
      <MemoryRouter initialEntries={['/workflows/all']}>
        <WorkflowsWorkspace />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      'Workflows & Task Orchestration'
    );

    await waitFor(() => {
      expect(screen.getByText('system_health_check')).toBeInTheDocument();
      expect(screen.getByText('Running')).toBeInTheDocument();
      expect(screen.getByText('65%')).toBeInTheDocument();
    });

    const dispatchBtn = screen.getByRole('button', { name: /dispatch diagnostic task/i });
    fireEvent.click(dispatchBtn);

    await waitFor(() => {
      expect(apiClient.createTask).toHaveBeenCalled();
    });
  });
});
