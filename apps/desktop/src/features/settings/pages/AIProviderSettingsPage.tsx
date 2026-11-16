import React from 'react';
import type { AISettings } from '@autonom/shared-types';
import { Cpu } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import {
  SettingsSection,
  SettingsField,
  SettingsToggle,
  SettingsUnavailableState,
  SettingsSaveBar,
} from '../components';

interface AIProviderSettingsPageProps {
  settings: AISettings;
  isDirty: boolean;
  isSaving: boolean;
  saveSuccess?: boolean;
  errorMessage?: string | null;
  onChange: (updated: Partial<AISettings>) => void;
  onSave: () => void;
  onReset: () => void;
}

export const AIProviderSettingsPage: React.FC<AIProviderSettingsPageProps> = ({
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
        title="AI Model Gateway & LLM Orchestration"
        roadmapStage="Stage 11"
        description="Stage 10 establishes the configuration architecture, parameter validation, and secure DPAPI credential binding. Live inference execution and local model loading will activate in Stage 11."
        configurationNotes="Target hardware allocation: NVIDIA GeForce RTX 4050 Laptop GPU (6GB VRAM) with single active model enforcement."
      />

      <SettingsSection
        title="Local Hardware Resource Limits (RTX 4050 / 6GB VRAM)"
        description="Enforce strict memory bounds to prevent GPU Out-of-Memory (OOM) crashes and system instability."
      >
        <SettingsField
          label="Single Active Model in VRAM"
          description="Strictly ensure only one quantized local model is loaded into VRAM at any time. Prevents memory thrashing."
          requiresRestart
        >
          <SettingsToggle
            checked={settings.single_active_model_enforced}
            onCheckedChange={(checked) => onChange({ single_active_model_enforced: checked })}
            ariaLabel="Single Active Model in VRAM"
          />
        </SettingsField>

        <SettingsField
          label="Maximum VRAM Allocation Budget"
          description="Ceiling for GPU memory allocated to local LLMs (Target: 5120 MB / 5.0 GB on 6 GB RTX 4050)."
        >
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={1024}
              max={6144}
              step={256}
              value={settings.max_vram_allocation_mb}
              onChange={(e) =>
                onChange({ max_vram_allocation_mb: parseInt(e.target.value, 10) || 5120 })
              }
              className="h-8 w-24 rounded-md border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
              aria-label="Maximum VRAM Allocation Budget"
            />
            <span className="text-xs text-muted-foreground font-mono">MB</span>
          </div>
        </SettingsField>

        <SettingsField
          label="Idle Model Unload Timeout"
          description="Automatically release model weights from GPU memory after period of inactivity."
        >
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={30}
              max={3600}
              step={30}
              value={settings.idle_model_unload_seconds}
              onChange={(e) =>
                onChange({ idle_model_unload_seconds: parseInt(e.target.value, 10) || 300 })
              }
              className="h-8 w-24 rounded-md border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
              aria-label="Idle Model Unload Timeout"
            />
            <span className="text-xs text-muted-foreground font-mono">seconds</span>
          </div>
        </SettingsField>

        <SettingsField
          label="Cloud Fallback on VRAM Saturation"
          description="Route complex tasks to configured cloud provider if local model exceeds context or memory limits."
        >
          <SettingsToggle
            checked={settings.cloud_fallback_enabled}
            onCheckedChange={(checked) => onChange({ cloud_fallback_enabled: checked })}
            ariaLabel="Cloud Fallback on VRAM Saturation"
          />
        </SettingsField>
      </SettingsSection>

      <SettingsSection
        title="Configured AI Providers"
        description="Local Ollama runtime and OpenAI/Anthropic cloud model endpoints."
      >
        <div className="space-y-3">
          {settings.providers.map((prov) => (
            <div
              key={prov.id}
              className="p-3.5 rounded-lg border border-border/50 bg-secondary/20 space-y-2.5"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Cpu className="h-4 w-4 text-cyan" />
                  <span className="text-xs font-semibold text-foreground">{prov.name}</span>
                  <Badge
                    variant={prov.provider_type === 'local' ? 'cyan' : 'outline'}
                    className="text-[10px]"
                  >
                    {prov.provider_type.toUpperCase()}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="inactive" className="text-[10px]">
                    {prov.connection_status}
                  </Badge>
                  <SettingsToggle
                    checked={prov.enabled}
                    onCheckedChange={(checked) => {
                      const updated = settings.providers.map((p) =>
                        p.id === prov.id ? { ...p, enabled: checked } : p
                      );
                      onChange({ providers: updated });
                    }}
                    ariaLabel={`Enable ${prov.name}`}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-[11px] text-muted-foreground">Endpoint URL:</span>
                  <input
                    type="text"
                    value={prov.endpoint}
                    onChange={(e) => {
                      const updated = settings.providers.map((p) =>
                        p.id === prov.id ? { ...p, endpoint: e.target.value } : p
                      );
                      onChange({ providers: updated });
                    }}
                    className="mt-0.5 w-full h-7 rounded border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
                  />
                </div>
                <div>
                  <span className="text-[11px] text-muted-foreground">Auth Protocol:</span>
                  <div className="mt-1 text-xs text-foreground font-mono flex items-center gap-1.5">
                    <span>
                      {prov.auth_method === 'none'
                        ? 'None (Local Loopback)'
                        : 'API Key via DPAPI Keystore'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </SettingsSection>

      <SettingsSection
        title="Model Assignments by Task Category"
        description="Assign quantized models to specialized roles (Job Scouting, Resume Tailoring, Code Synthesis)."
      >
        <div className="space-y-3">
          {settings.models.map((mod) => (
            <div
              key={mod.id}
              className="p-3 rounded-lg border border-border/40 bg-card/40 flex items-center justify-between gap-4"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-foreground">{mod.name}</span>
                  <Badge variant="outline" className="text-[10px] font-mono">
                    {mod.task_category}
                  </Badge>
                </div>
                <div className="flex items-center gap-3 text-[11px] text-muted-foreground mt-1">
                  <span>Context: {mod.context_window.toLocaleString()} tokens</span>
                  <span>Max Out: {mod.max_output_tokens.toLocaleString()}</span>
                  <span>Temp: {mod.temperature}</span>
                </div>
              </div>
              <Badge variant="neutral" className="text-[10px]">
                {mod.provider_id}
              </Badge>
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
