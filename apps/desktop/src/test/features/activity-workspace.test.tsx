import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { ActivityWorkspace } from '@/features/activity/ActivityWorkspace';
import { apiClient } from '@/lib/api-client';

describe('ActivityWorkspace', () => {
  beforeEach(() => {
    vi.spyOn(apiClient, 'getDashboardActivity').mockResolvedValue([
      {
        id: 'evt-1',
        task_id: 'task-test-999',
        event_type: 'task_completed',
        timestamp: new Date().toISOString(),
        state_transition: 'running -> completed',
        metadata: { exit_code: 0 },
        correlation_id: 'corr-1',
      },
    ]);
  });

  it('renders genuine task activity logs', async () => {
    render(
      <MemoryRouter initialEntries={['/activity/timeline']}>
        <ActivityWorkspace />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      'Activity Stream & Audit Logs'
    );

    await waitFor(() => {
      expect(screen.getByText('task_completed')).toBeInTheDocument();
      expect(screen.getByText('running -> completed')).toBeInTheDocument();
      expect(screen.getByText(/Task: task-test-999/)).toBeInTheDocument();
    });
  });
});
