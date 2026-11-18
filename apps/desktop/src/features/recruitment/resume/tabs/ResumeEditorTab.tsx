/**
 * Stage 23: Interactive Visual Resume Editor Tab.
 * Three-column workspace: Sections Ordering (Left), Editable Content (Center), Evidence & AI Assistance (Right).
 */

import * as React from 'react';
import {
  FileText,
  Save,
  Eye,
  CheckCircle2,
  AlertTriangle,
  ArrowUp,
  ArrowDown,
  ShieldCheck,
  Trash2,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import type { ResumeDocument, ResumeEntry } from '@autonom/shared-types';

interface ResumeEditorTabProps {
  resume: ResumeDocument | null;
  validationIssues: any[];
  onSaveResume: (updated: ResumeDocument) => Promise<void>;
  onNavigateTab: (tabId: string) => void;
}

export const ResumeEditorTab: React.FC<ResumeEditorTabProps> = ({
  resume,
  validationIssues,
  onSaveResume,
  onNavigateTab,
}) => {
  const [doc, setDoc] = React.useState<ResumeDocument | null>(resume);
  const [activeSectionId, setActiveSectionId] = React.useState<string | null>(null);
  const [selectedEntry, setSelectedEntry] = React.useState<ResumeEntry | null>(null);
  const [isSaving, setIsSaving] = React.useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = React.useState<boolean>(false);

  React.useEffect(() => {
    setDoc(resume);
    if (resume?.sections?.length) {
      setActiveSectionId(resume.sections[0].id);
      if (resume.sections[0].entries?.length) {
        setSelectedEntry(resume.sections[0].entries[0]);
      }
    }
  }, [resume]);

  if (!doc) {
    return (
      <Card className="bg-slate-900/60 border-slate-800 text-center py-16">
        <CardContent className="space-y-3">
          <FileText className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-semibold text-slate-300">No Resume Selected</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Select a resume from 'My Resumes' or create a new one using the Resume Builder wizard.
          </p>
          <Button
            size="sm"
            variant="primary"
            onClick={() => onNavigateTab('my_resumes')}
            className="bg-cyan-600 hover:bg-cyan-500 text-white mt-2"
          >
            Go to My Resumes
          </Button>
        </CardContent>
      </Card>
    );
  }

  const handleSave = async () => {
    if (!doc) return;
    setIsSaving(true);
    try {
      await onSaveResume(doc);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const handleMoveSection = (idx: number, direction: 'up' | 'down') => {
    if (!doc) return;
    const newIdx = direction === 'up' ? idx - 1 : idx + 1;
    if (newIdx < 0 || newIdx >= doc.sections.length) return;

    const sections = [...doc.sections];
    const [moved] = sections.splice(idx, 1);
    sections.splice(newIdx, 0, moved);
    sections.forEach((s, i) => (s.ordering = i));
    setDoc({ ...doc, sections });
  };

  const handleToggleSectionVisibility = (secId: string) => {
    if (!doc) return;
    const sections = doc.sections.map((s) => (s.id === secId ? { ...s, is_visible: !s.is_visible } : s));
    setDoc({ ...doc, sections });
  };

  const activeSection = doc.sections.find((s) => s.id === activeSectionId);

  return (
    <div className="space-y-4">
      {/* Top Action Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-3 bg-slate-900/80 border border-slate-800 rounded-lg">
        <div className="flex items-center gap-3">
          <Input
            value={doc.title}
            onChange={(e) => setDoc({ ...doc, title: e.target.value })}
            className="h-8 max-w-xs bg-slate-950 border-slate-700 text-slate-200 text-sm font-semibold"
          />
          <Badge variant="neutral" className="bg-slate-800 text-slate-300 font-mono text-xs">
            v{doc.current_version} ({doc.status})
          </Badge>
          <Badge variant="neutral" className="bg-cyan-950/60 text-cyan-400 border-cyan-800/60 text-xs">
            {doc.template_id}
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          {saveSuccess && (
            <span className="flex items-center gap-1 text-xs text-emerald-400 font-medium animate-pulse">
              <CheckCircle2 className="w-3.5 h-3.5" /> Saved
            </span>
          )}
          <Button
            size="sm"
            variant="outline"
            onClick={() => onNavigateTab('preview')}
            className="border-slate-700 text-slate-300 hover:text-cyan-400"
          >
            <Eye className="w-4 h-4 mr-1.5" />
            Preview
          </Button>
          <Button
            size="sm"
            variant="primary"
            disabled={isSaving}
            onClick={handleSave}
            className="bg-cyan-600 hover:bg-cyan-500 text-white"
          >
            <Save className="w-4 h-4 mr-1.5" />
            {isSaving ? 'Saving...' : 'Save Draft'}
          </Button>
        </div>
      </div>

      {/* 3-Column Visual Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left Column: Sections & Ordering (3 Cols) */}
        <div className="lg:col-span-3 space-y-3">
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center justify-between">
                <span>Resume Sections</span>
                <span className="text-slate-500 font-normal">{doc.sections.length}</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-2 space-y-1">
              {doc.sections.map((sec, idx) => {
                const isActive = sec.id === activeSectionId;
                return (
                  <div
                    key={sec.id}
                    onClick={() => setActiveSectionId(sec.id)}
                    className={`flex items-center justify-between p-2 rounded cursor-pointer text-xs transition-colors ${
                      isActive
                        ? 'bg-cyan-950/60 border border-cyan-500/50 text-cyan-300 font-medium'
                        : 'bg-slate-950/40 border border-slate-800/80 text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                    }`}
                  >
                    <span className="truncate max-w-[120px]">{sec.display_title}</span>
                    <div className="flex items-center gap-1">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleMoveSection(idx, 'up');
                        }}
                        disabled={idx === 0}
                        className="p-1 hover:text-cyan-400 disabled:opacity-20"
                        title="Move Up"
                      >
                        <ArrowUp className="w-3 h-3" />
                      </button>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleMoveSection(idx, 'down');
                        }}
                        disabled={idx === doc.sections.length - 1}
                        className="p-1 hover:text-cyan-400 disabled:opacity-20"
                        title="Move Down"
                      >
                        <ArrowDown className="w-3 h-3" />
                      </button>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleToggleSectionVisibility(sec.id);
                        }}
                        className={`text-[10px] px-1 rounded ${sec.is_visible ? 'text-emerald-400' : 'text-slate-600'}`}
                      >
                        {sec.is_visible ? 'ON' : 'OFF'}
                      </button>
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </div>

        {/* Center Column: Editable Content (6 Cols) */}
        <div className="lg:col-span-6 space-y-4">
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-3 border-b border-slate-800/80">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm text-slate-200">
                  {activeSection ? activeSection.display_title : 'Select Section'}
                </CardTitle>
                <Badge variant="neutral" className="bg-slate-800 text-slate-400 text-xs">
                  {activeSection?.entries?.length ?? 0} entries
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="p-4 space-y-4">
              {activeSection && activeSection.entries.length === 0 && (
                <div className="text-center py-8 text-xs text-slate-500">
                  No entries present in this section. Add one from the profile.
                </div>
              )}

              {activeSection?.entries.map((entry, eIdx) => {
                const isEntrySelected = selectedEntry?.id === entry.id;
                return (
                  <div
                    key={entry.id}
                    onClick={() => setSelectedEntry(entry)}
                    className={`p-3 rounded-lg border text-xs space-y-3 cursor-pointer transition-all ${
                      isEntrySelected
                        ? 'bg-slate-950/80 border-cyan-500/60 ring-1 ring-cyan-500/20'
                        : 'bg-slate-950/40 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="grid grid-cols-2 gap-2">
                      <div className="space-y-1">
                        <label className="text-[11px] text-slate-500">Title</label>
                        <Input
                          value={entry.title}
                          onChange={(e) => {
                            const newSections = [...doc.sections];
                            const s = newSections.find((x) => x.id === activeSection.id);
                            if (s) {
                              s.entries[eIdx].title = e.target.value;
                              setDoc({ ...doc, sections: newSections });
                            }
                          }}
                          className="h-7 text-xs bg-slate-900 border-slate-700 text-slate-200"
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="text-[11px] text-slate-500">Organization / Subtitle</label>
                        <Input
                          value={entry.subtitle || entry.organization || ''}
                          onChange={(e) => {
                            const newSections = [...doc.sections];
                            const s = newSections.find((x) => x.id === activeSection.id);
                            if (s) {
                              s.entries[eIdx].subtitle = e.target.value;
                              setDoc({ ...doc, sections: newSections });
                            }
                          }}
                          className="h-7 text-xs bg-slate-900 border-slate-700 text-slate-200"
                        />
                      </div>
                    </div>

                    {/* Description or Bullets */}
                    {entry.bullet_points.length > 0 ? (
                      <div className="space-y-2">
                        <label className="text-[11px] text-slate-500">Achievement Bullets</label>
                        {entry.bullet_points.map((b, bIdx) => (
                          <div key={bIdx} className="flex gap-2">
                            <textarea
                              value={b}
                              onChange={(e) => {
                                const newSections = [...doc.sections];
                                const s = newSections.find((x) => x.id === activeSection.id);
                                if (s) {
                                  s.entries[eIdx].bullet_points[bIdx] = e.target.value;
                                  setDoc({ ...doc, sections: newSections });
                                }
                              }}
                              rows={2}
                              className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                            />
                            <button
                              type="button"
                              onClick={() => {
                                const newSections = [...doc.sections];
                                const s = newSections.find((x) => x.id === activeSection.id);
                                if (s) {
                                  s.entries[eIdx].bullet_points.splice(bIdx, 1);
                                  setDoc({ ...doc, sections: newSections });
                                }
                              }}
                              className="text-slate-500 hover:text-rose-400 p-1"
                              title="Delete Bullet"
                            >
                              <Trash2 className="w-3 h-3" />
                            </button>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="space-y-1">
                        <label className="text-[11px] text-slate-500">Description</label>
                        <textarea
                          value={entry.description || ''}
                          onChange={(e) => {
                            const newSections = [...doc.sections];
                            const s = newSections.find((x) => x.id === activeSection.id);
                            if (s) {
                              s.entries[eIdx].description = e.target.value;
                              setDoc({ ...doc, sections: newSections });
                            }
                          }}
                          rows={3}
                          className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                        />
                      </div>
                    )}
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Source Evidence & Quality Validation (3 Cols) */}
        <div className="lg:col-span-3 space-y-4">
          {/* Source Evidence Card */}
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-2">
              <div className="flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-cyan-400" />
                <CardTitle className="text-xs font-mono uppercase tracking-wider text-slate-400">
                  Source Provenance
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-2 text-xs">
              {selectedEntry?.source_refs?.length ? (
                selectedEntry.source_refs.map((ref, idx) => (
                  <div key={idx} className="p-2 rounded bg-slate-950/60 border border-slate-800/80 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500 text-[10px]">Entity ID</span>
                      <span className="font-mono text-cyan-400 text-[10px]">{ref.source_entity_id}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500 text-[10px]">Verification</span>
                      <Badge variant="neutral" className="bg-emerald-950/40 text-emerald-400 text-[10px] py-0">
                        {ref.verification_status}
                      </Badge>
                    </div>
                    {ref.source_excerpt && (
                      <p className="text-[11px] text-slate-300 italic pt-1 border-t border-slate-800/50">
                        "{ref.source_excerpt}"
                      </p>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-slate-500 text-center py-4">
                  Select an entry to view underlying Stage 21 profile claims and GitHub evidence links.
                </div>
              )}
            </CardContent>
          </Card>

          {/* Validation Status Card */}
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-2">
              <div className="flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <CardTitle className="text-xs font-mono uppercase tracking-wider text-slate-400">
                  Factual Audit
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-2 text-xs">
              {validationIssues.length === 0 ? (
                <div className="flex items-center gap-2 text-emerald-400 py-2">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>All claims pass factual consistency checks.</span>
                </div>
              ) : (
                validationIssues.map((iss, idx) => (
                  <div key={idx} className="p-2 rounded bg-amber-950/30 border border-amber-800/60 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-amber-300 text-[11px]">{iss.code}</span>
                      <Badge variant="neutral" className="bg-amber-950/60 text-amber-400 text-[9px]">
                        {iss.severity}
                      </Badge>
                    </div>
                    <p className="text-[11px] text-slate-300">{iss.message}</p>
                    <span className="text-[10px] text-slate-500 block">{iss.location}</span>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

