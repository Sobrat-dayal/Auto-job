import {
  LayoutDashboard,
  Bot,
  Brain,
  Monitor,
  BriefcaseBusiness,
  MessagesSquare,
  CalendarCheck,
  Files,
  Code2,
  Box,
  ChartNoAxesCombined,
  Workflow,
  ChartColumn,
  History,
  Plug,
  Settings,
  Palette,
  Activity,
  Database,
  Sparkles,
  ShieldAlert,
  UserCheck,
  FileText,
  PenTool,
  Sliders,
} from 'lucide-react';
import type {
  NavigationGroup,
  NavigationItem,
  NavigationChildItem,
  BreadcrumbItem,
} from './navigation-types';

export const NAVIGATION_GROUPS: NavigationGroup[] = [
  {
    id: 'main',
    title: 'MAIN',
    order: 1,
    items: [
      {
        id: 'command-center',
        title: 'Command Center',
        icon: LayoutDashboard,
        path: '/dashboard',
        group: 'main',
        availability: 'implemented',
        description:
          'Overall AUTONOM operational overview, active task telemetry, and engine health.',
        shortcut: 'Ctrl+1',
      },
      {
        id: 'approvals',
        title: 'Pending Approvals',
        icon: ShieldAlert,
        path: '/approvals',
        group: 'main',
        availability: 'implemented',
        description: 'Review, approve, or deny sensitive agent actions and authorization requests.',
        badge: 'Live',
        shortcut: 'Ctrl+Shift+A',
      },
      {
        id: 'memory',
        title: 'Agent Memory',
        icon: Brain,
        path: '/memory',
        group: 'main',
        availability: 'implemented',
        description: 'Persistent agent memory, hybrid semantic retrieval, procedural workflows, and conflict review.',
        badge: 'v1',
        shortcut: 'Ctrl+Shift+M',
      },
      {
        id: 'agents',
        title: 'Agents',
        icon: Bot,
        path: '/agents',
        group: 'main',
        availability: 'planned',
        roadmapStage: 'Stage 12',
        description: 'Supervise, configure, and inspect the 24-agent autonomous swarm.',
        badge: 'v2',
        children: [
          {
            id: 'agents-all',
            title: 'All Agents',
            path: '/agents/all',
            availability: 'planned',
            roadmapStage: 'Stage 12',
            description: 'Catalog of all 24 specialist agents, capabilities, and system roles.',
          },
          {
            id: 'agents-active',
            title: 'Active Agents',
            path: '/agents/active',
            availability: 'planned',
            roadmapStage: 'Stage 12',
            description: 'Live agents currently executing tasks or holding memory locks.',
          },
          {
            id: 'agents-tasks',
            title: 'Agent Tasks',
            path: '/agents/tasks',
            availability: 'planned',
            roadmapStage: 'Stage 12',
            description: 'Task assignment queue, plan-execute-verify DAG states.',
          },
          {
            id: 'agents-performance',
            title: 'Agent Performance',
            path: '/agents/performance',
            availability: 'planned',
            roadmapStage: 'Stage 12',
            description: 'Token efficiency, completion latency, and error attribution metrics.',
          },
          {
            id: 'agents-config',
            title: 'Agent Configuration',
            path: '/agents/config',
            availability: 'planned',
            roadmapStage: 'Stage 12',
            description: 'Model bindings, temperature, system prompts, and tool permissions.',
          },
        ],
      },
      {
        id: 'computer-control',
        title: 'Computer Control',
        icon: Monitor,
        path: '/computer',
        group: 'main',
        availability: 'planned',
        roadmapStage: 'Stage 16',
        description:
          'Dual-modality computer interaction: visual grounding and Windows UI Automation.',
        badge: 'v2',
        children: [
          {
            id: 'computer-live',
            title: 'Live Desktop',
            path: '/computer/live',
            availability: 'planned',
            roadmapStage: 'Stage 16',
            description: 'Live visual viewport with action masks and interaction bounding boxes.',
          },
          {
            id: 'computer-tasks',
            title: 'Computer Tasks',
            path: '/computer/tasks',
            availability: 'planned',
            roadmapStage: 'Stage 16',
            description: 'Active UI automation steps, keystrokes, and click sequences.',
          },
          {
            id: 'computer-browser',
            title: 'Browser Sessions',
            path: '/computer/browser',
            availability: 'planned',
            roadmapStage: 'Stage 18',
            description: 'Playwright automation contexts, cookies, and active web pages.',
          },
          {
            id: 'computer-history',
            title: 'Interaction History',
            path: '/computer/history',
            availability: 'planned',
            roadmapStage: 'Stage 16',
            description: 'Recorded action traces, screenshots, and structural DOM diffs.',
          },
          {
            id: 'computer-permissions',
            title: 'Permissions',
            path: '/computer/permissions',
            availability: 'planned',
            roadmapStage: 'Stage 14',
            description: 'Human-in-the-loop permission boundary rules and sensitive area masks.',
          },
        ],
      },
    ],
  },
  {
    id: 'recruitment',
    title: 'RECRUITMENT',
    order: 2,
    items: [
      {
        id: 'applicant-profile',
        title: 'Applicant Profile & Identity',
        icon: UserCheck,
        path: '/recruitment/profile',
        group: 'recruitment',
        availability: 'implemented',
        roadmapStage: 'Stage 21',
        description: 'Verified professional identity, credentials, skills, experience, and evidence provenance.',
        badge: 'v1',
      },
      {
        id: 'github-portfolio',
        title: 'GitHub & Code Portfolio',
        icon: Code2,
        path: '/recruitment/github',
        group: 'recruitment',
        availability: 'implemented',
        roadmapStage: 'Stage 22',
        description: 'GitHub account connectivity, repository discovery, code intelligence, and candidate skills extraction.',
        badge: 'v1',
      },
      {
        id: 'resume-portfolio',
        title: 'Resumes & Portfolios',
        icon: FileText,
        path: '/recruitment/resumes',
        group: 'recruitment',
        availability: 'implemented',
        roadmapStage: 'Stage 23',
        description: 'ATS resume builder, job tailoring, DOCX/PDF export, version diffs, and developer portfolio.',
        badge: 'v1',
      },
      {
        id: 'recruitment-writing',
        title: 'Cover Letters & Answers',
        icon: PenTool,
        path: '/recruitment/writing',
        group: 'recruitment',
        availability: 'implemented',
        roadmapStage: 'Stage 24',
        description: 'Factual cover letter generation, screening question intelligence, reusable answer library, and application writing packages.',
        badge: 'v1',
      },
      {
        id: 'recruitment-policy',
        title: 'Career Preferences & Policies',
        icon: Sliders,
        path: '/recruitment/policy',
        group: 'recruitment',
        availability: 'implemented',
        roadmapStage: 'Stage 25',
        description: 'Career strategies, target role taxonomy, location & compensation floors, employer blocklists, and autonomous decisions.',
        badge: 'v1',
      },
      {
        id: 'jobs',
        title: 'Jobs & Applications',
        icon: BriefcaseBusiness,
        path: '/recruitment',
        group: 'recruitment',
        availability: 'planned',
        roadmapStage: 'Stage 26',
        description: 'Autonomous job scouting, match scoring, resume tailoring, and submissions.',
        badge: 'v2',
        children: [
          {
            id: 'jobs-discovery',
            title: 'Job Discovery',
            path: '/recruitment/discovery',
            availability: 'planned',
            roadmapStage: 'Stage 26',
            description:
              'Scouted listings across LinkedIn, Indeed, Greenhouse, Lever, and Workday.',
          },
          {
            id: 'jobs-recommended',
            title: 'Recommended Jobs',
            path: '/recruitment/recommended',
            availability: 'planned',
            roadmapStage: 'Stage 27',
            description:
              'Positions evaluated with high semantic match scores against your profile.',
          },
          {
            id: 'jobs-pipeline',
            title: 'Application Pipeline',
            path: '/recruitment/pipeline',
            availability: 'planned',
            roadmapStage: 'Stage 31',
            description: 'Visual Kanban pipeline: Discovered -> Tailoring -> Review -> Submitted.',
          },
          {
            id: 'jobs-submitted',
            title: 'Submitted Applications',
            path: '/recruitment/submitted',
            availability: 'planned',
            roadmapStage: 'Stage 32',
            description: 'Verified submissions with confirmation timestamps and portal links.',
          },
          {
            id: 'jobs-history',
            title: 'Application History',
            path: '/recruitment/history',
            availability: 'planned',
            roadmapStage: 'Stage 32',
            description: 'Chronological archive of past submissions, versions, and outcomes.',
          },
          {
            id: 'jobs-excluded',
            title: 'Excluded Jobs',
            path: '/recruitment/excluded',
            availability: 'planned',
            roadmapStage: 'Stage 27',
            description: 'Filtered or manually excluded companies, titles, and locations.',
          },
          {
            id: 'jobs-analytics',
            title: 'Recruitment Analytics',
            path: '/recruitment/analytics',
            availability: 'planned',
            roadmapStage: 'Stage 35',
            description: 'Response rates, conversion funnels, and compensation distributions.',
          },
        ],
      },
      {
        id: 'communications',
        title: 'Communications',
        icon: MessagesSquare,
        path: '/communications',
        group: 'recruitment',
        availability: 'planned',
        roadmapStage: 'Stage 36',
        description: 'Automated email triage, recruiter message drafting, and follow-ups.',
        badge: 'v2',
        children: [
          {
            id: 'comms-inbox',
            title: 'Inbox',
            path: '/communications/inbox',
            availability: 'planned',
            roadmapStage: 'Stage 36',
            description: 'Unified recruiter email and messaging inbox with priority triage.',
          },
          {
            id: 'comms-conversations',
            title: 'Recruiter Conversations',
            path: '/communications/conversations',
            availability: 'planned',
            roadmapStage: 'Stage 36',
            description:
              'Active correspondence threads with talent acquisition and hiring managers.',
          },
          {
            id: 'comms-email',
            title: 'Email Automation',
            path: '/communications/email',
            availability: 'planned',
            roadmapStage: 'Stage 36',
            description: 'IMAP/SMTP and Gmail/Outlook sync rules and screening triggers.',
          },
          {
            id: 'comms-telegram',
            title: 'Telegram',
            path: '/communications/telegram',
            availability: 'planned',
            roadmapStage: 'Stage 37',
            description: 'Telegram bot integration for instant approval alerts and notifications.',
          },
          {
            id: 'comms-whatsapp',
            title: 'WhatsApp',
            path: '/communications/whatsapp',
            availability: 'planned',
            roadmapStage: 'Stage 37',
            description: 'WhatsApp business API connector for recruiter reach-outs.',
          },
          {
            id: 'comms-follow-ups',
            title: 'Follow-ups',
            path: '/communications/follow-ups',
            availability: 'planned',
            roadmapStage: 'Stage 36',
            description: 'Automated follow-up scheduling with cadence and tone control.',
          },
        ],
      },
      {
        id: 'interviews',
        title: 'Interviews',
        icon: CalendarCheck,
        path: '/interviews',
        group: 'recruitment',
        availability: 'planned',
        roadmapStage: 'Stage 38',
        description:
          'Calendar synchronization, technical preparation dossiers, and mock interviews.',
        badge: 'v2',
        children: [
          {
            id: 'interviews-upcoming',
            title: 'Upcoming Interviews',
            path: '/interviews/upcoming',
            availability: 'planned',
            roadmapStage: 'Stage 38',
            description: 'Scheduled interviews with meeting links and recruiter briefing notes.',
          },
          {
            id: 'interviews-calendar',
            title: 'Interview Calendar',
            path: '/interviews/calendar',
            availability: 'planned',
            roadmapStage: 'Stage 38',
            description: 'Calendar view showing scheduled technical screens and panel loops.',
          },
          {
            id: 'interviews-prep',
            title: 'Interview Preparation',
            path: '/interviews/prep',
            availability: 'planned',
            roadmapStage: 'Stage 39',
            description: 'Automated briefing dossiers covering company research and interviewers.',
          },
          {
            id: 'interviews-mock',
            title: 'Mock Interviews',
            path: '/interviews/mock',
            availability: 'planned',
            roadmapStage: 'Stage 39',
            description: 'Simulated AI technical interview sessions with audio/text feedback.',
          },
          {
            id: 'interviews-history',
            title: 'Interview History',
            path: '/interviews/history',
            availability: 'planned',
            roadmapStage: 'Stage 38',
            description: 'Past interviews, retrospective notes, and compensation discussions.',
          },
        ],
      },
    ],
  },
  {
    id: 'workspace',
    title: 'WORKSPACE',
    order: 3,
    items: [
      {
        id: 'documents',
        title: 'Documents',
        icon: Files,
        path: '/documents',
        group: 'workspace',
        availability: 'planned',
        roadmapStage: 'Stage 41',
        description: 'Document generation, resume PDF tailoring, and spreadsheet analytics.',
        badge: 'v2',
        children: [
          {
            id: 'docs-workspace',
            title: 'File Workspace',
            path: '/documents/workspace',
            availability: 'planned',
            roadmapStage: 'Stage 41',
            description: 'Local workspace filesystem manager and artifact repository.',
          },
          {
            id: 'docs-text',
            title: 'Documents',
            path: '/documents/docs',
            availability: 'planned',
            roadmapStage: 'Stage 41',
            description: 'Markdown, Word, and LaTeX cover letter and career document editor.',
          },
          {
            id: 'docs-spreadsheets',
            title: 'Spreadsheets',
            path: '/documents/spreadsheets',
            availability: 'planned',
            roadmapStage: 'Stage 41',
            description: 'CSV and Excel data modeling for salary benchmarks and job trackers.',
          },
          {
            id: 'docs-presentations',
            title: 'Presentations',
            path: '/documents/presentations',
            availability: 'planned',
            roadmapStage: 'Stage 41',
            description: 'Slide decks for technical presentations and portfolio showcases.',
          },
          {
            id: 'docs-pdfs',
            title: 'PDFs',
            path: '/documents/pdfs',
            availability: 'planned',
            roadmapStage: 'Stage 41',
            description: 'Tailored resume PDF compiler and visual artifact viewer.',
          },
          {
            id: 'docs-artifacts',
            title: 'Generated Artifacts',
            path: '/documents/artifacts',
            availability: 'planned',
            roadmapStage: 'Stage 41',
            description: 'Synthesized documents, tailored portfolios, and export logs.',
          },
        ],
      },
      {
        id: 'coding',
        title: 'Coding',
        icon: Code2,
        path: '/coding',
        group: 'workspace',
        availability: 'planned',
        roadmapStage: 'Stage 43',
        description: 'Autonomous software engineering, git automation, tests, and code reviews.',
        badge: 'v2',
        children: [
          {
            id: 'coding-projects',
            title: 'Projects',
            path: '/coding/projects',
            availability: 'planned',
            roadmapStage: 'Stage 43',
            description: 'Local coding repositories and active software development workspaces.',
          },
          {
            id: 'coding-agents',
            title: 'Coding Agents',
            path: '/coding/agents',
            availability: 'planned',
            roadmapStage: 'Stage 43',
            description: 'Autonomous coding agents writing features, bug fixes, and tests.',
          },
          {
            id: 'coding-repos',
            title: 'Repository Activity',
            path: '/coding/repos',
            availability: 'planned',
            roadmapStage: 'Stage 43',
            description: 'Git commits, pull requests, branch management, and CI/CD status.',
          },
          {
            id: 'coding-builds',
            title: 'Builds & Tests',
            path: '/coding/builds',
            availability: 'planned',
            roadmapStage: 'Stage 43',
            description: 'Test runners, compilation output, and container build logs.',
          },
          {
            id: 'coding-reviews',
            title: 'Code Reviews',
            path: '/coding/reviews',
            availability: 'planned',
            roadmapStage: 'Stage 43',
            description: 'Automated diff analysis, security audits, and code quality assessments.',
          },
        ],
      },
      {
        id: 'creative',
        title: 'Creative Studio',
        icon: Box,
        path: '/creative',
        group: 'workspace',
        availability: 'planned',
        roadmapStage: 'Stage 44',
        description: '3D modeling, asset generation, animation sequences, and media synthesis.',
        badge: 'v2',
        children: [
          {
            id: 'creative-3d',
            title: '3D Workspace',
            path: '/creative/3d',
            availability: 'planned',
            roadmapStage: 'Stage 44',
            description: '3D mesh preview, glTF inspection, and spatial asset generators.',
          },
          {
            id: 'creative-animation',
            title: 'Animation',
            path: '/creative/animation',
            availability: 'planned',
            roadmapStage: 'Stage 44',
            description: 'Timeline control and parametric animation workflows.',
          },
          {
            id: 'creative-graphics',
            title: 'Graphics',
            path: '/creative/graphics',
            availability: 'planned',
            roadmapStage: 'Stage 44',
            description: 'Vector and raster asset generation for personal branding and portfolios.',
          },
          {
            id: 'creative-media',
            title: 'Media Workflows',
            path: '/creative/media',
            availability: 'planned',
            roadmapStage: 'Stage 44',
            description: 'Audio, video clipping, and media asset transformation pipelines.',
          },
          {
            id: 'creative-renders',
            title: 'Render Jobs',
            path: '/creative/renders',
            availability: 'planned',
            roadmapStage: 'Stage 44',
            description: 'Background GPU rendering queues and export jobs.',
          },
          {
            id: 'creative-assets',
            title: 'Generated Assets',
            path: '/creative/assets',
            availability: 'planned',
            roadmapStage: 'Stage 44',
            description: 'Creative asset vault and portfolio media library.',
          },
        ],
      },
      {
        id: 'research',
        title: 'Research & Markets',
        icon: ChartNoAxesCombined,
        path: '/research',
        group: 'workspace',
        availability: 'planned',
        roadmapStage: 'Stage 42',
        description: 'Web research synthesis, company intelligence, and industry talent trends.',
        badge: 'v2',
        children: [
          {
            id: 'research-projects',
            title: 'Research Projects',
            path: '/research/projects',
            availability: 'planned',
            roadmapStage: 'Stage 42',
            description: 'Deep-dive investigation folders and structured knowledge bases.',
          },
          {
            id: 'research-web',
            title: 'Web Research',
            path: '/research/web',
            availability: 'planned',
            roadmapStage: 'Stage 42',
            description: 'Autonomous multi-source search, document crawling, and summarization.',
          },
          {
            id: 'research-companies',
            title: 'Company Intelligence',
            path: '/research/companies',
            availability: 'planned',
            roadmapStage: 'Stage 42',
            description:
              'Dossiers on hiring companies: culture, financials, engineering tech stacks.',
          },
          {
            id: 'research-markets',
            title: 'Market Analysis',
            path: '/research/markets',
            availability: 'planned',
            roadmapStage: 'Stage 42',
            description: 'Compensation benchmarks and industry talent market supply/demand.',
          },
          {
            id: 'research-reports',
            title: 'Reports',
            path: '/research/reports',
            availability: 'planned',
            roadmapStage: 'Stage 42',
            description: 'Comprehensive research briefs and executive intelligence summaries.',
          },
          {
            id: 'research-watchlists',
            title: 'Watchlists',
            path: '/research/watchlists',
            availability: 'planned',
            roadmapStage: 'Stage 42',
            description: 'Monitored target companies, job feeds, and talent acquisition teams.',
          },
        ],
      },
      {
        id: 'workflows',
        title: 'Workflows',
        icon: Workflow,
        path: '/workflows',
        group: 'workspace',
        availability: 'planned',
        roadmapStage: 'Stage 46',
        description: 'Visual automation builder, scheduled recurring jobs, and multi-agent DAGs.',
        badge: 'v2',
        children: [
          {
            id: 'workflows-all',
            title: 'All Workflows',
            path: '/workflows/all',
            availability: 'planned',
            roadmapStage: 'Stage 46',
            description: 'Configured automated processes, triggers, and execution sequences.',
          },
          {
            id: 'workflows-active',
            title: 'Active Workflows',
            path: '/workflows/active',
            availability: 'planned',
            roadmapStage: 'Stage 46',
            description: 'Currently running automation pipelines and agent delegations.',
          },
          {
            id: 'workflows-builder',
            title: 'Automation Builder',
            path: '/workflows/builder',
            availability: 'planned',
            roadmapStage: 'Stage 46',
            description: 'Node-based visual workflow canvas for custom multi-agent tasks.',
          },
          {
            id: 'workflows-scheduled',
            title: 'Scheduled Tasks',
            path: '/workflows/scheduled',
            availability: 'planned',
            roadmapStage: 'Stage 46',
            description: 'Cron-style recurring routines: morning job scans, evening inbox triage.',
          },
          {
            id: 'workflows-history',
            title: 'Execution History',
            path: '/workflows/history',
            availability: 'planned',
            roadmapStage: 'Stage 46',
            description: 'Audit log of past workflow executions, durations, and outputs.',
          },
        ],
      },
    ],
  },
  {
    id: 'management',
    title: 'MANAGEMENT',
    order: 4,
    items: [
      {
        id: 'analytics',
        title: 'Analytics',
        icon: ChartColumn,
        path: '/analytics',
        group: 'management',
        availability: 'planned',
        roadmapStage: 'Stage 48',
        description: 'System-wide telemetry, agent conversion funnels, and resource metrics.',
        badge: 'v2',
        children: [
          {
            id: 'analytics-overview',
            title: 'Overview',
            path: '/analytics/overview',
            availability: 'planned',
            roadmapStage: 'Stage 48',
            description:
              'High-level KPI dashboard: applications sent, interviews booked, GPU usage.',
          },
          {
            id: 'analytics-jobs',
            title: 'Job Analytics',
            path: '/analytics/jobs',
            availability: 'planned',
            roadmapStage: 'Stage 48',
            description:
              'ATS conversion funnel: impressions -> matches -> applications -> screens.',
          },
          {
            id: 'analytics-agents',
            title: 'Agent Performance',
            path: '/analytics/agents',
            availability: 'planned',
            roadmapStage: 'Stage 48',
            description:
              'Individual agent token efficiency, success rates, and tool invocation stats.',
          },
          {
            id: 'analytics-workflows',
            title: 'Workflow Analytics',
            path: '/analytics/workflows',
            availability: 'planned',
            roadmapStage: 'Stage 48',
            description: 'Cadence, duration, bottleneck identification, and execution volume.',
          },
          {
            id: 'analytics-resources',
            title: 'System Resources',
            path: '/analytics/resources',
            availability: 'planned',
            roadmapStage: 'Stage 48',
            description: 'CPU, RAM, GPU VRAM allocation, and local disk WAL growth tracking.',
          },
        ],
      },
      {
        id: 'activity',
        title: 'Activity Logs',
        icon: History,
        path: '/activity',
        group: 'management',
        availability: 'planned',
        roadmapStage: 'Stage 47',
        description: 'Tamper-evident audit timeline, system events, and task execution trails.',
        badge: 'v2',
        children: [
          {
            id: 'activity-timeline',
            title: 'Activity Timeline',
            path: '/activity/timeline',
            availability: 'planned',
            roadmapStage: 'Stage 47',
            description: 'Unified chronological stream of all autonomous and user actions.',
          },
          {
            id: 'activity-agents',
            title: 'Agent Logs',
            path: '/activity/agents',
            availability: 'planned',
            roadmapStage: 'Stage 47',
            description: 'Internal agent reasoning traces, thought chains, and tool invocations.',
          },
          {
            id: 'activity-tasks',
            title: 'Task History',
            path: '/activity/tasks',
            availability: 'planned',
            roadmapStage: 'Stage 47',
            description: 'State transition logs and results for all background worker tasks.',
          },
          {
            id: 'activity-events',
            title: 'System Events',
            path: '/activity/events',
            availability: 'planned',
            roadmapStage: 'Stage 47',
            description: 'EventBus messages, SSE broadcast history, and daemon lifecycle events.',
          },
          {
            id: 'activity-errors',
            title: 'Error Logs',
            path: '/activity/errors',
            availability: 'planned',
            roadmapStage: 'Stage 47',
            description: 'Detailed exception tracebacks, sidecar supervisor restarts, and crashes.',
          },
          {
            id: 'activity-audit',
            title: 'Audit History',
            path: '/activity/audit',
            availability: 'planned',
            roadmapStage: 'Stage 47',
            description:
              'Cryptographically hashed immutable ledger of credential and data actions.',
          },
        ],
      },
      {
        id: 'integrations',
        title: 'Integrations',
        icon: Plug,
        path: '/integrations',
        group: 'management',
        availability: 'planned',
        roadmapStage: 'Stage 21',
        description: 'Third-party APIs, MCP servers, ATS integrations, and model providers.',
        badge: 'v2',
        children: [
          {
            id: 'integrations-connected',
            title: 'Connected Services',
            path: '/integrations/connected',
            availability: 'planned',
            roadmapStage: 'Stage 21',
            description: 'Active API connections, authenticated accounts, and tokens.',
          },
          {
            id: 'integrations-ai',
            title: 'AI Providers',
            path: '/integrations/ai',
            availability: 'planned',
            roadmapStage: 'Stage 11',
            description: 'OpenAI, Anthropic, Gemini, Ollama, and local ONNX runtime endpoints.',
          },
          {
            id: 'integrations-mcp',
            title: 'MCP Servers',
            path: '/integrations/mcp',
            availability: 'planned',
            roadmapStage: 'Stage 23',
            description: 'Model Context Protocol client configuration and external tool servers.',
          },
          {
            id: 'integrations-platforms',
            title: 'Job Platforms',
            path: '/integrations/platforms',
            availability: 'planned',
            roadmapStage: 'Stage 26',
            description: 'Connectors for LinkedIn, Indeed, Greenhouse, Lever, and Workday.',
          },
          {
            id: 'integrations-comms',
            title: 'Communication Services',
            path: '/integrations/comms',
            availability: 'planned',
            roadmapStage: 'Stage 36',
            description: 'Email, Telegram, WhatsApp, and notification dispatch services.',
          },
          {
            id: 'integrations-health',
            title: 'Integration Health',
            path: '/integrations/health',
            availability: 'planned',
            roadmapStage: 'Stage 21',
            description: 'Real-time heartbeat probes, rate-limit consumption, and latency scores.',
          },
        ],
      },
      {
        id: 'settings',
        title: 'Settings',
        icon: Settings,
        path: '/settings',
        group: 'management',
        availability: 'implemented',
        description:
          'System configuration, native desktop controls, database storage, and security.',
        children: [
          {
            id: 'settings-general',
            title: 'General',
            path: '/settings/general',
            availability: 'implemented',
            description:
              'Application name, default directories, localization, and language preferences.',
          },
          {
            id: 'settings-appearance',
            title: 'Appearance',
            path: '/settings/appearance',
            availability: 'implemented',
            description: 'Theme customization, density mode, font scaling, and motion preferences.',
          },
          {
            id: 'settings-ai',
            title: 'AI Providers & Models',
            path: '/settings/ai',
            availability: 'implemented',
            roadmapStage: 'Stage 11',
            description: 'Local Ollama runtime, cloud API providers, and RTX 4050 6GB VRAM limits.',
          },
          {
            id: 'settings-agents',
            title: 'Agent Preferences',
            path: '/settings/agents',
            availability: 'implemented',
            roadmapStage: 'Stage 12',
            description:
              '24-agent directory configuration, execution priorities, and approval gates.',
          },
          {
            id: 'settings-automation',
            title: 'Automation & Tasks',
            path: '/settings/automation',
            availability: 'implemented',
            description:
              'Worker concurrency bounds, task timeouts, retry limits, and dispatch rules.',
          },
          {
            id: 'settings-permissions',
            title: 'Authorization & Permissions',
            path: '/settings/permissions',
            availability: 'implemented',
            roadmapStage: 'Stage 14',
            description:
              '14-category action permission matrix, autonomy tiers, and killswitch hotkey.',
          },
          {
            id: 'settings-computer',
            title: 'Computer Control',
            path: '/settings/computer',
            availability: 'implemented',
            roadmapStage: 'Stage 16',
            description:
              'Structural UIA vs visual grounding, screenshot intervals, and process boundaries.',
          },
          {
            id: 'settings-integrations',
            title: 'Connected Services & MCP',
            path: '/settings/integrations',
            availability: 'implemented',
            roadmapStage: 'Stage 23',
            description:
              'Model Context Protocol tool servers, communication channels, and credentials.',
          },
          {
            id: 'settings-recruitment',
            title: 'Recruitment Preferences',
            path: '/settings/recruitment',
            availability: 'implemented',
            roadmapStage: 'Stage 25',
            description:
              'Target job titles, ATS match thresholds, salary minimums, and daily quotas.',
          },
          {
            id: 'settings-storage',
            title: 'Storage & Data',
            path: '/settings/storage',
            availability: 'implemented',
            description: 'SQLite database management, online snapshots, and verified restoration.',
          },
          {
            id: 'settings-notifications',
            title: 'Notifications',
            path: '/settings/notifications',
            availability: 'implemented',
            description: 'Windows Action Center toast routing, quiet hours, and alert filters.',
          },
          {
            id: 'settings-desktop',
            title: 'Desktop & Startup',
            path: '/settings/desktop',
            availability: 'implemented',
            description:
              'Close-to-tray, autostart on Windows boot, and process supervisor containment.',
          },
          {
            id: 'settings-security',
            title: 'Security & Privacy',
            path: '/settings/security',
            availability: 'implemented',
            description:
              'Windows DPAPI keystore, secret redaction, and local-first data protection.',
          },
          {
            id: 'settings-diagnostics',
            title: 'Backend Diagnostics',
            path: '/settings/diagnostics',
            availability: 'implemented',
            description:
              'Real-time task dispatch, SSE event streaming, and worker pool inspection.',
          },
          {
            id: 'settings-about',
            title: 'About & Updates',
            path: '/settings/about',
            availability: 'implemented',
            description:
              'Version information, Tauri runtime mode, open source licenses, and roadmap status.',
          },
        ],
      },
    ],
  },
  {
    id: 'development',
    title: 'DEVELOPMENT',
    order: 5,
    items: [
      {
        id: 'ai-gateway',
        title: 'AI Model Gateway',
        icon: Sparkles,
        path: '/ai',
        group: 'development',
        availability: 'implemented',
        roadmapStage: 'Stage 11',
        description:
          'Unified AI model gateway, local Ollama, cloud inference, streaming, routing, and GPU telemetry.',
        children: [
          {
            id: 'ai-playground',
            title: 'AI Playground',
            path: '/ai/playground',
            availability: 'implemented',
            roadmapStage: 'Stage 11',
            description: 'Direct interactive prompt testing, streaming responses, and cost accounting.',
          },
          {
            id: 'ai-models',
            title: 'Model Management',
            path: '/ai/models',
            availability: 'implemented',
            roadmapStage: 'Stage 11',
            description: 'Local Ollama & cloud model inventory, VRAM loading, and capability inspection.',
          },
          {
            id: 'ai-routing',
            title: 'Model Routing',
            path: '/ai/routing',
            availability: 'implemented',
            roadmapStage: 'Stage 11',
            description: '16 task category assignments, routing strategies, and live preview decisions.',
          },
          {
            id: 'ai-usage',
            title: 'AI Usage & Analytics',
            path: '/ai/usage',
            availability: 'implemented',
            roadmapStage: 'Stage 11',
            description: 'Token consumption, cost accounting, latency metrics, and recent inference requests.',
          },
        ],
      },
      {
        id: 'design-system',
        title: 'Design System',
        icon: Palette,
        path: '/design-system',
        group: 'development',
        availability: 'implemented',
        description:
          'Interactive showcase of all 20 design system aspects, tokens, and components.',
      },
      {
        id: 'diagnostics',
        title: 'Diagnostics & Tasks',
        icon: Activity,
        path: '/diagnostics',
        group: 'development',
        availability: 'implemented',
        description: 'Real-time task dispatch, SSE event streaming, and worker pool inspection.',
      },
      {
        id: 'desktop-diagnostics',
        title: 'Desktop Shell',
        icon: Monitor,
        path: '/desktop-diagnostics',
        group: 'development',
        availability: 'implemented',
        description:
          'Native Tauri host inspection, sidecar supervisor state, and Win32 Job Objects.',
      },
      {
        id: 'storage',
        title: 'Storage & Database',
        icon: Database,
        path: '/storage',
        group: 'development',
        availability: 'implemented',
        description: 'SQLite database management, online snapshots, and verified restoration.',
      },
    ],
  },
];

/**
 * Returns a flat array of all navigation items (both parents and nested children)
 * for search indexing, command palettes, and route matching.
 */
export function getAllNavigationItems(): Array<{
  id: string;
  title: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  group: string;
  availability: string;
  roadmapStage?: string;
  description?: string;
  parentTitle?: string;
}> {
  const result: Array<{
    id: string;
    title: string;
    path: string;
    icon: React.ComponentType<{ className?: string }>;
    group: string;
    availability: string;
    roadmapStage?: string;
    description?: string;
    parentTitle?: string;
  }> = [];

  for (const group of NAVIGATION_GROUPS) {
    for (const item of group.items) {
      result.push({
        id: item.id,
        title: item.title,
        path: item.path,
        icon: item.icon,
        group: group.title,
        availability: item.availability,
        roadmapStage: item.roadmapStage,
        description: item.description,
      });

      if (item.children) {
        for (const child of item.children) {
          result.push({
            id: child.id,
            title: child.title,
            path: child.path,
            icon: item.icon,
            group: group.title,
            availability: child.availability,
            roadmapStage: child.roadmapStage || item.roadmapStage,
            description: child.description,
            parentTitle: item.title,
          });
        }
      }
    }
  }

  return result;
}

/**
 * Resolves breadcrumb items for a given pathname.
 */
export function getBreadcrumbsForPath(pathname: string): BreadcrumbItem[] {
  // Normalize pathname: remove trailing slash if length > 1
  const cleanPath =
    pathname.length > 1 && pathname.endsWith('/') ? pathname.slice(0, -1) : pathname;

  if (cleanPath === '/' || cleanPath === '/dashboard') {
    return [
      { label: 'AUTONOM', path: '/dashboard' },
      { label: 'Command Center', isCurrent: true },
    ];
  }

  // Exact match search
  for (const group of NAVIGATION_GROUPS) {
    for (const item of group.items) {
      if (item.path === cleanPath) {
        return [
          { label: 'AUTONOM', path: '/dashboard' },
          { label: group.title },
          { label: item.title, isCurrent: true },
        ];
      }

      if (item.children) {
        for (const child of item.children) {
          if (child.path === cleanPath) {
            return [
              { label: 'AUTONOM', path: '/dashboard' },
              { label: item.title, path: item.path },
              { label: child.title, isCurrent: true },
            ];
          }
        }
      }
    }
  }

  // Match based on path segments
  const segments = cleanPath.split('/').filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [{ label: 'AUTONOM', path: '/dashboard' }];

  let currentPath = '';
  for (let i = 0; i < segments.length; i++) {
    currentPath += `/${segments[i]}`;
    const isLast = i === segments.length - 1;
    const label = segments[i].charAt(0).toUpperCase() + segments[i].slice(1).replace(/-/g, ' ');

    breadcrumbs.push({
      label,
      path: isLast ? undefined : currentPath,
      isCurrent: isLast,
    });
  }

  return breadcrumbs;
}

/**
 * Finds the top-level NavigationItem or ChildItem by exact path.
 */
export function findNavigationByPath(pathname: string): {
  item?: NavigationItem;
  child?: NavigationChildItem;
  group?: NavigationGroup;
} {
  const cleanPath =
    pathname.length > 1 && pathname.endsWith('/') ? pathname.slice(0, -1) : pathname;

  for (const group of NAVIGATION_GROUPS) {
    for (const item of group.items) {
      if (item.path === cleanPath || (cleanPath === '/' && item.path === '/dashboard')) {
        return { item, group };
      }
      if (item.children) {
        for (const child of item.children) {
          if (child.path === cleanPath) {
            return { item, child, group };
          }
        }
      }
    }
  }

  return {};
}
