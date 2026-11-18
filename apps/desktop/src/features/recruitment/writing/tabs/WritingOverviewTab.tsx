/**
 * Stage 24: Recruitment Writing Overview Tab.
 * Displays high-level analytics, active application materials, freshness alerts,
 * and quick workflow launchers.
 */

import * as React from 'react';
import {
  FileText,
  FileCheck2,
  HelpCircle,
  BookOpen,
  AlertTriangle,
  ShieldAlert,
  Archive,
  ArrowRight,
  Plus,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type {
  WritingOverviewStats,
  CoverLetterDocument,
  ApplicationWritingPackage,
} from '@autonom/shared-types';

interface WritingOverviewTabProps {
  stats: WritingOverviewStats | null;
  coverLetters: CoverLetterDocument[];
  packages: ApplicationWritingPackage[];
  onNavigateTab: (tabId: string) => void;
  onRefreshStats: () => Promise<void>;
  onCheckFreshness: () => Promise<void>;
}

export const WritingOverviewTab: React.FC<WritingOverviewTabProps> = ({
  stats,
  coverLetters,
  packages,
  onNavigateTab,
  onRefreshStats,
  onCheckFreshness,
}) => {
  const [isRefreshing, setIsRefreshing] = React.useState<boolean>(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await onRefreshStats();
    } finally {
      setIsRefreshing(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return <Badge variant="neutral" className="bg-emerald-950/60 text-emerald-400 border-emerald-800/60 text-[10px]">Approved</Badge>;
      case 'needs_review':
        return <Badge variant="neutral" className="bg-amber-950/60 text-amber-400 border-amber-800/60 text-[10px]">Needs Review</Badge>;
      case 'draft':
        return <Badge variant="neutral" className="bg-slate-800 text-slate-300 border-slate-700 text-[10px]">Draft</Badge>;
      case 'generating':
        return <Badge variant="neutral" className="bg-cyan-950/60 text-cyan-400 border-cyan-800/60 text-[10px]">Generating</Badge>;
      default:
        return <Badge variant="neutral" className="bg-slate-800 text-slate-400 text-[10px]">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner / Metrics Overview */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        <Card className="bg-slate-900/60 border-slate-800 p-3">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Cover Letters</span>
            <FileText className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <div className="mt-2 text-xl font-bold text-slate-100">
            {stats?.total_cover_letters ?? coverLetters.length}
          </div>
          <p className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
            <FileCheck2 className="w-3 h-3" />
            {stats?.approved_cover_letters ?? 0} approved
          </p>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800 p-3">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Screening Q&A</span>
            <HelpCircle className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <div className="mt-2 text-xl font-bold text-slate-100">
            {stats?.total_screening_questions ?? 0}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Across {stats?.total_question_sets ?? 0} question sets
          </p>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800 p-3">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Answer Library</span>
            <BookOpen className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="mt-2 text-xl font-bold text-slate-100">
            {stats?.approved_library_answers ?? 0}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Reusable parameterized items
          </p>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800 p-3">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Sensitive Decisions</span>
            <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div className="mt-2 text-xl font-bold text-amber-300">
            {stats?.sensitive_decisions_count ?? 0}
          </div>
          <p className="text-[11px] text-amber-400/80 mt-1">
            Requires direct human election
          </p>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800 p-3">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Writing Packages</span>
            <Archive className="w-3.5 h-3.5 text-purple-400" />
          </div>
          <div className="mt-2 text-xl font-bold text-slate-100">
            {stats?.writing_packages_count ?? packages.length}
          </div>
          <p className="text-[11px] text-purple-400/80 mt-1">
            Assembled submissions
          </p>
        </Card>
      </div>

      {/* Freshness & Missing Data Alerts */}
      {stats && (stats.missing_info_count > 0 || stats.sensitive_decisions_count > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {stats.sensitive_decisions_count > 0 && (
            <div className="p-3.5 rounded-lg border border-amber-500/30 bg-amber-950/20 flex items-start gap-3">
              <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <h4 className="text-xs font-semibold text-amber-200">
                  {stats.sensitive_decisions_count} Sensitive Question(s) Pending Review
                </h4>
                <p className="text-[11px] text-slate-300">
                  Work authorization, visa sponsorship, or compensation disclosures cannot be auto-filled by AI.
                </p>
                <button
                  type="button"
                  onClick={() => onNavigateTab('sensitive')}
                  className="text-xs text-amber-400 hover:text-amber-300 font-medium inline-flex items-center gap-1 pt-1"
                >
                  Review Sensitive Decisions <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          )}

          {stats.missing_info_count > 0 && (
            <div className="p-3.5 rounded-lg border border-cyan-500/30 bg-cyan-950/20 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <h4 className="text-xs font-semibold text-cyan-200">
                  {stats.missing_info_count} Profile Fact(s) Required for Completeness
                </h4>
                <p className="text-[11px] text-slate-300">
                  Some questions reference experience or metrics missing from your canonical applicant profile.
                </p>
                <button
                  type="button"
                  onClick={() => onNavigateTab('missing-conflicts')}
                  className="text-xs text-cyan-400 hover:text-cyan-300 font-medium inline-flex items-center gap-1 pt-1"
                >
                  View Missing Details <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Main Workspace Actions & Recents */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Quick Workflow Actions (4 Cols) */}
        <div className="lg:col-span-4 space-y-4">
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm text-slate-200 flex items-center justify-between">
                <span>Quick Actions</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleRefresh}
                  disabled={isRefreshing}
                  className="h-7 w-7 p-0 text-slate-400 hover:text-slate-200"
                  title="Refresh stats"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button
                variant="outline"
                className="w-full justify-between text-xs bg-slate-950/40 border-slate-800 hover:bg-slate-800/60 hover:text-cyan-300 h-9"
                onClick={() => onNavigateTab('studio')}
              >
                <span className="flex items-center gap-2">
                  <Plus className="w-3.5 h-3.5 text-cyan-400" />
                  Generate New Cover Letter
                </span>
                <ArrowRight className="w-3 h-3 text-slate-500" />
              </Button>

              <Button
                variant="outline"
                className="w-full justify-between text-xs bg-slate-950/40 border-slate-800 hover:bg-slate-800/60 hover:text-indigo-300 h-9"
                onClick={() => onNavigateTab('screening')}
              >
                <span className="flex items-center gap-2">
                  <HelpCircle className="w-3.5 h-3.5 text-indigo-400" />
                  Parse Screening Questions
                </span>
                <ArrowRight className="w-3 h-3 text-slate-500" />
              </Button>

              <Button
                variant="outline"
                className="w-full justify-between text-xs bg-slate-950/40 border-slate-800 hover:bg-slate-800/60 hover:text-emerald-300 h-9"
                onClick={() => onNavigateTab('library')}
              >
                <span className="flex items-center gap-2">
                  <BookOpen className="w-3.5 h-3.5 text-emerald-400" />
                  Reusable Answer Library
                </span>
                <ArrowRight className="w-3 h-3 text-slate-500" />
              </Button>

              <Button
                variant="outline"
                className="w-full justify-between text-xs bg-slate-950/40 border-slate-800 hover:bg-slate-800/60 hover:text-purple-300 h-9"
                onClick={() => onNavigateTab('packages')}
              >
                <span className="flex items-center gap-2">
                  <Archive className="w-3.5 h-3.5 text-purple-400" />
                  Application Packages
                </span>
                <ArrowRight className="w-3 h-3 text-slate-500" />
              </Button>

              <div className="pt-2 border-t border-slate-800/80">
                <Button
                  variant="ghost"
                  className="w-full justify-center text-xs text-slate-400 hover:text-slate-200 h-8"
                  onClick={onCheckFreshness}
                >
                  <Sparkles className="w-3 h-3 mr-1 text-cyan-400" />
                  Check Library Freshness
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Zero Hallucination Guarantee Badge */}
          <div className="p-3.5 rounded-lg border border-slate-800 bg-slate-950/50 space-y-1.5">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-200">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              Factual Grounding Guarantee
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Every sentence generated links to an authoritative profile claim or verified code artifact. No fictional years of experience, degrees, or certifications are ever fabricated.
            </p>
          </div>
        </div>

        {/* Right Column: Recent Cover Letters & Active Packages (8 Cols) */}
        <div className="lg:col-span-8 space-y-4">
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-sm text-slate-200">Recent Cover Letters</CardTitle>
                <p className="text-xs text-slate-400">
                  Targeted, tailored professional correspondence.
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="text-xs text-cyan-400 hover:text-cyan-300 h-7"
                onClick={() => onNavigateTab('my-letters')}
              >
                View All ({coverLetters.length})
              </Button>
            </CardHeader>
            <CardContent>
              {coverLetters.length === 0 ? (
                <div className="text-center py-8 text-xs text-slate-500">
                  No cover letters generated yet. Click "Generate New Cover Letter" to start.
                </div>
              ) : (
                <div className="divide-y divide-slate-800/60">
                  {coverLetters.slice(0, 5).map((cl) => (
                    <div
                      key={cl.id}
                      className="py-2.5 flex items-center justify-between hover:bg-slate-800/30 px-2 rounded cursor-pointer transition-colors"
                      onClick={() => onNavigateTab('editor')}
                    >
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-xs text-slate-200">{cl.title}</span>
                          {getStatusBadge(cl.status)}
                          <span className="text-[10px] text-slate-500 font-mono">v{cl.current_version}</span>
                        </div>
                        <p className="text-[11px] text-slate-400">
                          {cl.target_role} {cl.employer_name ? `at ${cl.employer_name}` : ''} • {cl.blocks.length} paragraphs
                        </p>
                      </div>
                      <span className="text-[11px] text-slate-500">
                        {new Date(cl.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Active Packages Card */}
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-sm text-slate-200">Active Application Packages</CardTitle>
                <p className="text-xs text-slate-400">
                  Complete submission bundles binding resume, cover letter, and screening answers.
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="text-xs text-purple-400 hover:text-purple-300 h-7"
                onClick={() => onNavigateTab('packages')}
              >
                View Packages ({packages.length})
              </Button>
            </CardHeader>
            <CardContent>
              {packages.length === 0 ? (
                <div className="text-center py-6 text-xs text-slate-500">
                  No application packages assembled yet. Bind your resume and answers in the Packages tab.
                </div>
              ) : (
                <div className="divide-y divide-slate-800/60">
                  {packages.slice(0, 3).map((pkg) => (
                    <div
                      key={pkg.id}
                      className="py-2.5 flex items-center justify-between hover:bg-slate-800/30 px-2 rounded cursor-pointer transition-colors"
                      onClick={() => onNavigateTab('packages')}
                    >
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-xs text-slate-200">
                            {pkg.target_job_title} at {pkg.target_employer}
                          </span>
                          <Badge variant="neutral" className="bg-purple-950/60 text-purple-300 border-purple-800/60 text-[10px]">
                            {pkg.status}
                          </Badge>
                        </div>
                        <p className="text-[11px] text-slate-400">
                          {pkg.answered_questions} of {pkg.total_questions} answered • {pkg.pending_sensitive_decisions} sensitive pending
                        </p>
                      </div>
                      <span className="text-[11px] text-slate-500 font-mono">
                        {pkg.is_ready_for_approval ? 'Ready' : 'Incomplete'}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
