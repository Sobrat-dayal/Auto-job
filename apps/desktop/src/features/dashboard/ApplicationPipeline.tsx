import * as React from 'react';
import {
  Send,
  Layers,
  ArrowRight,
  CheckCircle2,
  Clock,
  Sparkles,
  Inbox,
  Video,
  Award,
  XCircle,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import type { RecruitmentSummary } from '@/types/dashboard';

interface ApplicationPipelineProps {
  recruitment?: RecruitmentSummary;
  isConnected: boolean;
  onNavigateToApplications?: () => void;
}

interface PipelineStageConfig {
  key: string;
  label: string;
  stageNum: number;
  icon: React.ComponentType<{ className?: string }>;
}

const PIPELINE_STAGES: PipelineStageConfig[] = [
  { key: 'discovered', label: 'Discovered', stageNum: 1, icon: Layers },
  { key: 'evaluated', label: 'Evaluated', stageNum: 2, icon: Sparkles },
  { key: 'matched', label: 'Matched', stageNum: 3, icon: CheckCircle2 },
  { key: 'queued', label: 'Queued', stageNum: 4, icon: Clock },
  { key: 'preparing', label: 'Preparing', stageNum: 5, icon: Layers },
  { key: 'submitted', label: 'Submitted', stageNum: 6, icon: Send },
  { key: 'recruiter_response', label: 'Response', stageNum: 7, icon: Inbox },
  { key: 'interview', label: 'Interview', stageNum: 8, icon: Video },
  { key: 'offer', label: 'Offer', stageNum: 9, icon: Award },
  { key: 'rejected', label: 'Closed', stageNum: 10, icon: XCircle },
];

export const ApplicationPipeline: React.FC<ApplicationPipelineProps> = ({
  recruitment,
  isConnected,
  onNavigateToApplications,
}) => {
  const stages = recruitment?.pipeline_stages || {};
  const totalApps = recruitment?.applications_total || 0;

  return (
    <Card className="border-border/60 bg-surface/50 select-none flex flex-col justify-between">
      <CardHeader className="p-4 pb-2">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20">
              <Send className="h-4 w-4" />
            </div>
            <div>
              <CardTitle className="text-sm font-semibold text-foreground">
                Recruitment Application Pipeline
              </CardTitle>
              <CardDescription className="text-[11px] text-foreground-muted">
                10-stage lifecycle from discovery to offer acceptance
              </CardDescription>
            </div>
          </div>

          <Badge variant="outline" className="border-accent-cyan/40 text-accent-cyan text-[10px]">
            Stage 31
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="p-4 pt-2 space-y-3">
        {/* Horizontal 10-Stage Pipeline Flow */}
        <div className="grid grid-cols-5 sm:grid-cols-10 gap-1.5 p-2 rounded-lg bg-surface-elevated/40 border border-border/40">
          {PIPELINE_STAGES.map((stg) => {
            const count = isConnected ? stages[stg.key] || 0 : 0;
            const Icon = stg.icon;
            const hasItems = count > 0;

            return (
              <Tooltip key={stg.key}>
                <TooltipTrigger asChild>
                  <div
                    className={`flex flex-col items-center justify-center p-2 rounded transition-colors text-center cursor-default ${
                      hasItems
                        ? 'bg-accent-primary/15 border border-accent-primary/40 text-accent-primary font-semibold'
                        : 'bg-surface/50 border border-border/30 text-foreground-muted hover:border-border/60'
                    }`}
                  >
                    <Icon
                      className={`h-3.5 w-3.5 mb-1 ${
                        hasItems ? 'text-accent-primary' : 'text-foreground-muted/70'
                      }`}
                    />
                    <span className="font-mono-tech text-xs font-bold leading-none">{count}</span>
                    <span className="text-[9px] truncate max-w-full text-foreground-muted mt-1">
                      {stg.label}
                    </span>
                  </div>
                </TooltipTrigger>
                <TooltipContent side="top">
                  <div className="text-xs">
                    <p className="font-semibold text-foreground">
                      Stage {stg.stageNum}: {stg.label}
                    </p>
                    <p className="text-[10px] text-foreground-muted">
                      {count} application records in SQLite
                    </p>
                  </div>
                </TooltipContent>
              </Tooltip>
            );
          })}
        </div>

        {/* Empty State Banner */}
        {totalApps === 0 ? (
          <div className="rounded-lg border border-border/40 bg-surface-elevated/20 p-3 space-y-1.5 text-xs text-foreground-secondary">
            <div className="flex items-center gap-1.5 font-medium text-foreground text-[11px]">
              <Clock className="h-3.5 w-3.5 text-accent-primary" />
              <span>Application Tracking Inactive (Scheduled Stage 31)</span>
            </div>
            <p className="text-[11px] text-foreground-muted leading-relaxed">
              No applications have been drafted or submitted yet. The automated form filler, cover
              letter generator, and submission coordinator will go live in Stage 31.
            </p>
          </div>
        ) : (
          <div className="p-2.5 rounded-lg border border-border/40 bg-surface-elevated/30 flex items-center justify-between text-xs">
            <span className="text-foreground-secondary text-[11px]">
              {totalApps} active application records in SQLite.
            </span>
            <Badge variant="cyan" dot className="text-[10px]">
              ACTIVE PIPELINE
            </Badge>
          </div>
        )}

        {/* Footer Navigation */}
        <div className="flex items-center justify-between pt-1 border-t border-border/30">
          <span className="text-[10px] text-foreground-muted font-mono-tech">
            Table: applications (WAL)
          </span>

          <Button
            variant="ghost"
            size="sm"
            onClick={onNavigateToApplications}
            className="h-7 text-xs gap-1 text-accent-cyan hover:text-accent-cyan"
          >
            <span>View Kanban Board</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
