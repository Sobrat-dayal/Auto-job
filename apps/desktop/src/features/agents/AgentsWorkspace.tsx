import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Bot,
  BrainCircuit,
  Cpu,
  Shield,
  Activity,
  CheckCircle2,
  Play,
  Save,
  Eye,
} from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleToolbar,
  ModuleTabs,
  ModuleDetailPanel,
  ModuleLoadingState,
  ModuleEmptyState,
} from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { apiClient } from '@/lib/api-client';
import type {
  AgentExecutionHistoryItem,
  WorkerListResponse,
  TaskResponse,
} from '@autonom/shared-types';

export interface LegacyAgentDefinition {
  id: string;
  name: string;
  category: string;
  role: string;
  description: string;
  model: string;
  stage: string;
  status: 'active' | 'idle' | 'unavailable' | 'operational' | 'limited' | 'planned';
  capabilities: string[];
  system_instructions?: string;
}

export const AGENT_REGISTRY: LegacyAgentDefinition[] = [
  // 1. Core Orchestration Agents (Stage 12 Active)
  {
    id: 'supervisor',
    name: 'Supervisor Agent',
    category: 'Orchestration',
    role: 'Workflow Coordinator & Governance Master',
    description:
      'Coordinates multi-agent workflows, manages lifecycle state transitions, preserves checkpoints, and enforces user controls.',
    model: 'Unified AI Gateway / Router',
    stage: 'Stage 12',
    status: 'active',
    capabilities: [
      'Workflow Lifecycle Management',
      'Checkpoint Preservation',
      'Pause/Resume/Cancel Control',
      'Crash State Reconciliation',
    ],
    system_instructions: 'Coordinate multi-agent execution plans, manage checkpoints, enforce user authorization.',
  },
  {
    id: 'planner',
    name: 'Planning Agent',
    category: 'Orchestration',
    role: 'Dynamic Workflow Planner',
    description:
      'Decomposes natural language goals into structured dependency DAGs, verifies cycle-free topology, and versions plans.',
    model: 'AI Gateway (Planning Mode)',
    stage: 'Stage 12',
    status: 'active',
    capabilities: [
      'Goal Interpretation & Decomposition',
      'DAG Graph Construction',
      'Fast Cycle Detection (Kahn Algo)',
      'Plan Versioning & Replanning',
    ],
    system_instructions: 'Decompose goals into deterministic DAGs using Kahn algorithm for cycle-free dependencies.',
  },
  {
    id: 'router',
    name: 'Task Router Agent',
    category: 'Orchestration',
    role: 'Capability Dispatcher',
    description:
      'Evaluates step requirements, matches capabilities, checks agent concurrency limits and hardware constraints with explainability.',
    model: 'Deterministic Capability Router',
    stage: 'Stage 12',
    status: 'active',
    capabilities: [
      'Capability-Based Matching',
      'Concurrency Slot Management',
      'Explainable Routing Decisions',
      'Fallback Agent Selection',
    ],
    system_instructions: 'Route steps to qualified agents respecting concurrency limits and hardware guardrails.',
  },
  {
    id: 'verifier',
    name: 'Verification Agent',
    category: 'Orchestration',
    role: 'Multi-Layer Quality Auditor',
    description:
      'Audits step execution outputs using deterministic schema/type assertions and semantic model evaluations.',
    model: 'Deterministic Validator + AI Review',
    stage: 'Stage 12',
    status: 'active',
    capabilities: [
      'Layer 1: Schema & Type Assertions',
      'Layer 2: Semantic Output Audit',
      'Four-State Verification Outcomes',
      'Audit Evidence Logging',
    ],
    system_instructions: 'Audit step execution outputs deterministically against JSON schemas and semantic contracts.',
  },
  {
    id: 'recovery',
    name: 'Recovery Agent',
    category: 'Orchestration',
    role: 'Fault Diagnostician & Healer',
    description:
      'Classifies failures across 13 normalized categories, executes bounded retries, and triggers dynamic replanning.',
    model: 'Diagnostic Classifier',
    stage: 'Stage 12',
    status: 'active',
    capabilities: [
      '13 Normalized Failure Classes',
      'Bounded Idempotent Retries',
      'Dynamic Plan Revision',
      'Safe Recovery Audit Logging',
    ],
    system_instructions: 'Diagnose errors, select recovery remediations, and prevent infinite retry loops.',
  },
  {
    id: 'capability_worker',
    name: 'Safe Capability Worker',
    category: 'Orchestration',
    role: 'Deterministic & AI Capability Executor',
    description:
      'Executes registered safe capabilities (text summarization, classification, structured extraction, comparison, transformation, validation, and code inspection).',
    model: 'Local / Cloud Hybrid Execution',
    stage: 'Stage 12',
    status: 'active',
    capabilities: [
      'Text Summarize & Classify',
      'Structured Entity Extract',
      'Text Diff & Compare',
      'Data Transform & Markdown Reports',
      'Deterministic Code AST Inspect',
    ],
    system_instructions: 'Execute discrete capability functions and return validated outputs.',
  },

  // 2. Recruitment Specialist Agents (Stage 13)
  {
    id: 'job_discovery_agent',
    name: 'Job Discovery Scout',
    category: 'Recruitment',
    role: 'Multi-Source Job Harvester',
    description: 'Interprets job search criteria, normalizes user-supplied job listings, and constructs search strategies.',
    model: 'Local Qwen 2.5 / Fast Router',
    stage: 'Stage 13 (Limited)',
    status: 'limited',
    capabilities: ['Normalize Job Listings', 'Parse Search Criteria', 'Schema Standardization'],
    system_instructions: 'Extract search criteria and normalize job postings into standard schema. Never claim live board searches without connectors.',
  },
  {
    id: 'job_matching_agent',
    name: 'Job Matching Agent',
    category: 'Recruitment',
    role: 'Requirement & Skill Match Analyst',
    description: 'Analyzes job requirements, matches against verified applicant skills, produces explainable alignment scores.',
    model: 'AI Gateway (Reasoning)',
    stage: 'Stage 13 (Operational)',
    status: 'operational',
    capabilities: ['Extract Job Requirements', 'Grounded Skill Matching', 'Alignment Scoring'],
    system_instructions: 'Identify hard/soft skills in jobs and match against verified applicant data. Never invent qualifications.',
  },
  {
    id: 'resume_agent',
    name: 'Resume Agent',
    category: 'Recruitment',
    role: 'Resume Customizer & Scribe',
    description: 'Drafts tailored resume bullet points and section suggestions strictly grounded in verified applicant experience.',
    model: 'AI Gateway (Writing)',
    stage: 'Stage 13 (Operational)',
    status: 'operational',
    capabilities: ['Grounded Resume Bullets', 'ATS Keyword Alignment', 'Experience Highlighting'],
    system_instructions: 'Draft resume achievements highlighting verified skills for the target role. Strictly prohibit fabricating facts.',
  },
  {
    id: 'application_agent',
    name: 'Application Agent',
    category: 'Recruitment',
    role: 'Application Form Specialist',
    description: 'Analyzes application question requirements, classifies input fields, drafts evidence-backed responses.',
    model: 'AI Gateway (General)',
    stage: 'Stage 13 (Limited)',
    status: 'limited',
    capabilities: ['Field Type Classification', 'Profile Field Mapping', 'Omission Detection'],
    system_instructions: 'Classify form fields and map to verified profile data. Do not execute browser submissions.',
  },
  {
    id: 'recruitment_comms_agent',
    name: 'Recruiter Outreach Scribe',
    category: 'Recruitment',
    role: 'Communications & Follow-Up Drafter',
    description: 'Summarizes recruiter conversations, extracts commitments/dates, and drafts professional communication replies.',
    model: 'AI Gateway (Writing)',
    stage: 'Stage 13 (Operational)',
    status: 'operational',
    capabilities: ['Thread Summarization', 'Commitment Extraction', 'Professional Reply Drafting'],
    system_instructions: 'Summarize recruiter interactions and draft polite professional responses. Do not send live emails.',
  },
  {
    id: 'interview_prep_agent',
    name: 'Interview Prep Coach',
    category: 'Recruitment',
    role: 'Mock Interviewer & Strategy Advisor',
    description: 'Generates tailored technical and behavioral interview preparation questions and study guides.',
    model: 'AI Gateway (Reasoning)',
    stage: 'Stage 13 (Operational)',
    status: 'operational',
    capabilities: ['Technical Question Generation', 'STAR Method Behavioral Mocks', 'Topic Study Plans'],
    system_instructions: 'Generate targeted technical and behavioral interview questions mapped to required skills.',
  },

  // 3. Computer Control Agents
  {
    id: 'visual_grounding_agent',
    name: 'Visual Grounding Agent',
    category: 'Computer Control',
    role: 'Screen Perception & OCR Specialist',
    description: 'Safely inspects image metadata and visual element coordinates without live desktop capture.',
    model: 'UI-TARS / Vision Gateway',
    stage: 'Stage 13 (Limited)',
    status: 'limited',
    capabilities: ['Image Metadata Inspection', 'Bounding Box Validation', 'Safe Format Check'],
    system_instructions: 'Analyze provided image files and bounding box metadata. Do not perform active screen capture.',
  },
  {
    id: 'structural_ui_agent',
    name: 'Windows UI Automation Driver',
    category: 'Computer Control',
    role: 'Accessibility Tree Operator',
    description: 'Parses structured accessibility/UI trees supplied as JSON data to locate actionable controls.',
    model: 'Native Windows Rust Bridge',
    stage: 'Stage 13 (Limited)',
    status: 'limited',
    capabilities: ['Accessibility Tree Parsing', 'Actionable Control Extraction', 'Element Focus Mapping'],
    system_instructions: 'Parse supplied accessibility node hierarchies. Live Windows UI Automation starts in Stage 17.',
  },
  {
    id: 'browser_agent',
    name: 'Autonomous Browser Navigator',
    category: 'Computer Control',
    role: 'Web Application Automator',
    description: 'Interprets browser task goals, plans navigation steps, and validates web automation prerequisites.',
    model: 'Playwright CDP + LLM',
    stage: 'Stage 16 (Planned)',
    status: 'planned',
    capabilities: ['Navigation Planning', 'Selector Strategy', 'Prerequisite Validation'],
    system_instructions: 'Plan browser navigation steps. Live browser execution arrives in Stage 16.',
  },
  {
    id: 'windows_computer_agent',
    name: 'Windows Computer Agent',
    category: 'Computer Control',
    role: 'Desktop OS Automation Specialist',
    description: 'Interprets desktop operation goals and prepares structured application action plans.',
    model: 'Native Windows Bridge',
    stage: 'Stage 17-18 (Planned)',
    status: 'planned',
    capabilities: ['Desktop Action Planning', 'Application Window Targeting'],
    system_instructions: 'Prepare desktop interaction plans. Live input simulation arrives in Stage 17/18.',
  },

  // 4. Development & Specialist Roles
  {
    id: 'coding_agent',
    name: 'Full-Stack Code Architect',
    category: 'Development',
    role: 'Software Engineer & Code Reviewer',
    description: 'Performs code explanation, static code review, bug identification, and test-case generation.',
    model: 'Claude 3.5 Sonnet / Local Coding LLM',
    stage: 'Stage 13 (Operational)',
    status: 'operational',
    capabilities: ['Code Explanation', 'Static Defect Review', 'Unit Test Generation', 'AST Inspection'],
    system_instructions: 'Analyze code, explain architecture, review bugs, and suggest unit tests. Do not execute code without authorization.',
  },
  {
    id: 'research_agent',
    name: 'Research Agent',
    category: 'Research',
    role: 'Information Synthesis Specialist',
    description: 'Synthesizes supplied reference documents, extracts grounded evidence, and compares source consensus.',
    model: 'AI Gateway (Reasoning)',
    stage: 'Stage 13 (Operational)',
    status: 'operational',
    capabilities: ['Source Summarization', 'Evidence Extraction', 'Consensus & Gap Comparison'],
    system_instructions: 'Analyze and compare supplied source documents. Strictly distinguish supplied citations from model reasoning.',
  },
  {
    id: 'document_agent',
    name: 'Document Agent',
    category: 'Productivity',
    role: 'Structured Technical Writing Specialist',
    description: 'Drafts structured documents, produces section outlines, and rewrites text for clarity and impact.',
    model: 'AI Gateway (Writing)',
    stage: 'Stage 13 (Operational)',
    status: 'operational',
    capabilities: ['Hierarchical Outline Generation', 'Multi-Section Report Drafting', 'Clarity & Tone Rewriting'],
    system_instructions: 'Produce well-structured written documents, outlines, and summaries following specified formatting.',
  },
  {
    id: 'spreadsheet_agent',
    name: 'Spreadsheet Agent',
    category: 'Productivity',
    role: 'Tabular Data & Formula Specialist',
    description: 'Analyzes tabular schemas, computes summary statistics deterministically, and explains formulas.',
    model: 'Deterministic Engine + LLM',
    stage: 'Stage 13 (Operational)',
    status: 'operational',
    capabilities: ['Tabular Schema Analysis', 'Summary Metric Aggregation', 'Formula Explanation'],
    system_instructions: 'Compute deterministic summary metrics for tabular data and explain spreadsheet formula logic.',
  },
  {
    id: 'presentation_agent',
    name: 'Presentation Agent',
    category: 'Productivity',
    role: 'Slide Deck Narrative Specialist',
    description: 'Designs structured slide deck narratives, section structures, and drafts conversational speaker notes.',
    model: 'AI Gateway (Writing)',
    stage: 'Stage 13 (Operational)',
    status: 'operational',
    capabilities: ['Slide Deck Outline', 'Speaker Note Drafting', 'Visual Layout Planning'],
    system_instructions: 'Create cohesive presentation slide narratives with speaker notes. Do not claim PPTX file export.',
  },
  {
    id: 'creative_agent',
    name: 'Creative Agent',
    category: 'Creative',
    role: '3D Scene & Creative Brief Architect',
    description: 'Transforms creative briefs into structured 3D scene specifications, camera/lighting setups, and render plans.',
    model: 'AI Gateway (General)',
    stage: 'Stage 13 (Limited)',
    status: 'limited',
    capabilities: ['3D Scene Specification', 'Lighting & Camera Setup', 'Render Planning'],
    system_instructions: 'Draft structured 3D scene specifications. Do not execute live 3D rendering or Blender control.',
  },
  {
    id: 'messaging_agent',
    name: 'Messaging Agent',
    category: 'Communication',
    role: 'Conversational Intelligence Specialist',
    description: 'Classifies incoming communications by intent and urgency, and drafts contextual response suggestions.',
    model: 'AI Gateway (Fast)',
    stage: 'Stage 13 (Operational)',
    status: 'operational',
    capabilities: ['Message Intent Classification', 'Urgency Triage', 'Contextual Reply Drafting'],
    system_instructions: 'Classify incoming messages and draft respectful replies. Do not send external messages.',
  },
  {
    id: 'market_intelligence_agent',
    name: 'Market Intelligence Agent',
    category: 'Research',
    role: 'Market Data & Competitor Analyst',
    description: 'Analyzes supplied market indicators, benchmarks companies, and computes numerical comparisons.',
    model: 'Deterministic Engine',
    stage: 'Stage 13 (Limited)',
    status: 'limited',
    capabilities: ['Competitor Benchmarking', 'Metric Ranking', 'Evidence-Based Comparison'],
    system_instructions: 'Analyze supplied market datasets. Never fabricate live stock quotes or market projections.',
  },
  {
    id: 'workflow_automation_agent',
    name: 'Workflow Automation Agent',
    category: 'Automation',
    role: 'DAG Pipeline Architect',
    description: 'Decomposes complex automation goals into reusable DAG templates and validates dependency configurations.',
    model: 'Planning Engine',
    stage: 'Stage 13 (Operational)',
    status: 'operational',
    capabilities: ['DAG Template Proposal', 'Dependency Validation', 'Configuration Audit'],
    system_instructions: 'Structure automation pipelines into valid DAGs conforming to Stage 12 orchestration schemas.',
  },
];

export const AgentsWorkspace: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const [agents, setAgents] = React.useState<LegacyAgentDefinition[]>(AGENT_REGISTRY);
  const [selectedAgent, setSelectedAgent] = React.useState<LegacyAgentDefinition | null>(null);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [selectedCategory, setSelectedCategory] = React.useState<string>('all');
  const [isLoading, setIsLoading] = React.useState(false);
  const [isRefreshing, setIsRefreshing] = React.useState(false);
  const [activeTab, setActiveTab] = React.useState('all');

  // Backend state
  const [workersData, setWorkersData] = React.useState<WorkerListResponse | null>(null);
  const [tasksData, setTasksData] = React.useState<TaskResponse[]>([]);

  // Inspector detailed state
  const [inspectorTab, setInspectorTab] = React.useState<'overview' | 'config' | 'history' | 'diagnostics'>('overview');
  const [agentExecutions, setAgentExecutions] = React.useState<AgentExecutionHistoryItem[]>([]);
  const [diagnosticResult, setDiagnosticResult] = React.useState<any | null>(null);
  const [isTestingAgent, setIsTestingAgent] = React.useState(false);
  const [isSavingConfig, setIsSavingConfig] = React.useState(false);
  const [configForm, setConfigForm] = React.useState({
    preferred_model: '',
    concurrency_limit: 1,
    timeout_seconds: 60,
    temperature: 0.2,
  });

  const loadData = React.useCallback(async () => {
    try {
      const [workersRes, tasksRes] = await Promise.all([
        apiClient.getWorkers().catch(() => null),
        apiClient.listTasks().catch(() => ({ tasks: [], total: 0 })),
      ]);

      if (workersRes) setWorkersData(workersRes);
      if (tasksRes) setTasksData(tasksRes.tasks || []);

      // Attempt to load live agent manifests from backend
      try {
        const liveManifests = await apiClient.listAgentManifests();
        if (liveManifests && liveManifests.length > 0) {
          const mapped: LegacyAgentDefinition[] = liveManifests.map((m) => {
            const cat = m.category.charAt(0).toUpperCase() + m.category.slice(1);
            let statusVal: LegacyAgentDefinition['status'] = 'unavailable';
            if (m.availability_state === 'operational') statusVal = 'operational';
            else if (m.availability_state === 'limited') statusVal = 'limited';
            else if (m.availability_state === 'planned') statusVal = 'planned';

            return {
              id: m.agent_id,
              name: m.name,
              category: cat,
              role: m.role,
              description: m.description,
              model: m.model_profile?.preferred_model || 'Unified AI Gateway',
              stage: m.roadmap_stage,
              status: statusVal,
              capabilities: m.capabilities,
              system_instructions: m.system_instructions,
            };
          });

          // Merge live manifests while keeping any legacy test names (e.g. Job Discovery Scout)
          const merged = [...mapped];
          for (const item of AGENT_REGISTRY) {
            if (!merged.some((m) => m.name === item.name)) {
              merged.push(item);
            }
          }
          setAgents(merged);
        }
      } catch {
        // Fallback to static registry on network/server boot
      }
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  React.useEffect(() => {
    setIsLoading(true);
    loadData();
  }, [loadData]);

  // Sync route
  React.useEffect(() => {
    const path = location.pathname;
    if (path.includes('/recruitment')) {
      setActiveTab('recruitment');
      setSelectedCategory('Recruitment');
    } else if (path.includes('/computer')) {
      setActiveTab('computer');
      setSelectedCategory('Computer Control');
    } else if (path.includes('/orchestration')) {
      setActiveTab('orchestration');
      setSelectedCategory('Orchestration');
    } else {
      setActiveTab('all');
    }
  }, [location.pathname]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === 'all') {
      setSelectedCategory('all');
      navigate('/agents/all');
    } else if (tabId === 'recruitment') {
      setSelectedCategory('Recruitment');
      navigate('/agents/recruitment');
    } else if (tabId === 'computer') {
      setSelectedCategory('Computer Control');
      navigate('/agents/computer');
    } else if (tabId === 'orchestration') {
      setSelectedCategory('Orchestration');
      navigate('/agents/orchestration');
    }
  };

  // When an agent is selected, load its executions and configuration
  const handleSelectAgent = async (agent: LegacyAgentDefinition) => {
    setSelectedAgent(agent);
    setDiagnosticResult(null);
    setConfigForm({
      preferred_model: agent.model,
      concurrency_limit: 2,
      timeout_seconds: 60,
      temperature: 0.2,
    });

    try {
      const [history, cfg] = await Promise.all([
        apiClient.getAgentExecutions(agent.id, 10).catch(() => []),
        apiClient.getAgentConfiguration(agent.id).catch(() => null),
      ]);
      setAgentExecutions(history);
      if (cfg) {
        setConfigForm({
          preferred_model: cfg.preferred_model || agent.model,
          concurrency_limit: cfg.concurrency_limit || 2,
          timeout_seconds: cfg.timeout_seconds || 60,
          temperature: cfg.temperature ?? 0.2,
        });
      }
    } catch {
      // Ignored
    }
  };

  const handleRunDiagnostic = async () => {
    if (!selectedAgent) return;
    setIsTestingAgent(true);
    try {
      const res = await apiClient.testAgent(selectedAgent.id);
      setDiagnosticResult(res);
    } catch (err: any) {
      setDiagnosticResult({ passed: false, details: err.message || 'Diagnostic failed', duration_ms: 0 });
    } finally {
      setIsTestingAgent(false);
    }
  };

  const handleSaveConfig = async () => {
    if (!selectedAgent) return;
    setIsSavingConfig(true);
    try {
      await apiClient.updateAgentConfiguration(selectedAgent.id, {
        preferred_model: configForm.preferred_model,
        concurrency_limit: Number(configForm.concurrency_limit),
        timeout_seconds: Number(configForm.timeout_seconds),
        temperature: Number(configForm.temperature),
      });
      // Refresh
      await loadData();
    } catch (err) {
      console.error('Failed to save agent configuration:', err);
    } finally {
      setIsSavingConfig(false);
    }
  };

  const filteredAgents = React.useMemo(() => {
    return agents.filter((agent) => {
      const matchesSearch =
        searchQuery === '' ||
        agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        agent.role.toLowerCase().includes(searchQuery.toLowerCase()) ||
        agent.capabilities.some((c) => c.toLowerCase().includes(searchQuery.toLowerCase()));

      let matchesCategory = true;
      if (selectedCategory !== 'all') {
        const selLower = selectedCategory.toLowerCase();
        const catLower = agent.category.toLowerCase();
        matchesCategory = catLower.includes(selLower) || selLower.includes(catLower);
      }

      return matchesSearch && matchesCategory;
    });
  }, [agents, searchQuery, selectedCategory]);

  const tabs = [
    { id: 'all', label: 'All Agents', count: agents.length },
    { id: 'orchestration', label: 'Orchestration Core', count: agents.filter((a) => a.category.toLowerCase().includes('orchestration')).length },
    { id: 'recruitment', label: 'Recruitment', count: agents.filter((a) => a.category.toLowerCase().includes('recruitment')).length },
    { id: 'computer', label: 'Computer Control', count: agents.filter((a) => a.category.toLowerCase().includes('computer')).length },
  ];

  return (
    <ModulePage
      isDetailOpen={Boolean(selectedAgent)}
      detailPanel={
        selectedAgent ? (
          <ModuleDetailPanel
            title={selectedAgent.name}
            subtitle={selectedAgent.role}
            onClose={() => setSelectedAgent(null)}
          >
            <div className="space-y-4">
              {/* Status and Category badges */}
              <div className="flex flex-wrap items-center gap-2">
                <Badge
                  variant={
                    selectedAgent.status === 'operational' || selectedAgent.status === 'active'
                      ? 'success'
                      : selectedAgent.status === 'limited'
                      ? 'warning'
                      : 'neutral'
                  }
                  className="text-xs"
                >
                  {selectedAgent.status === 'operational' || selectedAgent.status === 'active'
                    ? 'Operational'
                    : selectedAgent.status === 'limited'
                    ? 'Limited Capabilities'
                    : 'Planned'}
                </Badge>
                <Badge variant="outline" className="text-xs font-mono">
                  {selectedAgent.category}
                </Badge>
                <Badge variant="outline" className="text-xs font-mono">
                  {selectedAgent.stage}
                </Badge>
              </div>

              {/* Inspector Sub-Tabs */}
              <div className="flex items-center gap-1 border-b border-border/60 pb-2">
                <Button
                  size="sm"
                  variant={inspectorTab === 'overview' ? 'secondary' : 'ghost'}
                  className="h-7 text-xs"
                  onClick={() => setInspectorTab('overview')}
                >
                  Overview
                </Button>
                <Button
                  size="sm"
                  variant={inspectorTab === 'config' ? 'secondary' : 'ghost'}
                  className="h-7 text-xs"
                  onClick={() => setInspectorTab('config')}
                >
                  Configuration
                </Button>
                <Button
                  size="sm"
                  variant={inspectorTab === 'history' ? 'secondary' : 'ghost'}
                  className="h-7 text-xs"
                  onClick={() => setInspectorTab('history')}
                >
                  History ({agentExecutions.length})
                </Button>
                <Button
                  size="sm"
                  variant={inspectorTab === 'diagnostics' ? 'secondary' : 'ghost'}
                  className="h-7 text-xs"
                  onClick={() => setInspectorTab('diagnostics')}
                >
                  Diagnostics
                </Button>
              </div>

              {inspectorTab === 'overview' && (
                <div className="space-y-4">
                  <div>
                    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Description
                    </span>
                    <p className="mt-1 text-xs text-foreground/90 leading-relaxed">
                      {selectedAgent.description}
                    </p>
                  </div>

                  <div>
                    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Target AI Model
                    </span>
                    <div className="mt-1.5 flex items-center gap-2">
                      <BrainCircuit className="h-4 w-4 text-primary" />
                      <span className="text-xs font-mono text-foreground">{selectedAgent.model}</span>
                    </div>
                  </div>

                  <div>
                    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Registered Capabilities
                    </span>
                    <ul className="mt-2 space-y-1.5">
                      {selectedAgent.capabilities.map((cap, i) => (
                        <li key={i} className="flex items-center gap-2 text-xs text-foreground/90">
                          <CheckCircle2 className="h-3.5 w-3.5 text-primary" />
                          <span>{cap}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {selectedAgent.system_instructions && (
                    <div>
                      <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                        System Instructions
                      </span>
                      <p className="mt-1 rounded bg-muted/30 p-2 font-mono text-[11px] text-muted-foreground border border-border/40">
                        {selectedAgent.system_instructions}
                      </p>
                    </div>
                  )}

                  <div className="rounded-lg border border-border/80 bg-muted/40 p-3.5 text-xs text-muted-foreground">
                    <div className="flex items-center gap-2 text-foreground font-semibold">
                      <Shield className="h-4 w-4 text-status-success" />
                      Operational Contract
                    </div>
                    <p className="mt-1 leading-relaxed">
                      Autonomous agents operate under Stage 01 & Stage 13 security guardrails. Privileged actions
                      enforce strict context isolation and input validation.
                    </p>
                  </div>
                </div>
              )}

              {inspectorTab === 'config' && (
                <div className="space-y-3">
                  <div>
                    <label className="text-xs font-medium text-foreground">Preferred Model / Alias</label>
                    <input
                      type="text"
                      className="mt-1 w-full rounded border border-border bg-background px-2.5 py-1.5 text-xs font-mono"
                      value={configForm.preferred_model}
                      onChange={(e) => setConfigForm({ ...configForm, preferred_model: e.target.value })}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-xs font-medium text-foreground">Concurrency</label>
                      <input
                        type="number"
                        min="1"
                        max="10"
                        className="mt-1 w-full rounded border border-border bg-background px-2.5 py-1.5 text-xs font-mono"
                        value={configForm.concurrency_limit}
                        onChange={(e) => setConfigForm({ ...configForm, concurrency_limit: parseInt(e.target.value) || 1 })}
                      />
                    </div>
                    <div>
                      <label className="text-xs font-medium text-foreground">Timeout (sec)</label>
                      <input
                        type="number"
                        min="5"
                        max="600"
                        className="mt-1 w-full rounded border border-border bg-background px-2.5 py-1.5 text-xs font-mono"
                        value={configForm.timeout_seconds}
                        onChange={(e) => setConfigForm({ ...configForm, timeout_seconds: parseInt(e.target.value) || 60 })}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-medium text-foreground">Temperature ({configForm.temperature})</label>
                    <input
                      type="range"
                      min="0.0"
                      max="1.0"
                      step="0.05"
                      className="mt-1 w-full"
                      value={configForm.temperature}
                      onChange={(e) => setConfigForm({ ...configForm, temperature: parseFloat(e.target.value) })}
                    />
                  </div>

                  <Button
                    size="sm"
                    className="w-full text-xs gap-1.5 mt-2"
                    onClick={handleSaveConfig}
                    disabled={isSavingConfig}
                  >
                    <Save className="h-3.5 w-3.5" />
                    {isSavingConfig ? 'Saving...' : 'Save Configuration'}
                  </Button>
                </div>
              )}

              {inspectorTab === 'history' && (
                <div className="space-y-2">
                  <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Recent Executions
                  </span>
                  {agentExecutions.length === 0 ? (
                    <p className="text-xs text-muted-foreground py-4 text-center">No recent executions recorded for this agent.</p>
                  ) : (
                    <div className="space-y-2 max-h-80 overflow-y-auto">
                      {agentExecutions.map((exec) => (
                        <div key={exec.id} className="rounded border border-border/50 bg-background/50 p-2.5 text-xs space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="font-mono text-[11px] font-semibold text-foreground">{exec.step_id}</span>
                            <Badge variant={exec.status === 'completed' ? 'success' : 'error'} className="text-[10px]">
                              {exec.status}
                            </Badge>
                          </div>
                          <div className="flex items-center justify-between text-[10px] text-muted-foreground font-mono">
                            <span>Duration: {exec.duration_ms}ms</span>
                            <span>Tokens: {exec.tokens_used}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {inspectorTab === 'diagnostics' && (
                <div className="space-y-3">
                  <p className="text-xs text-muted-foreground">
                    Execute a non-destructive self-test to verify manifest validity, registered capability bindings, and availability.
                  </p>
                  <Button
                    size="sm"
                    variant="outline"
                    className="w-full text-xs gap-1.5"
                    onClick={handleRunDiagnostic}
                    disabled={isTestingAgent}
                  >
                    <Play className="h-3.5 w-3.5 text-primary" />
                    {isTestingAgent ? 'Executing Diagnostic...' : 'Run Diagnostic Check'}
                  </Button>

                  {diagnosticResult && (
                    <div className="rounded border border-border/60 bg-muted/30 p-2.5 text-xs space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-foreground">Diagnostic Result:</span>
                        <Badge variant={diagnosticResult.passed ? 'success' : 'error'} className="text-[10px]">
                          {diagnosticResult.passed ? 'PASS' : 'FAIL'}
                        </Badge>
                      </div>
                      <p className="text-[11px] text-muted-foreground">{diagnosticResult.details}</p>
                      <span className="text-[10px] font-mono text-muted-foreground">Duration: {diagnosticResult.duration_ms}ms</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </ModuleDetailPanel>
        ) : null
      }
    >
      <ModuleHeader
        title="Autonomous Agent Swarm"
        description="Inspect, supervise, and configure the autonomous multi-agent coordination swarm."
        icon={Bot}
        stageTag="Stage 12 Active"
        badgeLabel={`${agents.length} Cataloged`}
        badgeVariant="outline"
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setIsRefreshing(true);
                loadData();
              }}
              className="text-xs gap-1.5"
            >
              <Activity className="h-3.5 w-3.5" />
              Worker Status
            </Button>
          </div>
        }
      />

      <div className="rounded-lg border border-primary/30 bg-primary/5 p-4 text-xs">
        <div className="flex items-center gap-2 font-semibold text-primary">
          <BrainCircuit className="h-4 w-4" />
          Multi-Agent Orchestration Runtime (Stage 12 Operational)
        </div>
        <p className="mt-1 text-muted-foreground">
          Core coordination agents (Supervisor, Planner, Router, Verifier, Recovery, Capability Worker) are active.
          Specialist domain agents across recruitment, coding, research, productivity, creative, comms, and automation are cataloged below.
        </p>
      </div>

      {/* Backend Worker Pool Status Card */}
      <Card className="border-border/60 bg-card/60 backdrop-blur-sm">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <Cpu className="h-4 w-4 text-primary" />
                Active Local Worker Pool (Stage 03 Foundation)
              </CardTitle>
              <CardDescription className="text-xs">
                Real background process workers available for asynchronous task dispatch
              </CardDescription>
            </div>
            <Badge variant="neutral" className="text-xs font-mono">
              {workersData?.active_workers ?? 0} / {workersData?.max_capacity ?? 4} Active
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <div className="rounded-lg border border-border/40 bg-background/50 p-3">
              <span className="text-[11px] text-muted-foreground uppercase font-semibold">
                Max Capacity
              </span>
              <p className="mt-1 text-lg font-bold text-foreground font-mono">
                {workersData?.max_capacity ?? 4}
              </p>
            </div>
            <div className="rounded-lg border border-border/40 bg-background/50 p-3">
              <span className="text-[11px] text-muted-foreground uppercase font-semibold">
                Active Workers
              </span>
              <p className="mt-1 text-lg font-bold text-status-success font-mono">
                {workersData?.active_workers ?? 0}
              </p>
            </div>
            <div className="rounded-lg border border-border/40 bg-background/50 p-3">
              <span className="text-[11px] text-muted-foreground uppercase font-semibold">
                Idle Workers
              </span>
              <p className="mt-1 text-lg font-bold text-cyan font-mono">
                {workersData?.idle_workers ?? 4}
              </p>
            </div>
            <div className="rounded-lg border border-border/40 bg-background/50 p-3">
              <span className="text-[11px] text-muted-foreground uppercase font-semibold">
                Tasks Handled
              </span>
              <p className="mt-1 text-lg font-bold text-primary font-mono">{tasksData.length}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={handleTabChange} />

      <ModuleToolbar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        searchPlaceholder="Filter agents by name, role, or capability..."
        onRefresh={() => {
          setIsRefreshing(true);
          loadData();
        }}
        isRefreshing={isRefreshing}
        filters={
          <div className="flex flex-wrap items-center gap-1.5">
            {[
              { id: 'all', label: 'All Roles' },
              { id: 'Orchestration', label: 'Orchestration' },
              { id: 'Recruitment', label: 'Recruitment' },
              { id: 'Computer Control', label: 'Computer' },
              { id: 'Development', label: 'Coding' },
              { id: 'Research', label: 'Research' },
              { id: 'Productivity', label: 'Productivity' },
              { id: 'Creative', label: 'Creative' },
              { id: 'Communication', label: 'Comms' },
              { id: 'Automation', label: 'Automation' },
            ].map((cat) => (
              <Button
                key={cat.id}
                variant={selectedCategory === cat.id ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setSelectedCategory(cat.id)}
                className="h-8 text-xs font-medium"
              >
                {cat.label}
              </Button>
            ))}
          </div>
        }
      />

      {isLoading ? (
        <ModuleLoadingState rows={6} layout="cards" />
      ) : filteredAgents.length === 0 ? (
        <ModuleEmptyState
          title="No matching agents found"
          description="Try adjusting your search criteria or clearing active category filters."
          actionLabel="Clear Filters"
          onAction={() => {
            setSearchQuery('');
            setSelectedCategory('all');
          }}
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filteredAgents.map((agent) => {
            const isOp = agent.status === 'operational' || agent.status === 'active';
            const isLim = agent.status === 'limited';

            return (
              <Card
                key={agent.id}
                className={`group cursor-pointer border border-border/60 bg-card/60 transition-all duration-200 hover:border-primary/50 hover:bg-card/90 hover:shadow-md ${
                  selectedAgent?.id === agent.id ? 'ring-2 ring-primary border-primary' : ''
                }`}
                onClick={() => handleSelectAgent(agent)}
              >
                <CardHeader className="p-4 pb-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2.5">
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-primary/20 bg-primary/10 text-primary">
                        <Bot className="h-4 w-4" />
                      </div>
                      <div>
                        <CardTitle className="text-sm font-semibold text-foreground group-hover:text-primary transition-colors">
                          {agent.name}
                        </CardTitle>
                        <CardDescription className="text-xs">{agent.category}</CardDescription>
                      </div>
                    </div>
                    <Badge
                      variant={isOp ? 'success' : isLim ? 'warning' : 'outline'}
                      className="text-[10px] font-mono shrink-0"
                    >
                      {isOp ? 'Active' : isLim ? 'Limited' : 'Planned'}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="p-4 pt-2">
                  <p className="line-clamp-2 text-xs text-muted-foreground leading-relaxed">
                    {agent.description}
                  </p>

                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {agent.capabilities.slice(0, 2).map((cap, i) => (
                      <span
                        key={i}
                        className="inline-flex items-center rounded-md bg-muted/60 px-2 py-0.5 text-[10px] text-muted-foreground"
                      >
                        {cap}
                      </span>
                    ))}
                    {agent.capabilities.length > 2 && (
                      <span className="inline-flex items-center rounded-md bg-muted/60 px-1.5 py-0.5 text-[10px] text-muted-foreground">
                        +{agent.capabilities.length - 2}
                      </span>
                    )}
                  </div>

                  <div className="mt-4 flex items-center justify-between border-t border-border/40 pt-2 text-[11px] text-muted-foreground">
                    <span className="truncate font-mono">{agent.model}</span>
                    <span className="text-primary opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
                      <Eye className="h-3 w-3" /> Inspect
                    </span>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </ModulePage>
  );
};

export default AgentsWorkspace;
