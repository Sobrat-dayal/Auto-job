import * as React from 'react';
import { Badge, type BadgeProps } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { useDensity } from '@/design-system/ThemeContext';

export interface StatusCardProperty {
  label: string;
  value: React.ReactNode;
  mono?: boolean;
}

export interface StatusCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  icon?: React.ReactNode;
  statusBadge?: {
    label: string;
    variant: BadgeProps['variant'];
    pulse?: boolean;
  };
  properties: StatusCardProperty[];
  footerActions?: React.ReactNode;
}

export function StatusCard({
  title,
  icon,
  statusBadge,
  properties,
  footerActions,
  className,
  ...props
}: StatusCardProps) {
  const { density } = useDensity();

  return (
    <div
      className={cn(
        'bg-surface rounded-lg border border-border flex flex-col justify-between shadow-subtle',
        density === 'compact' ? 'p-3 gap-2.5' : 'p-4 gap-3.5',
        className
      )}
      {...props}
    >
      <div className="flex items-center justify-between pb-2 border-b border-border/50 gap-2">
        <div className="flex items-center gap-2 min-w-0">
          {icon && <span className="shrink-0 text-foreground-muted">{icon}</span>}
          <h3 className="text-card-title text-foreground truncate">{title}</h3>
        </div>
        {statusBadge && (
          <Badge
            variant={statusBadge.variant}
            size="sm"
            dot
            pulse={statusBadge.pulse}
            className="shrink-0"
          >
            {statusBadge.label}
          </Badge>
        )}
      </div>

      <div className={cn('space-y-1.5 text-xs', density === 'compact' && 'space-y-1')}>
        {properties.map((prop, idx) => (
          <div key={idx} className="flex justify-between items-center gap-2">
            <span className="text-foreground-muted shrink-0">{prop.label}:</span>
            <span
              className={cn(
                'text-foreground truncate text-right',
                prop.mono && 'font-mono-tech text-[11px]'
              )}
            >
              {prop.value}
            </span>
          </div>
        ))}
      </div>

      {footerActions && (
        <div className="pt-2 border-t border-border/40 flex items-center justify-end gap-2">
          {footerActions}
        </div>
      )}
    </div>
  );
}
