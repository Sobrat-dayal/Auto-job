import * as React from 'react';
import {
  Activity,
  Cpu,
  Monitor,
  RefreshCw,
  RotateCcw,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type {
  DisplayInfo,
  VisualDiagnosticsInfo,
} from '@autonom/shared-types';

export const VisualDiagnosticsTab: React.FC = () => {
  const [diagnostics, setDiagnostics] = React.useState<VisualDiagnosticsInfo | null>(null);
  const [monitors, setMonitors] = React.useState<DisplayInfo[]>([]);
  const [recoveryEvents, setRecoveryEvents] = React.useState<any[]>([]);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);

  const fetchDiagnostics = React.useCallback(async () => {
    setIsLoading(true);
    try {
      const [diag, mons, rec] = await Promise.all([
        apiClient.getVisualDiagnostics(),
        apiClient.listVisualMonitors(),
        apiClient.listVisualRecoveryEvents(),
      ]);
      setDiagnostics(diag);
      setMonitors(mons);
      setRecoveryEvents(rec);
    } catch (err) {
      console.error('Failed to load diagnostics:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchDiagnostics();
  }, [fetchDiagnostics]);

  return (
    <div className="space-y-6">
      {/* Top Diagnostics Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-foreground flex items-center gap-2">
            <Activity className="h-5 w-5 text-cyan-400" />
            Visual Engine & Subsystem Diagnostics
          </h3>
          <p className="text-xs text-muted-foreground">
            Hardware acceleration, capture providers, display DPI boundaries, and automatic recovery logs.
          </p>
        </div>
        <Button size="sm" variant="outline" onClick={fetchDiagnostics} disabled={isLoading} className="gap-1.5 text-xs">
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Grid of Telemetry */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Providers & Hardware */}
        <Card className="border-border/60 bg-card/40">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Cpu className="h-4 w-4 text-purple-400" />
              Capture Providers & Engine Pipeline
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-xs font-mono">
            <div className="flex justify-between items-center py-1.5 border-b border-border/50">
              <span className="text-muted-foreground">Active Capture Provider:</span>
              <Badge variant="outline" className="border-purple-500/40 text-purple-400 uppercase">
                {diagnostics?.active_provider ?? 'MSS'}
              </Badge>
            </div>
            <div className="flex justify-between items-center py-1.5 border-b border-border/50">
              <span className="text-muted-foreground">Available Hardware Providers:</span>
              <span className="text-foreground">MSS, GDI PrintWindow, WGC Direct3D</span>
            </div>
            <div className="flex justify-between items-center py-1.5 border-b border-border/50">
              <span className="text-muted-foreground">Windows Media OCR (WinRT):</span>
              <Badge variant="outline" className="border-emerald-500/40 text-emerald-400">
                {diagnostics?.offline_windows_ocr_available ? 'OPERATIONAL (Offline)' : 'UNAVAILABLE'}
              </Badge>
            </div>
            <div className="flex justify-between items-center py-1.5 border-b border-border/50">
              <span className="text-muted-foreground">GPU Acceleration:</span>
              <span className="text-foreground font-semibold">{diagnostics?.gpu_acceleration ? 'Enabled' : 'Disabled'}</span>
            </div>
            <div className="flex justify-between items-center py-1.5">
              <span className="text-muted-foreground">Capture Latency / OCR Latency:</span>
              <span className="text-foreground font-semibold">
                ~{diagnostics?.last_capture_latency_ms ?? 16}ms / ~{diagnostics?.last_ocr_latency_ms ?? 45}ms
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Physical Display Configuration */}
        <Card className="border-border/60 bg-card/40">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Monitor className="h-4 w-4 text-cyan-400" />
              Physical Display Topologies ({monitors.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-xs font-mono">
            {monitors.map((m) => (
              <div key={m.display_index} className="p-2.5 rounded border border-border bg-background/50 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-foreground">
                    Display {m.display_index}: {m.name}
                  </span>
                  {m.is_primary && (
                    <Badge variant="outline" className="text-[10px] border-cyan-500/40 text-cyan-400">
                      Primary
                    </Badge>
                  )}
                </div>
                <div className="text-[11px] text-muted-foreground">
                  Resolution: {m.width}x{m.height} • Scale: {m.scale_factor}x • DPI: {m.dpi}
                </div>
                <div className="text-[10px] text-muted-foreground">
                  Bounds: [{m.left}, {m.top}, {m.right}, {m.bottom}]
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Recovery Manager History */}
      <Card className="border-border/60 bg-card/40">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <RotateCcw className="h-4 w-4 text-amber-400" />
            Automatic Action Recovery Events ({recoveryEvents.length})
          </CardTitle>
          <CardDescription className="text-xs">
            Logged when visual actions fail initial verification and require bounded re-acquisition, re-grounding, or coordinate correction.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-xs font-mono">
            {recoveryEvents.length === 0 && (
              <div className="text-center py-6 text-muted-foreground">
                No recovery events recorded. All visual actions executed with first-pass stability.
              </div>
            )}
            {recoveryEvents.map((ev, i) => (
              <div key={i} className="p-2.5 rounded border border-border flex items-center justify-between">
                <div>
                  <span className="font-semibold text-foreground">Attempt #{ev.attempt} for "{ev.query}"</span>
                  <span className="block text-[11px] text-muted-foreground">
                    Previous Status: {ev.previous_status} • {ev.error || 'Recovered'}
                  </span>
                </div>
                <Badge
                  variant="outline"
                  className={ev.success ? 'border-emerald-500/40 text-emerald-400' : 'border-rose-500/40 text-rose-400'}
                >
                  {ev.success ? 'Recovered' : 'Retrying / Failed'}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
