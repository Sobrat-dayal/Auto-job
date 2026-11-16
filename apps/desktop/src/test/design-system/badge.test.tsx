import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge } from '@/components/ui/badge';

describe('Badge Component', () => {
  it('renders with default variant and children', () => {
    render(<Badge>Default Badge</Badge>);
    const badge = screen.getByText('Default Badge');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('bg-surface-elevated');
  });

  it('renders status variants with appropriate colors', () => {
    const { rerender } = render(<Badge variant="success">Online</Badge>);
    expect(screen.getByText('Online')).toHaveClass('text-status-success');

    rerender(<Badge variant="warning">Pending</Badge>);
    expect(screen.getByText('Pending')).toHaveClass('text-status-warning');

    rerender(<Badge variant="error">Failed</Badge>);
    expect(screen.getByText('Failed')).toHaveClass('text-status-error');

    rerender(<Badge variant="cyan">Queued</Badge>);
    expect(screen.getByText('Queued')).toHaveClass('text-cyan');
  });

  it('renders dot indicator and pulse animation', () => {
    const { container } = render(
      <Badge variant="success" dot pulse>
        Live Pulse
      </Badge>
    );
    const dot = container.querySelector('.rounded-full.shrink-0');
    expect(dot).toBeInTheDocument();
    expect(dot).toHaveClass('animate-pulse');
  });

  it('renders different sizes', () => {
    const { rerender } = render(<Badge size="sm">Small</Badge>);
    expect(screen.getByText('Small')).toHaveClass('text-[10px]');

    rerender(<Badge size="md">Medium</Badge>);
    expect(screen.getByText('Medium')).toHaveClass('text-xs');
  });
});
