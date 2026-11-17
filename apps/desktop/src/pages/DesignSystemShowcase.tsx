import * as React from 'react';
import {
  Palette,
  Type,
  Layout,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  Activity,
  Layers,
  BarChart3,
  Search,
  HardDrive,
  Cpu,
  Monitor,
  Eye,
  Settings,
  Shield,
  Sparkles,
} from 'lucide-react';
import { PageContainer } from '@/components/layout/PageContainer';
import { SectionHeader } from '@/components/layout/SectionHeader';
import {
  Button,
  Input,
  Textarea,
  Checkbox,
  Switch,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Badge,
  Progress,
  Separator,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui';
import { MetricCard } from '@/components/data-display/MetricCard';
import { StatusCard } from '@/components/data-display/StatusCard';
import { EmptyState } from '@/components/data-display/EmptyState';
import { DataTable } from '@/components/data-display/DataTable';
import { LineChart } from '@/components/charts/LineChart';
import { BarChart } from '@/components/charts/BarChart';
import { DonutChart } from '@/components/charts/DonutChart';
import { ErrorState } from '@/components/feedback/ErrorState';
import { LoadingState } from '@/components/feedback/LoadingState';
import { useToast } from '@/components/feedback/Toast';
import { useDensity } from '@/design-system/ThemeContext';
import { PALETTE } from '@/design-system/tokens';
import type { ColumnDef } from '@tanstack/react-table';

// Sample static demonstration data fixtures (clearly marked as sample data)
interface SampleJobRecord {
  id: string;
  title: string;
  company: string;
  matchScore: number;
  status: 'Ready' | 'Applied' | 'Reviewing' | 'Archived';
  date: string;
}

const SAMPLE_TABLE_DATA: SampleJobRecord[] = [
  { id: 'JOB-001', title: 'Principal Software Engineer', company: 'DeepMind Technologies', matchScore: 98, status: 'Ready', date: '2026-11-16' },
  { id: 'JOB-002', title: 'Autonomous Systems Architect', company: 'Anthropic Research', matchScore: 95, status: 'Applied', date: '2026-11-15' },
  { id: 'JOB-003', title: 'Senior Windows Systems Engineer', company: 'Microsoft Core OS', matchScore: 91, status: 'Reviewing', date: '2026-11-14' },
  { id: 'JOB-004', title: 'Full Stack Desktop Lead', company: 'Vercel Foundation', matchScore: 89, status: 'Applied', date: '2026-11-13' },
  { id: 'JOB-005', title: 'AI Automation Engineer', company: 'OpenAI Robotics', matchScore: 86, status: 'Archived', date: '2026-11-12' },
  { id: 'JOB-006', title: 'Rust Systems Specialist', company: 'Fastly Edge Cloud', matchScore: 94, status: 'Ready', date: '2026-11-11' },
  { id: 'JOB-007', title: 'Distributed Systems Engineer', company: 'Google Cloud Infra', matchScore: 92, status: 'Reviewing', date: '2026-11-10' },
];

const SAMPLE_LINE_CHART = [
  { name: 'Mon', jobs: 24, applications: 4 },
  { name: 'Tue', jobs: 42, applications: 8 },
  { name: 'Wed', jobs: 38, applications: 12 },
  { name: 'Thu', jobs: 65, applications: 15 },
  { name: 'Fri', jobs: 54, applications: 18 },
  { name: 'Sat', jobs: 30, applications: 6 },
  { name: 'Sun', jobs: 48, applications: 10 },
];

const SAMPLE_BAR_CHART = [
  { name: 'Direct', volume: 45 },
  { name: 'LinkedIn', volume: 82 },
  { name: 'Indeed', volume: 38 },
  { name: 'Greenhouse', volume: 64 },
  { name: 'Lever', volume: 29 },
];

const SAMPLE_DONUT_CHART = [
  { name: 'Submitted', value: 48, color: PALETTE.primary },
  { name: 'Under Review', value: 24, color: PALETTE.cyan },
  { name: 'Interviewing', value: 12, color: PALETTE.status.success },
  { name: 'Queued', value: 16, color: PALETTE.status.warning },
];

export const DesignSystemShowcase: React.FC = () => {
  const { density, toggleDensity } = useDensity();
  const toast = useToast();

  const [inputVal, setInputVal] = React.useState('autonom-agent-01');
  const [checkboxVal, setCheckboxVal] = React.useState(true);
  const [switchVal, setSwitchVal] = React.useState(true);
  const [selectVal, setSelectVal] = React.useState('normal');
  const [progressVal] = React.useState(68);
  const [dialogOpen, setDialogOpen] = React.useState(false);

  // Table columns definition
  const columns: ColumnDef<SampleJobRecord>[] = React.useMemo(
    () => [
      {
        accessorKey: 'id',
        header: 'ID',
        cell: (info) => <span className="font-mono-tech text-foreground-muted">{info.getValue() as string}</span>,
      },
      {
        accessorKey: 'title',
        header: 'Position Title',
        cell: (info) => <span className="font-semibold text-foreground">{info.getValue() as string}</span>,
      },
      {
        accessorKey: 'company',
        header: 'Company',
        cell: (info) => <span>{info.getValue() as string}</span>,
      },
      {
        accessorKey: 'matchScore',
        header: 'Match',
        cell: (info) => {
          const score = info.getValue() as number;
          return (
            <Badge variant={score >= 90 ? 'cyan' : 'primary'} size="sm" dot>
              {score}% Match
            </Badge>
          );
        },
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: (info) => {
          const status = info.getValue() as string;
          const variant =
            status === 'Ready'
              ? 'success'
              : status === 'Applied'
                ? 'primary'
                : status === 'Reviewing'
                  ? 'warning'
                  : 'inactive';
          return (
            <Badge variant={variant} size="sm" dot>
              {status}
            </Badge>
          );
        },
      },
      {
        accessorKey: 'date',
        header: 'Scouted Date',
        cell: (info) => <span className="font-tabular text-foreground-muted">{info.getValue() as string}</span>,
      },
    ],
    []
  );

  return (
    <TooltipProvider>
      <PageContainer
        title="UI/UX Design System & Component Showcase"
        subtitle="AUTONOM Phase 2 visual foundation: semantic design tokens, WCAG 2.2 AA accessibility, and dark dashboard primitives."
        badge={
          <Badge variant="cyan" size="md" dot pulse>
            Stage 06 Active
          </Badge>
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={toggleDensity}
              leftIcon={<Sliders className="w-3.5 h-3.5" />}
            >
              Density: <strong className="ml-1 capitalize">{density}</strong>
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => toast.success('Design system gallery verified!', 'Notification System')}
              leftIcon={<Sparkles className="w-3.5 h-3.5" />}
            >
              Fire Test Toast
            </Button>
          </div>
        }
      >
        {/* Notice Banner */}
        <div className="p-3 bg-surface-secondary border border-border/80 rounded-md text-xs text-foreground-secondary flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan shrink-0" />
            <span>
              <strong>Sample Data Notice:</strong> All tables, charts, and metrics on this page render labeled static demonstration fixtures. Real application monitors are under Diagnostics and Storage.
            </span>
          </div>
          <Badge variant="neutral" size="sm">
            Interactive Showcase
          </Badge>
        </div>

        {/* 1. PALETTE & SEMANTIC COLOR TOKENS */}
        <div className="space-y-3">
          <SectionHeader
            title="1. Semantic Color Token Palette"
            subtitle="Clean, modern dark Windows dashboard theme (#0B1220 navy, charcoal-blue surfaces, electric blue & cyan accents)"
            icon={<Palette className="w-4 h-4 text-cyan" />}
          />
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
            {[
              { label: 'Background', hex: '#0B1220', bgClass: 'bg-background' },
              { label: 'Surface Primary', hex: '#0F1828', bgClass: 'bg-surface' },
              { label: 'Surface Secondary', hex: '#121E30', bgClass: 'bg-surface-secondary' },
              { label: 'Surface Elevated', hex: '#1B2B42', bgClass: 'bg-surface-elevated' },
              { label: 'Primary Blue', hex: '#338BDF', bgClass: 'bg-primary' },
              { label: 'Cyan Accent', hex: '#51C8E8', bgClass: 'bg-cyan' },
              { label: 'Border Default', hex: '#2A3A52', bgClass: 'bg-border' },
              { label: 'Status Success', hex: '#37B89A', bgClass: 'bg-status-success' },
              { label: 'Status Warning', hex: '#E3AA54', bgClass: 'bg-status-warning' },
              { label: 'Status Error', hex: '#E36E78', bgClass: 'bg-status-error' },
              { label: 'Status Inactive', hex: '#64748B', bgClass: 'bg-status-inactive' },
              { label: 'Text Primary', hex: '#F0F5FC', bgClass: 'bg-[#F0F5FC]' },
              { label: 'Text Secondary', hex: '#A7B6CB', bgClass: 'bg-[#A7B6CB]' },
              { label: 'Text Muted', hex: '#8495AC', bgClass: 'bg-[#8495AC]' },
            ].map((token) => (
              <div
                key={token.label}
                className="p-3 bg-surface rounded-md border border-border flex flex-col gap-2"
              >
                <div className={`h-8 rounded-xs w-full ${token.bgClass} border border-border/40 shadow-inner`} />
                <div>
                  <div className="text-xs font-semibold text-foreground truncate">{token.label}</div>
                  <div className="text-[11px] font-mono text-foreground-muted">{token.hex}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 2. TYPOGRAPHY HIERARCHY */}
        <div className="space-y-3">
          <SectionHeader
            title="2. Typography Hierarchy & Metrics"
            subtitle="Segoe UI / Inter clean desktop scale with tabular numeric alignment for agent telemetry"
            icon={<Type className="w-4 h-4 text-primary" />}
          />
          <div className="p-4 bg-surface rounded-lg border border-border space-y-3">
            <div className="flex flex-col md:flex-row md:items-baseline justify-between border-b border-border/40 pb-2">
              <span className="text-compact-label text-foreground-muted">Page Title (24px / Bold)</span>
              <span className="text-page-title">AUTONOM Executive Command Center</span>
            </div>
            <div className="flex flex-col md:flex-row md:items-baseline justify-between border-b border-border/40 pb-2">
              <span className="text-compact-label text-foreground-muted">Section Title (17px / Semibold)</span>
              <span className="text-section-title">Autonomous Agent Swarm Orchestration</span>
            </div>
            <div className="flex flex-col md:flex-row md:items-baseline justify-between border-b border-border/40 pb-2">
              <span className="text-compact-label text-foreground-muted">Card Title (14px / Semibold)</span>
              <span className="text-card-title">Active Scout Worker #04</span>
            </div>
            <div className="flex flex-col md:flex-row md:items-baseline justify-between border-b border-border/40 pb-2">
              <span className="text-compact-label text-foreground-muted">Body Standard (13px / Regular)</span>
              <span className="text-body-standard">
                Continuous job discovery evaluating match vectors against encrypted career evidence.
              </span>
            </div>
            <div className="flex flex-col md:flex-row md:items-baseline justify-between border-b border-border/40 pb-2">
              <span className="text-compact-label text-foreground-muted">Technical Monospace & IDs</span>
              <span className="font-mono-tech text-cyan">tsk-89bf1a04 (127.0.0.1:8765 / WAL ACTIVE)</span>
            </div>
            <div className="flex flex-col md:flex-row md:items-baseline justify-between">
              <span className="text-compact-label text-foreground-muted">Tabular Figures (TNUM)</span>
              <span className="font-tabular text-sm font-semibold text-foreground">
                98,421 ops/sec — Latency: 0.042ms — Uptime: 148,290s
              </span>
            </div>
          </div>
        </div>

        {/* 3. BUTTON SYSTEM */}
        <div className="space-y-3">
          <SectionHeader
            title="3. Button System & Interactive States"
            subtitle="Consistent sizing (sm, md, lg, icon), states (default, hover, focus, disabled, loading)"
            icon={<Layout className="w-4 h-4 text-cyan" />}
          />
          <div className="p-4 bg-surface rounded-lg border border-border space-y-4">
            <div className="space-y-2">
              <span className="text-xs font-semibold text-foreground-muted uppercase tracking-wider">
                Action Variants:
              </span>
              <div className="flex flex-wrap items-center gap-2.5">
                <Button variant="primary">Primary Action</Button>
                <Button variant="cyan">Cyan Accent</Button>
                <Button variant="secondary">Secondary Surface</Button>
                <Button variant="outline">Outline Border</Button>
                <Button variant="ghost">Ghost Button</Button>
                <Button variant="destructive">Destructive Action</Button>
                <Button variant="link">Inline Link Style</Button>
              </div>
            </div>

            <Separator />

            <div className="space-y-2">
              <span className="text-xs font-semibold text-foreground-muted uppercase tracking-wider">
                Sizes & State Modifiers:
              </span>
              <div className="flex flex-wrap items-center gap-2.5">
                <Button size="sm" variant="primary">
                  Small (28px)
                </Button>
                <Button size="md" variant="primary">
                  Standard (36px)
                </Button>
                <Button size="lg" variant="primary">
                  Large (40px)
                </Button>
                <Button size="icon" variant="outline" aria-label="Settings action">
                  <Settings className="w-4 h-4" />
                </Button>
                <Button variant="primary" isLoading loadingText="Processing...">
                  Loading State
                </Button>
                <Button variant="primary" disabled>
                  Disabled Button
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* 4. FORM PRIMITIVES & INPUT CONTROLS */}
        <div className="space-y-3">
          <SectionHeader
            title="4. Form Primitives & Field Inputs"
            subtitle="Text fields, search inputs, passwords, textareas, custom selects, switches, and checkboxes"
            icon={<Sliders className="w-4 h-4 text-primary" />}
          />
          <div className="p-4 bg-surface rounded-lg border border-border grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="space-y-1.5">
              <label className="text-compact-label text-foreground-secondary">Text Input with Icon</label>
              <Input
                value={inputVal}
                onChange={(e) => setInputVal(e.target.value)}
                leftIcon={<Cpu className="w-4 h-4" />}
                placeholder="Enter agent name..."
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-compact-label text-foreground-secondary">Search Filter Field</label>
              <Input
                placeholder="Search jobs, skills, credentials..."
                leftIcon={<Search className="w-4 h-4" />}
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-compact-label text-foreground-secondary">Input with Error State</label>
              <Input defaultValue="invalid_token_format" hasError />
              <span className="text-[11px] text-status-error">Bearer key must contain 32 hex characters</span>
            </div>

            <div className="space-y-1.5">
              <label className="text-compact-label text-foreground-secondary">Accessible Select Menu</label>
              <Select value={selectVal} onValueChange={setSelectVal}>
                <SelectTrigger>
                  <SelectValue placeholder="Select priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low Priority</SelectItem>
                  <SelectItem value="normal">Normal Priority</SelectItem>
                  <SelectItem value="high">High Priority</SelectItem>
                  <SelectItem value="critical">Critical (Interrupt Active)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label className="text-compact-label text-foreground-secondary">Checkbox Control</label>
              <div className="flex items-center gap-2 pt-2">
                <Checkbox
                  id="chk-sample"
                  checked={checkboxVal}
                  onCheckedChange={(c) => setCheckboxVal(!!c)}
                />
                <label htmlFor="chk-sample" className="text-xs text-foreground cursor-pointer select-none">
                  Enable automatic application submission
                </label>
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-compact-label text-foreground-secondary">Switch Control</label>
              <div className="flex items-center justify-between pt-2">
                <span className="text-xs text-foreground">Minimize to System Tray</span>
                <Switch checked={switchVal} onCheckedChange={setSwitchVal} />
              </div>
            </div>

            <div className="col-span-full space-y-1.5">
              <label className="text-compact-label text-foreground-secondary">Multiline Textarea</label>
              <Textarea
                placeholder="Provide instructions, custom cover letter guidance, or recruiter notes..."
                defaultValue="Ensure all technical achievements highlight distributed backend architecture and Windows systems programming."
                rows={3}
              />
            </div>
          </div>
        </div>

        {/* 5. METRIC & STATUS CARDS */}
        <div className="space-y-3">
          <SectionHeader
            title="5. Cards & Operational Status Panels"
            subtitle="Compact information density with live status badges, tabular metrics, and key-value properties"
            icon={<Activity className="w-4 h-4 text-cyan" />}
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
            <MetricCard
              title="Discovered Postings"
              value={142}
              subtitle="Scouted across 5 ATS sources"
              icon={<Search className="w-4 h-4" />}
              trend={{ value: 18.4, isPositive: true }}
              variant="cyan"
            />
            <MetricCard
              title="Autonomous Applications"
              value={38}
              subtitle="Submitted with tailored resumes"
              icon={<CheckCircle2 className="w-4 h-4" />}
              trend={{ value: 6.2, isPositive: true }}
              variant="primary"
            />
            <MetricCard
              title="Active Agent Swarm"
              value={4}
              subtitle="Coordinating tasks concurrently"
              icon={<Cpu className="w-4 h-4" />}
              variant="default"
            />
            <MetricCard
              title="Average Latency"
              value="3.2ms"
              subtitle="SQLite WAL loopback query"
              icon={<Activity className="w-4 h-4" />}
              variant="success"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <StatusCard
              title="Python Backend Supervisor"
              icon={<HardDrive className="w-4 h-4 text-primary" />}
              statusBadge={{ label: 'Ready / WAL Active', variant: 'success', pulse: true }}
              properties={[
                { label: 'Process Mode', value: 'Packaged Sidecar Binary', mono: true },
                { label: 'Host Binding', value: '127.0.0.1:8765', mono: true },
                { label: 'Kernel Limits', value: 'JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE' },
                { label: 'Crash Recovery', value: 'Bounded Exponential Backoff (5 max)' },
              ]}
              footerActions={
                <Button size="sm" variant="outline">
                  Supervisor Telemetry
                </Button>
              }
            />

            <StatusCard
              title="Tauri Windows Shell Harness"
              icon={<Monitor className="w-4 h-4 text-cyan" />}
              statusBadge={{ label: 'Single Instance Locked', variant: 'cyan' }}
              properties={[
                { label: 'Native Architecture', value: 'Windows 11 x86_64 (MSVC)' },
                { label: 'Desktop Settings', value: '%LOCALAPPDATA%\\AUTONOM\\config', mono: true },
                { label: 'System Tray', value: 'Close-to-Tray Active' },
                { label: 'Toast Center', value: 'WinRT Native Action Center' },
              ]}
              footerActions={
                <Button size="sm" variant="outline">
                  Window Preferences
                </Button>
              }
            />
          </div>
        </div>

        {/* 6. DATA TABLE WITH TANSTACK TABLE */}
        <div className="space-y-3">
          <SectionHeader
            title="6. Data Table System (TanStack Table)"
            subtitle="Searchable, sortable, paginated operational table with compact density and status badges"
            icon={<Layers className="w-4 h-4 text-primary" />}
          />
          <DataTable
            columns={columns}
            data={SAMPLE_TABLE_DATA}
            searchPlaceholder="Search candidate jobs by title, company, or status..."
            pageSize={4}
          />
        </div>

        {/* 7. CHARTS & VISUALIZATIONS */}
        <div className="space-y-3">
          <SectionHeader
            title="7. Analytics & Data Visualizations (Recharts)"
            subtitle="Dark theme chart components with responsive scaling, custom tooltips, and restrained color accents"
            icon={<BarChart3 className="w-4 h-4 text-cyan" />}
          />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <LineChart
              title="Job Discovery vs Applications"
              subtitle="Sample 7-day trend analysis"
              data={SAMPLE_LINE_CHART}
              series={[
                { dataKey: 'jobs', name: 'Scouted Jobs', color: PALETTE.cyan },
                { dataKey: 'applications', name: 'Applications Submitted', color: PALETTE.primary },
              ]}
              height={200}
            />

            <BarChart
              title="Volume by Source Platform"
              subtitle="Sample distribution metrics"
              data={SAMPLE_BAR_CHART}
              series={[{ dataKey: 'volume', name: 'Job Listings', color: PALETTE.primary }]}
              height={200}
            />

            <DonutChart
              title="Pipeline Application Status"
              subtitle="Sample stage breakdown"
              data={SAMPLE_DONUT_CHART}
              height={200}
            />
          </div>
        </div>

        {/* 8. STATUS INDICATORS & PROGRESS */}
        <div className="space-y-3">
          <SectionHeader
            title="8. Status Badges & Progress Indicators"
            subtitle="Non-color dependent status communication with explicit text and pulse modifiers"
            icon={<Activity className="w-4 h-4 text-primary" />}
          />
          <div className="p-4 bg-surface rounded-lg border border-border space-y-4">
            <div className="space-y-2">
              <span className="text-xs font-semibold text-foreground-muted uppercase tracking-wider">
                Status Lifecycle Badges:
              </span>
              <div className="flex flex-wrap gap-2">
                <Badge variant="success" dot pulse>
                  Ready / Online
                </Badge>
                <Badge variant="primary" dot pulse>
                  Running Task
                </Badge>
                <Badge variant="cyan" dot>
                  Queued (Position #2)
                </Badge>
                <Badge variant="warning" dot>
                  Waiting for User Approval
                </Badge>
                <Badge variant="error" dot>
                  Execution Failed
                </Badge>
                <Badge variant="inactive" dot>
                  Service Stopped
                </Badge>
                <Badge variant="neutral">Neutral Info</Badge>
              </div>
            </div>

            <Separator />

            <div className="space-y-3">
              <div className="flex justify-between text-xs text-foreground-secondary">
                <span>Task Execution Progress ({progressVal}%)</span>
                <span className="font-tabular text-foreground">{progressVal}/100 Units</span>
              </div>
              <Progress value={progressVal} variant="primary" />

              <div className="flex justify-between text-xs text-foreground-secondary pt-1">
                <span>Indeterminate Agent Synthesis</span>
                <span className="text-cyan text-[11px] font-mono">THINKING_ACTIVE</span>
              </div>
              <Progress isIndeterminate variant="cyan" size="sm" />
            </div>
          </div>
        </div>

        {/* 9. DIALOGS, DROPDOWNS & TOOLTIPS */}
        <div className="space-y-3">
          <SectionHeader
            title="9. Dialogs, Overlays & Dropdown Menus"
            subtitle="Accessible Radix UI primitives with focus trapping, ESC key dismissal, and backdrop blur"
            icon={<Shield className="w-4 h-4 text-cyan" />}
          />
          <div className="p-4 bg-surface rounded-lg border border-border flex flex-wrap items-center gap-3">
            {/* Modal Dialog */}
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="primary">Open Accessible Modal</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Autonomous Action Confirmation</DialogTitle>
                  <DialogDescription>
                    Review the parameters below before authorizing the agent swarm to submit this application.
                  </DialogDescription>
                </DialogHeader>
                <div className="p-3 bg-surface rounded-md border border-border text-xs space-y-2">
                  <div className="flex justify-between">
                    <span className="text-foreground-muted">Target Company:</span>
                    <span className="font-semibold text-foreground">DeepMind Technologies</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-foreground-muted">Tailored Resume:</span>
                    <span className="text-cyan font-mono-tech">resume_deepmind_2026.pdf</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-foreground-muted">Required Approvals:</span>
                    <span className="text-status-warning font-semibold">Compensation Attestation</span>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" size="sm" onClick={() => setDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => {
                      setDialogOpen(false);
                      toast.success('Application authorization confirmed.');
                    }}
                  >
                    Authorize Submission
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            {/* Dropdown Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="secondary">Actions Dropdown Menu</Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start">
                <DropdownMenuItem onClick={() => toast.info('Exporting task audit logs...')}>
                  Export Task Audit Logs
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => toast.info('Triggering manual backup snapshot...')}>
                  Trigger Online Backup
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem destructive onClick={() => toast.error('Emergency task abort dispatched.')}>
                  Emergency Swarm Abort
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Tooltip Sample */}
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" size="icon" aria-label="System Information">
                  <Eye className="w-4 h-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                Accessible tooltip with subtle shadow and automatic positioning
              </TooltipContent>
            </Tooltip>
          </div>
        </div>

        {/* 10. FEEDBACK STATES: ERROR, LOADING, EMPTY */}
        <div className="space-y-3">
          <SectionHeader
            title="10. Feedback States: Errors, Loading & Empty Fallbacks"
            subtitle="Standardized communication when systems fail, load, or contain zero records"
            icon={<AlertTriangle className="w-4 h-4 text-primary" />}
          />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <ErrorState
              title="Sidecar Process Unreachable"
              message="The local loopback connection at 127.0.0.1:8765 timed out. Supervisor is restarting child process."
              onRetry={() => toast.info('Retrying connection probe...')}
            />

            <div className="p-4 bg-surface rounded-lg border border-border flex items-center justify-center">
              <LoadingState message="Synchronizing agent knowledge graphs..." />
            </div>

            <EmptyState
              title="No Active Applications"
              description="No applications are currently awaiting manual intervention or user authorization."
              actionText="Scout New Positions"
              onAction={() => toast.info('Initiating scout agent dispatch...')}
            />
          </div>
        </div>
      </PageContainer>
    </TooltipProvider>
  );
};

