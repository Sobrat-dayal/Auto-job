import React from 'react';
import { Copy, Check, Terminal, Clock, Coins, Sparkles, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { TokenUsage } from '@autonom/shared-types';

interface StreamingOutputViewProps {
  content: string;
  isStreaming: boolean;
  usage?: TokenUsage | null;
  latencyMs?: number | null;
  costUsd?: number | null;
  modelUsed?: string | null;
  error?: string | null;
}

export const StreamingOutputView: React.FC<StreamingOutputViewProps> = ({
  content,
  isStreaming,
  usage,
  latencyMs,
  costUsd,
  modelUsed,
  error,
}) => {
  const [copied, setCopied] = React.useState(false);
  const scrollRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (isStreaming && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [content, isStreaming]);

  const handleCopy = async () => {
    if (!content) return;
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-lg border border-border/60 bg-card/60 backdrop-blur-xs flex flex-col h-full overflow-hidden">
      {/* Header telemetry bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 px-3.5 py-2.5 border-b border-border/40 bg-secondary/20 text-xs">
        <div className="flex items-center gap-2">
          <Terminal className="h-3.5 w-3.5 text-cyan" />
          <span className="font-semibold text-foreground tracking-wide text-[11px]">
            MODEL INFERENCE STREAM
          </span>
          {modelUsed && (
            <Badge variant="outline" className="font-mono text-[10px]">
              {modelUsed}
            </Badge>
          )}
          {isStreaming && (
            <Badge variant="cyan" className="text-[10px] animate-pulse">
              Streaming Tokens...
            </Badge>
          )}
        </div>

        <div className="flex items-center gap-3 text-[11px] font-mono text-muted-foreground">
          {latencyMs != null && (
            <div className="flex items-center gap-1">
              <Clock className="h-3 w-3 text-cyan" />
              <span>{latencyMs}ms</span>
            </div>
          )}

          {usage && (
            <div className="flex items-center gap-1">
              <Sparkles className="h-3 w-3 text-amber-400" />
              <span>
                {usage.prompt_tokens} in / {usage.completion_tokens} out ({usage.total_tokens} tok)
              </span>
            </div>
          )}

          {costUsd != null && (
            <div className="flex items-center gap-1">
              <Coins className="h-3 w-3 text-emerald-400" />
              <span className={costUsd === 0 ? 'text-emerald-400 font-semibold' : 'text-foreground'}>
                {costUsd === 0 ? '$0.00 (Free Local)' : `$${costUsd.toFixed(5)}`}
              </span>
            </div>
          )}

          <Button
            variant="ghost"
            size="sm"
            className="h-6 px-2 text-[11px] text-muted-foreground hover:text-foreground"
            onClick={handleCopy}
            disabled={!content}
          >
            {copied ? (
              <>
                <Check className="h-3 w-3 mr-1 text-emerald-400" />
                Copied
              </>
            ) : (
              <>
                <Copy className="h-3 w-3 mr-1" />
                Copy
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Content stream viewport */}
      <div
        ref={scrollRef}
        className="flex-1 p-4 overflow-y-auto font-mono text-xs text-foreground leading-relaxed whitespace-pre-wrap select-text selection:bg-cyan/30"
      >
        {content ? (
          <>
            {content}
            {isStreaming && (
              <span className="inline-block w-1.5 h-3.5 ml-1 bg-cyan animate-pulse align-middle" />
            )}
          </>
        ) : error ? (
          <div className="flex items-center gap-2 text-rose-400 p-2 rounded bg-rose-950/20 border border-rose-800/40">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        ) : (
          <span className="text-muted-foreground/60 italic">
            Output will stream here once prompt execution is initiated...
          </span>
        )}
      </div>
    </div>
  );
};
