import * as React from 'react';
import {
  Sliders,
} from 'lucide-react';
import { Card, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

export const SoftPreferencesTab: React.FC = () => {
  const [weights, setWeights] = React.useState({
    titleMatch: 30,
    compensation: 20,
    seniority: 15,
    arrangement: 15,
    skills: 10,
    employerTier: 10,
  });

  const total = Object.values(weights).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-semibold text-slate-200">Soft Preference Ranking & Scoring Weights</h3>
        <p className="text-xs text-slate-400">
          When multiple opportunities meet all hard invariants, the soft scoring engine calculates an affinity score (0 to 100) to prioritize high-value matches.
        </p>
      </div>

      <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xs font-semibold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
            <Sliders className="w-4 h-4" />
            Ranking Weight Distribution
          </CardTitle>
          <Badge
            variant="neutral"
            className={
              total === 100
                ? 'bg-emerald-950/60 text-emerald-400 border-emerald-800 text-[10px]'
                : 'bg-amber-950/60 text-amber-400 border-amber-800 text-[10px]'
            }
          >
            Total: {total}% {total === 100 ? '(Balanced)' : '(Unbalanced)'}
          </Badge>
        </div>

        <div className="space-y-3 text-xs">
          {[
            {
              key: 'titleMatch' as const,
              label: 'Role Title & Specialization Match',
              desc: 'Affinity to primary target roles and exact technical title keywords.',
            },
            {
              key: 'compensation' as const,
              label: 'Compensation Upside Above Target',
              desc: 'Premiums offered above target base compensation.',
            },
            {
              key: 'seniority' as const,
              label: 'Seniority Level Alignment',
              desc: 'Exact match with chosen career level.',
            },
            {
              key: 'arrangement' as const,
              label: 'Work Arrangement Preference',
              desc: 'Full remote vs hybrid proximity.',
            },
            {
              key: 'skills' as const,
              label: 'Evidenced Skill Overlap',
              desc: 'Percentage of requested technologies evidenced in verified profile.',
            },
            {
              key: 'employerTier' as const,
              label: 'Employer Allowlist Tier',
              desc: 'Priority tier rank of the hiring organization.',
            },
          ].map((dim) => (
            <div key={dim.key} className="p-2.5 rounded bg-slate-950/40 border border-slate-800/80">
              <div className="flex items-center justify-between mb-1">
                <div>
                  <span className="font-semibold text-slate-200 block">{dim.label}</span>
                  <span className="text-[11px] text-slate-400">{dim.desc}</span>
                </div>
                <span className="font-mono text-cyan-400 font-bold ml-2">{weights[dim.key]}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="50"
                step="5"
                value={weights[dim.key]}
                onChange={(e) =>
                  setWeights((prev) => ({
                    ...prev,
                    [dim.key]: Number(e.target.value),
                  }))
                }
                className="w-full accent-cyan-500"
              />
            </div>
          ))}
        </div>

        <div className="flex justify-end pt-2">
          <Button size="sm" className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs">
            Save Preference Weights
          </Button>
        </div>
      </Card>
    </div>
  );
};
