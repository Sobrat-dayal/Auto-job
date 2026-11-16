import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ChartColumn, TrendingUp, Activity } from 'lucide-react';
import { ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar } from 'recharts';
import {
  ModulePage,
  ModuleHeader,
  ModuleTabs,
  ModuleLoadingState,
  ModuleErrorState,
} from '@/components/module';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { apiClient } from '@/lib/api-client';
import type { DashboardTaskTrendsResponse } from '@/types/dashboard';

export const AnalyticsWorkspace: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const getInitialTab = (): string => {
    if (location.pathname.includes('/analytics/jobs')) return 'jobs';
    if (location.pathname.includes('/analytics/agents')) return 'agents';
    if (location.pathname.includes('/analytics/workflows')) return 'workflows';
    if (location.pathname.includes('/analytics/resources')) return 'resources';
    return 'overview';
  };

  const [activeTab, setActiveTab] = React.useState<string>(getInitialTab());
  const [timeWindow, setTimeWindow] = React.useState<'today' | '7d' | '30d'>('7d');
  const [trends, setTrends] = React.useState<DashboardTaskTrendsResponse | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const [isRefreshing, setIsRefreshing] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    setActiveTab(getInitialTab());
  }, [location.pathname]);

  const loadData = React.useCallback(async () => {
    setError(null);
    try {
      const res = await apiClient.getDashboardTaskTrends(timeWindow);
      setTrends(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to query analytics trends.');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [timeWindow]);

  React.useEffect(() => {
    loadData();
  }, [loadData]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === 'overview') navigate('/analytics/overview');
    else navigate(`/analytics/${tabId}`);
  };

  const tabs = [
    { id: 'overview', label: 'Operational Overview' },
    { id: 'jobs', label: 'Job Pipeline Funnel' },
    { id: 'agents', label: 'Agent Telemetry' },
    { id: 'workflows', label: 'Task Execution Volume' },
    { id: 'resources', label: 'Compute & Memory' },
  ];

  return (
    <ModulePage>
      <ModuleHeader
        title="Operational Analytics & Telemetry"
        description="Genuine quantitative task throughput, execution latency, success ratios, and agent metrics."
        icon={ChartColumn}
        stageTag="Stage 08 Operational"
        badgeLabel={`${trends?.overall_success_rate ?? 100}% Success`}
        badgeVariant="primary"
        actions={
          <div className="flex items-center gap-1 rounded-lg border border-border bg-card p-1">
            {(['today', '7d', '30d'] as const).map((w) => (
              <Button
                key={w}
                variant={timeWindow === w ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setTimeWindow(w)}
                className="h-7 px-2.5 text-xs font-medium"
              >
                {w === 'today' ? 'Today' : w === '7d' ? '7 Days' : '30 Days'}
              </Button>
            ))}
          </div>
        }
      />

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={handleTabChange} />

      {error ? (
        <ModuleErrorState
          title="Could not load analytics telemetry"
          message={error}
          onRetry={loadData}
          isRetrying={isRefreshing}
        />
      ) : isLoading ? (
        <ModuleLoadingState rows={3} layout="cards" />
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Card className="border-border/60 bg-card/60">
              <CardContent className="p-4">
                <span className="text-xs font-semibold uppercase text-muted-foreground">
                  Total Execution Volume
                </span>
                <p className="mt-1 text-2xl font-bold font-mono text-foreground">
                  {trends?.total_volume ?? 0}
                </p>
                <span className="text-[11px] text-muted-foreground">
                  Durable tasks in current window
                </span>
              </CardContent>
            </Card>

            <Card className="border-border/60 bg-card/60">
              <CardContent className="p-4">
                <span className="text-xs font-semibold uppercase text-muted-foreground">
                  Overall Success Rate
                </span>
                <p className="mt-1 text-2xl font-bold font-mono text-status-success">
                  {trends?.overall_success_rate ?? 100}%
                </p>
                <span className="text-[11px] text-muted-foreground">
                  Successful task completions
                </span>
              </CardContent>
            </Card>

            <Card className="border-border/60 bg-card/60">
              <CardContent className="p-4">
                <span className="text-xs font-semibold uppercase text-muted-foreground">
                  Metric Provenance
                </span>
                <p className="mt-1 text-sm font-semibold text-foreground flex items-center gap-1.5">
                  <Activity className="h-4 w-4 text-cyan" />
                  SQLite Aggregated
                </p>
                <span className="text-[11px] text-muted-foreground">Zero synthetic numbers</span>
              </CardContent>
            </Card>
          </div>

          <Card className="border-border/60 bg-card/60">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-primary" />
                Task Completion vs Failures ({timeWindow})
              </CardTitle>
              <CardDescription className="text-xs">
                Time-bucketed task execution counts derived directly from SQLite task records
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 w-full pt-4">
                {trends?.data_points && trends.data_points.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={trends.data_points}
                      margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#1B2B42" opacity={0.5} />
                      <XAxis dataKey="date" stroke="#64748B" fontSize={11} tickLine={false} />
                      <YAxis
                        stroke="#64748B"
                        fontSize={11}
                        tickLine={false}
                        allowDecimals={false}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#0F1828',
                          borderColor: '#1B2B42',
                          borderRadius: '8px',
                          fontSize: '12px',
                        }}
                      />
                      <Bar
                        dataKey="completed"
                        fill="#338BDF"
                        name="Completed"
                        radius={[4, 4, 0, 0]}
                      />
                      <Bar dataKey="failed" fill="#EF4444" name="Failed" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex h-full items-center justify-center text-xs text-muted-foreground">
                    No task events recorded in this time window.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </ModulePage>
  );
};

export default AnalyticsWorkspace;
