import * as React from 'react';
import { RefreshCw } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api-client';
import type { DesktopActionResult } from '@autonom/shared-types';

export const DesktopActionsTab: React.FC = () => {
  const [actions, setActions] = React.useState<DesktopActionResult[]>([]);
  const [loading, setLoading] = React.useState<boolean>(true);

  const fetchActions = React.useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiClient.listDesktopActions(50);
      setActions(data);
    } catch (err) {
      console.error('Failed to load action history:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchActions();
  }, [fetchActions]);

  return (
    <div className="space-y-4">
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base font-semibold">Desktop Action Execution History</CardTitle>
              <CardDescription>
                Audited ledger of dispatched UI Automation actions, control pattern executions, and post-action verification outcomes.
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchActions}
              disabled={loading}
              className="gap-1.5 text-xs h-8"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-border/60 bg-muted/30 text-muted-foreground font-mono uppercase text-[10px]">
                <tr>
                  <th className="py-2.5 px-3">Action ID</th>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3">Execution Status</th>
                  <th className="py-2.5 px-3">Verification</th>
                  <th className="py-2.5 px-3">Latency</th>
                  <th className="py-2.5 px-3 text-right">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40 font-mono">
                {actions.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-muted-foreground">
                      No desktop actions recorded yet.
                    </td>
                  </tr>
                ) : (
                  actions.map((act) => (
                    <tr key={act.action_id} className="hover:bg-muted/20 transition-colors">
                      <td className="py-2.5 px-3 text-cyan-400 font-medium">{act.action_id}</td>
                      <td className="py-2.5 px-3 font-semibold text-foreground uppercase">{act.action_type}</td>
                      <td className="py-2.5 px-3">
                        <Badge
                          variant={act.status === 'succeeded' ? 'success' : act.status === 'blocked' ? 'warning' : 'error'}
                          className="text-[10px]"
                        >
                          {act.status}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3">
                        <Badge
                          variant={act.verification_status === 'verified' ? 'success' : act.verification_status === 'failed' ? 'error' : 'neutral'}
                          className="text-[10px]"
                        >
                          {act.verification_status}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3 text-muted-foreground">{act.duration_ms.toFixed(1)}ms</td>
                      <td className="py-2.5 px-3 text-right text-muted-foreground">
                        {new Date(act.executed_at).toLocaleTimeString()}
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
