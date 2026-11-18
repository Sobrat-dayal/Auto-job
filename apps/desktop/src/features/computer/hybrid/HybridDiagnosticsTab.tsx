import * as React from 'react';
import { Activity, AlertTriangle, CheckCircle2, RefreshCw, Terminal } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import { HybridDiagnosticsInfo } from '@autonom/shared-types';

export const HybridDiagnosticsTab: React.FC = () => {
  const [diagnostics, setDiagnostics] = React.useState<HybridDiagnosticsInfo | null>(null);
  const [loading, setLoading] = React.useState<boolean>(false);

  const fetchDiagnostics = React.useCallback(async () => {
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
    fetchDiagnostics();
  }, [fetchDiagnostics]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
            <Activity className="h-4 w-4 text-blue-400" />
            Hybrid Engine Telemetry & System Diagnostics
          </h2>
          <p className="text-xs text-slate-400">
            Internal routing metrics, adapter latencies, and immutable decision audit lineage.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={fetchDiagnostics}
          disabled={loading}
          className="border-slate-700 bg-slate-800 text-slate-200"
        >
          <RefreshCw className={`mr-2 h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Diagnostics KPI Summary */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="border-slate-800 bg-slate-900/40">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs text-slate-400">Engine Version</CardDescription>
            <CardTitle className="text-xl font-mono font-bold text-slate-100">
              v{diagnostics?.engine_version ?? '1.0.0'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-xs text-emerald-400">Stage 19 Active</span>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/40">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs text-slate-400">System Interactivity</CardDescription>
            <CardTitle className="text-xl font-bold text-slate-100 flex items-center gap-2">
              {diagnostics?.is_healthy ? (
                <>
                  <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                  <span className="text-emerald-400">Interactive</span>
                </>
              ) : (
                <>
                  <AlertTriangle className="h-5 w-5 text-amber-400" />
                  <span className="text-amber-400">Degraded</span>
                </>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-xs text-slate-400">OpenInputDesktop healthy</span>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/40">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs text-slate-400">Global Emergency Stop</CardDescription>
            <CardTitle className="text-xl font-bold text-slate-100">
              {diagnostics?.emergency_stop_active ? (
                <span className="text-red-400">ACTIVE</span>
              ) : (
                <span className="text-emerald-400">DISENGAGED</span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-xs text-slate-400">Fail-closed enforcement</span>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/40">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs text-slate-400">Total Fallback Events</CardDescription>
            <CardTitle className="text-xl font-bold text-slate-100">
              {diagnostics?.total_fallbacks ?? 0}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-xs text-slate-400">Bounded to max 3 steps</span>
          </CardContent>
        </Card>
      </div>

      {/* Recent Routing Decisions Audit Ledger */}
      <Card className="border-slate-800 bg-slate-900/40">
        <CardHeader>
          <CardTitle className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Terminal className="h-4 w-4 text-blue-400" />
            Recent Routing Decisions Audit Ledger
          </CardTitle>
          <CardDescription className="text-xs text-slate-400">
            Immutable audit trail of method routing decisions, candidate scores, and explainable rationales.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="border-b border-slate-800 bg-slate-950/60 font-mono text-[11px] text-slate-400">
                <tr>
                  <th className="py-2.5 px-3">Decision ID</th>
                  <th className="py-2.5 px-3">Target ID</th>
                  <th className="py-2.5 px-3">Selected Method</th>
                  <th className="py-2.5 px-3">Candidates</th>
                  <th className="py-2.5 px-3">Selection Rationale</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
                {(diagnostics?.recent_routing_decisions ?? []).length > 0 ? (
                  diagnostics!.recent_routing_decisions.map((d) => (
                    <tr key={d.decision_id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-2.5 px-3 text-slate-400">{d.decision_id}</td>
                      <td className="py-2.5 px-3 text-slate-200">{d.target_id}</td>
                      <td className="py-2.5 px-3">
                        <Badge variant="outline" className="text-[10px] text-emerald-400 border-emerald-500/30">
                          {d.selected_method}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3 text-slate-400">{d.candidate_methods.length} methods</td>
                      <td className="py-2.5 px-3 text-slate-300 font-sans truncate max-w-[300px]">
                        {d.rationale}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="py-6 text-center text-slate-500 font-sans">
                      No routing decisions logged in this session yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
