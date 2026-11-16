import React, { useState } from 'react';
import type { NotificationSettings } from '@autonom/shared-types';
import { testDesktopNotification } from '@/services/tauri';
import { Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SettingsSection, SettingsField, SettingsToggle, SettingsSaveBar } from '../components';

interface NotificationSettingsPageProps {
  settings: NotificationSettings;
  isDirty: boolean;
  isSaving: boolean;
  saveSuccess?: boolean;
  errorMessage?: string | null;
  onChange: (updated: Partial<NotificationSettings>) => void;
  onSave: () => void;
  onReset: () => void;
}

export const NotificationSettingsPage: React.FC<NotificationSettingsPageProps> = ({
  settings,
  isDirty,
  isSaving,
  saveSuccess,
  errorMessage,
  onChange,
  onSave,
  onReset,
}) => {
  const [testStatus, setTestStatus] = useState<string | null>(null);
  const [isSendingTest, setIsSendingTest] = useState(false);

  const handleTestNotification = async () => {
    setIsSendingTest(true);
    setTestStatus('Dispatching Windows Action Center test notification...');
    try {
      const sent = await testDesktopNotification(
        'AUTONOM Notification Test',
        'Windows Action Center integration is active and operating normally.'
      );
      setTestStatus(
        sent
          ? 'Notification dispatched to Windows Action Center.'
          : 'Unable to send notification (check Windows Focus Assist / Notifications permissions).'
      );
    } catch {
      setTestStatus('Notification test failed.');
    } finally {
      setIsSendingTest(false);
    }
  };

  return (
    <div className="space-y-6">
      {testStatus && (
        <div className="p-3 rounded-lg bg-primary/10 border border-primary/30 text-xs text-primary flex items-center justify-between">
          <span>{testStatus}</span>
          <button
            type="button"
            onClick={() => setTestStatus(null)}
            className="text-muted-foreground hover:text-foreground text-xs"
          >
            Dismiss
          </button>
        </div>
      )}

      <SettingsSection
        title="Desktop Notifications & Alert Channels"
        description="Configure Windows toast notifications and in-app system feedback."
        headerAction={
          <Button
            variant="outline"
            size="sm"
            onClick={handleTestNotification}
            disabled={isSendingTest || !settings.notifications_enabled}
            className="h-7 text-xs px-2.5 gap-1.5"
          >
            <Send className="h-3 w-3" />
            <span>Send Test Notification</span>
          </Button>
        }
      >
        <SettingsField
          label="Master Desktop Notifications"
          description="Global toggle for all Windows Action Center popups and taskbar toasts."
        >
          <SettingsToggle
            checked={settings.notifications_enabled}
            onCheckedChange={(checked) => onChange({ notifications_enabled: checked })}
            ariaLabel="Master Notifications"
          />
        </SettingsField>

        <SettingsField
          label="Notify on Task Completion"
          description="Send notification when an autonomous background task finishes successfully."
        >
          <SettingsToggle
            checked={settings.notify_on_task_completion}
            onCheckedChange={(checked) => onChange({ notify_on_task_completion: checked })}
            disabled={!settings.notifications_enabled}
            ariaLabel="Notify on Task Completion"
          />
        </SettingsField>

        <SettingsField
          label="Notify on Task Failure"
          description="Send high-priority alert when a task encounters an unrecoverable error or timeout."
        >
          <SettingsToggle
            checked={settings.notify_on_task_failure}
            onCheckedChange={(checked) => onChange({ notify_on_task_failure: checked })}
            disabled={!settings.notifications_enabled}
            ariaLabel="Notify on Task Failure"
          />
        </SettingsField>

        <SettingsField
          label="Notify on Pending Human Approval"
          description="Alert immediately when an agent pauses at a Tier 2 gate awaiting human sign-off."
        >
          <SettingsToggle
            checked={settings.notify_on_pending_approval}
            onCheckedChange={(checked) => onChange({ notify_on_pending_approval: checked })}
            disabled={!settings.notifications_enabled}
            ariaLabel="Notify on Pending Approval"
          />
        </SettingsField>

        <SettingsField
          label="Notify on Backend Supervisor Events"
          description="Receive toasts when the Python backend starts, crashes, or is automatically restarted."
        >
          <SettingsToggle
            checked={settings.notify_on_backend_events}
            onCheckedChange={(checked) => onChange({ notify_on_backend_events: checked })}
            disabled={!settings.notifications_enabled}
            ariaLabel="Notify on Backend Events"
          />
        </SettingsField>
      </SettingsSection>

      <SettingsSection
        title="Quiet Hours & Notification Sound"
        description="Mute non-urgent alerts during scheduled rest periods."
      >
        <SettingsField
          label="Notification Sound Chime"
          description="Play subtle Windows notification audio chime alongside toasts."
        >
          <SettingsToggle
            checked={settings.sound_enabled}
            onCheckedChange={(checked) => onChange({ sound_enabled: checked })}
            disabled={!settings.notifications_enabled}
            ariaLabel="Notification Sound"
          />
        </SettingsField>

        <SettingsField
          label="Quiet Hours Suppression"
          description="Suppress sound and intrusive banners during defined hours."
        >
          <SettingsToggle
            checked={settings.quiet_hours_enabled}
            onCheckedChange={(checked) => onChange({ quiet_hours_enabled: checked })}
            disabled={!settings.notifications_enabled}
            ariaLabel="Quiet Hours"
          />
        </SettingsField>

        {settings.quiet_hours_enabled && (
          <SettingsField
            label="Quiet Hours Window"
            description="Start and end times for alert suppression (24h format)."
          >
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={settings.quiet_hours_start}
                onChange={(e) => onChange({ quiet_hours_start: e.target.value })}
                className="h-8 w-20 rounded border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary text-center"
                placeholder="22:00"
              />
              <span className="text-xs text-muted-foreground">to</span>
              <input
                type="text"
                value={settings.quiet_hours_end}
                onChange={(e) => onChange({ quiet_hours_end: e.target.value })}
                className="h-8 w-20 rounded border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary text-center"
                placeholder="08:00"
              />
            </div>
          </SettingsField>
        )}

        <SettingsField
          label="Mask Sensitive Toast Content"
          description="Omit applicant names, email addresses, and salary figures from Windows Action Center popups."
        >
          <SettingsToggle
            checked={settings.mask_sensitive_previews}
            onCheckedChange={(checked) => onChange({ mask_sensitive_previews: checked })}
            ariaLabel="Mask Sensitive Previews"
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
