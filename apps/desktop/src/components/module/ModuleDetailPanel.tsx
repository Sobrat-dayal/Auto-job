import * as React from 'react';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export interface ModuleDetailPanelProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  subtitle?: string;
  onClose: () => void;
  actions?: React.ReactNode;
  children: React.ReactNode;
}

export const ModuleDetailPanel: React.FC<ModuleDetailPanelProps> = ({
  className,
  title,
  subtitle,
  onClose,
  actions,
  children,
  ...props
}) => {
  return (
    <div
      role="region"
      aria-label={`${title} inspector`}
      className={cn('flex h-full flex-col overflow-hidden', className)}
      {...props}
    >
      <div className="flex items-center justify-between border-b border-border/60 px-5 py-4">
        <div className="min-w-0 flex-1">
          <h2 className="truncate text-sm font-semibold text-foreground sm:text-base">{title}</h2>
          {subtitle && <p className="truncate text-xs text-muted-foreground">{subtitle}</p>}
        </div>

        <div className="flex items-center gap-1.5 pl-2">
          {actions}
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
            onClick={onClose}
            aria-label="Close details"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-4">{children}</div>
    </div>
  );
};

ModuleDetailPanel.displayName = 'ModuleDetailPanel';
