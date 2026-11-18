/**
 * AUTONOM Recruitment Writing & Application Intelligence Shared Types (Stage 24)
 */

export type CoverLetterType =
  | 'general'
  | 'role_specific'
  | 'internship'
  | 'experienced'
  | 'research'
  | 'short';

export type WritingTone =
  | 'professional'
  | 'concise'
  | 'formal'
  | 'friendly_professional'
  | 'technical'
  | 'research_focused'
  | 'early_career'
  | 'executive';

export type WritingLength =
  | 'short'
  | 'standard'
  | 'detailed'
  | 'custom';

export type WritingDocumentStatus =
  | 'draft'
  | 'generating'
  | 'needs_review'
  | 'validating'
  | 'approved'
  | 'published'
  | 'archived'
  | 'failed';

export type QuestionCategory =
  | 'contact'
  | 'education'
  | 'experience'
  | 'skills'
  | 'projects'
  | 'work_eligibility'
  | 'availability'
  | 'compensation'
  | 'motivation'
  | 'behavioral'
  | 'technical'
  | 'portfolio'
  | 'references'
  | 'sensitive_disclosure'
  | 'attestation'
  | 'unknown';

export type AnswerType =
  | 'free_text'
  | 'short_text'
  | 'paragraph'
  | 'numeric'
  | 'date'
  | 'boolean'
  | 'single_choice'
  | 'multiple_choice'
  | 'dropdown'
  | 'multi_part'
  | 'conditional';

export type AnswerState =
  | 'available_confirmed'
  | 'available_evidence_supported'
  | 'available_user_reported'
  | 'draft_generated'
  | 'requires_user_confirmation'
  | 'requires_user_attestation'
  | 'missing_information'
  | 'conflicting_information'
  | 'sensitive_optional'
  | 'not_applicable'
  | 'unsupported'
  | 'rejected'
  | 'approved';

export type AnswerFreshnessStatus =
  | 'fresh'
  | 'outdated'
  | 'superseded'
  | 'requires_revalidation';

export type WritingPackageStatus =
  | 'created'
  | 'gathering_context'
  | 'generating'
  | 'needs_review'
  | 'incomplete'
  | 'validating'
  | 'ready_for_approval'
  | 'approved'
  | 'archived'
  | 'failed';

export interface WritingSourceReference {
  source_entity_id: string;
  source_type: 'claim' | 'education' | 'experience' | 'project' | 'skill' | 'github_repo' | 'resume_bullet';
  claim_id?: string | null;
  verification_status: string;
  attribution_text?: string | null;
  evidence_url?: string | null;
}

export interface CoverLetterContentBlock {
  id: string;
  block_type: 'header' | 'salutation' | 'opening' | 'qualifications' | 'evidence_example' | 'motivation' | 'closing' | 'signature';
  title?: string | null;
  text: string;
  ordering: number;
  source_refs: WritingSourceReference[];
  word_count: number;
  is_user_edited: boolean;
}

export interface CoverLetterDocument {
  id: string;
  owner_id: string;
  profile_id: string;
  profile_snapshot_id: string;
  resume_id?: string | null;
  resume_version?: number | null;
  title: string;
  letter_type: CoverLetterType;
  target_role: string;
  employer_name?: string | null;
  job_description_raw?: string | null;
  template_id: string;
  tone: WritingTone;
  length_preference: WritingLength;
  max_words?: number | null;
  recipient_name?: string | null;
  recipient_title?: string | null;
  recipient_organization?: string | null;
  recipient_address?: string | null;
  status: WritingDocumentStatus;
  current_version: number;
  content_hash: string;
  blocks: CoverLetterContentBlock[];
  created_at: string;
  updated_at: string;
  approved_at?: string | null;
}

export interface CoverLetterTemplateDefinition {
  id: string;
  name: string;
  description: string;
  category: string;
  version: string;
  primary_font: string;
  heading_font: string;
  base_font_size_pt: number;
  heading_font_size_pt: number;
  margin_top_in: number;
  margin_bottom_in: number;
  margin_left_in: number;
  margin_right_in: number;
  primary_color: string;
  accent_color: string;
  text_color: string;
  line_spacing: number;
  layout_style: 'classic' | 'modern' | 'compact' | 'academic' | 'technical';
}

export interface CoverLetterVersionRecord {
  id: string;
  cover_letter_id: string;
  version_number: number;
  profile_snapshot_id: string;
  content_hash: string;
  changelog: string;
  created_at: string;
  actor_id: string;
  is_published: boolean;
  document_snapshot: Record<string, any>;
  export_artifact_ids: string[];
}

export interface ApplicationQuestionRecord {
  id: string;
  set_id: string;
  exact_question_text: string;
  question_text?: string;
  normalized_question: string;
  category: QuestionCategory;
  answer_type: AnswerType;
  is_required: boolean;
  allowed_options: string[];
  max_characters?: number | null;
  max_words?: number | null;
  min_numeric_value?: number | null;
  max_numeric_value?: number | null;
  numeric_unit?: string | null;
  conditional_parent_id?: string | null;
  conditional_trigger_value?: string | null;
  is_sensitive: boolean;
  requires_attestation: boolean;
  current_answer?: ApplicationAnswer | null;
}

export interface ApplicationAnswer {
  id: string;
  question_id: string;
  profile_id: string;
  profile_version: number;
  answer_text: string;
  numeric_value?: number | null;
  boolean_value?: boolean | null;
  date_value?: string | null;
  selected_options: string[];
  state: AnswerState;
  freshness_status: AnswerFreshnessStatus;
  source_refs: WritingSourceReference[];
  confidence_score: number;
  is_user_overridden: boolean;
  user_attestation_timestamp?: string | null;
  user_attestation_actor?: string | null;
  validation_issues: string[];
  created_at: string;
  updated_at: string;
}

export interface ApplicationQuestionSet {
  id: string;
  owner_id: string;
  job_title: string;
  employer?: string | null;
  job_description_id?: string | null;
  title: string;
  questions: ApplicationQuestionRecord[];
  created_at: string;
  updated_at: string;
}

export interface AnswerLibraryEntry {
  id: string;
  owner_id: string;
  title: string;
  category: QuestionCategory;
  parameterized_template: string;
  sample_resolved_text: string;
  answer_type: AnswerType;
  applicable_technologies: string[];
  associated_project_ids: string[];
  state: 'candidate' | 'draft' | 'needs_review' | 'approved' | 'outdated' | 'deprecated';
  version_number: number;
  reuse_count: number;
  last_used_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface MissingInformationItem {
  id: string;
  question_id: string;
  question_text: string;
  required_field: string;
  field_description: string;
  is_mandatory: boolean;
  suggested_profile_destination?: string | null;
  user_input_provided?: string | null;
  resolved: boolean;
}

export interface SensitiveDecisionItem {
  id: string;
  question_id: string;
  question_text: string;
  category: 'work_authorization' | 'visa_sponsorship' | 'compensation_expectation' | 'voluntary_disclosure' | 'legal_attestation';
  allowed_choices: string[];
  is_voluntary: boolean;
  user_decision?: string | null;
  attestation_accepted: boolean;
  decided_at?: string | null;
}

export interface ConflictItem {
  id: string;
  title: string;
  description: string;
  source_a: string;
  source_b: string;
  claim_a_value: string;
  claim_b_value: string;
  resolved: boolean;
  resolution_note?: string | null;
}

export interface ApplicationWritingPackage {
  id: string;
  owner_id: string;
  target_job_title: string;
  target_employer: string;
  job_description_raw?: string | null;
  profile_snapshot_id: string;
  resume_id?: string | null;
  resume_version?: number | null;
  cover_letter_id?: string | null;
  cover_letter_version?: number | null;
  question_set_id?: string | null;
  status: WritingPackageStatus;
  version_number: number;
  total_questions: number;
  answered_questions: number;
  pending_sensitive_decisions: number;
  pending_attestations: number;
  missing_information_count: number;
  conflicts_count: number;
  is_ready_for_approval: boolean;
  approved_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface WritingOverviewStats {
  total_cover_letters: number;
  approved_cover_letters: number;
  total_question_sets: number;
  total_screening_questions: number;
  approved_library_answers: number;
  pending_reviews: number;
  missing_info_count: number;
  sensitive_decisions_count: number;
  writing_packages_count: number;
}

export interface CoverLetterCreateRequest {
  title: string;
  target_role: string;
  employer_name?: string | null;
  job_description_raw?: string | null;
  letter_type?: CoverLetterType;
  template_id?: string;
  tone?: WritingTone;
  length_preference?: WritingLength;
  max_words?: number | null;
  recipient_name?: string | null;
  recipient_organization?: string | null;
}

export interface CoverLetterUpdateRequest {
  title?: string;
  target_role?: string;
  employer_name?: string | null;
  job_description_raw?: string | null;
  template_id?: string;
  tone?: WritingTone;
  length_preference?: WritingLength;
  letter_type?: CoverLetterType;
  recipient_name?: string | null;
  blocks?: CoverLetterContentBlock[];
}

export interface CoverLetterGenerateRequest {
  target_role: string;
  employer_name?: string | null;
  job_description_raw?: string | null;
  letter_type?: CoverLetterType;
  tone?: WritingTone;
  template_id?: string;
  length_preference?: WritingLength;
}

export interface CoverLetterExportRequest {
  format: 'pdf' | 'docx' | 'txt' | 'markdown';
  output_filename?: string;
}

export interface ParagraphRewriteRequest {
  paragraph_id: string;
  instructions?: string;
  instruction?: string;
  tone?: WritingTone;
}

export interface QuestionParseRequest {
  raw_text: string;
  employer_name?: string;
  target_role?: string;
}

export interface QuestionSetCreateRequest {
  title: string;
  target_employer?: string | null;
  employer?: string | null;
  target_role?: string | null;
  job_title?: string | null;
  raw_text?: string | null;
  questions?: Partial<ApplicationQuestionRecord>[];
}

export interface AnswerUpdateRequest {
  answer_text: string;
  selected_options?: string[];
  numeric_value?: number | null;
  boolean_value?: boolean | null;
  state?: AnswerState;
}

export interface AnswerLibraryCreateRequest {
  title?: string;
  category: QuestionCategory;
  question_pattern?: string;
  normalized_prompt?: string;
  approved_answer_text?: string;
  parameterized_template?: string;
  answer_type?: AnswerType;
  tags?: string[];
}

export interface AnswerLibraryUpdateRequest {
  approved_answer_text?: string;
  question_pattern?: string;
  category?: QuestionCategory;
  tags?: string[];
}

export interface AnswerReusePreviewRequest {
  question_id?: string;
  library_entry_id?: string;
  target_employer?: string;
  target_role?: string;
}

export interface UserAttestationRequest {
  decision_id?: string;
  decision_item_id?: string;
  attestation_text?: string;
  selected_choice?: string;
  accepted_attestation?: boolean;
  agreed?: boolean;
}

export interface WritingPackageCreateRequest {
  target_job_title: string;
  target_employer: string;
  job_description_raw?: string | null;
  resume_id?: string | null;
  cover_letter_id?: string | null;
  question_set_id?: string | null;
}

