import * as React from 'react';
import {
  Monitor,
  Activity,
  Layers,
  ShieldCheck,
  ShieldAlert,
  Play,
  CheckCircle2,
  RefreshCw,
  Cpu,
  Terminal,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api-client';
import type { DesktopDiagnosticsInfo, DesktopSessionInfo } from '@autonom/shared-types';

export const DesktopOverviewTab: React.FC = () => {
  const [diagnostics, setDiagnostics] = React.useState<DesktopDiagnosticsInfo | null>(null);
  const [session, setSession] = React.useState<DesktopSessionInfo | null>(null);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [launchingApp, setLaunchingApp] = React.useState<string | null>(null);
  const [launchMessage, setLaunchMessage] = React.useState<string | null>(null);

  const fetchTelemetry = React.useCallback(async () => {
    try {
      setLoading(true);
      const [diagData, sessData] = await Promise.all([
        apiClient.getDesktopDiagnostics(),
        apiClient.getDesktopSession(),
      ]);
      setDiagnostics(diagData);
      setSession(sessData);
    } catch (err) {
      console.error('Failed to load desktop telemetry:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchTelemetry();
  }, [fetchTelemetry]);

  const handleLaunch = async (appName: string) => {
    try {
      setLaunchingApp(appName);
      setLaunchMessage(null);
      const win = await apiClient.launchDesktopApplication(appName);
      if (win) {
        setLaunchMessage(`Successfully launched ${appName} (${win.window_ref}: "${win.title}")`);
      } else {
        setLaunchMessage(`Launched ${appName}, waiting for window discovery...`);
      }
      fetchTelemetry();
    } catch (err: unknown) {
      setLaunchMessage(`Failed to launch ${appName}: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLaunchingApp(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Telemetry Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="border-border/60 bg-card/60">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Windows Session
            </CardTitle>
            <Monitor className="h-4 w-4 text-cyan-400" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold font-mono text-foreground">
                Session {session?.wts_session_id ?? 1}
              </span>
              <Badge
                variant={session?.is_locked ? 'error' : session?.status === 'active' ? 'success' : 'warning'}
                className="text-[10px]"
              >
                {session?.is_locked ? 'Locked' : session?.status ?? 'Active'}
              </Badge>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              {session?.resolution ?? '1920x1080'} | {session?.user_name ?? 'User'}
            </p>
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-card/60">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Discovered Windows
            </CardTitle>
            <Layers className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold font-mono text-foreground">
                {diagnostics?.cached_windows ?? 0}
              </span>
              <Badge variant="primary" className="text-[10px]">
                Top-Level
              </Badge>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              Interactive Default Desktop
            </p>
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-card/60">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Running Applications
            </CardTitle>
            <Cpu className="h-4 w-4 text-emerald-400" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold font-mono text-foreground">
                {diagnostics?.registered_applications ?? 0}
              </span>
              <Badge variant="success" className="text-[10px]">
                Active
              </Badge>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              Cataloged Process Trees
            </p>
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-card/60">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              UIA Worker Pool
            </CardTitle>
            <Activity className="h-4 w-4 text-amber-400" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold font-mono text-foreground">
                {diagnostics?.active_worker_threads ?? 0}
              </span>
              <span className="text-xs text-muted-foreground">/ 4 MTA Threads</span>
              <Badge variant="outline" className="text-[10px] text-cyan-400 border-cyan-500/30">
                UIA Core
              </Badge>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              MTA COM Multi-Threaded Model
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Launch & Security Status */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="border-border/60 bg-card/60 lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-base font-semibold">Quick Launch Approved Application</CardTitle>
                <CardDescription>
                  Start an authorized Windows native application and automatically detect its main window.
                </CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={fetchTelemetry}
                disabled={loading}
                className="gap-1.5 text-xs"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2.5">
              {[
                { name: 'Notepad', exe: 'notepad.exe', desc: 'Text editor' },
                { name: 'Calculator', exe: 'calc.exe', desc: 'Arithmetic UI' },
                { name: 'File Explorer', exe: 'explorer.exe', desc: 'Shell browser' },
                { name: 'Command Prompt', exe: 'cmd.exe', desc: 'Standard shell' },
                { name: 'PowerShell', exe: 'powershell.exe', desc: 'Scripting console' },
              ].map((app) => (
                <Button
                  key={app.exe}
                  variant="outline"
                  size="sm"
                  disabled={launchingApp !== null}
                  onClick={() => handleLaunch(app.exe)}
                  className="gap-2 border-border/80 bg-background/50 hover:bg-primary/10 hover:border-primary/40 text-xs"
                >
                  <Play className="h-3 w-3 text-cyan-400" />
                  <span className="font-medium">{app.name}</span>
                  <span className="text-[10px] text-muted-foreground font-mono">({app.exe})</span>
                </Button>
              ))}
            </div>

            {launchMessage && (
              <div className="rounded-md border border-primary/30 bg-primary/10 p-3 text-xs text-foreground font-mono">
                {launchMessage}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Engine and Security Status Card */}
        <Card className="border-border/60 bg-card/60">
          <CardHeader>
            <CardTitle className="text-base font-semibold">Automation & Safety Guard</CardTitle>
            <CardDescription>Security policies governing structural automation</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between py-1 border-b border-border/40 text-xs">
              <span className="text-muted-foreground flex items-center gap-1.5">
                <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
                Microsoft UI Automation
              </span>
              <Badge variant="success" className="text-[10px]">Operational</Badge>
            </div>

            <div className="flex items-center justify-between py-1 border-b border-border/40 text-xs">
              <span className="text-muted-foreground flex items-center gap-1.5">
                <CheckCircle2 className="h-3.5 w-3.5 text-cyan-400" />
                Win32 Compatibility Adapter
              </span>
              <Badge variant="primary" className="text-[10px]">Available</Badge>
            </div>

            <div className="flex items-center justify-between py-1 border-b border-border/40 text-xs">
              <span className="text-muted-foreground flex items-center gap-1.5">
                <Terminal className="h-3.5 w-3.5 text-amber-400" />
                Emergency Stop Guard
              </span>
              <Badge
                variant={diagnostics?.emergency_stop_active ? 'error' : 'neutral'}
                className="text-[10px]"
              >
                {diagnostics?.emergency_stop_active ? 'Active (Halted)' : 'Normal (Armed)'}
              </Badge>
            </div>

            <div className="flex items-center justify-between py-1 text-xs">
              <span className="text-muted-foreground flex items-center gap-1.5">
                <ShieldAlert className="h-3.5 w-3.5 text-emerald-400" />
                Application Allowlist
              </span>
              <Badge variant="outline" className="text-[10px] border-emerald-500/30 text-emerald-400">
                Stage 14 Enforced
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
