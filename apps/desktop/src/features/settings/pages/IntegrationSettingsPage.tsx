import React, { useEffect, useState } from 'react';
import type { IntegrationSettings, CredentialStatus } from '@autonom/shared-types';
import { apiClient } from '@/lib/api-client';
import { Boxes, Key } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import {
  SettingsSection,
  SettingsField,
  SettingsToggle,
  SettingsUnavailableState,
  SettingsSaveBar,
} from '../components';

interface IntegrationSettingsPageProps {
  settings: IntegrationSettings;
  isDirty: boolean;
  isSaving: boolean;
  saveSuccess?: boolean;
  errorMessage?: string | null;
  onChange: (updated: Partial<IntegrationSettings>) => void;
  onSave: () => void;
  onReset: () => void;
}

export const IntegrationSettingsPage: React.FC<IntegrationSettingsPageProps> = ({
  settings,
  isDirty,
  isSaving,
  saveSuccess,
  errorMessage,
  onChange,
  onSave,
  onReset,
}) => {
  const [credentials, setCredentials] = useState<CredentialStatus[]>([]);
  const [isLoadingCreds, setIsLoadingCreds] = useState(false);

  useEffect(() => {
    let mounted = true;
    const fetchCreds = async () => {
      setIsLoadingCreds(true);
      try {
        const list = await apiClient.getCredentialStatus();
        if (mounted) setCredentials(list);
      } catch {
        // Backend offline or error
      } finally {
        if (mounted) setIsLoadingCreds(false);
      }
    };
    fetchCreds();
    return () => {
      mounted = false;
    };
  }, []);

  const handleMCPServerToggle = (serverId: string, enabled: boolean) => {
    const updated = settings.mcp_servers.map((s) =>
      s.server_id === serverId ? { ...s, enabled } : s
    );
    onChange({ mcp_servers: updated });
  };

  return (
    <div className="space-y-6">
      <SettingsUnavailableState
        title="Model Context Protocol (MCP) & Service Connectors"
        roadmapStage="Stage 23 / Stage 45"
        description="Stage 10 provides secure endpoint configuration and DPAPI credential binding. Automated tool execution via MCP client pipelines will activate in Stages 23 and 45."
        configurationNotes="Local credential vault is active and backed by Windows DPAPI key wrapping."
      />

      <SettingsSection
        title="Communication & Sourcing Integrations"
        description="Enable autonomous interaction with external communication networks and job boards."
      >
        <SettingsField
          label="Job Board Scouting Connectors"
          description="Index opportunities from supported ATS platforms (LinkedIn, Indeed, Greenhouse, Lever, Workday)."
        >
          <SettingsToggle
            checked={settings.job_board_scouting_enabled}
            onCheckedChange={(checked) => onChange({ job_board_scouting_enabled: checked })}
            ariaLabel="Job Board Scouting"
          />
        </SettingsField>

        <SettingsField
          label="Recruitment Email Inbox Monitoring"
          description="Read recruiter responses and parse interview invitations via IMAP/OAuth (Stage 36)."
        >
          <SettingsToggle
            checked={settings.email_integration_enabled}
            onCheckedChange={(checked) => onChange({ email_integration_enabled: checked })}
            ariaLabel="Email Monitoring"
          />
        </SettingsField>

        <SettingsField
          label="Telegram Notification & Alert Bot"
          description="Dispatch real-time job alerts and interview invitations to your Telegram chat (Stage 36)."
        >
          <SettingsToggle
            checked={settings.telegram_integration_enabled}
            onCheckedChange={(checked) => onChange({ telegram_integration_enabled: checked })}
            ariaLabel="Telegram Integration"
          />
        </SettingsField>

        <SettingsField
          label="WhatsApp Recruiter Messaging"
          description="Automate WhatsApp follow-ups with corporate recruiters and hiring managers (Stage 36)."
        >
          <SettingsToggle
            checked={settings.whatsapp_integration_enabled}
            onCheckedChange={(checked) => onChange({ whatsapp_integration_enabled: checked })}
            ariaLabel="WhatsApp Integration"
          />
        </SettingsField>
      </SettingsSection>

      <SettingsSection
        title="Model Context Protocol (MCP) Servers"
        description="External tool servers providing specialized capabilities to autonomous agents."
      >
        <div className="space-y-3">
          {settings.mcp_servers.map((server) => (
            <div
              key={server.server_id}
              className="p-3.5 rounded-lg border border-border/50 bg-secondary/20 space-y-2.5"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Boxes className="h-4 w-4 text-primary" />
                  <span className="text-xs font-semibold text-foreground">{server.name}</span>
                  <Badge variant="outline" className="text-[10px] font-mono">
                    {server.transport.toUpperCase()}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={server.trusted ? 'success' : 'neutral'} className="text-[10px]">
                    {server.trusted ? 'Trusted' : 'Untrusted'}
                  </Badge>
                  <SettingsToggle
                    checked={server.enabled}
                    onCheckedChange={(checked) => handleMCPServerToggle(server.server_id, checked)}
                    ariaLabel={`Enable ${server.name}`}
                  />
                </div>
              </div>

              <div>
                <span className="text-[11px] text-muted-foreground">
                  Execution Command / Endpoint:
                </span>
                <div className="mt-0.5 p-1.5 rounded bg-card border border-border/40 font-mono text-xs text-foreground truncate">
                  {server.command_or_url}
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-1.5 pt-1">
                <span className="text-[11px] text-muted-foreground mr-1">Allowed Tools:</span>
                {server.allowed_tools.map((tool) => (
                  <Badge key={tool} variant="neutral" className="text-[10px] font-mono">
                    {tool}
                  </Badge>
                ))}
              </div>
            </div>
          ))}
        </div>
      </SettingsSection>

      <SettingsSection
        title="Configured Credential References (Windows DPAPI Vault)"
        description="Sensitive API tokens and OAuth secrets stored securely at rest."
      >
        {isLoadingCreds ? (
          <div className="text-xs text-muted-foreground py-2">Loading credential references...</div>
        ) : credentials.length === 0 ? (
          <div className="p-4 rounded-lg border border-border/30 bg-card/20 text-center">
            <p className="text-xs text-muted-foreground">
              No third-party credentials currently stored. Configure providers in Security &
              Privacy.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {credentials.map((cred) => (
              <div
                key={cred.provider}
                className="p-2.5 rounded-md border border-border/40 bg-card/40 flex items-center justify-between text-xs"
              >
                <div className="flex items-center gap-2.5">
                  <Key className="h-4 w-4 text-cyan" />
                  <span className="font-semibold text-foreground">{cred.provider}</span>
                  <Badge variant="cyan" className="text-[10px]">
                    {cred.credential_type}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="success" className="text-[10px]">
                    Configured (DPAPI Encrypted)
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        )}
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
