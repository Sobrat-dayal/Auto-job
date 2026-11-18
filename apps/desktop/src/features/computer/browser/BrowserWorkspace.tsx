import * as React from 'react';
import {
  Globe,
  Code2,
  FolderDown,
  Lock,
  Layers,
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import {
  BrowserRuntimeStatus,
  BrowserSessionSummary,
  BrowserSessionResponse,
  BrowserSessionCreateRequest,
  BrowserNavigateRequest,
  BrowserActionRequest,
  BrowserProfileResponse,
  BrowserProfileCreateRequest,
  BrowserDownloadResponse,
} from '@autonom/shared-types';
import { BrowserOverviewTab } from './BrowserOverviewTab';
import { BrowserLiveControllerTab } from './BrowserLiveControllerTab';
import { BrowserDOMInspectorTab } from './BrowserDOMInspectorTab';
import { BrowserDownloadsTab } from './BrowserDownloadsTab';
import { BrowserProfilesTab } from './BrowserProfilesTab';

export const BrowserWorkspace: React.FC = () => {
  const [subTab, setSubTab] = React.useState<string>('overview');
  const [runtimeStatus, setRuntimeStatus] = React.useState<BrowserRuntimeStatus | null>(null);
  const [sessions, setSessions] = React.useState<BrowserSessionSummary[]>([]);
  const [selectedSession, setSelectedSession] = React.useState<BrowserSessionResponse | null>(null);
  const [profiles, setProfiles] = React.useState<BrowserProfileResponse[]>([]);
  const [downloads, setDownloads] = React.useState<BrowserDownloadResponse[]>([]);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);

  const loadData = React.useCallback(async () => {
    setIsLoading(true);
    try {
      const [status, sessionList, profileList, downloadList] = await Promise.all([
        apiClient.getBrowserRuntimeStatus().catch(() => null),
        apiClient.listBrowserSessions().catch(() => []),
        apiClient.listBrowserProfiles().catch(() => []),
        apiClient.listBrowserDownloads().catch(() => []),
      ]);

      setRuntimeStatus(status);
      setSessions(sessionList);
      setProfiles(profileList);
      setDownloads(downloadList);

      // If active session selected, refresh its details
      if (selectedSession) {
        const refreshed = await apiClient.getBrowserSession(selectedSession.id).catch(() => null);
        setSelectedSession(refreshed);
      } else if (sessionList.length > 0) {
        // Auto-select first running session if none selected
        const running = sessionList.find((s) => s.status === 'running') || sessionList[0];
        const detailed = await apiClient.getBrowserSession(running.id).catch(() => null);
        setSelectedSession(detailed);
      }
    } finally {
      setIsLoading(false);
    }
  }, [selectedSession?.id]);

  React.useEffect(() => {
    loadData();
  }, []);

  const handleLaunchSession = async (req: BrowserSessionCreateRequest) => {
    const created = await apiClient.createBrowserSession(req);
    setSelectedSession(created);
    await loadData();
    setSubTab('controller');
  };

  const handleCloseSession = async (sessionId: string) => {
    await apiClient.closeBrowserSession(sessionId);
    if (selectedSession?.id === sessionId) {
      setSelectedSession(null);
    }
    await loadData();
  };

  const handleSelectSession = async (sessionId: string) => {
    const sess = await apiClient.getBrowserSession(sessionId);
    setSelectedSession(sess);
    setSubTab('controller');
  };

  const handleNavigate = async (sessionId: string, req: BrowserNavigateRequest) => {
    await apiClient.navigateBrowser(sessionId, req);
    const updated = await apiClient.getBrowserSession(sessionId);
    setSelectedSession(updated);
  };

  const handleExecuteAction = async (sessionId: string, req: BrowserActionRequest) => {
    const res = await apiClient.executeBrowserAction(sessionId, req);
    const updated = await apiClient.getBrowserSession(sessionId);
    setSelectedSession(updated);
    return res;
  };

  const handleCaptureScreenshot = async (sessionId: string) => {
    return await apiClient.captureBrowserScreenshot(sessionId);
  };

  const handleSwitchTab = async (sessionId: string, tabId: string) => {
    await apiClient.switchBrowserTab(sessionId, tabId);
    const updated = await apiClient.getBrowserSession(sessionId);
    setSelectedSession(updated);
  };

  const handleCreateTab = async (sessionId: string, url?: string) => {
    await apiClient.createBrowserTab(sessionId, { url });
    const updated = await apiClient.getBrowserSession(sessionId);
    setSelectedSession(updated);
  };

  const handleCloseTab = async (sessionId: string, tabId: string) => {
    await apiClient.closeBrowserTab(sessionId, tabId);
    const updated = await apiClient.getBrowserSession(sessionId);
    setSelectedSession(updated);
  };

  const handleInspectDOM = async (sessionId: string) => {
    return await apiClient.inspectBrowserDOM(sessionId);
  };

  const handleCreateProfile = async (req: BrowserProfileCreateRequest) => {
    await apiClient.createBrowserProfile(req);
    const list = await apiClient.listBrowserProfiles();
    setProfiles(list);
  };

  const subTabs = [
    { id: 'overview', label: 'Runtime & Sessions', icon: Layers },
    { id: 'controller', label: 'Live Controller & Canvas', icon: Globe },
    { id: 'dom', label: 'DOM & Form Inspector', icon: Code2 },
    { id: 'downloads', label: 'Downloads & Artifacts', icon: FolderDown },
    { id: 'profiles', label: 'Profiles & Vault', icon: Lock },
  ];

  return (
    <div className="space-y-6">
      {/* Sub-tab Navigation */}
      <div className="flex items-center gap-2 border-b border-border/60 pb-3">
        {subTabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = subTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setSubTab(tab.id)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {subTab === 'overview' && (
        <BrowserOverviewTab
          runtimeStatus={runtimeStatus}
          sessions={sessions}
          onRefresh={loadData}
          onLaunchSession={handleLaunchSession}
          onCloseSession={handleCloseSession}
          onSelectSession={handleSelectSession}
          isLoading={isLoading}
        />
      )}

      {subTab === 'controller' && (
        <BrowserLiveControllerTab
          session={selectedSession}
          onNavigate={handleNavigate}
          onExecuteAction={handleExecuteAction}
          onCaptureScreenshot={handleCaptureScreenshot}
          onSwitchTab={handleSwitchTab}
          onCreateTab={handleCreateTab}
          onCloseTab={handleCloseTab}
          isLoading={isLoading}
        />
      )}

      {subTab === 'dom' && (
        <BrowserDOMInspectorTab
          session={selectedSession}
          onInspectDOM={handleInspectDOM}
          onExecuteAction={handleExecuteAction}
          isLoading={isLoading}
        />
      )}

      {subTab === 'downloads' && (
        <BrowserDownloadsTab
          downloads={downloads}
          onRefresh={loadData}
          isLoading={isLoading}
        />
      )}

      {subTab === 'profiles' && (
        <BrowserProfilesTab
          profiles={profiles}
          onCreateProfile={handleCreateProfile}
          onRefresh={loadData}
          isLoading={isLoading}
        />
      )}
    </div>
  );
};
