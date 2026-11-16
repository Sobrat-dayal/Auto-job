import React, { useEffect, useState } from 'react';
import type {
  StorageSettings,
  StorageStatus,
  StorageHealth,
  BackupManifest,
} from '@autonom/shared-types';
import { apiClient } from '@/lib/api-client';
import { RefreshCw, Archive, RotateCcw, ShieldCheck } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  SettingsSection,
  SettingsField,
  SettingsToggle,
  SettingsConfirmationDialog,
  SettingsSaveBar,
} from '../components';

interface StorageSettingsPageProps {
  settings: StorageSettings;
  isDirty: boolean;
  isSaving: boolean;
  saveSuccess?: boolean;
  errorMessage?: string | null;
  onChange: (updated: Partial<StorageSettings>) => void;
  onSave: () => void;
  onReset: () => void;
}

export const StorageSettingsPage: React.FC<StorageSettingsPageProps> = ({
  settings,
  isDirty,
  isSaving,
  saveSuccess,
  errorMessage,
  onChange,
  onSave,
  onReset,
}) => {
  const [status, setStatus] = useState<StorageStatus | null>(null);
  const [health, setHealth] = useState<StorageHealth | null>(null);
  const [backups, setBackups] = useState<BackupManifest[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isBackingUp, setIsBackingUp] = useState(false);
  const [restoreConfirmFile, setRestoreConfirmFile] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const fetchStorageData = async () => {
    setIsLoading(true);
    try {
      const [sData, hData, bData] = await Promise.all([
        apiClient.getStorageStatus(),
        apiClient.getStorageHealth(),
        apiClient.listBackups(),
      ]);
      setStatus(sData);
      setHealth(hData);
      setBackups(bData);
    } catch {
      // Backend offline or error
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStorageData();
  }, []);

  const handleCreateBackup = async () => {
    setIsBackingUp(true);
    setActionMessage('Creating online database snapshot...');
    try {
      const manifest = await apiClient.createBackup();
      setActionMessage(`Backup created successfully: ${manifest.filename}`);
      await fetchStorageData();
    } catch (err) {
      setActionMessage(err instanceof Error ? err.message : 'Backup failed');
    } finally {
      setIsBackingUp(false);
    }
  };

  const handleConfirmRestore = async () => {
    if (!restoreConfirmFile) return;
    setActionMessage(`Restoring database from ${restoreConfirmFile}...`);
    try {
      const result = await apiClient.restoreBackup(restoreConfirmFile);
      setActionMessage(
        `Restored successfully from ${result.backup_source}. Safety backup created.`
      );
      setRestoreConfirmFile(null);
      await fetchStorageData();
    } catch (err) {
      setActionMessage(err instanceof Error ? err.message : 'Restore failed');
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
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
        title="SQLite Storage Status & Health"
        description="Local storage utilization across relational tables, write-ahead logs (WAL), and file artifacts."
        headerAction={
          <Button
            variant="outline"
            size="sm"
            onClick={fetchStorageData}
            disabled={isLoading}
            className="h-7 text-xs px-2.5 gap-1.5"
          >
            <RefreshCw className={`h-3 w-3 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </Button>
        }
      >
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 rounded-lg border border-border/40 bg-card/40">
            <span className="text-[10px] text-muted-foreground uppercase font-semibold">
              Database Size
            </span>
            <div className="text-base font-bold text-foreground mt-0.5">
              {status ? formatBytes(status.database_size_bytes) : '—'}
            </div>
            <span className="text-[10px] text-muted-foreground">SQLite WAL Mode</span>
          </div>

          <div className="p-3 rounded-lg border border-border/40 bg-card/40">
            <span className="text-[10px] text-muted-foreground uppercase font-semibold">
              WAL Log Size
            </span>
            <div className="text-base font-bold text-foreground mt-0.5">
              {status ? formatBytes(status.wal_size_bytes) : '—'}
            </div>
            <span className="text-[10px] text-muted-foreground">Transient Journal</span>
          </div>

          <div className="p-3 rounded-lg border border-border/40 bg-card/40">
            <span className="text-[10px] text-muted-foreground uppercase font-semibold">
              Artifact Storage
            </span>
            <div className="text-base font-bold text-foreground mt-0.5">
              {status ? formatBytes(status.artifacts_size_bytes) : '—'}
            </div>
            <span className="text-[10px] text-muted-foreground">Resumes & Briefs</span>
          </div>

          <div className="p-3 rounded-lg border border-border/40 bg-card/40">
            <span className="text-[10px] text-muted-foreground uppercase font-semibold">
              Integrity Status
            </span>
            <div className="text-base font-bold text-emerald-400 mt-0.5 flex items-center gap-1.5">
              <ShieldCheck className="h-4 w-4" />
              <span>{health?.integrity_check_passed ? 'Healthy' : 'Verifying...'}</span>
            </div>
            <span className="text-[10px] text-muted-foreground">PRAGMA Integrity Check</span>
          </div>
        </div>
      </SettingsSection>

      <SettingsSection
        title="Backup Management & Retention Rules"
        description="Configure automated database snapshot limits and disk cleanup."
        headerAction={
          <Button
            variant="primary"
            size="sm"
            onClick={handleCreateBackup}
            disabled={isBackingUp}
            className="h-7 text-xs px-2.5 gap-1.5"
          >
            <Archive className="h-3 w-3" />
            <span>{isBackingUp ? 'Creating...' : 'Create Backup Snapshot'}</span>
          </Button>
        }
      >
        <SettingsField
          label="Database Backup Retention Count"
          description="Number of past database backup snapshots to preserve before rotating oldest out."
        >
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={3}
              max={50}
              value={settings.backup_retention_count}
              onChange={(e) =>
                onChange({ backup_retention_count: parseInt(e.target.value, 10) || 10 })
              }
              className="h-8 w-20 rounded-md border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
              aria-label="Backup Retention Count"
            />
            <span className="text-xs text-muted-foreground font-mono">backups</span>
          </div>
        </SettingsField>

        <SettingsField
          label="Auto-Backup on Application Launch"
          description="Create a consistent online SQLite snapshot whenever the desktop shell starts up."
        >
          <SettingsToggle
            checked={settings.auto_backup_on_startup}
            onCheckedChange={(checked) => onChange({ auto_backup_on_startup: checked })}
            ariaLabel="Auto-Backup on Startup"
          />
        </SettingsField>

        <SettingsField
          label="Automatic Incremental Vacuum"
          description="Periodically reclaim unused pages and shrink WAL files in the background."
        >
          <SettingsToggle
            checked={settings.auto_vacuum_enabled}
            onCheckedChange={(checked) => onChange({ auto_vacuum_enabled: checked })}
            ariaLabel="Automatic Incremental Vacuum"
          />
        </SettingsField>

        <SettingsField
          label="Artifact Disk Storage Quota"
          description="Maximum disk capacity allocated to tailored PDF resumes, covers, and analytical files."
        >
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={512}
              max={20480}
              step={256}
              value={settings.artifact_storage_limit_mb}
              onChange={(e) =>
                onChange({ artifact_storage_limit_mb: parseInt(e.target.value, 10) || 2048 })
              }
              className="h-8 w-24 rounded-md border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
              aria-label="Artifact Storage Quota"
            />
            <span className="text-xs text-muted-foreground font-mono">MB</span>
          </div>
        </SettingsField>
      </SettingsSection>

      <SettingsSection
        title="Available Database Backups"
        description="Online snapshots available for instant point-in-time restoration."
      >
        {backups.length === 0 ? (
          <p className="text-xs text-muted-foreground italic">
            No backups found in local backups directory.
          </p>
        ) : (
          <div className="space-y-2">
            {backups.map((b) => (
              <div
                key={b.backup_id}
                className="p-3 rounded-lg border border-border/40 bg-card/40 flex items-center justify-between gap-4 text-xs"
              >
                <div>
                  <div className="font-semibold text-foreground font-mono">{b.filename}</div>
                  <div className="text-[11px] text-muted-foreground mt-0.5 flex items-center gap-3">
                    <span>Size: {formatBytes(b.file_size_bytes)}</span>
                    <span>Created: {new Date(b.created_at).toLocaleString()}</span>
                  </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setRestoreConfirmFile(b.filename)}
                  className="h-7 text-xs border-amber-500/30 text-amber-300 hover:bg-amber-500/10 gap-1.5"
                >
                  <RotateCcw className="h-3 w-3" />
                  <span>Restore</span>
                </Button>
              </div>
            ))}
          </div>
        )}
      </SettingsSection>

      <SettingsConfirmationDialog
        open={!!restoreConfirmFile}
        onOpenChange={(open) => !open && setRestoreConfirmFile(null)}
        title="Confirm Database Restoration"
        description={`Restoring '${restoreConfirmFile}' will replace the current active SQLite database. An automated pre-restore safety snapshot will be created before applying. Do you want to proceed?`}
        confirmLabel="Confirm & Restore Database"
        variant="destructive"
        onConfirm={handleConfirmRestore}
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
