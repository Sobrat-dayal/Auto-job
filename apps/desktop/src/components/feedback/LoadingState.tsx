import * as React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface LoadingStateProps extends React.HTMLAttributes<HTMLDivElement> {
  message?: string;
}

export function LoadingState({ message = 'Loading...', className, ...props }: LoadingStateProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={cn(
        'flex flex-col items-center justify-center p-8 gap-3 min-h-[160px] text-foreground-muted',
        className
      )}
      {...props}
    >
      <Loader2 className="w-6 h-6 animate-spin text-primary shrink-0" />
      <span className="text-xs font-medium text-foreground-secondary">{message}</span>
    </div>
  );
}
