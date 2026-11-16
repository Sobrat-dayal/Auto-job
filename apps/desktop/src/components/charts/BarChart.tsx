import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { ChartContainer, type ChartContainerProps } from './ChartContainer';
import { PALETTE } from '@/design-system/tokens';
import type { DataPoint } from './LineChart';

export interface BarSeries {
  dataKey: string;
  name?: string;
  color?: string;
}

export interface BarChartProps extends Omit<ChartContainerProps, 'children'> {
  data: DataPoint[];
  series: BarSeries[];
}

export function BarChart({
  data,
  series,
  title,
  subtitle,
  action,
  height,
  className,
}: BarChartProps) {
  return (
    <ChartContainer
      title={title}
      subtitle={subtitle}
      action={action}
      height={height}
      className={className}
    >
      <ResponsiveContainer width="100%" height="100%">
        <RechartsBarChart data={data} margin={{ top: 8, right: 12, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(42, 58, 82, 0.4)" vertical={false} />
          <XAxis
            dataKey="name"
            stroke={PALETTE.textMuted}
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: PALETTE.borderDefault }}
          />
          <YAxis
            stroke={PALETTE.textMuted}
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: PALETTE.borderDefault }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: PALETTE.surfaceElevated,
              borderColor: PALETTE.borderDefault,
              borderRadius: 6,
              color: PALETTE.textPrimary,
              fontSize: 12,
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)',
            }}
          />
          {series.map((s, idx) => (
            <Bar
              key={s.dataKey}
              dataKey={s.dataKey}
              name={s.name || s.dataKey}
              fill={s.color || (idx === 0 ? PALETTE.primary : PALETTE.cyan)}
              radius={[4, 4, 0, 0]}
            />
          ))}
        </RechartsBarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
