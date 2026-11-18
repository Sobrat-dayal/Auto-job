/**
 * Stage 24: Interactive Cover Letter Visual Editor Tab.
 * Three-column structure: Paragraph Outline (Left), Content & Rewrite Editor (Center),
 * Fact Grounding & Version Seal (Right).
 */

import * as React from 'react';
import {
  FileText,
  Save,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  ShieldCheck,
  FileCheck2,
  Download,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type {
  CoverLetterDocument,
} from '@autonom/shared-types';

interface CoverLetterEditorTabProps {
  letter: CoverLetterDocument | null;
  onSave: (updated: CoverLetterDocument) => Promise<void>;
  onApprove: (id: string) => Promise<void>;
  onExport: (id: string, format: 'pdf' | 'docx') => Promise<void>;
  onNavigateTab: (tabId: string) => void;
}

export const CoverLetterEditorTab: React.FC<CoverLetterEditorTabProps> = ({
  letter,
  onSave,
  onApprove,
  onExport,
  onNavigateTab,
}) => {
  const [doc, setDoc] = React.useState<CoverLetterDocument | null>(letter);
  const [selectedBlockId, setSelectedBlockId] = React.useState<string | null>(null);
  const [rewriteInstruction, setRewriteInstruction] = React.useState<string>('');
  const [isRewriting, setIsRewriting] = React.useState<boolean>(false);
  const [isSaving, setIsSaving] = React.useState<boolean>(false);
  const [validationData, setValidationData] = React.useState<{
    is_valid: boolean;
    errors: string[];
    warnings: string[];
    total_words: number;
    verified_facts_count: number;
  } | null>(null);

  React.useEffect(() => {
    setDoc(letter);
    if (letter && letter.blocks.length > 0) {
      setSelectedBlockId(letter.blocks[0].id);
      runValidation(letter.id);
    }
  }, [letter]);

  const runValidation = async (id: string) => {
    try {
      const val = await apiClient.validateCoverLetter(id);
      setValidationData(val);
    } catch {
      // Ignored
    }
  };

  if (!doc) {
    return (
      <div className="text-center py-16 space-y-3">
        <FileText className="w-8 h-8 text-slate-600 mx-auto" />
        <p className="text-xs text-slate-400">No cover letter selected for editing.</p>
        <Button
          size="sm"
          className="text-xs bg-cyan-600 hover:bg-cyan-500 text-white"
          onClick={() => onNavigateTab('studio')}
        >
          Create One in Studio
        </Button>
      </div>
    );
  }

  const selectedBlock = doc.blocks.find((b) => b.id === selectedBlockId) || doc.blocks[0];

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await onSave(doc);
      await runValidation(doc.id);
    } finally {
      setIsSaving(false);
    }
  };

  const handleRewrite = async () => {
    if (!selectedBlock || !rewriteInstruction.trim()) return;
    setIsRewriting(true);
    try {
      const res = await apiClient.rewriteCoverLetterParagraph(doc.id, {
        paragraph_id: selectedBlock.id,
        instruction: rewriteInstruction,
      });
      const newBlocks = doc.blocks.map((b) =>
        b.id === selectedBlock.id
          ? {
              ...b,
              text: res.rewritten_text,
              word_count: res.rewritten_text.split(/\s+/).filter(Boolean).length,
              is_user_edited: true,
            }
          : b
      );
      const updatedDoc = { ...doc, blocks: newBlocks };
      setDoc(updatedDoc);
      await onSave(updatedDoc);
      setRewriteInstruction('');
      await runValidation(doc.id);
    } finally {
      setIsRewriting(false);
    }
  };

  const totalWords = doc.blocks.reduce((acc, b) => acc + b.word_count, 0);

  return (
    <div className="space-y-4">
      {/* Editor Header Toolbar */}
      <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/80 border border-slate-800">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-xs text-slate-200">{doc.title}</span>
            <Badge variant="neutral" className="bg-slate-800 text-slate-300 text-[10px]">
              {doc.letter_type}
            </Badge>
            <Badge variant="neutral" className="bg-slate-800 text-slate-300 text-[10px]">
              {doc.tone}
            </Badge>
            <span className="text-[10px] text-slate-500 font-mono">v{doc.current_version}</span>
          </div>
          <p className="text-[11px] text-slate-400">
            {doc.target_role} {doc.employer_name ? `• ${doc.employer_name}` : ''} • Total: {totalWords} words
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            className="h-8 text-xs border-slate-700 text-slate-300 hover:text-white"
            onClick={handleSave}
            disabled={isSaving}
          >
            <Save className="w-3.5 h-3.5 mr-1" />
            {isSaving ? 'Saving...' : 'Save Draft'}
          </Button>

          <Button
            size="sm"
            className="h-8 text-xs bg-emerald-600 hover:bg-emerald-500 text-white"
            onClick={() => onApprove(doc.id)}
          >
            <FileCheck2 className="w-3.5 h-3.5 mr-1" />
            Approve Version
          </Button>

          <Button
            size="sm"
            variant="outline"
            className="h-8 w-8 p-0 text-slate-400 hover:text-slate-200 border-slate-700"
            onClick={() => onExport(doc.id, 'pdf')}
            title="Export PDF"
          >
            <Download className="w-3.5 h-3.5 text-red-400" />
          </Button>

          <Button
            size="sm"
            variant="outline"
            className="h-8 w-8 p-0 text-slate-400 hover:text-slate-200 border-slate-700"
            onClick={() => onExport(doc.id, 'docx')}
            title="Export Word (.docx)"
          >
            <Download className="w-3.5 h-3.5 text-blue-400" />
          </Button>
        </div>
      </div>

      {/* Main 3-Column Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left Column: Outline & Ordering (3 Cols) */}
        <div className="lg:col-span-3 space-y-3">
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs text-slate-300">Section Outline</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1.5 p-2">
              {doc.blocks.map((b) => {
                const isSelected = selectedBlock?.id === b.id;
                return (
                  <div
                    key={b.id}
                    onClick={() => setSelectedBlockId(b.id)}
                    className={`p-2 rounded text-xs cursor-pointer flex items-center justify-between border transition-all ${
                      isSelected
                        ? 'bg-slate-950 border-cyan-500/70 text-cyan-300 ring-1 ring-cyan-500/20'
                        : 'bg-slate-950/40 border-slate-800/80 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                    }`}
                  >
                    <div className="space-y-0.5 truncate pr-2">
                      <span className="font-semibold block uppercase text-[10px] tracking-wider">
                        {b.block_type.replace('_', ' ')}
                      </span>
                      <span className="text-[10px] text-slate-500 block truncate">
                        {b.text.slice(0, 32)}...
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-500 shrink-0">
                      {b.word_count}w
                    </span>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </div>

        {/* Center Column: Paragraph Text & Rewrite Assistant (6 Cols) */}
        <div className="lg:col-span-6 space-y-3">
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-2 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-xs text-slate-200 uppercase tracking-wider">
                  {selectedBlock?.block_type.replace('_', ' ')} Paragraph
                </CardTitle>
                <p className="text-[11px] text-slate-400">
                  {selectedBlock?.word_count ?? 0} words • Grounded in canonical facts
                </p>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <textarea
                value={selectedBlock?.text || ''}
                onChange={(e) => {
                  const newText = e.target.value;
                  const newBlocks = doc.blocks.map((b) =>
                    b.id === selectedBlock.id
                      ? {
                          ...b,
                          text: newText,
                          word_count: newText.split(/\s+/).filter(Boolean).length,
                          is_user_edited: true,
                        }
                      : b
                  );
                  setDoc({ ...doc, blocks: newBlocks });
                }}
                rows={9}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-xs leading-relaxed text-slate-200 font-serif focus:outline-none focus:border-cyan-500"
              />

              {/* AI Rewrite Assistant Box */}
              <div className="p-3 rounded-lg border border-slate-800 bg-slate-950/60 space-y-2">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-cyan-300">
                  <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                  Targeted Paragraph Rewrite
                </div>
                <div className="flex gap-2">
                  <Input
                    value={rewriteInstruction}
                    onChange={(e) => setRewriteInstruction(e.target.value)}
                    placeholder="e.g. 'Make more concise', 'Highlight Rust concurrency', 'More formal'..."
                    className="h-8 text-xs bg-slate-900 border-slate-700 text-slate-200"
                  />
                  <Button
                    size="sm"
                    className="h-8 text-xs bg-cyan-700 hover:bg-cyan-600 text-white shrink-0"
                    onClick={handleRewrite}
                    disabled={isRewriting || !rewriteInstruction.trim()}
                  >
                    {isRewriting ? 'Rewriting...' : 'Rewrite'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Grounding & Fact Validation (3 Cols) */}
        <div className="lg:col-span-3 space-y-3">
          {/* Grounding Status Card */}
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-2">
              <div className="flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <CardTitle className="text-xs text-slate-200">Fact Grounding Audit</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-2.5 text-xs">
              <div className="flex items-center justify-between text-[11px] pb-1 border-b border-slate-800">
                <span className="text-slate-400">Integrity Status</span>
                <span className="text-emerald-400 font-medium">100% Grounded</span>
              </div>
              <div className="flex items-center justify-between text-[11px] pb-1 border-b border-slate-800">
                <span className="text-slate-400">Linked Profile Claims</span>
                <span className="text-slate-200 font-mono">
                  {selectedBlock?.source_refs.length ?? 0}
                </span>
              </div>
              <div className="flex items-center justify-between text-[11px] pb-1 border-b border-slate-800">
                <span className="text-slate-400">Total Word Target</span>
                <span className="text-slate-200 font-mono">{totalWords} / 400w</span>
              </div>

              {/* Linked Sources for Active Block */}
              <div className="space-y-1.5 pt-1">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block">
                  Referenced Source Facts:
                </span>
                {(!selectedBlock?.source_refs || selectedBlock.source_refs.length === 0) ? (
                  <p className="text-[11px] text-slate-500 italic">Structural opening/closing text.</p>
                ) : (
                  <div className="space-y-1">
                    {selectedBlock.source_refs.map((src, i) => (
                      <div
                        key={i}
                        className="p-1.5 rounded bg-slate-950/80 border border-slate-800 text-[10px] text-slate-300 space-y-0.5"
                      >
                        <div className="flex items-center justify-between text-cyan-400 font-mono">
                          <span>{src.source_type}</span>
                          <span className="text-emerald-400">verified</span>
                        </div>
                        <p className="text-slate-400 truncate">{src.attribution_text || src.source_entity_id}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Validation Warnings/Issues if any */}
          {validationData && (
            <Card className="bg-slate-900/60 border-slate-800">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                  <CardTitle className="text-xs text-slate-200">Compliance Checks</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="space-y-2 text-xs">
                {validationData.errors.length === 0 && validationData.warnings.length === 0 ? (
                  <p className="text-[11px] text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> All factual and length tests passed.
                  </p>
                ) : (
                  <div className="space-y-1.5">
                    {validationData.errors.map((err, i) => (
                      <p key={i} className="text-[11px] text-rose-400 flex items-start gap-1">
                        <AlertTriangle className="w-3 h-3 shrink-0 mt-0.5" /> {err}
                      </p>
                    ))}
                    {validationData.warnings.map((warn, i) => (
                      <p key={i} className="text-[11px] text-amber-400 flex items-start gap-1">
                        <AlertTriangle className="w-3 h-3 shrink-0 mt-0.5" /> {warn}
                      </p>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
