import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AutomationSettingsPage } from '@/features/settings/pages/AutomationSettingsPage';
import { RecruitmentSettingsPage } from '@/features/settings/pages/RecruitmentSettingsPage';
import { SecuritySettingsPage } from '@/features/settings/pages/SecuritySettingsPage';
import { NotificationSettingsPage } from '@/features/settings/pages/NotificationSettingsPage';
import { DesktopSettingsPage } from '@/features/settings/pages/DesktopSettingsPage';
import { apiClient } from '@/lib/api-client';
import * as tauriService from '@/services/tauri';
import { mockAllSettings } from './settings-mock-data';

describe('Settings Category Pages', () => {
  describe('AutomationSettingsPage', () => {
    it('renders worker bounds and triggers restart notice', () => {
      const onChange = vi.fn();
      const onSave = vi.fn();
      const onReset = vi.fn();

      render(
        <AutomationSettingsPage
          settings={mockAllSettings.automation}
          isDirty={false}
          isSaving={false}
          onChange={onChange}
          onSave={onSave}
          onReset={onReset}
        />
      );

      expect(
        screen.getByText('Background Worker Pool & Execution Concurrency')
      ).toBeInTheDocument();
      expect(screen.getByLabelText('Maximum Concurrent Workers')).toHaveValue(4);

      // Change worker concurrency
      const workerInput = screen.getByLabelText('Maximum Concurrent Workers');
      fireEvent.change(workerInput, { target: { value: '6' } });
      expect(onChange).toHaveBeenCalledWith({ max_concurrent_workers: 6 });
    });
  });

  describe('RecruitmentSettingsPage', () => {
    it('allows adding and removing desired job titles', () => {
      const onChange = vi.fn();
      render(
        <RecruitmentSettingsPage
          settings={mockAllSettings.recruitment}
          isDirty={false}
          isSaving={false}
          onChange={onChange}
          onSave={vi.fn()}
          onReset={vi.fn()}
        />
      );

      expect(screen.getByText('Software Engineer')).toBeInTheDocument();
      expect(screen.getByText('Backend Developer')).toBeInTheDocument();

      // Add new title
      const titleInput = screen.getByPlaceholderText(/Add job title/i);
      fireEvent.change(titleInput, { target: { value: 'AI Architect' } });
      fireEvent.click(screen.getByRole('button', { name: /^Add$/i }));

      expect(onChange).toHaveBeenCalledWith({
        desired_job_titles: ['Software Engineer', 'Backend Developer', 'AI Architect'],
      });

      // Remove title
      const removeBtn = screen.getByLabelText('Remove Software Engineer');
      fireEvent.click(removeBtn);

      expect(onChange).toHaveBeenCalledWith({
        desired_job_titles: ['Backend Developer'],
      });
    });
  });

  describe('SecuritySettingsPage', () => {
    beforeEach(() => {
      vi.spyOn(apiClient, 'getCredentialStatus').mockResolvedValue([
        {
          provider: 'anthropic',
          credential_type: 'api_key',
          status: 'active',
          is_configured: true,
          created_at: '2026-11-16T12:00:00Z',
        },
      ]);
      vi.spyOn(apiClient, 'storeCredential').mockResolvedValue({ success: true });
      vi.spyOn(apiClient, 'deleteCredential').mockResolvedValue({ deleted: true });
    });

    it('renders DPAPI vault metrics and lists stored credentials', async () => {
      render(
        <SecuritySettingsPage
          settings={mockAllSettings.security}
          isDirty={false}
          isSaving={false}
          onChange={vi.fn()}
          onSave={vi.fn()}
          onReset={vi.fn()}
        />
      );

      expect(screen.getByText('Windows DPAPI Keystore & Vault Health')).toBeInTheDocument();
      expect(screen.getByText('AES-256-GCM')).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.getByText(/anthropic/i)).toBeInTheDocument();
      });
    });

    it('opens store credential modal and encrypts secret', async () => {
      render(
        <SecuritySettingsPage
          settings={mockAllSettings.security}
          isDirty={false}
          isSaving={false}
          onChange={vi.fn()}
          onSave={vi.fn()}
          onReset={vi.fn()}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /Store Credential/i }));

      await waitFor(() => {
        expect(screen.getByText('Store Secret in Windows DPAPI Vault')).toBeInTheDocument();
      });

      const providerInput = screen.getByPlaceholderText(/e\.g\. openai/i);
      const secretInput = screen.getByPlaceholderText(/Paste API key/i);

      fireEvent.change(providerInput, { target: { value: 'openai' } });
      fireEvent.change(secretInput, { target: { value: 'sk-test123456789' } });

      fireEvent.click(screen.getByRole('button', { name: /Encrypt & Save/i }));

      await waitFor(() => {
        expect(apiClient.storeCredential).toHaveBeenCalledWith('openai', 'sk-test123456789');
      });
    });
  });

  describe('NotificationSettingsPage', () => {
    it('dispatches desktop notification test', async () => {
      const notifySpy = vi.spyOn(tauriService, 'testDesktopNotification').mockResolvedValue(true);

      render(
        <NotificationSettingsPage
          settings={mockAllSettings.notifications}
          isDirty={false}
          isSaving={false}
          onChange={vi.fn()}
          onSave={vi.fn()}
          onReset={vi.fn()}
        />
      );

      const testBtn = screen.getByRole('button', { name: /Send Test Notification/i });
      fireEvent.click(testBtn);

      await waitFor(() => {
        expect(notifySpy).toHaveBeenCalled();
        expect(
          screen.getByText('Notification dispatched to Windows Action Center.')
        ).toBeInTheDocument();
      });
    });
  });

  describe('DesktopSettingsPage', () => {
    it('handles restart backend confirmation dialog', async () => {
      const restartSpy = vi.spyOn(tauriService, 'restartBackendProcess').mockResolvedValue({
        state: 'Ready',
        pid: 9999,
        port: 8765,
        uptime_seconds: 1,
        restart_count: 1,
        max_restarts: 5,
        last_error: null,
        backend_mode: 'development-venv',
        database_ready: true,
      });

      render(
        <DesktopSettingsPage
          settings={mockAllSettings.desktop}
          isDirty={false}
          isSaving={false}
          onChange={vi.fn()}
          onSave={vi.fn()}
          onReset={vi.fn()}
        />
      );

      const restartBtn = screen.getByRole('button', { name: /Restart Backend Sidecar/i });
      fireEvent.click(restartBtn);

      await waitFor(() => {
        expect(screen.getByText('Restart Backend Sidecar Service')).toBeInTheDocument();
      });

      const confirmBtn = screen.getByRole('button', { name: /Confirm & Restart Backend/i });
      fireEvent.click(confirmBtn);

      await waitFor(() => {
        expect(restartSpy).toHaveBeenCalled();
        expect(screen.getByText(/Backend restarted successfully/i)).toBeInTheDocument();
      });
    });
  });
});
