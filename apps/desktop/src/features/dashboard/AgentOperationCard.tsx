import * as React from 'react';
import { Bot, Compass, FileText, Info, Layers } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import type { AgentOperationStatus, AgentOperationState } from '@/types/dashboard';

interface AgentOperationCardProps {
  agent: AgentOperationStatus;
  onInspect?: (agentId: string) => void;
}

export const AgentOperationCard: React.FC<AgentOperationCardProps> = ({ agent, onInspect }) => {
  const getStatusBadge = (status: AgentOperationState) => {
    switch (status) {
      case 'running':
        return (
          <Badge variant="cyan" dot pulse>
            RUNNING
          </Badge>
        );
      case 'planning':
        return (
          <Badge variant="warning" dot pulse>
            PLANNING
          </Badge>
        );
      case 'waiting_approval':
        return (
          <Badge variant="warning" dot>
            APPROVAL NEEDED
          </Badge>
        );
      case 'idle':
        return (
          <Badge variant="success" dot>
            IDLE
          </Badge>
        );
      case 'failed':
        return (
          <Badge variant="error" dot>
            FAILED
          </Badge>
        );
      case 'paused':
        return (
          <Badge variant="neutral" dot>
            PAUSED
          </Badge>
        );
      case 'unavailable':
      default:
        return (
          <Badge variant="neutral" className="font-mono-tech text-[10px]">
            UNAVAILABLE ({agent.target_stage})
          </Badge>
        );
    }
  };

  const getAgentIcon = (id: string) => {
    if (id.includes('discovery')) return Compass;
    if (id.includes('application')) return FileText;
    if (id.includes('supervisor')) return Layers;
    return Bot;
  };

  const AgentIcon = getAgentIcon(agent.id);

  return (
    <Card className="border-border/60 bg-surface/50 hover:border-border transition-colors flex flex-col justify-between select-none">
      <CardHeader className="p-4 pb-2 space-y-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent-primary/10 text-accent-primary border border-accent-primary/20 shrink-0">
              <AgentIcon className="h-4 w-4" />
            </div>
            <div className="min-w-0">
              <CardTitle className="text-sm font-semibold text-foreground truncate">
                {agent.name}
              </CardTitle>
              <CardDescription className="text-[11px] text-foreground-muted truncate">
                {agent.role}
              </CardDescription>
            </div>
          </div>

          <div className="shrink-0">{getStatusBadge(agent.status)}</div>
        </div>

        {/* Informative Roadmap Notice / Message */}
        <p className="text-[11px] text-foreground-secondary/90 leading-relaxed line-clamp-2 pt-1 border-t border-border/30">
          {agent.message}
        </p>
      </CardHeader>

      <CardContent className="p-4 pt-2 space-y-3">
        {/* Current Task Progress */}
        <div className="space-y-1.5 p-2 rounded-md bg-surface-elevated/40 border border-border/40">
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-foreground-muted truncate pr-2">
              {agent.current_task || 'Runtime Status'}
            </span>
            <span className="font-mono-tech text-foreground-muted text-[10px] shrink-0">
              {agent.progress !== null && agent.progress !== undefined
                ? `${Math.round(agent.progress)}%`
                : agent.target_stage}
            </span>
          </div>
          <Progress
            value={agent.progress || 0}
            className="h-1.5 bg-surface border border-border/40"
          />
        </div>

        {/* Operational Stats Grid */}
        <div className="grid grid-cols-2 gap-2 text-[11px]">
          <div className="p-1.5 rounded bg-surface/60 border border-border/30">
            <span className="text-[10px] text-foreground-muted block">Tasks Executed</span>
            <span className="font-mono-tech font-semibold text-foreground">
              {agent.successful_tasks + agent.failed_tasks}
            </span>
          </div>

          <div className="p-1.5 rounded bg-surface/60 border border-border/30">
            <span className="text-[10px] text-foreground-muted block">Target Release</span>
            <span className="font-mono-tech font-semibold text-accent-cyan">
              {agent.target_stage}
            </span>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-1 border-t border-border/30 text-xs">
          <span className="text-[10px] text-foreground-muted font-mono-tech">
            {agent.is_available ? 'Active Runtime' : 'Scheduled Capability'}
          </span>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onInspect?.(agent.id)}
                className="h-7 px-2 text-[11px] gap-1 text-foreground-secondary hover:text-foreground"
              >
                <Info className="h-3 w-3" />
                <span>Info</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent side="top">
              View scheduled architecture and capabilities for {agent.name}
            </TooltipContent>
          </Tooltip>
        </div>
      </CardContent>
    </Card>
  );
};
