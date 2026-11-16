import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { TooltipProvider } from '@/components/ui/tooltip';
import { LiveTaskQueue } from '@/features/dashboard/LiveTaskQueue';
import { apiClient } from '@/lib/api-client';
import type { TaskResponse } from '@autonom/shared-types';

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    cancelTask: vi.fn().mockResolvedValue({ task_id: 'task-1', state: 'cancelled' }),
    getTaskHistory: vi.fn().mockResolvedValue([]),
  },
}));

const mockTasks: TaskResponse[] = [
  {
    task_id: 'task-1',
    task_type: 'test.sleep_progress',
    state: 'running',
    priority: 'normal',
    progress: 50,
    created_at: '2026-11-16T12:00:00Z',
    started_at: '2026-11-16T12:00:01Z',
    completed_at: null,
    error: null,
  },
  {
    task_id: 'task-2',
    task_type: 'system.health_check',
    state: 'queued',
    priority: 'high',
    progress: 0,
    created_at: '2026-11-16T12:01:00Z',
    started_at: null,
    completed_at: null,
    error: null,
  },
  {
    task_id: 'task-3',
    task_type: 'data.backup',
    state: 'completed',
    priority: 'low',
    progress: 100,
    created_at: '2026-11-16T11:50:00Z',
    started_at: '2026-11-16T11:50:01Z',
    completed_at: '2026-11-16T11:50:04Z',
    error: null,
  },
  {
    task_id: 'task-4',
    task_type: 'scout.job_crawl',
    state: 'failed',
    priority: 'normal',
    progress: 25,
    created_at: '2026-11-16T11:45:00Z',
    started_at: '2026-11-16T11:45:01Z',
    completed_at: '2026-11-16T11:45:03Z',
    error: 'Connection timed out to remote gateway',
  },
];

describe('LiveTaskQueue Component', () => {
  it('renders task queue table with all tasks and filter counts', () => {
    render(
      <TooltipProvider>
        <LiveTaskQueue tasks={mockTasks} isLoading={false} onRefresh={vi.fn()} />
      </TooltipProvider>
    );

    expect(screen.getByText('Live Background Task Queue')).toBeInTheDocument();
    expect(screen.getByText('All Tasks')).toBeInTheDocument();
    expect(screen.getByText('Running')).toBeInTheDocument();
    expect(screen.getByText('Queued')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText('Failed')).toBeInTheDocument();

    expect(screen.getByText('test.sleep_progress')).toBeInTheDocument();
    expect(screen.getByText('system.health_check')).toBeInTheDocument();
    expect(screen.getByText('data.backup')).toBeInTheDocument();
    expect(screen.getByText('scout.job_crawl')).toBeInTheDocument();
  });

  it('filters tasks when selecting a state tab', () => {
    const onFilterChange = vi.fn();
    const { rerender } = render(
      <TooltipProvider>
        <LiveTaskQueue
          tasks={mockTasks}
          isLoading={false}
          onRefresh={vi.fn()}
          activeFilter="all"
          onFilterChange={onFilterChange}
        />
      </TooltipProvider>
    );

    // Click 'Running' tab button
    fireEvent.click(screen.getByText('Running'));
    expect(onFilterChange).toHaveBeenCalledWith('running');

    // Rerender with activeFilter="running"
    rerender(
      <TooltipProvider>
        <LiveTaskQueue
          tasks={mockTasks}
          isLoading={false}
          onRefresh={vi.fn()}
          activeFilter="running"
          onFilterChange={onFilterChange}
        />
      </TooltipProvider>
    );

    expect(screen.getByText('test.sleep_progress')).toBeInTheDocument();
    expect(screen.queryByText('data.backup')).not.toBeInTheDocument();
    expect(screen.queryByText('scout.job_crawl')).not.toBeInTheDocument();
  });

  it('opens task details dialog when clicking inspect button', async () => {
    render(
      <TooltipProvider>
        <LiveTaskQueue tasks={mockTasks} isLoading={false} onRefresh={vi.fn()} />
      </TooltipProvider>
    );

    const inspectButtons = screen.getAllByTitle('Inspect Task Details');
    expect(inspectButtons.length).toBe(4);

    fireEvent.click(inspectButtons[0]);

    await waitFor(() => {
      expect(screen.getByText('Task Execution Details')).toBeInTheDocument();
      expect(screen.getByText('Task Identifier')).toBeInTheDocument();
      expect(screen.getByText('task-1')).toBeInTheDocument();
    });
  });

  it('allows cooperative cancellation for running or queued tasks', async () => {
    const onRefresh = vi.fn();
    render(
      <TooltipProvider>
        <LiveTaskQueue tasks={mockTasks} isLoading={false} onRefresh={onRefresh} />
      </TooltipProvider>
    );

    const cancelButtons = screen.getAllByTitle('Cancel Task');
    expect(cancelButtons.length).toBe(2); // for task-1 (running) and task-2 (queued)

    fireEvent.click(cancelButtons[0]);

    await waitFor(() => {
      expect(apiClient.cancelTask).toHaveBeenCalledWith('task-1');
      expect(onRefresh).toHaveBeenCalled();
    });
  });
});
