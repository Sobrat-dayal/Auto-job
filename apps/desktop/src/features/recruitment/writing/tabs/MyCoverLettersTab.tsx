/**
 * Stage 24: My Cover Letters Tab.
 * Lists all historical and active cover letter documents with direct management actions.
 */

import * as React from 'react';
import {
  FileText,
  Search,
  Plus,
  Edit3,
  Trash2,
  Download,
  FileCheck2,
} from 'lucide-react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import type { CoverLetterDocument } from '@autonom/shared-types';

interface MyCoverLettersTabProps {
  coverLetters: CoverLetterDocument[];
  selectedLetterId: string | null;
  onSelectLetter: (letter: CoverLetterDocument) => void;
  onDeleteLetter: (id: string) => Promise<void>;
  onExportLetter: (id: string, format: 'pdf' | 'docx') => Promise<void>;
  onApproveLetter: (id: string) => Promise<void>;
  onNavigateTab: (tabId: string) => void;
}

export const MyCoverLettersTab: React.FC<MyCoverLettersTabProps> = ({
  coverLetters,
  selectedLetterId,
  onSelectLetter,
  onDeleteLetter,
  onExportLetter,
  onApproveLetter,
  onNavigateTab,
}) => {
  const [search, setSearch] = React.useState<string>('');
  const [typeFilter, setTypeFilter] = React.useState<string>('all');

  const filteredLetters = React.useMemo(() => {
    return coverLetters.filter((cl) => {
      const matchesSearch =
        cl.title.toLowerCase().includes(search.toLowerCase()) ||
        cl.target_role.toLowerCase().includes(search.toLowerCase()) ||
        (cl.employer_name || '').toLowerCase().includes(search.toLowerCase());
      const matchesType = typeFilter === 'all' || cl.letter_type === typeFilter;
      return matchesSearch && matchesType;
    });
  }, [coverLetters, search, typeFilter]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return <Badge variant="neutral" className="bg-emerald-950/60 text-emerald-400 border-emerald-800/60 text-[10px]">Approved</Badge>;
      case 'needs_review':
        return <Badge variant="neutral" className="bg-amber-950/60 text-amber-400 border-amber-800/60 text-[10px]">Needs Review</Badge>;
      case 'draft':
        return <Badge variant="neutral" className="bg-slate-800 text-slate-300 text-[10px]">Draft</Badge>;
      default:
        return <Badge variant="neutral" className="bg-slate-800 text-slate-400 text-[10px]">{status}</Badge>;
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
              placeholder="Search by title, role, or company..."
              className="h-8 pl-8 text-xs bg-slate-900 border-slate-700 text-slate-200"
            />
          </div>

          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="h-8 bg-slate-900 border border-slate-700 rounded px-2 text-xs text-slate-200"
          >
            <option value="all">All Archetypes</option>
            <option value="role_specific">Role-Specific</option>
            <option value="experienced">Experienced</option>
            <option value="internship">Internship</option>
            <option value="research">Research</option>
            <option value="short">Short</option>
            <option value="general">General</option>
          </select>
        </div>

        <Button
          size="sm"
          className="h-8 text-xs bg-cyan-600 hover:bg-cyan-500 text-white"
          onClick={() => onNavigateTab('studio')}
        >
          <Plus className="w-3.5 h-3.5 mr-1" />
          Create Cover Letter
        </Button>
      </div>

      {/* Grid of Letters */}
      {filteredLetters.length === 0 ? (
        <Card className="bg-slate-900/40 border-slate-800 text-center py-12">
          <CardContent className="space-y-3">
            <FileText className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-xs text-slate-400">
              {search || typeFilter !== 'all'
                ? 'No cover letters match the current search filter.'
                : 'No cover letters have been generated yet.'}
            </p>
            <Button
              variant="outline"
              size="sm"
              className="h-7 text-xs border-slate-700 text-slate-300"
              onClick={() => onNavigateTab('studio')}
            >
              Start in Studio
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredLetters.map((cl) => {
            const isSelected = selectedLetterId === cl.id;
            const totalWords = cl.blocks.reduce((acc, b) => acc + b.word_count, 0);

            return (
              <Card
                key={cl.id}
                className={`bg-slate-900/60 border transition-all ${
                  isSelected
                    ? 'border-cyan-500/80 ring-1 ring-cyan-500/20'
                    : 'border-slate-800 hover:border-slate-700'
                }`}
              >
                <CardHeader className="pb-2 space-y-1.5">
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-semibold text-xs text-slate-200 line-clamp-1">
                      {cl.title}
                    </span>
                    {getStatusBadge(cl.status)}
                  </div>
                  <p className="text-[11px] text-slate-400 flex items-center justify-between">
                    <span>
                      {cl.target_role} {cl.employer_name ? `• ${cl.employer_name}` : ''}
                    </span>
                    <span className="font-mono text-slate-500 text-[10px]">v{cl.current_version}</span>
                  </p>
                </CardHeader>

                <CardContent className="space-y-3 pt-1">
                  <div className="text-[11px] text-slate-400 line-clamp-2 italic bg-slate-950/40 p-2 rounded border border-slate-800/60">
                    "{cl.blocks.find((b) => b.block_type === 'opening')?.text || 'Dear Hiring Manager...'}"
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-slate-500 border-t border-slate-800/80 pt-2">
                    <span>{totalWords} words • {cl.blocks.length} paragraphs</span>
                    <span>{new Date(cl.updated_at).toLocaleDateString()}</span>
                  </div>

                  {/* Actions Toolbar */}
                  <div className="flex items-center justify-between pt-1 gap-1 border-t border-slate-800/60">
                    <div className="flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs text-cyan-400 hover:bg-cyan-950/40 px-2"
                        onClick={() => {
                          onSelectLetter(cl);
                          onNavigateTab('editor');
                        }}
                      >
                        <Edit3 className="w-3 h-3 mr-1" />
                        Edit
                      </Button>

                      {cl.status !== 'approved' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 text-xs text-emerald-400 hover:bg-emerald-950/40 px-2"
                          onClick={() => onApproveLetter(cl.id)}
                          title="Seal immutable approved version"
                        >
                          <FileCheck2 className="w-3 h-3 mr-1" />
                          Approve
                        </Button>
                      )}
                    </div>

                    <div className="flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 w-7 p-0 text-slate-400 hover:text-slate-200"
                        onClick={() => onExportLetter(cl.id, 'pdf')}
                        title="Export PDF"
                      >
                        <Download className="w-3 h-3 text-red-400" />
                      </Button>

                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 w-7 p-0 text-slate-400 hover:text-slate-200"
                        onClick={() => onExportLetter(cl.id, 'docx')}
                        title="Export Word (.docx)"
                      >
                        <Download className="w-3 h-3 text-blue-400" />
                      </Button>

                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 w-7 p-0 text-slate-400 hover:text-rose-400"
                        onClick={() => onDeleteLetter(cl.id)}
                        title="Delete Cover Letter"
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};
