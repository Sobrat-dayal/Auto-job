import * as React from 'react';
import {
  Compass,
  ShieldCheck,
  Briefcase,
  AlertTriangle,
  Zap,
  TrendingUp,
  Building2,
  DollarSign,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type {
  CareerStrategy,
  RecruitmentBudget,
  AutonomyStatusResponse,
  RecruitmentDecision,
} from '@autonom/shared-types';

interface CareerOverviewTabProps {
  activeStrategy: CareerStrategy | null;
  autonomyStatus: AutonomyStatusResponse | null;
  budget: RecruitmentBudget | null;
  recentDecisions: RecruitmentDecision[];
  onNavigateTab: (tab: string) => void;
}

export const CareerOverviewTab: React.FC<CareerOverviewTabProps> = ({
  activeStrategy,
  autonomyStatus,
  budget,
  recentDecisions,
  onNavigateTab,
}) => {
  const getAutonomyLabel = (mode?: string) => {
    switch (mode) {
      case 'mode_1_research_only':
        return { label: 'Mode 1: Research Only', color: 'bg-blue-950/60 text-blue-400 border-blue-800' };
      case 'mode_2_prepare_and_review':
        return { label: 'Mode 2: Prepare & Review (Default)', color: 'bg-emerald-950/60 text-emerald-400 border-emerald-800' };
      case 'mode_3_preauthorized_preparation':
        return { label: 'Mode 3: Preauthorized Preparation', color: 'bg-purple-950/60 text-purple-400 border-purple-800' };
      case 'mode_4_bounded_autonomous_applications':
        return { label: 'Mode 4: Bounded Autonomous', color: 'bg-amber-950/60 text-amber-400 border-amber-800' };
      default:
        return { label: 'Unknown Mode', color: 'bg-slate-800 text-slate-400 border-slate-700' };
    }
  };

  const autonomyInfo = getAutonomyLabel(autonomyStatus?.active_autonomy_mode);

  return (
    <div className="space-y-6">
      {/* Top Banner / Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Active Strategy Card */}
        <Card className="bg-slate-900/60 border-slate-800">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase text-slate-400 tracking-wider">Active Strategy</span>
              <Compass className="w-4 h-4 text-cyan-400" />
            </div>
            <CardTitle className="text-base text-slate-100 font-bold truncate">
              {activeStrategy ? activeStrategy.title : 'None Selected'}
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <p className="text-xs text-slate-400 truncate mb-3">
              {activeStrategy?.description || 'No strategy description available'}
            </p>
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-500">Target Roles: {activeStrategy?.target_roles.length || 0}</span>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 text-xs text-cyan-400 hover:text-cyan-300 p-0"
                onClick={() => onNavigateTab('strategies')}
              >
                Switch &rarr;
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Autonomy Mode Card */}
        <Card className="bg-slate-900/60 border-slate-800">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase text-slate-400 tracking-wider">Autonomy Level</span>
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="pt-1">
              <Badge variant="neutral" className={`${autonomyInfo.color} text-xs font-mono`}>
                {autonomyInfo.label}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="pt-2">
            <p className="text-xs text-slate-400 mb-3">
              {autonomyStatus?.pending_review_queue_count || 0} applications in review queue
            </p>
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-500">Standing Grants: {autonomyStatus?.standing_grants_count || 0}</span>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 text-xs text-emerald-400 hover:text-emerald-300 p-0"
                onClick={() => onNavigateTab('autonomy')}
              >
                Configure &rarr;
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Daily Application Budget Card */}
        <Card className="bg-slate-900/60 border-slate-800">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase text-slate-400 tracking-wider">Daily Budget</span>
              <Zap className="w-4 h-4 text-amber-400" />
            </div>
            <CardTitle className="text-xl text-slate-100 font-mono">
              {budget ? `${budget.daily_applications_count} / ${budget.daily_application_limit}` : '0 / 10'}
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-2">
              <div
                className="bg-amber-500 h-full rounded-full transition-all"
                style={{
                  width: `${
                    budget
                      ? Math.min(100, (budget.daily_applications_count / budget.daily_application_limit) * 100)
                      : 0
                  }%`,
                }}
              />
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-500">Reservations: {budget?.active_reservations_count || 0}</span>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 text-xs text-amber-400 hover:text-amber-300 p-0"
                onClick={() => onNavigateTab('budgets')}
              >
                Manage &rarr;
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Employer Safety Card */}
        <Card className="bg-slate-900/60 border-slate-800">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase text-slate-400 tracking-wider">Employer Guard</span>
              <Building2 className="w-4 h-4 text-rose-400" />
            </div>
            <CardTitle className="text-base text-slate-100 font-bold">
              {activeStrategy?.employers.blocked_employers.length || 0} Blocked
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <p className="text-xs text-slate-400 mb-3">
              Mode: <span className="font-mono text-slate-300">{activeStrategy?.employers.allowlist_mode || 'no_allowlist'}</span>
            </p>
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-500">Industries: {activeStrategy?.employers.blocked_industries.length || 0}</span>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 text-xs text-rose-400 hover:text-rose-300 p-0"
                onClick={() => onNavigateTab('employers')}
              >
                Rules &rarr;
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Policy Pillars Quick Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Pillar 1: Roles & Seniority */}
        <Card className="bg-slate-900/40 border-slate-800">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <Briefcase className="w-4 h-4 text-cyan-400" />
                Target Roles & Seniority
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 text-xs text-cyan-400 p-0"
                onClick={() => onNavigateTab('target-roles')}
              >
                Edit
              </Button>
            </div>
          </CardHeader>
          <CardContent className="text-xs space-y-2">
            <div>
              <span className="text-slate-500">Allowed Seniority: </span>
              <span className="text-slate-300">
                {activeStrategy?.seniority.target_levels.map((l) => l.replace('_', ' ')).join(', ') || 'Any'}
              </span>
            </div>
            <div>
              <span className="text-slate-500">Primary Roles: </span>
              <span className="text-slate-300">
                {activeStrategy?.target_roles.map((r) => r.title).slice(0, 3).join(', ') || 'None'}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Pillar 2: Geography & Work Arrangement */}
        <Card className="bg-slate-900/40 border-slate-800">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <Compass className="w-4 h-4 text-purple-400" />
                Location & Arrangement
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 text-xs text-purple-400 p-0"
                onClick={() => onNavigateTab('locations')}
              >
                Edit
              </Button>
            </div>
          </CardHeader>
          <CardContent className="text-xs space-y-2">
            <div>
              <span className="text-slate-500">Allowed Arrangements: </span>
              <span className="text-slate-300 uppercase font-mono">
                {activeStrategy?.work_arrangement.allowed_arrangements.join(', ') || 'Remote'}
              </span>
            </div>
            <div>
              <span className="text-slate-500">Countries: </span>
              <span className="text-slate-300">
                {activeStrategy?.geography.preferred_countries.join(', ') || 'Any'}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Pillar 3: Compensation Guard */}
        <Card className="bg-slate-900/40 border-slate-800">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-emerald-400" />
                Compensation Floor
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 text-xs text-emerald-400 p-0"
                onClick={() => onNavigateTab('compensation')}
              >
                Edit
              </Button>
            </div>
          </CardHeader>
          <CardContent className="text-xs space-y-2">
            <div>
              <span className="text-slate-500">Target Salary: </span>
              <span className="text-slate-200 font-mono">
                {activeStrategy?.compensation.target_amount
                  ? `$${activeStrategy.compensation.target_amount.toLocaleString()} ${activeStrategy.compensation.currency}`
                  : 'Flexible'}
              </span>
            </div>
            <div>
              <span className="text-slate-500">Hard Floor: </span>
              <span className="text-rose-400 font-mono">
                {activeStrategy?.compensation.hard_floor_amount
                  ? `$${activeStrategy.compensation.hard_floor_amount.toLocaleString()} ${activeStrategy.compensation.currency}`
                  : 'None'}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Policy Decisions Log */}
      <Card className="bg-slate-900/60 border-slate-800">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-cyan-400" />
              Recent Recruitment Decisions & Audit Trail
            </CardTitle>
            <Button
              variant="outline"
              size="sm"
              className="h-7 text-xs border-slate-700 hover:bg-slate-800 text-slate-300"
              onClick={() => onNavigateTab('simulator')}
            >
              Test New Job in Simulator &rarr;
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {recentDecisions.length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-xs">
              No recent recruitment decisions recorded. Run the policy simulator to evaluate job opportunities against active rules.
            </div>
          ) : (
            <div className="space-y-2.5">
              {recentDecisions.slice(0, 5).map((d) => {
                const isProceed = d.decision === 'proceed' || d.decision === 'proceed_with_conditions';
                const isReview = d.decision === 'needs_review';
                return (
                  <div
                    key={d.id}
                    className="p-3 rounded-lg bg-slate-950/50 border border-slate-800/80 flex items-center justify-between text-xs"
                  >
                    <div className="flex items-start gap-3">
                      {isProceed ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5" />
                      ) : isReview ? (
                        <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5" />
                      ) : (
                        <XCircle className="w-4 h-4 text-rose-400 mt-0.5" />
                      )}
                      <div>
                        <div className="font-semibold text-slate-200 flex items-center gap-2">
                          <span>{d.job_title}</span>
                          <span className="text-slate-500">&bull;</span>
                          <span className="text-slate-400">{d.employer_name}</span>
                        </div>
                        <p className="text-slate-400 text-[11px] mt-0.5">{d.primary_rationale}</p>
                      </div>
                    </div>
                    <div className="text-right space-y-1">
                      <Badge
                        variant="neutral"
                        className={
                          isProceed
                            ? 'bg-emerald-950/60 text-emerald-400 border-emerald-800 text-[10px]'
                            : isReview
                            ? 'bg-amber-950/60 text-amber-400 border-amber-800 text-[10px]'
                            : 'bg-rose-950/60 text-rose-400 border-rose-800 text-[10px]'
                        }
                      >
                        {d.decision.replace(/_/g, ' ').toUpperCase()}
                      </Badge>
                      <div className="text-[10px] text-slate-500 font-mono">
                        Level {d.precedence_level} Precedence
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
