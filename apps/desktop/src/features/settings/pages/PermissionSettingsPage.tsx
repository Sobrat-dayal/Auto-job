import React from 'react';
import type { PermissionSettings } from '@autonom/shared-types';
import { Badge } from '@/components/ui/badge';
import {
  SettingsSection,
  SettingsField,
  SettingsToggle,
  SettingsUnavailableState,
  SettingsSaveBar,
} from '../components';

interface PermissionSettingsPageProps {
  settings: PermissionSettings;
  isDirty: boolean;
  isSaving: boolean;
  saveSuccess?: boolean;
  errorMessage?: string | null;
  onChange: (updated: Partial<PermissionSettings>) => void;
  onSave: () => void;
  onReset: () => void;
}

export const PermissionSettingsPage: React.FC<PermissionSettingsPageProps> = ({
  settings,
  isDirty,
  isSaving,
  saveSuccess,
  errorMessage,
  onChange,
  onSave,
  onReset,
}) => {
  const handlePermissionChange = (
    categoryId: string,
    field: 'allowed' | 'requires_approval',
    value: boolean
  ) => {
    const updated = settings.permissions.map((p) =>
      p.category_id === categoryId ? { ...p, [field]: value } : p
    );
    onChange({ permissions: updated });
  };

  return (
    <div className="space-y-6">
      <SettingsUnavailableState
        title="Autonomous Authorization & Action Policy Engine"
        roadmapStage="Stage 14"
        description="Stage 10 establishes the centralized permission matrix and pre-authorization boundaries. Full real-time policy evaluation and runtime interceptors will activate in Stage 14."
        configurationNotes="Current model: 14 distinct action categories across 3 security tiers."
      />

      <SettingsSection
        title="Hardware Interruption & Pre-Authorization Gates"
        description="Define physical killswitch keys and safe autonomous exploration rules."
      >
        <SettingsField
          label="Emergency Automation Killswitch Hotkey"
          description="Global Windows hotkey to immediately revoke execution permissions and pause active workers."
        >
          <div className="flex items-center gap-2">
            <kbd className="px-2.5 py-1 rounded bg-card border border-border text-xs font-mono text-cyan font-bold shadow-xs">
              {settings.emergency_killswitch_hotkey}
            </kbd>
            <span className="text-[11px] text-muted-foreground">(Also supports Ctrl+Alt+Esc)</span>
          </div>
        </SettingsField>

        <SettingsField
          label="Pre-Authorize Read-Only Job Discovery"
          description="Allow agents to search job boards and aggregate listings without asking for individual permission."
        >
          <SettingsToggle
            checked={settings.preauthorize_discovery}
            onCheckedChange={(checked) => onChange({ preauthorize_discovery: checked })}
            ariaLabel="Pre-Authorize Discovery"
          />
        </SettingsField>

        <SettingsField
          label="Pre-Authorize Application Dossier Preparation"
          description="Allow tailoring resumes, compiling cover letters, and drafting responses in local workspace without human gate."
        >
          <SettingsToggle
            checked={settings.preauthorize_dossier_prep}
            onCheckedChange={(checked) => onChange({ preauthorize_dossier_prep: checked })}
            ariaLabel="Pre-Authorize Dossier Prep"
          />
        </SettingsField>
      </SettingsSection>

      <SettingsSection
        title="Action Category Permissions Matrix"
        description="Granular control over file access, network requests, computer automation, and sensitive operations."
      >
        <div className="space-y-2">
          {settings.permissions.map((rule) => (
            <div
              key={rule.category_id}
              className="p-3 rounded-lg border border-border/40 bg-card/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
            >
              <div className="space-y-0.5 max-w-md">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-foreground">{rule.name}</span>
                  <Badge variant="outline" className="text-[10px] font-mono">
                    {rule.category_id}
                  </Badge>
                </div>
                <p className="text-[11px] text-muted-foreground">{rule.description}</p>
              </div>

              <div className="flex items-center gap-4 shrink-0">
                <div className="flex items-center gap-1.5">
                  <span className="text-[11px] text-muted-foreground">Allowed:</span>
                  <SettingsToggle
                    checked={rule.allowed}
                    onCheckedChange={(val) =>
                      handlePermissionChange(rule.category_id, 'allowed', val)
                    }
                    ariaLabel={`Allow ${rule.name}`}
                  />
                </div>

                <div className="flex items-center gap-1.5 border-l border-border/40 pl-3">
                  <span className="text-[11px] text-muted-foreground">Require Sign-off:</span>
                  <SettingsToggle
                    checked={rule.requires_approval}
                    onCheckedChange={(val) =>
                      handlePermissionChange(rule.category_id, 'requires_approval', val)
                    }
                    disabled={!rule.allowed}
                    ariaLabel={`Require approval for ${rule.name}`}
                  />
                </div>
              </div>
            </div>
          ))}
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
