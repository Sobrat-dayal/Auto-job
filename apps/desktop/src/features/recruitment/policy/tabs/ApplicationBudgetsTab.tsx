import * as React from 'react';
import {
  Zap,
  Calendar,
  Layers,
  ShieldCheck,
} from 'lucide-react';
import { Card, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type {
  RecruitmentBudget,
} from '@autonom/shared-types';

interface ApplicationBudgetsTabProps {
  budget: RecruitmentBudget | null;
  onUpdateBudget: (req: Partial<RecruitmentBudget>) => Promise<void>;
}

export const ApplicationBudgetsTab: React.FC<ApplicationBudgetsTabProps> = ({
  budget,
  onUpdateBudget,
}) => {
  const [dailyCap, setDailyCap] = React.useState(budget?.daily_application_limit || 10);
  const [weeklyCap, setWeeklyCap] = React.useState(budget?.weekly_application_limit || 50);
  const [monthlyCap, setMonthlyCap] = React.useState(budget?.monthly_application_limit || 150);

  React.useEffect(() => {
    if (budget) {
      setDailyCap(budget.daily_application_limit);
      setWeeklyCap(budget.weekly_application_limit);
      setMonthlyCap(budget.monthly_application_limit);
    }
  }, [budget]);

  const handleSave = async () => {
    await onUpdateBudget({
      daily_application_limit: Number(dailyCap),
      weekly_application_limit: Number(weeklyCap),
      monthly_application_limit: Number(monthlyCap),
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-semibold text-slate-200">Multi-Agent Application Budgets & Concurrency Safety</h3>
        <p className="text-xs text-slate-400">
          Shared atomic quota controller prevents concurrent specialist agents from overbooking applications or exceeding daily safety limits.
        </p>
      </div>

      {/* Quota Progress Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Daily Progress */}
        <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase text-slate-400">Daily Quota</span>
            <Zap className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-slate-100">
            {budget?.daily_applications_count || 0} / {budget?.daily_application_limit || 10}
          </div>
          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
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
          <div className="text-[11px] text-slate-500">
            Remaining: {Math.max(0, (budget?.daily_application_limit || 10) - (budget?.daily_applications_count || 0))} submissions
          </div>
        </Card>

        {/* Weekly Progress */}
        <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase text-slate-400">Weekly Quota</span>
            <Calendar className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-slate-100">
            {budget?.weekly_applications_count || 0} / {budget?.weekly_application_limit || 50}
          </div>
          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div
              className="bg-cyan-500 h-full rounded-full transition-all"
              style={{
                width: `${
                  budget
                    ? Math.min(100, (budget.weekly_applications_count / budget.weekly_application_limit) * 100)
                    : 0
                }%`,
              }}
            />
          </div>
          <div className="text-[11px] text-slate-500">
            Resets on Monday 00:00 UTC
          </div>
        </Card>

        {/* Monthly Progress */}
        <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase text-slate-400">Monthly Quota</span>
            <Layers className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-slate-100">
            {budget?.monthly_applications_count || 0} / {budget?.monthly_application_limit || 150}
          </div>
          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div
              className="bg-purple-500 h-full rounded-full transition-all"
              style={{
                width: `${
                  budget
                    ? Math.min(100, (budget.monthly_applications_count / budget.monthly_application_limit) * 100)
                    : 0
                }%`,
              }}
            />
          </div>
          <div className="text-[11px] text-slate-500">
            Resets on 1st of month 00:00 UTC
          </div>
        </Card>
      </div>

      {/* Budget Limit Configuration */}
      <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-4">
        <CardTitle className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          Application Safety Limit Caps
        </CardTitle>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div>
            <label className="text-xs text-slate-300 font-medium block mb-1">Daily Cap</label>
            <Input
              type="number"
              value={dailyCap}
              onChange={(e) => setDailyCap(Number(e.target.value))}
              className="bg-slate-950 border-slate-700 text-xs font-mono"
              min={1}
              max={50}
            />
          </div>

          <div>
            <label className="text-xs text-slate-300 font-medium block mb-1">Weekly Cap</label>
            <Input
              type="number"
              value={weeklyCap}
              onChange={(e) => setWeeklyCap(Number(e.target.value))}
              className="bg-slate-950 border-slate-700 text-xs font-mono"
              min={5}
              max={250}
            />
          </div>

          <div>
            <label className="text-xs text-slate-300 font-medium block mb-1">Monthly Cap</label>
            <Input
              type="number"
              value={monthlyCap}
              onChange={(e) => setMonthlyCap(Number(e.target.value))}
              className="bg-slate-950 border-slate-700 text-xs font-mono"
              min={10}
              max={1000}
            />
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <Button
            size="sm"
            className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs"
            onClick={handleSave}
          >
            Update Budget Caps
          </Button>
        </div>
      </Card>
    </div>
  );
};
