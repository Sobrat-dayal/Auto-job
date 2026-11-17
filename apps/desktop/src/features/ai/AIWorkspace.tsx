import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Sparkles, Cpu, Route, BarChart3, AlertCircle } from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleTabs,
  ModuleLoadingState,
  type ModuleTabItem,
} from '@/components/module';
import { ResourceMonitorCard } from './components/ResourceMonitorCard';
import { AIPlayground } from './pages/AIPlayground';
import { ModelManagementPage } from './pages/ModelManagementPage';
import { ModelRoutingPage } from './pages/ModelRoutingPage';
import { AIUsagePage } from './pages/AIUsagePage';
import { apiClient } from '@/lib/api-client';
import type {
  HardwareTelemetry,
  ModelInfo,
  ProviderSummary,
  AIRoutingPreference,
  AIUsageSummary,
} from '@autonom/shared-types';

export const AIWorkspace: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Navigation tab determination
  const getCurrentTab = (): string => {
    if (location.pathname.includes('/ai/models')) return 'models';
    if (location.pathname.includes('/ai/routing')) return 'routing';
    if (location.pathname.includes('/ai/usage')) return 'usage';
    return 'playground';
  };

  const activeTab = getCurrentTab();

  const handleTabChange = (tabId: string) => {
    navigate(`/ai/${tabId}`);
  };

  // State
  const [telemetry, setTelemetry] = React.useState<HardwareTelemetry | null>(null);
  const [models, setModels] = React.useState<ModelInfo[]>([]);
  const [providers, setProviders] = React.useState<ProviderSummary[]>([]);
  const [preferences, setPreferences] = React.useState<AIRoutingPreference[]>([]);
  const [usageSummary, setUsageSummary] = React.useState<AIUsageSummary | null>(null);

  const [isLoading, setIsLoading] = React.useState(true);
  const [isRefreshingTelemetry, setIsRefreshingTelemetry] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  const loadData = React.useCallback(async () => {
    setErrorMessage(null);
    try {
      const [resTelemetry, resModels, resProviders, resPrefs, resUsage] =
        await Promise.allSettled([
          apiClient.getAIHardwareResources(),
          apiClient.getAIModels(),
          apiClient.getAIProviders(),
          apiClient.getAIRoutingPreferences(),
          apiClient.getAIUsageSummary(30),
        ]);

      if (resTelemetry.status === 'fulfilled') setTelemetry(resTelemetry.value);
      if (resModels.status === 'fulfilled') setModels(resModels.value);
      if (resProviders.status === 'fulfilled') setProviders(resProviders.value);
      if (resPrefs.status === 'fulfilled') setPreferences(resPrefs.value);
      if (resUsage.status === 'fulfilled') setUsageSummary(resUsage.value);
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to initialize AI workspace data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refreshTelemetryOnly = async () => {
    setIsRefreshingTelemetry(true);
    try {
      const t = await apiClient.getAIHardwareResources();
      setTelemetry(t);
    } catch (err) {
      console.error('Failed to refresh telemetry:', err);
    } finally {
      setIsRefreshingTelemetry(false);
    }
  };

  React.useEffect(() => {
    loadData();

    // Telemetry polling interval (every 6 seconds)
    const interval = setInterval(() => {
      apiClient.getAIHardwareResources().then(setTelemetry).catch(() => {});
    }, 6000);

    return () => clearInterval(interval);
  }, [loadData]);

  const handleLoadModel = async (modelId: string) => {
    await apiClient.loadLocalAIModel(modelId);
    await refreshTelemetryOnly();
  };

  const handleUnloadModel = async (modelId: string) => {
    await apiClient.unloadLocalAIModel(modelId);
    await refreshTelemetryOnly();
  };

  const tabItems: ModuleTabItem[] = [
    {
      id: 'playground',
      label: 'AI Playground',
      icon: Sparkles,
    },
    {
      id: 'models',
      label: `Model Management (${models.length})`,
      icon: Cpu,
    },
    {
      id: 'routing',
      label: 'Model Routing',
      icon: Route,
    },
    {
      id: 'usage',
      label: 'AI Usage & Analytics',
      icon: BarChart3,
    },
  ];

  if (isLoading) {
    return (
      <ModulePage>
        <ModuleHeader
          title="AI Model Gateway"
          description="Unified local and cloud LLM inference, dynamic model routing, and GPU telemetry."
          badgeLabel="Stage 11"
          badgeVariant="cyan"
          icon={Sparkles}
        />
        <ModuleLoadingState rows={3} layout="cards" />
      </ModulePage>
    );
  }

  return (
    <ModulePage>
      <ModuleHeader
        title="AI Model Gateway"
        description="Unified local and cloud inference engine with intelligent routing, streaming token delivery, and single-model RTX 4050 6GB VRAM bounds."
        badgeLabel="Stage 11 Active"
        badgeVariant="cyan"
        icon={Sparkles}
      />

      {errorMessage && (
        <div className="p-3 rounded-lg border border-rose-800/40 bg-rose-950/20 text-xs text-rose-300 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      <div className="space-y-4">
        {/* Hardware & GPU Telemetry Bar */}
        <ResourceMonitorCard
          telemetry={telemetry}
          isLoading={isRefreshingTelemetry}
          onRefresh={refreshTelemetryOnly}
          onModelUnloaded={refreshTelemetryOnly}
        />

        {/* Tab Navigation */}
        <ModuleTabs
          tabs={tabItems}
          activeTab={activeTab}
          onTabChange={handleTabChange}
        />

        {/* Tab Content */}
        {activeTab === 'playground' && (
          <AIPlayground models={models} />
        )}

        {activeTab === 'models' && (
          <ModelManagementPage
            models={models}
            providers={providers}
            activeModelInVram={telemetry?.active_local_model}
            isLoading={isLoading}
            onRefresh={loadData}
            onLoadModel={handleLoadModel}
            onUnloadModel={handleUnloadModel}
          />
        )}

        {activeTab === 'routing' && (
          <ModelRoutingPage
            models={models}
            preferences={preferences}
            onRefreshPreferences={loadData}
          />
        )}

        {activeTab === 'usage' && (
          <AIUsagePage
            usageSummary={usageSummary}
            isLoading={isLoading}
            onRefresh={loadData}
          />
        )}
      </div>
    </ModulePage>
  );
};

export default AIWorkspace;
