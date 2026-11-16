import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
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
    expect(screen.getByText('Stage 02 Active')).toBeInTheDocument();
  });

  it('renders navigation sidebar items including Diagnostics, Desktop Shell, and Storage', () => {
    render(<App />);
    expect(screen.getByText('Diagnostics & Tasks')).toBeInTheDocument();
    expect(screen.getByText('Desktop Shell')).toBeInTheDocument();
    expect(screen.getByText('Storage & Database')).toBeInTheDocument();
    expect(screen.getByText('Jobs & Applications')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });
});
