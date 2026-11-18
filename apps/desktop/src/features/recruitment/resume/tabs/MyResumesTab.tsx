/**
 * Stage 23: My Resumes Tab.
 * Lists all active and historical resume documents with actionable controls.
 */

import * as React from 'react';
import {
  FileText,
  Copy,
  Trash2,
  Edit3,
  Eye,
  Sparkles,
  ShieldCheck,
  Plus,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { ResumeDocument } from '@autonom/shared-types';

interface MyResumesTabProps {
  resumes: ResumeDocument[];
  selectedResume: ResumeDocument | null;
  onSelectResume: (resume: ResumeDocument) => void;
  onDuplicateResume: (resumeId: string) => void;
  onDeleteResume: (resumeId: string) => void;
  onNavigateTab: (tabId: string) => void;
}

export const MyResumesTab: React.FC<MyResumesTabProps> = ({
  resumes,
  selectedResume,
  onSelectResume,
  onDuplicateResume,
  onDeleteResume,
  onNavigateTab,
}) => {
  const [filterType, setFilterType] = React.useState<string>('all');

  const filtered = React.useMemo(() => {
    if (filterType === 'all') return resumes;
    return resumes.filter((r) => r.resume_type === filterType);
  }, [resumes, filterType]);

  const getTypeBadgeVariant = (type: string) => {
    switch (type) {
      case 'master':
        return 'bg-cyan-950/60 text-cyan-400 border-cyan-800/60';
      case 'job_tailored':
        return 'bg-purple-950/60 text-purple-400 border-purple-800/60';
      case 'internship':
        return 'bg-emerald-950/60 text-emerald-400 border-emerald-800/60';
      case 'academic':
        return 'bg-amber-950/60 text-amber-400 border-amber-800/60';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return <Badge variant="neutral" className="bg-emerald-950/60 text-emerald-400 border-emerald-800/60">Approved</Badge>;
      case 'needs_review':
        return <Badge variant="neutral" className="bg-amber-950/60 text-amber-400 border-amber-800/60">Needs Review</Badge>;
      default:
        return <Badge variant="neutral" className="bg-slate-800 text-slate-400 border-slate-700">Draft</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant={filterType === 'all' ? 'primary' : 'outline'}
            onClick={() => setFilterType('all')}
            className={filterType === 'all' ? 'bg-cyan-600 text-white' : 'border-slate-700 text-slate-400'}
          >
            All ({resumes.length})
          </Button>
          <Button
            size="sm"
            variant={filterType === 'master' ? 'primary' : 'outline'}
            onClick={() => setFilterType('master')}
            className={filterType === 'master' ? 'bg-cyan-600 text-white' : 'border-slate-700 text-slate-400'}
          >
            Master
          </Button>
          <Button
            size="sm"
            variant={filterType === 'job_tailored' ? 'primary' : 'outline'}
            onClick={() => setFilterType('job_tailored')}
            className={filterType === 'job_tailored' ? 'bg-cyan-600 text-white' : 'border-slate-700 text-slate-400'}
          >
            Tailored
          </Button>
          <Button
            size="sm"
            variant={filterType === 'internship' ? 'primary' : 'outline'}
            onClick={() => setFilterType('internship')}
            className={filterType === 'internship' ? 'bg-cyan-600 text-white' : 'border-slate-700 text-slate-400'}
          >
            Internship
          </Button>
        </div>

        <Button
          size="sm"
          variant="primary"
          onClick={() => onNavigateTab('builder')}
          className="bg-cyan-600 hover:bg-cyan-500 text-white"
        >
          <Plus className="w-4 h-4 mr-1.5" />
          Create New Resume
        </Button>
      </div>

      {/* Resumes Grid */}
      {filtered.length === 0 ? (
        <Card className="bg-slate-900/60 border-slate-800 text-center py-12">
          <CardContent className="space-y-3">
            <FileText className="w-12 h-12 text-slate-600 mx-auto" />
            <h3 className="text-base font-semibold text-slate-300">No resumes found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Start by creating a Master Resume or generate an internship/job-tailored draft from your verified profile.
            </p>
            <Button
              size="sm"
              variant="primary"
              onClick={() => onNavigateTab('builder')}
              className="bg-cyan-600 hover:bg-cyan-500 text-white mt-2"
            >
              Launch Resume Builder
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((res) => {
            const isSelected = selectedResume?.id === res.id;
            return (
              <Card
                key={res.id}
                className={`bg-slate-900/60 border-slate-800 transition-all ${
                  isSelected ? 'ring-1 ring-cyan-500/60 border-cyan-800/80 shadow-md shadow-cyan-950/20' : 'hover:border-slate-700'
                }`}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <CardTitle className="text-base font-semibold text-slate-200">{res.title}</CardTitle>
                        <Badge variant="neutral" className={getTypeBadgeVariant(res.resume_type)}>
                          {res.resume_type.replace('_', ' ')}
                        </Badge>
                      </div>
                      <p className="text-xs text-slate-400">
                        Target Role: <span className="text-slate-300 font-medium">{res.target_role || 'General Software Engineering'}</span>
                      </p>
                    </div>
                    {getStatusBadge(res.status)}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-3 gap-2 text-xs bg-slate-950/60 p-2.5 rounded border border-slate-800/80 font-mono">
                    <div>
                      <span className="text-slate-500 block">Template</span>
                      <span className="text-slate-300">{res.template_id}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Version</span>
                      <span className="text-slate-300">v{res.current_version}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Format</span>
                      <span className="text-slate-300">{res.page_format.toUpperCase()}</span>
                    </div>
                  </div>

                  {/* Actions bar */}
                  <div className="flex items-center justify-between pt-2 border-t border-slate-800/80">
                    <div className="flex items-center gap-1.5">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          onSelectResume(res);
                          onNavigateTab('editor');
                        }}
                        className="h-8 px-2.5 text-xs border-slate-700 text-slate-300 hover:text-cyan-400"
                        title="Edit Content"
                      >
                        <Edit3 className="w-3.5 h-3.5 mr-1" />
                        Edit
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          onSelectResume(res);
                          onNavigateTab('tailoring');
                        }}
                        className="h-8 px-2.5 text-xs border-slate-700 text-slate-300 hover:text-purple-400"
                        title="Tailor to Job"
                      >
                        <Sparkles className="w-3.5 h-3.5 mr-1" />
                        Tailor
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          onSelectResume(res);
                          onNavigateTab('preview');
                        }}
                        className="h-8 px-2.5 text-xs border-slate-700 text-slate-300 hover:text-cyan-400"
                        title="Preview"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          onSelectResume(res);
                          onNavigateTab('ats');
                        }}
                        className="h-8 px-2.5 text-xs border-slate-700 text-slate-300 hover:text-emerald-400"
                        title="ATS Audit"
                      >
                        <ShieldCheck className="w-3.5 h-3.5" />
                      </Button>
                    </div>

                    <div className="flex items-center gap-1.5">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => onDuplicateResume(res.id)}
                        className="h-8 w-8 p-0 text-slate-400 hover:text-slate-200"
                        title="Duplicate"
                      >
                        <Copy className="w-3.5 h-3.5" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => onDeleteResume(res.id)}
                        className="h-8 w-8 p-0 text-rose-400/80 hover:text-rose-400 hover:bg-rose-950/30"
                        title="Delete"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
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

