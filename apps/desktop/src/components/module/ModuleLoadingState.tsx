import * as React from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';

export interface ModuleLoadingStateProps extends React.HTMLAttributes<HTMLDivElement> {
  rows?: number;
  layout?: 'cards' | 'table' | 'simple';
}

export const ModuleLoadingState: React.FC<ModuleLoadingStateProps> = ({
  className,
  rows = 4,
  layout = 'cards',
  ...props
}) => {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-label="Loading workspace data"
      className={cn('space-y-4', className)}
      {...props}
    >
      <div className="flex items-center justify-between pb-2">
        <Skeleton className="h-9 w-64 rounded-md" />
        <Skeleton className="h-9 w-24 rounded-md" />
      </div>

      {layout === 'cards' && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: rows }).map((_, i) => (
            <div
              key={i}
              className="flex flex-col gap-3 rounded-xl border border-border/60 bg-card/60 p-4"
            >
              <div className="flex items-center justify-between">
                <Skeleton className="h-5 w-32" />
                <Skeleton className="h-5 w-16 rounded-full" />
              </div>
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <div className="mt-2 flex items-center justify-between pt-2 border-t border-border/40">
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-7 w-20 rounded-md" />
              </div>
            </div>
          ))}
        </div>
      )}

      {layout === 'table' && (
        <div className="rounded-xl border border-border/60 bg-card/40 p-4">
          <div className="space-y-3">
            <Skeleton className="h-8 w-full rounded" />
            {Array.from({ length: rows }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full rounded" />
            ))}
          </div>
        </div>
      )}

      {layout === 'simple' && (
        <div className="space-y-3">
          {Array.from({ length: rows }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full rounded-lg" />
          ))}
        </div>
      )}

      <span className="sr-only">Loading...</span>
    </div>
  );
};

ModuleLoadingState.displayName = 'ModuleLoadingState';
