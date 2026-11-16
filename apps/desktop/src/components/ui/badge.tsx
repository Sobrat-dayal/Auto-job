import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

export const badgeVariants = cva(
  'inline-flex items-center gap-1.5 font-medium transition-colors select-none',
  {
    variants: {
      variant: {
        primary: 'bg-primary/10 text-primary border border-primary/25',
        cyan: 'bg-cyan/10 text-cyan border border-cyan/25',
        success: 'bg-status-success/10 text-status-success border border-status-success/25',
        warning: 'bg-status-warning/10 text-status-warning border border-status-warning/25',
        error: 'bg-status-error/10 text-status-error border border-status-error/25',
        inactive: 'bg-status-inactive/10 text-status-inactive border border-status-inactive/25',
        neutral: 'bg-surface-elevated text-foreground-secondary border border-border',
        outline: 'bg-transparent text-foreground-secondary border border-border',
      },
      size: {
        sm: 'px-1.5 py-0.2 text-[10px] rounded-xs uppercase tracking-wider',
        md: 'px-2 py-0.5 text-xs rounded-sm',
        lg: 'px-2.5 py-1 text-xs rounded-md',
      },
    },
    defaultVariants: {
      variant: 'neutral',
      size: 'md',
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {
  dot?: boolean;
  pulse?: boolean;
}

export function Badge({
  className,
  variant,
  size,
  dot = false,
  pulse = false,
  children,
  ...props
}: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant, size, className }))} {...props}>
      {dot && (
        <span
          className={cn(
            'w-1.5 h-1.5 rounded-full shrink-0',
            variant === 'success' && 'bg-status-success',
            variant === 'warning' && 'bg-status-warning',
            variant === 'error' && 'bg-status-error',
            variant === 'cyan' && 'bg-cyan',
            variant === 'primary' && 'bg-primary',
            variant === 'inactive' && 'bg-status-inactive',
            (!variant || variant === 'neutral' || variant === 'outline') && 'bg-foreground-muted',
            pulse && 'animate-pulse'
          )}
        />
      )}
      {children}
    </div>
  );
}
