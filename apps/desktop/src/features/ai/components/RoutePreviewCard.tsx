import React from 'react';
import { Cpu, Cloud, Route } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { apiClient } from '@/lib/api-client';
import type { TaskCategory, RoutingStrategy, RoutingDecision } from '@autonom/shared-types';

const TASK_CATEGORIES: { id: TaskCategory; label: string }[] = [
  { id: 'job_description_analysis', label: 'Job Description Analysis' },
  { id: 'resume_analysis', label: 'Resume & Skill Analysis' },
  { id: 'screening_answer_drafting', label: 'Screening Answer Drafting' },
  { id: 'coding', label: 'Coding & Debugging' },
  { id: 'code_review', label: 'Code Review & Security' },
  { id: 'research_synthesis', label: 'Research & Synthesis' },
  { id: 'document_writing', label: 'Document & Cover Letter Writing' },
  { id: 'summarization', label: 'Text Summarization' },
  { id: 'structured_extraction', label: 'Structured Extraction (JSON)' },
  { id: 'classification', label: 'Category Classification' },
  { id: 'short_reasoning', label: 'Short Reasoning' },
  { id: 'complex_reasoning', label: 'Complex Multi-step Reasoning' },
  { id: 'general_conversation', label: 'General Conversation' },
  { id: 'planning', label: 'Planning & DAG Construction' },
  { id: 'vision_interpretation', label: 'Vision & Screenshot Grounding' },
  { id: 'computer_control_grounding', label: 'Computer Action Coordinate Grounding' },
];

const STRATEGIES: { id: RoutingStrategy; label: string }[] = [
  { id: 'local_first', label: 'Local-First (Privacy & Free)' },
  { id: 'cloud_first', label: 'Cloud-First' },
  { id: 'lowest_cost', label: 'Lowest Cost' },
  { id: 'lowest_latency', label: 'Lowest Latency' },
  { id: 'capability_first', label: 'Capability-First' },
  { id: 'privacy_restricted', label: 'Strict Privacy Only' },
];

export const RoutePreviewCard: React.FC = () => {
  const [category, setCategory] = React.useState<TaskCategory>('job_description_analysis');
  const [tokens, setTokens] = React.useState<number>(1200);
  const [privacyRestricted, setPrivacyRestricted] = React.useState<boolean>(false);
  const [strategy, setStrategy] = React.useState<RoutingStrategy>('local_first');
  const [decision, setDecision] = React.useState<RoutingDecision | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  const handlePreview = React.useCallback(async () => {
    setError(null);
    try {
      const res = await apiClient.previewAIRoute({
        task_category: category,
        routing_strategy: strategy,
        is_local_only: privacyRestricted,
        messages: [
          {
            role: 'user',
            content: `Simulation prompt with approximately ${tokens} tokens budget.`,
          },
        ],
      });
      setDecision(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to simulate routing decision');
    }
  }, [category, privacyRestricted, strategy, tokens]);

  React.useEffect(() => {
    handlePreview();
  }, [handlePreview]);

  return (
    <Card className="border-border/60 bg-card/60 backdrop-blur-xs">
      <CardContent className="p-4 space-y-4">
        <div className="flex items-center justify-between border-b border-border/40 pb-2.5">
          <div className="flex items-center gap-2">
            <Route className="h-4 w-4 text-cyan" />
            <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider">
              Intelligent Model Routing Simulator
            </h3>
          </div>
          <Badge variant="outline" className="text-[10px] font-mono">
            Explainable Decision Engine
          </Badge>
        </div>

        {/* Inputs */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
          <div className="space-y-1 md:col-span-2">
            <label className="text-[11px] text-muted-foreground font-medium">
              Task Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value as TaskCategory)}
              className="w-full h-8 rounded-md border border-input bg-card px-2.5 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            >
              {TASK_CATEGORIES.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-[11px] text-muted-foreground font-medium">
              Estimated Prompt Tokens
            </label>
            <input
              type="number"
              min={100}
              max={128000}
              step={500}
              value={tokens}
              onChange={(e) => setTokens(parseInt(e.target.value, 10) || 500)}
              className="w-full h-8 rounded-md border border-input bg-card px-2.5 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[11px] text-muted-foreground font-medium">
              Routing Strategy
            </label>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value as RoutingStrategy)}
              className="w-full h-8 rounded-md border border-input bg-card px-2 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            >
              {STRATEGIES.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Privacy Switch */}
        <div className="flex items-center justify-between p-2.5 rounded-lg border border-border/40 bg-secondary/20">
          <div className="space-y-0.5">
            <span className="text-xs font-medium text-foreground block">
              Strict Local-Only Privacy Boundary
            </span>
            <span className="text-[11px] text-muted-foreground block">
              Prevents cloud transmission even if the prompt exceeds local context bounds.
            </span>
          </div>
          <Switch
            checked={privacyRestricted}
            onCheckedChange={setPrivacyRestricted}
            aria-label="Toggle strict privacy boundary"
          />
        </div>

        {/* Decision Output Card */}
        {decision && (
          <div className="p-3.5 rounded-lg border border-cyan/40 bg-cyan/5 space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-cyan/20 pb-2">
              <div className="flex items-center gap-2">
                <span className="text-[11px] text-muted-foreground">Routing Outcome:</span>
                <div className="flex items-center gap-1.5">
                  {decision.is_local ? (
                    <Cpu className="h-4 w-4 text-cyan" />
                  ) : (
                    <Cloud className="h-4 w-4 text-violet-400" />
                  )}
                  <span className="text-sm font-semibold text-foreground font-mono">
                    {decision.selected_provider_id} / {decision.selected_model_id}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-1.5">
                <Badge
                  variant={decision.is_local ? 'cyan' : 'neutral'}
                  className="text-[10px] font-mono uppercase"
                >
                  {decision.is_local ? 'Zero Cloud Leak (Local)' : 'Cloud API Endpoint'}
                </Badge>
              </div>
            </div>

            <div className="space-y-1.5 text-xs">
              <div className="flex items-start gap-2">
                <span className="text-muted-foreground min-w-[90px]">Rule Applied:</span>
                <span className="font-mono text-foreground font-medium">
                  {decision.rule_applied}
                </span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-muted-foreground min-w-[90px]">Explanation:</span>
                <span className="text-foreground leading-relaxed">
                  {decision.explanation}
                </span>
              </div>
            </div>

            {/* Fallbacks */}
            {decision.fallbacks_available.length > 0 && (
              <div className="pt-2 border-t border-cyan/20 text-[11px] flex items-center gap-2 text-muted-foreground">
                <span>Fallbacks in Reserve:</span>
                <div className="flex flex-wrap gap-1">
                  {decision.fallbacks_available.map((fb) => (
                    <span
                      key={fb}
                      className="px-1.5 py-0.5 rounded bg-background/50 font-mono text-[10px] text-foreground"
                    >
                      {fb}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="p-3 rounded-lg border border-rose-800/40 bg-rose-950/20 text-xs text-rose-300">
            {error}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
