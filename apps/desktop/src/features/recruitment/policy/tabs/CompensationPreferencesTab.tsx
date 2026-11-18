import * as React from 'react';
import {
  DollarSign,
  AlertTriangle,
} from 'lucide-react';
import { Card, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type {
  CareerStrategy,
  CompensationUnit,
  UndisclosedSalaryHandling,
  CareerStrategyUpdateRequest,
} from '@autonom/shared-types';

interface CompensationPreferencesTabProps {
  strategy: CareerStrategy | null;
  onUpdateStrategy: (id: string, req: CareerStrategyUpdateRequest) => Promise<void>;
}

export const CompensationPreferencesTab: React.FC<CompensationPreferencesTabProps> = ({
  strategy,
  onUpdateStrategy,
}) => {
  const [targetAmount, setTargetAmount] = React.useState<number | ''>(
    strategy?.compensation.target_amount || ''
  );
  const [floorAmount, setFloorAmount] = React.useState<number | ''>(
    strategy?.compensation.hard_floor_amount || ''
  );
  const [currency, setCurrency] = React.useState(strategy?.compensation.currency || 'USD');
  const [unit, setUnit] = React.useState<CompensationUnit>(
    strategy?.compensation.unit || 'annual'
  );
  const [undisclosedHandling, setUndisclosedHandling] = React.useState<UndisclosedSalaryHandling>(
    strategy?.compensation.undisclosed_handling || 'require_review'
  );
  const [equityRequired, setEquityRequired] = React.useState(
    strategy?.compensation.equity_required || false
  );

  React.useEffect(() => {
    if (strategy) {
      setTargetAmount(strategy.compensation.target_amount || '');
      setFloorAmount(strategy.compensation.hard_floor_amount || '');
      setCurrency(strategy.compensation.currency);
      setUnit(strategy.compensation.unit);
      setUndisclosedHandling(strategy.compensation.undisclosed_handling);
      setEquityRequired(strategy.compensation.equity_required);
    }
  }, [strategy]);

  const handleSave = async () => {
    if (!strategy) return;
    await onUpdateStrategy(strategy.id, {
      compensation: {
        ...strategy.compensation,
        target_amount: targetAmount ? Number(targetAmount) : undefined,
        hard_floor_amount: floorAmount ? Number(floorAmount) : undefined,
        currency,
        unit,
        undisclosed_handling: undisclosedHandling,
        equity_required: equityRequired,
      },
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-semibold text-slate-200">Compensation Policies & Salary Floor Guard</h3>
        <p className="text-xs text-slate-400">
          Enforce hard salary floors below which opportunities are automatically rejected, handle undisclosed postings without guessing, and configure target currency and equity preferences.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Core Salary Settings */}
        <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-4">
          <CardTitle className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
            <DollarSign className="w-4 h-4" />
            Base Compensation Parameters
          </CardTitle>

          <div className="space-y-3 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-300 font-medium block mb-1">Target Compensation</label>
                <Input
                  type="number"
                  placeholder="e.g. 140000"
                  value={targetAmount}
                  onChange={(e) => setTargetAmount(e.target.value ? Number(e.target.value) : '')}
                  className="bg-slate-950 border-slate-700 text-xs font-mono"
                />
              </div>

              <div>
                <label className="text-xs text-rose-400 font-medium block mb-1">
                  Hard Floor (Absolute Min)
                </label>
                <Input
                  type="number"
                  placeholder="e.g. 110000"
                  value={floorAmount}
                  onChange={(e) => setFloorAmount(e.target.value ? Number(e.target.value) : '')}
                  className="bg-slate-950 border-rose-900 text-xs font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-300 font-medium block mb-1">Currency</label>
                <select
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-slate-200"
                >
                  <option value="USD">USD ($)</option>
                  <option value="CAD">CAD ($)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="GBP">GBP (£)</option>
                  <option value="INR">INR (₹)</option>
                </select>
              </div>

              <div>
                <label className="text-xs text-slate-300 font-medium block mb-1">Rate Unit</label>
                <select
                  value={unit}
                  onChange={(e) => setUnit(e.target.value as CompensationUnit)}
                  className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-slate-200"
                >
                  <option value="annual">Annual Salary</option>
                  <option value="hourly">Hourly Rate</option>
                  <option value="monthly">Monthly</option>
                  <option value="weekly">Weekly</option>
                  <option value="daily">Daily</option>
                  <option value="stipend">Stipend</option>
                </select>
              </div>
            </div>
          </div>
        </Card>

        {/* Undisclosed Salary Policy */}
        <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-4">
          <CardTitle className="text-xs font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            Undisclosed Salary Handling Policy
          </CardTitle>

          <div className="space-y-3 text-xs">
            <p className="text-slate-400">
              When a job listing does not state a salary or compensation range, AUTONOM must adhere to your explicit preference rather than inventing an estimate:
            </p>

            <div className="space-y-2">
              {[
                {
                  value: 'require_review',
                  title: 'Require Human Review (Recommended)',
                  desc: 'Flag the posting and queue it for human decision before preparing an application.',
                },
                {
                  value: 'consider',
                  title: 'Consider Automatically',
                  desc: 'Assume acceptable compensation if role title and seniority match, proceeding normally.',
                },
                {
                  value: 'exclude',
                  title: 'Exclude Immediately',
                  desc: 'Reject all listings that fail to disclose explicit salary numbers upfront.',
                },
              ].map((opt) => (
                <label
                  key={opt.value}
                  className={`block p-2.5 rounded border cursor-pointer transition-all ${
                    undisclosedHandling === opt.value
                      ? 'bg-amber-950/40 border-amber-500 text-amber-200'
                      : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <input
                      type="radio"
                      name="undisclosed"
                      value={opt.value}
                      checked={undisclosedHandling === opt.value}
                      onChange={() => setUndisclosedHandling(opt.value as UndisclosedSalaryHandling)}
                      className="mt-0.5 text-amber-500"
                    />
                    <div>
                      <span className="font-semibold text-xs block">{opt.title}</span>
                      <span className="text-[11px] text-slate-400">{opt.desc}</span>
                    </div>
                  </div>
                </label>
              ))}
            </div>

            <div className="pt-2">
              <label className="flex items-center gap-2 cursor-pointer text-slate-300">
                <input
                  type="checkbox"
                  checked={equityRequired}
                  onChange={(e) => setEquityRequired(e.target.checked)}
                  className="rounded text-cyan-500"
                />
                <span>Require equity / stock options (RSUs) in package</span>
              </label>
            </div>
          </div>
        </Card>
      </div>

      <div className="flex justify-end pt-2">
        <Button
          size="sm"
          className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs"
          onClick={handleSave}
        >
          Save Compensation Policies
        </Button>
      </div>
    </div>
  );
};
