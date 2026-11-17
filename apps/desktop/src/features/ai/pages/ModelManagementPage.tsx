import React from 'react';
import { Cpu, Cloud, RefreshCw, Terminal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { ModelCard } from '../components/ModelCard';
import { ModelDetailDrawer } from '../components/ModelDetailDrawer';
import { apiClient } from '@/lib/api-client';
import type { ModelInfo, ProviderSummary } from '@autonom/shared-types';

interface ModelManagementPageProps {
  models: ModelInfo[];
  providers: ProviderSummary[];
  activeModelInVram?: string | null;
  isLoading?: boolean;
  onRefresh: () => Promise<void>;
  onLoadModel: (modelId: string) => Promise<void>;
  onUnloadModel: (modelId: string) => Promise<void>;
}

export const ModelManagementPage: React.FC<ModelManagementPageProps> = ({
  models,
  providers,
  activeModelInVram,
  isLoading = false,
  onRefresh,
  onLoadModel,
  onUnloadModel,
}) => {
  const [filter, setFilter] = React.useState<'all' | 'local' | 'cloud' | 'custom'>('all');
  const [inspectingModel, setInspectingModel] = React.useState<ModelInfo | null>(null);
  const [refreshing, setRefreshing] = React.useState(false);

  const handleManualRefresh = async () => {
    setRefreshing(true);
    try {
      await apiClient.refreshAIModels();
      await onRefresh();
    } finally {
      setRefreshing(false);
    }
  };

  const filteredModels = models.filter((m) => {
    if (filter === 'all') return true;
    if (filter === 'local') return m.provider_type === 'local';
    if (filter === 'cloud') return m.provider_type === 'cloud' && m.provider_id === 'openai';
    if (filter === 'custom') return m.provider_id === 'custom';
    return true;
  });

  const localModelsCount = models.filter((m) => m.provider_type === 'local').length;

  return (
    <div className="space-y-4">
      {/* Top Controls & Provider Status */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-card/60 p-3 rounded-lg border border-border/60">
        {/* Filter Pills */}
        <div className="flex items-center gap-1.5">
          {(['all', 'local', 'cloud', 'custom'] as const).map((tab) => (
            <Button
              key={tab}
              variant={filter === tab ? 'primary' : 'ghost'}
              size="sm"
              className={`h-7 px-3 text-xs capitalize ${
                filter === tab ? 'bg-cyan text-primary-foreground font-medium' : 'text-muted-foreground'
              }`}
              onClick={() => setFilter(tab)}
            >
              {tab === 'all'
                ? `All (${models.length})`
                : tab === 'local'
                ? `Local (${localModelsCount})`
                : tab === 'cloud'
                ? 'Cloud (OpenAI)'
                : 'Custom Endpoints'}
            </Button>
          ))}
        </div>

        {/* Refresh & Actions */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="h-7 text-xs border-border/60"
            onClick={handleManualRefresh}
            disabled={isLoading || refreshing}
          >
            <RefreshCw className={`h-3 w-3 mr-1.5 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh Discovered Models
          </Button>
        </div>
      </div>

      {/* Provider Connection Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {providers.map((p) => (
          <div
            key={p.provider_id}
            className="p-3 rounded-lg border border-border/50 bg-secondary/15 flex items-center justify-between"
          >
            <div className="space-y-0.5">
              <div className="flex items-center gap-1.5">
                {p.provider_type === 'local' ? (
                  <Cpu className="h-3.5 w-3.5 text-cyan" />
                ) : (
                  <Cloud className="h-3.5 w-3.5 text-violet-400" />
                )}
                <span className="text-xs font-semibold text-foreground">{p.display_name}</span>
              </div>
              <p className="text-[10px] text-muted-foreground font-mono">
                {p.provider_type === 'local' ? '127.0.0.1:11434' : 'HTTPS REST API'}
              </p>
            </div>
            <div className="flex items-center gap-1.5">
              <span
                className={`h-2 w-2 rounded-full ${
                  p.is_healthy ? 'bg-emerald-400' : 'bg-amber-400'
                }`}
              />
              <span className="text-[11px] font-mono text-muted-foreground capitalize">
                {p.status}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Zero Local Models Honest Notice */}
      {filter !== 'cloud' && localModelsCount === 0 && (
        <Card className="border-amber-800/40 bg-amber-950/10">
          <CardContent className="p-4 space-y-2.5">
            <div className="flex items-center gap-2 text-amber-400">
              <Terminal className="h-4 w-4" />
              <h4 className="text-xs font-semibold uppercase tracking-wide">
                No Local Models Installed in Ollama
              </h4>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Ollama is active on loopback, but zero models are currently installed in your local library.
              To enable 100% offline, free local inference optimized for your{' '}
              <strong className="text-foreground">RTX 4050 6GB Laptop GPU</strong>, pull any recommended model in PowerShell:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 pt-1 font-mono text-[11px]">
              <div className="p-2 rounded bg-background/60 border border-border/40">
                <span className="text-cyan block font-semibold">ollama pull llama3.2:3b</span>
                <span className="text-muted-foreground text-[10px]">~2.0 GB VRAM • Fast reasoning</span>
              </div>
              <div className="p-2 rounded bg-background/60 border border-border/40">
                <span className="text-cyan block font-semibold">ollama pull llama3:8b</span>
                <span className="text-muted-foreground text-[10px]">~4.7 GB VRAM • Best generalist</span>
              </div>
              <div className="p-2 rounded bg-background/60 border border-border/40">
                <span className="text-cyan block font-semibold">ollama pull qwen2.5-coder:7b</span>
                <span className="text-muted-foreground text-[10px]">~4.5 GB VRAM • Code specialist</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Models Grid */}
      {filteredModels.length === 0 ? (
        <div className="text-center py-12 border border-dashed border-border/60 rounded-lg">
          <p className="text-xs text-muted-foreground">
            No models found matching the selected filter ({filter}).
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
          {filteredModels.map((model) => (
            <ModelCard
              key={model.id}
              model={model}
              isLoadedInVram={activeModelInVram === model.model_id}
              onLoadModel={onLoadModel}
              onUnloadModel={onUnloadModel}
              onInspect={(m) => setInspectingModel(m)}
            />
          ))}
        </div>
      )}

      {/* Inspector Drawer */}
      <ModelDetailDrawer
        model={inspectingModel}
        onClose={() => setInspectingModel(null)}
      />
    </div>
  );
};
