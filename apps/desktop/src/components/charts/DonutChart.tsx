import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { ChartContainer, type ChartContainerProps } from './ChartContainer';
import { PALETTE } from '@/design-system/tokens';

export interface PieDataPoint {
  name: string;
  value: number;
  color?: string;
}

export interface DonutChartProps extends Omit<ChartContainerProps, 'children'> {
  data: PieDataPoint[];
}

const DEFAULT_DONUT_COLORS = [
  PALETTE.primary,
  PALETTE.cyan,
  PALETTE.status.success,
  PALETTE.status.warning,
  PALETTE.status.error,
  PALETTE.status.inactive,
];

export function DonutChart({ data, title, subtitle, action, height, className }: DonutChartProps) {
  return (
    <ChartContainer
      title={title}
      subtitle={subtitle}
      action={action}
      height={height}
      className={className}
    >
      <ResponsiveContainer width="100%" height="100%">
        <RechartsPieChart>
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
          <Legend
            verticalAlign="bottom"
            height={36}
            iconType="circle"
            wrapperStyle={{ fontSize: 11, color: PALETTE.textSecondary }}
          />
          <Pie
            data={data}
            cx="50%"
            cy="45%"
            innerRadius={45}
            outerRadius={70}
            paddingAngle={3}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.color || DEFAULT_DONUT_COLORS[index % DEFAULT_DONUT_COLORS.length]}
                stroke={PALETTE.surfacePrimary}
                strokeWidth={2}
              />
            ))}
          </Pie>
        </RechartsPieChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
