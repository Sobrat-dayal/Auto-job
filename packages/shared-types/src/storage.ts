/**
 * Storage, Database Diagnostics, and Backup Manifest types.
 */

export interface StorageStatus {
  database_exists: boolean;
  database_size_bytes: number;
  wal_size_bytes: number;
  shm_size_bytes: number;
  artifacts_size_bytes: number;
  backups_size_bytes: number;
  total_backups_count: number;
  disk_free_bytes: number;
  disk_total_bytes: number;
  latest_backup: BackupManifest | null;
}

export interface StorageHealth {
  integrity_check_passed: boolean;
  integrity_details: string[];
  foreign_keys_passed: boolean;
  foreign_key_violations: Array<Record<string, unknown>>;
}

export interface BackupManifest {
  backup_id: string;
  filename: string;
  created_at: string;
  app_version: string;
  file_size_bytes: number;
  sha256_checksum: string;
  integrity_check_passed: boolean;
  integrity_message: string;
}

export interface RestoreResponse {
  restored: boolean;
  backup_source: string;
  target_database: string;
  pre_restore_safety_backup: string | null;
  integrity_verified: boolean;
  timestamp: string;
}

export interface CredentialStatus {
  id?: string;
  provider: string;
  credential_type: string;
  status: string;
  is_configured: boolean;
  created_at?: string;
  last_validated_at?: string | null;
}

export interface ProfileSummary {
  id: string;
  profile_name: string;
  summary: string | null;
  has_contact_info: boolean;
  updated_at: string;
}
