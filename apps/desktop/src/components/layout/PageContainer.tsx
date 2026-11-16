import * as React from 'react';
import { cn } from '@/lib/utils';
import { useDensity } from '@/design-system/ThemeContext';

export interface PageContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  subtitle?: string;
  badge?: React.ReactNode;
  actions?: React.ReactNode;
}

export function PageContainer({
  title,
  subtitle,
  badge,
  actions,
  children,
  className,
  ...props
}: PageContainerProps) {
  const { density } = useDensity();

  return (
    <div
      className={cn(
        'w-full max-w-7xl mx-auto flex flex-col',
        density === 'compact' ? 'p-4 gap-3.5' : 'p-6 gap-6',
        className
      )}
      {...props}
    >
      {(title || actions) && (
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-border/70">
          <div>
            <div className="flex items-center gap-2.5">
              {title && (
                <h1 className="text-xl md:text-2xl font-bold tracking-tight text-foreground">
                  {title}
                </h1>
              )}
              {badge}
            </div>
            {subtitle && (
              <p className="text-xs md:text-sm text-foreground-secondary mt-1">{subtitle}</p>
            )}
          </div>
          {actions && <div className="flex items-center gap-2 shrink-0">{actions}</div>}
        </div>
      )}
      {children}
    </div>
  );
}
