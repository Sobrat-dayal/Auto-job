/**
 * Stage 23: Resume Intelligence Engine & Portfolio Builder Workspace.
 * Full desktop workspace integrating resume synthesis, ATS readability auditing,
 * job-specific tailoring with zero-hallucination evidence matching,
 * dual DOCX/PDF compilation, version diffing, and developer portfolio creation.
 */

import * as React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  FileText,
  FileCheck2,
  FolderGit2,
  Sparkles,
  ShieldCheck,
  Download,
  History,
  Layers,
  Edit3,
  Sliders,
  Briefcase,
} from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleTabs,
} from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type {
  ResumeDocument,
  ResumeOverviewStats,
  ResumeTemplateDefinition,
  ResumeCreateRequest,
  ResumeUpdateRequest,
  ExportFormat,
} from '@autonom/shared-types';

import { ResumeOverviewTab } from './tabs/ResumeOverviewTab';
import { MyResumesTab } from './tabs/MyResumesTab';
import { ResumeBuilderTab } from './tabs/ResumeBuilderTab';
import { ResumeEditorTab } from './tabs/ResumeEditorTab';
import { JobTailoringTab } from './tabs/JobTailoringTab';
import { TemplateGalleryTab } from './tabs/TemplateGalleryTab';
import { ATSReadabilityTab } from './tabs/ATSReadabilityTab';
import { DocumentPreviewTab } from './tabs/DocumentPreviewTab';
import { ResumeVersionsTab } from './tabs/ResumeVersionsTab';
import { ExportManagerTab } from './tabs/ExportManagerTab';
import { PortfolioBuilderTab } from './tabs/PortfolioBuilderTab';

export const ResumePortfolioWorkspace: React.FC = () => {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = React.useState<string>('overview');
  const [selectedResumeId, setSelectedResumeId] = React.useState<string | null>(null);

  // 1. Fetch Overview Stats
  const { data: overviewStats = null } = useQuery<ResumeOverviewStats>({
    queryKey: ['resumes-overview'],
    queryFn: () => apiClient.getResumesOverview(),
  });

  // 2. Fetch Resumes List
  const { data: resumes = [] } = useQuery<ResumeDocument[]>({
    queryKey: ['resumes-list'],
    queryFn: () => apiClient.listResumes(),
  });

  // 3. Fetch Templates
  const { data: templates = [] } = useQuery<ResumeTemplateDefinition[]>({
    queryKey: ['resume-templates'],
    queryFn: () => apiClient.listResumeTemplates(),
  });

  // Keep selected resume synced
  const selectedResume = React.useMemo(() => {
    if (!selectedResumeId && resumes.length > 0) {
      return resumes[0];
    }
    return resumes.find((r) => r.id === selectedResumeId) || (resumes.length > 0 ? resumes[0] : null);
  }, [resumes, selectedResumeId]);

  // 4. Fetch Validation Issues for Selected Resume
  const { data: validationData = null } = useQuery({
    queryKey: ['resume-validation', selectedResume?.id],
    queryFn: () => (selectedResume ? apiClient.getResumeValidation(selectedResume.id) : Promise.resolve(null)),
    enabled: !!selectedResume?.id,
  });

  // Mutations
  const createResumeMutation = useMutation({
    mutationFn: (req: ResumeCreateRequest) => apiClient.createResume(req),
    onSuccess: (created) => {
      queryClient.invalidateQueries({ queryKey: ['resumes-list'] });
      queryClient.invalidateQueries({ queryKey: ['resumes-overview'] });
      setSelectedResumeId(created.id);
      setActiveTab('editor');
    },
  });

  const duplicateResumeMutation = useMutation({
    mutationFn: (resumeId: string) => apiClient.duplicateResume(resumeId),
    onSuccess: (duplicated) => {
      queryClient.invalidateQueries({ queryKey: ['resumes-list'] });
      queryClient.invalidateQueries({ queryKey: ['resumes-overview'] });
      setSelectedResumeId(duplicated.id);
    },
  });

  const deleteResumeMutation = useMutation({
    mutationFn: (resumeId: string) => apiClient.deleteResume(resumeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes-list'] });
      queryClient.invalidateQueries({ queryKey: ['resumes-overview'] });
      setSelectedResumeId(null);
    },
  });

  const updateResumeMutation = useMutation({
    mutationFn: ({ id, req }: { id: string; req: ResumeUpdateRequest }) => apiClient.updateResume(id, req),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes-list'] });
      queryClient.invalidateQueries({ queryKey: ['resume-validation', selectedResume?.id] });
    },
  });

  const approveResumeMutation = useMutation({
    mutationFn: (id: string) => apiClient.approveResume(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes-list'] });
      queryClient.invalidateQueries({ queryKey: ['resumes-overview'] });
    },
  });

  const exportResumeMutation = useMutation({
    mutationFn: ({ id, format }: { id: string; format: ExportFormat }) =>
      apiClient.exportResume(id, { format, validate_extraction: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes-list'] });
    },
  });

  const handleSelectResume = (r: ResumeDocument) => {
    setSelectedResumeId(r.id);
  };

  const handleCreateResume = async (req: ResumeCreateRequest): Promise<ResumeDocument | null> => {
    const res = await createResumeMutation.mutateAsync(req);
    return res;
  };

  const handleSaveResume = async (updated: ResumeDocument) => {
    await updateResumeMutation.mutateAsync({
      id: updated.id,
      req: {
        title: updated.title,
        target_role: updated.target_role,
        sections: updated.sections,
        template_id: updated.template_id,
        page_format: updated.page_format,
        max_pages: updated.max_pages,
      },
    });
  };

  const handleApplyTemplate = async (templateId: string) => {
    if (!selectedResume) return;
    await updateResumeMutation.mutateAsync({
      id: selectedResume.id,
      req: { template_id: templateId },
    });
  };

  const handleApproveSelected = async () => {
    if (!selectedResume) return;
    await approveResumeMutation.mutateAsync(selectedResume.id);
  };

  const handleExportSelected = async (format: ExportFormat) => {
    if (!selectedResume) return;
    await exportResumeMutation.mutateAsync({ id: selectedResume.id, format });
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: FileText },
    { id: 'my_resumes', label: `My Resumes (${resumes.length})`, icon: FolderGit2 },
    { id: 'builder', label: 'Builder Wizard', icon: Sparkles },
    { id: 'editor', label: 'Visual Editor', icon: Edit3 },
    { id: 'tailoring', label: 'Job Tailoring', icon: Sliders },
    { id: 'templates', label: `Templates (${templates.length})`, icon: Layers },
    { id: 'ats', label: 'ATS Readability', icon: ShieldCheck },
    { id: 'preview', label: 'Preview & Sheet', icon: FileCheck2 },
    { id: 'versions', label: 'Versions & Diff', icon: History },
    { id: 'exports', label: 'Export Manager', icon: Download },
    { id: 'portfolio', label: 'Portfolio Builder', icon: Briefcase },
  ];

  return (
    <ModulePage>
      <ModuleHeader
        title="Resume Intelligence Engine & Portfolio Builder"
        description="Stage 23: Synthesize verified, ATS-compatible resumes and multi-page professional portfolios grounded in verified profile claims and GitHub intelligence with zero hallucination."
        actions={
          <div className="flex items-center gap-2">
            {selectedResume && (
              <Badge variant="outline" className="bg-indigo-500/10 text-indigo-400 border-indigo-500/30 gap-1 text-xs">
                Active: {selectedResume.title} ({selectedResume.resume_type})
              </Badge>
            )}
            <Badge variant="neutral" className="text-xs">
              Stage 23 of 50
            </Badge>
          </div>
        }
      />

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="flex-1 p-6 overflow-y-auto">
        {activeTab === 'overview' && (
          <ResumeOverviewTab
            stats={overviewStats}
            resumes={resumes}
            onSelectResume={(r) => {
              handleSelectResume(r);
              setActiveTab('editor');
            }}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'my_resumes' && (
          <MyResumesTab
            resumes={resumes}
            selectedResume={selectedResume}
            onSelectResume={handleSelectResume}
            onDuplicateResume={(id) => duplicateResumeMutation.mutate(id)}
            onDeleteResume={(id) => deleteResumeMutation.mutate(id)}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'builder' && (
          <ResumeBuilderTab
            onCreateResume={handleCreateResume}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'editor' && (
          <ResumeEditorTab
            resume={selectedResume}
            validationIssues={validationData?.issues || []}
            onSaveResume={handleSaveResume}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'tailoring' && (
          <JobTailoringTab
            resume={selectedResume}
            onSelectResume={handleSelectResume}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'templates' && (
          <TemplateGalleryTab
            templates={templates}
            currentResume={selectedResume}
            onApplyTemplate={handleApplyTemplate}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'ats' && (
          <ATSReadabilityTab
            resume={selectedResume}
          />
        )}

        {activeTab === 'preview' && (
          <DocumentPreviewTab
            resume={selectedResume}
            onExport={handleExportSelected}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'versions' && (
          <ResumeVersionsTab
            resume={selectedResume}
            onApproveResume={handleApproveSelected}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'exports' && (
          <ExportManagerTab
            resume={selectedResume}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'portfolio' && (
          <PortfolioBuilderTab
            onNavigateTab={setActiveTab}
          />
        )}
      </div>
    </ModulePage>
  );
};

export default ResumePortfolioWorkspace;
