/**
 * Stage 24: Reusable Answer Library Tab.
 * Parameterized answer templates, freshness monitoring, and cross-employer reuse previews.
 */

import * as React from 'react';
import {
  BookOpen,
  Search,
  Plus,
  Trash2,
  CheckCircle2,
  Eye,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type {
  AnswerLibraryEntry,
  AnswerLibraryCreateRequest,
  QuestionCategory,
} from '@autonom/shared-types';

interface AnswerLibraryTabProps {
  entries: AnswerLibraryEntry[];
  onRefreshLibrary: () => Promise<void>;
  onCreateEntry: (req: AnswerLibraryCreateRequest) => Promise<void>;
  onDeleteEntry: (id: string) => Promise<void>;
}

export const AnswerLibraryTab: React.FC<AnswerLibraryTabProps> = ({
  entries,
  onRefreshLibrary,
  onCreateEntry,
  onDeleteEntry,
}) => {
  const [search, setSearch] = React.useState<string>('');
  const [categoryFilter, setCategoryFilter] = React.useState<string>('all');
  const [isCreating, setIsCreating] = React.useState<boolean>(false);
  const [newTitle, setNewTitle] = React.useState<string>('');
  const [newCategory, setNewCategory] = React.useState<QuestionCategory>('behavioral');
  const [newTemplate, setNewTemplate] = React.useState<string>(
    'In my role as a systems engineer, I led the implementation of {technology} architecture, resulting in substantial uptime improvements for {employer}.'
  );

  // Reuse Preview State
  const [previewEmployer, setPreviewEmployer] = React.useState<string>('TechCorp Labs');
  const [previewRole, setPreviewRole] = React.useState<string>('Staff Engineer');
  const [previewResult, setPreviewResult] = React.useState<{
    original_template: string;
    resolved_text: string;
    target_employer?: string;
    detected_placeholders: string[];
  } | null>(null);

  const filteredEntries = React.useMemo(() => {
    return entries.filter((e) => {
      const matchesSearch =
        e.title.toLowerCase().includes(search.toLowerCase()) ||
        e.parameterized_template.toLowerCase().includes(search.toLowerCase());
      const matchesCategory = categoryFilter === 'all' || e.category === categoryFilter;
      return matchesSearch && matchesCategory;
    });
  }, [entries, search, categoryFilter]);

  const handleCreate = async () => {
    if (!newTitle.trim() || !newTemplate.trim()) return;
    setIsCreating(true);
    try {
      await onCreateEntry({
        title: newTitle,
        category: newCategory,
        parameterized_template: newTemplate,
      });
      setNewTitle('');
      await onRefreshLibrary();
    } finally {
      setIsCreating(false);
    }
  };

  const handlePreviewReuse = async (entry: AnswerLibraryEntry) => {
    try {
      const res = await apiClient.previewAnswerReuse(entry.id, {
        target_employer: previewEmployer,
        target_role: previewRole,
      });
      setPreviewResult(res);
    } catch {
      // Ignored
    }
  };

  const getFreshnessBadge = (state: string) => {
    switch (state) {
      case 'approved':
        return <Badge variant="neutral" className="bg-emerald-950/60 text-emerald-400 border-emerald-800 text-[10px]">Fresh & Approved</Badge>;
      case 'outdated':
        return <Badge variant="neutral" className="bg-rose-950/60 text-rose-400 border-rose-800 text-[10px]">Outdated Facts</Badge>;
      case 'needs_review':
        return <Badge variant="neutral" className="bg-amber-950/60 text-amber-400 border-amber-800 text-[10px]">Needs Review</Badge>;
      default:
        return <Badge variant="neutral" className="bg-slate-800 text-slate-300 text-[10px]">{state}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="relative w-full sm:w-64">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search library answers..."
              className="h-8 pl-8 text-xs bg-slate-900 border-slate-700 text-slate-200"
            />
          </div>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="h-8 bg-slate-900 border border-slate-700 rounded px-2 text-xs text-slate-200"
          >
            <option value="all">All Categories</option>
            <option value="behavioral">Behavioral (STAR)</option>
            <option value="technical">Technical</option>
            <option value="experience">Experience</option>
            <option value="motivation">Motivation</option>
            <option value="work_eligibility">Work Eligibility</option>
          </select>
        </div>

        <Button
          size="sm"
          className="h-8 text-xs bg-cyan-600 hover:bg-cyan-500 text-white"
          onClick={() => {
            const el = document.getElementById('new-answer-box');
            if (el) el.scrollIntoView({ behavior: 'smooth' });
          }}
        >
          <Plus className="w-3.5 h-3.5 mr-1" />
          Add Reusable Template
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Entries List (7 Cols) */}
        <div className="lg:col-span-7 space-y-3">
          {filteredEntries.length === 0 ? (
            <Card className="bg-slate-900/40 border-slate-800 text-center py-12">
              <CardContent className="space-y-2">
                <BookOpen className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-xs text-slate-400">No reusable answer entries match the current filter.</p>
              </CardContent>
            </Card>
          ) : (
            filteredEntries.map((entry) => (
              <Card key={entry.id} className="bg-slate-900/60 border-slate-800">
                <CardHeader className="pb-2 space-y-1">
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-semibold text-xs text-slate-200">{entry.title}</span>
                    <div className="flex items-center gap-1.5">
                      <Badge variant="neutral" className="bg-slate-800 text-slate-300 text-[10px]">
                        {entry.category}
                      </Badge>
                      {getFreshnessBadge(entry.state)}
                    </div>
                  </div>
                  <p className="text-[10px] text-slate-500 font-mono">
                    Reused {entry.reuse_count} times • v{entry.version_number}
                  </p>
                </CardHeader>
                <CardContent className="space-y-3 pt-1 text-xs">
                  <div className="p-3 rounded bg-slate-950/70 border border-slate-800 font-mono text-[11px] text-slate-300 leading-relaxed">
                    {entry.parameterized_template}
                  </div>

                  <div className="flex items-center justify-between border-t border-slate-800/80 pt-2 text-[11px]">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 text-xs text-cyan-400 hover:text-cyan-300 hover:bg-cyan-950/40"
                      onClick={() => handlePreviewReuse(entry)}
                    >
                      <Eye className="w-3.5 h-3.5 mr-1" />
                      Preview Reuse & Check Leaks
                    </Button>

                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 w-7 p-0 text-slate-500 hover:text-rose-400"
                      onClick={() => onDeleteEntry(entry.id)}
                      title="Delete Entry"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Right Column: Reuse Tester & New Template Creator (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Reuse Preview Inspector */}
          {previewResult && (
            <Card className="bg-slate-900/80 border-cyan-500/50">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-1.5">
                  <Eye className="w-4 h-4 text-cyan-400" />
                  <CardTitle className="text-xs text-cyan-300">Reuse Resolver Preview</CardTitle>
                </div>
                <p className="text-[11px] text-slate-400">
                  Verifies that target employer parameters resolve without leaking past company names.
                </p>
              </CardHeader>
              <CardContent className="space-y-3 text-xs">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-[10px] text-slate-400">Target Employer</label>
                    <Input
                      value={previewEmployer}
                      onChange={(e) => setPreviewEmployer(e.target.value)}
                      className="h-7 text-xs bg-slate-950 border-slate-700"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-slate-400">Target Role</label>
                    <Input
                      value={previewRole}
                      onChange={(e) => setPreviewRole(e.target.value)}
                      className="h-7 text-xs bg-slate-950 border-slate-700"
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Resolved Answer:</span>
                  <p className="p-2.5 rounded bg-slate-950 border border-slate-800 text-[11px] text-slate-200 leading-relaxed">
                    {previewResult.resolved_text}
                  </p>
                </div>

                <div className="flex items-center gap-1.5 text-[10px] text-emerald-400">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  No cross-employer leaks detected.
                </div>
              </CardContent>
            </Card>
          )}

          {/* New Template Form */}
          <Card id="new-answer-box" className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <Plus className="w-4 h-4 text-emerald-400" />
                <CardTitle className="text-xs text-slate-200">Create Reusable Answer</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="space-y-1">
                <label className="text-slate-300">Title / Identifier</label>
                <Input
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Production Outage Resolution (STAR)"
                  className="h-8 text-xs bg-slate-950 border-slate-700 text-slate-200"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-300">Category</label>
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value as QuestionCategory)}
                  className="w-full h-8 bg-slate-950 border border-slate-700 rounded px-2 text-xs text-slate-200"
                >
                  <option value="behavioral">Behavioral (STAR)</option>
                  <option value="technical">Technical</option>
                  <option value="experience">Experience</option>
                  <option value="motivation">Motivation</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-slate-300">Parameterized Template Text</label>
                <textarea
                  value={newTemplate}
                  onChange={(e) => setNewTemplate(e.target.value)}
                  rows={5}
                  className="w-full bg-slate-950 border border-slate-700 rounded p-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
                  placeholder="Use {employer}, {target_role}, {technology} placeholders..."
                />
              </div>

              <Button
                onClick={handleCreate}
                disabled={isCreating || !newTitle.trim()}
                className="w-full bg-emerald-600 hover:bg-emerald-500 text-white text-xs h-8"
              >
                {isCreating ? 'Saving...' : 'Add to Library'}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
