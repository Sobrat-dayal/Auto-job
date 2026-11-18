import * as React from 'react';
import {
  Cpu,
  Layers,
  Monitor,
  RefreshCw,
  Shield,
  ShieldAlert,
  Zap,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import { HybridDiagnosticsInfo, MethodHealthStatus } from '@autonom/shared-types';

export const HybridOverviewTab: React.FC = () => {
  const [diagnostics, setDiagnostics] = React.useState<HybridDiagnosticsInfo | null>(null);
  const [loading, setLoading] = React.useState<boolean>(false);
  const [killswitchBusy, setKillswitchBusy] = React.useState<boolean>(false);

  const fetchTelemetry = React.useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiClient.getHybridDiagnostics();
      setDiagnostics(data);
    } catch (err) {
      console.error('Failed to load hybrid diagnostics:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchTelemetry();
  }, [fetchTelemetry]);

  const handleToggleKillswitch = async () => {
    if (!diagnostics) return;
    setKillswitchBusy(true);
    try {
      if (diagnostics.emergency_stop_active) {
        await apiClient.deactivateHybridKillswitch();
      } else {
        await apiClient.activateHybridKillswitch('Operator triggered from Hybrid Overview');
      }
      await fetchTelemetry();
    } catch (err) {
      console.error('Killswitch toggle error:', err);
    } finally {
      setKillswitchBusy(false);
    }
  };

  const getMethodIcon = (method: string) => {
    if (method.includes('BROWSER')) return <Layers className="h-4 w-4 text-emerald-400" />;
    if (method.includes('UIA')) return <Cpu className="h-4 w-4 text-cyan-400" />;
    if (method.includes('WIN32')) return <Monitor className="h-4 w-4 text-blue-400" />;
    return <Zap className="h-4 w-4 text-purple-400" />;
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Status Controls */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between rounded-lg border border-slate-800 bg-slate-900/60 p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500/10 text-blue-400">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-semibold text-slate-100">Hybrid Interaction Engine</h2>
              <Badge variant="outline" className="border-blue-500/30 bg-blue-500/10 text-xs font-mono text-blue-400">
                Stage 19 Production
              </Badge>
              {diagnostics?.emergency_stop_active ? (
                <Badge variant="outline" className="border-red-500/30 bg-red-500/10 text-xs text-red-400">
                  Killswitch Engaged
                </Badge>
              ) : (
                <Badge variant="outline" className="border-emerald-500/30 bg-emerald-500/10 text-xs text-emerald-400">
                  Operational
                </Badge>
              )}
            </div>
            <p className="text-xs text-slate-400">
              Deterministic method routing: Browser DOM &gt; Windows UIA &gt; Win32 &gt; Visual Grounding with context-aware fallback.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchTelemetry}
            disabled={loading}
            className="border-slate-700 bg-slate-800 text-slate-200"
          >
            <RefreshCw className={`mr-2 h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>

          <Button
            variant={diagnostics?.emergency_stop_active ? 'primary' : 'destructive'}
            size="sm"
            onClick={handleToggleKillswitch}
            disabled={killswitchBusy}
            className={diagnostics?.emergency_stop_active ? 'bg-amber-600 hover:bg-amber-500' : ''}
          >
            <ShieldAlert className="mr-2 h-3.5 w-3.5" />
            {diagnostics?.emergency_stop_active ? 'Reset Emergency Stop' : 'Emergency Stop'}
          </Button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="border-slate-800 bg-slate-900/40">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs text-slate-400">Active Tasks</CardDescription>
            <CardTitle className="text-2xl font-bold text-slate-100">
              {diagnostics?.active_tasks ?? 0}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-xs text-slate-400">Total submitted: {diagnostics?.total_tasks ?? 0}</span>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/40">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs text-slate-400">Context Fallbacks</CardDescription>
            <CardTitle className="text-2xl font-bold text-slate-100">
              {diagnostics?.total_fallbacks ?? 0}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-xs text-emerald-400">Max switch depth: 3</span>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/40">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs text-slate-400">Input Lease Owner</CardDescription>
            <CardTitle className="text-lg font-mono font-medium text-slate-100 truncate">
              {diagnostics?.input_lease_owner || 'None (Idle)'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-xs text-slate-400">Cross-method lock</span>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/40">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs text-slate-400">Methods Online</CardDescription>
            <CardTitle className="text-2xl font-bold text-slate-100">
              {diagnostics?.methods.length ?? 4} / 4
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-xs text-slate-400">DOM, UIA, Win32, Visual</span>
          </CardContent>
        </Card>
      </div>

      {/* Methods Status Cards */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-slate-200">Registered Interaction Adapters</h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          {(diagnostics?.methods ?? []).map((methodHealth: MethodHealthStatus) => (
            <Card key={methodHealth.method} className="border-slate-800 bg-slate-900/40">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getMethodIcon(methodHealth.method)}
                    <span className="text-xs font-mono font-bold text-slate-200">{methodHealth.method}</span>
                  </div>
                  <Badge
                    variant="outline"
                    className={`text-[10px] ${
                      methodHealth.status === 'operational'
                        ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
                        : 'border-amber-500/30 bg-amber-500/10 text-amber-400'
                    }`}
                  >
                    {methodHealth.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-1.5 text-xs text-slate-400">
                <div className="flex justify-between">
                  <span>Success count:</span>
                  <span className="font-mono text-slate-200">{methodHealth.success_count}</span>
                </div>
                <div className="flex justify-between">
                  <span>Failures:</span>
                  <span className="font-mono text-slate-200">{methodHealth.failure_count}</span>
                </div>
                <div className="flex justify-between">
                  <span>Avg Latency:</span>
                  <span className="font-mono text-slate-200">{methodHealth.avg_latency_ms} ms</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};
