import * as React from 'react';
import { Compass, HelpCircle, Play } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import {
  HybridActionType,
  InteractionMethod,
  InteractionTarget,
  RoutingDecisionRecord,
  SurfaceType,
  TargetType,
} from '@autonom/shared-types';

export const RoutingInspectorTab: React.FC = () => {
  const [surfaceType, setSurfaceType] = React.useState<SurfaceType>('BROWSER_DOM');
  const [targetType, setTargetType] = React.useState<TargetType>('BROWSER_ELEMENT');
  const [actionType, setActionType] = React.useState<HybridActionType>('click');
  const [targetHint, setTargetHint] = React.useState<string>('button#submit-app');
  const [preferredMethod, setPreferredMethod] = React.useState<string>('auto');

  const [loading, setLoading] = React.useState<boolean>(false);
  const [decision, setDecision] = React.useState<RoutingDecisionRecord | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  const handleSimulateRoute = async () => {
    setLoading(true);
    setError(null);
    try {
      const target: InteractionTarget = {
        target_id: 'sim_target_01',
        target_type: targetType,
        surface_type: surfaceType,
        dom_selector: surfaceType === 'BROWSER_DOM' ? targetHint : undefined,
        element_name: surfaceType === 'NATIVE_UIA' ? targetHint : undefined,
        window_handle: surfaceType === 'NATIVE_WIN32' ? 12345 : undefined,
      };

      const pref = preferredMethod === 'auto' ? undefined : (preferredMethod as InteractionMethod);

      const res = await apiClient.previewHybridRoute({
        target,
        action_type: actionType,
        preferred_method: pref,
      });
      setDecision(res);
    } catch (err: any) {
      console.error('Route preview failed:', err);
      setError(err?.message || 'Failed to simulate route');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Controls Card */}
        <Card className="border-slate-800 bg-slate-900/40">
          <CardHeader>
            <CardTitle className="text-base text-slate-100 flex items-center gap-2">
              <Compass className="h-4 w-4 text-blue-400" />
              Routing Policy Simulator
            </CardTitle>
            <CardDescription className="text-xs text-slate-400">
              Simulate deterministic method ranking, capability filtering, and explainable decisions without executing actions.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">Surface Type</label>
              <select
                value={surfaceType}
                onChange={(e) => setSurfaceType(e.target.value as SurfaceType)}
                className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:border-blue-500 focus:outline-none"
              >
                <option value="BROWSER_DOM">BROWSER_DOM (Chromium Web Page)</option>
                <option value="NATIVE_UIA">NATIVE_UIA (Desktop Windows App)</option>
                <option value="NATIVE_WIN32">NATIVE_WIN32 (Legacy Window Handle)</option>
                <option value="CUSTOM_RENDERED">CUSTOM_RENDERED (DirectX / Canvas / Games)</option>
                <option value="UNKNOWN">UNKNOWN (Unclassified Surface)</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">Target Type</label>
              <select
                value={targetType}
                onChange={(e) => setTargetType(e.target.value as TargetType)}
                className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:border-blue-500 focus:outline-none"
              >
                <option value="BROWSER_ELEMENT">BROWSER_ELEMENT</option>
                <option value="BROWSER_PAGE">BROWSER_PAGE</option>
                <option value="NATIVE_WINDOW">NATIVE_WINDOW</option>
                <option value="UIA_ELEMENT">UIA_ELEMENT</option>
                <option value="VISUAL_CAPTURE_TARGET">VISUAL_CAPTURE_TARGET</option>
                <option value="VISUAL_REGION">VISUAL_REGION</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">Action Type</label>
              <select
                value={actionType}
                onChange={(e) => setActionType(e.target.value as HybridActionType)}
                className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:border-blue-500 focus:outline-none"
              >
                <option value="click">Click</option>
                <option value="enter_text">Enter Text / Fill</option>
                <option value="navigate">Navigate URL</option>
                <option value="scroll">Scroll Content</option>
                <option value="inspect">Inspect Structure</option>
                <option value="submit">Submit Application</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">Target Hint / Locator</label>
              <Input
                value={targetHint}
                onChange={(e) => setTargetHint(e.target.value)}
                placeholder="button#submit or Window Title"
                className="h-8 border-slate-700 bg-slate-800 text-xs text-slate-200"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">Preferred Method (Optional Override)</label>
              <select
                value={preferredMethod}
                onChange={(e) => setPreferredMethod(e.target.value)}
                className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:border-blue-500 focus:outline-none"
              >
                <option value="auto">Auto (Deterministic Routing Policy)</option>
                <option value="BROWSER_DOM">Force BROWSER_DOM</option>
                <option value="WINDOWS_UIA">Force WINDOWS_UIA</option>
                <option value="WINDOWS_WIN32">Force WINDOWS_WIN32</option>
                <option value="VISUAL_GROUNDING">Force VISUAL_GROUNDING</option>
              </select>
            </div>

            <Button
              onClick={handleSimulateRoute}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 text-xs font-semibold"
            >
              <Play className="mr-2 h-3.5 w-3.5" />
              {loading ? 'Simulating...' : 'Preview Routing Decision'}
            </Button>

            {error && (
              <div className="rounded border border-red-500/30 bg-red-500/10 p-2 text-xs text-red-400">
                {error}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results Card */}
        <Card className="border-slate-800 bg-slate-900/40">
          <CardHeader>
            <CardTitle className="text-base text-slate-100 flex items-center justify-between">
              <span>Routing Decision Record</span>
              {decision && (
                <Badge variant="outline" className="border-emerald-500/30 bg-emerald-500/10 text-xs text-emerald-400">
                  Selected: {decision.selected_method}
                </Badge>
              )}
            </CardTitle>
            <CardDescription className="text-xs text-slate-400">
              Explainable selection rationale, candidate ranking scores, and filtered rejections.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {decision ? (
              <div className="space-y-4 text-xs">
                {/* Rationale Box */}
                <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3 space-y-1">
                  <span className="font-semibold text-slate-200">Selection Rationale:</span>
                  <p className="text-slate-300 leading-relaxed">{decision.rationale}</p>
                </div>

                {/* Candidate Scoring */}
                <div className="space-y-2">
                  <span className="font-semibold text-slate-200">Candidate Scoring Breakdown:</span>
                  <div className="space-y-2">
                    {Object.entries(decision.scoring || {}).map(([method, score]) => (
                      <div key={method} className="space-y-1">
                        <div className="flex justify-between font-mono text-[11px]">
                          <span className={method === decision.selected_method ? 'text-emerald-400 font-bold' : 'text-slate-400'}>
                            {method}
                          </span>
                          <span className="text-slate-300">{score} / 100</span>
                        </div>
                        <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              method === decision.selected_method ? 'bg-emerald-500' : 'bg-slate-600'
                            }`}
                            style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Rejected Methods */}
                {Object.keys(decision.rejected_methods || {}).length > 0 && (
                  <div className="space-y-1.5">
                    <span className="font-semibold text-slate-200">Filtered / Inapplicable Methods:</span>
                    <ul className="space-y-1 text-slate-400">
                      {Object.entries(decision.rejected_methods).map(([method, reason]) => (
                        <li key={method} className="rounded border border-slate-800/80 bg-slate-900/60 p-2 text-[11px]">
                          <span className="font-mono font-semibold text-amber-400">{method}:</span> {reason}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex h-48 flex-col items-center justify-center text-center text-slate-500">
                <HelpCircle className="h-8 w-8 mb-2 stroke-1" />
                <p className="text-xs">Select target parameters and click preview to inspect routing reasoning.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
