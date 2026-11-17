import React from 'react';
import { Cpu, HardDrive, ShieldCheck, RefreshCw, Zap, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent } from '@/components/ui/card';
import { apiClient } from '@/lib/api-client';
import type { HardwareTelemetry } from '@autonom/shared-types';

interface ResourceMonitorCardProps {
  telemetry: HardwareTelemetry | null;
  isLoading?: boolean;
  onRefresh?: () => void;
  onModelUnloaded?: () => void;
}

export const ResourceMonitorCard: React.FC<ResourceMonitorCardProps> = ({
  telemetry,
  isLoading = false,
  onRefresh,
  onModelUnloaded,
}) => {
  const [unloading, setUnloading] = React.useState(false);

  const handleUnload = async () => {
    if (!telemetry?.active_local_model) return;
    setUnloading(true);
    try {
      await apiClient.unloadLocalAIModel(telemetry.active_local_model);
      if (onModelUnloaded) onModelUnloaded();
      if (onRefresh) onRefresh();
    } catch (err) {
      console.error('Failed to unload model:', err);
    } finally {
      setUnloading(false);
    }
  };

  const ramUsedGb = telemetry
    ? (telemetry.system_ram_used_mb / 1024).toFixed(1)
    : '0.0';
  const ramTotalGb = telemetry
    ? (telemetry.system_ram_total_mb / 1024).toFixed(1)
    : '16.0';
  const ramPercent = telemetry ? telemetry.system_ram_percent : 0;

  const vramUsedMb = telemetry?.gpu_vram_used_mb ?? 0;
  const vramTotalMb = telemetry?.gpu_vram_total_mb ?? 6141;
  const vramPercent = telemetry?.gpu_vram_percent ?? 0;
  const gpuName = telemetry?.gpu_name || 'NVIDIA GeForce RTX 4050 Laptop GPU';

  // RTX 4050 6GB budget threshold: 5120 MB
  const isVramHigh = vramUsedMb > 4800;

  return (
    <Card className="border-border/60 bg-card/60 backdrop-blur-xs">
      <CardContent className="p-4 space-y-3.5">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/40 pb-2.5">
          <div className="flex items-center gap-2">
            <Cpu className="h-4 w-4 text-cyan" />
            <span className="text-xs font-semibold text-foreground tracking-wide">
              HARDWARE & LOCAL VRAM TELEMETRY
            </span>
            <Badge variant="outline" className="text-[10px] text-cyan border-cyan/30">
              Single-Model VRAM Guard Active
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-muted-foreground font-mono">
              Slots: {telemetry?.active_inference_count || 0}/{telemetry?.local_concurrency_limit || 1}
            </span>
            {onRefresh && (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 text-muted-foreground hover:text-foreground"
                onClick={onRefresh}
                disabled={isLoading}
                title="Refresh telemetry"
              >
                <RefreshCw className={`h-3 w-3 ${isLoading ? 'animate-spin' : ''}`} />
              </Button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Host RAM */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <HardDrive className="h-3.5 w-3.5" />
                <span>Host System Memory</span>
              </div>
              <span className="font-mono text-foreground font-medium">
                {ramUsedGb} / {ramTotalGb} GB ({ramPercent.toFixed(0)}%)
              </span>
            </div>
            <Progress value={ramPercent} className="h-1.5" />
            <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
              <span>Available: {telemetry ? (telemetry.system_ram_available_mb / 1024).toFixed(1) : 0} GB</span>
              <span>16 GB Total Target</span>
            </div>
          </div>

          {/* GPU VRAM */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <Zap className={`h-3.5 w-3.5 ${isVramHigh ? 'text-amber-500' : 'text-cyan'}`} />
                <span className="truncate max-w-[170px]" title={gpuName}>{gpuName}</span>
              </div>
              <span className="font-mono text-foreground font-medium">
                {vramUsedMb.toLocaleString()} / {vramTotalMb.toLocaleString()} MB ({vramPercent.toFixed(0)}%)
              </span>
            </div>
            <Progress
              value={vramPercent}
              className={`h-1.5 ${isVramHigh ? '[&>div]:bg-amber-500' : '[&>div]:bg-cyan'}`}
            />
            <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
              <span>Budget Cap: 5,120 MB</span>
              <span>{telemetry?.gpu_vram_available_mb ? `${telemetry.gpu_vram_available_mb.toLocaleString()} MB Free` : 'Direct NVML'}</span>
            </div>
          </div>
        </div>

        {/* Active Loaded Model Banner */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-border/30 text-xs">
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-muted-foreground">Active Model in VRAM:</span>
            {telemetry?.active_local_model ? (
              <Badge variant="cyan" className="font-mono text-[11px] px-2 py-0.5">
                {telemetry.active_local_model}
              </Badge>
            ) : (
              <span className="font-mono text-[11px] text-muted-foreground/80 italic">
                None (Memory Clean — Ready for On-Demand Load)
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1 text-[11px] text-muted-foreground">
              <ShieldCheck className="h-3 w-3 text-emerald-400" />
              <span>OOM Crash Prevention: </span>
              <span className="text-emerald-400 font-medium">Enforced</span>
            </div>
            {telemetry?.active_local_model && (
              <Button
                variant="outline"
                size="sm"
                className="h-6 px-2 text-[11px] text-rose-400 hover:text-rose-300 border-rose-800/40 hover:bg-rose-950/30"
                onClick={handleUnload}
                disabled={unloading}
              >
                <Trash2 className="h-3 w-3 mr-1" />
                {unloading ? 'Unloading...' : 'Unload Model'}
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
