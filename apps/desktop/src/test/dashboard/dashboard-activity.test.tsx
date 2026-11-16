import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TooltipProvider } from '@/components/ui/tooltip';
import { ActivityFeed } from '@/features/dashboard/ActivityFeed';
import type { EventEnvelope } from '@autonom/shared-types';

const mockEvents: EventEnvelope[] = [
  {
    event_id: 'ev-1',
    event_type: 'task.completed',
    timestamp: '2026-11-16T12:00:00Z',
    payload: { task_id: 'task-1', task_type: 'test.sleep_progress' },
  },
  {
    event_id: 'ev-2',
    event_type: 'worker.started',
    timestamp: '2026-11-16T12:01:00Z',
    payload: { worker_id: 'worker-1', task_id: 'task-2' },
  },
  {
    event_id: 'ev-3',
    event_type: 'system.health',
    timestamp: '2026-11-16T12:02:00Z',
    payload: { status: 'ok', uptime: 120 },
  },
];

describe('ActivityFeed Component', () => {
  it('renders live activity feed events with stream status pill', () => {
    render(
      <TooltipProvider>
        <ActivityFeed events={mockEvents} streamStatus="connected" />
      </TooltipProvider>
    );

    expect(screen.getByText('Real-Time Event Stream')).toBeInTheDocument();
    expect(screen.getByText('LIVE SSE (8765)')).toBeInTheDocument();

    expect(screen.getByText('task.completed')).toBeInTheDocument();
    expect(screen.getByText('worker.started')).toBeInTheDocument();
    expect(screen.getByText('system.health')).toBeInTheDocument();
  });

  it('filters events by category tabs', () => {
    render(
      <TooltipProvider>
        <ActivityFeed events={mockEvents} streamStatus="connected" />
      </TooltipProvider>
    );

    // Filter by tasks
    fireEvent.click(screen.getByText('tasks'));
    expect(screen.getByText('task.completed')).toBeInTheDocument();
    expect(screen.queryByText('worker.started')).not.toBeInTheDocument();
    expect(screen.queryByText('system.health')).not.toBeInTheDocument();

    // Filter by workers
    fireEvent.click(screen.getByText('workers'));
    expect(screen.getByText('worker.started')).toBeInTheDocument();
    expect(screen.queryByText('task.completed')).not.toBeInTheDocument();

    // Filter by system
    fireEvent.click(screen.getByText('system'));
    expect(screen.getByText('system.health')).toBeInTheDocument();
  });

  it('invokes clear callback when clear button clicked', () => {
    const onClear = vi.fn();
    render(
      <TooltipProvider>
        <ActivityFeed events={mockEvents} streamStatus="connected" onClear={onClear} />
      </TooltipProvider>
    );

    const clearButton = screen.getByTitle('Clear Activity Feed');
    fireEvent.click(clearButton);
    expect(onClear).toHaveBeenCalled();
  });
});
