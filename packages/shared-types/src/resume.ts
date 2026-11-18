/**
 * Stage 23: Resume Intelligence & Professional Portfolio Shared Types.
 */

export type ResumeType =
  | 'master'
  | 'general'
  | 'job_tailored'
  | 'internship'
  | 'experienced'
  | 'academic'
  | 'minimalist';

export type DocumentStatus =
  | 'draft'
  | 'generating'
  | 'needs_review'
  | 'validating'
  | 'approved'
  | 'published'
  | 'archived'
  | 'failed';

export type PageFormat = 'letter' | 'a4';

export type SectionType =
  | 'header'
  | 'summary'
  | 'education'
  | 'experience'
  | 'internships'
  | 'skills'
  | 'projects'
  | 'research'
  | 'publications'
  | 'certifications'
  | 'awards'
  | 'leadership'
  | 'volunteering'
  | 'coursework'
  | 'custom';

export type RequirementMatchCategory =
  | 'directly_supported'
  | 'partially_supported'
  | 'related_experience'
  | 'not_evidenced'
  | 'requires_review';

export type ATSCheckStatus = 'pass' | 'warning' | 'error' | 'not_evaluated';

export type ExportFormat = 'docx' | 'pdf' | 'html' | 'json';

export type TemplateCategory =
  | 'ats_classic'
  | 'modern_professional'
  | 'technical_engineer'
  | 'internship_graduate'
  | 'academic_research'
  | 'minimalist';

export interface SourceFactReference {
  source_entity_id: string;
  claim_id?: string | null;
  verification_status: string;
  applicant_profile_version: number;
  evidence_id?: string | null;
  attribution_level?: string | null;
  source_excerpt?: string | null;
}

export interface ResumeEntry {
  id: string;
  entry_type: string;
  title: string;
  subtitle?: string | null;
  organization?: string | null;
  location?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  is_current: boolean;
  description?: string | null;
  bullet_points: string[];
  tags: string[];
  source_refs: SourceFactReference[];
  metrics: Record<string, any>;
  is_visible: boolean;
  ordering: number;
}

export interface ResumeSection {
  id: string;
  section_type: SectionType;
  display_title: string;
  ordering: number;
  is_visible: boolean;
  entries: ResumeEntry[];
  source_references: SourceFactReference[];
  validation_state: string;
}

export interface ResumeDocument {
  id: string;
  owner_id: string;
  profile_id: string;
  profile_snapshot_id: string;
  title: string;
  resume_type: ResumeType;
  target_role?: string | null;
  job_ref?: string | null;
  template_id: string;
  template_version: string;
  status: DocumentStatus;
  current_version: number;
  locale: string;
  page_format: PageFormat;
  max_pages: number;
  header_contact: Record<string, any>;
  sections: ResumeSection[];
  created_at: string;
  updated_at: string;
  approved_at?: string | null;
  approval_actor?: string | null;
}

export interface ResumeCreateRequest {
  profile_id?: string;
  title: string;
  resume_type?: ResumeType;
  target_role?: string | null;
  template_id?: string;
  page_format?: PageFormat;
  max_pages?: number;
  job_description_text?: string | null;
  selected_project_ids?: string[] | null;
  selected_skill_names?: string[] | null;
}

export interface ResumeUpdateRequest {
  title?: string | null;
  target_role?: string | null;
  template_id?: string | null;
  page_format?: PageFormat | null;
  max_pages?: number | null;
  status?: DocumentStatus | null;
  header_contact?: Record<string, any> | null;
  sections?: ResumeSection[] | null;
}

export interface ResumeVersionRecord {
  id: string;
  resume_id: string;
  version_number: number;
  profile_snapshot_id: string;
  job_ref?: string | null;
  template_id: string;
  template_version: string;
  content_hash: string;
  changelog: string;
  created_at: string;
  actor_id: string;
  is_published: boolean;
  document_snapshot: Record<string, any>;
  export_artifact_ids: string[];
}

export interface JobDescriptionSnapshot {
  id: string;
  owner_id: string;
  job_title: string;
  employer?: string | null;
  raw_text: string;
  required_skills: string[];
  preferred_skills: string[];
  experience_reqs: string[];
  education_reqs: string[];
  responsibilities: string[];
  tech_stack: string[];
  location?: string | null;
  work_arrangement?: string | null;
  source_url?: string | null;
  extracted_at: string;
}

export interface JobDescriptionParseRequest {
  raw_text: string;
  job_title?: string | null;
  employer?: string | null;
  source_url?: string | null;
}

export interface RequirementEvidenceMapping {
  requirement_id: string;
  requirement_text: string;
  is_required: boolean;
  claim_id?: string | null;
  claim_text?: string | null;
  match_category: RequirementMatchCategory;
  explanation: string;
  uncertainty: number;
}

export interface ResumeTailorRequest {
  resume_id: string;
  job_description_text?: string | null;
  job_id?: string | null;
  target_role?: string | null;
  generate_summary?: boolean;
  prioritize_skills?: boolean;
  prioritize_projects?: boolean;
}

export interface ATSCheckResult {
  check_name: string;
  status: ATSCheckStatus;
  observed_evidence: string;
  impact_explanation: string;
  suggested_remediation?: string | null;
  location?: string | null;
}

export interface ATSReadabilityReport {
  overall_status: ATSCheckStatus;
  passed_count: number;
  warning_count: number;
  error_count: number;
  checks: ATSCheckResult[];
  evaluated_at: string;
  document_id: string;
  format: string;
  notes: string;
}

export interface ResumeTemplateDefinition {
  id: string;
  name: string;
  description: string;
  category: TemplateCategory;
  version: string;
  supported_page_formats: PageFormat[];
  supported_sections: SectionType[];
  primary_font: string;
  heading_font: string;
  base_font_size_pt: number;
  heading_font_size_pt: number;
  title_font_size_pt: number;
  margin_top_in: number;
  margin_bottom_in: number;
  margin_left_in: number;
  margin_right_in: number;
  primary_color: string;
  accent_color: string;
  has_header_border: boolean;
  is_two_column: boolean;
  ats_friendly: boolean;
}

export interface ExportArtifact {
  export_id: string;
  resume_id: string;
  version_id: string;
  format: ExportFormat;
  filename: string;
  file_path: string;
  file_size_bytes: number;
  sha256_checksum: string;
  created_at: string;
  status: string;
  validation_result?: Record<string, any> | null;
}

export interface ResumeExportRequest {
  format: ExportFormat;
  output_directory?: string | null;
  custom_filename?: string | null;
  validate_extraction?: boolean;
}

export interface PortfolioProjectEntry {
  project_id: string;
  title: string;
  summary: string;
  problem_addressed?: string | null;
  tech_stack: string[];
  architecture_highlights: string[];
  individual_contribution: string;
  deliverables: string[];
  repo_url?: string | null;
  demo_url?: string | null;
  screenshot_path?: string | null;
  attribution_level: string;
  is_public_eligible: boolean;
  ordering: number;
}

export interface PortfolioDocument {
  id: string;
  owner_id: string;
  profile_id: string;
  title: string;
  professional_intro: string;
  selected_skills: string[];
  selected_projects: PortfolioProjectEntry[];
  publications: Record<string, any>[];
  certifications: Record<string, any>[];
  public_contact: Record<string, any>;
  template_id: string;
  created_at: string;
  updated_at: string;
  status: DocumentStatus;
}

export interface PortfolioCreateRequest {
  title?: string;
  professional_intro?: string | null;
  selected_project_ids?: string[] | null;
  selected_skills?: string[] | null;
  template_id?: string;
}

export interface PortfolioUpdateRequest {
  title?: string | null;
  professional_intro?: string | null;
  selected_skills?: string[] | null;
  selected_projects?: PortfolioProjectEntry[] | null;
  public_contact?: Record<string, any> | null;
  template_id?: string | null;
  status?: DocumentStatus | null;
}

export interface ResumeOverviewStats {
  total_resumes: number;
  draft_count: number;
  approved_count: number;
  master_resume_id?: string | null;
  master_resume_title?: string | null;
  recent_resumes: {
    id: string;
    title: string;
    type: string;
    status: string;
    updated_at: string;
  }[];
}
