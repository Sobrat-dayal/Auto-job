/**
 * Stage 21: Applicant Document Import & Review Queue Tab.
 * Human-in-the-loop candidate extraction verification preventing unauthorized hallucination.
 */

import * as React from 'react';
import {
  FileUp,
  CheckCircle,
  XCircle,
  Edit3,
  Clock,
  Check,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import type { ImportJob, ExtractionCandidate } from '@autonom/shared-types';

interface ApplicantImportsTabProps {
  importJobs: ImportJob[];
  activeJob: ImportJob | null;
  onInitiateImport: (file: File | null, rawText: string, filename: string) => Promise<void>;
  onReviewCandidate: (
    importId: string,
    candidateId: string,
    action: 'accept' | 'reject' | 'modify',
    modifiedData?: any,
    notes?: string
  ) => Promise<void>;
  onSelectJob: (job: ImportJob) => void;
  isProcessing: boolean;
}

export const ApplicantImportsTab: React.FC<ApplicantImportsTabProps> = ({
  importJobs,
  activeJob,
  onInitiateImport,
  onReviewCandidate,
  onSelectJob,
  isProcessing,
}) => {
  const [file, setFile] = React.useState<File | null>(null);
  const [rawText, setRawText] = React.useState<string>('');
  const [importMode, setImportMode] = React.useState<'file' | 'text'>('file');
  const [editingCandidateId, setEditingCandidateId] = React.useState<string | null>(null);
  const [editValue, setEditValue] = React.useState<string>('');

  const handleStartImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (importMode === 'file' && !file) return;
    if (importMode === 'text' && !rawText.trim()) return;

    const filename = file?.name || 'pasted_resume.txt';
    await onInitiateImport(file, rawText, filename);
    setFile(null);
    setRawText('');
  };

  const handleStartEdit = (candidate: ExtractionCandidate) => {
    setEditingCandidateId(candidate.id);
    setEditValue(
      typeof candidate.extracted_value === 'string'
        ? candidate.extracted_value
        : JSON.stringify(candidate.extracted_value, null, 2)
    );
  };

  const handleSaveEdit = async (candidate: ExtractionCandidate) => {
    let parsed: any = editValue;
    try {
      parsed = JSON.parse(editValue);
    } catch {
      parsed = editValue;
    }

    if (activeJob) {
      await onReviewCandidate(activeJob.id, candidate.id, 'modify', parsed, 'User modified during import review');
    }
    setEditingCandidateId(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">Document Ingestion & Staged Extraction Pipeline</h3>
          <p className="text-sm text-muted-foreground">
            Strict human review queue. Extracted items NEVER enter the authoritative profile without explicit acceptance.
          </p>
        </div>
      </div>

      {/* Ingestion Trigger Form */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <FileUp className="h-4 w-4 text-primary" />
              Import Resume or Professional Document
            </CardTitle>
            <div className="flex gap-1 border rounded p-0.5 text-xs bg-muted">
              <button
                type="button"
                onClick={() => setImportMode('file')}
                className={`px-3 py-1 rounded transition-colors ${importMode === 'file' ? 'bg-background shadow font-medium' : 'text-muted-foreground'}`}
              >
                File Upload
              </button>
              <button
                type="button"
                onClick={() => setImportMode('text')}
                className={`px-3 py-1 rounded transition-colors ${importMode === 'text' ? 'bg-background shadow font-medium' : 'text-muted-foreground'}`}
              >
                Paste Text
              </button>
            </div>
          </div>
          <CardDescription>
            Supported formats: PDF, DOCX, TXT, JSON, MD. Safe sandboxed parsing with regex & heuristic NER.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleStartImport} className="space-y-4">
            {importMode === 'file' ? (
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Select Resume Document File
                </label>
                <Input
                  type="file"
                  accept=".pdf,.docx,.txt,.json,.md"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="mt-1"
                />
              </div>
            ) : (
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Paste Resume or Profile Text
                </label>
                <textarea
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  placeholder="Paste raw resume or LinkedIn summary text here..."
                  rows={4}
                  className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                />
              </div>
            )}

            <div className="flex justify-end">
              <Button type="submit" disabled={isProcessing || (importMode === 'file' ? !file : !rawText.trim())}>
                <FileUp className="mr-2 h-4 w-4" />
                {isProcessing ? 'Parsing & Extracting...' : 'Parse & Extract Claims'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Review Queue Workspace */}
      <div className="grid gap-6 md:grid-cols-3">
        {/* Import Jobs List */}
        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle className="text-sm font-semibold">Import History & Jobs</CardTitle>
            <CardDescription>Select an ingestion run to review extracted candidates.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 p-3">
            {importJobs.length === 0 ? (
              <p className="text-xs text-muted-foreground text-center py-4">No import jobs recorded.</p>
            ) : (
              importJobs.map((job) => (
                <div
                  key={job.id}
                  onClick={() => onSelectJob(job)}
                  className={`p-3 rounded-md border cursor-pointer transition-colors ${activeJob?.id === job.id ? 'border-primary bg-primary/5' : 'hover:bg-muted/50'}`}
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold truncate max-w-[150px]">{job.filename}</span>
                    <Badge variant={job.status === 'completed' ? 'primary' : 'neutral'} className="text-[10px]">
                      {job.status}
                    </Badge>
                  </div>
                  <div className="mt-1 text-[11px] text-muted-foreground flex justify-between">
                    <span>{job.candidates.length} candidates</span>
                    <span>{job.accepted_count} accepted</span>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        {/* Candidate Items Review Queue */}
        <Card className="md:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-base font-semibold">
                  Extraction Candidates Review Queue
                </CardTitle>
                <CardDescription>
                  {activeJob ? (
                    <span>
                      Job: <strong className="text-foreground">{activeJob.filename}</strong> • {activeJob.candidates.filter((c) => c.status === 'extracted').length} pending review
                    </span>
                  ) : (
                    'Select an import job from the left to begin candidate review.'
                  )}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {!activeJob || activeJob.candidates.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground">
                <Clock className="mb-2 h-10 w-10 text-muted-foreground" />
                <p className="font-medium">No Candidates to Review</p>
                <p className="text-xs">Upload a resume to automatically stage candidates for review.</p>
              </div>
            ) : (
              activeJob.candidates.map((cand) => {
                const isPending = cand.status === 'extracted';
                const isAccepted = cand.status === 'accepted';
                const isRejected = cand.status === 'rejected';
                const isModified = cand.status === 'modified';

                return (
                  <div
                    key={cand.id}
                    className={`rounded-lg border p-4 space-y-2 transition-colors ${
                      isAccepted
                        ? 'border-emerald-500/30 bg-emerald-50/20 dark:bg-emerald-950/10'
                        : isRejected
                          ? 'border-muted opacity-60'
                          : 'bg-card'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-sm capitalize">{cand.field_name.replace(/_/g, ' ')}</span>
                          <Badge variant="outline" className="text-[10px] capitalize">
                            {cand.category}
                          </Badge>
                          <span className="text-[11px] text-muted-foreground">
                            Confidence: {Math.round(cand.confidence * 100)}%
                          </span>
                          {cand.duplicate_flag && (
                            <Badge variant="warning" className="text-[10px]">
                              Duplicate Flag
                            </Badge>
                          )}
                        </div>

                        {cand.raw_text_snippet && (
                          <p className="text-xs text-muted-foreground italic">
                            Source: "{cand.raw_text_snippet}"
                          </p>
                        )}
                      </div>

                      {/* Review Buttons */}
                      <div className="flex items-center gap-1.5">
                        {isPending ? (
                          <>
                            <Button
                              size="sm"
                              variant="primary"
                              onClick={() => onReviewCandidate(activeJob.id, cand.id, 'accept')}
                              disabled={isProcessing}
                              className="h-7 text-xs bg-emerald-600 hover:bg-emerald-700"
                            >
                              <CheckCircle className="mr-1 h-3.5 w-3.5" /> Accept
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleStartEdit(cand)}
                              disabled={isProcessing}
                              className="h-7 text-xs"
                            >
                              <Edit3 className="mr-1 h-3.5 w-3.5" /> Edit
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => onReviewCandidate(activeJob.id, cand.id, 'reject')}
                              disabled={isProcessing}
                              className="h-7 text-xs text-destructive hover:bg-destructive/10"
                            >
                              <XCircle className="mr-1 h-3.5 w-3.5" /> Reject
                            </Button>
                          </>
                        ) : (
                          <Badge
                            variant={isAccepted || isModified ? 'primary' : 'neutral'}
                            className="capitalize text-xs"
                          >
                            {cand.status}
                          </Badge>
                        )}
                      </div>
                    </div>

                    {/* Value Display or Edit Mode */}
                    {editingCandidateId === cand.id ? (
                      <div className="pt-2 space-y-2 border-t">
                        <textarea
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          rows={3}
                          className="w-full rounded-md border border-input bg-background p-2 font-mono text-xs shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                        />
                        <div className="flex justify-end gap-2">
                          <Button size="sm" variant="ghost" onClick={() => setEditingCandidateId(null)} className="h-7 text-xs">
                            Cancel
                          </Button>
                          <Button size="sm" onClick={() => handleSaveEdit(cand)} className="h-7 text-xs">
                            <Check className="mr-1 h-3.5 w-3.5" /> Save & Accept
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="mt-1 rounded bg-muted/50 p-2 text-xs font-mono break-all">
                        {typeof cand.extracted_value === 'object'
                          ? JSON.stringify(cand.extracted_value, null, 2)
                          : String(cand.extracted_value)}
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
