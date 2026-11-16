import * as React from 'react';
import { CalendarClock, ShieldCheck, Sparkles, ArrowRight, ExternalLink } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button, buttonVariants } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export interface ModuleUnavailableStateProps extends React.HTMLAttributes<HTMLDivElement> {
  moduleName: string;
  stageTag: string;
  stageName: string;
  description: string;
  plannedCapabilities?: string[];
  docsHref?: string;
  onExploreFoundation?: () => void;
}

export const ModuleUnavailableState: React.FC<ModuleUnavailableStateProps> = ({
  className,
  moduleName,
  stageTag,
  stageName,
  description,
  plannedCapabilities = [],
  docsHref,
  onExploreFoundation,
  ...props
}) => {
  return (
    <div
      role="region"
      aria-label={`${moduleName} Status`}
      className={cn(
        'relative overflow-hidden rounded-xl border border-primary/20 bg-gradient-to-br from-card/90 via-card/60 to-primary/5 p-6 shadow-sm backdrop-blur-md',
        className
      )}
      {...props}
    >
      <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <Badge
              variant="outline"
              className="border-primary/40 bg-primary/10 text-xs font-semibold text-primary"
            >
              <CalendarClock className="mr-1.5 h-3.5 w-3.5" />
              Scheduled for {stageTag}
            </Badge>
            <Badge
              variant="neutral"
              className="border-border text-xs font-medium text-muted-foreground"
            >
              <ShieldCheck className="mr-1 h-3.5 w-3.5 text-status-success" />
              Architecture & Data Contracts Ready
            </Badge>
          </div>

          <div>
            <h3 className="text-lg font-bold text-foreground">
              {moduleName} Engine ({stageName})
            </h3>
            <p className="mt-1 text-sm text-muted-foreground max-w-2xl leading-relaxed">
              {description}
            </p>
          </div>

          {plannedCapabilities.length > 0 && (
            <div className="pt-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Planned Autonomous Capabilities:
              </span>
              <ul className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
                {plannedCapabilities.map((cap, idx) => (
                  <li key={idx} className="flex items-center gap-2 text-xs text-foreground/90">
                    <Sparkles className="h-3.5 w-3.5 shrink-0 text-primary" />
                    <span>{cap}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="flex shrink-0 flex-col gap-2 pt-2 sm:pt-0">
          {onExploreFoundation && (
            <Button size="sm" onClick={onExploreFoundation} className="gap-1.5 text-xs shadow-sm">
              Explore Workspace
              <ArrowRight className="h-3.5 w-3.5" />
            </Button>
          )}
          {docsHref && (
            <a
              href={docsHref}
              target="_blank"
              rel="noreferrer"
              className={cn(
                buttonVariants({ variant: 'outline', size: 'sm' }),
                'gap-1.5 text-xs text-muted-foreground'
              )}
            >
              Stage Specification
              <ExternalLink className="h-3 w-3" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
};

ModuleUnavailableState.displayName = 'ModuleUnavailableState';
