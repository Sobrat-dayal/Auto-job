/**
 * AUTONOM 24-Agent Catalog & Role Definitions
 */

export type AgentId =
  // Core Coordination (1-5)
  | 'supervisor-01'
  | 'planning-01'
  | 'task-router-01'
  | 'verification-01'
  | 'recovery-01'
  // Job Automation (6-11)
  | 'job-discovery-01'
  | 'job-matching-01'
  | 'resume-tailor-01'
  | 'application-01'
  | 'recruitment-comm-01'
  | 'interview-prep-01'
  // Computer Automation (12-15)
  | 'browser-01'
  | 'windows-computer-01'
  | 'visual-grounding-01'
  | 'structural-ui-01'
  // General-Purpose (16-24)
  | 'coding-01'
  | 'research-01'
  | 'document-01'
  | 'spreadsheet-01'
  | 'presentation-01'
  | 'creative-3d-01'
  | 'messaging-01'
  | 'market-intelligence-01'
  | 'workflow-automation-01';

export type AgentTier = 'coordination' | 'recruitment' | 'computer_use' | 'general_purpose';

export type AgentStatus =
  'idle' | 'planning' | 'executing' | 'verifying' | 'awaiting_approval' | 'paused' | 'error';

export interface AgentDescriptor {
  id: AgentId;
  name: string;
  role: string;
  tier: AgentTier;
  status: AgentStatus;
  currentTaskId: string | null;
  tasksCompleted: number;
  model: string;
  allowedTools: string[];
}
