import React from 'react';
import type { GeneralSettings } from '@autonom/shared-types';
import { SettingsSection, SettingsField, SettingsToggle, SettingsSaveBar } from '../components';

interface GeneralSettingsPageProps {
  settings: GeneralSettings;
  isDirty: boolean;
  isSaving: boolean;
  saveSuccess?: boolean;
  errorMessage?: string | null;
  onChange: (updated: Partial<GeneralSettings>) => void;
  onSave: () => void;
  onReset: () => void;
}

export const GeneralSettingsPage: React.FC<GeneralSettingsPageProps> = ({
  settings,
  isDirty,
  isSaving,
  saveSuccess,
  errorMessage,
  onChange,
  onSave,
  onReset,
}) => {
  return (
    <div className="space-y-6">
      <SettingsSection
        title="Localization & Regional Format"
        description="Configure language, calendar date formats, clock display, and timezone presentation."
      >
        <SettingsField
          label="Application Language"
          description="Interface display language (architecture ready for multi-language localization)."
        >
          <select
            value={settings.app_language}
            onChange={(e) => onChange({ app_language: e.target.value })}
            className="h-8 rounded-md border border-input bg-card px-2.5 py-1 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            aria-label="Application Language"
          >
            <option value="en-US">English (United States) — en-US</option>
            <option value="en-GB">English (United Kingdom) — en-GB</option>
            <option value="de-DE">Deutsch (Germany) — de-DE</option>
            <option value="fr-FR">Français (France) — fr-FR</option>
            <option value="ja-JP">日本語 (Japan) — ja-JP</option>
          </select>
        </SettingsField>

        <SettingsField
          label="Date Presentation Format"
          description="Standard date presentation across job applications, history trails, and logs."
        >
          <select
            value={settings.date_format}
            onChange={(e) =>
              onChange({
                date_format: e.target.value as GeneralSettings['date_format'],
              })
            }
            className="h-8 rounded-md border border-input bg-card px-2.5 py-1 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            aria-label="Date Presentation Format"
          >
            <option value="YYYY-MM-DD">ISO 8601 (YYYY-MM-DD)</option>
            <option value="DD/MM/YYYY">International (DD/MM/YYYY)</option>
            <option value="MM/DD/YYYY">US Standard (MM/DD/YYYY)</option>
          </select>
        </SettingsField>

        <SettingsField
          label="Clock Display Format"
          description="Choose between 24-hour military clock and 12-hour AM/PM format."
        >
          <select
            value={settings.time_format}
            onChange={(e) =>
              onChange({
                time_format: e.target.value as GeneralSettings['time_format'],
              })
            }
            className="h-8 rounded-md border border-input bg-card px-2.5 py-1 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            aria-label="Clock Display Format"
          >
            <option value="24h">24-Hour (18:30)</option>
            <option value="12h">12-Hour (06:30 PM)</option>
          </select>
        </SettingsField>

        <SettingsField
          label="Timezone Representation"
          description="Timestamps are stored in UTC at rest and formatted to local system time or explicit UTC."
        >
          <select
            value={settings.timezone_display}
            onChange={(e) =>
              onChange({
                timezone_display: e.target.value as GeneralSettings['timezone_display'],
              })
            }
            className="h-8 rounded-md border border-input bg-card px-2.5 py-1 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            aria-label="Timezone Representation"
          >
            <option value="Local">Local System Timezone</option>
            <option value="UTC">Universal Coordinated Time (UTC)</option>
          </select>
        </SettingsField>
      </SettingsSection>

      <SettingsSection
        title="Application Navigation & Landing Page"
        description="Choose the initial workspace route when launching AUTONOM."
      >
        <SettingsField
          label="Default Startup Workspace"
          description="Route automatically loaded when the application boots."
        >
          <select
            value={settings.default_landing_page}
            onChange={(e) => onChange({ default_landing_page: e.target.value })}
            className="h-8 rounded-md border border-input bg-card px-2.5 py-1 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            aria-label="Default Startup Workspace"
          >
            <option value="/dashboard">Command Center Dashboard (/dashboard)</option>
            <option value="/recruitment">Recruitment & Job Scout (/recruitment)</option>
            <option value="/agents">Agent Swarm Directory (/agents)</option>
            <option value="/workflows">Workflow Canvas & Automation (/workflows)</option>
            <option value="/activity">Activity Ledger & Audit Log (/activity)</option>
          </select>
        </SettingsField>
      </SettingsSection>

      <SettingsSection
        title="Safety & User Confirmation Gates"
        description="Configure human confirmation dialogs before executing critical or irreversible operations."
      >
        <SettingsField
          label="Confirm Destructive Actions"
          description="Show modal confirmation dialog before deleting artifacts, credentials, or logs."
        >
          <SettingsToggle
            checked={settings.confirm_destructive_actions}
            onCheckedChange={(checked) => onChange({ confirm_destructive_actions: checked })}
            ariaLabel="Confirm Destructive Actions"
          />
        </SettingsField>

        <SettingsField
          label="Confirm Database Restoration"
          description="Require explicit two-step confirmation before replacing SQLite database with a backup snapshot."
        >
          <SettingsToggle
            checked={settings.confirm_backup_restore}
            onCheckedChange={(checked) => onChange({ confirm_backup_restore: checked })}
            ariaLabel="Confirm Database Restoration"
          />
        </SettingsField>

        <SettingsField
          label="Confirm Task Cancellation"
          description="Prompt confirmation before sending cooperative cancellation interrupt to active workers."
        >
          <SettingsToggle
            checked={settings.confirm_task_cancellation}
            onCheckedChange={(checked) => onChange({ confirm_task_cancellation: checked })}
            ariaLabel="Confirm Task Cancellation"
          />
        </SettingsField>
      </SettingsSection>

      <SettingsSection
        title="Accessibility & Technical Visibility"
        description="Fine-tune diagnostic telemetry and accessibility options."
      >
        <SettingsField
          label="Show Technical Hardware Metrics"
          description="Display VRAM allocation, thread pool utilization, and latency metrics in headers and dashboards."
        >
          <SettingsToggle
            checked={settings.show_technical_metrics}
            onCheckedChange={(checked) => onChange({ show_technical_metrics: checked })}
            ariaLabel="Show Technical Hardware Metrics"
          />
        </SettingsField>

        <SettingsField
          label="High Contrast Surface Borders"
          description="Accentuate card and panel borders for improved readability and accessibility."
        >
          <SettingsToggle
            checked={settings.high_contrast_borders}
            onCheckedChange={(checked) => onChange({ high_contrast_borders: checked })}
            ariaLabel="High Contrast Surface Borders"
          />
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
