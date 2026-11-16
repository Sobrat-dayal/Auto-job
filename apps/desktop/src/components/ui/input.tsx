import * as React from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  hasError?: boolean;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type = 'text', leftIcon, rightIcon, hasError, disabled, ...props }, ref) => {
    return (
      <div className="relative flex items-center w-full">
        {leftIcon && (
          <div className="absolute left-2.5 text-foreground-muted pointer-events-none flex items-center">
            {leftIcon}
          </div>
        )}
        <input
          type={type}
          ref={ref}
          disabled={disabled}
          aria-invalid={hasError ? 'true' : props['aria-invalid']}
          className={cn(
            'flex h-9 w-full rounded-md border bg-surface-secondary px-3 py-1 text-sm text-foreground placeholder:text-foreground-muted/60 transition-colors',
            'border-border focus:border-border-focused focus:outline-none focus:ring-1 focus:ring-primary',
            'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-surface-disabled',
            leftIcon && 'pl-8',
            rightIcon && 'pr-8',
            hasError && 'border-status-error focus:border-status-error focus:ring-status-error',
            className
          )}
          {...props}
        />
        {rightIcon && (
          <div className="absolute right-2.5 text-foreground-muted flex items-center">
            {rightIcon}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
