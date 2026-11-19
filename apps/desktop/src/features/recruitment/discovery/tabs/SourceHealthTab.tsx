/**
 * Tab: Source Health & Telemetry (Stage 26).
 * Inspects provider uptime, latency, consecutive failures, and rate limit cooldowns.
 */

import * as React from 'react';
import { RefreshCw } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { JobSourceHealth, JobSourceConfig } from '@autonom/shared-types';

interface SourceHealthTabProps {
  healthList: JobSourceHealth[];
  sources: JobSourceConfig[];
  onRefresh: () => void;
}

export const SourceHealthTab: React.FC<SourceHealthTabProps> = ({
  healthList,
  sources,
  onRefresh,
}) => {
  const sourceNameMap = React.useMemo(() => {
    const map = new Map<string, string>();
    for (const s of sources) {
      map.set(s.id, s.name);
    }
    return map;
  }, [sources]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold">Source Health & Operational Telemetry</h3>
          <p className="text-sm text-muted-foreground">
            Track round-trip response latency, consecutive connection failures, and HTTP 429 throttling events.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={onRefresh}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh Metrics
        </Button>
      </div>

      <Card className="border">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead className="bg-muted/50 border-b text-muted-foreground">
                <tr>
                  <th className="py-2.5 px-4 text-left font-medium">Source / Endpoint</th>
                  <th className="py-2.5 px-4 text-left font-medium">Status</th>
                  <th className="py-2.5 px-4 text-right font-medium">Latency</th>
                  <th className="py-2.5 px-4 text-right font-medium">Postings Retrieved</th>
                  <th className="py-2.5 px-4 text-right font-medium">Errors / Failures</th>
                  <th className="py-2.5 px-4 text-right font-medium">Rate Limited</th>
                  <th className="py-2.5 px-4 text-right font-medium">Last Checked</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {healthList.map((h) => {
                  const name = sourceNameMap.get(h.source_id) || h.source_id;
                  const isHealthy = h.consecutive_failures === 0;
                  return (
                    <tr key={h.source_id} className="hover:bg-muted/30">
                      <td className="py-2.5 px-4 font-medium">
                        <div>{name}</div>
                        <div className="text-[10px] text-muted-foreground font-mono">{h.source_id}</div>
                      </td>
                      <td className="py-2.5 px-4">
                        <Badge
                          variant="outline"
                          className={`text-[10px] capitalize ${
                            isHealthy
                              ? 'text-emerald-600 border-emerald-300'
                              : 'text-rose-600 border-rose-300'
                          }`}
                        >
                          {h.current_status.replace(/_/g, ' ')}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-4 text-right font-mono">
                        {h.response_latency_ms ? `${h.response_latency_ms.toFixed(0)} ms` : '—'}
                      </td>
                      <td className="py-2.5 px-4 text-right font-mono font-medium">
                        {h.retrieved_count}
                      </td>
                      <td className="py-2.5 px-4 text-right">
                        <span
                          className={`font-mono ${
                            h.consecutive_failures > 0 ? 'text-rose-600 font-bold' : 'text-muted-foreground'
                          }`}
                        >
                          {h.error_count} (consec: {h.consecutive_failures})
                        </span>
                      </td>
                      <td className="py-2.5 px-4 text-right font-mono text-muted-foreground">
                        {h.rate_limited_count}
                      </td>
                      <td className="py-2.5 px-4 text-right text-muted-foreground font-mono text-[11px]">
                        {new Date(h.last_checked_at).toLocaleTimeString()}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
