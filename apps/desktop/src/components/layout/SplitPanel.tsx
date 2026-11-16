import * as React from 'react';
import { cn } from '@/lib/utils';

export interface SplitPanelProps extends React.HTMLAttributes<HTMLDivElement> {
  left: React.ReactNode;
  right: React.ReactNode;
  leftWidthClass?: string;
}

export function SplitPanel({
  left,
  right,
  leftWidthClass = 'w-full lg:w-1/2',
  className,
  ...props
}: SplitPanelProps) {
  return (
    <div
      className={cn(
        'flex flex-col lg:flex-row items-stretch gap-4 w-full overflow-hidden',
        className
      )}
      {...props}
    >
      <div className={cn('flex flex-col shrink-0 overflow-y-auto', leftWidthClass)}>{left}</div>
      <div className="flex-1 flex flex-col overflow-y-auto min-w-0">{right}</div>
    </div>
  );
}
