/**
 * Stage 23: Resume Builder Tab.
 * Step-by-step wizard for synthesizing evidence-grounded resumes from verified profile facts.
 */

import * as React from 'react';
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type { ResumeCreateRequest, ResumeDocument, ResumeType, PageFormat } from '@autonom/shared-types';

interface ResumeBuilderTabProps {
  onCreateResume: (req: ResumeCreateRequest) => Promise<ResumeDocument | null>;
  onNavigateTab: (tabId: string) => void;
}

export const ResumeBuilderTab: React.FC<ResumeBuilderTabProps> = ({
  onCreateResume,
  onNavigateTab,
}) => {
  const [title, setTitle] = React.useState<string>('Software Engineer Resume 2026');
  const [resumeType, setResumeType] = React.useState<ResumeType>('general');
  const [targetRole, setTargetRole] = React.useState<string>('Software Engineer');
  const [templateId, setTemplateId] = React.useState<string>('ats_classic');
  const [pageFormat, setPageFormat] = React.useState<PageFormat>('letter');
  const [maxPages, setMaxPages] = React.useState<number>(1);
  const [jobDescription, setJobDescription] = React.useState<string>('');
  const [isSubmitting, setIsSubmitting] = React.useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setIsSubmitting(true);
    try {
      const created = await onCreateResume({
        title: title.trim(),
        resume_type: resumeType,
        target_role: targetRole.trim() || undefined,
        template_id: templateId,
        page_format: pageFormat,
        max_pages: maxPages,
        job_description_text: jobDescription.trim() || undefined,
      });
      if (created) {
        onNavigateTab('editor');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const templates = [
    { id: 'ats_classic', name: 'Classic ATS', desc: 'Maximum ATS readability, single-column, standard serif typography.' },
    { id: 'modern_professional', name: 'Modern Professional', desc: 'Clean contemporary sans-serif layout with subtle dividing rules.' },
    { id: 'technical_engineer', name: 'Technical Engineer', desc: 'Prioritizes programming skills, system architecture, and projects.' },
    { id: 'internship_graduate', name: 'Internship / Graduate', desc: 'Emphasizes university education, coursework, and practical projects.' },
    { id: 'academic_research', name: 'Academic / Research', desc: 'Curriculum vitae layout for publications, research, and methods.' },
    { id: 'minimalist', name: 'Minimalist', desc: 'Ultra-compact single-column layout for condensed 1-page portfolios.' },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card className="bg-slate-900/60 border-slate-800">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-cyan-400" />
            <CardTitle className="text-base text-slate-200">Resume Builder Wizard</CardTitle>
          </div>
          <p className="text-xs text-slate-400">
            Synthesize an accurate, evidence-backed resume directly from verified profile claims and GitHub findings. Zero hallucination.
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 1. Identity & Objective */}
            <div className="space-y-4">
              <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400 border-b border-slate-800 pb-2">
                1. Document Identity & Objective
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs text-slate-300">Resume Title</label>
                  <Input
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="e.g. Master Resume or Backend Engineer 2026"
                    className="bg-slate-950 border-slate-700 text-slate-200 text-sm"
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs text-slate-300">Target Role</label>
                  <Input
                    value={targetRole}
                    onChange={(e) => setTargetRole(e.target.value)}
                    placeholder="e.g. Backend Developer, AI/ML Intern"
                    className="bg-slate-950 border-slate-700 text-slate-200 text-sm"
                  />
                </div>
              </div>

              {/* Archetype Selector */}
              <div className="space-y-2">
                <label className="text-xs text-slate-300">Resume Archetype</label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {[
                    { id: 'master', label: 'Master Resume' },
                    { id: 'general', label: 'General' },
                    { id: 'job_tailored', label: 'Job Tailored' },
                    { id: 'internship', label: 'Internship' },
                    { id: 'experienced', label: 'Experienced' },
                    { id: 'academic', label: 'Academic / CV' },
                    { id: 'minimalist', label: 'Minimalist' },
                  ].map((archetype) => (
                    <button
                      key={archetype.id}
                      type="button"
                      onClick={() => setResumeType(archetype.id as ResumeType)}
                      className={`px-3 py-2 text-xs rounded border text-left transition-all ${
                        resumeType === archetype.id
                          ? 'bg-cyan-950/60 border-cyan-500/80 text-cyan-300 font-semibold shadow-sm'
                          : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:border-slate-700'
                      }`}
                    >
                      {archetype.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* 2. Template Selection */}
            <div className="space-y-3">
              <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400 border-b border-slate-800 pb-2">
                2. Professional Template
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {templates.map((tpl) => (
                  <button
                    key={tpl.id}
                    type="button"
                    onClick={() => setTemplateId(tpl.id)}
                    className={`p-3 rounded-lg border text-left transition-all ${
                      templateId === tpl.id
                        ? 'bg-cyan-950/40 border-cyan-500 text-slate-100 ring-1 ring-cyan-500'
                        : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-xs text-slate-200">{tpl.name}</span>
                      <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                    </div>
                    <p className="text-[11px] text-slate-400 leading-snug">{tpl.desc}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* 3. Page Budget & Geometry */}
            <div className="space-y-3">
              <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400 border-b border-slate-800 pb-2">
                3. Page Budget & Format
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs text-slate-300">Page Standard</label>
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      size="sm"
                      variant={pageFormat === 'letter' ? 'primary' : 'outline'}
                      onClick={() => setPageFormat('letter')}
                      className={`flex-1 text-xs ${pageFormat === 'letter' ? 'bg-cyan-600 text-white' : 'border-slate-700 text-slate-400'}`}
                    >
                      US Letter (8.5 × 11")
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant={pageFormat === 'a4' ? 'primary' : 'outline'}
                      onClick={() => setPageFormat('a4')}
                      className={`flex-1 text-xs ${pageFormat === 'a4' ? 'bg-cyan-600 text-white' : 'border-slate-700 text-slate-400'}`}
                    >
                      ISO A4 (210 × 297mm)
                    </Button>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs text-slate-300">Target Page Length</label>
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      size="sm"
                      variant={maxPages === 1 ? 'primary' : 'outline'}
                      onClick={() => setMaxPages(1)}
                      className={`flex-1 text-xs ${maxPages === 1 ? 'bg-cyan-600 text-white' : 'border-slate-700 text-slate-400'}`}
                    >
                      1 Page (Standard)
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant={maxPages === 2 ? 'primary' : 'outline'}
                      onClick={() => setMaxPages(2)}
                      className={`flex-1 text-xs ${maxPages === 2 ? 'bg-cyan-600 text-white' : 'border-slate-700 text-slate-400'}`}
                    >
                      2 Pages (Senior)
                    </Button>
                  </div>
                </div>
              </div>
            </div>

            {/* 4. Optional Job Description */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs text-slate-300">Target Job Description (Optional)</label>
                <span className="text-[11px] text-slate-500">Enables automated requirement matching</span>
              </div>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the target job description or requirements here to automatically extract keywords and rank relevant verified skills..."
                rows={4}
                className="w-full bg-slate-950 border border-slate-700 rounded-md p-3 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>

            {/* Action Bar */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
              <Button
                type="button"
                variant="outline"
                onClick={() => onNavigateTab('overview')}
                className="border-slate-700 text-slate-400"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isSubmitting || !title.trim()}
                className="bg-cyan-600 hover:bg-cyan-500 text-white min-w-[140px]"
              >
                {isSubmitting ? (
                  'Synthesizing...'
                ) : (
                  <>
                    Build Resume
                    <ArrowRight className="w-4 h-4 ml-1.5" />
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

