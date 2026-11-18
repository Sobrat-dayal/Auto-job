/**
 * Stage 24: Recruitment Writing Intelligence & Application Answers Master Workspace.
 * Comprehensive desktop workspace connecting:
 * - Factual Cover Letter Synthesis & ATS Formatting
 * - Screening Question Intelligence & STAR Answer Generation
 * - Reusable Parameterized Answer Library & Freshness Checking
 * - Missing Information & Fact Contradiction Audits
 * - Strictly Guarded Sensitive Disclosures & Legal Attestations
 * - Application Writing Package Assembly
 */

import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  FileText,
  Sparkles,
  ShieldCheck,
  Layers,
  Edit3,
  HelpCircle,
  BookOpen,
  AlertTriangle,
  ShieldAlert,
  Archive,
  Plus,
} from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleTabs,
} from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type {
  CoverLetterDocument,
  CoverLetterTemplateDefinition,
  CoverLetterCreateRequest,
  ApplicationQuestionSet,
  QuestionSetCreateRequest,
  AnswerLibraryEntry,
  AnswerLibraryCreateRequest,
  MissingInformationItem,
  SensitiveDecisionItem,
  ConflictItem,
  ApplicationWritingPackage,
  WritingPackageCreateRequest,
  WritingOverviewStats,
  UserAttestationRequest,
} from '@autonom/shared-types';

import { WritingOverviewTab } from './tabs/WritingOverviewTab';
import { CoverLetterStudioTab } from './tabs/CoverLetterStudioTab';
import { MyCoverLettersTab } from './tabs/MyCoverLettersTab';
import { CoverLetterEditorTab } from './tabs/CoverLetterEditorTab';
import { CoverLetterTemplatesTab } from './tabs/CoverLetterTemplatesTab';
import { ScreeningQuestionsTab } from './tabs/ScreeningQuestionsTab';
import { AnswerLibraryTab } from './tabs/AnswerLibraryTab';
import { MissingInfoConflictsTab } from './tabs/MissingInfoConflictsTab';
import { SensitiveDecisionsTab } from './tabs/SensitiveDecisionsTab';
import { WritingPackagesTab } from './tabs/WritingPackagesTab';

export const RecruitmentWritingWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState<string>('overview');
  const [selectedLetterId, setSelectedLetterId] = React.useState<string | null>(null);
  const [selectedQuestionSetId, setSelectedQuestionSetId] = React.useState<string | null>(null);

  // 1. Fetch Overview Stats
  const { data: stats = null, refetch: refetchStats } = useQuery<WritingOverviewStats>({
    queryKey: ['writing-overview'],
    queryFn: () => apiClient.getWritingOverview(),
  });

  // 2. Fetch Cover Letters List
  const { data: coverLetters = [], refetch: refetchLetters } = useQuery<CoverLetterDocument[]>({
    queryKey: ['cover-letters-list'],
    queryFn: () => apiClient.listCoverLetters(),
  });

  // 3. Fetch Templates
  const { data: templates = [] } = useQuery<CoverLetterTemplateDefinition[]>({
    queryKey: ['cover-letter-templates'],
    queryFn: () => apiClient.listCoverLetterTemplates(),
  });

  // 4. Fetch Question Sets
  const { data: questionSets = [], refetch: refetchQuestionSets } = useQuery<ApplicationQuestionSet[]>({
    queryKey: ['question-sets-list'],
    queryFn: () => apiClient.listQuestionSets(),
  });

  // 5. Fetch Answer Library
  const { data: libraryEntries = [], refetch: refetchLibrary } = useQuery<AnswerLibraryEntry[]>({
    queryKey: ['answer-library-list'],
    queryFn: () => apiClient.listAnswerLibrary(),
  });

  // 6. Fetch Missing Info Items
  const { data: missingItems = [], refetch: refetchMissing } = useQuery<MissingInformationItem[]>({
    queryKey: ['writing-missing-info'],
    queryFn: () => apiClient.getMissingInformation(),
  });

  // 7. Fetch Sensitive Decisions
  const { data: sensitiveDecisions = [], refetch: refetchSensitive } = useQuery<SensitiveDecisionItem[]>({
    queryKey: ['writing-sensitive-decisions'],
    queryFn: () => apiClient.getSensitiveDecisions(),
  });

  // 8. Fetch Fact Conflicts
  const { data: conflicts = [], refetch: refetchConflicts } = useQuery<ConflictItem[]>({
    queryKey: ['writing-conflicts'],
    queryFn: () => apiClient.getWritingConflicts(),
  });

  // 9. Fetch Writing Packages
  const { data: packages = [], refetch: refetchPackages } = useQuery<ApplicationWritingPackage[]>({
    queryKey: ['writing-packages-list'],
    queryFn: () => apiClient.listWritingPackages(),
  });

  // Synchronize Active Cover Letter Selection
  const selectedLetter = React.useMemo(() => {
    if (!selectedLetterId && coverLetters.length > 0) {
      return coverLetters[0];
    }
    return coverLetters.find((c) => c.id === selectedLetterId) || (coverLetters.length > 0 ? coverLetters[0] : null);
  }, [coverLetters, selectedLetterId]);

  // Synchronize Active Question Set Selection
  const selectedQuestionSet = React.useMemo(() => {
    if (!selectedQuestionSetId && questionSets.length > 0) {
      return questionSets[0];
    }
    return questionSets.find((qs) => qs.id === selectedQuestionSetId) || (questionSets.length > 0 ? questionSets[0] : null);
  }, [questionSets, selectedQuestionSetId]);

  // Handlers
  const handleGenerateCoverLetter = async (req: CoverLetterCreateRequest): Promise<CoverLetterDocument | null> => {
    try {
      const doc = await apiClient.createCoverLetter(req);
      await refetchLetters();
      await refetchStats();
      setSelectedLetterId(doc.id);
      return doc;
    } catch (e) {
      console.error('Failed to generate cover letter:', e);
      return null;
    }
  };

  const handleSaveCoverLetter = async (updated: CoverLetterDocument): Promise<void> => {
    try {
      await apiClient.updateCoverLetter(updated.id, {
        title: updated.title,
        letter_type: updated.letter_type,
        target_role: updated.target_role,
        employer_name: updated.employer_name,
        template_id: updated.template_id,
        tone: updated.tone,
        length_preference: updated.length_preference,
        recipient_name: updated.recipient_name,
        blocks: updated.blocks,
      });
      await refetchLetters();
      await refetchStats();
    } catch (e) {
      console.error('Failed to save cover letter:', e);
    }
  };

  const handleDeleteCoverLetter = async (id: string): Promise<void> => {
    try {
      await apiClient.deleteCoverLetter(id);
      if (selectedLetterId === id) {
        setSelectedLetterId(null);
      }
      await refetchLetters();
      await refetchStats();
    } catch (e) {
      console.error('Failed to delete cover letter:', e);
    }
  };

  const handleApproveCoverLetter = async (id: string): Promise<void> => {
    try {
      await apiClient.approveCoverLetter(id);
      await refetchLetters();
      await refetchStats();
    } catch (e) {
      console.error('Failed to approve cover letter:', e);
    }
  };

  const handleExportCoverLetter = async (id: string, format: 'pdf' | 'docx'): Promise<void> => {
    try {
      await apiClient.exportCoverLetter(id, { format });
    } catch (e) {
      console.error('Failed to export cover letter:', e);
    }
  };

  const handleApplyTemplate = async (templateId: string): Promise<void> => {
    if (!selectedLetter) return;
    try {
      await apiClient.updateCoverLetter(selectedLetter.id, {
        template_id: templateId,
      });
      await refetchLetters();
    } catch (e) {
      console.error('Failed to apply template:', e);
    }
  };

  const handleCreateQuestionSet = async (req: QuestionSetCreateRequest): Promise<ApplicationQuestionSet | null> => {
    try {
      const created = await apiClient.createQuestionSet(req);
      await refetchQuestionSets();
      await refetchStats();
      setSelectedQuestionSetId(created.id);
      return created;
    } catch (e) {
      console.error('Failed to create question set:', e);
      return null;
    }
  };

  const handleGenerateAnswers = async (setId: string): Promise<void> => {
    try {
      await apiClient.generateAnswersForQuestionSet(setId);
      await refetchQuestionSets();
      await refetchStats();
    } catch (e) {
      console.error('Failed to generate answers:', e);
    }
  };

  const handleUpdateAnswer = async (setId: string, questionId: string, answerText: string): Promise<void> => {
    try {
      await apiClient.updateAnswer(setId, questionId, { answer_text: answerText });
      await refetchQuestionSets();
    } catch (e) {
      console.error('Failed to update answer:', e);
    }
  };

  const handleCreateLibraryEntry = async (req: AnswerLibraryCreateRequest): Promise<void> => {
    try {
      await apiClient.createAnswerLibraryEntry(req);
      await refetchLibrary();
      await refetchStats();
    } catch (e) {
      console.error('Failed to create library entry:', e);
    }
  };

  const handleDeleteLibraryEntry = async (id: string): Promise<void> => {
    try {
      await apiClient.deleteAnswerLibraryEntry(id);
      await refetchLibrary();
      await refetchStats();
    } catch (e) {
      console.error('Failed to delete library entry:', e);
    }
  };

  const handleCheckFreshness = async (): Promise<void> => {
    try {
      await apiClient.checkAnswerLibraryFreshness();
      await refetchLibrary();
      await refetchStats();
    } catch (e) {
      console.error('Failed to check freshness:', e);
    }
  };

  const handleRecordAttestation = async (req: UserAttestationRequest): Promise<void> => {
    try {
      await apiClient.recordUserAttestation(req);
      await refetchSensitive();
      await refetchStats();
    } catch (e) {
      console.error('Failed to record attestation:', e);
    }
  };

  const handleCreatePackage = async (req: WritingPackageCreateRequest): Promise<ApplicationWritingPackage | null> => {
    try {
      const created = await apiClient.createWritingPackage(req);
      await refetchPackages();
      await refetchStats();
      return created;
    } catch (e) {
      console.error('Failed to assemble package:', e);
      return null;
    }
  };

  const handleApprovePackage = async (id: string): Promise<void> => {
    try {
      await apiClient.approveWritingPackage(id);
      await refetchPackages();
      await refetchStats();
    } catch (e) {
      console.error('Failed to approve package:', e);
    }
  };

  const tabs = [
    {
      id: 'overview',
      label: 'Overview',
      icon: Sparkles,
    },
    {
      id: 'studio',
      label: 'Cover Letter Studio',
      icon: Plus,
    },
    {
      id: 'my-letters',
      label: `My Letters (${coverLetters.length})`,
      icon: FileText,
    },
    {
      id: 'editor',
      label: 'Visual Editor',
      icon: Edit3,
    },
    {
      id: 'templates',
      label: 'Templates (6)',
      icon: Layers,
    },
    {
      id: 'screening',
      label: `Screening Q&A (${questionSets.length})`,
      icon: HelpCircle,
    },
    {
      id: 'library',
      label: `Answer Library (${libraryEntries.length})`,
      icon: BookOpen,
    },
    {
      id: 'missing-conflicts',
      label: 'Gaps & Conflicts',
      icon: AlertTriangle,
    },
    {
      id: 'sensitive',
      label: 'Sensitive Decisions',
      icon: ShieldAlert,
    },
    {
      id: 'packages',
      label: `Packages (${packages.length})`,
      icon: Archive,
    },
  ];

  return (
    <ModulePage>
      <ModuleHeader
        title="Recruitment Writing & Application Intelligence"
        description="Factual cover letter synthesis, truthful screening answers, reusable answer library, and complete application submission packages grounded in verified applicant profile facts."
        actions={
          <div className="flex items-center gap-2">
            {stats && stats.sensitive_decisions_count > 0 && (
              <Badge variant="neutral" className="bg-amber-950/70 text-amber-300 border-amber-800 text-xs">
                {stats.sensitive_decisions_count} Sensitive Decisions Pending
              </Badge>
            )}
            <Badge variant="neutral" className="bg-cyan-950/60 text-cyan-400 border-cyan-800 text-xs flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" />
              Zero-Hallucination Enforced
            </Badge>
          </div>
        }
      />

      <ModuleTabs
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      <div className="mt-6">
        {activeTab === 'overview' && (
          <WritingOverviewTab
            stats={stats}
            coverLetters={coverLetters}
            packages={packages}
            onNavigateTab={setActiveTab}
            onRefreshStats={async () => {
              await refetchStats();
              await refetchLetters();
              await refetchPackages();
            }}
            onCheckFreshness={handleCheckFreshness}
          />
        )}

        {activeTab === 'studio' && (
          <CoverLetterStudioTab
            onGenerate={handleGenerateCoverLetter}
            onSelectLetter={(cl) => setSelectedLetterId(cl.id)}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'my-letters' && (
          <MyCoverLettersTab
            coverLetters={coverLetters}
            selectedLetterId={selectedLetterId}
            onSelectLetter={(cl) => setSelectedLetterId(cl.id)}
            onDeleteLetter={handleDeleteCoverLetter}
            onExportLetter={handleExportCoverLetter}
            onApproveLetter={handleApproveCoverLetter}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'editor' && (
          <CoverLetterEditorTab
            letter={selectedLetter}
            onSave={handleSaveCoverLetter}
            onApprove={handleApproveCoverLetter}
            onExport={handleExportCoverLetter}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'templates' && (
          <CoverLetterTemplatesTab
            templates={templates}
            currentLetter={selectedLetter}
            onApplyTemplate={handleApplyTemplate}
          />
        )}

        {activeTab === 'screening' && (
          <ScreeningQuestionsTab
            questionSets={questionSets}
            selectedSet={selectedQuestionSet}
            onSelectSet={(qs) => setSelectedQuestionSetId(qs.id)}
            onCreateSet={handleCreateQuestionSet}
            onGenerateAnswers={handleGenerateAnswers}
            onUpdateAnswer={handleUpdateAnswer}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'library' && (
          <AnswerLibraryTab
            entries={libraryEntries}
            onRefreshLibrary={async () => {
              await refetchLibrary();
            }}
            onCreateEntry={handleCreateLibraryEntry}
            onDeleteEntry={handleDeleteLibraryEntry}
          />
        )}

        {activeTab === 'missing-conflicts' && (
          <MissingInfoConflictsTab
            missingItems={missingItems}
            conflicts={conflicts}
            onRefresh={async () => {
              await refetchMissing();
              await refetchConflicts();
            }}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'sensitive' && (
          <SensitiveDecisionsTab
            decisions={sensitiveDecisions}
            onRecordAttestation={handleRecordAttestation}
            onRefresh={async () => {
              await refetchSensitive();
              await refetchStats();
            }}
          />
        )}

        {activeTab === 'packages' && (
          <WritingPackagesTab
            packages={packages}
            coverLetters={coverLetters}
            questionSets={questionSets}
            onCreatePackage={handleCreatePackage}
            onApprovePackage={handleApprovePackage}
            onRefresh={async () => {
              await refetchPackages();
              await refetchStats();
            }}
          />
        )}
      </div>
    </ModulePage>
  );
};

export default RecruitmentWritingWorkspace;
