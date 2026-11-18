/**
 * Stage 24: Application Writing Packages Tab.
 * Assembles and seals complete application submissions binding resumes, cover letters,
 * and screening answers into immutable audit-ready packages.
 */

import * as React from 'react';
import {
  Archive,
  Plus,
  AlertTriangle,
  FileCheck2,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type {
  ApplicationWritingPackage,
  CoverLetterDocument,
  ApplicationQuestionSet,
  WritingPackageCreateRequest,
} from '@autonom/shared-types';

interface WritingPackagesTabProps {
  packages: ApplicationWritingPackage[];
  coverLetters: CoverLetterDocument[];
  questionSets: ApplicationQuestionSet[];
  onCreatePackage: (req: WritingPackageCreateRequest) => Promise<ApplicationWritingPackage | null>;
  onApprovePackage: (id: string) => Promise<void>;
  onRefresh: () => Promise<void>;
}

export const WritingPackagesTab: React.FC<WritingPackagesTabProps> = ({
  packages,
  coverLetters,
  questionSets,
  onCreatePackage,
  onApprovePackage,
  onRefresh,
}) => {
  const [isCreating, setIsCreating] = React.useState<boolean>(false);
  const [jobTitle, setJobTitle] = React.useState<string>('Senior Software Engineer');
  const [employer, setEmployer] = React.useState<string>('Stripe');
  const [selectedLetterId, setSelectedLetterId] = React.useState<string>('');
  const [selectedSetId, setSelectedSetId] = React.useState<string>('');
  const [jobDescription, setJobDescription] = React.useState<string>('');
  const [selectedPackageId, setSelectedPackageId] = React.useState<string | null>(null);
  const [validationReport, setValidationReport] = React.useState<{
    is_valid: boolean;
    errors: string[];
    warnings: string[];
    ready_for_approval: boolean;
  } | null>(null);

  React.useEffect(() => {
    if (coverLetters.length > 0 && !selectedLetterId) {
      setSelectedLetterId(coverLetters[0].id);
    }
    if (questionSets.length > 0 && !selectedSetId) {
      setSelectedSetId(questionSets[0].id);
    }
  }, [coverLetters, questionSets]);

  const handleCreate = async () => {
    if (!jobTitle.trim() || !employer.trim()) return;
    setIsCreating(true);
    try {
      const pkg = await onCreatePackage({
        target_job_title: jobTitle,
        target_employer: employer,
        cover_letter_id: selectedLetterId || null,
        question_set_id: selectedSetId || null,
        job_description_raw: jobDescription || null,
      });
      if (pkg) {
        setSelectedPackageId(pkg.id);
        await onRefresh();
      }
    } finally {
      setIsCreating(false);
    }
  };

  const handleAuditPackage = async (pkgId: string) => {
    setSelectedPackageId(pkgId);
    try {
      const rep = await apiClient.validateWritingPackage(pkgId);
      setValidationReport(rep);
    } catch {
      // Ignored
    }
  };

  const selectedPkg = packages.find((p) => p.id === selectedPackageId) || packages[0];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="p-4 rounded-lg bg-purple-950/20 border border-purple-500/30 flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <Archive className="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h3 className="text-xs font-semibold text-purple-200">
              Application Submission Package Assembly
            </h3>
            <p className="text-[11px] text-slate-300 leading-relaxed">
              Consolidates targeted resumes, customized cover letters, and screened Q&A responses into an immutable, verifiable application bundle. AUTONOM prepares packages for your inspection and manual delivery.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Creator & Packages List (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <Plus className="w-4 h-4 text-purple-400" />
                <CardTitle className="text-xs font-semibold text-slate-200">Assemble New Package</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <label className="text-slate-300">Target Role *</label>
                  <Input
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    className="h-8 text-xs bg-slate-950 border-slate-700 text-slate-200"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-slate-300">Target Employer *</label>
                  <Input
                    value={employer}
                    onChange={(e) => setEmployer(e.target.value)}
                    className="h-8 text-xs bg-slate-950 border-slate-700 text-slate-200"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-slate-300">Bound Cover Letter</label>
                <select
                  value={selectedLetterId}
                  onChange={(e) => setSelectedLetterId(e.target.value)}
                  className="w-full h-8 bg-slate-950 border border-slate-700 rounded px-2 text-xs text-slate-200"
                >
                  <option value="">None (Resume/Q&A only)</option>
                  {coverLetters.map((cl) => (
                    <option key={cl.id} value={cl.id}>
                      {cl.title} (v{cl.current_version})
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-slate-300">Bound Screening Question Set</label>
                <select
                  value={selectedSetId}
                  onChange={(e) => setSelectedSetId(e.target.value)}
                  className="w-full h-8 bg-slate-950 border border-slate-700 rounded px-2 text-xs text-slate-200"
                >
                  <option value="">None (Documents only)</option>
                  {questionSets.map((qs) => (
                    <option key={qs.id} value={qs.id}>
                      {qs.title} ({qs.questions.length} questions)
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-slate-300">Job Description Notes</label>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  rows={3}
                  className="w-full bg-slate-950 border border-slate-700 rounded p-2 text-xs text-slate-200 font-mono"
                  placeholder="Optional job posting excerpt..."
                />
              </div>

              <Button
                onClick={handleCreate}
                disabled={isCreating || !jobTitle.trim() || !employer.trim()}
                className="w-full bg-purple-600 hover:bg-purple-500 text-white text-xs h-8"
              >
                {isCreating ? 'Assembling Package...' : 'Assemble Application Package'}
              </Button>
            </CardContent>
          </Card>

          {/* Existing Packages List */}
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs text-slate-300">Existing Packages ({packages.length})</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 p-2 text-xs">
              {packages.length === 0 ? (
                <div className="py-6 text-center text-xs text-slate-500">
                  No packages created yet.
                </div>
              ) : (
                packages.map((pkg) => {
                  const isSelected = selectedPkg?.id === pkg.id;
                  return (
                    <div
                      key={pkg.id}
                      onClick={() => handleAuditPackage(pkg.id)}
                      className={`p-3 rounded-lg border cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-slate-950 border-purple-500/80 ring-1 ring-purple-500/20'
                          : 'bg-slate-950/40 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-200">
                          {pkg.target_job_title} at {pkg.target_employer}
                        </span>
                        <Badge variant="neutral" className="bg-purple-950/60 text-purple-300 text-[10px]">
                          {pkg.status}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1.5 font-mono">
                        <span>{pkg.answered_questions} / {pkg.total_questions} answers</span>
                        <span>{pkg.is_ready_for_approval ? 'Ready' : 'Pending'}</span>
                      </div>
                    </div>
                  );
                })
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Package Inspector & Approval Audit (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          {!selectedPkg ? (
            <Card className="bg-slate-900/40 border-slate-800 text-center py-16">
              <CardContent className="space-y-2">
                <Archive className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-xs text-slate-400">Select an application package to inspect.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              <Card className="bg-slate-900/60 border-slate-800">
                <CardHeader className="pb-3 flex flex-row items-center justify-between">
                  <div className="space-y-0.5">
                    <CardTitle className="text-xs font-semibold text-slate-200">
                      Package Detail: {selectedPkg.target_job_title} at {selectedPkg.target_employer}
                    </CardTitle>
                    <p className="text-[11px] text-slate-400 font-mono">
                      ID: {selectedPkg.id} • Version {selectedPkg.version_number}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    {selectedPkg.status !== 'approved' && (
                      <Button
                        size="sm"
                        className="h-8 text-xs bg-emerald-600 hover:bg-emerald-500 text-white"
                        onClick={() => onApprovePackage(selectedPkg.id)}
                      >
                        <FileCheck2 className="w-3.5 h-3.5 mr-1" />
                        Approve & Seal Package
                      </Button>
                    )}
                  </div>
                </CardHeader>

                <CardContent className="space-y-4 text-xs">
                  {/* Bound Assets Matrix */}
                  <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-slate-950/80 border border-slate-800 font-mono text-[11px]">
                    <div>
                      <span className="text-slate-500 block">Cover Letter</span>
                      <span className="text-slate-300">
                        {selectedPkg.cover_letter_id ? `Bound (${selectedPkg.cover_letter_id})` : 'None'}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Question Set</span>
                      <span className="text-slate-300">
                        {selectedPkg.question_set_id ? `Bound (${selectedPkg.question_set_id})` : 'None'}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Answer Progress</span>
                      <span className="text-cyan-400">
                        {selectedPkg.answered_questions} / {selectedPkg.total_questions}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Sensitive Items</span>
                      <span className="text-amber-400">
                        {selectedPkg.pending_sensitive_decisions} Pending
                      </span>
                    </div>
                  </div>

                  {/* Readiness & Consistency Report */}
                  {validationReport && (
                    <div className="p-3 rounded-lg border border-slate-800 bg-slate-950/60 space-y-2">
                      <div className="flex items-center justify-between text-xs font-semibold">
                        <span className="text-slate-200">Cross-Document Consistency Audit:</span>
                        <span className={validationReport.is_valid ? 'text-emerald-400' : 'text-rose-400'}>
                          {validationReport.is_valid ? 'Consistent & Verified' : 'Attention Required'}
                        </span>
                      </div>

                      {validationReport.errors.length > 0 && (
                        <div className="space-y-1">
                          {validationReport.errors.map((err, i) => (
                            <p key={i} className="text-[11px] text-rose-400 flex items-start gap-1">
                              <AlertTriangle className="w-3 h-3 shrink-0 mt-0.5" /> {err}
                            </p>
                          ))}
                        </div>
                      )}

                      {validationReport.warnings.length > 0 && (
                        <div className="space-y-1">
                          {validationReport.warnings.map((warn, i) => (
                            <p key={i} className="text-[11px] text-amber-400 flex items-start gap-1">
                              <AlertTriangle className="w-3 h-3 shrink-0 mt-0.5" /> {warn}
                            </p>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  <div className="p-3 rounded-lg border border-slate-800 bg-slate-950/40 text-[11px] text-slate-400 space-y-1">
                    <span className="font-semibold text-slate-300 block">Package Guarantee:</span>
                    <p>
                      All included claims are checked against canonical profile records. No demographic questions are filled automatically. Ready for one-click attachment or copy-paste into employer application forms.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
