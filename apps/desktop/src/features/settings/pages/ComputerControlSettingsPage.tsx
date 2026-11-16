import React from 'react';
import type { ComputerControlSettings } from '@autonom/shared-types';
import { ShieldAlert } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import {
  SettingsSection,
  SettingsField,
  SettingsToggle,
  SettingsUnavailableState,
  SettingsSaveBar,
} from '../components';

interface ComputerControlSettingsPageProps {
  settings: ComputerControlSettings;
  isDirty: boolean;
  isSaving: boolean;
  saveSuccess?: boolean;
  errorMessage?: string | null;
  onChange: (updated: Partial<ComputerControlSettings>) => void;
  onSave: () => void;
  onReset: () => void;
}

export const ComputerControlSettingsPage: React.FC<ComputerControlSettingsPageProps> = ({
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
      <SettingsUnavailableState
        title="Autonomous Computer Interaction & Browser Control"
        roadmapStage="Stages 16–20"
        description="Stage 10 defines interaction modes, capture frequency, security masks, and process boundaries. Autonomous mouse/keyboard input and structural UIA drivers will activate in Stages 16 through 20."
        configurationNotes="Zero-Desktop-Capture Rule: No background screenshotting or input synthesis occurs until explicit computer control sessions are authorized."
      />

      <SettingsSection
        title="Interaction Modality & Vision Grounding"
        description="Choose between structural automation (Windows Accessibility Tree / DOM) and vision models."
      >
        <SettingsField
          label="Preferred Interaction Modality"
          description="Structural-first queries accessible Win32/UIA and browser DOM nodes before consuming GPU vision tokens."
        >
          <select
            value={settings.preferred_interaction_mode}
            onChange={(e) =>
              onChange({
                preferred_interaction_mode: e.target
                  .value as ComputerControlSettings['preferred_interaction_mode'],
              })
            }
            className="h-8 rounded-md border border-input bg-card px-2.5 py-1 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            aria-label="Preferred Interaction Modality"
          >
            <option value="structural_first">
              Structural-First (UIA/DOM with Visual Fallback)
            </option>
            <option value="visual_first">Visual-First (Screenshots & Coordinate Grounding)</option>
            <option value="structural_only">Structural-Only (Strict Win32 UIA Tree Only)</option>
          </select>
        </SettingsField>

        <SettingsField
          label="Vision Coordinate Fallback"
          description="Allow vision model fallback when Windows controls lack accessibility labels (e.g. custom game engines, canvas widgets)."
        >
          <SettingsToggle
            checked={settings.visual_fallback_enabled}
            onCheckedChange={(checked) => onChange({ visual_fallback_enabled: checked })}
            ariaLabel="Vision Coordinate Fallback"
          />
        </SettingsField>

        <SettingsField
          label="Synthesized Mouse & Keyboard Input"
          description="Permit synthetic Win32 SendInput events. Strictly disabled during Stage 10."
        >
          <SettingsToggle
            checked={settings.mouse_keyboard_control_enabled}
            onCheckedChange={(checked) => onChange({ mouse_keyboard_control_enabled: checked })}
            disabled={true}
            activeLabel="Enabled"
            inactiveLabel="Disabled (Planned S17)"
            ariaLabel="Synthesized Mouse and Keyboard Input"
          />
        </SettingsField>
      </SettingsSection>

      <SettingsSection
        title="Desktop Screenshot Policy & Privacy Redaction"
        description="Configure capture frequency, local retention limits, and automatic privacy masking."
      >
        <SettingsField
          label="Sensitive Screen Region Redaction"
          description="Automatically mask password inputs, credit card forms, and banking windows before processing."
        >
          <SettingsToggle
            checked={settings.sensitive_region_redaction}
            onCheckedChange={(checked) => onChange({ sensitive_region_redaction: checked })}
            ariaLabel="Sensitive Screen Region Redaction"
          />
        </SettingsField>

        <SettingsField
          label="Active Session Screenshot Retention"
          description="Number of hours interaction screenshots are preserved in local artifacts before automated deletion."
        >
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={1}
              max={168}
              value={settings.screenshot_retention_hours}
              onChange={(e) =>
                onChange({ screenshot_retention_hours: parseInt(e.target.value, 10) || 24 })
              }
              className="h-8 w-20 rounded-md border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
              aria-label="Screenshot Retention Hours"
            />
            <span className="text-xs text-muted-foreground font-mono">hours</span>
          </div>
        </SettingsField>

        <SettingsField
          label="Session Inactivity Timeout"
          description="Automatically terminate computer control context if no user or agent activity occurs."
        >
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={5}
              max={240}
              step={5}
              value={settings.session_timeout_minutes}
              onChange={(e) =>
                onChange({ session_timeout_minutes: parseInt(e.target.value, 10) || 30 })
              }
              className="h-8 w-20 rounded-md border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
              aria-label="Session Inactivity Timeout"
            />
            <span className="text-xs text-muted-foreground font-mono">minutes</span>
          </div>
        </SettingsField>
      </SettingsSection>

      <SettingsSection
        title="Application Security Boundaries"
        description="Allowed and strictly blocked Win32 executables."
      >
        <div className="space-y-3">
          <div>
            <span className="text-xs font-medium text-foreground">
              Permitted Application Scope:
            </span>
            <div className="flex flex-wrap gap-1.5 mt-1.5">
              {settings.allowed_applications.map((app) => (
                <Badge key={app} variant="cyan" className="text-[11px] font-mono">
                  {app}
                </Badge>
              ))}
            </div>
          </div>

          <div className="pt-2 border-t border-border/30">
            <span className="text-xs font-medium text-rose-300 flex items-center gap-1.5">
              <ShieldAlert className="h-3.5 w-3.5" />
              <span>Strictly Blocked Processes (Hard Enforced):</span>
            </span>
            <div className="flex flex-wrap gap-1.5 mt-1.5">
              {settings.blocked_applications.map((app) => (
                <Badge key={app} variant="error" className="text-[11px] font-mono">
                  {app}
                </Badge>
              ))}
            </div>
          </div>
        </div>
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
