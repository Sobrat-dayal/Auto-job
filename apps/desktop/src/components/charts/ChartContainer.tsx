import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ChartContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  height?: number;
}

export function ChartContainer({
  title,
  subtitle,
  action,
  height = 240,
  children,
  className,
  ...props
}: ChartContainerProps) {
  return (
    <div
      className={cn(
        'bg-surface rounded-lg border border-border p-4 flex flex-col justify-between shadow-subtle',
        className
      )}
      {...props}
    >
      <div className="flex items-center justify-between pb-2 mb-3 border-b border-border/50 gap-2">
        <div>
          <h3 className="text-card-title text-foreground">{title}</h3>
          {subtitle && <p className="text-caption text-foreground-muted mt-0.5">{subtitle}</p>}
        </div>
        {action && <div className="shrink-0">{action}</div>}
      </div>

      <div style={{ height, width: '100%' }} className="relative flex-1 min-h-[160px]">
        {children}
      </div>
    </div>
  );
}
