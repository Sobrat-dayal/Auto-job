import React from 'react';
import type { AppearanceSettings } from '@autonom/shared-types';
import { useDensity } from '@/design-system/ThemeContext';
import { SettingsSection, SettingsField, SettingsToggle, SettingsSaveBar } from '../components';

interface AppearanceSettingsPageProps {
  settings: AppearanceSettings;
  isDirty: boolean;
  isSaving: boolean;
  saveSuccess?: boolean;
  errorMessage?: string | null;
  onChange: (updated: Partial<AppearanceSettings>) => void;
  onSave: () => void;
  onReset: () => void;
}

export const AppearanceSettingsPage: React.FC<AppearanceSettingsPageProps> = ({
  settings,
  isDirty,
  isSaving,
  saveSuccess,
  errorMessage,
  onChange,
  onSave,
  onReset,
}) => {
  const { setDensity } = useDensity();

  const handleDensityChange = (newDensity: AppearanceSettings['density']) => {
    onChange({ density: newDensity });
    setDensity(newDensity);
  };

  return (
    <div className="space-y-6">
      <SettingsSection
        title="Theme & Visual Palette"
        description="Configure dark mode aesthetic and surface accents. Professional dark navy design is the established standard."
      >
        <SettingsField
          label="Visual Color Theme"
          description="High-contrast dark navy surfaces with vibrant blue and cyan accents."
        >
          <select
            value={settings.theme}
            onChange={(e) => onChange({ theme: e.target.value as AppearanceSettings['theme'] })}
            className="h-8 rounded-md border border-input bg-card px-2.5 py-1 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            aria-label="Visual Color Theme"
          >
            <option value="navy-dark">Navy Dark (Default Charcoal-Blue)</option>
            <option value="dark">Pure Dark (High Contrast)</option>
          </select>
        </SettingsField>

        <SettingsField
          label="Interface Layout Density"
          description="Comfortable density gives breathing room; compact density maximizes information on 1080p and smaller screens."
        >
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => handleDensityChange('comfortable')}
              className={`px-3 py-1.5 rounded-md text-xs font-medium border transition-colors ${
                settings.density === 'comfortable'
                  ? 'bg-primary/20 text-primary border-primary/50'
                  : 'bg-card text-muted-foreground border-border hover:bg-muted/40'
              }`}
            >
              Comfortable
            </button>
            <button
              type="button"
              onClick={() => handleDensityChange('compact')}
              className={`px-3 py-1.5 rounded-md text-xs font-medium border transition-colors ${
                settings.density === 'compact'
                  ? 'bg-primary/20 text-primary border-primary/50'
                  : 'bg-card text-muted-foreground border-border hover:bg-muted/40'
              }`}
            >
              Compact
            </button>
          </div>
        </SettingsField>

        <SettingsField
          label="Global Font Scaling"
          description="Adjust root typography size for readability across high-DPI desktop displays."
        >
          <select
            value={settings.font_scale}
            onChange={(e) =>
              onChange({ font_scale: e.target.value as AppearanceSettings['font_scale'] })
            }
            className="h-8 rounded-md border border-input bg-card px-2.5 py-1 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            aria-label="Global Font Scaling"
          >
            <option value="90%">90% (Dense / Small)</option>
            <option value="100%">100% (Standard 14px Base)</option>
            <option value="110%">110% (Enlarged / Large)</option>
          </select>
        </SettingsField>
      </SettingsSection>

      <SettingsSection
        title="Navigation & Motion Preferences"
        description="Configure sidebar default behavior and transition animations."
      >
        <SettingsField
          label="Sidebar Default Expanded"
          description="Keep navigation labels expanded by default rather than starting in collapsed icon-rail mode."
        >
          <SettingsToggle
            checked={settings.sidebar_default_expanded}
            onCheckedChange={(checked) => onChange({ sidebar_default_expanded: checked })}
            ariaLabel="Sidebar Default Expanded"
          />
        </SettingsField>

        <SettingsField
          label="Reduced Motion"
          description="Minimize smooth transitions, pulse indicators, and CSS keyframe animations."
        >
          <SettingsToggle
            checked={settings.reduced_motion}
            onCheckedChange={(checked) => onChange({ reduced_motion: checked })}
            ariaLabel="Reduced Motion"
          />
        </SettingsField>

        <SettingsField
          label="Chart Animations"
          description="Enable animated line transitions and bar entrance effects on Recharts dashboards."
        >
          <SettingsToggle
            checked={settings.chart_animations}
            onCheckedChange={(checked) => onChange({ chart_animations: checked })}
            ariaLabel="Chart Animations"
          />
        </SettingsField>

        <SettingsField
          label="Data Table Density"
          description="Adjust cell vertical padding inside jobs, tasks, and audit logs."
        >
          <select
            value={settings.table_density}
            onChange={(e) =>
              onChange({ table_density: e.target.value as AppearanceSettings['table_density'] })
            }
            className="h-8 rounded-md border border-input bg-card px-2.5 py-1 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            aria-label="Data Table Density"
          >
            <option value="normal">Normal (Padding 12px)</option>
            <option value="compact">Compact (Padding 6px)</option>
          </select>
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
