import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ModulePageProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  detailPanel?: React.ReactNode;
  isDetailOpen?: boolean;
}

export const ModulePage = React.forwardRef<HTMLDivElement, ModulePageProps>(
  ({ className, children, detailPanel, isDetailOpen = false, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'relative flex h-full w-full flex-1 overflow-hidden bg-background text-foreground',
          className
        )}
        {...props}
      >
        <div className="flex h-full min-w-0 flex-1 flex-col overflow-y-auto px-6 py-6 transition-all duration-200">
          <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">{children}</div>
        </div>

        {detailPanel && isDetailOpen && (
          <aside
            aria-label="Detail inspector"
            className="w-96 shrink-0 border-l border-border bg-card/95 shadow-xl backdrop-blur-md transition-all duration-300"
          >
            {detailPanel}
          </aside>
        )}
      </div>
    );
  }
);

ModulePage.displayName = 'ModulePage';
