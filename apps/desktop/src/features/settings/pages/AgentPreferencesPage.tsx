import React from 'react';
import type { AgentSettings, AgentConfigItem } from '@autonom/shared-types';
import { Bot, Clock } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import {
  SettingsSection,
  SettingsField,
  SettingsToggle,
  SettingsUnavailableState,
  SettingsSaveBar,
} from '../components';

interface AgentPreferencesPageProps {
  settings: AgentSettings;
  isDirty: boolean;
  isSaving: boolean;
  saveSuccess?: boolean;
  errorMessage?: string | null;
  onChange: (updated: Partial<AgentSettings>) => void;
  onSave: () => void;
  onReset: () => void;
}

export const AgentPreferencesPage: React.FC<AgentPreferencesPageProps> = ({
  settings,
  isDirty,
  isSaving,
  saveSuccess,
  errorMessage,
  onChange,
  onSave,
  onReset,
}) => {
  const handleAgentToggle = (agentId: string, enabled: boolean) => {
    const updatedAgents = settings.agents.map((ag) =>
      ag.agent_id === agentId ? { ...ag, enabled } : ag
    );
    onChange({ agents: updatedAgents });
  };

  const handleApprovalChange = (
    agentId: string,
    approval: AgentConfigItem['human_approval_requirement']
  ) => {
    const updatedAgents = settings.agents.map((ag) =>
      ag.agent_id === agentId ? { ...ag, human_approval_requirement: approval } : ag
    );
    onChange({ agents: updatedAgents });
  };

  return (
    <div className="space-y-6">
      <SettingsUnavailableState
        title="Multi-Agent Swarm Orchestration"
        roadmapStage="Stage 12 / Stage 13"
        description="Stage 10 defines the agent configuration schemas, resource limits, and approval policies. Agent execution dispatch and multi-agent consensus protocols will activate in Stages 12 and 13."
        configurationNotes="Current definitions: 24 specialized agent profiles across 4 operational tiers."
      />

      <SettingsSection
        title="Global Autonomy Policies & Error Recovery"
        description="Configure default supervision levels across all autonomous agent roles."
      >
        <SettingsField
          label="Default System Autonomy Tier"
          description="Baseline human-in-the-loop requirement. Tier 2 Supervised requires sign-off for external submissions and communications."
        >
          <select
            value={settings.default_autonomy_level}
            onChange={(e) =>
              onChange({
                default_autonomy_level: e.target.value as AgentSettings['default_autonomy_level'],
              })
            }
            className="h-8 rounded-md border border-input bg-card px-2.5 py-1 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            aria-label="Default System Autonomy Tier"
          >
            <option value="tier1_full">Tier 1: Full Autonomy (Read-Only / Low-Risk)</option>
            <option value="tier2_supervised">Tier 2: Supervised Approval (Default)</option>
            <option value="tier3_manual">Tier 3: Strict Manual Gate (Every Step)</option>
          </select>
        </SettingsField>

        <SettingsField
          label="Automatic Task Retry on Transient Failures"
          description="Retry idempotent tasks (e.g. rate-limited HTTP queries or temporary network disconnects)."
        >
          <SettingsToggle
            checked={settings.auto_retry_failed_tasks}
            onCheckedChange={(checked) => onChange({ auto_retry_failed_tasks: checked })}
            ariaLabel="Automatic Task Retry"
          />
        </SettingsField>

        <SettingsField
          label="Maximum Agent Retries"
          description="Maximum retry attempts per task before escalating to user."
        >
          <input
            type="number"
            min={0}
            max={5}
            value={settings.max_agent_retries}
            onChange={(e) => onChange({ max_agent_retries: parseInt(e.target.value, 10) || 0 })}
            className="h-8 w-20 rounded-md border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            aria-label="Maximum Agent Retries"
          />
        </SettingsField>
      </SettingsSection>

      <SettingsSection
        title="Agent Behavioral Profiles & Approval Requirements"
        description="Fine-tune individual agent timeouts, model preferences, and human approval gates."
      >
        <div className="space-y-3">
          {settings.agents.map((ag) => (
            <div
              key={ag.agent_id}
              className="p-3.5 rounded-lg border border-border/50 bg-secondary/20 space-y-2.5"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Bot className="h-4 w-4 text-primary" />
                  <span className="text-xs font-semibold text-foreground">{ag.role}</span>
                  <Badge variant="outline" className="text-[10px] font-mono">
                    {ag.agent_id}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <Badge
                    variant={ag.human_approval_requirement === 'always' ? 'warning' : 'neutral'}
                    className="text-[10px]"
                  >
                    Approval: {ag.human_approval_requirement}
                  </Badge>
                  <SettingsToggle
                    checked={ag.enabled}
                    onCheckedChange={(checked) => handleAgentToggle(ag.agent_id, checked)}
                    ariaLabel={`Enable ${ag.role}`}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs pt-1">
                <div>
                  <span className="text-[11px] text-muted-foreground">Human Approval Gate:</span>
                  <select
                    value={ag.human_approval_requirement}
                    onChange={(e) =>
                      handleApprovalChange(
                        ag.agent_id,
                        e.target.value as AgentConfigItem['human_approval_requirement']
                      )
                    }
                    className="mt-1 w-full h-7 rounded border border-input bg-card px-2 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
                  >
                    <option value="always">Always Require Approval</option>
                    <option value="sensitive_only">Sensitive Actions Only</option>
                    <option value="never">Pre-Authorized / Never</option>
                  </select>
                </div>

                <div>
                  <span className="text-[11px] text-muted-foreground">Execution Priority:</span>
                  <div className="mt-1.5 text-xs text-foreground font-mono flex items-center gap-1.5">
                    <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                    <span>Priority: {ag.execution_priority}</span>
                  </div>
                </div>

                <div>
                  <span className="text-[11px] text-muted-foreground">Max Duration:</span>
                  <div className="mt-1.5 text-xs text-foreground font-mono">
                    {ag.max_execution_duration_seconds}s timeout
                  </div>
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
