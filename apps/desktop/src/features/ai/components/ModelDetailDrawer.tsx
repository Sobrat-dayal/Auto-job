import React from 'react';
import { X, Cpu, Cloud, Check, ShieldCheck } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { ModelInfo } from '@autonom/shared-types';

interface ModelDetailDrawerProps {
  model: ModelInfo | null;
  onClose: () => void;
}

export const ModelDetailDrawer: React.FC<ModelDetailDrawerProps> = ({ model, onClose }) => {
  if (!model) return null;

  const isLocal = model.provider_type === 'local';

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-card border-l border-border shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="p-4 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          {isLocal ? (
            <Cpu className="h-4 w-4 text-cyan" />
          ) : (
            <Cloud className="h-4 w-4 text-violet-400" />
          )}
          <div>
            <h3 className="text-sm font-semibold text-foreground">{model.display_name}</h3>
            <p className="text-[11px] font-mono text-muted-foreground">{model.id}</p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="h-7 w-7 p-0 text-muted-foreground hover:text-foreground"
          onClick={onClose}
        >
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
        {/* Status Section */}
        <div className="p-3 rounded-lg border border-border/50 bg-secondary/20 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Provider:</span>
            <Badge variant="outline" className="font-mono text-[10px]">
              {model.provider_id.toUpperCase()} ({model.provider_type})
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Availability Status:</span>
            <span className="font-mono text-foreground font-medium">
              {model.is_available ? 'Available & Registered' : 'Offline / Unreachable'}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Last Discovered:</span>
            <span className="font-mono text-muted-foreground text-[11px]">
              {new Date(model.last_discovered_at).toLocaleString()}
            </span>
          </div>
        </div>

        {/* Token Limits */}
        <div className="space-y-2">
          <h4 className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            Token & Context Bounds
          </h4>
          <div className="grid grid-cols-2 gap-2">
            <div className="p-2.5 rounded border border-border/40 bg-card/40">
              <span className="text-[10px] text-muted-foreground block">Max Context Window</span>
              <span className="text-sm font-mono font-semibold text-foreground">
                {model.context_window.toLocaleString()}
              </span>
              <span className="text-[10px] text-muted-foreground block">total tokens</span>
            </div>
            <div className="p-2.5 rounded border border-border/40 bg-card/40">
              <span className="text-[10px] text-muted-foreground block">Max Generation Limit</span>
              <span className="text-sm font-mono font-semibold text-foreground">
                {model.max_output_tokens.toLocaleString()}
              </span>
              <span className="text-[10px] text-muted-foreground block">completion tokens</span>
            </div>
          </div>
        </div>

        {/* Pricing Specification */}
        <div className="space-y-2">
          <h4 className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            Pricing Accounting (Per 1 Million Tokens)
          </h4>
          <div className="p-3 rounded-lg border border-border/50 bg-card space-y-2 font-mono">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Input Token Cost:</span>
              <span className="text-foreground">
                ${model.pricing.input_cost_per_million.toFixed(4)} USD
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Output Token Cost:</span>
              <span className="text-foreground">
                ${model.pricing.output_cost_per_million.toFixed(4)} USD
              </span>
            </div>
            <div className="flex justify-between pt-1 border-t border-border/30 text-[11px]">
              <span className="text-muted-foreground">Cost Attribution:</span>
              <span className="text-cyan">
                {isLocal ? '100% Free / Zero Cloud Billing' : 'Charged to Provider Account'}
              </span>
            </div>
          </div>
        </div>

        {/* Capabilities Checklist */}
        <div className="space-y-2">
          <h4 className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            Supported Gateway Capabilities
          </h4>
          <div className="grid grid-cols-2 gap-2">
            {[
              'chat',
              'streaming',
              'structured_output',
              'tool_calling',
              'vision',
              'reasoning',
            ].map((cap) => {
              const supported = model.capabilities.includes(cap);
              return (
                <div
                  key={cap}
                  className={`p-2 rounded border flex items-center justify-between text-xs ${
                    supported
                      ? 'border-emerald-800/40 bg-emerald-950/10 text-foreground'
                      : 'border-border/30 bg-muted/20 text-muted-foreground line-through'
                  }`}
                >
                  <span className="font-mono">{cap}</span>
                  {supported && <Check className="h-3.5 w-3.5 text-emerald-400" />}
                </div>
              );
            })}
          </div>
        </div>

        {/* Privacy & Hardware Guarantees */}
        <div className="p-3 rounded-lg border border-cyan/30 bg-cyan/5 space-y-1.5">
          <div className="flex items-center gap-1.5 text-cyan font-medium">
            <ShieldCheck className="h-4 w-4" />
            <span>Safety & Resource Boundary</span>
          </div>
          <p className="text-[11px] text-muted-foreground leading-relaxed">
            {isLocal
              ? 'Zero-leak guarantee: All prompt tokens and inference computations run completely offline on local loopback (127.0.0.1:11434). No telemetry or user data leaves your machine.'
              : 'External Cloud API: Prompt tokens are transmitted via HTTPS to the provider. Requests marked with privacy_restricted=True will automatically bypass this model and enforce local execution.'}
          </p>
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-border flex justify-end">
        <Button variant="outline" size="sm" onClick={onClose}>
          Close
        </Button>
      </div>
    </div>
  );
};
