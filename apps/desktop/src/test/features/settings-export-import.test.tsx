import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SettingsWorkspace } from '@/features/settings/SettingsWorkspace';
import { apiClient } from '@/lib/api-client';
import { mockAllSettings } from './settings-mock-data';

describe('Settings Export & Import Integration', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false, gcTime: 0 },
      },
    });

    vi.spyOn(apiClient, 'getAllSettings').mockResolvedValue(mockAllSettings);
    vi.spyOn(apiClient, 'exportSettings').mockResolvedValue({
      app_version: '0.1.0-dev',
      exported_at: '2026-11-16T20:00:00Z',
      schema_version: 1,
      settings: { general: mockAllSettings.general },
    });
    vi.spyOn(apiClient, 'importSettings').mockResolvedValue({
      success: true,
      imported_categories: ['general'],
      total_categories: 1,
    });
    vi.spyOn(apiClient, 'resetSettingCategory').mockResolvedValue(mockAllSettings.general);
  });

  const renderWorkspace = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/settings/general']}>
          <SettingsWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );
  };

  it('triggers export settings download', async () => {
    renderWorkspace();

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Export/i })).toBeInTheDocument();
    });

    // Mock createObjectURL & revokeObjectURL & link click
    const createObjectUrlMock = vi.fn().mockReturnValue('blob:mock-url');
    const revokeObjectUrlMock = vi.fn();
    const clickMock = vi.fn();
    global.URL.createObjectURL = createObjectUrlMock;
    global.URL.revokeObjectURL = revokeObjectUrlMock;
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(clickMock);

    fireEvent.click(screen.getByRole('button', { name: /Export/i }));

    await waitFor(() => {
      expect(apiClient.exportSettings).toHaveBeenCalled();
      expect(createObjectUrlMock).toHaveBeenCalled();
      expect(clickMock).toHaveBeenCalled();
    });
  });

  it('opens import modal, validates JSON, and triggers import', async () => {
    renderWorkspace();

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Import/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /Import/i }));

    await waitFor(() => {
      expect(screen.getByText('Import Configuration JSON')).toBeInTheDocument();
    });

    const textarea = screen.getByPlaceholderText(/Paste exported JSON/i);
    const validJson = JSON.stringify({
      schema_version: 1,
      settings: { general: { app_language: 'en-US' } },
    });

    fireEvent.change(textarea, { target: { value: validJson } });

    const validateBtn = screen.getByRole('button', { name: /Validate & Import/i });
    fireEvent.click(validateBtn);

    await waitFor(() => {
      expect(apiClient.importSettings).toHaveBeenCalledWith(JSON.parse(validJson));
      expect(screen.getByText(/Imported 1 categories successfully/i)).toBeInTheDocument();
    });
  });

  it('handles reset all settings with confirmation modal', async () => {
    renderWorkspace();

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Reset Defaults/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /Reset Defaults/i }));

    await waitFor(() => {
      expect(screen.getByText('Reset All Settings to Defaults')).toBeInTheDocument();
    });

    const confirmBtn = screen.getByRole('button', { name: 'Reset All to Defaults' });
    fireEvent.click(confirmBtn);

    await waitFor(() => {
      expect(apiClient.resetSettingCategory).toHaveBeenCalledWith('all');
    });
  });
});
