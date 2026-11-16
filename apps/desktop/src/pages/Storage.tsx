import React, { useEffect, useState } from 'react';
import {
  Database,
  HardDrive,
  CheckCircle2,
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
    <div className="p-6 space-y-6 max-w-6xl mx-auto overflow-y-auto">
      {/* Header Banner */}
      <div className="border-b border-border pb-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <span>Storage & Database Diagnostics</span>
            <span className="text-xs px-2 py-0.5 rounded bg-primary/20 text-primary-light border border-primary/30 font-mono font-normal">
              Stage 04 Active
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            SQLite WAL persistence, Windows DPAPI credential protection, online snapshots, and
            verified restoration.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start md:self-auto">
          <button
            onClick={handleCreateBackup}
            disabled={isBackingUp}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-primary hover:bg-primary-hover text-white text-xs font-medium transition-colors disabled:opacity-50"
          >
            <Archive className={`w-3.5 h-3.5 ${isBackingUp ? 'animate-bounce' : ''}`} />
            <span>{isBackingUp ? 'Backing Up...' : 'Create Backup'}</span>
          </button>

          <button
            onClick={fetchStorageData}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-surface-elevated hover:bg-slate-700 text-slate-200 text-xs font-medium border border-border transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-cyan' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {actionMessage && (
        <div className="p-3 rounded bg-surface-elevated border border-primary/30 text-xs font-mono text-cyan flex items-center justify-between">
          <span>{actionMessage}</span>
          <button
            onClick={() => setActionMessage(null)}
            className="text-slate-400 hover:text-white"
          >
            ✕
          </button>
        </div>
      )}

      {/* Storage Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-lg bg-surface border border-border">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Database className="w-4 h-4 text-primary-light" />
            Database File
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-xl font-bold font-mono text-slate-100">
              {formatBytes(status?.database_size_bytes ?? 0)}
            </span>
          </div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">
            WAL: {formatBytes(status?.wal_size_bytes ?? 0)}
          </div>
        </div>

        <div className="p-4 rounded-lg bg-surface border border-border">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <FolderArchive className="w-4 h-4 text-cyan" />
            Artifacts Vault
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-xl font-bold font-mono text-slate-100">
              {formatBytes(status?.artifacts_size_bytes ?? 0)}
            </span>
          </div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">Resumes, PDFs & documents</div>
        </div>

        <div className="p-4 rounded-lg bg-surface border border-border">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Archive className="w-4 h-4 text-emerald-400" />
            Backup Snapshots
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-xl font-bold font-mono text-slate-100">
              {status?.total_backups_count ?? 0}
            </span>
            <span className="text-xs text-slate-400 font-mono">retained</span>
          </div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">
            Size: {formatBytes(status?.backups_size_bytes ?? 0)}
          </div>
        </div>

        <div className="p-4 rounded-lg bg-surface border border-border">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <HardDrive className="w-4 h-4 text-amber-400" />
            Free Disk Space
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-xl font-bold font-mono text-slate-100">
              {formatBytes(status?.disk_free_bytes ?? 0)}
            </span>
          </div>
          <div className="text-[11px] text-slate-400 font-mono mt-1">
            of {formatBytes(status?.disk_total_bytes ?? 0)}
          </div>
        </div>
      </div>

      {/* Integrity & Encryption Badges */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 rounded-lg bg-surface border border-border space-y-3">
          <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <FileCheck className="w-4 h-4 text-emerald-400" />
            SQLite Database Integrity
          </span>
          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between items-center p-2 rounded bg-surface-elevated">
              <span className="text-slate-400">PRAGMA integrity_check:</span>
              {health?.integrity_check_passed ? (
                <span className="text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> PASSED
                </span>
              ) : (
                <span className="text-rose-400 flex items-center gap-1">
                  <AlertTriangle className="w-3.5 h-3.5" /> FAILED
                </span>
              )}
            </div>
            <div className="flex justify-between items-center p-2 rounded bg-surface-elevated">
              <span className="text-slate-400">PRAGMA foreign_key_check:</span>
              {health?.foreign_keys_passed ? (
                <span className="text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> ENFORCED (0 Violations)
                </span>
              ) : (
                <span className="text-rose-400 flex items-center gap-1">
                  <AlertTriangle className="w-3.5 h-3.5" /> VIOLATIONS DETECTED
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="p-4 rounded-lg bg-surface border border-border space-y-3">
          <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Shield className="w-4 h-4 text-primary-light" />
            Cryptographic Vault & Protection
          </span>
          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between items-center p-2 rounded bg-surface-elevated">
              <span className="text-slate-400">Key Protection:</span>
              <span className="text-emerald-400">Windows DPAPI (CryptProtectData)</span>
            </div>
            <div className="flex justify-between items-center p-2 rounded bg-surface-elevated">
              <span className="text-slate-400">Field Encryption:</span>
              <span className="text-cyan">AES-256-GCM Authenticated</span>
            </div>
          </div>
        </div>
      </div>

      {/* Online Backups Table */}
      <div className="p-4 rounded-lg bg-surface border border-border space-y-3">
        <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <Archive className="w-4 h-4 text-emerald-400" />
          Available Backups ({backups.length})
        </span>

        <div className="overflow-x-auto max-h-56 overflow-y-auto font-mono text-xs border border-border rounded bg-surface-elevated">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-border bg-slate-800/50 text-slate-400 text-[11px]">
                <th className="p-2">Filename</th>
                <th className="p-2">Timestamp</th>
                <th className="p-2">Size</th>
                <th className="p-2">SHA256 Checksum</th>
                <th className="p-2">Integrity</th>
                <th className="p-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {backups.length > 0 ? (
                backups.map((b) => (
                  <tr
                    key={b.backup_id}
                    className="border-b border-border/50 hover:bg-slate-800/30 text-[11px]"
                  >
                    <td className="p-2 text-slate-200 whitespace-nowrap">{b.filename}</td>
                    <td className="p-2 text-slate-400 whitespace-nowrap">
                      {new Date(b.created_at).toLocaleString()}
                    </td>
                    <td className="p-2 text-slate-300 whitespace-nowrap">
                      {formatBytes(b.file_size_bytes)}
                    </td>
                    <td className="p-2 text-slate-400 font-mono text-[10px] truncate max-w-xs">
                      {b.sha256_checksum.slice(0, 16)}...
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {b.integrity_check_passed ? 'VERIFIED' : 'FAILED'}
                      </span>
                    </td>
                    <td className="p-2 text-right whitespace-nowrap">
                      <button
                        onClick={() => setRestoreConfirmFile(b.filename)}
                        className="px-2 py-1 rounded bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px] font-medium"
                      >
                        Restore
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="p-4 text-center text-slate-500 text-xs">
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
      {restoreConfirmFile && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-surface border border-rose-500/40 rounded-lg p-5 max-w-md w-full space-y-4">
            <div className="flex items-center gap-2 text-rose-400 font-bold text-sm">
              <AlertTriangle className="w-5 h-5" />
              <span>Confirm Database Restoration</span>
            </div>
            <p className="text-xs text-slate-300">
              Restoring from <strong className="text-white">{restoreConfirmFile}</strong> will
              replace the active database. A pre-restore safety snapshot will be taken automatically
              before replacing data.
            </p>
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setRestoreConfirmFile(null)}
                className="px-3 py-1.5 rounded bg-surface-elevated text-slate-300 text-xs border border-border"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmRestore}
                className="px-3 py-1.5 rounded bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold flex items-center gap-1.5"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Authorize & Restore</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Credential Status Summary Table */}
      <div className="p-4 rounded-lg bg-surface border border-border space-y-3">
        <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <Key className="w-4 h-4 text-primary-light" />
          Configured Integration Credentials ({credentials.length})
        </span>

        <div className="overflow-x-auto max-h-48 overflow-y-auto font-mono text-xs border border-border rounded bg-surface-elevated">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-border bg-slate-800/50 text-slate-400 text-[11px]">
                <th className="p-2">Provider</th>
                <th className="p-2">Type</th>
                <th className="p-2">Security Status</th>
                <th className="p-2">Storage Layer</th>
              </tr>
            </thead>
            <tbody>
              {credentials.length > 0 ? (
                credentials.map((c) => (
                  <tr
                    key={c.provider}
                    className="border-b border-border/50 hover:bg-slate-800/30 text-[11px]"
                  >
                    <td className="p-2 text-slate-200 font-semibold">{c.provider}</td>
                    <td className="p-2 text-slate-400">{c.credential_type}</td>
                    <td className="p-2 text-emerald-400">
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 border border-emerald-500/20">
                        {c.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="p-2 text-slate-400">Windows DPAPI Encrypted</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="p-4 text-center text-slate-500 text-xs">
                    No third-party credentials configured yet. Secrets stored here are protected
                    with Windows DPAPI.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
