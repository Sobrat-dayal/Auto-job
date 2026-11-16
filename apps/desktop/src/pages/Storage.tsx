import React, { useEffect, useState } from 'react';
import {
  Database,
  HardDrive,
  AlertTriangle,
  RefreshCw,
  Archive,
  RotateCcw,
  Shield,
  Key,
  FolderArchive,
  FileCheck,
} from 'lucide-react';
import type {
  BackupManifest,
  CredentialStatus,
  StorageHealth,
  StorageStatus,
} from '@autonom/shared-types';
import { apiClient } from '@/lib/api-client';
import { PageContainer } from '@/components/layout/PageContainer';
import { SectionHeader } from '@/components/layout/SectionHeader';
import { MetricCard } from '@/components/data-display/MetricCard';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

export const Storage: React.FC = () => {
  const [status, setStatus] = useState<StorageStatus | null>(null);
  const [health, setHealth] = useState<StorageHealth | null>(null);
  const [backups, setBackups] = useState<BackupManifest[]>([]);
  const [credentials, setCredentials] = useState<CredentialStatus[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isBackingUp, setIsBackingUp] = useState<boolean>(false);
  const [restoreConfirmFile, setRestoreConfirmFile] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const fetchStorageData = async () => {
    setIsLoading(true);
    try {
      const [sData, hData, bData, cData] = await Promise.all([
        apiClient.getStorageStatus(),
        apiClient.getStorageHealth(),
        apiClient.listBackups(),
        apiClient.getCredentialStatus(),
      ]);
      setStatus(sData);
      setHealth(hData);
      setBackups(bData);
      setCredentials(cData);
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
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  return (
    <PageContainer
      title="Storage & Database Diagnostics"
      subtitle="SQLite WAL persistence, Windows DPAPI credential protection, online snapshots, and verified restoration"
      badge={
        <Badge variant="primary" dot>
          Stage 04 Active
        </Badge>
      }
      actions={
        <div className="flex items-center gap-2">
          <Button
            variant="primary"
            size="sm"
            onClick={handleCreateBackup}
            disabled={isBackingUp}
            isLoading={isBackingUp}
            loadingText="Backing Up..."
          >
            <Archive className="w-3.5 h-3.5 mr-1.5" />
            Create Backup
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={fetchStorageData}
            disabled={isLoading}
            isLoading={isLoading}
            loadingText="Refreshing..."
          >
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
            Refresh
          </Button>
        </div>
      }
    >
      {actionMessage && (
        <div className="p-3 rounded-lg bg-surface border border-primary/40 text-xs font-mono-tech text-cyan flex items-center justify-between">
          <span>{actionMessage}</span>
          <button
            onClick={() => setActionMessage(null)}
            className="text-foreground-muted hover:text-foreground p-1"
            aria-label="Dismiss message"
          >
            ✕
          </button>
        </div>
      )}

      {/* Storage Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3.5">
        <MetricCard
          title="Database File"
          value={formatBytes(status?.database_size_bytes ?? 0)}
          subtitle={`WAL: ${formatBytes(status?.wal_size_bytes ?? 0)}`}
          icon={<Database className="w-4 h-4" />}
          variant="primary"
        />

        <MetricCard
          title="Artifacts Vault"
          value={formatBytes(status?.artifacts_size_bytes ?? 0)}
          subtitle="Resumes, PDFs & documents"
          icon={<FolderArchive className="w-4 h-4" />}
          variant="cyan"
        />

        <MetricCard
          title="Backup Snapshots"
          value={status?.total_backups_count ?? 0}
          subtitle={`Total: ${formatBytes(status?.backups_size_bytes ?? 0)}`}
          icon={<Archive className="w-4 h-4" />}
          variant="success"
        />

        <MetricCard
          title="Free Disk Space"
          value={formatBytes(status?.disk_free_bytes ?? 0)}
          subtitle={`of ${formatBytes(status?.disk_total_bytes ?? 0)}`}
          icon={<HardDrive className="w-4 h-4" />}
          variant="default"
        />
      </div>

      {/* Integrity & Encryption Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 rounded-lg bg-surface border border-border space-y-3">
          <SectionHeader
            title="SQLite Database Integrity"
            subtitle="Verified via PRAGMA runtime probes"
            icon={<FileCheck className="w-4 h-4 text-status-success" />}
          />
          <div className="space-y-2 text-xs font-mono-tech">
            <div className="flex justify-between items-center p-2.5 rounded bg-surface-elevated border border-border/40">
              <span className="text-foreground-secondary">PRAGMA integrity_check:</span>
              {health?.integrity_check_passed ? (
                <Badge variant="success" dot>
                  PASSED
                </Badge>
              ) : (
                <Badge variant="error" dot>
                  FAILED
                </Badge>
              )}
            </div>
            <div className="flex justify-between items-center p-2.5 rounded bg-surface-elevated border border-border/40">
              <span className="text-foreground-secondary">PRAGMA foreign_key_check:</span>
              {health?.foreign_keys_passed ? (
                <Badge variant="success" dot>
                  ENFORCED (0 Violations)
                </Badge>
              ) : (
                <Badge variant="error" dot>
                  VIOLATIONS DETECTED
                </Badge>
              )}
            </div>
          </div>
        </div>

        <div className="p-4 rounded-lg bg-surface border border-border space-y-3">
          <SectionHeader
            title="Cryptographic Vault & Protection"
            subtitle="Hardware-backed OS keystore binding"
            icon={<Shield className="w-4 h-4 text-primary" />}
          />
          <div className="space-y-2 text-xs font-mono-tech">
            <div className="flex justify-between items-center p-2.5 rounded bg-surface-elevated border border-border/40">
              <span className="text-foreground-secondary">Key Protection:</span>
              <span className="text-status-success font-semibold">
                Windows DPAPI (CryptProtectData)
              </span>
            </div>
            <div className="flex justify-between items-center p-2.5 rounded bg-surface-elevated border border-border/40">
              <span className="text-foreground-secondary">Field Encryption:</span>
              <span className="text-cyan font-semibold">AES-256-GCM Authenticated</span>
            </div>
          </div>
        </div>
      </div>

      {/* Online Backups Table */}
      <div className="p-4 rounded-lg bg-surface border border-border space-y-3">
        <SectionHeader
          title={`Available Backups (${backups.length})`}
          subtitle="Point-in-time snapshots with SHA256 integrity digests"
          icon={<Archive className="w-4 h-4 text-cyan" />}
        />

        <div className="overflow-x-auto max-h-56 overflow-y-auto font-mono-tech text-xs border border-border rounded-md bg-surface-elevated">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-border bg-surface-secondary/60 text-foreground-muted text-[11px]">
                <th className="p-2.5">Filename</th>
                <th className="p-2.5">Timestamp</th>
                <th className="p-2.5">Size</th>
                <th className="p-2.5">SHA256 Checksum</th>
                <th className="p-2.5">Integrity</th>
                <th className="p-2.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {backups.length > 0 ? (
                backups.map((b) => (
                  <tr
                    key={b.backup_id}
                    className="border-b border-border/40 hover:bg-surface-hover text-[11px] transition-colors"
                  >
                    <td className="p-2.5 text-foreground font-semibold whitespace-nowrap">
                      {b.filename}
                    </td>
                    <td className="p-2.5 text-foreground-muted whitespace-nowrap">
                      {new Date(b.created_at).toLocaleString()}
                    </td>
                    <td className="p-2.5 text-foreground-secondary whitespace-nowrap">
                      {formatBytes(b.file_size_bytes)}
                    </td>
                    <td className="p-2.5 text-foreground-muted font-mono-tech text-[10px] truncate max-w-xs">
                      {b.sha256_checksum.slice(0, 16)}...
                    </td>
                    <td className="p-2.5 whitespace-nowrap">
                      <Badge
                        variant={b.integrity_check_passed ? 'success' : 'error'}
                        className="text-[10px] py-0 px-1.5"
                      >
                        {b.integrity_check_passed ? 'VERIFIED' : 'FAILED'}
                      </Badge>
                    </td>
                    <td className="p-2.5 text-right whitespace-nowrap">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setRestoreConfirmFile(b.filename)}
                        className="text-[11px] h-6 px-2 text-status-warning border-status-warning/40 hover:bg-status-warning/15"
                      >
                        Restore
                      </Button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="p-4 text-center text-foreground-muted text-xs">
                    No database backups found. Click &quot;Create Backup&quot; to generate an
                    on-demand snapshot.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Restore Confirmation Dialog Modal */}
      <Dialog
        open={Boolean(restoreConfirmFile)}
        onOpenChange={(open) => !open && setRestoreConfirmFile(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-status-error">
              <AlertTriangle className="w-5 h-5" />
              Confirm Database Restoration
            </DialogTitle>
            <DialogDescription>
              Restoring from <strong className="text-foreground">{restoreConfirmFile}</strong> will
              replace the active database. A pre-restore safety snapshot will be taken automatically
              before replacing data.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setRestoreConfirmFile(null)}>
              Cancel
            </Button>
            <Button variant="destructive" size="sm" onClick={handleConfirmRestore}>
              <RotateCcw className="w-3.5 h-3.5 mr-1.5" />
              Authorize & Restore
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Credential Status Summary Table */}
      <div className="p-4 rounded-lg bg-surface border border-border space-y-3">
        <SectionHeader
          title={`Configured Integration Credentials (${credentials.length})`}
          subtitle="Protected at rest using Windows Data Protection API (DPAPI)"
          icon={<Key className="w-4 h-4 text-primary" />}
        />

        <div className="overflow-x-auto max-h-48 overflow-y-auto font-mono-tech text-xs border border-border rounded-md bg-surface-elevated">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-border bg-surface-secondary/60 text-foreground-muted text-[11px]">
                <th className="p-2.5">Provider</th>
                <th className="p-2.5">Type</th>
                <th className="p-2.5">Security Status</th>
                <th className="p-2.5">Storage Layer</th>
              </tr>
            </thead>
            <tbody>
              {credentials.length > 0 ? (
                credentials.map((c) => (
                  <tr
                    key={c.provider}
                    className="border-b border-border/40 hover:bg-surface-hover text-[11px] transition-colors"
                  >
                    <td className="p-2.5 text-foreground font-semibold">{c.provider}</td>
                    <td className="p-2.5 text-foreground-secondary">{c.credential_type}</td>
                    <td className="p-2.5">
                      <Badge variant="success" className="text-[10px] py-0 px-1.5 font-mono-tech">
                        {c.status.toUpperCase()}
                      </Badge>
                    </td>
                    <td className="p-2.5 text-foreground-muted">Windows DPAPI Encrypted</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="p-4 text-center text-foreground-muted text-xs">
                    No third-party credentials configured yet. Secrets stored here are protected
                    with Windows DPAPI.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </PageContainer>
  );
};
