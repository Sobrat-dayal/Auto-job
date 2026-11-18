import * as React from 'react';
import {
  Play,
  Square,
  Globe,
  CheckCircle2,
  AlertCircle,
  Monitor,
  ExternalLink,
  RefreshCw,
  Layers,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  BrowserRuntimeStatus,
  BrowserSessionSummary,
  BrowserSessionCreateRequest,
} from '@autonom/shared-types';

interface BrowserOverviewTabProps {
  runtimeStatus: BrowserRuntimeStatus | null;
  sessions: BrowserSessionSummary[];
  onRefresh: () => void;
  onLaunchSession: (req: BrowserSessionCreateRequest) => Promise<void>;
  onCloseSession: (id: string) => Promise<void>;
  onSelectSession: (id: string) => void;
  isLoading: boolean;
}

export const BrowserOverviewTab: React.FC<BrowserOverviewTabProps> = ({
  runtimeStatus,
  sessions,
  onRefresh,
  onLaunchSession,
  onCloseSession,
  onSelectSession,
  isLoading,
}) => {
  const [isHeadless, setIsHeadless] = React.useState<boolean>(true);
  const [selectedBrowser, setSelectedBrowser] = React.useState<string>('chromium');
  const [isLaunching, setIsLaunching] = React.useState<boolean>(false);

  const handleLaunch = async () => {
    setIsLaunching(true);
    try {
      await onLaunchSession({
        browser_type: selectedBrowser as any,
        is_headless: isHeadless,
        viewport_width: 1280,
        viewport_height: 800,
      });
    } finally {
      setIsLaunching(false);
    }
  };

  const activeSessions = sessions.filter((s) => s.status === 'running');

  return (
    <div className="space-y-6">
      {/* Top Telemetry Row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="border-border/60 bg-card/60">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-medium uppercase tracking-wider">
              Playwright Runtime
            </CardDescription>
            <CardTitle className="text-2xl font-bold flex items-center gap-2">
              {runtimeStatus?.playwright_available ? (
                <>
                  <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                  <span className="text-emerald-400">Operational</span>
                </>
              ) : (
                <>
                  <AlertCircle className="h-5 w-5 text-amber-400" />
                  <span className="text-amber-400">Initializing</span>
                </>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            Python 3.12 • Windows 11 Native Process
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-card/60">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-medium uppercase tracking-wider">
              Installed Engines
            </CardDescription>
            <CardTitle className="text-2xl font-bold flex items-center gap-2">
              <Globe className="h-5 w-5 text-cyan-400" />
              <span>{runtimeStatus?.installed_browsers.length || 0} Engines</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground flex gap-1 flex-wrap">
            {runtimeStatus?.installed_browsers.map((b) => (
              <Badge key={b} variant="neutral" className="text-[10px] uppercase font-mono">
                {b}
              </Badge>
            ))}
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-card/60">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-medium uppercase tracking-wider">
              Active Sessions
            </CardDescription>
            <CardTitle className="text-2xl font-bold flex items-center gap-2">
              <Layers className="h-5 w-5 text-purple-400" />
              <span>
                {activeSessions.length} / {runtimeStatus?.max_concurrent_sessions || 5}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            Isolated browser contexts in memory
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-card/60">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-medium uppercase tracking-wider">
              Security Boundary
            </CardDescription>
            <CardTitle className="text-2xl font-bold flex items-center gap-2">
              <span className="text-emerald-400">Stage 14 Gate</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            SSRF Protection & Submission Approval
          </CardContent>
        </Card>
      </div>

      {/* Session Launcher & Control Bar */}
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <Play className="h-4 w-4 text-primary" />
                Launch Browser Session
              </CardTitle>
              <CardDescription className="text-xs">
                Spawns a clean, sandboxed browser context with dedicated cookies and download handlers.
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={onRefresh}
              disabled={isLoading}
              className="gap-1.5 text-xs"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center justify-between gap-4 rounded-lg border border-border/40 bg-background/50 p-4">
            <div className="flex flex-wrap items-center gap-6">
              <div className="space-y-1">
                <label className="text-xs font-medium text-muted-foreground">Browser Engine</label>
                <div className="flex items-center gap-2">
                  {['chromium', 'msedge', 'chrome'].map((engine) => (
                    <Button
                      key={engine}
                      type="button"
                      variant={selectedBrowser === engine ? 'primary' : 'outline'}
                      size="sm"
                      onClick={() => setSelectedBrowser(engine)}
                      className="text-xs capitalize font-mono h-8"
                    >
                      {engine}
                    </Button>
                  ))}
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-muted-foreground">Headless Mode</label>
                <div className="flex items-center gap-2 pt-1">
                  <Switch checked={isHeadless} onCheckedChange={setIsHeadless} id="headless-switch" />
                  <label htmlFor="headless-switch" className="text-xs cursor-pointer font-mono">
                    {isHeadless ? 'Headless (Fast / Background)' : 'Headed (Visible Window)'}
                  </label>
                </div>
              </div>
            </div>

            <Button
              onClick={handleLaunch}
              disabled={isLaunching || isLoading}
              className="gap-2 bg-primary text-primary-foreground font-semibold h-9 px-5"
            >
              <Play className="h-4 w-4 fill-current" />
              {isLaunching ? 'Launching...' : 'Start New Session'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Sessions Table / Cards */}
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <Monitor className="h-4 w-4 text-cyan-400" />
                Managed Browser Sessions
              </CardTitle>
              <CardDescription className="text-xs">
                Active and completed browser contexts managed by the runtime service.
              </CardDescription>
            </div>
            <Badge variant="outline" className="font-mono text-xs">
              {sessions.length} total recorded
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {sessions.length === 0 ? (
            <div className="py-12 text-center text-muted-foreground">
              <Globe className="h-10 w-10 mx-auto mb-3 opacity-30" />
              <p className="text-sm font-medium">No browser sessions launched yet</p>
              <p className="text-xs mt-1">
                Launch a session above to begin automated web navigation and DOM inspection.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {sessions.map((s) => (
                <div
                  key={s.id}
                  className="flex items-center justify-between p-3.5 rounded-lg border border-border/40 bg-background/40 hover:bg-background/80 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className={`h-2.5 w-2.5 rounded-full ${
                        s.status === 'running' ? 'bg-emerald-400 animate-pulse' : 'bg-muted-foreground'
                      }`}
                    />
                    <div className="space-y-0.5 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-semibold text-foreground">
                          {s.id.slice(0, 8)}
                        </span>
                        <Badge
                          variant={s.status === 'running' ? 'success' : 'neutral'}
                          className="text-[10px] uppercase font-mono"
                        >
                          {s.status}
                        </Badge>
                        <Badge variant="outline" className="text-[10px] capitalize font-mono">
                          {s.browser_type}
                        </Badge>
                        {s.is_headless && (
                          <Badge variant="outline" className="text-[10px] text-muted-foreground">
                            headless
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground truncate">
                        {s.current_url ? (
                          <span className="font-mono text-primary/80">{s.current_url}</span>
                        ) : (
                          'about:blank'
                        )}{' '}
                        {s.current_title && `• "${s.current_title}"`}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onSelectSession(s.id)}
                      className="text-xs gap-1.5 h-8"
                    >
                      <ExternalLink className="h-3.5 w-3.5" />
                      Inspect & Control
                    </Button>
                    {s.status === 'running' && (
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => onCloseSession(s.id)}
                        className="text-xs gap-1.5 h-8"
                      >
                        <Square className="h-3 w-3 fill-current" />
                        Close
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
