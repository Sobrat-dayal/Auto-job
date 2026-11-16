import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { ChartContainer, type ChartContainerProps } from './ChartContainer';
import { PALETTE } from '@/design-system/tokens';

export interface DataPoint {
  name: string;
  [key: string]: string | number;
}

export interface LineSeries {
  dataKey: string;
  name?: string;
  color?: string;
  strokeWidth?: number;
}

export interface LineChartProps extends Omit<ChartContainerProps, 'children'> {
  data: DataPoint[];
  series: LineSeries[];
}

export function LineChart({
  data,
  series,
  title,
  subtitle,
  action,
  height,
  className,
}: LineChartProps) {
  return (
    <ChartContainer
      title={title}
      subtitle={subtitle}
      action={action}
      height={height}
      className={className}
    >
      <ResponsiveContainer width="100%" height="100%">
        <RechartsLineChart data={data} margin={{ top: 8, right: 12, left: -20, bottom: 0 }}>
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
            <Line
              key={s.dataKey}
              type="monotone"
              dataKey={s.dataKey}
              name={s.name || s.dataKey}
              stroke={s.color || (idx === 0 ? PALETTE.primary : PALETTE.cyan)}
              strokeWidth={s.strokeWidth || 2}
              dot={{ r: 3, fill: s.color || (idx === 0 ? PALETTE.primary : PALETTE.cyan) }}
              activeDot={{ r: 5 }}
            />
          ))}
        </RechartsLineChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
