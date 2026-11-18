import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Monitor, ShieldCheck, Video } from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleTabs,
  ModuleEmptyState,
} from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BrowserWorkspace } from './browser/BrowserWorkspace';
import { DesktopWorkspace } from './desktop/DesktopWorkspace';
import { VisualWorkspace } from './visual/VisualWorkspace';
import { HybridWorkspace } from './hybrid/HybridWorkspace';
import { WorkflowReliabilityWorkspace } from './reliability/WorkflowReliabilityWorkspace';

export const ComputerWorkspace: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const getInitialTab = (): string => {
    if (
      location.pathname.includes('/computer/reliability') ||
      location.pathname.includes('/computer/recordings') ||
      location.pathname.includes('/computer/procedures') ||
      location.pathname.includes('/computer/replay') ||
      location.pathname.includes('/computer/checkpoints') ||
      location.pathname.includes('/computer/recovery')
    ) {
      return 'reliability';
    }
    if (location.pathname.includes('/computer/hybrid')) return 'hybrid';
    if (location.pathname.includes('/computer/visual')) return 'visual';
    if (location.pathname.includes('/computer/desktop')) return 'desktop';
    if (location.pathname.includes('/computer/browser')) return 'browser';
    if (location.pathname.includes('/computer/live')) return 'live';
    if (location.pathname.includes('/computer/tasks')) return 'tasks';
    if (location.pathname.includes('/computer/history')) return 'history';
    if (location.pathname.includes('/computer/permissions')) return 'permissions';
    return 'desktop';
  };

  const [activeTab, setActiveTab] = React.useState<string>(getInitialTab());

  React.useEffect(() => {
    setActiveTab(getInitialTab());
  }, [location.pathname]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === 'reliability') navigate('/computer/reliability');
    else if (tabId === 'hybrid') navigate('/computer/hybrid');
    else if (tabId === 'visual') navigate('/computer/visual');
    else if (tabId === 'desktop') navigate('/computer/desktop');
    else if (tabId === 'live') navigate('/computer/live');
    else navigate(`/computer/${tabId}`);
  };

  const tabs = [
    { id: 'reliability', label: 'Workflow Reliability & Recording', badge: 'Stage 20 Active' },
    { id: 'hybrid', label: 'Hybrid Computer Engine', badge: 'Stage 19 Active' },
    { id: 'visual', label: 'Visual Automation & OCR', badge: 'Stage 18 Active' },
    { id: 'desktop', label: 'Windows Structural Automation', badge: 'Stage 17 Active' },
    { id: 'browser', label: 'Chromium Browser Automation', badge: 'Stage 16 Active' },
    { id: 'live', label: 'Live Desktop Viewport' },
    { id: 'tasks', label: 'Computer Tasks', badge: 0 },
    { id: 'history', label: 'Action & Keystroke Logs' },
    { id: 'permissions', label: 'Safety Boundaries & Killswitch' },
  ];

  return (
    <ModulePage>
      <ModuleHeader
        title="Computer Control & Automation"
        description="Unified hybrid computer automation: Intelligent routing between Chromium browser DOM, Microsoft UI Automation structural control, Win32 messaging, visual coordinate grounding, structured action recording, and state-aware crash recovery."
        icon={Monitor}
        stageTag="Stage 20 Production Active"
        badgeLabel="Stage 18 Production Active"
        badgeVariant="outline"
        actions={
          <div className="flex items-center gap-2">
            <Badge
              variant="outline"
              className="border-slate-700 bg-slate-800/40 text-xs font-mono text-slate-300"
            >
              Stage 17 Production Active
            </Badge>
            <Badge
              variant="outline"
              className="border-purple-500/30 bg-purple-500/10 text-xs font-mono text-purple-400"
            >
              Stage 19 Production Active
            </Badge>
            <Badge
              variant="outline"
              className="border-emerald-500/30 bg-emerald-500/10 text-xs font-mono text-emerald-400"
            >
              Reliability: Operational
            </Badge>
            <Badge
              variant="outline"
              className="border-blue-500/30 bg-blue-500/10 text-xs font-mono text-blue-400"
            >
              Hybrid Engine: Operational
            </Badge>
            <Badge
              variant="outline"
              className="border-purple-500/30 bg-purple-500/10 text-xs font-mono text-purple-400"
            >
              Visual Engine: Operational
            </Badge>
            <Badge
              variant="outline"
              className="border-cyan-500/30 bg-cyan-500/10 text-xs font-mono text-cyan-400"
            >
              UIA: Operational
            </Badge>
            <Badge
              variant="outline"
              className="border-emerald-500/30 bg-emerald-500/10 text-xs font-mono text-emerald-400"
            >
              Browser: Operational
            </Badge>
            <Badge
              variant="outline"
              className="border-amber-500/30 bg-amber-500/10 text-xs font-mono text-amber-400"
            >
              Killswitch: Pause / Break
            </Badge>
          </div>
        }
      />

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={handleTabChange} />

      {activeTab === 'reliability' && <WorkflowReliabilityWorkspace />}
      {activeTab === 'hybrid' && <HybridWorkspace />}
      {activeTab === 'visual' && <VisualWorkspace />}
      {activeTab === 'desktop' && <DesktopWorkspace />}
      {activeTab === 'browser' && <BrowserWorkspace />}

      {activeTab === 'live' && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-4">
            <Card className="border-border/60 bg-card/60">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <CardTitle className="text-sm font-semibold flex items-center gap-2">
                      <Video className="h-4 w-4 text-primary" />
                      Visual Grounding Canvas Viewport
                    </CardTitle>
                    <CardDescription className="text-xs">
                      Simulated screen capture preview with element bounding boxes
                    </CardDescription>
                  </div>
                  <Badge variant="outline" className="text-xs font-mono">
                    1920x1080 • Primary Monitor
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="relative aspect-video w-full overflow-hidden rounded-lg border border-border/80 bg-background/90 flex flex-col items-center justify-center p-6 text-center">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-muted/60 text-muted-foreground ring-1 ring-border">
                    <Monitor className="h-6 w-6" />
                  </div>
                  <h4 className="mt-3 text-sm font-semibold text-foreground">
                    Viewport Inactive (Stage 17)
                  </h4>
                  <p className="mt-1 max-w-sm text-xs text-muted-foreground">
                    Direct screen stream and action bounding box overlays will render here once the
                    Stage 17 visual perception engine is initialized.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-4">
            <Card className="border-border/60 bg-card/60">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-status-success" />
                  Safety & Guardrail Controls
                </CardTitle>
                <CardDescription className="text-xs">
                  Physical limits and authorization boundaries
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 text-xs">
                <div className="rounded-lg border border-border/40 bg-background/50 p-3">
                  <span className="font-semibold text-foreground">Global Panic Killswitch</span>
                  <p className="mt-0.5 text-muted-foreground">
                    Pressing{' '}
                    <kbd className="rounded bg-muted px-1.5 py-0.5 font-mono text-[11px]">
                      Pause
                    </kbd>{' '}
                    or{' '}
                    <kbd className="rounded bg-muted px-1.5 py-0.5 font-mono text-[11px]">
                      Ctrl+Alt+Esc
                    </kbd>{' '}
                    immediately detaches OS input hooks.
                  </p>
                </div>
                <div className="rounded-lg border border-border/40 bg-background/50 p-3">
                  <span className="font-semibold text-foreground">
                    Human-in-the-Loop Intercepts
                  </span>
                  <p className="mt-0.5 text-muted-foreground">
                    Financial transactions, credential reveals, and irreversible deletions require
                    explicit UI confirmation.
                  </p>
                </div>
                <div className="rounded-lg border border-border/40 bg-background/50 p-3">
                  <span className="font-semibold text-foreground">Dual-Modality Arbitration</span>
                  <p className="mt-0.5 text-muted-foreground">
                    Prefers UIA accessibility tree selectors for deterministic precision; falls back
                    to visual vision models.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {activeTab !== 'live' &&
        activeTab !== 'browser' &&
        activeTab !== 'desktop' &&
        activeTab !== 'visual' &&
        activeTab !== 'hybrid' &&
        activeTab !== 'reliability' && (
          <ModuleEmptyState
            title={`No active ${activeTab} data`}
            description={`Computer control ${activeTab} capabilities will become fully interactive when Stage 17-20 engines are operational.`}
          />
        )}
    </ModulePage>
  );
};

export default ComputerWorkspace;
