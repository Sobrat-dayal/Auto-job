import React, { useState } from 'react';
import type { DesktopSettingsModel } from '@autonom/shared-types';
import {
  restartBackendProcess,
  openArtifactLocation,
  updateDesktopSettings,
} from '@/services/tauri';
import { Folder, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  SettingsSection,
  SettingsField,
  SettingsToggle,
  SettingsConfirmationDialog,
  SettingsSaveBar,
} from '../components';

interface DesktopSettingsPageProps {
  settings: DesktopSettingsModel;
  isDirty: boolean;
  isSaving: boolean;
  saveSuccess?: boolean;
  errorMessage?: string | null;
  onChange: (updated: Partial<DesktopSettingsModel>) => void;
  onSave: () => void;
  onReset: () => void;
}

export const DesktopSettingsPage: React.FC<DesktopSettingsPageProps> = ({
  settings,
  isDirty,
  isSaving,
  saveSuccess,
  errorMessage,
  onChange,
  onSave,
  onReset,
}) => {
  const [isRestarting, setIsRestarting] = useState(false);
  const [restartConfirmOpen, setRestartConfirmOpen] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const handleRestartBackend = async () => {
    setIsRestarting(true);
    setRestartConfirmOpen(false);
    setActionMessage('Restarting Python FastAPI sidecar process...');
    try {
      const status = await restartBackendProcess();
      setActionMessage(
        `Backend restarted successfully (PID: ${status.pid}, Port: ${status.port}).`
      );
    } catch (err) {
      setActionMessage(err instanceof Error ? err.message : 'Backend restart failed');
    } finally {
      setIsRestarting(false);
    }
  };

  const handleOpenAppData = async () => {
    setActionMessage('Opening %LOCALAPPDATA%\\AUTONOM in Windows File Explorer...');
    try {
      await openArtifactLocation('');
    } catch (err) {
      setActionMessage(err instanceof Error ? err.message : 'Failed to open directory');
    }
  };

  return (
    <div className="space-y-6">
      {actionMessage && (
        <div className="p-3 rounded-lg bg-primary/10 border border-primary/30 text-xs text-primary flex items-center justify-between">
          <span>{actionMessage}</span>
          <button
            type="button"
            onClick={() => setActionMessage(null)}
            className="text-muted-foreground hover:text-foreground text-xs"
          >
            Dismiss
          </button>
        </div>
      )}

      <SettingsSection
        title="Windows 11 Desktop Shell & Lifecycle"
        description="Configure Windows startup, system notification tray behavior, and window geometry."
        headerAction={
          <Button
            variant="outline"
            size="sm"
            onClick={handleOpenAppData}
            className="h-7 text-xs px-2.5 gap-1.5"
            title="Open %LOCALAPPDATA%\AUTONOM in Windows File Explorer"
          >
            <Folder className="h-3 w-3" />
            <span>Open App Data</span>
          </Button>
        }
      >
        <SettingsField
          label="Launch at Windows Login"
          description="Register AUTONOM with Windows Startup (CurrentVersion\Run) to start on boot."
        >
          <SettingsToggle
            checked={settings.start_at_login}
            onCheckedChange={(checked) => {
              onChange({ start_at_login: checked });
              updateDesktopSettings({ start_at_login: checked });
            }}
            ariaLabel="Launch at Windows Login"
          />
        </SettingsField>

        <SettingsField
          label="Close-to-Tray Minimization"
          description="Closing the window hides it to the Windows notification tray instead of terminating the app."
        >
          <SettingsToggle
            checked={settings.close_to_tray}
            onCheckedChange={(checked) => {
              onChange({ close_to_tray: checked });
              updateDesktopSettings({ close_to_tray: checked });
            }}
            ariaLabel="Close to Tray"
          />
        </SettingsField>

        <SettingsField
          label="Minimize-to-Tray"
          description="Minimizing the window sends it to the system tray rather than the taskbar."
        >
          <SettingsToggle
            checked={settings.minimize_to_tray}
            onCheckedChange={(checked) => onChange({ minimize_to_tray: checked })}
            ariaLabel="Minimize to Tray"
          />
        </SettingsField>

        <SettingsField
          label="Restore Window Geometry on Launch"
          description="Remember previous window size, coordinates, and monitor placement across sessions."
        >
          <SettingsToggle
            checked={settings.restore_window_position}
            onCheckedChange={(checked) => onChange({ restore_window_position: checked })}
            ariaLabel="Restore Window Position"
          />
        </SettingsField>
      </SettingsSection>

      <SettingsSection
        title="Python Backend Sidecar Supervision"
        description="Manage the native Rust supervisor overseeing the local FastAPI HTTP/SSE server."
        headerAction={
          <Button
            variant="outline"
            size="sm"
            onClick={() => setRestartConfirmOpen(true)}
            disabled={isRestarting}
            className="h-7 text-xs px-2.5 gap-1.5 border-amber-500/30 text-amber-300 hover:bg-amber-500/10"
          >
            <RotateCcw className={`h-3 w-3 ${isRestarting ? 'animate-spin' : ''}`} />
            <span>Restart Backend Sidecar</span>
          </Button>
        }
      >
        <SettingsField
          label="Auto-Start Backend Sidecar with Desktop"
          description="Automatically launch and monitor the Python FastAPI backend process when AUTONOM starts."
        >
          <SettingsToggle
            checked={settings.auto_start_backend_sidecar}
            onCheckedChange={(checked) => onChange({ auto_start_backend_sidecar: checked })}
            ariaLabel="Auto-Start Backend Sidecar"
          />
        </SettingsField>

        <SettingsField
          label="Maximum Supervisor Crash Restarts"
          description="Maximum consecutive restarts if the backend crashes unexpectedly before halting to prevent boot loops."
        >
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={1}
              max={20}
              value={settings.max_backend_restarts}
              onChange={(e) =>
                onChange({ max_backend_restarts: parseInt(e.target.value, 10) || 5 })
              }
              className="h-8 w-20 rounded-md border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
              aria-label="Max Backend Restarts"
            />
            <span className="text-xs text-muted-foreground font-mono">restarts</span>
          </div>
        </SettingsField>
      </SettingsSection>

      <SettingsConfirmationDialog
        open={restartConfirmOpen}
        onOpenChange={setRestartConfirmOpen}
        title="Restart Backend Sidecar Service"
        description="Restarting the backend sidecar terminates the active FastAPI process and re-establishes local SQLite and event streaming connections. Any tasks actively executing in memory may be interrupted. Do you wish to proceed?"
        confirmLabel="Confirm & Restart Backend"
        variant="destructive"
        isConfirming={isRestarting}
        onConfirm={handleRestartBackend}
      />

      <SettingsSaveBar
        isDirty={isDirty}
        isSaving={isSaving}
        saveSuccess={saveSuccess}
        errorMessage={errorMessage}
        onSave={onSave}
        onReset={onReset}
      />
    </div>
  );
};
