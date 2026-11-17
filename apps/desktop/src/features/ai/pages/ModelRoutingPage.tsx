import React from 'react';
import { Save, Check, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { RoutePreviewCard } from '../components/RoutePreviewCard';
import { apiClient } from '@/lib/api-client';
import type {
  ModelInfo,
  TaskCategory,
  AIRoutingPreference,
} from '@autonom/shared-types';

interface ModelRoutingPageProps {
  models: ModelInfo[];
  preferences: AIRoutingPreference[];
  onRefreshPreferences?: () => Promise<void>;
}

const CATEGORY_NAMES: Record<TaskCategory, string> = {
  general_conversation: 'General Conversation',
  short_reasoning: 'Short Reasoning',
  complex_reasoning: 'Complex Multi-step Reasoning',
  coding: 'Autonomous Coding & Scripts',
  code_review: 'Code Review & Security Analysis',
  research_synthesis: 'Research & Knowledge Synthesis',
  document_writing: 'Document & Application Drafting',
  job_description_analysis: 'Job Description Extraction & Matching',
  resume_analysis: 'Resume Parsing & Skill Scoring',
  screening_answer_drafting: 'Screening Question Formulations',
  summarization: 'Text & Log Summarization',
  structured_extraction: 'Structured JSON Entity Extraction',
  classification: 'Triage & Intent Classification',
  planning: 'Multi-Agent DAG Planning',
  vision_interpretation: 'Visual Screenshot Understanding',
  computer_control_grounding: 'Computer Action Coordinate Grounding',
};

export const ModelRoutingPage: React.FC<ModelRoutingPageProps> = ({
  models,
  preferences: initialPreferences,
  onRefreshPreferences,
}) => {
  const [prefs, setPrefs] = React.useState<AIRoutingPreference[]>(initialPreferences);
  const [dirtyCategories, setDirtyCategories] = React.useState<Set<TaskCategory>>(new Set());
  const [savingCategory, setSavingCategory] = React.useState<TaskCategory | null>(null);
  const [saveSuccessCategory, setSaveSuccessCategory] = React.useState<TaskCategory | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    setPrefs(initialPreferences);
  }, [initialPreferences]);

  const handleUpdateField = (
    category: TaskCategory,
    field: keyof AIRoutingPreference,
    value: any
  ) => {
    setPrefs((prev) =>
      prev.map((p) => {
        if (p.category === category) {
          return { ...p, [field]: value };
        }
        return p;
      })
    );
    setDirtyCategories((prev) => new Set(prev).add(category));
  };

  const handleSaveCategory = async (category: TaskCategory) => {
    const pref = prefs.find((p) => p.category === category);
    if (!pref) return;

    setSavingCategory(category);
    setError(null);
    try {
      await apiClient.updateAIRoutingPreference({
        category: pref.category,
        preferred_provider: pref.preferred_provider,
        preferred_model: pref.preferred_model,
        fallback_provider: pref.fallback_provider || undefined,
        fallback_model: pref.fallback_model || undefined,
        is_local_only: pref.is_local_only,
      });

      setDirtyCategories((prev) => {
        const next = new Set(prev);
        next.delete(category);
        return next;
      });

      setSaveSuccessCategory(category);
      setTimeout(() => setSaveSuccessCategory(null), 2500);

      if (onRefreshPreferences) {
        await onRefreshPreferences();
      }
    } catch (err: any) {
      setError(err?.message || `Failed to update preferences for ${category}`);
    } finally {
      setSavingCategory(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Interactive Simulator Card */}
      <RoutePreviewCard />

      {/* 16-Category Routing Table */}
      <Card className="border-border/60 bg-card/60 backdrop-blur-xs">
        <CardContent className="p-4 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/40 pb-2.5">
            <div>
              <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider">
                Category Routing Preferences (16 Categories)
              </h3>
              <p className="text-[11px] text-muted-foreground mt-0.5">
                Assign preferred local or cloud models for each distinct functional specialization.
              </p>
            </div>
            <Badge variant="outline" className="text-[10px] text-cyan border-cyan/30">
              Local-First Priority Active
            </Badge>
          </div>

          {error && (
            <div className="p-2.5 rounded-md bg-rose-950/20 border border-rose-800/40 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-border/50 text-[11px] text-muted-foreground font-mono">
                  <th className="py-2 px-3">Task Category</th>
                  <th className="py-2 px-3">Preferred Model</th>
                  <th className="py-2 px-3">Fallback Model</th>
                  <th className="py-2 px-3 text-center">Local Only</th>
                  <th className="py-2 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/30">
                {prefs.map((p) => {
                  const isDirty = dirtyCategories.has(p.category);
                  const isSaving = savingCategory === p.category;
                  const isSaved = saveSuccessCategory === p.category;

                  return (
                    <tr key={p.category} className="hover:bg-secondary/15 transition-colors">
                      {/* Category Label */}
                      <td className="py-2.5 px-3">
                        <span className="font-medium text-foreground block">
                          {CATEGORY_NAMES[p.category] || p.category}
                        </span>
                        <span className="font-mono text-[10px] text-muted-foreground">
                          {p.category}
                        </span>
                      </td>

                      {/* Preferred Model */}
                      <td className="py-2.5 px-3">
                        <select
                          value={`${p.preferred_provider}:${p.preferred_model}`}
                          onChange={(e) => {
                            const [prov, mod] = e.target.value.split(':');
                            handleUpdateField(p.category, 'preferred_provider', prov);
                            handleUpdateField(p.category, 'preferred_model', mod);
                          }}
                          className="h-7 w-48 rounded border border-input bg-card px-2 text-[11px] font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
                        >
                          <option value="ollama:llama3:8b">ollama:llama3:8b (Local)</option>
                          <option value="ollama:llama3.2:3b">ollama:llama3.2:3b (Local)</option>
                          <option value="ollama:qwen2.5-coder:7b">ollama:qwen2.5-coder:7b (Local)</option>
                          <option value="openai:gpt-4o">openai:gpt-4o (Cloud)</option>
                          <option value="openai:gpt-4o-mini">openai:gpt-4o-mini (Cloud)</option>
                          {models.map((m) => (
                            <option key={m.id} value={`${m.provider_id}:${m.model_id}`}>
                              {m.id}
                            </option>
                          ))}
                        </select>
                      </td>

                      {/* Fallback Model */}
                      <td className="py-2.5 px-3">
                        <select
                          value={
                            p.fallback_provider && p.fallback_model
                              ? `${p.fallback_provider}:${p.fallback_model}`
                              : ''
                          }
                          onChange={(e) => {
                            if (!e.target.value) {
                              handleUpdateField(p.category, 'fallback_provider', null);
                              handleUpdateField(p.category, 'fallback_model', null);
                            } else {
                              const [prov, mod] = e.target.value.split(':');
                              handleUpdateField(p.category, 'fallback_provider', prov);
                              handleUpdateField(p.category, 'fallback_model', mod);
                            }
                          }}
                          className="h-7 w-48 rounded border border-input bg-card px-2 text-[11px] font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
                        >
                          <option value="">None (Fail if unavailable)</option>
                          <option value="openai:gpt-4o-mini">openai:gpt-4o-mini (Cloud)</option>
                          <option value="openai:gpt-4o">openai:gpt-4o (Cloud)</option>
                          <option value="ollama:llama3:8b">ollama:llama3:8b (Local)</option>
                          {models.map((m) => (
                            <option key={`fb-${m.id}`} value={`${m.provider_id}:${m.model_id}`}>
                              {m.id}
                            </option>
                          ))}
                        </select>
                      </td>

                      {/* Local Only */}
                      <td className="py-2.5 px-3 text-center">
                        <input
                          type="checkbox"
                          checked={p.is_local_only}
                          onChange={(e) =>
                            handleUpdateField(p.category, 'is_local_only', e.target.checked)
                          }
                          className="h-4 w-4 rounded border-input text-cyan focus:ring-cyan"
                          title="Restrict strictly to local model"
                        />
                      </td>

                      {/* Action */}
                      <td className="py-2.5 px-3 text-right">
                        {isSaved ? (
                          <span className="text-[11px] text-emerald-400 font-mono inline-flex items-center gap-1">
                            <Check className="h-3 w-3" /> Saved
                          </span>
                        ) : (
                          <Button
                            variant={isDirty ? 'primary' : 'ghost'}
                            size="sm"
                            className={`h-7 px-2.5 text-xs ${
                              isDirty
                                ? 'bg-cyan hover:bg-cyan/90 text-primary-foreground font-medium'
                                : 'text-muted-foreground'
                            }`}
                            onClick={() => handleSaveCategory(p.category)}
                            disabled={!isDirty || isSaving}
                          >
                            <Save className="h-3 w-3 mr-1" />
                            {isSaving ? 'Saving...' : 'Save'}
                          </Button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
