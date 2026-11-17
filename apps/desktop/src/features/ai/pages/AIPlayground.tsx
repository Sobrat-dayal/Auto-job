import React from 'react';
import { Send, Square, Sliders } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent } from '@/components/ui/card';
import { StreamingOutputView } from '../components/StreamingOutputView';
import { apiClient } from '@/lib/api-client';
import type {
  ModelInfo,
  TaskCategory,
  RoutingStrategy,
  TokenUsage,
} from '@autonom/shared-types';

interface AIPlaygroundProps {
  models: ModelInfo[];
  isLoadingModels?: boolean;
}

const TASK_CATEGORIES: { id: TaskCategory; label: string }[] = [
  { id: 'general_conversation', label: 'General Conversation' },
  { id: 'job_description_analysis', label: 'Job Description Analysis' },
  { id: 'resume_analysis', label: 'Resume & Skill Analysis' },
  { id: 'screening_answer_drafting', label: 'Screening Answer Drafting' },
  { id: 'coding', label: 'Coding & Debugging' },
  { id: 'code_review', label: 'Code Review & Security' },
  { id: 'research_synthesis', label: 'Research & Synthesis' },
  { id: 'document_writing', label: 'Document & Cover Letter' },
  { id: 'summarization', label: 'Text Summarization' },
  { id: 'structured_extraction', label: 'Structured Extraction (JSON)' },
  { id: 'classification', label: 'Category Classification' },
  { id: 'short_reasoning', label: 'Short Reasoning' },
  { id: 'complex_reasoning', label: 'Complex Multi-step Reasoning' },
  { id: 'planning', label: 'Planning & DAG Construction' },
  { id: 'vision_interpretation', label: 'Vision & Screenshot Grounding' },
  { id: 'computer_control_grounding', label: 'Computer Action Coordinate Grounding' },
];

export const AIPlayground: React.FC<AIPlaygroundProps> = ({ models }) => {
  // Selection
  const [selectedModel, setSelectedModel] = React.useState<string>('auto');
  const [selectedCategory, setSelectedCategory] = React.useState<TaskCategory>('general_conversation');
  const [routingStrategy] = React.useState<RoutingStrategy>('local_first');
  const [isLocalOnly, setIsLocalOnly] = React.useState<boolean>(false);

  // Parameters
  const [temperature, setTemperature] = React.useState<number>(0.7);
  const [maxTokens, setMaxTokens] = React.useState<number>(2048);
  const [systemPrompt, setSystemPrompt] = React.useState<string>(
    'You are AUTONOM, a precise, capable, and security-conscious desktop AI assistant.'
  );
  const [userPrompt, setUserPrompt] = React.useState<string>('');

  // Execution state
  const [isStreaming, setIsStreaming] = React.useState<boolean>(false);
  const [streamContent, setStreamContent] = React.useState<string>('');
  const [activeRequestId, setActiveRequestId] = React.useState<string | null>(null);
  const [latencyMs, setLatencyMs] = React.useState<number | null>(null);
  const [tokenUsage, setTokenUsage] = React.useState<TokenUsage | null>(null);
  const [costUsd, setCostUsd] = React.useState<number | null>(null);
  const [modelUsed, setModelUsed] = React.useState<string | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const startTimeRef = React.useRef<number>(0);
  const abortCleanupRef = React.useRef<(() => void) | null>(null);

  const handleSendPrompt = () => {
    if (!userPrompt.trim() || isStreaming) return;

    setError(null);
    setStreamContent('');
    setLatencyMs(null);
    setTokenUsage(null);
    setCostUsd(null);
    setModelUsed(null);
    setIsStreaming(true);
    startTimeRef.current = Date.now();

    const providerPref = selectedModel === 'auto' ? undefined : selectedModel.split(':')[0];
    const modelPref = selectedModel === 'auto' ? undefined : selectedModel.split(':')[1];

    try {
      const cancelFn = apiClient.streamAIChat(
        {
          prompt: userPrompt,
          system_prompt: systemPrompt || undefined,
          task_category: selectedCategory,
          routing_strategy: routingStrategy,
          provider_preference: providerPref,
          model_preference: modelPref,
          temperature,
          max_tokens: maxTokens,
          is_local_only: isLocalOnly,
        },
        {
          onStart: (data: any) => {
            if (data?.request_id) setActiveRequestId(data.request_id);
            if (data?.provider_id && data?.model_id) {
              setModelUsed(`${data.provider_id}:${data.model_id}`);
            }
          },
          onDelta: (delta: string) => {
            setStreamContent((prev) => prev + delta);
          },
          onComplete: (data: any) => {
            const duration = Date.now() - startTimeRef.current;
            setLatencyMs(duration);
            if (data?.usage) setTokenUsage(data.usage);
            if (data?.estimated_cost_usd != null) setCostUsd(data.estimated_cost_usd);
            setIsStreaming(false);
            setActiveRequestId(null);
            abortCleanupRef.current = null;
          },
          onError: (err: string) => {
            setError(err);
            setIsStreaming(false);
            setActiveRequestId(null);
            abortCleanupRef.current = null;
          },
        }
      );

      abortCleanupRef.current = cancelFn;
    } catch (err: any) {
      setError(err?.message || 'Inference execution failed');
      setIsStreaming(false);
      setActiveRequestId(null);
    }
  };

  const handleStopGeneration = async () => {
    if (abortCleanupRef.current) {
      abortCleanupRef.current();
      abortCleanupRef.current = null;
    }
    if (activeRequestId) {
      try {
        await apiClient.cancelAIRequest(activeRequestId);
      } catch (err) {
        console.error('Failed to cancel request:', err);
      }
    }
    setIsStreaming(false);
    setActiveRequestId(null);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSendPrompt();
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-[calc(100vh-170px)] min-h-[550px]">
      {/* Configuration & Input Column */}
      <div className="lg:col-span-5 flex flex-col gap-3 h-full overflow-y-auto pr-1">
        {/* Routing & Model Parameters Card */}
        <Card className="border-border/60 bg-card/60 backdrop-blur-xs">
          <CardContent className="p-3.5 space-y-3">
            <div className="flex items-center justify-between border-b border-border/40 pb-2">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-foreground">
                <Sliders className="h-3.5 w-3.5 text-cyan" />
                <span>INFERENCE PARAMETERS</span>
              </div>
              <Badge variant="outline" className="text-[10px] font-mono">
                {selectedModel === 'auto' ? 'Dynamic Router' : 'Direct Binding'}
              </Badge>
            </div>

            <div className="space-y-2 text-xs">
              {/* Model Selector */}
              <div>
                <label className="text-[11px] text-muted-foreground block mb-1">
                  Target Model / Gateway Binding
                </label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full h-8 rounded-md border border-input bg-card px-2.5 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
                >
                  <option value="auto">⚡ Auto-Route by Task Category (Recommended)</option>
                  {models.map((m) => (
                    <option key={m.id} value={`${m.provider_id}:${m.model_id}`}>
                      {m.display_name} ({m.provider_id.toUpperCase()} - {m.provider_type})
                    </option>
                  ))}
                </select>
              </div>

              {/* Task Category */}
              <div>
                <label className="text-[11px] text-muted-foreground block mb-1">
                  Task Category
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value as TaskCategory)}
                  className="w-full h-8 rounded-md border border-input bg-card px-2.5 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
                >
                  {TASK_CATEGORIES.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Sliders: Temp & Max Tokens */}
              <div className="grid grid-cols-2 gap-3 pt-1">
                <div>
                  <div className="flex justify-between text-[11px] text-muted-foreground mb-1">
                    <span>Temperature</span>
                    <span className="font-mono text-foreground">{temperature.toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    className="w-full h-1.5 bg-secondary rounded-lg appearance-none cursor-pointer accent-cyan"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-[11px] text-muted-foreground mb-1">
                    <span>Max Tokens</span>
                    <span className="font-mono text-foreground">{maxTokens}</span>
                  </div>
                  <input
                    type="number"
                    min={128}
                    max={8192}
                    step={128}
                    value={maxTokens}
                    onChange={(e) => setMaxTokens(parseInt(e.target.value, 10) || 1024)}
                    className="w-full h-7 rounded border border-input bg-card px-2 font-mono text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
                  />
                </div>
              </div>

              {/* Strict Local Privacy Switch */}
              <div className="flex items-center justify-between p-2 rounded border border-border/40 bg-secondary/20 mt-1">
                <div className="space-y-0.5">
                  <span className="text-[11px] font-medium text-foreground block">
                    Strict Local-Only
                  </span>
                  <span className="text-[10px] text-muted-foreground block">
                    Never transmit to cloud
                  </span>
                </div>
                <Switch
                  checked={isLocalOnly}
                  onCheckedChange={setIsLocalOnly}
                  aria-label="Strict local only"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* System Prompt (Collapsible/Editable) */}
        <Card className="border-border/60 bg-card/60 backdrop-blur-xs">
          <CardContent className="p-3 space-y-1.5">
            <span className="text-[11px] font-medium text-muted-foreground block">
              System Instructions
            </span>
            <textarea
              rows={2}
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              placeholder="Instructions defining persona and output constraints..."
              className="w-full rounded-md border border-input bg-card p-2 text-xs text-foreground placeholder:text-muted-foreground/50 focus:outline-hidden focus:ring-1 focus:ring-primary font-mono"
            />
          </CardContent>
        </Card>

        {/* User Prompt Input */}
        <div className="flex-1 flex flex-col gap-2 min-h-[140px]">
          <textarea
            rows={5}
            value={userPrompt}
            onChange={(e) => setUserPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your prompt here... Press Ctrl+Enter to execute inference."
            className="flex-1 w-full rounded-md border border-input bg-card/80 p-3 text-xs text-foreground placeholder:text-muted-foreground/60 focus:outline-hidden focus:ring-1 focus:ring-primary resize-none font-sans"
          />

          <div className="flex items-center justify-between">
            <span className="text-[11px] text-muted-foreground font-mono">
              Ctrl+Enter to Run
            </span>

            {isStreaming ? (
              <Button
                variant="outline"
                size="sm"
                className="border-rose-800/50 text-rose-400 hover:bg-rose-950/20 h-8 px-4"
                onClick={handleStopGeneration}
              >
                <Square className="h-3.5 w-3.5 mr-1.5 fill-current" />
                Stop Generation
              </Button>
            ) : (
              <Button
                size="sm"
                className="bg-cyan hover:bg-cyan/90 text-primary-foreground h-8 px-4 font-medium"
                onClick={handleSendPrompt}
                disabled={!userPrompt.trim()}
              >
                <Send className="h-3.5 w-3.5 mr-1.5" />
                Send Prompt
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Output Stream Column */}
      <div className="lg:col-span-7 h-full">
        <StreamingOutputView
          content={streamContent}
          isStreaming={isStreaming}
          usage={tokenUsage}
          latencyMs={latencyMs}
          costUsd={costUsd}
          modelUsed={modelUsed}
          error={error}
        />
      </div>
    </div>
  );
};
