import React from 'react';
import type { AutomationSettings } from '@autonom/shared-types';
import {
  SettingsSection,
  SettingsField,
  SettingsToggle,
  SettingsRestartNotice,
  SettingsSaveBar,
} from '../components';

interface AutomationSettingsPageProps {
  settings: AutomationSettings;
  isDirty: boolean;
  isSaving: boolean;
  saveSuccess?: boolean;
  errorMessage?: string | null;
  onChange: (updated: Partial<AutomationSettings>) => void;
  onSave: () => void;
  onReset: () => void;
  onRestartBackend?: () => void;
  isRestartingBackend?: boolean;
}

export const AutomationSettingsPage: React.FC<AutomationSettingsPageProps> = ({
  settings,
  isDirty,
  isSaving,
  saveSuccess,
  errorMessage,
  onChange,
  onSave,
  onReset,
  onRestartBackend,
  isRestartingBackend,
}) => {
  return (
    <div className="space-y-6">
      <SettingsRestartNotice
        onRestartBackend={onRestartBackend}
        isRestarting={isRestartingBackend}
        message="Changes to maximum concurrent workers or bounded queue depth take effect upon restarting the backend sidecar service."
      />

      <SettingsSection
        title="Background Worker Pool & Execution Concurrency"
        description="Configure Stage 03 task execution pool bounds to balance responsiveness with CPU and memory usage."
      >
        <SettingsField
          label="Maximum Concurrent Workers"
          description="Number of parallel worker execution slots (bounded between 1 and 8 to prevent CPU starvation)."
          requiresRestart
        >
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={1}
              max={8}
              value={settings.max_concurrent_workers}
              onChange={(e) =>
                onChange({ max_concurrent_workers: parseInt(e.target.value, 10) || 4 })
              }
              className="h-8 w-20 rounded-md border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
              aria-label="Maximum Concurrent Workers"
            />
            <span className="text-xs text-muted-foreground font-mono">workers</span>
          </div>
        </SettingsField>

        <SettingsField
          label="Maximum Bounded Task Queue Depth"
          description="Backpressure limit. Tasks submitted beyond this capacity are rejected with HTTP 429."
          requiresRestart
        >
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={10}
              max={200}
              step={10}
              value={settings.max_queued_tasks}
              onChange={(e) => onChange({ max_queued_tasks: parseInt(e.target.value, 10) || 50 })}
              className="h-8 w-20 rounded-md border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
              aria-label="Maximum Bounded Task Queue Depth"
            />
            <span className="text-xs text-muted-foreground font-mono">tasks</span>
          </div>
        </SettingsField>

        <SettingsField
          label="Default Task Execution Timeout"
          description="Global watchdog execution timeout for asynchronous background worker jobs."
        >
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={5}
              max={600}
              step={5}
              value={settings.task_default_timeout_seconds}
              onChange={(e) =>
                onChange({ task_default_timeout_seconds: parseFloat(e.target.value) || 60.0 })
              }
              className="h-8 w-20 rounded-md border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
              aria-label="Default Task Execution Timeout"
            />
            <span className="text-xs text-muted-foreground font-mono">seconds</span>
          </div>
        </SettingsField>

        <SettingsField
          label="Automatic Retry Limit"
          description="Maximum automatic retries before a failing task transitions to Failed state."
        >
          <input
            type="number"
            min={0}
            max={10}
            value={settings.retry_limit}
            onChange={(e) => onChange({ retry_limit: parseInt(e.target.value, 10) || 0 })}
            className="h-8 w-20 rounded-md border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            aria-label="Automatic Retry Limit"
          />
        </SettingsField>
      </SettingsSection>

      <SettingsSection
        title="Queue Dispatch & Error Containment"
        description="Automated circuit breakers to halt task execution during error spikes."
      >
        <SettingsField
          label="Background Task Dispatch Enabled"
          description="Master dispatch switch. Disabling prevents new tasks from being accepted by workers."
        >
          <SettingsToggle
            checked={settings.background_dispatch_enabled}
            onCheckedChange={(checked) => onChange({ background_dispatch_enabled: checked })}
            ariaLabel="Background Task Dispatch"
          />
        </SettingsField>

        <SettingsField
          label="Pause Dispatch on Error Spike"
          description="Automatically pause task queue if consecutive task failures exceed 50% in a 5-minute window."
        >
          <SettingsToggle
            checked={settings.pause_dispatch_on_error_spike}
            onCheckedChange={(checked) => onChange({ pause_dispatch_on_error_spike: checked })}
            ariaLabel="Pause Dispatch on Error Spike"
          />
        </SettingsField>

        <SettingsField
          label="Notify on Task Failure"
          description="Dispatch desktop notification when any background job fails or times out."
        >
          <SettingsToggle
            checked={settings.notify_on_task_failure}
            onCheckedChange={(checked) => onChange({ notify_on_task_failure: checked })}
            ariaLabel="Notify on Task Failure"
          />
        </SettingsField>

        <SettingsField
          label="Task History SQLite Retention"
          description="Number of days completed and cancelled task records are preserved before automated vacuum."
        >
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={7}
              max={365}
              value={settings.task_history_retention_days}
              onChange={(e) =>
                onChange({ task_history_retention_days: parseInt(e.target.value, 10) || 30 })
              }
              className="h-8 w-20 rounded-md border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
              aria-label="Task History SQLite Retention"
            />
            <span className="text-xs text-muted-foreground font-mono">days</span>
          </div>
        </SettingsField>
      </SettingsSection>

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
