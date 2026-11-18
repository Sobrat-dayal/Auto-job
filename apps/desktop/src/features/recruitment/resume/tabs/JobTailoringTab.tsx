/**
 * Stage 23: Job-Specific Resume Tailoring Tab.
 * Ingests job descriptions, maps requirements against verified facts, and prioritizes matching skills.
 */

import * as React from 'react';
import {
  Sparkles,
  Briefcase,
  ArrowRight,
  ShieldAlert,
  Search,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type {
  RequirementEvidenceMapping,
  ResumeDocument,
} from '@autonom/shared-types';

interface JobTailoringTabProps {
  resume: ResumeDocument | null;
  onSelectResume: (resume: ResumeDocument) => void;
  onNavigateTab: (tabId: string) => void;
}

export const JobTailoringTab: React.FC<JobTailoringTabProps> = ({
  resume,
  onSelectResume,
  onNavigateTab,
}) => {
  const [jobText, setJobText] = React.useState<string>(
    `Backend Software Engineer - Cloud Systems
Requirements:
- 3+ years experience with Python and FastAPI
- Hands-on implementation with SQL databases (PostgreSQL or SQLite)
- Strong understanding of REST API design and automated testing
- Experience with Docker containerization
- Bonus: Knowledge of Kubernetes and AWS cloud deployments`
  );
  const [targetRole, setTargetRole] = React.useState<string>('Backend Software Engineer');
  const [isAnalyzing, setIsAnalyzing] = React.useState<boolean>(false);
  const [mappings, setMappings] = React.useState<RequirementEvidenceMapping[]>([]);

  const handleAnalyze = async () => {
    if (!jobText.trim()) return;
    setIsAnalyzing(true);
    try {
      await apiClient.analyzeJobDescription({
        raw_text: jobText,
        job_title: targetRole,
      });

      if (resume) {
        const tailored = await apiClient.tailorResume(resume.id, {
          resume_id: resume.id,
          job_description_text: jobText,
          target_role: targetRole,
        });
        setMappings(tailored.evidence_mappings);
        onSelectResume(tailored.resume);
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getMatchBadge = (category: string) => {
    switch (category) {
      case 'directly_supported':
        return <Badge variant="neutral" className="bg-emerald-950/60 text-emerald-400 border-emerald-800/60">Direct Match</Badge>;
      case 'partially_supported':
        return <Badge variant="neutral" className="bg-cyan-950/60 text-cyan-400 border-cyan-800/60">Partial Match</Badge>;
      case 'related_experience':
        return <Badge variant="neutral" className="bg-amber-950/60 text-amber-400 border-amber-800/60">Related Domain</Badge>;
      case 'not_evidenced':
        return <Badge variant="neutral" className="bg-rose-950/60 text-rose-400 border-rose-800/60">Not Evidenced</Badge>;
      default:
        return <Badge variant="neutral" className="bg-slate-800 text-slate-400 border-slate-700">Review Needed</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Job Description Input (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <Briefcase className="w-4 h-4 text-cyan-400" />
                <CardTitle className="text-sm text-slate-200">Job Description Input</CardTitle>
              </div>
              <p className="text-xs text-slate-400">
                Paste job requirements or qualifications to evaluate against verified profile claims.
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs text-slate-300">Target Role Title</label>
                <input
                  type="text"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded p-2 text-xs text-slate-200 font-medium"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs text-slate-300">Job Specification Text</label>
                <textarea
                  value={jobText}
                  onChange={(e) => setJobText(e.target.value)}
                  rows={10}
                  className="w-full bg-slate-950 border border-slate-700 rounded-md p-3 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500 font-mono"
                  placeholder="Paste job posting content here..."
                />
              </div>

              <Button
                size="sm"
                variant="primary"
                disabled={isAnalyzing || !jobText.trim()}
                onClick={handleAnalyze}
                className="w-full bg-cyan-600 hover:bg-cyan-500 text-white"
              >
                <Sparkles className="w-4 h-4 mr-1.5" />
                {isAnalyzing ? 'Analyzing Criteria...' : 'Analyze & Match Evidence'}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Requirement-to-Evidence Match Matrix (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-3 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-sm text-slate-200">Requirement-to-Evidence Matrix</CardTitle>
                <p className="text-xs text-slate-400">
                  Transparent mapping showing which requirements are evidenced and which are missing.
                </p>
              </div>
              {mappings.length > 0 && (
                <Badge variant="neutral" className="bg-cyan-950/60 text-cyan-400 border-cyan-800/60 text-xs">
                  {mappings.filter((m) => m.match_category === 'directly_supported').length} / {mappings.length} Matched
                </Badge>
              )}
            </CardHeader>
            <CardContent className="space-y-3">
              {mappings.length === 0 ? (
                <div className="text-center py-16 space-y-2 text-slate-500 text-xs">
                  <Search className="w-8 h-8 mx-auto text-slate-600" />
                  <p>Paste a job description on the left and click 'Analyze & Match Evidence'.</p>
                </div>
              ) : (
                <div className="space-y-2.5 max-h-[500px] overflow-y-auto pr-1">
                  {mappings.map((m, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs space-y-1.5"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <span className="font-semibold text-slate-200">{m.requirement_text}</span>
                        {getMatchBadge(m.match_category)}
                      </div>
                      <p className="text-slate-400 text-[11px]">{m.explanation}</p>
                      {m.claim_text && (
                        <div className="text-[10px] text-cyan-400/90 font-mono bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800">
                          {m.claim_text}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Zero Hallucination Guarantee Banner */}
              <div className="p-3 rounded-md bg-cyan-950/30 border border-cyan-800/60 flex items-start gap-2 text-xs text-slate-300">
                <ShieldAlert className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold text-cyan-300 block mb-0.5">Zero-Hallucination Tailoring Guarantee</span>
                  Missing skills and unevidenced requirements are never fabricated into the resume. Tailoring re-ranks genuine verified strengths.
                </div>
              </div>

              {resume && mappings.length > 0 && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => onNavigateTab('editor')}
                  className="w-full border-slate-700 text-slate-300 hover:text-cyan-400"
                >
                  Review Tailored Content in Editor
                  <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
                </Button>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

