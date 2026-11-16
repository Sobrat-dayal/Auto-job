import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, useDensity } from '@/design-system/ThemeContext';

const TestDensityConsumer = () => {
  const { density, toggleDensity, setDensity } = useDensity();
  return (
    <div>
      <span data-testid="density-value">{density}</span>
      <button onClick={toggleDensity}>Toggle</button>
      <button onClick={() => setDensity('compact')}>Set Compact</button>
      <button onClick={() => setDensity('comfortable')}>Set Comfortable</button>
    </div>
  );
};

describe('ThemeContext & Density', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute('data-density');
  });

  it('provides default comfortable density mode', () => {
    render(
      <ThemeProvider>
        <TestDensityConsumer />
      </ThemeProvider>
    );

    expect(screen.getByTestId('density-value')).toHaveTextContent('comfortable');
    expect(document.documentElement.getAttribute('data-density')).toBe('comfortable');
  });

  it('toggles density mode between comfortable and compact', () => {
    render(
      <ThemeProvider>
        <TestDensityConsumer />
      </ThemeProvider>
    );

    const toggleBtn = screen.getByRole('button', { name: 'Toggle' });

    // Toggle to compact
    fireEvent.click(toggleBtn);
    expect(screen.getByTestId('density-value')).toHaveTextContent('compact');
    expect(document.documentElement.getAttribute('data-density')).toBe('compact');
    expect(localStorage.getItem('autonom_density')).toBe('compact');

    // Toggle back to comfortable
    fireEvent.click(toggleBtn);
    expect(screen.getByTestId('density-value')).toHaveTextContent('comfortable');
    expect(document.documentElement.getAttribute('data-density')).toBe('comfortable');
    expect(localStorage.getItem('autonom_density')).toBe('comfortable');
  });

  it('directly sets density via setDensity', () => {
    render(
      <ThemeProvider>
        <TestDensityConsumer />
      </ThemeProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Set Compact' }));
    expect(screen.getByTestId('density-value')).toHaveTextContent('compact');

    fireEvent.click(screen.getByRole('button', { name: 'Set Comfortable' }));
    expect(screen.getByTestId('density-value')).toHaveTextContent('comfortable');
  });
});
