import * as React from 'react';
import {
  Clock,
  MousePointer,
  Play,
  RefreshCw,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';
import type {
  VisualActionRequest,
  VisualActionResult,
  VisualActionType,
} from '@autonom/shared-types';

export const VisualActionsTab: React.FC = () => {
  const [actionType, setActionType] = React.useState<VisualActionType>('click');
  const [targetX, setTargetX] = React.useState<number>(500);
  const [targetY, setTargetY] = React.useState<number>(500);
  const [targetElement, setTargetElement] = React.useState<string>('');
  const [textInput, setTextInput] = React.useState<string>('Hello World');
  const [keyInput, setKeyInput] = React.useState<string>('Enter');
  const [buttonChoice, setButtonChoice] = React.useState<string>('left');
  const [isExecuting, setIsExecuting] = React.useState<boolean>(false);
  const [actionResult, setActionResult] = React.useState<VisualActionResult | null>(null);
  const [actionHistory, setActionHistory] = React.useState<VisualActionResult[]>([]);

  const handleExecute = async () => {
    setIsExecuting(true);
    setActionResult(null);
    try {
      const sess = await apiClient.createVisualSession({ display_index: 0 });
      const req: VisualActionRequest = {
        action_type: actionType,
        target_point: targetElement.trim() ? undefined : { x: targetX, y: targetY },
        target_element: targetElement.trim() || undefined,
        text: actionType === 'enter_text' ? textInput : undefined,
        key: actionType === 'press_key' ? keyInput : undefined,
        button: buttonChoice,
        wait_for_render: true,
      };

      const res = await apiClient.executeVisualAction(sess.session_id, req);
      setActionResult(res);
      setActionHistory((prev) => [res, ...prev.slice(0, 19)]);
      await apiClient.closeVisualSession(sess.session_id);
    } catch (err: any) {
      console.error('Action execution failed:', err);
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Dispatcher Controls */}
      <Card className="border-border/60 bg-card/40">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <MousePointer className="h-5 w-5 text-purple-400" />
            Coordinate-Based Input Dispatcher & Visual Action Verifier
          </CardTitle>
          <CardDescription className="text-xs">
            Dispatches hardware-level mouse/keyboard SendInput events with DPI awareness, multi-monitor coordinate bounds, and post-action visual state verification.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">Action Type</label>
              <select
                value={actionType}
                onChange={(e) => setActionType(e.target.value as VisualActionType)}
                className="w-full h-9 rounded-md border border-input bg-background px-3 py-1 text-xs font-mono shadow-sm focus:outline-none focus:ring-1 focus:ring-purple-500"
              >
                <option value="click">Mouse Click</option>
                <option value="double_click">Double Click</option>
                <option value="right_click">Right Click</option>
                <option value="move">Move Cursor</option>
                <option value="enter_text">Enter Unicode Text</option>
                <option value="press_key">Press Virtual Key</option>
                <option value="scroll">Mouse Wheel Scroll</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">Target Element Query (Optional)</label>
              <Input
                placeholder="Or ground query (e.g. 'Start')"
                value={targetElement}
                onChange={(e) => setTargetElement(e.target.value)}
                className="text-xs font-mono h-9"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground">Coord X (px)</label>
                <Input
                  type="number"
                  value={targetX}
                  onChange={(e) => setTargetX(Number(e.target.value))}
                  disabled={Boolean(targetElement.trim())}
                  className="text-xs font-mono h-9"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground">Coord Y (px)</label>
                <Input
                  type="number"
                  value={targetY}
                  onChange={(e) => setTargetY(Number(e.target.value))}
                  disabled={Boolean(targetElement.trim())}
                  className="text-xs font-mono h-9"
                />
              </div>
            </div>

            <div>
              <Button
                onClick={handleExecute}
                disabled={isExecuting}
                className="w-full gap-2 bg-purple-600 hover:bg-purple-500 text-white text-xs h-9"
              >
                {isExecuting ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
                Execute & Verify
              </Button>
            </div>
          </div>

          {/* Conditional Input Parameters */}
          {actionType === 'click' && (
            <div className="space-y-1.5 pt-2">
              <label className="text-xs font-medium text-muted-foreground">Mouse Button</label>
              <select
                value={buttonChoice}
                onChange={(e) => setButtonChoice(e.target.value)}
                className="w-full h-9 rounded-md border border-input bg-background px-3 py-1 text-xs font-mono shadow-sm focus:outline-none focus:ring-1 focus:ring-purple-500"
              >
                <option value="left">Left Button</option>
                <option value="right">Right Button</option>
                <option value="middle">Middle Button</option>
              </select>
            </div>
          )}

          {actionType === 'enter_text' && (
            <div className="space-y-1.5 pt-2">
              <label className="text-xs font-medium text-muted-foreground">Text to Enter</label>
              <Input
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Enter string..."
                className="text-xs font-mono"
              />
            </div>
          )}

          {actionType === 'press_key' && (
            <div className="space-y-1.5 pt-2">
              <label className="text-xs font-medium text-muted-foreground">Virtual Key</label>
              <Input
                value={keyInput}
                onChange={(e) => setKeyInput(e.target.value)}
                placeholder="Key (e.g. Enter, Tab, Escape, F5, Backspace)..."
                className="text-xs font-mono"
              />
            </div>
          )}

          {/* Result Card */}
          {actionResult && (
            <div className="p-4 rounded-lg border border-purple-500/30 bg-purple-500/5 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge
                    variant="outline"
                    className={
                      actionResult.verification_status === 'verified'
                        ? 'border-emerald-500/40 text-emerald-400'
                        : actionResult.verification_status === 'failed'
                        ? 'border-rose-500/40 text-rose-400'
                        : 'border-amber-500/40 text-amber-400'
                    }
                  >
                    Status: {actionResult.verification_status.toUpperCase()}
                  </Badge>
                  <span className="text-xs font-mono text-foreground font-semibold">
                    {actionResult.action_type.toUpperCase()}
                  </span>
                </div>
                <div className="text-xs font-mono text-muted-foreground flex items-center gap-2">
                  <Clock className="h-3.5 w-3.5" />
                  <span>{actionResult.execution_time_ms.toFixed(1)}ms</span>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs font-mono">
                <div className="p-2 rounded bg-background/50 border border-border">
                  <span className="text-muted-foreground block text-[10px]">Visual Pixel Difference:</span>
                  <span className="font-bold text-foreground">{(actionResult.visual_difference * 100).toFixed(3)}%</span>
                </div>
                <div className="p-2 rounded bg-background/50 border border-border col-span-2">
                  <span className="text-muted-foreground block text-[10px]">Verification Telemetry:</span>
                  <span className="text-foreground">{actionResult.verification_notes || 'Action verified successfully.'}</span>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Execution History */}
      <Card className="border-border/60 bg-card/40">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            Session Action History & Verification Log
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-xs font-mono">
            {actionHistory.length === 0 && (
              <div className="text-center py-6 text-muted-foreground">
                No actions dispatched yet in this session.
              </div>
            )}
            {actionHistory.map((act, i) => (
              <div key={i} className="p-2 rounded border border-border flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-[10px] uppercase">
                    {act.action_type}
                  </Badge>
                  <span className="text-muted-foreground">{act.verification_notes}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-[11px] text-muted-foreground">
                    Diff: {(act.visual_difference * 100).toFixed(3)}%
                  </span>
                  <Badge
                    variant="outline"
                    className={
                      act.verification_status === 'verified'
                        ? 'text-emerald-400 border-emerald-500/30'
                        : 'text-amber-400 border-amber-500/30'
                    }
                  >
                    {act.verification_status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
