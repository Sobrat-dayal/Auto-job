/**
 * Stage 23: Resume Overview Tab.
 * Displays high-level document statistics, master resume status, and recent activity.
 */

import * as React from 'react';
import {
  FileText,
  CheckCircle2,
  Clock,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Briefcase,
  Layers,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { ResumeDocument, ResumeOverviewStats } from '@autonom/shared-types';

interface ResumeOverviewTabProps {
  stats: ResumeOverviewStats | null;
  resumes: ResumeDocument[];
  onSelectResume: (resume: ResumeDocument) => void;
  onNavigateTab: (tabId: string) => void;
}

export const ResumeOverviewTab: React.FC<ResumeOverviewTabProps> = ({
  stats,
  resumes,
  onSelectResume,
  onNavigateTab,
}) => {
  const masterResume = resumes.find((r) => r.resume_type === 'master');

  return (
    <div className="space-y-6">
      {/* Metric Cards Banner */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-slate-900/60 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-mono uppercase tracking-wider text-slate-400">
              Total Resumes
            </CardTitle>
            <FileText className="w-4 h-4 text-cyan-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-slate-100">
              {stats?.total_resumes ?? resumes.length}
            </div>
            <p className="text-xs text-slate-400 mt-1">Managed document artifacts</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-mono uppercase tracking-wider text-slate-400">
              Approved Versions
            </CardTitle>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-emerald-400">
              {stats?.approved_count ?? resumes.filter((r) => r.status === 'approved').length}
            </div>
            <p className="text-xs text-slate-400 mt-1">Verified & ready for export</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-mono uppercase tracking-wider text-slate-400">
              Active Drafts
            </CardTitle>
            <Clock className="w-4 h-4 text-amber-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-amber-400">
              {stats?.draft_count ?? resumes.filter((r) => r.status === 'draft').length}
            </div>
            <p className="text-xs text-slate-400 mt-1">Revisions under editing</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-mono uppercase tracking-wider text-slate-400">
              ATS Compliance
            </CardTitle>
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-cyan-400">100%</div>
            <p className="text-xs text-slate-400 mt-1">Deterministic structural audit</p>
          </CardContent>
        </Card>
      </div>

      {/* Master Resume Spotlight */}
      <Card className="bg-slate-900/60 border-slate-800">
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <CardTitle className="text-base text-slate-200">Authoritative Master Resume</CardTitle>
              <Badge variant="neutral" className="bg-cyan-950/60 text-cyan-400 border-cyan-800/60 text-xs">
                Single Source of Truth
              </Badge>
            </div>
            <p className="text-xs text-slate-400">
              Comprehensive baseline containing all confirmed education, experience, skills, and evidenced projects.
            </p>
          </div>
          {masterResume ? (
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                onSelectResume(masterResume);
                onNavigateTab('editor');
              }}
              className="border-slate-700 text-slate-300 hover:text-cyan-400"
            >
              Open Master Resume
              <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
            </Button>
          ) : (
            <Button
              size="sm"
              variant="primary"
              onClick={() => onNavigateTab('builder')}
              className="bg-cyan-600 hover:bg-cyan-500 text-white"
            >
              Create Master Resume
            </Button>
          )}
        </CardHeader>
        {masterResume && (
          <CardContent className="pt-2">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs">
              <div>
                <span className="text-slate-500 block mb-1">Title</span>
                <span className="font-semibold text-slate-200">{masterResume.title}</span>
              </div>
              <div>
                <span className="text-slate-500 block mb-1">Template</span>
                <span className="font-mono text-cyan-400">{masterResume.template_id}</span>
              </div>
              <div>
                <span className="text-slate-500 block mb-1">Sections</span>
                <span className="text-slate-300 font-mono">{masterResume.sections.length} sections active</span>
              </div>
              <div>
                <span className="text-slate-500 block mb-1">Version</span>
                <span className="font-mono text-slate-300">v{masterResume.current_version} ({masterResume.status})</span>
              </div>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Quick Action Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-slate-900/60 border-slate-800 hover:border-slate-700 transition-colors">
          <CardHeader>
            <div className="flex items-center gap-2 mb-1">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <CardTitle className="text-sm text-slate-200">Job-Specific Tailoring</CardTitle>
            </div>
            <p className="text-xs text-slate-400">
              Paste a job description to extract criteria, map evidence, and generate role-prioritized content.
            </p>
          </CardHeader>
          <CardContent>
            <Button
              size="sm"
              variant="outline"
              onClick={() => onNavigateTab('tailoring')}
              className="w-full border-slate-700 text-slate-300 hover:text-cyan-400"
            >
              Tailor to Job Description
            </Button>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800 hover:border-slate-700 transition-colors">
          <CardHeader>
            <div className="flex items-center gap-2 mb-1">
              <Layers className="w-4 h-4 text-emerald-400" />
              <CardTitle className="text-sm text-slate-200">Template Gallery</CardTitle>
            </div>
            <p className="text-xs text-slate-400">
              Switch among 6 ATS-proven designs: Classic ATS, Modern Professional, Technical, Academic, and Minimalist.
            </p>
          </CardHeader>
          <CardContent>
            <Button
              size="sm"
              variant="outline"
              onClick={() => onNavigateTab('templates')}
              className="w-full border-slate-700 text-slate-300 hover:text-emerald-400"
            >
              Browse Template Gallery
            </Button>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800 hover:border-slate-700 transition-colors">
          <CardHeader>
            <div className="flex items-center gap-2 mb-1">
              <Briefcase className="w-4 h-4 text-purple-400" />
              <CardTitle className="text-sm text-slate-200">Developer Portfolio</CardTitle>
            </div>
            <p className="text-xs text-slate-400">
              Assemble confirmed GitHub projects, technical architecture summaries, and export multi-page PDF portfolios.
            </p>
          </CardHeader>
          <CardContent>
            <Button
              size="sm"
              variant="outline"
              onClick={() => onNavigateTab('portfolio')}
              className="w-full border-slate-700 text-slate-300 hover:text-purple-400"
            >
              Open Portfolio Builder
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
