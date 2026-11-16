/**
 * Data contracts and response types for Stage 09 Workspace Modules.
 */

export interface JobListingItem {
  id: string;
  source_id: string;
  external_id: string;
  company: string;
  title: string;
  location: string | null;
  employment_type: string | null;
  work_arrangement: string | null;
  salary_range: string | null;
  description: string | null;
  requirements: string | null;
  application_url: string;
  discovered_at: string;
  last_verified_at: string | null;
  status: string;
}

export interface JobListResponse {
  items: JobListingItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface ApplicationAttemptItem {
  id: string;
  application_id: string;
  attempted_at: string;
  execution_status: string;
  failure_category: string | null;
  error_summary: string | null;
  retry_eligible: boolean;
  idempotency_key: string;
}

export interface ApplicationItem {
  id: string;
  job_id: string;
  profile_id: string;
  resume_version_id: string | null;
  status: string;
  submitted_at: string | null;
  updated_at: string;
  confirmation_ref: string | null;
  notes: string | null;
  authorization_ref: string | null;
  company: string | null;
  job_title: string | null;
  attempts: ApplicationAttemptItem[];
}

export interface ApplicationListResponse {
  items: ApplicationItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface ArtifactItem {
  id: string;
  artifact_type: string;
  storage_path: string;
  file_size: number;
  checksum: string;
  related_task_id: string | null;
  related_profile_id: string | null;
  related_application_id: string | null;
  retention_class: string;
  created_at: string;
}

export interface ArtifactListResponse {
  items: ArtifactItem[];
  total: number;
  limit: number;
  offset: number;
}
