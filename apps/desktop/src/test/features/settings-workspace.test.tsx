import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SettingsWorkspace } from '@/features/settings/SettingsWorkspace';
import { apiClient } from '@/lib/api-client';
import { mockAllSettings } from './settings-mock-data';

describe('SettingsWorkspace', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false, gcTime: 0 },
      },
    });

    vi.spyOn(apiClient, 'getAllSettings').mockResolvedValue(mockAllSettings);
    vi.spyOn(apiClient, 'updateSettingCategory').mockResolvedValue(mockAllSettings.general);
    vi.spyOn(apiClient, 'getCredentialStatus').mockResolvedValue([]);
    vi.spyOn(apiClient, 'getStorageStatus').mockResolvedValue({
      database_exists: true,
      database_size_bytes: 1048576,
      wal_size_bytes: 65536,
      shm_size_bytes: 32768,
      artifacts_size_bytes: 524288,
      backups_size_bytes: 2097152,
      total_backups_count: 2,
      disk_free_bytes: 50000000000,
      disk_total_bytes: 500000000000,
      latest_backup: null,
    });
    vi.spyOn(apiClient, 'getStorageHealth').mockResolvedValue({
      integrity_check_passed: true,
      integrity_details: ['ok'],
      foreign_keys_passed: true,
      foreign_key_violations: [],
    });
    vi.spyOn(apiClient, 'listBackups').mockResolvedValue([]);
  });

  const renderWithProviders = (initialRoute = '/settings/general') => {
    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[initialRoute]}>
          <SettingsWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );
  };

  it('renders Settings header and navigation category list', async () => {
    renderWithProviders('/settings/general');

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: /Settings & Operational Controls/i })
      ).toBeInTheDocument();
      expect(screen.getByRole('heading', { level: 2, name: /General/i })).toBeInTheDocument();
    });

    // Check all categories are rendered in navigation
    expect(screen.getByRole('button', { name: /General/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Appearance/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /AI Providers & Models/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Agent Preferences/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Automation & Tasks/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Permissions & Autonomy/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Computer Control/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Connected Services & MCP/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Recruitment Preferences/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Storage & Data/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Notifications/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Desktop & Startup/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Security & Privacy/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Diagnostics & Health/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /About & Updates/i })).toBeInTheDocument();
  });

  it('switches categories when clicking navigation items', async () => {
    renderWithProviders('/settings/general');

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 2, name: /General/i })).toBeInTheDocument();
    });

    // Click Appearance
    fireEvent.click(screen.getByRole('button', { name: /Appearance/i }));
    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 2, name: /Appearance/i })).toBeInTheDocument();
      expect(screen.getByText('Visual Color Theme')).toBeInTheDocument();
    });

    // Click AI Providers
    fireEvent.click(screen.getByRole('button', { name: /AI Providers & Models/i }));
    await waitFor(() => {
      expect(
        screen.getByRole('heading', { level: 2, name: /AI Providers & Models/i })
      ).toBeInTheDocument();
      expect(screen.getByText(/Planned — Stage 11/i)).toBeInTheDocument();
    });
  });

  it('detects dirty state on edits and reveals Save bar', async () => {
    renderWithProviders('/settings/general');

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 2, name: /General/i })).toBeInTheDocument();
    });

    // Initially save bar is not visible
    expect(screen.queryByText('You have unsaved changes.')).not.toBeInTheDocument();

    // Change language select
    const langSelect = screen.getByLabelText('Application Language');
    fireEvent.change(langSelect, { target: { value: 'de-DE' } });

    // Save bar appears with dirty indicator
    await waitFor(() => {
      expect(screen.getByText('You have unsaved changes.')).toBeInTheDocument();
    });

    // Discard changes
    const discardBtn = screen.getByRole('button', { name: /Discard Changes/i });
    fireEvent.click(discardBtn);

    // Save bar hides
    await waitFor(() => {
      expect(screen.queryByText('You have unsaved changes.')).not.toBeInTheDocument();
    });
  });

  it('saves changes when clicking Save Preferences', async () => {
    renderWithProviders('/settings/general');

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 2, name: /General/i })).toBeInTheDocument();
    });

    const timeFormatSelect = screen.getByLabelText('Clock Display Format');
    fireEvent.change(timeFormatSelect, { target: { value: '12h' } });

    await waitFor(() => {
      expect(screen.getByText('You have unsaved changes.')).toBeInTheDocument();
    });

    const saveBtn = screen.getByRole('button', { name: /Save Preferences/i });
    fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(apiClient.updateSettingCategory).toHaveBeenCalledWith(
        'general',
        expect.objectContaining({ time_format: '12h' })
      );
    });
  });

  it('filters category navigation using search input', async () => {
    renderWithProviders('/settings/general');

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search settings...')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search settings...');
    fireEvent.change(searchInput, { target: { value: 'Desktop' } });

    expect(screen.getByRole('button', { name: /Desktop & Startup/i })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /^General$/i })).not.toBeInTheDocument();
  });
});
