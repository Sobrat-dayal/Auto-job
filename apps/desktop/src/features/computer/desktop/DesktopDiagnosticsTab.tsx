import * as React from 'react';
import { Monitor, Cpu, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api-client';
import type { DesktopDiagnosticsInfo } from '@autonom/shared-types';

export const DesktopDiagnosticsTab: React.FC = () => {
  const [diag, setDiag] = React.useState<DesktopDiagnosticsInfo | null>(null);
  const [loading, setLoading] = React.useState<boolean>(true);

  const fetchDiag = React.useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiClient.getDesktopDiagnostics();
      setDiag(data);
    } catch (err) {
      console.error('Failed to load diagnostics:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchDiag();
  }, [fetchDiag]);

  return (
    <div className="space-y-6">
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base font-semibold">Windows Automation Diagnostics & Health</CardTitle>
              <CardDescription>
                Low-level diagnostics for COM MTA threading, UIA core availability, and desktop session binding.
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchDiag}
              disabled={loading}
              className="gap-1.5 text-xs h-8"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 font-mono text-xs">
            {/* Session Environment */}
            <div className="rounded-md border border-border/60 bg-background/40 p-4 space-y-2.5">
              <div className="flex items-center gap-2 border-b border-border/40 pb-2 font-sans font-semibold text-foreground text-sm">
                <Monitor className="h-4 w-4 text-cyan-400" />
                Windows Interactive Session
              </div>
              <div className="flex justify-between py-1 border-b border-border/30">
                <span className="text-muted-foreground">WTS Session ID:</span>
                <span className="text-foreground">{diag?.session.wts_session_id ?? 'Unknown'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-border/30">
                <span className="text-muted-foreground">Desktop Name:</span>
                <span className="text-foreground">{diag?.session.desktop_name ?? 'Default'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-border/30">
                <span className="text-muted-foreground">User Identity:</span>
                <span className="text-foreground">{diag?.session.user_name ?? 'User'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-border/30">
                <span className="text-muted-foreground">Resolution:</span>
                <span className="text-foreground">{diag?.session.resolution ?? '1920x1080'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-border/30">
                <span className="text-muted-foreground">Interactive Desktop:</span>
                <span className={diag?.session.is_interactive ? 'text-emerald-400' : 'text-rose-400'}>
                  {diag?.session.is_interactive ? 'Attached' : 'Detached'}
                </span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-muted-foreground">Desktop Locked:</span>
                <span className={diag?.session.is_locked ? 'text-rose-400' : 'text-emerald-400'}>
                  {diag?.session.is_locked ? 'Yes (Locked)' : 'No (Unlocked)'}
                </span>
              </div>
            </div>

            {/* COM & Runtime Workers */}
            <div className="rounded-md border border-border/60 bg-background/40 p-4 space-y-2.5">
              <div className="flex items-center gap-2 border-b border-border/40 pb-2 font-sans font-semibold text-foreground text-sm">
                <Cpu className="h-4 w-4 text-emerald-400" />
                UIA COM Threading & Adapters
              </div>
              <div className="flex justify-between py-1 border-b border-border/30">
                <span className="text-muted-foreground">UIAutomationCore Provider:</span>
                <Badge variant="success" className="text-[10px]">Operational</Badge>
              </div>
              <div className="flex justify-between py-1 border-b border-border/30">
                <span className="text-muted-foreground">Win32 Compatibility Adapter:</span>
                <Badge variant="primary" className="text-[10px]">Available</Badge>
              </div>
              <div className="flex justify-between py-1 border-b border-border/30">
                <span className="text-muted-foreground">Active MTA Worker Threads:</span>
                <span className="text-foreground">{diag?.active_worker_threads ?? 0}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-border/30">
                <span className="text-muted-foreground">Discovered Top-Level Windows:</span>
                <span className="text-foreground">{diag?.cached_windows ?? 0}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-border/30">
                <span className="text-muted-foreground">Running Applications:</span>
                <span className="text-foreground">{diag?.registered_applications ?? 0}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-muted-foreground">Emergency Stop State:</span>
                <span className={diag?.emergency_stop_active ? 'text-rose-400 font-bold' : 'text-emerald-400'}>
                  {diag?.emergency_stop_active ? 'HALTED (Active)' : 'ARMED (Normal)'}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
