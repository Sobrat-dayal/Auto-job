import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../App';

// Mock Tauri native bridge
vi.mock('@/services/tauri', () => ({
  getNativeAppInfo: vi.fn().mockResolvedValue({
    name: 'AUTONOM (Test Mode)',
    version: '0.1.0-test',
    tauri_version: '2.0.0-test',
    os: 'Windows 11 (Test)',
    arch: 'x86_64',
  }),
}));

describe('App Component', () => {
  it('renders AUTONOM branding and command center', async () => {
    render(<App />);
    expect(screen.getAllByText(/AUTONOM/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText('Command Center').length).toBeGreaterThanOrEqual(1);
    await waitFor(() => {
      expect(screen.getByText('Stage 06 Active')).toBeInTheDocument();
    });
  });

  it('renders navigation sidebar items including Design System', () => {
    render(<App />);
    expect(screen.getByText('Diagnostics & Tasks')).toBeInTheDocument();
    expect(screen.getByText('Desktop Shell')).toBeInTheDocument();
    expect(screen.getByText('Storage & Database')).toBeInTheDocument();
    expect(screen.getByText('Design System')).toBeInTheDocument();
    expect(screen.getByText('Jobs & Applications')).toBeInTheDocument();
    expect(screen.getAllByText('Settings').length).toBeGreaterThanOrEqual(1);
  });

  it('navigates to Design System showcase when clicked', async () => {
    render(<App />);
    const designSystemNav = screen.getByText('Design System');
    fireEvent.click(designSystemNav);
    await waitFor(() => {
      expect(screen.getByText(/UI\/UX Design System/)).toBeInTheDocument();
    });
  });
});
