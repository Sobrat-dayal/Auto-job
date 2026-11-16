import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Bot, BrainCircuit, Cpu, Shield, Activity, CheckCircle2, Eye } from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleToolbar,
  ModuleTabs,
  ModuleUnavailableState,
  ModuleDetailPanel,
  ModuleLoadingState,
  ModuleEmptyState,
} from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { apiClient } from '@/lib/api-client';
import type { TaskResponse, WorkerListResponse } from '@autonom/shared-types';

export interface AgentDefinition {
  id: string;
  name: string;
  category: 'Orchestration' | 'Recruitment' | 'Computer Control' | 'Specialist & Creative';
  role: string;
  description: string;
  model: string;
  stage: string;
  status: 'active' | 'idle' | 'unavailable';
  capabilities: string[];
}

export const AGENT_REGISTRY: AgentDefinition[] = [
  // Tier 1: Orchestration & Swarm
  {
    id: 'supervisor-swarm',
    name: 'Supervisor Swarm Coordinator',
    category: 'Orchestration',
    role: 'Multi-Agent Orchestrator & Safety Gate',
    description:
      'Plans, breaks down high-level user directives into DAGs, and assigns tasks to specialist agents.',
    model: 'Claude 3.5 Sonnet / GPT-4o',
    stage: 'Stage 12',
    status: 'unavailable',
    capabilities: [
      'Dynamic DAG Generation',
      'Safety Policy Verification',
      'Failure Recovery & Retries',
    ],
  },
  {
    id: 'plan-execute-verify',
    name: 'PEV Plan-Execute-Verify Engine',
    category: 'Orchestration',
    role: 'Verification & Quality Auditor',
    description:
      'Inspects intermediate agent outputs and validates results against requirements before finalizing.',
    model: 'Gemini 1.5 Pro',
    stage: 'Stage 12',
    status: 'unavailable',
    capabilities: ['Self-Correction Loops', 'Deterministic Invariant Checks', 'Audit Trails'],
  },
  {
    id: 'safety-guardrail',
    name: 'Safety & Guardrails Officer',
    category: 'Orchestration',
    role: 'Security Boundary Validator',
    description:
      'Enforces human-in-the-loop authorization gates for financial, credential, and system actions.',
    model: 'Deterministic Rule Engine + Local LLM',
    stage: 'Stage 13',
    status: 'unavailable',
    capabilities: ['Authorization Interception', 'Zero-Trust Policy Gate', 'Secret Masking'],
  },

  // Tier 2: Job & Recruitment Specialists
  {
    id: 'job-discovery',
    name: 'Job Discovery Scout',
    category: 'Recruitment',
    role: 'Multi-Source Job Harvester',
    description: 'Monitors LinkedIn, Greenhouse, Lever, and Indeed for high-match opportunities.',
    model: 'GPT-4o Mini',
    stage: 'Stage 26',
    status: 'unavailable',
    capabilities: ['Hourly ATS Feeds', 'Boolean Query Expansion', 'Anti-Deduplication Engine'],
  },
  {
    id: 'application-tailor',
    name: 'Application Tailor Agent',
    category: 'Recruitment',
    role: 'Resume Customizer & Scribe',
    description:
      'Aligns verified candidate career experiences with job requirements without hallucination.',
    model: 'Claude 3.5 Sonnet',
    stage: 'Stage 31',
    status: 'unavailable',
    capabilities: ['Evidence-Based Grounding', 'ATS Keyword Tuning', 'PDF Compiling'],
  },
  {
    id: 'recruiter-outreach',
    name: 'Recruiter Outreach Scribe',
    category: 'Recruitment',
    role: 'Communications & Follow-Up Drafter',
    description:
      'Drafts tailored cover letters, intro emails, and recruiter inquiries with human approval.',
    model: 'Claude 3.5 Sonnet',
    stage: 'Stage 36',
    status: 'unavailable',
    capabilities: ['Contextual Tone Matching', 'Thread Summarization', 'Safe Staging'],
  },
  {
    id: 'interview-prep-coach',
    name: 'Interview Prep Coach',
    category: 'Recruitment',
    role: 'Mock Interviewer & Strategy Advisor',
    description:
      'Simulates technical and behavioral interviews tailored to the target company culture and stack.',
    model: 'Gemini 1.5 Pro',
    stage: 'Stage 39',
    status: 'unavailable',
    capabilities: ['STAR Method Coaching', 'Live Audio/Text Mocks', 'Technical Deep Dives'],
  },

  // Tier 3: Computer Control
  {
    id: 'visual-grounding',
    name: 'Visual Grounding Agent',
    category: 'Computer Control',
    role: 'Screen Perception & OCR Specialist',
    description:
      'Perceives Windows desktop state via coordinate grounding and high-resolution screen parsing.',
    model: 'UI-TARS / Gemini 1.5 Flash',
    stage: 'Stage 17',
    status: 'unavailable',
    capabilities: ['Coordinate Localization', 'Multi-Monitor Vision', 'Visual Change Detection'],
  },
  {
    id: 'uia-driver',
    name: 'Windows UI Automation Driver',
    category: 'Computer Control',
    role: 'Accessibility Tree Operator',
    description:
      'Navigates Windows applications through native accessibility trees for sub-millisecond reliability.',
    model: 'Native Windows Rust Bridge',
    stage: 'Stage 18',
    status: 'unavailable',
    capabilities: [
      'Direct Element Focus',
      'Native Click/Type Injection',
      'Zero-Latency Inspection',
    ],
  },
  {
    id: 'browser-navigator',
    name: 'Autonomous Browser Navigator',
    category: 'Computer Control',
    role: 'Web Application Automator',
    description:
      'Drives Chromium browser instances via CDP for complex web portals and multi-step forms.',
    model: 'Playwright CDP + LLM',
    stage: 'Stage 16',
    status: 'unavailable',
    capabilities: ['Form Fill Verification', 'Cookie Session Persistence', 'CAPTCHA Intercept'],
  },

  // Tier 4: Specialists & Creative
  {
    id: 'code-architect',
    name: 'Full-Stack Code Architect',
    category: 'Specialist & Creative',
    role: 'Software Engineer & Code Reviewer',
    description:
      'Builds features, fixes bugs, generates unit tests, and validates git commits in local repositories.',
    model: 'Claude 3.5 Sonnet',
    stage: 'Stage 41',
    status: 'unavailable',
    capabilities: ['Multi-File Edits', 'Test Run Supervision', 'Git Flow Management'],
  },
  {
    id: 'document-generator',
    name: 'Document & Report Generator',
    category: 'Specialist & Creative',
    role: 'Technical Writer & Publisher',
    description: 'Produces formatted Markdown, Word, PDF, and spreadsheet deliverables.',
    model: 'GPT-4o',
    stage: 'Stage 42',
    status: 'unavailable',
    capabilities: ['Format Conversion', 'Table Structuring', 'Formula Generation'],
  },
  {
    id: 'creative-studio',
    name: '3D & Creative Studio Specialist',
    category: 'Specialist & Creative',
    role: 'Media & 3D Content Creator',
    description: 'Generates graphics, renders 3D models, and automates video/animation scripts.',
    model: 'Blender Python API + Flux',
    stage: 'Stage 43',
    status: 'unavailable',
    capabilities: ['Blender Headless Rendering', 'Image Generation', 'Timeline Synthesis'],
  },
  {
    id: 'market-researcher',
    name: 'Deep Research & Market Analyst',
    category: 'Specialist & Creative',
    role: 'Intelligence Harvester',
    description:
      'Performs structured market research, company financial analysis, and competitive landscape briefs.',
    model: 'Claude 3.5 Sonnet / Perplexity',
    stage: 'Stage 44',
    status: 'unavailable',
    capabilities: ['Web Synthesis', 'Citation Verification', 'Executive Briefings'],
  },
  {
    id: 'mcp-integrator',
    name: 'Model Context Protocol (MCP) Bridge',
    category: 'Specialist & Creative',
    role: 'External Tool Router',
    description:
      'Discovers, loads, and executes tools across standard Model Context Protocol servers.',
    model: 'MCP TypeScript Runtime',
    stage: 'Stage 45',
    status: 'unavailable',
    capabilities: ['Dynamic Schema Introspection', 'Standard JSON-RPC 2.0', 'Tool Sandboxing'],
  },
];

export const AgentsWorkspace: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const getInitialTab = (): string => {
    if (location.pathname.includes('/agents/active')) return 'active';
    if (location.pathname.includes('/agents/tasks')) return 'tasks';
    if (location.pathname.includes('/agents/performance')) return 'performance';
    if (location.pathname.includes('/agents/config')) return 'config';
    return 'all';
  };

  const [activeTab, setActiveTab] = React.useState<string>(getInitialTab());
  const [searchQuery, setSearchQuery] = React.useState('');
  const [selectedCategory, setSelectedCategory] = React.useState<string>('all');
  const [selectedAgent, setSelectedAgent] = React.useState<AgentDefinition | null>(null);
  const [workersData, setWorkersData] = React.useState<WorkerListResponse | null>(null);
  const [tasksData, setTasksData] = React.useState<TaskResponse[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [isRefreshing, setIsRefreshing] = React.useState(false);

  React.useEffect(() => {
    setActiveTab(getInitialTab());
  }, [location.pathname]);

  const loadData = React.useCallback(async () => {
    try {
      const [wRes, tRes] = await Promise.allSettled([
        apiClient.getWorkers(),
        apiClient.listTasks(),
      ]);
      if (wRes.status === 'fulfilled') setWorkersData(wRes.value);
      if (tRes.status === 'fulfilled') setTasksData(tRes.value.tasks);
    } catch {
      // Backend not running is gracefully handled
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  React.useEffect(() => {
    loadData();
  }, [loadData]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === 'all') navigate('/agents/all');
    else navigate(`/agents/${tabId}`);
  };

  const filteredAgents = AGENT_REGISTRY.filter((agent) => {
    const matchesSearch =
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.role.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || agent.category === selectedCategory;
    const matchesTab = activeTab !== 'active' || agent.status === 'active';
    return matchesSearch && matchesCategory && matchesTab;
  });

  const tabs = [
    { id: 'all', label: 'All Agents', badge: AGENT_REGISTRY.length },
    {
      id: 'active',
      label: 'Active & Workers',
      badge: workersData?.active_workers ?? 0,
    },
    { id: 'tasks', label: 'Task Assignments', badge: tasksData.length },
    { id: 'performance', label: 'Telemetry & Latency' },
    { id: 'config', label: 'Configuration & Models' },
  ];

  return (
    <ModulePage
      isDetailOpen={!!selectedAgent}
      detailPanel={
        selectedAgent ? (
          <ModuleDetailPanel
            title={selectedAgent.name}
            subtitle={`${selectedAgent.category} • ${selectedAgent.stage}`}
            onClose={() => setSelectedAgent(null)}
            actions={
              <Badge variant="outline" className="text-xs">
                {selectedAgent.stage}
              </Badge>
            }
          >
            <div className="space-y-5">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Role & Specialty
                </span>
                <p className="mt-1 text-sm font-medium text-foreground">{selectedAgent.role}</p>
                <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
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

              <div className="rounded-lg border border-border/80 bg-muted/40 p-3.5 text-xs text-muted-foreground">
                <div className="flex items-center gap-2 text-foreground font-semibold">
                  <Shield className="h-4 w-4 text-status-success" />
                  Operational Contract
                </div>
                <p className="mt-1 leading-relaxed">
                  Autonomous agents operate under Stage 01 security guardrails. All privileged OS
                  and browser actions require supervisory authorization.
                </p>
              </div>
            </div>
          </ModuleDetailPanel>
        ) : null
      }
    >
      <ModuleHeader
        title="Autonomous Agent Swarm"
        description="Inspect, supervise, and configure the 24-agent autonomous specialist swarm."
        icon={Bot}
        stageTag="Stage 12 Planned"
        badgeLabel={`${AGENT_REGISTRY.length} Cataloged`}
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

      <ModuleUnavailableState
        moduleName="Autonomous Swarm Orchestration"
        stageTag="Stage 12"
        stageName="24-Agent Swarm Runtime"
        description="Full multi-agent autonomous swarm execution, dynamic Plan-Execute-Verify cycles, and peer-to-peer message bus communication will activate in Stage 12. Below is the operational agent registry and current local background worker pool."
        plannedCapabilities={[
          'Dynamic multi-agent DAG decomposition',
          'Autonomous plan-execute-verify loops',
          'Deterministic safety barrier gating',
          'Agent-to-agent async event broadcasting',
        ]}
      />

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
          <div className="flex flex-wrap items-center gap-2">
            {(
              [
                'all',
                'Orchestration',
                'Recruitment',
                'Computer Control',
                'Specialist & Creative',
              ] as const
            ).map((cat) => (
              <Button
                key={cat}
                variant={selectedCategory === cat ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setSelectedCategory(cat)}
                className="h-8 text-xs font-medium"
              >
                {cat === 'all' ? 'All Roles' : cat}
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
          {filteredAgents.map((agent) => (
            <Card
              key={agent.id}
              className={`group cursor-pointer border border-border/60 bg-card/60 transition-all duration-200 hover:border-primary/50 hover:bg-card/90 hover:shadow-md ${
                selectedAgent?.id === agent.id ? 'ring-2 ring-primary border-primary' : ''
              }`}
              onClick={() => setSelectedAgent(agent)}
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
                  <Badge variant="outline" className="text-[10px] font-mono shrink-0">
                    {agent.stage}
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
          ))}
        </div>
      )}
    </ModulePage>
  );
};

export default AgentsWorkspace;
