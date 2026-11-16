import * as React from 'react';
import { cn } from '@/lib/utils';

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  hasError?: boolean;
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, hasError, disabled, ...props }, ref) => {
    return (
      <textarea
        ref={ref}
        disabled={disabled}
        className={cn(
          'flex min-h-[80px] w-full rounded-md border border-border bg-surface-secondary px-3 py-2 text-sm text-foreground placeholder:text-foreground-muted/60 transition-colors',
          'focus:border-border-focused focus:outline-none focus:ring-1 focus:ring-primary',
          'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-surface-disabled',
          hasError && 'border-status-error focus:border-status-error focus:ring-status-error',
          className
        )}
        {...props}
      />
    );
  }
);

Textarea.displayName = 'Textarea';
