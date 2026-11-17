import React from 'react';
import { Cpu, Cloud, Zap, Info } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { ModelInfo } from '@autonom/shared-types';

interface ModelCardProps {
  model: ModelInfo;
  isLoadedInVram?: boolean;
  onLoadModel?: (modelId: string) => Promise<void>;
  onUnloadModel?: (modelId: string) => Promise<void>;
  onInspect?: (model: ModelInfo) => void;
}

export const ModelCard: React.FC<ModelCardProps> = ({
  model,
  isLoadedInVram = false,
  onLoadModel,
  onUnloadModel,
  onInspect,
}) => {
  const [actionPending, setActionPending] = React.useState(false);

  const handleToggleLoad = async () => {
    setActionPending(true);
    try {
      if (isLoadedInVram && onUnloadModel) {
        await onUnloadModel(model.model_id);
      } else if (!isLoadedInVram && onLoadModel) {
        await onLoadModel(model.model_id);
      }
    } finally {
      setActionPending(false);
    }
  };

  const isLocal = model.provider_type === 'local';
  const priceDisplay = isLocal
    ? '$0.00 / 1M (Free Local)'
    : `$${model.pricing.input_cost_per_million.toFixed(3)} in / $${model.pricing.output_cost_per_million.toFixed(3)} out`;

  return (
    <Card className={`border transition-all ${
      isLoadedInVram
        ? 'border-cyan/60 bg-cyan/5 shadow-xs shadow-cyan/10'
        : 'border-border/60 bg-card/60 hover:border-border'
    }`}>
      <CardContent className="p-4 space-y-3">
        {/* Header */}
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              {isLocal ? (
                <Cpu className="h-4 w-4 text-cyan shrink-0" />
              ) : (
                <Cloud className="h-4 w-4 text-violet-400 shrink-0" />
              )}
              <h4 className="text-sm font-semibold text-foreground tracking-tight">
                {model.display_name}
              </h4>
            </div>
            <p className="text-[11px] font-mono text-muted-foreground">
              {model.id}
            </p>
          </div>

          <div className="flex flex-col items-end gap-1">
            <div className="flex items-center gap-1.5">
              <Badge
                variant={isLocal ? 'cyan' : 'neutral'}
                className="text-[10px] uppercase font-mono tracking-wider"
              >
                {model.provider_id}
              </Badge>
              {isLoadedInVram && (
                <Badge variant="cyan" className="text-[10px]">
                  Loaded in VRAM
                </Badge>
              )}
            </div>
            <span className="text-[10px] text-muted-foreground font-mono">
              {model.is_available ? 'Available' : 'Unavailable'}
            </span>
          </div>
        </div>

        {/* Specifications Grid */}
        <div className="grid grid-cols-2 gap-2 text-xs py-1 border-y border-border/30">
          <div>
            <span className="text-[10px] text-muted-foreground block">Context Window</span>
            <span className="font-mono text-foreground font-medium">
              {model.context_window.toLocaleString()} tokens
            </span>
          </div>
          <div>
            <span className="text-[10px] text-muted-foreground block">Max Output</span>
            <span className="font-mono text-foreground font-medium">
              {model.max_output_tokens.toLocaleString()} tokens
            </span>
          </div>
          <div>
            <span className="text-[10px] text-muted-foreground block">Pricing</span>
            <span className="font-mono text-foreground text-[11px]">
              {priceDisplay}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-muted-foreground block">
              {isLocal ? 'Quantization / Size' : 'Execution Mode'}
            </span>
            <span className="font-mono text-foreground text-[11px]">
              {isLocal
                ? model.quantization || (model.reported_size_bytes ? `${(model.reported_size_bytes / 1e9).toFixed(1)} GB` : 'Local GGUF')
                : 'Cloud API'}
            </span>
          </div>
        </div>

        {/* Capabilities Pills */}
        <div className="flex flex-wrap gap-1">
          {model.capabilities.map((cap) => (
            <span
              key={cap}
              className="text-[10px] px-1.5 py-0.5 rounded bg-secondary/50 text-secondary-foreground font-mono"
            >
              {cap}
            </span>
          ))}
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-1 gap-2">
          {onInspect && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs text-muted-foreground hover:text-foreground px-2"
              onClick={() => onInspect(model)}
            >
              <Info className="h-3 w-3 mr-1" />
              Specs & Schema
            </Button>
          )}

          {isLocal && (onLoadModel || onUnloadModel) && (
            <Button
              variant={isLoadedInVram ? 'outline' : 'primary'}
              size="sm"
              className={`h-7 text-xs px-2.5 ml-auto ${
                isLoadedInVram
                  ? 'border-rose-800/40 text-rose-400 hover:bg-rose-950/20'
                  : 'bg-cyan hover:bg-cyan/90 text-primary-foreground font-medium'
              }`}
              onClick={handleToggleLoad}
              disabled={actionPending}
            >
              <Zap className="h-3 w-3 mr-1" />
              {actionPending
                ? 'Processing...'
                : isLoadedInVram
                ? 'Unload from VRAM'
                : 'Load into VRAM'}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
