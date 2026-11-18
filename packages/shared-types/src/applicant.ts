/**
 * Stage 21: Applicant Identity & Verified Professional Profile Shared Types.
 */

export type ClaimVerificationStatus =
  | 'unverified'
  | 'user_reported'
  | 'user_confirmed'
  | 'evidence_supported'
  | 'externally_verified'
  | 'conflicted'
  | 'superseded'
  | 'rejected';

export type ClaimCategory =
  | 'identity'
  | 'contact'
  | 'location'
  | 'eligibility'
  | 'education'
  | 'employment'
  | 'skill'
  | 'project'
  | 'certification'
  | 'publication'
  | 'award'
  | 'link';

export type SkillProficiency = 'beginner' | 'intermediate' | 'advanced' | 'expert';

export type CandidateStatus = 'extracted' | 'accepted' | 'rejected' | 'modified';

export type ImportJobStatus = 'pending' | 'parsing' | 'extracting' | 'ready_for_review' | 'completed' | 'failed';

export interface ContactInfo {
  legal_name?: string | null;
  preferred_name?: string | null;
  primary_email?: string | null;
  phone_number?: string | null;
  linkedin_url?: string | null;
  github_url?: string | null;
  portfolio_url?: string | null;
  custom_links?: Record<string, string>;
  is_verified?: boolean;
}

export interface LocationInfo {
  city?: string | null;
  state_or_province?: string | null;
  postal_code?: string | null;
  country?: string | null;
  timezone?: string | null;
  is_remote_open?: boolean;
  willing_to_relocate?: boolean;
  relocation_preferences?: string[];
}

export interface EmploymentEligibility {
  citizenship_country?: string | null;
  work_authorization_status?: string | null;
  requires_sponsorship?: boolean;
  security_clearance?: string | null;
  notice_period_days?: number | null;
  available_start_date?: string | null;
}

export interface EducationRecord {
  id: string;
  institution: string;
  degree: string;
  field_of_study: string;
  start_date?: string | null;
  end_date?: string | null;
  is_current?: boolean;
  gpa?: string | null;
  honors?: string[];
  activities?: string[];
  claim_id?: string | null;
}

export interface AchievementItem {
  id: string;
  description: string;
  metric?: string | null;
  impact?: string | null;
  evidence_ids?: string[];
}

export interface EmploymentRecord {
  id: string;
  employer: string;
  job_title: string;
  employment_type?: string | null;
  location?: string | null;
  is_remote?: boolean;
  start_date?: string | null;
  end_date?: string | null;
  is_current?: boolean;
  summary?: string | null;
  achievements?: AchievementItem[];
  technologies_used?: string[];
  claim_id?: string | null;
}

export interface SkillItem {
  id: string;
  name: string;
  canonical_name: string;
  category: 'technical' | 'soft' | 'domain' | 'language' | 'tool' | 'framework' | 'other';
  proficiency?: SkillProficiency;
  years_experience?: number | null;
  last_used_year?: number | null;
  is_primary?: boolean;
  claim_id?: string | null;
  evidence_count?: number;
}

export interface ProjectRecord {
  id: string;
  title: string;
  role?: string | null;
  summary?: string | null;
  organization?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  is_ongoing?: boolean;
  repository_url?: string | null;
  demo_url?: string | null;
  technologies?: string[];
  highlights?: string[];
  claim_id?: string | null;
}

export interface CertificationRecord {
  id: string;
  name: string;
  issuing_organization: string;
  issue_date?: string | null;
  expiration_date?: string | null;
  does_not_expire?: boolean;
  credential_id?: string | null;
  credential_url?: string | null;
  claim_id?: string | null;
}

export interface EvidenceMetadata {
  id: string;
  profile_id: string;
  filename: string;
  storage_path: string;
  content_hash_sha256: string;
  file_size_bytes: number;
  mime_type: string;
  document_type: string;
  tags?: string[];
  linked_claims?: string[];
  uploaded_at: string;
}

export interface ApplicantClaim {
  id: string;
  profile_id: string;
  category: ClaimCategory;
  field_path: string;
  claimed_value: any;
  status: ClaimVerificationStatus;
  evidence_ids?: string[];
  provenance_source?: string;
  confidence_score: number;
  user_review_notes?: string | null;
  created_at: string;
  updated_at: string;
  verified_at?: string | null;
}

export interface ProfileConflict {
  id: string;
  profile_id: string;
  field_path: string;
  category: ClaimCategory;
  claim_a_id: string;
  claim_a_value: any;
  claim_b_id: string;
  claim_b_value: any;
  detected_at: string;
  resolved: boolean;
  resolution_strategy?: string | null;
  chosen_claim_id?: string | null;
  manual_resolved_value?: any;
  resolution_rationale?: string | null;
  resolved_at?: string | null;
}

export interface ExtractionCandidate {
  id: string;
  category: ClaimCategory;
  field_name: string;
  extracted_value: any;
  raw_text_snippet?: string;
  confidence: number;
  status: CandidateStatus;
  existing_canonical_value?: any;
  duplicate_flag?: boolean;
}

export interface ImportJob {
  id: string;
  profile_id: string;
  filename: string;
  file_hash_sha256: string;
  status: ImportJobStatus;
  total_candidates: number;
  reviewed_count: number;
  accepted_count: number;
  rejected_count: number;
  candidates: ExtractionCandidate[];
  error_message?: string | null;
  created_at: string;
  completed_at?: string | null;
}

export interface DataQualityIssue {
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  field_path: string;
  message: string;
  recommendation?: string;
}

export interface DataQualityReport {
  profile_id: string;
  overall_score: number; // 0-100
  completeness_score: number; // 0-100
  consistency_score: number; // 0-100
  evidence_coverage_score: number; // 0-100
  readiness_status: 'incomplete' | 'ready_for_review' | 'verified_for_agents' | 'comprehensive';
  total_claims: number;
  verified_claims: number;
  conflicted_claims: number;
  unverified_claims: number;
  issues: DataQualityIssue[];
  evaluated_at: string;
}

export interface ProfileSnapshot {
  profile_id: string;
  version: number;
  target_agent: string;
  authorized_scopes: string[];
  filtered_data: Record<string, any>;
  generated_at: string;
}

export interface ProfileVersionRecord {
  id: string;
  profile_id: string;
  version: number;
  changed_by: string;
  change_reason?: string | null;
  modified_fields: string[];
  created_at: string;
}

export interface ApplicantProfile {
  id: string;
  owner_id: string;
  display_label: string;
  status: string;
  version: number;
  contact?: ContactInfo | null;
  location?: LocationInfo | null;
  eligibility?: EmploymentEligibility | null;
  education: EducationRecord[];
  employment: EmploymentRecord[];
  skills: SkillItem[];
  projects: ProjectRecord[];
  certifications: CertificationRecord[];
  publications?: any[];
  awards?: any[];
  custom_sections?: Record<string, any>;
  created_at: string;
  updated_at: string;
}
