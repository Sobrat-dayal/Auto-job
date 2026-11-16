import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export const buttonVariants = cva(
  'inline-flex items-center justify-center font-medium transition-colors select-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-1 focus-visible:ring-offset-background disabled:opacity-50 disabled:pointer-events-none active:scale-[0.98]',
  {
    variants: {
      variant: {
        primary:
          'bg-primary text-white hover:bg-primary-hover active:bg-primary-active border border-primary/40 shadow-subtle',
        secondary:
          'bg-surface-elevated text-foreground hover:bg-surface-hover active:bg-surface-secondary border border-border text-foreground',
        outline:
          'bg-transparent text-foreground hover:bg-surface-hover active:bg-surface-elevated border border-border',
        ghost:
          'bg-transparent text-foreground-secondary hover:text-foreground hover:bg-surface-hover active:bg-surface-elevated',
        destructive:
          'bg-status-error/15 text-status-error hover:bg-status-error/25 active:bg-status-error/35 border border-status-error/30',
        cyan: 'bg-cyan/15 text-cyan hover:bg-cyan/25 active:bg-cyan/35 border border-cyan/30',
        link: 'bg-transparent text-primary underline-offset-4 hover:underline p-0 h-auto active:scale-100',
      },
      size: {
        sm: 'h-7 px-2.5 text-xs rounded-sm gap-1.5',
        md: 'h-9 px-3.5 text-sm rounded-md gap-2',
        lg: 'h-10 px-4 text-base rounded-md gap-2.5',
        icon: 'h-8 w-8 p-0 rounded-md shrink-0',
        'icon-sm': 'h-7 w-7 p-0 rounded-sm shrink-0',
      },
    },
    defaultVariants: {
      variant: 'secondary',
      size: 'md',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
  isLoading?: boolean;
  loadingText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      isLoading = false,
      loadingText,
      leftIcon,
      rightIcon,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        className={cn(buttonVariants({ variant, size, className }))}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <>
            <Loader2 className="w-3.5 h-3.5 animate-spin shrink-0" />
            {loadingText || children}
          </>
        ) : (
          <>
            {leftIcon && <span className="shrink-0">{leftIcon}</span>}
            {children}
            {rightIcon && <span className="shrink-0">{rightIcon}</span>}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';
