/**
 * Flagship Career & Job Automation Domain Models
 */

export interface ApplicantProfile {
  id: string;
  fullName: string;
  email: string;
  phone: string | null;
  locationCity: string;
  locationState: string | null;
  locationCountry: string;
  linkedinUrl: string | null;
  githubUrl: string | null;
  portfolioUrl: string | null;
  targetJobTitles: string[];
  targetMinSalary: number | null;
  targetCurrency: string;
  workAuthorizationStatus: 'US_CITIZEN' | 'GREEN_CARD' | 'NEEDS_VISA' | 'OTHER';
  isActivelySearching: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface VerifiedSkill {
  id: string;
  profileId: string;
  name: string;
  category: 'LANGUAGE' | 'FRAMEWORK' | 'DATABASE' | 'TOOL' | 'METHODOLOGY' | 'SOFT_SKILL';
  yearsExperience: number;
  proficiencyLevel: 'EXPERT' | 'PROFICIENT' | 'FAMILIAR';
  lastUsedYear: number;
  verifiedByUser: boolean;
}

export interface ProjectEvidence {
  id: string;
  profileId: string;
  title: string;
  organization: string;
  roleTitle: string;
  startDate: string;
  endDate: string | null;
  bulletPoints: string[];
  verifiedMetrics: Record<string, string> | null;
  codeRepositoryUrl: string | null;
  liveUrl: string | null;
}

export interface ResumeVersion {
  id: string;
  profileId: string;
  versionName: string;
  targetRoleType: string | null;
  fileFormat: 'PDF' | 'DOCX' | 'MARKDOWN';
  filePath: string;
  fileHashSha256: string;
  contentAstJson: Record<string, unknown>;
  isBaseTemplate: boolean;
  createdAt: string;
}

export interface JobSource {
  id: string;
  name: string;
  sourceType: 'AGGREGATOR' | 'ATS_DIRECT' | 'CAREER_SITE';
  baseUrl: string;
  isEnabled: boolean;
  rateLimitPerMinute: number;
  lastScrapedAt: string | null;
  consecutiveFailures: number;
}

export interface JobListing {
  id: string;
  sourceId: string;
  externalJobId: string | null;
  title: string;
  companyName: string;
  locationRaw: string;
  remoteType: 'REMOTE' | 'HYBRID' | 'ONSITE';
  salaryMin: number | null;
  salaryMax: number | null;
  salaryCurrency: string;
  applyUrl: string;
  atsPlatform: 'Greenhouse' | 'Lever' | 'Workday' | 'iCIMS' | 'Unknown';
  descriptionText: string;
  rawHtmlPath: string | null;
  postedDate: string | null;
  discoveredAt: string;
  isActive: boolean;
}

export interface JobMatch {
  id: string;
  profileId: string;
  jobId: string;
  overallScore: number;
  skillsScore: number;
  experienceScore: number;
  seniorityScore: number;
  compensationScore: number;
  matchingSkills: string[];
  missingSkills: string[];
  gapAnalysisSummary: string;
  recommendedAction: 'APPLY_NOW' | 'TAILOR_FIRST' | 'SKIP_NOT_ELIGIBLE';
  evaluatedAt: string;
}

export type ApplicationStatus =
  | 'QUEUED'
  | 'TAILORING'
  | 'READY_TO_SUBMIT'
  | 'PENDING_APPROVAL'
  | 'SUBMITTING'
  | 'SUBMITTED'
  | 'UNDER_REVIEW'
  | 'INTERVIEWING'
  | 'OFFER_EXTENDED'
  | 'REJECTED'
  | 'WITHDRAWN';

export interface Application {
  id: string;
  profileId: string;
  jobId: string;
  resumeVersionId: string | null;
  currentStatus: ApplicationStatus;
  submissionMode: 'MANUAL' | 'AUTONOMOUS_APPROVED' | 'AUTONOMOUS_FULL';
  appliedAt: string | null;
  portalUsername: string | null;
  lastStatusCheck: string | null;
  notes: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface ApplicationAttempt {
  id: string;
  applicationId: string;
  attemptNumber: number;
  startedAt: string;
  endedAt: string | null;
  outcome: 'SUCCESS' | 'FAILED_VERIFICATION' | 'BLOCKED_CAPTCHA' | 'TIMED_OUT';
  receiptScreenshotPath: string | null;
  errorMessage: string | null;
  sessionRecordingPath: string | null;
}

export interface ScreeningAnswer {
  id: string;
  profileId: string;
  questionPattern: string;
  questionExample: string;
  answerText: string;
  isSensitive: boolean;
  approvedByUser: boolean;
  lastUsedAt: string | null;
}

export interface RecruiterConversation {
  id: string;
  applicationId: string;
  recruiterName: string | null;
  recruiterEmail: string;
  channel: 'EMAIL' | 'LINKEDIN' | 'SMS';
  subject: string | null;
  lastMessageSnippet: string | null;
  sentiment: 'POSITIVE' | 'NEUTRAL' | 'REJECTION' | null;
  nextActionDue: string | null;
  updatedAt: string;
}

export interface Interview {
  id: string;
  applicationId: string;
  stageName: 'RECRUITER_SCREEN' | 'TECHNICAL_1' | 'SYSTEM_DESIGN' | 'BEHAVIORAL' | 'ONSITE';
  scheduledAt: string;
  durationMinutes: number;
  meetingUrl: string | null;
  interviewerNames: string | null;
  dossierPath: string | null;
  status: 'SCHEDULED' | 'COMPLETED' | 'CANCELLED' | 'RESCHEDULED';
}
