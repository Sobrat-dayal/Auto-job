import * as React from 'react';
import { Briefcase, Compass, ArrowRight } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { RecruitmentSummary } from '@/types/dashboard';

interface JobDiscoveryOverviewProps {
  recruitment?: RecruitmentSummary;
  isConnected: boolean;
  onNavigateToRecruitment?: () => void;
}

export const JobDiscoveryOverview: React.FC<JobDiscoveryOverviewProps> = ({
  recruitment,
  isConnected,
  onNavigateToRecruitment,
}) => {
  const jobsCount = recruitment?.jobs_discovered || 0;
  const jobsToday = recruitment?.jobs_discovered_today || 0;
  const activeListings = recruitment?.active_listings || 0;

  return (
    <Card className="border-border/60 bg-surface/50 select-none flex flex-col justify-between">
      <CardHeader className="p-4 pb-2">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent-primary/10 text-accent-primary border border-accent-primary/20">
              <Briefcase className="h-4 w-4" />
            </div>
            <div>
              <CardTitle className="text-sm font-semibold text-foreground">
                Job Discovery Engine
              </CardTitle>
              <CardDescription className="text-[11px] text-foreground-muted">
                Opportunity scouting across LinkedIn, Indeed, Greenhouse, and Lever
              </CardDescription>
            </div>
          </div>

          <Badge
            variant="outline"
            className="border-accent-primary/40 text-accent-primary text-[10px]"
          >
            Stage 26
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="p-4 pt-2 space-y-3">
        {/* Metric tiles */}
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="p-2 rounded-lg bg-surface-elevated/40 border border-border/40">
            <span className="text-[10px] text-foreground-muted block">Total Discovered</span>
            <span className="font-mono-tech text-base font-bold text-foreground">
              {isConnected ? jobsCount : '0'}
            </span>
          </div>

          <div className="p-2 rounded-lg bg-surface-elevated/40 border border-border/40">
            <span className="text-[10px] text-foreground-muted block">Discovered Today</span>
            <span className="font-mono-tech text-base font-bold text-accent-cyan">
              {isConnected ? jobsToday : '0'}
            </span>
          </div>

          <div className="p-2 rounded-lg bg-surface-elevated/40 border border-border/40">
            <span className="text-[10px] text-foreground-muted block">Active Listings</span>
            <span className="font-mono-tech text-base font-bold text-foreground">
              {isConnected ? activeListings : '0'}
            </span>
          </div>
        </div>

        {/* Discovery State Banner */}
        {jobsCount === 0 ? (
          <div className="rounded-lg border border-border/40 bg-surface-elevated/20 p-3 space-y-1.5 text-xs text-foreground-secondary">
            <div className="flex items-center gap-1.5 font-medium text-foreground text-[11px]">
              <Compass className="h-3.5 w-3.5 text-accent-cyan" />
              <span>Awaiting Autonomous Discovery (Stage 26)</span>
            </div>
            <p className="text-[11px] text-foreground-muted leading-relaxed">
              No job listings have been scouted yet. The autonomous multi-platform crawler, ATS
              connector, and semantic match scorer are scheduled for Stage 26.
            </p>
          </div>
        ) : (
          <div className="p-2.5 rounded-lg border border-border/40 bg-surface-elevated/30 flex items-center justify-between text-xs">
            <span className="text-foreground-secondary text-[11px]">
              {jobsCount} job listing records currently in SQLite.
            </span>
            <Badge variant="success" dot className="text-[10px]">
              DB SYNCED
            </Badge>
          </div>
        )}

        {/* Action Link */}
        <div className="flex items-center justify-between pt-1 border-t border-border/30">
          <span className="text-[10px] text-foreground-muted font-mono-tech">
            Table: job_listings (WAL)
          </span>

          <Button
            variant="ghost"
            size="sm"
            onClick={onNavigateToRecruitment}
            className="h-7 text-xs gap-1 text-accent-primary hover:text-accent-primary"
          >
            <span>Open Jobs & Applications</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
