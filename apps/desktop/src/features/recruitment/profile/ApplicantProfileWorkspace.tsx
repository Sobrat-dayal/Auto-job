/**
 * Stage 21: Authoritative Applicant Profile Workspace.
 * Full integration of Identity, Education, Experience, Skills, Projects, Evidence,
 * Import Review Queue, Claim Registry, Conflict Resolution, and Downstream Scoped Snapshots.
 */

import * as React from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { AlertTriangle } from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleTabs,
  ModuleLoadingState,
  ModuleErrorState,
} from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type {
  ApplicantProfile,
  DataQualityReport,
  ImportJob,
  EvidenceMetadata,
  ApplicantClaim,
  ProfileConflict,
  ProfileVersionRecord,
  ContactInfo,
  LocationInfo,
  EmploymentEligibility,
  EducationRecord,
  EmploymentRecord,
  SkillItem,
  ProjectRecord,
} from '@autonom/shared-types';

import { ApplicantOverviewTab } from './tabs/ApplicantOverviewTab';
import { ApplicantIdentityTab } from './tabs/ApplicantIdentityTab';
import { ApplicantEducationTab } from './tabs/ApplicantEducationTab';
import { ApplicantExperienceTab } from './tabs/ApplicantExperienceTab';
import { ApplicantSkillsTab } from './tabs/ApplicantSkillsTab';
import { ApplicantProjectsTab } from './tabs/ApplicantProjectsTab';
import { ApplicantEvidenceTab } from './tabs/ApplicantEvidenceTab';
import { ApplicantImportsTab } from './tabs/ApplicantImportsTab';
import { ApplicantVerificationTab } from './tabs/ApplicantVerificationTab';
import { ApplicantHistoryTab } from './tabs/ApplicantHistoryTab';

export const ApplicantProfileWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState<string>('overview');
  const [selectedImportJob, setSelectedImportJob] = React.useState<ImportJob | null>(null);

  // 1. Fetch Primary Profile
  const {
    data: profiles = [],
    isLoading: profilesLoading,
    error: profilesError,
    refetch: refetchProfiles,
  } = useQuery<ApplicantProfile[]>({
    queryKey: ['applicant-profiles'],
    queryFn: () => apiClient.listApplicantProfiles(),
  });

  const activeProfile = profiles.length > 0 ? profiles[0] : null;
  const profileId = activeProfile?.id || 'prof_primary_applicant';

  // 2. Fetch Data Quality Report
  const {
    data: qualityReport = null,
    isLoading: qualityLoading,
    refetch: refetchQuality,
  } = useQuery<DataQualityReport | null>({
    queryKey: ['applicant-quality', profileId],
    queryFn: () => (activeProfile ? apiClient.getApplicantQualityReport(profileId) : Promise.resolve(null)),
    enabled: !!activeProfile,
  });

  // 3. Fetch Claims
  const { data: claims = [], refetch: refetchClaims } = useQuery<ApplicantClaim[]>({
    queryKey: ['applicant-claims', profileId],
    queryFn: () => (activeProfile ? apiClient.listApplicantClaims(profileId) : Promise.resolve([])),
    enabled: !!activeProfile,
  });

  // 4. Fetch Conflicts
  const { data: conflicts = [], refetch: refetchConflicts } = useQuery<ProfileConflict[]>({
    queryKey: ['applicant-conflicts', profileId],
    queryFn: () => (activeProfile ? apiClient.listApplicantConflicts(profileId) : Promise.resolve([])),
    enabled: !!activeProfile,
  });

  // 5. Fetch Evidence Documents
  const { data: evidence = [], refetch: refetchEvidence } = useQuery<EvidenceMetadata[]>({
    queryKey: ['applicant-evidence', profileId],
    queryFn: () => (activeProfile ? apiClient.listApplicantEvidence(profileId) : Promise.resolve([])),
    enabled: !!activeProfile,
  });

  // 6. Fetch Version History
  const { data: versions = [], refetch: refetchVersions } = useQuery<ProfileVersionRecord[]>({
    queryKey: ['applicant-versions', profileId],
    queryFn: () => (activeProfile ? apiClient.getApplicantVersions(profileId) : Promise.resolve([])),
    enabled: !!activeProfile,
  });

  // State for in-flight import jobs
  const [importJobsList, setImportJobsList] = React.useState<ImportJob[]>([]);

  // Invalidate and refresh all profile state
  const handleRefreshAll = async () => {
    await Promise.all([
      refetchProfiles(),
      refetchQuality(),
      refetchClaims(),
      refetchConflicts(),
      refetchEvidence(),
      refetchVersions(),
    ]);
  };

  // Mutations
  const updateIdentityMutation = useMutation({
    mutationFn: (payload: { contact: ContactInfo; location: LocationInfo; eligibility: EmploymentEligibility }) =>
      apiClient.updateApplicantIdentity(profileId, payload),
    onSuccess: () => handleRefreshAll(),
  });

  const addEducationMutation = useMutation({
    mutationFn: (edu: Partial<EducationRecord>) => apiClient.addApplicantEducation(profileId, edu),
    onSuccess: () => handleRefreshAll(),
  });

  const deleteEducationMutation = useMutation({
    mutationFn: (eduId: string) => apiClient.deleteApplicantEducation(profileId, eduId),
    onSuccess: () => handleRefreshAll(),
  });

  const addExperienceMutation = useMutation({
    mutationFn: (exp: Partial<EmploymentRecord>) => apiClient.addApplicantExperience(profileId, exp),
    onSuccess: () => handleRefreshAll(),
  });

  const deleteExperienceMutation = useMutation({
    mutationFn: (expId: string) => apiClient.deleteApplicantExperience(profileId, expId),
    onSuccess: () => handleRefreshAll(),
  });

  const upsertSkillMutation = useMutation({
    mutationFn: (skill: Partial<SkillItem>) => apiClient.upsertApplicantSkill(profileId, skill),
    onSuccess: () => handleRefreshAll(),
  });

  const deleteSkillMutation = useMutation({
    mutationFn: (skillId: string) => apiClient.deleteApplicantSkill(profileId, skillId),
    onSuccess: () => handleRefreshAll(),
  });

  const addProjectMutation = useMutation({
    mutationFn: (proj: Partial<ProjectRecord>) => apiClient.addApplicantProject(profileId, proj),
    onSuccess: () => handleRefreshAll(),
  });

  const deleteProjectMutation = useMutation({
    mutationFn: (projId: string) => apiClient.deleteApplicantProject(profileId, projId),
    onSuccess: () => handleRefreshAll(),
  });

  const deleteEvidenceMutation = useMutation({
    mutationFn: (evId: string) => apiClient.deleteApplicantEvidence(profileId, evId),
    onSuccess: () => handleRefreshAll(),
  });

  const confirmClaimMutation = useMutation({
    mutationFn: ({ claimId, notes }: { claimId: string; notes?: string }) =>
      apiClient.confirmApplicantClaim(profileId, claimId, notes),
    onSuccess: () => handleRefreshAll(),
  });

  const rejectClaimMutation = useMutation({
    mutationFn: ({ claimId, reason }: { claimId: string; reason?: string }) =>
      apiClient.rejectApplicantClaim(profileId, claimId, reason),
    onSuccess: () => handleRefreshAll(),
  });

  const resolveConflictMutation = useMutation({
    mutationFn: (payload: { conflictId: string; choice: string; chosenClaimId?: string; manualVal?: any; rationale?: string }) =>
      apiClient.resolveApplicantConflict(profileId, payload.conflictId, {
        resolution_choice: payload.choice,
        chosen_claim_id: payload.chosenClaimId,
        manual_value: payload.manualVal,
        rationale: payload.rationale,
      }),
    onSuccess: () => handleRefreshAll(),
  });

  const handleUploadEvidence = async (file: File) => {
    const reader = new FileReader();
    reader.onload = async () => {
      const base64 = (reader.result as string).split(',')[1];
      const job = await apiClient.createApplicantImport(profileId, {
        filename: file.name,
        content_base64: base64,
      });
      setImportJobsList((prev) => [job, ...prev]);
      setSelectedImportJob(job);
      await handleRefreshAll();
    };
    reader.readAsDataURL(file);
  };

  const handleInitiateImport = async (file: File | null, rawText: string, filename: string) => {
    if (file) {
      const reader = new FileReader();
      reader.onload = async () => {
        const base64 = (reader.result as string).split(',')[1];
        const job = await apiClient.createApplicantImport(profileId, {
          filename,
          content_base64: base64,
        });
        setImportJobsList((prev) => [job, ...prev]);
        setSelectedImportJob(job);
        await handleRefreshAll();
      };
      reader.readAsDataURL(file);
    } else {
      const job = await apiClient.createApplicantImport(profileId, {
        filename,
        raw_text: rawText,
      });
      setImportJobsList((prev) => [job, ...prev]);
      setSelectedImportJob(job);
      await handleRefreshAll();
    }
  };

  const handleReviewCandidate = async (
    importId: string,
    candidateId: string,
    action: 'accept' | 'reject' | 'modify',
    modifiedData?: any,
    notes?: string
  ) => {
    await apiClient.reviewImportCandidate(profileId, importId, candidateId, action, modifiedData, notes);
    const updatedJob = await apiClient.getApplicantImport(profileId, importId);
    setImportJobsList((prev) => prev.map((j) => (j.id === importId ? updatedJob : j)));
    if (selectedImportJob?.id === importId) {
      setSelectedImportJob(updatedJob);
    }
    await handleRefreshAll();
  };

  const handleExportProfile = async () => {
    const data = await apiClient.exportApplicantProfile(profileId);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `autonom_applicant_profile_${profileId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (profilesLoading) {
    return (
      <ModulePage>
        <ModuleLoadingState layout="cards" />
      </ModulePage>
    );
  }

  if (profilesError) {
    return (
      <ModulePage>
        <ModuleErrorState
          title="Failed to Load Applicant Profile"
          message={String(profilesError)}
          onRetry={refetchProfiles}
        />
      </ModulePage>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview & Readiness' },
    { id: 'identity', label: 'Identity & Eligibility' },
    { id: 'education', label: `Education (${activeProfile?.education?.length || 0})` },
    { id: 'experience', label: `Experience (${activeProfile?.employment?.length || 0})` },
    { id: 'skills', label: `Skills (${activeProfile?.skills?.length || 0})` },
    { id: 'projects', label: `Projects (${activeProfile?.projects?.length || 0})` },
    { id: 'evidence', label: `Evidence Library (${evidence.length})` },
    { id: 'imports', label: `Document Imports (${importJobsList.length})` },
    { id: 'verification', label: `Claims & Conflicts (${claims.length})` },
    { id: 'history', label: 'History & Snapshots' },
  ];

  return (
    <ModulePage>
      <ModuleHeader
        title="Applicant Profile & Recruitment Identity"
        description="The authoritative, zero-hallucination ground truth for applicant credentials, employment, education, skills, and evidence provenance."
      >
        <div className="flex items-center gap-2">
          {conflicts.length > 0 && (
            <Badge variant="error" className="flex items-center gap-1">
              <AlertTriangle className="h-3 w-3" /> {conflicts.length} Active Conflicts
            </Badge>
          )}
          <Badge variant="outline" className="border-emerald-500 text-emerald-600 font-mono text-xs">
            Single Source of Truth
          </Badge>
        </div>
      </ModuleHeader>

      <div className="border-b px-6">
        <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      <div className="p-6">
        {activeTab === 'overview' && (
          <ApplicantOverviewTab
            profile={activeProfile}
            quality={qualityReport}
            isLoading={qualityLoading}
            onRefresh={handleRefreshAll}
            onExport={handleExportProfile}
          />
        )}

        {activeTab === 'identity' && (
          <ApplicantIdentityTab
            profile={activeProfile}
            onSave={async (payload) => {
              await updateIdentityMutation.mutateAsync(payload);
            }}
            isSaving={updateIdentityMutation.isPending}
          />
        )}

        {activeTab === 'education' && (
          <ApplicantEducationTab
            educationList={activeProfile?.education || []}
            onAdd={async (edu) => {
              await addEducationMutation.mutateAsync(edu);
            }}
            onDelete={async (id) => {
              await deleteEducationMutation.mutateAsync(id);
            }}
            isProcessing={addEducationMutation.isPending || deleteEducationMutation.isPending}
          />
        )}

        {activeTab === 'experience' && (
          <ApplicantExperienceTab
            experienceList={activeProfile?.employment || []}
            onAdd={async (exp) => {
              await addExperienceMutation.mutateAsync(exp);
            }}
            onDelete={async (id) => {
              await deleteExperienceMutation.mutateAsync(id);
            }}
            isProcessing={addExperienceMutation.isPending || deleteExperienceMutation.isPending}
          />
        )}

        {activeTab === 'skills' && (
          <ApplicantSkillsTab
            skillsList={activeProfile?.skills || []}
            onUpsert={async (skill) => {
              await upsertSkillMutation.mutateAsync(skill);
            }}
            onDelete={async (id) => {
              await deleteSkillMutation.mutateAsync(id);
            }}
            isProcessing={upsertSkillMutation.isPending || deleteSkillMutation.isPending}
          />
        )}

        {activeTab === 'projects' && (
          <ApplicantProjectsTab
            projectsList={activeProfile?.projects || []}
            onAdd={async (proj) => {
              await addProjectMutation.mutateAsync(proj);
            }}
            onDelete={async (id) => {
              await deleteProjectMutation.mutateAsync(id);
            }}
            isProcessing={addProjectMutation.isPending || deleteProjectMutation.isPending}
          />
        )}

        {activeTab === 'evidence' && (
          <ApplicantEvidenceTab
            evidenceList={evidence}
            onUpload={handleUploadEvidence}
            onDelete={async (id) => {
              await deleteEvidenceMutation.mutateAsync(id);
            }}
            isProcessing={deleteEvidenceMutation.isPending}
          />
        )}

        {activeTab === 'imports' && (
          <ApplicantImportsTab
            importJobs={importJobsList}
            activeJob={selectedImportJob}
            onInitiateImport={handleInitiateImport}
            onReviewCandidate={handleReviewCandidate}
            onSelectJob={setSelectedImportJob}
            isProcessing={false}
          />
        )}

        {activeTab === 'verification' && (
          <ApplicantVerificationTab
            claims={claims}
            conflicts={conflicts}
            onConfirmClaim={async (id, notes) => {
              await confirmClaimMutation.mutateAsync({ claimId: id, notes });
            }}
            onRejectClaim={async (id, reason) => {
              await rejectClaimMutation.mutateAsync({ claimId: id, reason });
            }}
            onResolveConflict={async (conflictId, choice, chosenClaimId, manualVal, rationale) => {
              await resolveConflictMutation.mutateAsync({ conflictId, choice, chosenClaimId, manualVal, rationale });
            }}
            isProcessing={confirmClaimMutation.isPending || rejectClaimMutation.isPending || resolveConflictMutation.isPending}
          />
        )}

        {activeTab === 'history' && (
          <ApplicantHistoryTab
            versionHistory={versions}
            onGenerateSnapshot={(targetAgent) => apiClient.generateApplicantSnapshot(profileId, targetAgent)}
            isProcessing={false}
          />
        )}
      </div>
    </ModulePage>
  );
};

export default ApplicantProfileWorkspace;
