import * as React from 'react';
import {
  Save,
  AlertTriangle,
  Lock,
  Layers,
  Sliders,
  Shield,
  FileCheck,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type { ReusableProcedure } from '@autonom/shared-types';

interface ProcedureEditorTabProps {
  procedure: ReusableProcedure | null;
  onProcedureUpdated?: (updated: ReusableProcedure) => void;
}

export const ProcedureEditorTab: React.FC<ProcedureEditorTabProps> = ({
  procedure,
  onProcedureUpdated,
}) => {
  const [currentProc, setCurrentProc] = React.useState<ReusableProcedure | null>(procedure);
  const [isSaving, setIsSaving] = React.useState<boolean>(false);
  const [message, setMessage] = React.useState<string | null>(null);

  React.useEffect(() => {
    setCurrentProc(procedure);
  }, [procedure]);

  if (!currentProc) {
    return (
      <Card className="border-border/60 bg-card/60" data-testid="procedure-editor-empty">
        <CardContent className="py-12 text-center text-slate-400 text-xs">
          No procedure selected. Select a procedure from the Library or compile a new one from the Recording Studio.
        </CardContent>
      </Card>
    );
  }

  const handleSaveDraft = async () => {
    if (!currentProc) return;
    setIsSaving(true);
    setMessage(null);
    try {
      const updated = await apiClient.updateProcedureDraft(currentProc.procedure_id, currentProc);
      setCurrentProc(updated);
      onProcedureUpdated?.(updated);
      setMessage(`Draft v${updated.version} saved successfully.`);
    } catch (err: any) {
      setMessage(`Save error: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handlePublish = async () => {
    if (!currentProc) return;
    setIsSaving(true);
    setMessage(null);
    try {
      const published = await apiClient.publishProcedureVersion(currentProc.procedure_id);
      setCurrentProc(published);
      onProcedureUpdated?.(published);
      setMessage(`Procedure v${published.version} published! It is now immutable.`);
    } catch (err: any) {
      setMessage(`Publish error: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="procedure-editor-tab">
      {/* Editor Header Bar */}
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <CardTitle className="text-base font-semibold text-slate-100">{currentProc.name}</CardTitle>
                <Badge variant="outline" className="font-mono text-xs">
                  v{currentProc.version}
                </Badge>
                {currentProc.is_draft ? (
                  <Badge variant="outline" className="border-amber-500/40 text-amber-400 bg-amber-500/10 text-xs">
                    EDITABLE DRAFT
                  </Badge>
                ) : (
                  <Badge variant="outline" className="border-emerald-500/40 text-emerald-400 bg-emerald-500/10 text-xs flex items-center gap-1">
                    <Lock className="h-3 w-3" /> IMMUTABLE PUBLISHED
                  </Badge>
                )}
              </div>
              <CardDescription className="text-xs font-mono mt-0.5">
                ID: {currentProc.procedure_id} • Category: {currentProc.category}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              {currentProc.is_draft ? (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleSaveDraft}
                    disabled={isSaving}
                    className="h-8 text-xs gap-1"
                    data-testid="save-draft-btn"
                  >
                    <Save className="h-3.5 w-3.5" />
                    Save Draft
                  </Button>
                  <Button
                    size="sm"
                    onClick={handlePublish}
                    disabled={isSaving}
                    className="h-8 text-xs gap-1 bg-emerald-600 hover:bg-emerald-700 text-white"
                    data-testid="publish-procedure-btn"
                  >
                    <FileCheck className="h-3.5 w-3.5" />
                    Publish Version
                  </Button>
                </>
              ) : (
                <span className="text-xs text-slate-400 font-mono italic">
                  Published versions cannot be edited. Branch a new draft to make modifications.
                </span>
              )}
            </div>
          </div>
        </CardHeader>
        {message && (
          <CardContent className="pt-0">
            <div className="text-xs p-2 rounded bg-slate-800/80 border border-slate-700 text-slate-300 font-mono">
              {message}
            </div>
          </CardContent>
        )}
      </Card>

      {/* Grid: Parameters & Risk Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Parameters Specification */}
        <Card className="border-border/60 bg-card/60 lg:col-span-2">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Sliders className="h-4 w-4 text-purple-400" />
              Procedure Parameters ({currentProc.parameters.length})
            </CardTitle>
            <CardDescription className="text-xs">
              Dynamic inputs injected during replay using placeholder substitution syntax (e.g. &#123;&#123;param_name&#125;&#125;).
            </CardDescription>
          </CardHeader>
          <CardContent>
            {currentProc.parameters.length === 0 ? (
              <div className="text-center py-6 text-slate-400 text-xs">
                No parameters declared. Steps execute with static input parameters.
              </div>
            ) : (
              <div className="space-y-2">
                {currentProc.parameters.map((param) => (
                  <div
                    key={param.name}
                    className="flex items-center justify-between p-2.5 rounded border border-slate-800 bg-slate-900/50 text-xs font-mono"
                    data-testid={`parameter-row-${param.name}`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-blue-400">&#123;&#123;{param.name}&#125;&#125;</span>
                      <Badge variant="outline" className="text-[10px] uppercase">
                        {param.type}
                      </Badge>
                      {param.required && (
                        <Badge variant="outline" className="border-red-500/30 text-red-400 text-[10px]">
                          Required
                        </Badge>
                      )}
                      {param.is_secret && (
                        <Badge variant="outline" className="border-amber-500/30 text-amber-400 text-[10px] flex items-center gap-0.5">
                          <Lock className="h-2.5 w-2.5" /> Secret
                        </Badge>
                      )}
                    </div>
                    <div className="text-slate-400 text-[11px]">
                      Default: <span className="text-slate-200">{String(param.default_value ?? 'None')}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Risk & Safety Analysis Panel */}
        <Card className="border-border/60 bg-card/60">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Shield className="h-4 w-4 text-emerald-400" />
              Safety & Static Risk Audit
            </CardTitle>
            <CardDescription className="text-xs">
              Automated static analysis of step destructive potential and side-effect categories.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-2.5 rounded border border-slate-800 bg-slate-900/40">
              <span className="text-slate-300">Static Risk Score</span>
              <span className="font-mono font-bold text-sm text-slate-100">
                {currentProc.static_risk_score} / 100
              </span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded border border-slate-800 bg-slate-900/40">
              <span className="text-slate-300">Validation Status</span>
              <Badge variant="outline" className="font-mono text-[10px] uppercase text-emerald-400 border-emerald-500/30">
                {currentProc.validation_status}
              </Badge>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded border border-slate-800 bg-slate-900/40">
              <span className="text-slate-300">Required Permissions</span>
              <span className="font-mono text-[11px] text-slate-400">
                {currentProc.required_permissions.length || 0} scopes
              </span>
            </div>
            {currentProc.validation_issues.length > 0 && (
              <div className="p-2 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[11px]">
                <div className="font-semibold flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" /> Potential Issues:
                </div>
                <ul className="list-disc pl-4 mt-1 space-y-0.5">
                  {currentProc.validation_issues.map((iss, i) => (
                    <li key={i}>{iss}</li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Steps Sequence Inspector & Editor */}
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <Layers className="h-4 w-4 text-cyan-400" />
            Execution Steps Sequence ({currentProc.steps.length} steps)
          </CardTitle>
          <CardDescription className="text-xs">
            Declarative operations executed during state-aware replay with dynamic target re-resolution.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {currentProc.steps.map((step) => (
              <div
                key={step.step_id}
                className="p-3.5 rounded border border-slate-800 bg-slate-900/50 space-y-2 text-xs"
                data-testid={`step-row-${step.order_index}`}
              >
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-slate-400 w-5">#{step.order_index}</span>
                    <span className="font-semibold text-slate-200">{step.name}</span>
                    <Badge variant="outline" className="font-mono text-[10px] uppercase text-cyan-400 border-cyan-500/30">
                      {step.target_surface}
                    </Badge>
                    <span className="font-mono text-slate-400 text-[11px]">[{step.action_type}]</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant="outline"
                      className={`font-mono text-[10px] ${
                        step.side_effect_class === 'read_only'
                          ? 'text-blue-400 border-blue-500/30'
                          : step.side_effect_class === 'idempotent'
                          ? 'text-emerald-400 border-emerald-500/30'
                          : 'text-amber-400 border-amber-500/30'
                      }`}
                    >
                      {step.side_effect_class}
                    </Badge>
                    <Badge variant="outline" className="font-mono text-[10px] text-slate-400 border-slate-700">
                      {step.checkpoint_policy}
                    </Badge>
                    <span className="font-mono text-slate-500 text-[11px]">
                      {step.timeout_ms}ms • retries: {step.max_retries}
                    </span>
                  </div>
                </div>

                {/* Input Bindings & Locators */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                  <div className="p-2 rounded bg-slate-950/60 border border-slate-800/80 font-mono text-[11px]">
                    <div className="text-slate-400 mb-1 font-sans font-medium text-xs">Target Locator:</div>
                    <pre className="text-slate-300 overflow-x-auto whitespace-pre-wrap">
                      {JSON.stringify(step.locator_schema, null, 2)}
                    </pre>
                  </div>
                  <div className="p-2 rounded bg-slate-950/60 border border-slate-800/80 font-mono text-[11px]">
                    <div className="text-slate-400 mb-1 font-sans font-medium text-xs">Input Bindings:</div>
                    <pre className="text-slate-300 overflow-x-auto whitespace-pre-wrap">
                      {JSON.stringify(step.input_bindings, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
