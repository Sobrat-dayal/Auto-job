import * as React from 'react';
import { LucideIcon } from 'lucide-react';
import { Badge, type BadgeProps } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

export interface ModuleHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  description?: string;
  icon?: LucideIcon;
  badgeLabel?: string;
  badgeVariant?: BadgeProps['variant'];
  stageTag?: string;
  actions?: React.ReactNode;
}

export const ModuleHeader = React.forwardRef<HTMLDivElement, ModuleHeaderProps>(
  (
    {
      className,
      title,
      description,
      icon: Icon,
      badgeLabel,
      badgeVariant = 'neutral',
      stageTag,
      actions,
      ...props
    },
    ref
  ) => {
    return (
      <header
        ref={ref}
        className={cn(
          'flex flex-col gap-4 border-b border-border/40 pb-5 sm:flex-row sm:items-center sm:justify-between',
          className
        )}
        {...props}
      >
        <div className="flex items-start gap-3.5">
          {Icon && (
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-primary/20 bg-primary/10 text-primary shadow-sm shadow-primary/5">
              <Icon className="h-5 w-5" aria-hidden="true" />
            </div>
          )}
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2.5">
              <h1 className="text-xl font-bold tracking-tight text-foreground sm:text-2xl">
                {title}
              </h1>
              {stageTag && (
                <Badge
                  variant="outline"
                  className="border-primary/30 bg-primary/5 text-xs font-semibold text-primary"
                >
                  {stageTag}
                </Badge>
              )}
              {badgeLabel && (
                <Badge variant={badgeVariant} className="text-xs font-medium">
                  {badgeLabel}
                </Badge>
              )}
            </div>
            {description && <p className="text-sm text-muted-foreground">{description}</p>}
          </div>
        </div>

        {actions && (
          <div className="flex shrink-0 items-center gap-2 sm:self-center">{actions}</div>
        )}
      </header>
    );
  }
);

ModuleHeader.displayName = 'ModuleHeader';
