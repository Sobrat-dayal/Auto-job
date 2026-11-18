import * as React from 'react';
import {
  Play,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  FileCode,
  Sparkles,
} from 'lucide-react';
import { Card, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type {
  PolicySimulationRequest,
  PolicySimulationResponse,
  WorkArrangement,
} from '@autonom/shared-types';

interface PolicySimulatorTabProps {
  onSimulate: (req: PolicySimulationRequest) => Promise<PolicySimulationResponse>;
}

export const PolicySimulatorTab: React.FC<PolicySimulatorTabProps> = ({
  onSimulate,
}) => {
  const [jobTitle, setJobTitle] = React.useState('Senior Backend Engineer');
  const [employerName, setEmployerName] = React.useState('TechCorp Global');
  const [workArrangement, setWorkArrangement] = React.useState<WorkArrangement>('remote');
  const [salaryMin, setSalaryMin] = React.useState<number | ''>(135000);
  const [locationCity, setLocationCity] = React.useState('San Francisco');
  const [locationCountry, setLocationCountry] = React.useState('United States');
  const [requiredSkills, setRequiredSkills] = React.useState('Python, FastAPI, PostgreSQL, Docker');
  const [experienceYears, setExperienceYears] = React.useState<number | ''>(4);
  const [requiredDegree, setRequiredDegree] = React.useState('Bachelor');
  const [workAuthRequired, setWorkAuthRequired] = React.useState(true);

  const [simulationResult, setSimulationResult] = React.useState<PolicySimulationResponse | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);

  const handleRunSimulation = async () => {
    setIsLoading(true);
    try {
      const res = await onSimulate({
        synthetic_job: {
          title: jobTitle,
          employer_name: employerName,
          work_arrangement: workArrangement,
          compensation_min: salaryMin ? Number(salaryMin) : undefined,
          location_city: locationCity,
          location_country: locationCountry,
          required_skills: requiredSkills.split(',').map((s) => s.trim()).filter(Boolean),
          required_experience_years: experienceYears ? Number(experienceYears) : undefined,
          required_degree: requiredDegree || undefined,
          work_authorization_required: workAuthRequired,
        },
      });
      setSimulationResult(res);
    } finally {
      setIsLoading(false);
    }
  };

  const decision = simulationResult?.decision;
  const isProceed = decision?.decision === 'proceed' || decision?.decision === 'proceed_with_conditions';
  const isReview = decision?.decision === 'needs_review';

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-semibold text-slate-200">Zero-Side-Effect Policy Sandbox & Simulator</h3>
        <p className="text-xs text-slate-400">
          Hypothetically test any job opportunity against your currently active career strategy, employer restrictions, and factual eligibility standards with zero persistence or real-world action.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Form: Synthetic Job Description */}
        <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-4">
          <CardTitle className="text-xs font-semibold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
            <FileCode className="w-4 h-4" />
            Hypothetical Job Attributes
          </CardTitle>

          <div className="space-y-3 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-300 font-medium block mb-1">Job Title</label>
                <Input
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="bg-slate-950 border-slate-700 text-xs"
                />
              </div>

              <div>
                <label className="text-xs text-slate-300 font-medium block mb-1">Employer Name</label>
                <Input
                  value={employerName}
                  onChange={(e) => setEmployerName(e.target.value)}
                  className="bg-slate-950 border-slate-700 text-xs"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-300 font-medium block mb-1">Work Arrangement</label>
                <select
                  value={workArrangement}
                  onChange={(e) => setWorkArrangement(e.target.value as WorkArrangement)}
                  className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-slate-200"
                >
                  <option value="remote">Remote</option>
                  <option value="hybrid">Hybrid</option>
                  <option value="onsite">Onsite</option>
                </select>
              </div>

              <div>
                <label className="text-xs text-slate-300 font-medium block mb-1">Base Salary Min ($)</label>
                <Input
                  type="number"
                  value={salaryMin}
                  onChange={(e) => setSalaryMin(e.target.value ? Number(e.target.value) : '')}
                  className="bg-slate-950 border-slate-700 text-xs font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-300 font-medium block mb-1">Location City</label>
                <Input
                  value={locationCity}
                  onChange={(e) => setLocationCity(e.target.value)}
                  className="bg-slate-950 border-slate-700 text-xs"
                />
              </div>

              <div>
                <label className="text-xs text-slate-300 font-medium block mb-1">Country</label>
                <Input
                  value={locationCountry}
                  onChange={(e) => setLocationCountry(e.target.value)}
                  className="bg-slate-950 border-slate-700 text-xs"
                />
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-300 font-medium block mb-1">
                Required Skills (comma-separated)
              </label>
              <Input
                value={requiredSkills}
                onChange={(e) => setRequiredSkills(e.target.value)}
                className="bg-slate-950 border-slate-700 text-xs font-mono"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-300 font-medium block mb-1">Experience Years</label>
                <Input
                  type="number"
                  value={experienceYears}
                  onChange={(e) => setExperienceYears(e.target.value ? Number(e.target.value) : '')}
                  className="bg-slate-950 border-slate-700 text-xs font-mono"
                />
              </div>

              <div>
                <label className="text-xs text-slate-300 font-medium block mb-1">Degree Required</label>
                <select
                  value={requiredDegree}
                  onChange={(e) => setRequiredDegree(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-slate-200"
                >
                  <option value="Bachelor">Bachelor Degree</option>
                  <option value="Master">Master Degree</option>
                  <option value="PhD">PhD / Doctorate</option>
                  <option value="Associate">Associate Degree</option>
                  <option value="">No Degree Specified</option>
                </select>
              </div>
            </div>

            <div className="pt-1">
              <label className="flex items-center gap-2 cursor-pointer text-slate-300">
                <input
                  type="checkbox"
                  checked={workAuthRequired}
                  onChange={(e) => setWorkAuthRequired(e.target.checked)}
                  className="rounded text-cyan-500"
                />
                <span>Requires Legal Work Authorization in Target Country</span>
              </label>
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <Button
              size="sm"
              className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs flex items-center gap-1.5"
              onClick={handleRunSimulation}
              disabled={isLoading || !jobTitle.trim() || !employerName.trim()}
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              {isLoading ? 'Simulating...' : 'Run Policy Simulation'}
            </Button>
          </div>
        </Card>

        {/* Results: Decision Breakdown */}
        <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-4">
          <CardTitle className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-400" />
            Decision Rationale & Precedence Audit
          </CardTitle>

          {!decision ? (
            <div className="text-center py-16 text-slate-500 text-xs">
              Configure job parameters on the left and click &quot;Run Policy Simulation&quot; to test.
            </div>
          ) : (
            <div className="space-y-4 text-xs">
              {/* Verdict Header */}
              <div
                className={`p-3.5 rounded-lg border flex items-center justify-between ${
                  isProceed
                    ? 'bg-emerald-950/40 border-emerald-700/80 text-emerald-300'
                    : isReview
                    ? 'bg-amber-950/40 border-amber-700/80 text-amber-300'
                    : 'bg-rose-950/40 border-rose-700/80 text-rose-300'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  {isProceed ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  ) : isReview ? (
                    <AlertTriangle className="w-5 h-5 text-amber-400" />
                  ) : (
                    <XCircle className="w-5 h-5 text-rose-400" />
                  )}
                  <div>
                    <span className="font-bold text-sm block">
                      {decision.decision.replace(/_/g, ' ').toUpperCase()}
                    </span>
                    <span className="text-[11px] opacity-90">
                      Evaluated under Precedence Level {decision.precedence_level}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xs opacity-75 block">Soft Affinity</span>
                  <span className="text-base font-bold font-mono">
                    {decision.soft_preference_score.toFixed(1)} / 100
                  </span>
                </div>
              </div>

              {/* Rationale Text */}
              <div className="p-3 rounded bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-slate-500 text-[11px] font-semibold uppercase block">Primary Rationale</span>
                <p className="text-slate-200 leading-relaxed">{decision.primary_rationale}</p>
                <span className="text-cyan-400 text-[11px] block mt-1">
                  Recommended Action: {decision.recommended_action}
                </span>
              </div>

              {/* Eligibility Assessment Details */}
              {decision.eligibility_assessment && (
                <div className="p-3 rounded bg-slate-950/60 border border-slate-800 space-y-2">
                  <span className="text-slate-500 text-[11px] font-semibold uppercase block">
                    Factual Qualification Assessment
                  </span>
                  <div className="grid grid-cols-2 gap-2 text-[11px]">
                    <div>
                      <span className="text-slate-500">Education Match: </span>
                      <span
                        className={
                          decision.eligibility_assessment.education_matched
                            ? 'text-emerald-400 font-bold'
                            : 'text-rose-400 font-bold'
                        }
                      >
                        {decision.eligibility_assessment.education_matched ? 'Verified' : 'Failed'}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500">Work Authorization: </span>
                      <span
                        className={
                          decision.eligibility_assessment.work_authorization_valid
                            ? 'text-emerald-400 font-bold'
                            : 'text-amber-400 font-bold'
                        }
                      >
                        {decision.eligibility_assessment.work_authorization_valid ? 'Valid' : 'Requires Review'}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500">Experience Years: </span>
                      <span className="text-slate-300 font-mono">
                        {decision.eligibility_assessment.experience_years_verified} verified /{' '}
                        {decision.eligibility_assessment.experience_years_required} required
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500">Skills Overlap: </span>
                      <span className="text-cyan-400 font-mono font-bold">
                        {decision.eligibility_assessment.skill_match_percentage.toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Review Triggers or Violations */}
              {decision.review_triggers.length > 0 && (
                <div>
                  <span className="text-amber-400 text-[11px] font-semibold uppercase block mb-1">
                    Human Review Triggers
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {decision.review_triggers.map((t, idx) => (
                      <Badge
                        key={idx}
                        variant="neutral"
                        className="bg-amber-950/60 text-amber-300 border-amber-800 text-[10px]"
                      >
                        {t.replace(/_/g, ' ')}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {decision.violations.length > 0 && (
                <div>
                  <span className="text-rose-400 text-[11px] font-semibold uppercase block mb-1">
                    Rule Violations
                  </span>
                  <div className="space-y-1">
                    {decision.violations.map((v, idx) => (
                      <div key={idx} className="text-rose-300 text-[11px] flex items-center gap-1.5">
                        <XCircle className="w-3.5 h-3.5 text-rose-500 shrink-0" />
                        <span>{v}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};
