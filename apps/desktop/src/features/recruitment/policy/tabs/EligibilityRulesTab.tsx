import * as React from 'react';
import {
  GraduationCap,
  FileCheck2,
} from 'lucide-react';
import { Card, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type {
  CareerStrategy,
  EligibilityRulesConfig,
  CareerStrategyUpdateRequest,
} from '@autonom/shared-types';

interface EligibilityRulesTabProps {
  strategy: CareerStrategy | null;
  onUpdateStrategy: (id: string, req: CareerStrategyUpdateRequest) => Promise<void>;
}

export const EligibilityRulesTab: React.FC<EligibilityRulesTabProps> = ({
  strategy,
  onUpdateStrategy,
}) => {
  const [rules, setRules] = React.useState<EligibilityRulesConfig>(
    strategy?.eligibility_rules || {
      enforce_degree_requirements: true,
      allow_enrolled_for_future_grads: true,
      enforce_work_authorization: true,
      enforce_minimum_experience: true,
      enforce_required_certifications: true,
      minimum_skill_match_percentage: 60.0,
      require_evidenced_skills: false,
    }
  );

  React.useEffect(() => {
    if (strategy?.eligibility_rules) {
      setRules(strategy.eligibility_rules);
    }
  }, [strategy]);

  const toggleRule = (key: keyof EligibilityRulesConfig) => {
    setRules((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const handleSave = async () => {
    if (!strategy) return;
    await onUpdateStrategy(strategy.id, {
      eligibility_rules: rules,
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-semibold text-slate-200">Factual Job Eligibility Rules & Verification Standards</h3>
        <p className="text-xs text-slate-400">
          Strictly separate applicant aspirations from verified facts. The eligibility engine evaluates true claims from Stage 21 profile facts and Stage 22 GitHub commits, preventing AUTONOM from claiming unverified qualifications.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Education & Experience Audits */}
        <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-4">
          <CardTitle className="text-xs font-semibold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
            <GraduationCap className="w-4 h-4" />
            Education & Experience Invariants
          </CardTitle>

          <div className="space-y-3 text-xs">
            <label className="flex items-start gap-2.5 cursor-pointer">
              <input
                type="checkbox"
                checked={rules.enforce_degree_requirements}
                onChange={() => toggleRule('enforce_degree_requirements')}
                className="mt-0.5 rounded text-cyan-500"
              />
              <div>
                <span className="font-semibold text-slate-200 block">Strictly Enforce Degree Level</span>
                <span className="text-slate-400 text-[11px]">
                  Reject jobs requiring a Masters/PhD if your canonical profile only holds a Bachelor degree.
                </span>
              </div>
            </label>

            <label className="flex items-start gap-2.5 cursor-pointer">
              <input
                type="checkbox"
                checked={rules.allow_enrolled_for_future_grads}
                onChange={() => toggleRule('allow_enrolled_for_future_grads')}
                className="mt-0.5 rounded text-cyan-500"
              />
              <div>
                <span className="font-semibold text-slate-200 block">Allow Current Enrollment for Internships</span>
                <span className="text-slate-400 text-[11px]">
                  Permit jobs for upcoming graduation dates if profile shows current enrollment.
                </span>
              </div>
            </label>

            <label className="flex items-start gap-2.5 cursor-pointer">
              <input
                type="checkbox"
                checked={rules.enforce_minimum_experience}
                onChange={() => toggleRule('enforce_minimum_experience')}
                className="mt-0.5 rounded text-cyan-500"
              />
              <div>
                <span className="font-semibold text-slate-200 block">Enforce Experience Year Thresholds</span>
                <span className="text-slate-400 text-[11px]">
                  Reject jobs asking for 8+ years of experience if verified employment history is 3 years.
                </span>
              </div>
            </label>
          </div>
        </Card>

        {/* Legal & Skill Standards */}
        <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-4">
          <CardTitle className="text-xs font-semibold text-purple-400 uppercase tracking-wider flex items-center gap-2">
            <FileCheck2 className="w-4 h-4" />
            Work Authorization & Skill Evidence
          </CardTitle>

          <div className="space-y-3 text-xs">
            <label className="flex items-start gap-2.5 cursor-pointer">
              <input
                type="checkbox"
                checked={rules.enforce_work_authorization}
                onChange={() => toggleRule('enforce_work_authorization')}
                className="mt-0.5 rounded text-cyan-500"
              />
              <div>
                <span className="font-semibold text-slate-200 block">Work Authorization / Sponsorship Guard</span>
                <span className="text-slate-400 text-[11px]">
                  Require human review if legal authorization in the job country cannot be verified.
                </span>
              </div>
            </label>

            <label className="flex items-start gap-2.5 cursor-pointer">
              <input
                type="checkbox"
                checked={rules.require_evidenced_skills}
                onChange={() => toggleRule('require_evidenced_skills')}
                className="mt-0.5 rounded text-cyan-500"
              />
              <div>
                <span className="font-semibold text-slate-200 block">Require Proven Evidence for Critical Skills</span>
                <span className="text-slate-400 text-[11px]">
                  Demand commits, code artifacts, or verified claims for key technical requirements.
                </span>
              </div>
            </label>

            <div>
              <label className="text-slate-300 font-medium block mb-1">
                Minimum Skill Match Threshold ({rules.minimum_skill_match_percentage}%)
              </label>
              <input
                type="range"
                min="30"
                max="90"
                step="5"
                value={rules.minimum_skill_match_percentage}
                onChange={(e) =>
                  setRules((prev) => ({
                    ...prev,
                    minimum_skill_match_percentage: Number(e.target.value),
                  }))
                }
                className="w-full accent-cyan-500"
              />
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
          Save Eligibility Rules
        </Button>
      </div>
    </div>
  );
};
