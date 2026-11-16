import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
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
  it('renders AUTONOM branding and command center', () => {
    render(<App />);
    expect(screen.getAllByText(/AUTONOM/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText('Command Center').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Stage 06 Active')).toBeInTheDocument();
  });

  it('renders navigation sidebar items including Design System', () => {
    render(<App />);
    expect(screen.getByText('Diagnostics & Tasks')).toBeInTheDocument();
    expect(screen.getByText('Desktop Shell')).toBeInTheDocument();
    expect(screen.getByText('Storage & Database')).toBeInTheDocument();
    expect(screen.getByText('Design System')).toBeInTheDocument();
    expect(screen.getByText('Jobs & Applications')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('navigates to Design System showcase when clicked', () => {
    render(<App />);
    const designSystemNav = screen.getByText('Design System');
    fireEvent.click(designSystemNav);
    expect(screen.getByText(/UI\/UX Design System/)).toBeInTheDocument();
  });
});
