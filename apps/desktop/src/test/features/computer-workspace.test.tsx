import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { ComputerWorkspace } from '@/features/computer/ComputerWorkspace';

describe('ComputerWorkspace', () => {
  it('renders dual-modality computer interaction status and safety boundaries', () => {
    render(
      <MemoryRouter initialEntries={['/computer/live']}>
        <ComputerWorkspace />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      'Computer Control & Automation'
    );
    expect(screen.getByText('Stage 19 Production Active')).toBeInTheDocument();
    expect(screen.getByText(/Killswitch: Pause \/ Break/i)).toBeInTheDocument();
    expect(screen.getByText('Global Panic Killswitch')).toBeInTheDocument();
    expect(screen.getByText('Dual-Modality Arbitration')).toBeInTheDocument();
  });
});
