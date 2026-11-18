import * as React from 'react';
import { Eye, Globe, Laptop, Lock, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';

export const UnifiedSessionsTab: React.FC = () => {
  const [browserSessions, setBrowserSessions] = React.useState<any[]>([]);
  const [desktopWindows, setDesktopWindows] = React.useState<any[]>([]);
  const [visualSessions, setVisualSessions] = React.useState<any[]>([]);
  const [diagnostics, setDiagnostics] = React.useState<any | null>(null);
  const [loading, setLoading] = React.useState<boolean>(false);

  const loadData = React.useCallback(async () => {
    setLoading(true);
    try {
      const [bSessions, dWindows, vSessions, diag] = await Promise.all([
        apiClient.listBrowserSessions().catch(() => []),
        apiClient.listDesktopWindows().catch(() => []),
        apiClient.listVisualSessions().catch(() => []),
        apiClient.getHybridDiagnostics().catch(() => null),
      ]);
      setBrowserSessions(bSessions);
      setDesktopWindows(dWindows);
      setVisualSessions(vSessions);
      setDiagnostics(diag);
    } catch (err) {
      console.error('Failed to load unified session telemetry:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadData();
  }, [loadData]);

  return (
    <div className="space-y-6">
      {/* Input Lease & Synchronizer Card */}
      <Card className="border-slate-800 bg-slate-900/40">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base text-slate-100 flex items-center gap-2">
                <Lock className="h-4 w-4 text-amber-400" />
                Cross-Method Input Ownership Lease
              </CardTitle>
              <CardDescription className="text-xs text-slate-400">
                Mutual exclusion coordinator preventing conflicting keyboard and mouse injection between UIA, Win32, and SendInput.
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={loadData}
              disabled={loading}
              className="border-slate-700 bg-slate-800 text-slate-200"
            >
              <RefreshCw className={`mr-2 h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4 rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-xs">
            <div className="flex items-center gap-2">
              <span className="text-slate-400">Current Lease Holder:</span>
              <Badge variant="outline" className="font-mono text-xs border-amber-500/30 bg-amber-500/10 text-amber-400">
                {diagnostics?.input_lease_owner || 'None (System Input Free)'}
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-slate-400">Session Locked:</span>
              <span className="font-mono text-slate-200">
                {diagnostics?.is_healthy ? 'No (Interactive)' : 'Yes'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tri-Modality Active Contexts Grid */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        {/* 1. Browser Sessions */}
        <Card className="border-slate-800 bg-slate-900/40">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <Globe className="h-4 w-4 text-emerald-400" />
                Playwright Browser Sessions
              </CardTitle>
              <Badge variant="outline" className="text-[10px] text-emerald-400 border-emerald-500/30">
                {browserSessions.length} Active
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-2 text-xs">
            {browserSessions.length > 0 ? (
              browserSessions.map((s) => (
                <div key={s.session_id} className="rounded border border-slate-800 bg-slate-950/60 p-2.5 space-y-1">
                  <div className="flex justify-between font-mono text-[11px]">
                    <span className="text-slate-200 font-semibold">{s.session_name || 'Browser'}</span>
                    <span className="text-emerald-400">{s.status}</span>
                  </div>
                  <div className="text-[11px] text-slate-400 truncate">
                    Tabs: {s.tabs_count || 1} | Browser: {s.browser_type}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-slate-500 text-center py-6">No active browser sessions</p>
            )}
          </CardContent>
        </Card>

        {/* 2. Windows Applications */}
        <Card className="border-slate-800 bg-slate-900/40">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <Laptop className="h-4 w-4 text-cyan-400" />
                Discovered Windows
              </CardTitle>
              <Badge variant="outline" className="text-[10px] text-cyan-400 border-cyan-500/30">
                {desktopWindows.length} Windows
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-2 text-xs">
            {desktopWindows.length > 0 ? (
              desktopWindows.slice(0, 5).map((w) => (
                <div key={w.window_ref || w.hwnd} className="rounded border border-slate-800 bg-slate-950/60 p-2.5 space-y-1">
                  <div className="flex justify-between font-mono text-[11px]">
                    <span className="text-slate-200 font-semibold truncate max-w-[150px]">{w.title || 'Window'}</span>
                    <span className="text-cyan-400">PID {w.process_id}</span>
                  </div>
                  <div className="text-[11px] text-slate-400 truncate">
                    HWND: {w.hwnd} | {w.process_name}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-slate-500 text-center py-6">No active native windows</p>
            )}
          </CardContent>
        </Card>

        {/* 3. Visual Capture Sessions */}
        <Card className="border-slate-800 bg-slate-900/40">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <Eye className="h-4 w-4 text-purple-400" />
                Visual Capture Sessions
              </CardTitle>
              <Badge variant="outline" className="text-[10px] text-purple-400 border-purple-500/30">
                {visualSessions.length} Streams
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-2 text-xs">
            {visualSessions.length > 0 ? (
              visualSessions.map((v) => (
                <div key={v.session_id} className="rounded border border-slate-800 bg-slate-950/60 p-2.5 space-y-1">
                  <div className="flex justify-between font-mono text-[11px]">
                    <span className="text-slate-200 font-semibold">{v.session_name || 'Stream'}</span>
                    <span className="text-purple-400">{v.provider}</span>
                  </div>
                  <div className="text-[11px] text-slate-400 truncate">
                    Target: {v.target_type} | FPS: {v.fps || 1}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-slate-500 text-center py-6">No visual capture streams active</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
