import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Plug, ShieldCheck, Key } from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleToolbar,
  ModuleTabs,
  ModuleUnavailableState,
  ModuleDetailPanel,
  ModuleEmptyState,
} from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { apiClient } from '@/lib/api-client';
import type { CredentialStatus } from '@autonom/shared-types';

export interface ServiceConnector {
  id: string;
  name: string;
  category: 'ai' | 'mcp' | 'platforms' | 'comms';
  description: string;
  stage: string;
  status: 'active' | 'configured' | 'unconfigured' | 'planned';
  authType: 'api_key' | 'oauth2' | 'stdio' | 'token';
}

export const CONNECTOR_CATALOG: ServiceConnector[] = [
  // AI Models
  {
    id: 'anthropic',
    name: 'Anthropic (Claude 3.5 Sonnet)',
    category: 'ai',
    description: 'Primary reasoning and code architecture LLM backend.',
    stage: 'Stage 11',
    status: 'configured',
    authType: 'api_key',
  },
  {
    id: 'openai',
    name: 'OpenAI (GPT-4o / GPT-4o Mini)',
    category: 'ai',
    description: 'Fast scraping, document parsing, and structured extraction.',
    stage: 'Stage 11',
    status: 'unconfigured',
    authType: 'api_key',
  },
  {
    id: 'google-gemini',
    name: 'Google Gemini (Gemini 1.5 Pro / Flash)',
    category: 'ai',
    description: 'High-context multimodal document analysis and visual grounding.',
    stage: 'Stage 11',
    status: 'unconfigured',
    authType: 'api_key',
  },
  {
    id: 'ollama-local',
    name: 'Local Ollama / Llama 3',
    category: 'ai',
    description: 'Zero-cloud offline local model for privacy-sensitive personal tasks.',
    stage: 'Stage 11',
    status: 'unconfigured',
    authType: 'api_key',
  },

  // MCP Servers
  {
    id: 'mcp-filesystem',
    name: 'MCP Filesystem Server',
    category: 'mcp',
    description: 'Standard Model Context Protocol local workspace filesystem tools.',
    stage: 'Stage 45',
    status: 'planned',
    authType: 'stdio',
  },
  {
    id: 'mcp-github',
    name: 'MCP GitHub Server',
    category: 'mcp',
    description: 'Repository management, pull requests, and automated review integration.',
    stage: 'Stage 45',
    status: 'planned',
    authType: 'token',
  },

  // Job Platforms
  {
    id: 'linkedin',
    name: 'LinkedIn Job Search Connector',
    category: 'platforms',
    description: 'Feed ingestion and job opportunity tracking on LinkedIn.',
    stage: 'Stage 26',
    status: 'planned',
    authType: 'oauth2',
  },
  {
    id: 'greenhouse',
    name: 'Greenhouse ATS Connector',
    category: 'platforms',
    description: 'Direct ATS job application board harvesting and status verification.',
    stage: 'Stage 26',
    status: 'planned',
    authType: 'api_key',
  },

  // Communications
  {
    id: 'email-imap',
    name: 'Email IMAP / SMTP (Gmail / O365)',
    category: 'comms',
    description: 'Encrypted email synchronization and recruiter response tracking.',
    stage: 'Stage 36',
    status: 'planned',
    authType: 'oauth2',
  },
  {
    id: 'telegram-bot',
    name: 'Telegram Bot Gateway',
    category: 'comms',
    description: 'Mobile status alerts, quick approval responses, and incident notifications.',
    stage: 'Stage 38',
    status: 'planned',
    authType: 'token',
  },
];

export const IntegrationsWorkspace: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const getInitialTab = (): string => {
    if (location.pathname.includes('/integrations/ai')) return 'ai';
    if (location.pathname.includes('/integrations/mcp')) return 'mcp';
    if (location.pathname.includes('/integrations/platforms')) return 'platforms';
    if (location.pathname.includes('/integrations/comms')) return 'comms';
    if (location.pathname.includes('/integrations/health')) return 'health';
    return 'connected';
  };

  const [activeTab, setActiveTab] = React.useState<string>(getInitialTab());
  const [searchQuery, setSearchQuery] = React.useState('');
  const [selectedConnector, setSelectedConnector] = React.useState<ServiceConnector | null>(null);

  const [vaultCredentials, setVaultCredentials] = React.useState<CredentialStatus[]>([]);
  const [isRefreshing, setIsRefreshing] = React.useState(false);

  React.useEffect(() => {
    setActiveTab(getInitialTab());
  }, [location.pathname]);

  const loadData = React.useCallback(async () => {
    try {
      const res = await apiClient.getCredentialStatus();
      setVaultCredentials(res);
    } catch {
      // Gracefully handled if backend offline
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  React.useEffect(() => {
    loadData();
  }, [loadData]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === 'connected') navigate('/integrations/connected');
    else navigate(`/integrations/${tabId}`);
  };

  const filteredConnectors = CONNECTOR_CATALOG.filter((c) => {
    const matchesSearch =
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.description.toLowerCase().includes(searchQuery.toLowerCase());

    if (activeTab === 'ai') return matchesSearch && c.category === 'ai';
    if (activeTab === 'mcp') return matchesSearch && c.category === 'mcp';
    if (activeTab === 'platforms') return matchesSearch && c.category === 'platforms';
    if (activeTab === 'comms') return matchesSearch && c.category === 'comms';
    if (activeTab === 'connected')
      return matchesSearch && (c.status === 'configured' || c.status === 'active');
    return matchesSearch;
  });

  const tabs = [
    { id: 'connected', label: 'Connected & Configured', badge: vaultCredentials.length },
    { id: 'ai', label: 'AI Model Providers' },
    { id: 'mcp', label: 'MCP Tool Servers' },
    { id: 'platforms', label: 'Job Boards & ATS' },
    { id: 'comms', label: 'Messaging & Notifications' },
    { id: 'health', label: 'Connector Health & Latency' },
  ];

  return (
    <ModulePage
      isDetailOpen={!!selectedConnector}
      detailPanel={
        selectedConnector ? (
          <ModuleDetailPanel
            title={selectedConnector.name}
            subtitle={`${selectedConnector.category.toUpperCase()} • ${selectedConnector.stage}`}
            onClose={() => setSelectedConnector(null)}
            actions={
              <Badge variant="outline" className="text-xs">
                {selectedConnector.status}
              </Badge>
            }
          >
            <div className="space-y-5">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Description
                </span>
                <p className="mt-1 text-xs text-foreground leading-relaxed">
                  {selectedConnector.description}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="rounded-lg border border-border/40 bg-background/50 p-2.5">
                  <span className="text-[10px] text-muted-foreground uppercase font-semibold">
                    Auth Type
                  </span>
                  <p className="mt-0.5 font-semibold font-mono text-foreground uppercase">
                    {selectedConnector.authType}
                  </p>
                </div>
                <div className="rounded-lg border border-border/40 bg-background/50 p-2.5">
                  <span className="text-[10px] text-muted-foreground uppercase font-semibold">
                    Stage
                  </span>
                  <p className="mt-0.5 font-semibold font-mono text-foreground">
                    {selectedConnector.stage}
                  </p>
                </div>
              </div>

              <div className="rounded-lg border border-border/80 bg-muted/30 p-3.5 text-xs text-muted-foreground">
                <div className="flex items-center gap-2 text-foreground font-semibold">
                  <ShieldCheck className="h-4 w-4 text-status-success" />
                  DPAPI Vault Storage
                </div>
                <p className="mt-1 leading-relaxed">
                  Credentials for this provider are encrypted with Windows DPAPI AES-256-GCM.
                  Unencrypted secrets are never exposed in logs or telemetry.
                </p>
              </div>

              <div className="pt-2">
                <Button
                  size="sm"
                  onClick={() => navigate('/settings/credentials')}
                  className="w-full text-xs gap-1.5"
                >
                  <Key className="h-3.5 w-3.5" />
                  Configure in Vault
                </Button>
              </div>
            </div>
          </ModuleDetailPanel>
        ) : null
      }
    >
      <ModuleHeader
        title="Integrations & Service Connectors"
        description="External AI foundation models, Model Context Protocol servers, ATS platforms, and communication channels."
        icon={Plug}
        stageTag="Stage 11 / 45 Planned"
        badgeLabel={`${vaultCredentials.length} Configured in Vault`}
        badgeVariant="outline"
      />

      <ModuleUnavailableState
        moduleName="External Service & MCP Connector Hub"
        stageTag="Stage 11 & 45"
        stageName="AI Providers & Tool Routing"
        description="Multi-provider LLM failover switches activate in Stage 11. Dynamic Model Context Protocol (MCP) server discovery and tool routing activate in Stage 45. Secure Windows DPAPI vault storage is operational below."
        plannedCapabilities={[
          'Universal multi-LLM provider routing & cost budget enforcement (Stage 11)',
          'MCP JSON-RPC standard tool discovery & execution (Stage 45)',
          'Encrypted DPAPI credential references at rest (Active)',
          'Automated connectivity health pings (Stage 11)',
        ]}
      />

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={handleTabChange} />

      <ModuleToolbar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        searchPlaceholder="Filter connectors by service name or description..."
        onRefresh={() => {
          setIsRefreshing(true);
          loadData();
        }}
        isRefreshing={isRefreshing}
      />

      {filteredConnectors.length === 0 ? (
        <ModuleEmptyState
          icon={Plug}
          title="No connectors in this category"
          description="Switch to AI Model Providers or MCP Tool Servers to view available service definitions."
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filteredConnectors.map((c) => (
            <Card
              key={c.id}
              className={`cursor-pointer border border-border/60 bg-card/60 transition-all hover:border-primary/50 hover:bg-card/90 ${
                selectedConnector?.id === c.id ? 'ring-2 ring-primary border-primary' : ''
              }`}
              onClick={() => setSelectedConnector(c)}
            >
              <CardHeader className="p-4 pb-2">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2.5">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-primary/20 bg-primary/10 text-primary">
                      <Plug className="h-4 w-4" />
                    </div>
                    <div>
                      <CardTitle className="text-sm font-semibold text-foreground">
                        {c.name}
                      </CardTitle>
                      <CardDescription className="text-xs uppercase font-mono">
                        {c.category}
                      </CardDescription>
                    </div>
                  </div>
                  <Badge variant="outline" className="text-[10px] font-mono shrink-0">
                    {c.stage}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="p-4 pt-2">
                <p className="line-clamp-2 text-xs text-muted-foreground leading-relaxed">
                  {c.description}
                </p>

                <div className="mt-4 flex items-center justify-between border-t border-border/40 pt-2 text-[11px] text-muted-foreground">
                  <span className="font-mono uppercase">{c.authType}</span>
                  <Badge
                    variant={
                      c.status === 'configured' || c.status === 'active' ? 'primary' : 'neutral'
                    }
                    className="text-[10px]"
                  >
                    {c.status}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </ModulePage>
  );
};

export default IntegrationsWorkspace;
