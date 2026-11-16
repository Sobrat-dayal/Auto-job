import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Input } from '@/components/ui/input';

describe('Input Component', () => {
  it('renders standard text input with placeholder', () => {
    render(<Input placeholder="Search jobs..." />);
    const input = screen.getByPlaceholderText('Search jobs...');
    expect(input).toBeInTheDocument();
    expect(input).toHaveClass('bg-surface-secondary');
  });

  it('renders left and right icons', () => {
    render(
      <Input
        placeholder="Icon test"
        leftIcon={<span data-testid="left-icon">L</span>}
        rightIcon={<span data-testid="right-icon">R</span>}
      />
    );
    expect(screen.getByTestId('left-icon')).toBeInTheDocument();
    expect(screen.getByTestId('right-icon')).toBeInTheDocument();
  });

  it('handles error state and accessibility attributes', () => {
    render(<Input placeholder="Error input" hasError />);
    const input = screen.getByPlaceholderText('Error input');
    expect(input).toHaveAttribute('aria-invalid', 'true');
    expect(input).toHaveClass('border-status-error');
  });

  it('captures user input and fires onChange', () => {
    const handleChange = vi.fn();
    render(<Input placeholder="Type here" onChange={handleChange} />);
    const input = screen.getByPlaceholderText('Type here');
    fireEvent.change(input, { target: { value: 'Autonomous Agent' } });
    expect(handleChange).toHaveBeenCalled();
    expect((input as HTMLInputElement).value).toBe('Autonomous Agent');
  });

  it('handles disabled state', () => {
    render(<Input placeholder="Disabled" disabled />);
    const input = screen.getByPlaceholderText('Disabled');
    expect(input).toBeDisabled();
    expect(input).toHaveClass('disabled:opacity-50');
  });
});
