import React, { useEffect, useState } from 'react';
import type { SecurityPrivacySettings, CredentialStatus } from '@autonom/shared-types';
import { apiClient } from '@/lib/api-client';
import { Key, Eye, EyeOff, Plus, Trash2, ShieldCheck } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  SettingsSection,
  SettingsField,
  SettingsToggle,
  SettingsConfirmationDialog,
  SettingsSaveBar,
} from '../components';

interface SecuritySettingsPageProps {
  settings: SecurityPrivacySettings;
  isDirty: boolean;
  isSaving: boolean;
  saveSuccess?: boolean;
  errorMessage?: string | null;
  onChange: (updated: Partial<SecurityPrivacySettings>) => void;
  onSave: () => void;
  onReset: () => void;
}

export const SecuritySettingsPage: React.FC<SecuritySettingsPageProps> = ({
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
  const [addCredModalOpen, setAddCredModalOpen] = useState(false);
  const [newProvider, setNewProvider] = useState('');
  const [newSecret, setNewSecret] = useState('');
  const [showSecret, setShowSecret] = useState(false);
  const [isSubmittingCred, setIsSubmittingCred] = useState(false);
  const [credToDelete, setCredToDelete] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const fetchCredentials = async () => {
    setIsLoadingCreds(true);
    try {
      const list = await apiClient.getCredentialStatus();
      setCredentials(list);
    } catch {
      // Backend offline or error
    } finally {
      setIsLoadingCreds(false);
    }
  };

  useEffect(() => {
    fetchCredentials();
  }, []);

  const handleSaveCredential = async () => {
    if (!newProvider.trim() || !newSecret.trim()) return;
    setIsSubmittingCred(true);
    try {
      await apiClient.storeCredential(newProvider.trim().toLowerCase(), newSecret.trim());
      setActionMessage(
        `Credential for '${newProvider}' securely encrypted in Windows DPAPI vault.`
      );
      setNewProvider('');
      setNewSecret('');
      setShowSecret(false);
      setAddCredModalOpen(false);
      await fetchCredentials();
    } catch (err) {
      setActionMessage(err instanceof Error ? err.message : 'Failed to store credential');
    } finally {
      setIsSubmittingCred(false);
    }
  };

  const handleConfirmDeleteCredential = async () => {
    if (!credToDelete) return;
    try {
      await apiClient.deleteCredential(credToDelete);
      setActionMessage(`Credential for '${credToDelete}' revoked and deleted from vault.`);
      setCredToDelete(null);
      await fetchCredentials();
    } catch (err) {
      setActionMessage(err instanceof Error ? err.message : 'Failed to delete credential');
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
        title="Windows DPAPI Keystore & Vault Health"
        description="Credentials are encrypted at rest using Windows Data Protection API (DPAPI) user-scope key wrapping."
        headerAction={
          <Button
            variant="primary"
            size="sm"
            onClick={() => setAddCredModalOpen(true)}
            className="h-7 text-xs px-2.5 gap-1.5"
          >
            <Plus className="h-3 w-3" />
            <span>Store Credential</span>
          </Button>
        }
      >
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
          <div className="p-3 rounded-lg border border-border/40 bg-card/40">
            <span className="text-[10px] text-muted-foreground uppercase font-semibold">
              Vault Engine
            </span>
            <div className="text-sm font-bold text-foreground mt-0.5 flex items-center gap-1.5">
              <ShieldCheck className="h-4 w-4 text-cyan" />
              <span>Windows DPAPI</span>
            </div>
            <span className="text-[10px] text-muted-foreground">User-Scope Bound</span>
          </div>

          <div className="p-3 rounded-lg border border-border/40 bg-card/40">
            <span className="text-[10px] text-muted-foreground uppercase font-semibold">
              Encryption Algorithm
            </span>
            <div className="text-sm font-bold text-foreground mt-0.5 font-mono">AES-256-GCM</div>
            <span className="text-[10px] text-muted-foreground">Authenticated Cipher</span>
          </div>

          <div className="p-3 rounded-lg border border-border/40 bg-card/40">
            <span className="text-[10px] text-muted-foreground uppercase font-semibold">
              Configured Secrets
            </span>
            <div className="text-sm font-bold text-foreground mt-0.5 font-mono">
              {credentials.length} stored
            </div>
            <span className="text-[10px] text-muted-foreground">Zero Plaintext in UI/Logs</span>
          </div>
        </div>

        <div className="space-y-2">
          {isLoadingCreds ? (
            <p className="text-xs text-muted-foreground">Loading credentials...</p>
          ) : credentials.length === 0 ? (
            <p className="text-xs text-muted-foreground italic">
              No credentials stored in local vault.
            </p>
          ) : (
            credentials.map((cred) => (
              <div
                key={cred.provider}
                className="p-3 rounded-lg border border-border/40 bg-card/40 flex items-center justify-between text-xs"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <Key className="h-3.5 w-3.5 text-cyan" />
                    <span className="font-semibold text-foreground uppercase">{cred.provider}</span>
                    <Badge variant="cyan" className="text-[10px]">
                      {cred.credential_type}
                    </Badge>
                  </div>
                  <div className="text-[11px] text-muted-foreground mt-0.5">
                    Added:{' '}
                    {cred.created_at ? new Date(cred.created_at).toLocaleDateString() : 'Active'}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="font-mono text-muted-foreground text-[11px]">
                    ••••••••••••••••
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setCredToDelete(cred.provider)}
                    className="h-7 w-7 p-0 text-muted-foreground hover:text-rose-400"
                    title={`Delete credential for ${cred.provider}`}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>
      </SettingsSection>

      <SettingsSection
        title="Privacy Architecture & Telemetry Protection"
        description="Local-first data sovereignty. External network traffic is strictly opt-in."
      >
        <SettingsField
          label="Strict Local-First Mode"
          description="Enforces zero network transmission unless explicit external provider (OpenAI, Anthropic, ATS portal) is configured."
        >
          <SettingsToggle
            checked={settings.local_first_strict_mode}
            onCheckedChange={(checked) => onChange({ local_first_strict_mode: checked })}
            ariaLabel="Strict Local-First Mode"
          />
        </SettingsField>

        <SettingsField
          label="Redact Sensitive Secrets in Logs"
          description="Strict regex redaction replacing API keys, bearer tokens, and session cookies with [REDACTED]."
        >
          <SettingsToggle
            checked={settings.redact_secrets_in_logs}
            onCheckedChange={(checked) => onChange({ redact_secrets_in_logs: checked })}
            ariaLabel="Redact Secrets in Logs"
          />
        </SettingsField>

        <SettingsField
          label="Security Audit Logging Granularity"
          description="Define detail level for tamper-evident activity events stored in SQLite."
        >
          <select
            value={settings.audit_logging_level}
            onChange={(e) =>
              onChange({
                audit_logging_level: e.target
                  .value as SecurityPrivacySettings['audit_logging_level'],
              })
            }
            className="h-8 rounded-md border border-input bg-card px-2.5 py-1 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            aria-label="Security Audit Logging Granularity"
          >
            <option value="all_actions">All Actions (Full Operations & Settings Audit)</option>
            <option value="sensitive_only">Sensitive Only (Credentials & Permissions)</option>
            <option value="security_only">Security Only (Auth & Vault Access Only)</option>
          </select>
        </SettingsField>
      </SettingsSection>

      {/* Add Credential Modal Dialog */}
      <Dialog open={addCredModalOpen} onOpenChange={setAddCredModalOpen}>
        <DialogContent className="max-w-md bg-card border-border shadow-xl">
          <DialogHeader>
            <DialogTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
              <Key className="h-4 w-4 text-cyan" />
              <span>Store Secret in Windows DPAPI Vault</span>
            </DialogTitle>
            <DialogDescription className="text-xs text-muted-foreground">
              Secrets are encrypted using Windows DPAPI key wrapping and stored in local SQLite.
              They are never transmitted or exposed in plain text.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-3 py-2 text-xs">
            <div>
              <label className="text-xs font-medium text-foreground">
                Provider or Service Name
              </label>
              <input
                type="text"
                placeholder="e.g. openai, anthropic, greenhouse, linkedin"
                value={newProvider}
                onChange={(e) => setNewProvider(e.target.value)}
                className="mt-1 w-full h-8 rounded border border-input bg-card px-2.5 text-xs text-foreground font-mono focus:outline-hidden focus:ring-1 focus:ring-primary"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-foreground">
                Secret Value (API Key or Token)
              </label>
              <div className="relative mt-1">
                <input
                  type={showSecret ? 'text' : 'password'}
                  placeholder="Paste API key or secret token"
                  value={newSecret}
                  onChange={(e) => setNewSecret(e.target.value)}
                  className="w-full h-8 rounded border border-input bg-card pl-2.5 pr-8 text-xs text-foreground font-mono focus:outline-hidden focus:ring-1 focus:ring-primary"
                />
                <button
                  type="button"
                  onClick={() => setShowSecret(!showSecret)}
                  className="absolute right-2 top-2 text-muted-foreground hover:text-foreground"
                >
                  {showSecret ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
          </div>

          <DialogFooter className="mt-2 gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setAddCredModalOpen(false)}
              className="text-xs h-8"
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleSaveCredential}
              disabled={isSubmittingCred || !newProvider.trim() || !newSecret.trim()}
              className="text-xs h-8"
            >
              {isSubmittingCred ? 'Encrypting...' : 'Encrypt & Save'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Confirm Delete Dialog */}
      <SettingsConfirmationDialog
        open={!!credToDelete}
        onOpenChange={(open) => !open && setCredToDelete(null)}
        title="Revoke and Delete Credential"
        description={`Are you sure you want to delete the credential for '${credToDelete}'? Any agents relying on this service will immediately lose authorization.`}
        confirmLabel="Confirm & Delete Credential"
        variant="destructive"
        onConfirm={handleConfirmDeleteCredential}
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
