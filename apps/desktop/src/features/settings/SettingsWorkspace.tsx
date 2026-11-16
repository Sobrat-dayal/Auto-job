import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { AllSettingsResponse } from '@autonom/shared-types';
import { apiClient } from '@/lib/api-client';
import { restartBackendProcess } from '@/services/tauri';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Upload, AlertTriangle, RefreshCw } from 'lucide-react';
import { SettingsLayout, SettingsConfirmationDialog, SETTINGS_CATEGORIES } from './components';
import {
  GeneralSettingsPage,
  AppearanceSettingsPage,
  AIProviderSettingsPage,
  AgentPreferencesPage,
  AutomationSettingsPage,
  PermissionSettingsPage,
  ComputerControlSettingsPage,
  IntegrationSettingsPage,
  RecruitmentSettingsPage,
  StorageSettingsPage,
  NotificationSettingsPage,
  DesktopSettingsPage,
  SecuritySettingsPage,
  DiagnosticsSettingsPage,
  AboutSettingsPage,
} from './pages';

export const SettingsWorkspace: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const queryClient = useQueryClient();

  // Extract category from URL: /settings/:category or default to general
  const pathParts = location.pathname.split('/').filter(Boolean);
  const routeCategory = pathParts[1] || 'general';

  // Normalize selected category
  const [selectedCategory, setSelectedCategory] = useState<string>(routeCategory);

  useEffect(() => {
    if (routeCategory && routeCategory !== selectedCategory) {
      setSelectedCategory(routeCategory);
    }
  }, [routeCategory]);

  const handleCategorySelect = (categoryId: string) => {
    setSelectedCategory(categoryId);
    navigate(`/settings/${categoryId}`);
  };

  // Centralized query for all settings
  const {
    data: allSettings,
    isLoading,
    isError,
    refetch,
  } = useQuery<AllSettingsResponse>({
    queryKey: ['settings', 'all'],
    queryFn: () => apiClient.getAllSettings(),
    staleTime: 5000,
  });

  // Local editable draft state
  const [draftSettings, setDraftSettings] = useState<AllSettingsResponse | null>(null);
  const [dirtyCategories, setDirtyCategories] = useState<string[]>([]);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);
  const [saveErrorMessage, setSaveErrorMessage] = useState<string | null>(null);

  // Sync draft when data loads
  useEffect(() => {
    if (allSettings) {
      setDraftSettings(allSettings);
      setDirtyCategories([]);
    }
  }, [allSettings]);

  // Mutation for saving a specific category
  const updateMutation = useMutation({
    mutationFn: async ({ category, value }: { category: string; value: unknown }) => {
      return apiClient.updateSettingCategory(category, value as Record<string, unknown>);
    },
    onSuccess: (_, variables) => {
      setSaveSuccess(true);
      setSaveErrorMessage(null);
      setDirtyCategories((prev) => prev.filter((c) => c !== variables.category));
      queryClient.invalidateQueries({ queryKey: ['settings', 'all'] });
      setTimeout(() => setSaveSuccess(false), 3500);
    },
    onError: (err) => {
      setSaveSuccess(false);
      setSaveErrorMessage(err instanceof Error ? err.message : 'Failed to save settings');
    },
  });

  // Helper to update draft for a category
  const handleCategoryDraftChange = <K extends keyof AllSettingsResponse>(
    category: K,
    updates: Partial<AllSettingsResponse[K]>
  ) => {
    if (!draftSettings) return;
    const current = draftSettings[category];
    if (typeof current === 'object' && current !== null) {
      const updatedCategory = { ...current, ...updates } as AllSettingsResponse[K];
      setDraftSettings({ ...draftSettings, [category]: updatedCategory });
      if (!dirtyCategories.includes(category as string)) {
        setDirtyCategories((prev) => [...prev, category as string]);
      }
      setSaveSuccess(false);
      setSaveErrorMessage(null);
    }
  };

  const handleSaveCategory = (category: string) => {
    if (!draftSettings) return;
    const val = draftSettings[category as keyof AllSettingsResponse];
    updateMutation.mutate({ category, value: val });
  };

  const handleResetCategoryDraft = (category: string) => {
    if (!allSettings || !draftSettings) return;
    const original = allSettings[category as keyof AllSettingsResponse];
    setDraftSettings({ ...draftSettings, [category]: original });
    setDirtyCategories((prev) => prev.filter((c) => c !== category));
    setSaveSuccess(false);
    setSaveErrorMessage(null);
  };

  // Export / Import Modals & Actions
  const [importModalOpen, setImportModalOpen] = useState(false);
  const [importJsonText, setImportJsonText] = useState('');
  const [importStatus, setImportStatus] = useState<string | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [resetAllConfirmOpen, setResetAllConfirmOpen] = useState(false);
  const [isResettingAll, setIsResettingAll] = useState(false);
  const [isRestartingBackend, setIsRestartingBackend] = useState(false);

  const handleExport = async () => {
    try {
      const payload = await apiClient.exportSettings();
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `autonom_settings_export_${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(`Export failed: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  const handleImportSubmit = async () => {
    if (!importJsonText.trim()) return;
    setIsImporting(true);
    setImportStatus('Validating and applying configuration...');
    try {
      const parsed = JSON.parse(importJsonText);
      const res = await apiClient.importSettings(parsed);
      setImportStatus(
        `Imported ${res.total_categories} categories successfully (${res.imported_categories.join(', ')}).`
      );
      await refetch();
      setTimeout(() => {
        setImportModalOpen(false);
        setImportJsonText('');
        setImportStatus(null);
      }, 1500);
    } catch (err) {
      setImportStatus(`Import failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsImporting(false);
    }
  };

  const handleResetAllDefaults = async () => {
    setIsResettingAll(true);
    try {
      await apiClient.resetSettingCategory('all');
      await refetch();
      setResetAllConfirmOpen(false);
    } finally {
      setIsResettingAll(false);
    }
  };

  const handleRestartBackend = async () => {
    setIsRestartingBackend(true);
    try {
      await restartBackendProcess();
      await refetch();
    } finally {
      setIsRestartingBackend(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-full w-full items-center justify-center p-12 text-muted-foreground">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="h-6 w-6 animate-spin text-primary" />
          <span className="text-xs font-medium">Loading settings from persistent storage...</span>
        </div>
      </div>
    );
  }

  if (isError || !draftSettings) {
    return (
      <div className="flex h-full w-full items-center justify-center p-12 text-muted-foreground">
        <div className="flex flex-col items-center gap-3 max-w-md text-center">
          <AlertTriangle className="h-8 w-8 text-rose-400" />
          <span className="text-sm font-semibold text-foreground">Failed to Load Settings</span>
          <p className="text-xs text-muted-foreground">
            The local settings service or SQLite persistence could not be reached. Ensure the
            backend sidecar is active.
          </p>
          <Button variant="outline" size="sm" onClick={() => refetch()} className="text-xs mt-2">
            Retry Connection
          </Button>
        </div>
      </div>
    );
  }

  // Active Category Meta
  const activeMeta =
    SETTINGS_CATEGORIES.find((c) => c.id === selectedCategory) || SETTINGS_CATEGORIES[0];
  const isCategoryDirty = dirtyCategories.includes(selectedCategory);

  return (
    <SettingsLayout
      selectedCategoryId={selectedCategory}
      onSelectCategory={handleCategorySelect}
      title={activeMeta.label}
      description={`Manage and configure ${activeMeta.label.toLowerCase()} preferences and system rules.`}
      dirtyCategories={dirtyCategories}
      onExportSettings={handleExport}
      onImportSettings={() => setImportModalOpen(true)}
      onResetAll={() => setResetAllConfirmOpen(true)}
    >
      {/* 1. General */}
      {selectedCategory === 'general' && (
        <GeneralSettingsPage
          settings={draftSettings.general}
          isDirty={isCategoryDirty}
          isSaving={updateMutation.isPending}
          saveSuccess={saveSuccess}
          errorMessage={saveErrorMessage}
          onChange={(updates) => handleCategoryDraftChange('general', updates)}
          onSave={() => handleSaveCategory('general')}
          onReset={() => handleResetCategoryDraft('general')}
        />
      )}

      {/* 2. Appearance */}
      {selectedCategory === 'appearance' && (
        <AppearanceSettingsPage
          settings={draftSettings.appearance}
          isDirty={isCategoryDirty}
          isSaving={updateMutation.isPending}
          saveSuccess={saveSuccess}
          errorMessage={saveErrorMessage}
          onChange={(updates) => handleCategoryDraftChange('appearance', updates)}
          onSave={() => handleSaveCategory('appearance')}
          onReset={() => handleResetCategoryDraft('appearance')}
        />
      )}

      {/* 3. AI Providers */}
      {selectedCategory === 'ai' && (
        <AIProviderSettingsPage
          settings={draftSettings.ai}
          isDirty={isCategoryDirty}
          isSaving={updateMutation.isPending}
          saveSuccess={saveSuccess}
          errorMessage={saveErrorMessage}
          onChange={(updates) => handleCategoryDraftChange('ai', updates)}
          onSave={() => handleSaveCategory('ai')}
          onReset={() => handleResetCategoryDraft('ai')}
        />
      )}

      {/* 4. Agent Preferences */}
      {selectedCategory === 'agents' && (
        <AgentPreferencesPage
          settings={draftSettings.agents}
          isDirty={isCategoryDirty}
          isSaving={updateMutation.isPending}
          saveSuccess={saveSuccess}
          errorMessage={saveErrorMessage}
          onChange={(updates) => handleCategoryDraftChange('agents', updates)}
          onSave={() => handleSaveCategory('agents')}
          onReset={() => handleResetCategoryDraft('agents')}
        />
      )}

      {/* 5. Automation */}
      {selectedCategory === 'automation' && (
        <AutomationSettingsPage
          settings={draftSettings.automation}
          isDirty={isCategoryDirty}
          isSaving={updateMutation.isPending}
          saveSuccess={saveSuccess}
          errorMessage={saveErrorMessage}
          onChange={(updates) => handleCategoryDraftChange('automation', updates)}
          onSave={() => handleSaveCategory('automation')}
          onReset={() => handleResetCategoryDraft('automation')}
          onRestartBackend={handleRestartBackend}
          isRestartingBackend={isRestartingBackend}
        />
      )}

      {/* 6. Permissions */}
      {selectedCategory === 'permissions' && (
        <PermissionSettingsPage
          settings={draftSettings.permissions}
          isDirty={isCategoryDirty}
          isSaving={updateMutation.isPending}
          saveSuccess={saveSuccess}
          errorMessage={saveErrorMessage}
          onChange={(updates) => handleCategoryDraftChange('permissions', updates)}
          onSave={() => handleSaveCategory('permissions')}
          onReset={() => handleResetCategoryDraft('permissions')}
        />
      )}

      {/* 7. Computer Control */}
      {selectedCategory === 'computer' && (
        <ComputerControlSettingsPage
          settings={draftSettings.computer}
          isDirty={isCategoryDirty}
          isSaving={updateMutation.isPending}
          saveSuccess={saveSuccess}
          errorMessage={saveErrorMessage}
          onChange={(updates) => handleCategoryDraftChange('computer', updates)}
          onSave={() => handleSaveCategory('computer')}
          onReset={() => handleResetCategoryDraft('computer')}
        />
      )}

      {/* 8. Integrations */}
      {selectedCategory === 'integrations' && (
        <IntegrationSettingsPage
          settings={draftSettings.integrations}
          isDirty={isCategoryDirty}
          isSaving={updateMutation.isPending}
          saveSuccess={saveSuccess}
          errorMessage={saveErrorMessage}
          onChange={(updates) => handleCategoryDraftChange('integrations', updates)}
          onSave={() => handleSaveCategory('integrations')}
          onReset={() => handleResetCategoryDraft('integrations')}
        />
      )}

      {/* 9. Recruitment */}
      {selectedCategory === 'recruitment' && (
        <RecruitmentSettingsPage
          settings={draftSettings.recruitment}
          isDirty={isCategoryDirty}
          isSaving={updateMutation.isPending}
          saveSuccess={saveSuccess}
          errorMessage={saveErrorMessage}
          onChange={(updates) => handleCategoryDraftChange('recruitment', updates)}
          onSave={() => handleSaveCategory('recruitment')}
          onReset={() => handleResetCategoryDraft('recruitment')}
        />
      )}

      {/* 10. Storage */}
      {selectedCategory === 'storage' && (
        <StorageSettingsPage
          settings={draftSettings.storage}
          isDirty={isCategoryDirty}
          isSaving={updateMutation.isPending}
          saveSuccess={saveSuccess}
          errorMessage={saveErrorMessage}
          onChange={(updates) => handleCategoryDraftChange('storage', updates)}
          onSave={() => handleSaveCategory('storage')}
          onReset={() => handleResetCategoryDraft('storage')}
        />
      )}

      {/* 11. Notifications */}
      {selectedCategory === 'notifications' && (
        <NotificationSettingsPage
          settings={draftSettings.notifications}
          isDirty={isCategoryDirty}
          isSaving={updateMutation.isPending}
          saveSuccess={saveSuccess}
          errorMessage={saveErrorMessage}
          onChange={(updates) => handleCategoryDraftChange('notifications', updates)}
          onSave={() => handleSaveCategory('notifications')}
          onReset={() => handleResetCategoryDraft('notifications')}
        />
      )}

      {/* 12. Desktop & Startup */}
      {selectedCategory === 'desktop' && (
        <DesktopSettingsPage
          settings={draftSettings.desktop}
          isDirty={isCategoryDirty}
          isSaving={updateMutation.isPending}
          saveSuccess={saveSuccess}
          errorMessage={saveErrorMessage}
          onChange={(updates) => handleCategoryDraftChange('desktop', updates)}
          onSave={() => handleSaveCategory('desktop')}
          onReset={() => handleResetCategoryDraft('desktop')}
        />
      )}

      {/* 13. Security */}
      {selectedCategory === 'security' && (
        <SecuritySettingsPage
          settings={draftSettings.security}
          isDirty={isCategoryDirty}
          isSaving={updateMutation.isPending}
          saveSuccess={saveSuccess}
          errorMessage={saveErrorMessage}
          onChange={(updates) => handleCategoryDraftChange('security', updates)}
          onSave={() => handleSaveCategory('security')}
          onReset={() => handleResetCategoryDraft('security')}
        />
      )}

      {/* 14. Diagnostics */}
      {selectedCategory === 'diagnostics' && <DiagnosticsSettingsPage />}

      {/* 15. About */}
      {selectedCategory === 'about' && <AboutSettingsPage />}

      {/* Import Modal */}
      <Dialog open={importModalOpen} onOpenChange={setImportModalOpen}>
        <DialogContent className="max-w-lg bg-card border-border shadow-xl">
          <DialogHeader>
            <DialogTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
              <Upload className="h-4 w-4 text-primary" />
              <span>Import Configuration JSON</span>
            </DialogTitle>
            <DialogDescription className="text-xs text-muted-foreground">
              Paste exported configuration JSON. Settings will be validated against strict Pydantic
              schemas before persisting.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-2 py-2">
            <textarea
              rows={8}
              placeholder='Paste exported JSON (e.g. { "schema_version": 1, "settings": { ... } })'
              value={importJsonText}
              onChange={(e) => setImportJsonText(e.target.value)}
              className="w-full rounded border border-input bg-card p-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            />
            {importStatus && <p className="text-xs text-cyan">{importStatus}</p>}
          </div>

          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setImportModalOpen(false)}
              className="text-xs h-8"
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleImportSubmit}
              disabled={isImporting || !importJsonText.trim()}
              className="text-xs h-8"
            >
              {isImporting ? 'Validating...' : 'Validate & Import'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reset All Confirmation Dialog */}
      <SettingsConfirmationDialog
        open={resetAllConfirmOpen}
        onOpenChange={setResetAllConfirmOpen}
        title="Reset All Settings to Defaults"
        description="Are you sure you want to restore all 13 settings categories to system defaults? Stored credentials and job application records will not be deleted."
        confirmLabel="Reset All to Defaults"
        variant="destructive"
        isConfirming={isResettingAll}
        onConfirm={handleResetAllDefaults}
      />
    </SettingsLayout>
  );
};

export default SettingsWorkspace;
