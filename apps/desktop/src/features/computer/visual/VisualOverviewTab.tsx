import * as React from 'react';
import {
  Camera,
  CheckCircle2,
  Eye,
  Monitor,
  MousePointer,
  RefreshCw,
  Search,
  ShieldCheck,
  Type,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';
import type {
  DisplayInfo,
  VisualActionResult,
  VisualDiagnosticsInfo,
  VisualGroundingResult,
} from '@autonom/shared-types';

interface VisualOverviewTabProps {
  onNavigateTab: (tabId: string) => void;
}

export const VisualOverviewTab: React.FC<VisualOverviewTabProps> = ({ onNavigateTab }) => {
  const [diagnostics, setDiagnostics] = React.useState<VisualDiagnosticsInfo | null>(null);
  const [monitors, setMonitors] = React.useState<DisplayInfo[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [latestFrameB64, setLatestFrameB64] = React.useState<string | null>(null);
  const [quickQuery, setQuickQuery] = React.useState('');
  const [groundingResult, setGroundingResult] = React.useState<VisualGroundingResult | null>(null);
  const [isGrounding, setIsGrounding] = React.useState(false);
  const [actionFeedback, setActionFeedback] = React.useState<VisualActionResult | null>(null);

  const fetchOverview = React.useCallback(async () => {
    setIsLoading(true);
    try {
      const [diag, mons] = await Promise.all([
        apiClient.getVisualDiagnostics(),
        apiClient.listVisualMonitors(),
      ]);
      setDiagnostics(diag);
      setMonitors(mons);
    } catch (err) {
      console.error('Failed to load visual overview:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchOverview();
  }, [fetchOverview]);

  const handleQuickCapture = async () => {
    try {
      const sess = await apiClient.createVisualSession({ display_index: 0 });
      const frame = await apiClient.captureVisualFrame(sess.session_id);
      setLatestFrameB64(frame.thumbnail_b64);
      await apiClient.closeVisualSession(sess.session_id);
    } catch (err) {
      console.error('Failed quick capture:', err);
    }
  };

  const handleQuickGround = async () => {
    if (!quickQuery.trim()) return;
    setIsGrounding(true);
    try {
      const sess = await apiClient.createVisualSession({ display_index: 0 });
      const res = await apiClient.groundVisualQuery(sess.session_id, quickQuery.trim());
      setGroundingResult(res);
      await apiClient.closeVisualSession(sess.session_id);
    } catch (err) {
      console.error('Quick ground failed:', err);
    } finally {
      setIsGrounding(false);
    }
  };

  const handleQuickClickGrounded = async () => {
    if (!groundingResult?.target_point) return;
    try {
      const sess = await apiClient.createVisualSession({ display_index: 0 });
      const res = await apiClient.quickVisualClick(
        sess.session_id,
        groundingResult.target_point.x,
        groundingResult.target_point.y
      );
      setActionFeedback(res);
      await apiClient.closeVisualSession(sess.session_id);
    } catch (err) {
      console.error('Click grounded failed:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-card/50 border-border/60">
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1.5 text-xs">
              <Monitor className="h-3.5 w-3.5 text-cyan-400" />
              Connected Displays
            </CardDescription>
            <CardTitle className="text-2xl font-bold text-foreground">
              {monitors.length > 0 ? monitors.length : (diagnostics?.monitors_count ?? 1)}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground font-mono">
              Primary: {diagnostics?.primary_display_resolution ?? '1920x1080'} (Scale: {diagnostics?.dpi_scaling_factor ?? 1.0}x)
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card/50 border-border/60">
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1.5 text-xs">
              <Type className="h-3.5 w-3.5 text-emerald-400" />
              Windows Media OCR
            </CardDescription>
            <CardTitle className="text-2xl font-bold text-foreground flex items-center gap-2">
              <span>{diagnostics?.offline_windows_ocr_available ? 'Active' : 'Offline'}</span>
              <Badge variant="outline" className="text-[10px] border-emerald-500/30 text-emerald-400">
                100% Offline
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground font-mono">
              Latency: ~{diagnostics?.last_ocr_latency_ms ?? 45}ms • WinRT Local
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card/50 border-border/60">
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1.5 text-xs">
              <Camera className="h-3.5 w-3.5 text-indigo-400" />
              Screen Capture Provider
            </CardDescription>
            <CardTitle className="text-2xl font-bold text-foreground uppercase">
              {diagnostics?.active_provider ?? 'MSS'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground font-mono">
              Providers: MSS, GDI BitBlt, WGC
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card/50 border-border/60">
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1.5 text-xs">
              <ShieldCheck className="h-3.5 w-3.5 text-amber-400" />
              Safety Gate & Bounds
            </CardDescription>
            <CardTitle className="text-2xl font-bold text-foreground">
              Enforced
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground font-mono">
              Emergency Stop • Session Lock Gate
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Visual Grounding & Perception Console */}
      <Card className="border-border/60 bg-card/40">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg font-semibold flex items-center gap-2">
                <Eye className="h-5 w-5 text-cyan-400" />
                Live Visual Perception & Grounding Console
              </CardTitle>
              <CardDescription>
                Test real-time offline OCR, visual element grounding, and coordinate resolution against your active screen.
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={handleQuickCapture} className="gap-1.5">
                <Camera className="h-3.5 w-3.5" />
                Capture Screen
              </Button>
              <Button size="sm" variant="outline" onClick={fetchOverview} disabled={isLoading} className="gap-1.5">
                <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Find visual UI element (e.g., 'Start', 'Search', 'Notepad', 'File', 'OK')..."
                value={quickQuery}
                onChange={(e) => setQuickQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleQuickGround()}
                className="pl-9 font-mono text-sm"
              />
            </div>
            <Button
              onClick={handleQuickGround}
              disabled={isGrounding || !quickQuery.trim()}
              className="gap-2 bg-cyan-600 hover:bg-cyan-500 text-white"
            >
              {isGrounding ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Eye className="h-4 w-4" />}
              Ground Element
            </Button>
          </div>

          {groundingResult && (
            <div className="p-4 rounded-lg border border-cyan-500/20 bg-cyan-500/5 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className={groundingResult.success ? 'border-emerald-500/40 text-emerald-400' : 'border-rose-500/40 text-rose-400'}>
                    {groundingResult.success ? 'Grounded Successfully' : 'Grounding Failed'}
                  </Badge>
                  <span className="text-xs text-muted-foreground font-mono">
                    Query: "{groundingResult.query}" • Confidence: {(groundingResult.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                {groundingResult.target_point && (
                  <Button
                    size="sm"
                    onClick={handleQuickClickGrounded}
                    className="gap-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs h-8"
                  >
                    <MousePointer className="h-3.5 w-3.5" />
                    Click ({groundingResult.target_point.x}, {groundingResult.target_point.y})
                  </Button>
                )}
              </div>
              <p className="text-xs text-foreground/80 font-mono">
                {groundingResult.explanation}
              </p>
            </div>
          )}

          {actionFeedback && (
            <div className="p-3 rounded border border-emerald-500/20 bg-emerald-500/5 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-mono text-emerald-400">
                <CheckCircle2 className="h-4 w-4" />
                <span>Action Executed ({actionFeedback.action_type}) • Verification: {actionFeedback.verification_status}</span>
              </div>
              <span className="text-[11px] text-muted-foreground font-mono">
                Visual Diff: {(actionFeedback.visual_difference * 100).toFixed(3)}% • {actionFeedback.execution_time_ms.toFixed(1)}ms
              </span>
            </div>
          )}

          {latestFrameB64 && (
            <div className="space-y-2 pt-2">
              <span className="text-xs font-medium text-muted-foreground">Latest Captured Screen Snapshot:</span>
              <div className="rounded-lg border border-border overflow-hidden bg-black/40 max-h-80 flex items-center justify-center">
                <img
                  src={`data:image/png;base64,${latestFrameB64}`}
                  alt="Desktop Screen Preview"
                  className="max-h-80 object-contain w-auto"
                />
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Feature Navigation Tiles */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card
          className="border-border/60 bg-card/30 hover:border-cyan-500/40 cursor-pointer transition-all"
          onClick={() => onNavigateTab('capture')}
        >
          <CardHeader>
            <div className="flex items-center gap-2 text-cyan-400">
              <Camera className="h-5 w-5" />
              <CardTitle className="text-base font-semibold">Screen Perception & Capture</CardTitle>
            </div>
            <CardDescription className="text-xs">
              Live multi-monitor capture, GDI window isolation, and high-DPI scaling configuration.
            </CardDescription>
          </CardHeader>
        </Card>

        <Card
          className="border-border/60 bg-card/30 hover:border-emerald-500/40 cursor-pointer transition-all"
          onClick={() => onNavigateTab('grounding')}
        >
          <CardHeader>
            <div className="flex items-center gap-2 text-emerald-400">
              <Eye className="h-5 w-5" />
              <CardTitle className="text-base font-semibold">Visual Grounding & OCR</CardTitle>
            </div>
            <CardDescription className="text-xs">
              Offline Windows Media OCR token overlay, bounding box viewer, and semantic locator resolution.
            </CardDescription>
          </CardHeader>
        </Card>

        <Card
          className="border-border/60 bg-card/30 hover:border-purple-500/40 cursor-pointer transition-all"
          onClick={() => onNavigateTab('actions')}
        >
          <CardHeader>
            <div className="flex items-center gap-2 text-purple-400">
              <MousePointer className="h-5 w-5" />
              <CardTitle className="text-base font-semibold">Actions & Verification</CardTitle>
            </div>
            <CardDescription className="text-xs">
              Coordinate mouse/keyboard SendInput dispatch with pre/post visual state verification.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    </div>
  );
};
