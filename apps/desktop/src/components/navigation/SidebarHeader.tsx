import * as React from 'react';
import { PanelLeftClose, PanelLeftOpen, Terminal } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';

interface SidebarHeaderProps {
  isExpanded: boolean;
  onToggle: () => void;
}

export const SidebarHeader: React.FC<SidebarHeaderProps> = ({ isExpanded, onToggle }) => {
  return (
    <div
      className={`h-12 border-b border-border/60 flex items-center px-3 select-none ${
        isExpanded ? 'justify-between' : 'justify-center'
      }`}
    >
      {isExpanded ? (
        <>
          <div className="flex items-center gap-2 overflow-hidden">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-accent-primary/10 text-accent-primary border border-accent-primary/30 shrink-0">
              <Terminal className="h-4 w-4" />
            </div>
            <div className="flex items-baseline gap-1.5 min-w-0">
              <span className="font-bold tracking-wider text-xs text-foreground font-sans truncate">
                AUTONOM
              </span>
              <Badge variant="neutral" className="text-[9px] py-0 px-1 font-mono-tech shrink-0">
                v0.1
              </Badge>
            </div>
          </div>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={onToggle}
                className="h-7 w-7 text-foreground-secondary hover:text-foreground hover:bg-surface-elevated shrink-0"
                aria-label="Collapse sidebar (Ctrl+B)"
                aria-expanded={isExpanded}
              >
                <PanelLeftClose className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              Collapse sidebar{' '}
              <span className="text-foreground-muted ml-1 font-mono-tech">Ctrl+B</span>
            </TooltipContent>
          </Tooltip>
        </>
      ) : (
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              onClick={onToggle}
              className="h-8 w-8 text-foreground-secondary hover:text-foreground hover:bg-surface-elevated"
              aria-label="Expand sidebar (Ctrl+B)"
              aria-expanded={isExpanded}
            >
              <PanelLeftOpen className="h-4 w-4 text-accent-primary" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">
            Expand sidebar <span className="text-foreground-muted ml-1 font-mono-tech">Ctrl+B</span>
          </TooltipContent>
        </Tooltip>
      )}
    </div>
  );
};
