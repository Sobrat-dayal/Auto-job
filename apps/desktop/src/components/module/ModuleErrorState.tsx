import * as React from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export interface ModuleErrorStateProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  message?: string;
  errorDetails?: string;
  onRetry?: () => void;
  isRetrying?: boolean;
}

export const ModuleErrorState: React.FC<ModuleErrorStateProps> = ({
  className,
  title = 'Failed to load module data',
  message = 'An unexpected error occurred while communicating with the local AUTONOM backend service.',
  errorDetails,
  onRetry,
  isRetrying = false,
  ...props
}) => {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className={cn(
        'flex flex-col items-center justify-center rounded-xl border border-destructive/30 bg-destructive/5 p-8 text-center backdrop-blur-sm',
        className
      )}
      {...props}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-destructive/10 text-destructive ring-1 ring-destructive/20 shadow-sm">
        <AlertTriangle className="h-6 w-6" aria-hidden="true" />
      </div>

      <h3 className="mt-4 text-base font-semibold text-foreground sm:text-lg">{title}</h3>
      <p className="mt-1.5 max-w-md text-xs text-muted-foreground sm:text-sm">{message}</p>

      {errorDetails && (
        <pre className="mt-3 max-w-lg overflow-x-auto rounded-md bg-background/80 p-2.5 text-left text-[11px] font-mono text-destructive">
          {errorDetails}
        </pre>
      )}

      {onRetry && (
        <div className="mt-5">
          <Button
            variant="outline"
            size="sm"
            onClick={onRetry}
            disabled={isRetrying}
            className="gap-2"
          >
            <RotateCcw className={cn('h-3.5 w-3.5', isRetrying && 'animate-spin')} />
            {isRetrying ? 'Retrying...' : 'Retry Connection'}
          </Button>
        </div>
      )}
    </div>
  );
};

ModuleErrorState.displayName = 'ModuleErrorState';
