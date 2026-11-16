import * as React from 'react';
import { ArrowDownRight, ArrowUpRight } from 'lucide-react';
import { cn, formatMetric } from '@/lib/utils';
import { useDensity } from '@/design-system/ThemeContext';

export interface MetricCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  value: React.ReactNode;
  subtitle?: React.ReactNode;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    label?: string;
    isPositive?: boolean;
  };
  variant?: 'default' | 'primary' | 'cyan' | 'success';
}

export function MetricCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  variant = 'default',
  className,
  ...props
}: MetricCardProps) {
  const { density } = useDensity();

  const formattedValue = typeof value === 'number' ? formatMetric(value) : value;

  const accentBorder = {
    default: 'border-border',
    primary: 'border-primary/40',
    cyan: 'border-cyan/40',
    success: 'border-status-success/40',
  }[variant];

  return (
    <div
      className={cn(
        'bg-surface rounded-lg border flex flex-col justify-between shadow-subtle transition-all hover:border-border-focused',
        accentBorder,
        density === 'compact' ? 'p-3 gap-2' : 'p-4 gap-3',
        className
      )}
      {...props}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-compact-label text-foreground-secondary truncate">{title}</span>
        {icon && <span className="text-foreground-muted shrink-0">{icon}</span>}
      </div>

      <div className="flex items-baseline justify-between gap-2">
        <div className="text-2xl font-bold font-tabular tracking-tight text-foreground">
          {formattedValue}
        </div>

        {trend && (
          <div
            className={cn(
              'flex items-center text-xs font-semibold',
              trend.isPositive ? 'text-status-success' : 'text-status-error'
            )}
          >
            {trend.isPositive ? (
              <ArrowUpRight className="w-3.5 h-3.5 shrink-0" />
            ) : (
              <ArrowDownRight className="w-3.5 h-3.5 shrink-0" />
            )}
            <span>{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>

      {subtitle && <p className="text-caption text-foreground-muted truncate">{subtitle}</p>}
    </div>
  );
}
