import * as React from 'react';
import {
  Globe,
  ArrowRight,
  Camera,
  MousePointer,
  Type,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Plus,
  X,
  ShieldCheck,
  ShieldAlert,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  BrowserSessionResponse,
  BrowserNavigateRequest,
  BrowserActionRequest,
  BrowserScreenshotResponse,
  BrowserActionResponse,
} from '@autonom/shared-types';

interface BrowserLiveControllerTabProps {
  session: BrowserSessionResponse | null;
  onNavigate: (sessionId: string, req: BrowserNavigateRequest) => Promise<void>;
  onExecuteAction: (sessionId: string, req: BrowserActionRequest) => Promise<BrowserActionResponse>;
  onCaptureScreenshot: (sessionId: string) => Promise<BrowserScreenshotResponse>;
  onSwitchTab: (sessionId: string, tabId: string) => Promise<void>;
  onCreateTab: (sessionId: string, url?: string) => Promise<void>;
  onCloseTab: (sessionId: string, tabId: string) => Promise<void>;
  isLoading: boolean;
}

export const BrowserLiveControllerTab: React.FC<BrowserLiveControllerTabProps> = ({
  session,
  onNavigate,
  onExecuteAction,
  onCaptureScreenshot,
  onSwitchTab,
  onCreateTab,
  onCloseTab,
  isLoading,
}) => {
  const [urlInput, setUrlInput] = React.useState<string>('https://example.com');
  const [clickLocator, setClickLocator] = React.useState<string>('role=link[name="More information..."]');
  const [fillLocator, setFillLocator] = React.useState<string>('input[name="search"]');
  const [fillValue, setFillValue] = React.useState<string>('Senior Python Engineer');
  const [screenshotData, setScreenshotData] = React.useState<BrowserScreenshotResponse | null>(null);
  const [actionHistory, setActionHistory] = React.useState<BrowserActionResponse[]>([]);
  const [isNavigating, setIsNavigating] = React.useState<boolean>(false);
  const [isActing, setIsActing] = React.useState<boolean>(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  const activeTab = session?.tabs.find((t) => t.is_active) || session?.tabs[0];

  React.useEffect(() => {
    if (activeTab?.url && activeTab.url !== 'about:blank') {
      setUrlInput(activeTab.url);
    }
  }, [activeTab?.id, activeTab?.url]);

  const handleNavigate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!session || !urlInput.trim()) return;
    setIsNavigating(true);
    setErrorMessage(null);
    try {
      await onNavigate(session.id, {
        url: urlInput.trim(),
        tab_id: activeTab?.id,
      });
      // Capture preview screenshot automatically
      const shot = await onCaptureScreenshot(session.id);
      setScreenshotData(shot);
    } catch (err: any) {
      setErrorMessage(err.message || 'Navigation failed.');
    } finally {
      setIsNavigating(false);
    }
  };

  const handleClickAction = async () => {
    if (!session || !clickLocator.trim()) return;
    setIsActing(true);
    setErrorMessage(null);
    try {
      const res = await onExecuteAction(session.id, {
        action_type: 'click',
        target_locator: clickLocator.trim(),
        tab_id: activeTab?.id,
      });
      setActionHistory((prev) => [res, ...prev.slice(0, 9)]);
      // Auto-refresh screenshot
      const shot = await onCaptureScreenshot(session.id);
      setScreenshotData(shot);
    } catch (err: any) {
      setErrorMessage(err.message || 'Click action failed.');
    } finally {
      setIsActing(false);
    }
  };

  const handleFillAction = async () => {
    if (!session || !fillLocator.trim()) return;
    setIsActing(true);
    setErrorMessage(null);
    try {
      const res = await onExecuteAction(session.id, {
        action_type: 'fill',
        target_locator: fillLocator.trim(),
        tab_id: activeTab?.id,
        parameters: { value: fillValue },
      });
      setActionHistory((prev) => [res, ...prev.slice(0, 9)]);
      // Auto-refresh screenshot
      const shot = await onCaptureScreenshot(session.id);
      setScreenshotData(shot);
    } catch (err: any) {
      setErrorMessage(err.message || 'Fill action failed.');
    } finally {
      setIsActing(false);
    }
  };

  const handleTakeScreenshot = async () => {
    if (!session) return;
    try {
      const shot = await onCaptureScreenshot(session.id);
      setScreenshotData(shot);
    } catch (err: any) {
      setErrorMessage(err.message || 'Screenshot failed.');
    }
  };

  if (!session) {
    return (
      <Card className="border-border/60 bg-card/60">
        <CardContent className="py-16 text-center text-muted-foreground">
          <Globe className="h-10 w-10 mx-auto mb-3 opacity-30" />
          <p className="text-sm font-medium">No session selected</p>
          <p className="text-xs mt-1">
            Select or launch a browser session from the Overview tab to use the controller.
          </p>
        </CardContent>
      </Card>
    );
  }

  const isSecure = urlInput.startsWith('https://');

  return (
    <div className="space-y-6">
      {/* Session & Tab Bar */}
      <div className="flex items-center justify-between gap-4 p-3 rounded-lg border border-border/60 bg-card/60">
        <div className="flex items-center gap-2 overflow-x-auto min-w-0">
          <Badge variant="outline" className="font-mono text-xs text-primary flex-shrink-0">
            Session: {session.id.slice(0, 8)}
          </Badge>
          <div className="flex items-center gap-1.5 min-w-0">
            {session.tabs.map((tab) => (
              <div
                key={tab.id}
                onClick={() => onSwitchTab(session.id, tab.id)}
                className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs cursor-pointer border transition-colors ${
                  tab.is_active
                    ? 'border-primary/50 bg-primary/10 text-foreground font-medium'
                    : 'border-border/40 bg-background/30 text-muted-foreground hover:bg-background/60'
                }`}
              >
                <span className="truncate max-w-[140px]">
                  {tab.title || tab.url || `Tab ${tab.tab_index + 1}`}
                </span>
                {session.tabs.length > 1 && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onCloseTab(session.id, tab.id);
                    }}
                    className="opacity-60 hover:opacity-100"
                  >
                    <X className="h-3 w-3" />
                  </button>
                )}
              </div>
            ))}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onCreateTab(session.id)}
              className="h-6 w-6 p-0 text-muted-foreground hover:text-foreground"
            >
              <Plus className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <Badge variant="neutral" className="font-mono text-xs">
            {session.viewport_width}x{session.viewport_height}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={handleTakeScreenshot}
            className="text-xs gap-1.5 h-8"
          >
            <Camera className="h-3.5 w-3.5 text-primary" />
            Snapshot
          </Button>
        </div>
      </div>

      {/* Address Bar */}
      <form onSubmit={handleNavigate} className="flex items-center gap-2">
        <div className="relative flex-1">
          <div className="absolute left-3 top-1/2 -translate-y-1/2 flex items-center">
            {isSecure ? (
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
            ) : (
              <ShieldAlert className="h-4 w-4 text-amber-400" />
            )}
          </div>
          <Input
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            placeholder="Enter destination URL (e.g. https://jobs.github.com)..."
            className="pl-9 font-mono text-xs h-10 bg-background/60"
          />
        </div>
        <Button
          type="submit"
          disabled={isNavigating || isLoading}
          className="gap-1.5 h-10 px-5 font-semibold"
        >
          {isNavigating ? <RefreshCw className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />}
          Navigate
        </Button>
      </form>

      {errorMessage && (
        <div className="flex items-center gap-2 p-3 rounded-lg border border-destructive/50 bg-destructive/10 text-xs text-destructive">
          <AlertTriangle className="h-4 w-4 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Interactive Screen Preview & Action Dispatcher Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Visual Viewport Canvas */}
        <Card className="lg:col-span-2 border-border/60 bg-card/60">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <Globe className="h-4 w-4 text-cyan-400" />
                Live Page Viewport
              </CardTitle>
              <Badge variant="outline" className="font-mono text-[10px]">
                {activeTab?.status || 'ready'}
              </Badge>
            </div>
            <CardDescription className="text-xs truncate font-mono text-primary/80">
              {activeTab?.url || 'about:blank'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="relative aspect-[16/10] w-full rounded-lg border border-border/60 bg-black/40 overflow-hidden flex items-center justify-center">
              {screenshotData?.thumbnail_base64 ? (
                <img
                  src={screenshotData.thumbnail_base64}
                  alt="Browser Viewport"
                  className="w-full h-full object-contain"
                />
              ) : (
                <div className="text-center text-muted-foreground p-6">
                  <Camera className="h-8 w-8 mx-auto mb-2 opacity-30" />
                  <p className="text-xs font-mono">No screenshot rendered</p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleTakeScreenshot}
                    className="mt-3 text-xs gap-1.5"
                  >
                    Capture Viewport
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Action Controls & Dispatcher */}
        <div className="space-y-4">
          <Card className="border-border/60 bg-card/60">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <MousePointer className="h-4 w-4 text-primary" />
                Dispatch Click Action
              </CardTitle>
              <CardDescription className="text-xs">
                Target element by accessibility role, text, or CSS selector.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Input
                value={clickLocator}
                onChange={(e) => setClickLocator(e.target.value)}
                placeholder="role=button[name='Search']"
                className="font-mono text-xs h-8"
              />
              <Button
                size="sm"
                onClick={handleClickAction}
                disabled={isActing}
                className="w-full gap-1.5 text-xs font-semibold h-8"
              >
                <MousePointer className="h-3.5 w-3.5" />
                Execute Click
              </Button>
            </CardContent>
          </Card>

          <Card className="border-border/60 bg-card/60">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <Type className="h-4 w-4 text-purple-400" />
                Dispatch Fill Action
              </CardTitle>
              <CardDescription className="text-xs">
                Fill input or textarea by semantic locator.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2.5">
              <Input
                value={fillLocator}
                onChange={(e) => setFillLocator(e.target.value)}
                placeholder="input[name='query']"
                className="font-mono text-xs h-8"
              />
              <Input
                value={fillValue}
                onChange={(e) => setFillValue(e.target.value)}
                placeholder="Value to enter..."
                className="text-xs h-8"
              />
              <Button
                size="sm"
                onClick={handleFillAction}
                disabled={isActing}
                className="w-full gap-1.5 text-xs font-semibold h-8"
              >
                <Type className="h-3.5 w-3.5" />
                Execute Fill
              </Button>
            </CardContent>
          </Card>

          {/* Action Log Card */}
          <Card className="border-border/60 bg-card/60">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Action Verification Log
              </CardTitle>
            </CardHeader>
            <CardContent>
              {actionHistory.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-3">No actions dispatched yet</p>
              ) : (
                <div className="space-y-2">
                  {actionHistory.map((act) => (
                    <div
                      key={act.id}
                      className="p-2 rounded border border-border/40 bg-background/50 text-xs space-y-1"
                    >
                      <div className="flex items-center justify-between font-mono">
                        <span className="font-semibold capitalize text-primary">{act.action_type}</span>
                        <span className="text-[10px] text-muted-foreground">{act.duration_ms}ms</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <CheckCircle className="h-3.5 w-3.5 text-emerald-400 flex-shrink-0" />
                        <span className="text-emerald-400 font-medium">Outcome Verified</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
