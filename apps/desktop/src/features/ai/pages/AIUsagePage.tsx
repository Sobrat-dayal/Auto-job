import React from 'react';
import {
  Coins,
  Sparkles,
  Clock,
  Cpu,
  Cloud,
  Search,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api-client';
import type { AIUsageSummary } from '@autonom/shared-types';

interface AIUsagePageProps {
  usageSummary: AIUsageSummary | null;
  isLoading?: boolean;
  onRefresh?: () => Promise<void>;
}

export const AIUsagePage: React.FC<AIUsagePageProps> = ({
  usageSummary,
}) => {
  const [recentRequests, setRecentRequests] = React.useState<any[]>([]);
  const [loadingRequests, setLoadingRequests] = React.useState(false);
  const [searchTerm, setSearchTerm] = React.useState('');

  const loadRequests = async () => {
    setLoadingRequests(true);
    try {
      const res = await apiClient.listInferenceRequests({ limit: 50, offset: 0 });
      setRecentRequests(res.items || []);
    } catch (err) {
      console.error('Failed to load recent AI requests:', err);
    } finally {
      setLoadingRequests(false);
    }
  };

  React.useEffect(() => {
    loadRequests();
  }, []);

  const totalReqs = usageSummary?.total_requests ?? 0;
  const localReqs = usageSummary?.local_requests ?? 0;
  const cloudReqs = usageSummary?.cloud_requests ?? 0;
  const localRatio = totalReqs > 0 ? ((localReqs / totalReqs) * 100).toFixed(0) : '100';

  const filteredRequests = recentRequests.filter((r) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      r.task_category?.toLowerCase().includes(term) ||
      r.model_id?.toLowerCase().includes(term) ||
      r.provider_id?.toLowerCase().includes(term) ||
      r.request_id?.toLowerCase().includes(term)
    );
  });

  return (
    <div className="space-y-6">
      {/* 5 KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {/* Total Requests */}
        <Card className="border-border/60 bg-card/60">
          <CardContent className="p-3.5 space-y-1">
            <span className="text-[11px] text-muted-foreground block font-medium">
              Total Inferences
            </span>
            <div className="flex items-baseline justify-between">
              <span className="text-xl font-bold font-mono text-foreground">
                {totalReqs.toLocaleString()}
              </span>
              <span className="text-[10px] text-emerald-400 font-mono">
                {usageSummary?.success_rate_percent ?? 100}% OK
              </span>
            </div>
            <span className="text-[10px] text-muted-foreground">
              {usageSummary?.failed_requests ?? 0} errors recorded
            </span>
          </CardContent>
        </Card>

        {/* Local vs Cloud Ratio */}
        <Card className="border-border/60 bg-card/60">
          <CardContent className="p-3.5 space-y-1">
            <span className="text-[11px] text-muted-foreground block font-medium">
              Local Execution Ratio
            </span>
            <div className="flex items-baseline justify-between">
              <span className="text-xl font-bold font-mono text-cyan">
                {localRatio}%
              </span>
              <Badge variant="cyan" className="text-[9px] px-1 py-0">
                LOCAL FIRST
              </Badge>
            </div>
            <span className="text-[10px] text-muted-foreground font-mono">
              {localReqs} local • {cloudReqs} cloud
            </span>
          </CardContent>
        </Card>

        {/* Token Volume */}
        <Card className="border-border/60 bg-card/60">
          <CardContent className="p-3.5 space-y-1">
            <span className="text-[11px] text-muted-foreground block font-medium">
              Total Tokens Processed
            </span>
            <div className="flex items-baseline justify-between">
              <span className="text-xl font-bold font-mono text-foreground">
                {(usageSummary?.total_tokens ?? 0).toLocaleString()}
              </span>
              <Sparkles className="h-3.5 w-3.5 text-amber-400" />
            </div>
            <span className="text-[10px] text-muted-foreground font-mono">
              {(usageSummary?.total_prompt_tokens ?? 0).toLocaleString()} in / {(usageSummary?.total_completion_tokens ?? 0).toLocaleString()} out
            </span>
          </CardContent>
        </Card>

        {/* Estimated Spend */}
        <Card className="border-border/60 bg-card/60">
          <CardContent className="p-3.5 space-y-1">
            <span className="text-[11px] text-muted-foreground block font-medium">
              Cloud Spend (USD)
            </span>
            <div className="flex items-baseline justify-between">
              <span className="text-xl font-bold font-mono text-emerald-400">
                ${(usageSummary?.total_estimated_cost_usd ?? 0).toFixed(4)}
              </span>
              <Coins className="h-3.5 w-3.5 text-emerald-400" />
            </div>
            <span className="text-[10px] text-muted-foreground">
              Offline savings maximized
            </span>
          </CardContent>
        </Card>

        {/* Average Latency */}
        <Card className="border-border/60 bg-card/60">
          <CardContent className="p-3.5 space-y-1">
            <span className="text-[11px] text-muted-foreground block font-medium">
              Avg Latency
            </span>
            <div className="flex items-baseline justify-between">
              <span className="text-xl font-bold font-mono text-foreground">
                {(usageSummary?.average_latency_ms ?? 0).toFixed(0)} ms
              </span>
              <Clock className="h-3.5 w-3.5 text-cyan" />
            </div>
            <span className="text-[10px] text-muted-foreground">
              End-to-end response time
            </span>
          </CardContent>
        </Card>
      </div>

      {/* Breakdown by Provider & Model */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* By Provider */}
        <Card className="border-border/60 bg-card/60">
          <CardContent className="p-4 space-y-3">
            <h4 className="text-xs font-semibold text-foreground uppercase tracking-wider">
              Token Consumption by Provider
            </h4>
            <div className="space-y-2">
              {(usageSummary?.by_provider ?? []).length === 0 ? (
                <p className="text-xs text-muted-foreground py-2 italic">
                  No provider inference traffic recorded yet.
                </p>
              ) : (
                usageSummary?.by_provider.map((p) => (
                  <div
                    key={p.provider_id}
                    className="p-2.5 rounded-md border border-border/40 bg-secondary/15 flex items-center justify-between text-xs font-mono"
                  >
                    <div className="flex items-center gap-2">
                      {p.provider_id === 'ollama' ? (
                        <Cpu className="h-3.5 w-3.5 text-cyan" />
                      ) : (
                        <Cloud className="h-3.5 w-3.5 text-violet-400" />
                      )}
                      <span className="font-semibold text-foreground uppercase">
                        {p.provider_id}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-[11px] text-muted-foreground">
                      <span>{p.requests} reqs</span>
                      <span>{p.tokens.toLocaleString()} tok</span>
                      <span className="text-emerald-400 font-semibold">
                        ${p.cost_usd.toFixed(4)}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* By Model */}
        <Card className="border-border/60 bg-card/60">
          <CardContent className="p-4 space-y-3">
            <h4 className="text-xs font-semibold text-foreground uppercase tracking-wider">
              Inference Volume by Model
            </h4>
            <div className="space-y-2">
              {(usageSummary?.by_model ?? []).length === 0 ? (
                <p className="text-xs text-muted-foreground py-2 italic">
                  No model executions logged in active window.
                </p>
              ) : (
                usageSummary?.by_model.map((m) => (
                  <div
                    key={`${m.provider_id}-${m.model_id}`}
                    className="p-2.5 rounded-md border border-border/40 bg-secondary/15 flex items-center justify-between text-xs font-mono"
                  >
                    <span className="text-foreground truncate max-w-[180px]">
                      {m.model_id}
                    </span>
                    <div className="flex items-center gap-3 text-[11px] text-muted-foreground">
                      <span>{m.requests} reqs</span>
                      <span>{m.tokens.toLocaleString()} tok</span>
                      <span className="text-emerald-400 font-semibold">
                        ${m.cost_usd.toFixed(4)}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Inference Logs Table */}
      <Card className="border-border/60 bg-card/60">
        <CardContent className="p-4 space-y-3.5">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h4 className="text-xs font-semibold text-foreground uppercase tracking-wider">
                Recent Inference Audit Logs
              </h4>
              <p className="text-[11px] text-muted-foreground">
                Detailed record of requests, token counts, routing rules, and costs.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Filter logs..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="h-7 w-44 pl-8 text-xs bg-card"
                />
              </div>
              <Button
                variant="outline"
                size="sm"
                className="h-7 text-xs"
                onClick={loadRequests}
                disabled={loadingRequests}
              >
                Refresh
              </Button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse font-mono">
              <thead>
                <tr className="border-b border-border/50 text-[10px] text-muted-foreground">
                  <th className="py-2 px-2.5">Time</th>
                  <th className="py-2 px-2.5">Category</th>
                  <th className="py-2 px-2.5">Target</th>
                  <th className="py-2 px-2.5">Rule Applied</th>
                  <th className="py-2 px-2.5 text-right">Tokens (In/Out)</th>
                  <th className="py-2 px-2.5 text-right">Latency</th>
                  <th className="py-2 px-2.5 text-right">Cost</th>
                  <th className="py-2 px-2.5 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/30 text-[11px]">
                {filteredRequests.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-6 text-center text-muted-foreground italic">
                      {loadingRequests ? 'Loading audit records...' : 'No inference events found.'}
                    </td>
                  </tr>
                ) : (
                  filteredRequests.map((r) => (
                    <tr key={r.id || r.request_id} className="hover:bg-secondary/15 transition-colors">
                      <td className="py-2 px-2.5 text-muted-foreground">
                        {r.created_at ? new Date(r.created_at).toLocaleTimeString() : '—'}
                      </td>
                      <td className="py-2 px-2.5 text-foreground">
                        {r.task_category || 'general'}
                      </td>
                      <td className="py-2 px-2.5">
                        <span className="text-cyan font-semibold">{r.provider_id}</span>
                        <span className="text-muted-foreground">/{r.model_id}</span>
                      </td>
                      <td className="py-2 px-2.5 text-muted-foreground truncate max-w-[140px]" title={r.routing_rule_applied}>
                        {r.routing_rule_applied || 'Default'}
                      </td>
                      <td className="py-2 px-2.5 text-right text-muted-foreground">
                        {r.prompt_tokens ?? 0} / {r.completion_tokens ?? 0}
                      </td>
                      <td className="py-2 px-2.5 text-right text-foreground">
                        {r.latency_ms ? `${r.latency_ms}ms` : '—'}
                      </td>
                      <td className="py-2 px-2.5 text-right text-emerald-400">
                        ${(r.estimated_cost_usd ?? 0).toFixed(5)}
                      </td>
                      <td className="py-2 px-2.5 text-center">
                        <Badge
                          variant={r.status === 'completed' ? 'cyan' : r.status === 'failed' ? 'error' : 'neutral'}
                          className="text-[9px] uppercase px-1.5 py-0"
                        >
                          {r.status || 'OK'}
                        </Badge>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
