import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number;
  max?: number;
  variant?: 'primary' | 'cyan' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
  isIndeterminate?: boolean;
}

export const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  (
    {
      className,
      value = 0,
      max = 100,
      variant = 'primary',
      size = 'md',
      isIndeterminate = false,
      ...props
    },
    ref
  ) => {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

    const variantColor = {
      primary: 'bg-primary',
      cyan: 'bg-cyan',
      success: 'bg-status-success',
      warning: 'bg-status-warning',
      error: 'bg-status-error',
    }[variant];

    const sizeHeight = {
      sm: 'h-1.5',
      md: 'h-2.5',
      lg: 'h-4',
    }[size];

    return (
      <div
        ref={ref}
        role="progressbar"
        aria-valuenow={isIndeterminate ? undefined : Math.round(percentage)}
        aria-valuemin={0}
        aria-valuemax={100}
        className={cn(
          'w-full overflow-hidden rounded-full bg-surface-elevated border border-border/50',
          sizeHeight,
          className
        )}
        {...props}
      >
        <div
          className={cn(
            'h-full transition-all duration-300 rounded-full',
            variantColor,
            isIndeterminate && 'w-1/3 animate-[pulse_1.5s_ease-in-out_infinite]'
          )}
          style={{ width: isIndeterminate ? undefined : `${percentage}%` }}
        />
      </div>
    );
  }
);

Progress.displayName = 'Progress';
