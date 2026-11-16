import * as React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

export interface ErrorStateProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  message: string;
  onRetry?: () => void;
  retryText?: string;
}

export function ErrorState({
  title = 'An error occurred',
  message,
  onRetry,
  retryText = 'Retry',
  className,
  ...props
}: ErrorStateProps) {
  return (
    <div
      role="alert"
      className={cn(
        'p-5 rounded-lg border border-status-error/30 bg-status-error/10 text-status-error flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-subtle',
        className
      )}
      {...props}
    >
      <div className="flex items-start gap-3 min-w-0">
        <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5 text-status-error" />
        <div>
          <h4 className="text-sm font-semibold text-foreground">{title}</h4>
          <p className="text-xs text-foreground-secondary mt-0.5 leading-relaxed break-words">
            {message}
          </p>
        </div>
      </div>

      {onRetry && (
        <Button
          variant="destructive"
          size="sm"
          onClick={onRetry}
          leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
          className="shrink-0"
        >
          {retryText}
        </Button>
      )}
    </div>
  );
}
