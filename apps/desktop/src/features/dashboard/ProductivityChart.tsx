import * as React from 'react';
import { useState } from 'react';
import { BarChart, type BarSeries } from '@/components/charts/BarChart';
import { useDashboardTaskTrends } from '@/hooks/use-dashboard';

export const ProductivityChart: React.FC = () => {
  const [window, setWindow] = useState<'today' | '7d' | '30d'>('7d');
  const { data } = useDashboardTaskTrends(window);

  const series: BarSeries[] = [
    { dataKey: 'completed', name: 'Completed', color: '#34D399' },
    { dataKey: 'failed', name: 'Failed', color: '#F43F5E' },
    { dataKey: 'created', name: 'Total Created', color: '#338BDF' },
  ];

  const chartData = (data?.data_points || []).map((dp) => ({
    name: dp.date.length > 5 ? dp.date.slice(5) : dp.date,
    completed: dp.completed,
    failed: dp.failed,
    created: dp.created,
  }));

  const windowActions = (
    <div className="flex items-center gap-1 bg-surface-elevated/70 p-0.5 rounded-lg border border-border/50 text-[11px]">
      {(['today', '7d', '30d'] as const).map((w) => (
        <button
          key={w}
          onClick={() => setWindow(w)}
          className={`px-2 py-0.5 rounded font-mono-tech transition-colors ${
            window === w
              ? 'bg-accent-primary text-white font-semibold'
              : 'text-foreground-muted hover:text-foreground'
          }`}
        >
          {w === 'today' ? 'Today' : w === '7d' ? '7 Days' : '30 Days'}
        </button>
      ))}
    </div>
  );

  const subtitleText = data
    ? `Durable SQLite tasks: ${data.overall_success_rate}% success (${data.total_volume} total)`
    : 'Durable tasks recorded in SQLite ledger';

  return (
    <div className="space-y-2 select-none">
      <BarChart
        title="Task Execution Trends"
        subtitle={subtitleText}
        data={chartData}
        series={series}
        height={220}
        action={windowActions}
      />
    </div>
  );
};
