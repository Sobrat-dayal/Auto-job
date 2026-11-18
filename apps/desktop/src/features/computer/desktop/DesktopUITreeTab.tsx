import * as React from 'react';
import {
  Layers,
  Sparkles,
  Play,
  Edit3,
  CheckSquare,
  Search,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';
import type {
  WindowInfo,
  UITreeSnapshot,
  UITreeNode,
  UIElementInfo,
  DesktopActionResult,
} from '@autonom/shared-types';

interface DesktopUITreeTabProps {
  initialWindowRef?: string;
}

export const DesktopUITreeTab: React.FC<DesktopUITreeTabProps> = ({ initialWindowRef }) => {
  const [windows, setWindows] = React.useState<WindowInfo[]>([]);
  const [selectedWindowRef, setSelectedWindowRef] = React.useState<string>(initialWindowRef || '');
  const [treeSnapshot, setTreeSnapshot] = React.useState<UITreeSnapshot | null>(null);
  const [loading, setLoading] = React.useState<boolean>(false);
  const [error, setError] = React.useState<string | null>(null);

  // Inspector state
  const [selectedElement, setSelectedElement] = React.useState<UIElementInfo | null>(null);
  const [searchFilter, setSearchFilter] = React.useState<string>('');
  const [maxDepth, setMaxDepth] = React.useState<number>(5);
  const [maxNodes, setMaxNodes] = React.useState<number>(150);

  // Action execution state
  const [inputValue, setInputValue] = React.useState<string>('');
  const [actionInProgress, setActionInProgress] = React.useState<boolean>(false);
  const [actionResult, setActionResult] = React.useState<DesktopActionResult | null>(null);

  // Load window list
  React.useEffect(() => {
    apiClient.listDesktopWindows().then((wins) => {
      setWindows(wins);
      if (!selectedWindowRef && wins.length > 0) {
        setSelectedWindowRef(wins[0].window_ref);
      }
    });
  }, []);

  const handleInspect = async () => {
    if (!selectedWindowRef) return;
    try {
      setLoading(true);
      setError(null);
      setActionResult(null);
      setSelectedElement(null);
      const snapshot = await apiClient.inspectDesktopTree(selectedWindowRef, {
        max_depth: maxDepth,
        max_nodes: maxNodes,
        view_type: 'control',
      });
      setTreeSnapshot(snapshot);
      if (snapshot.root) {
        setSelectedElement(snapshot.root.element);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async (actionType: 'invoke' | 'set_value' | 'toggle' | 'select') => {
    if (!selectedWindowRef || !selectedElement) return;
    try {
      setActionInProgress(true);
      setActionResult(null);
      const res = await apiClient.executeDesktopAction({
        action_type: actionType,
        window_ref: selectedWindowRef,
        element_ref: selectedElement.element_ref,
        locator: {
          automation_id: selectedElement.automation_id || undefined,
          name: selectedElement.name || undefined,
          control_type: selectedElement.control_type,
        },
        value: actionType === 'set_value' ? inputValue : undefined,
        verify: true,
      });
      setActionResult(res);
      // Re-inspect to reflect state mutations
      handleInspect();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setActionInProgress(false);
    }
  };

  // Flatten tree for list rendering
  const flattenedNodes = React.useMemo(() => {
    if (!treeSnapshot) return [];
    const list: Array<{ node: UITreeNode; depth: number }> = [];

    const walk = (n: UITreeNode, d: number) => {
      list.push({ node: n, depth: d });
      for (const child of n.children) {
        walk(child, d + 1);
      }
    };
    walk(treeSnapshot.root, 0);

    if (!searchFilter.trim()) return list;
    const q = searchFilter.toLowerCase();
    return list.filter(
      (item) =>
        (item.node.element.name && item.node.element.name.toLowerCase().includes(q)) ||
        (item.node.element.automation_id && item.node.element.automation_id.toLowerCase().includes(q)) ||
        item.node.element.control_type.toLowerCase().includes(q)
    );
  }, [treeSnapshot, searchFilter]);

  return (
    <div className="space-y-4">
      {/* Top Controls Bar */}
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <CardTitle className="text-base font-semibold">UI Automation Tree Inspector</CardTitle>
              <CardDescription>
                Traverse live Microsoft UI Automation controls, view accessibility hierarchies, and dispatch structural actions.
              </CardDescription>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <select
                value={selectedWindowRef}
                onChange={(e) => setSelectedWindowRef(e.target.value)}
                className="h-8 max-w-[260px] truncate rounded-md border border-border/80 bg-background/50 px-2.5 text-xs font-mono text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              >
                {windows.map((w) => (
                  <option key={w.window_ref} value={w.window_ref}>
                    {w.title.slice(0, 32)} ({w.process_name})
                  </option>
                ))}
              </select>

              <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-mono">
                <span>Depth:</span>
                <input
                  type="number"
                  min={1}
                  max={10}
                  value={maxDepth}
                  onChange={(e) => setMaxDepth(Number(e.target.value))}
                  className="h-8 w-14 rounded-md border border-border/80 bg-background/50 px-2 text-center text-xs"
                />
              </div>

              <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-mono">
                <span>Nodes:</span>
                <input
                  type="number"
                  min={10}
                  max={500}
                  value={maxNodes}
                  onChange={(e) => setMaxNodes(Number(e.target.value))}
                  className="h-8 w-16 rounded-md border border-border/80 bg-background/50 px-2 text-center text-xs"
                />
              </div>

              <Button
                variant="primary"
                size="sm"
                onClick={handleInspect}
                disabled={loading || !selectedWindowRef}
                className="gap-1.5 text-xs h-8 bg-cyan-600 hover:bg-cyan-500 text-white font-medium"
              >
                <Sparkles className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
                Inspect Tree
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {error && (
        <div className="flex items-center gap-2 rounded-md border border-destructive/40 bg-destructive/10 p-3 text-xs text-destructive">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Two-Pane View: Left Tree, Right Inspector */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Left Tree Explorer */}
        <Card className="border-border/60 bg-card/60 lg:col-span-7">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CardTitle className="text-sm font-medium">Control Hierarchy</CardTitle>
                {treeSnapshot && (
                  <Badge variant="outline" className="text-[10px] font-mono">
                    {treeSnapshot.total_nodes} nodes | ~{treeSnapshot.estimated_tokens} tokens
                  </Badge>
                )}
              </div>
              <div className="relative w-48">
                <Search className="absolute left-2 top-2 h-3 w-3 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Filter nodes..."
                  value={searchFilter}
                  onChange={(e) => setSearchFilter(e.target.value)}
                  className="h-7 pl-7 text-[11px] bg-background/50 border-border/80"
                />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {!treeSnapshot ? (
              <div className="flex flex-col items-center justify-center py-16 text-center text-muted-foreground">
                <Layers className="h-10 w-10 text-muted-foreground/40 mb-3" />
                <p className="text-xs">Select a window and click "Inspect Tree" to traverse controls.</p>
              </div>
            ) : (
              <div className="max-h-[520px] overflow-y-auto space-y-1 font-mono text-xs pr-1">
                {flattenedNodes.map(({ node, depth }) => {
                  const el = node.element;
                  const isSelected = selectedElement?.element_ref === el.element_ref;

                  return (
                    <div
                      key={el.element_ref}
                      onClick={() => setSelectedElement(el)}
                      style={{ paddingLeft: `${depth * 14}px` }}
                      className={`flex items-center justify-between rounded px-2 py-1.5 cursor-pointer transition-colors ${
                        isSelected
                          ? 'bg-cyan-500/15 border border-cyan-500/40 text-foreground'
                          : 'hover:bg-muted/30 text-muted-foreground'
                      }`}
                    >
                      <div className="flex items-center gap-1.5 truncate">
                        <span className="text-cyan-400 font-bold text-[10px]">[{el.control_type}]</span>
                        <span className="text-foreground truncate max-w-[200px]" title={el.name || ''}>
                          {el.name || '<Unnamed>'}
                        </span>
                        {el.automation_id && (
                          <span className="text-[10px] text-muted-foreground">#{el.automation_id}</span>
                        )}
                      </div>
                      <div className="flex items-center gap-1 shrink-0">
                        {el.supported_patterns.map((p) => (
                          <span
                            key={p}
                            className="rounded bg-muted/60 px-1 py-0.5 text-[9px] text-muted-foreground uppercase"
                          >
                            {p}
                          </span>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Right Element Inspector & Action Dispatcher */}
        <Card className="border-border/60 bg-card/60 lg:col-span-5">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Selected Element Inspector</CardTitle>
            <CardDescription className="text-xs">
              Properties and direct control pattern dispatch for the active element.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {!selectedElement ? (
              <div className="py-12 text-center text-xs text-muted-foreground">
                Click any element in the hierarchy tree to inspect details.
              </div>
            ) : (
              <div className="space-y-4">
                {/* Element Properties Grid */}
                <div className="rounded-md border border-border/60 bg-background/40 p-3 space-y-2 text-xs font-mono">
                  <div className="flex justify-between border-b border-border/40 pb-1.5">
                    <span className="text-muted-foreground">Control Type:</span>
                    <span className="font-semibold text-cyan-400">{selectedElement.control_type}</span>
                  </div>
                  <div className="flex justify-between border-b border-border/40 pb-1.5">
                    <span className="text-muted-foreground">Name:</span>
                    <span className="text-foreground truncate max-w-[180px]">{selectedElement.name || 'None'}</span>
                  </div>
                  <div className="flex justify-between border-b border-border/40 pb-1.5">
                    <span className="text-muted-foreground">Automation ID:</span>
                    <span className="text-foreground">{selectedElement.automation_id || 'None'}</span>
                  </div>
                  <div className="flex justify-between border-b border-border/40 pb-1.5">
                    <span className="text-muted-foreground">Class Name:</span>
                    <span className="text-muted-foreground truncate max-w-[180px]">{selectedElement.class_name || 'None'}</span>
                  </div>
                  <div className="flex justify-between border-b border-border/40 pb-1.5">
                    <span className="text-muted-foreground">Bounding Box:</span>
                    <span className="text-muted-foreground">
                      {selectedElement.bounding_box.width}x{selectedElement.bounding_box.height} at ({selectedElement.bounding_box.left}, {selectedElement.bounding_box.top})
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-border/40 pb-1.5">
                    <span className="text-muted-foreground">Enabled:</span>
                    <span className={selectedElement.is_enabled ? 'text-emerald-400' : 'text-rose-400'}>
                      {selectedElement.is_enabled ? 'True' : 'False'}
                    </span>
                  </div>
                  {selectedElement.value !== null && selectedElement.value !== undefined && (
                    <div className="flex justify-between border-b border-border/40 pb-1.5">
                      <span className="text-muted-foreground">Current Value:</span>
                      <span className="text-amber-400 font-semibold">{selectedElement.value}</span>
                    </div>
                  )}
                  {selectedElement.toggle_state && (
                    <div className="flex justify-between pb-1">
                      <span className="text-muted-foreground">Toggle State:</span>
                      <span className="text-emerald-400 font-semibold capitalize">{selectedElement.toggle_state}</span>
                    </div>
                  )}
                </div>

                {/* Supported Patterns Badges */}
                <div className="space-y-1.5">
                  <span className="text-xs font-medium text-muted-foreground">Supported Control Patterns</span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedElement.supported_patterns.length === 0 ? (
                      <span className="text-xs text-muted-foreground">No interactive patterns supported.</span>
                    ) : (
                      selectedElement.supported_patterns.map((p) => (
                        <Badge key={p} variant="primary" className="text-[10px] font-mono">
                          {p}
                        </Badge>
                      ))
                    )}
                  </div>
                </div>

                {/* Direct Action Dispatcher */}
                <div className="space-y-2.5 rounded-md border border-primary/20 bg-primary/5 p-3">
                  <span className="text-xs font-semibold text-foreground">Execute Pattern Action</span>

                  <div className="flex flex-wrap gap-2">
                    {selectedElement.supported_patterns.includes('invoke') && (
                      <Button
                        variant="primary"
                        size="sm"
                        disabled={actionInProgress}
                        onClick={() => handleExecute('invoke')}
                        className="gap-1.5 text-xs h-7 bg-cyan-600 hover:bg-cyan-500"
                      >
                        <Play className="h-3 w-3" />
                        Invoke Button
                      </Button>
                    )}

                    {selectedElement.supported_patterns.includes('toggle') && (
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={actionInProgress}
                        onClick={() => handleExecute('toggle')}
                        className="gap-1.5 text-xs h-7 border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/10"
                      >
                        <CheckSquare className="h-3 w-3" />
                        Toggle Switch/Box
                      </Button>
                    )}

                    {selectedElement.supported_patterns.includes('selection_item') && (
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={actionInProgress}
                        onClick={() => handleExecute('select')}
                        className="gap-1.5 text-xs h-7"
                      >
                        Select Item
                      </Button>
                    )}
                  </div>

                  {/* ValuePattern text field */}
                  {selectedElement.supported_patterns.includes('value') && (
                    <div className="flex items-center gap-2 pt-1">
                      <Input
                        type="text"
                        placeholder="Enter text value..."
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        className="h-7 text-xs bg-background/60"
                      />
                      <Button
                        variant="primary"
                        size="sm"
                        disabled={actionInProgress || !inputValue.trim()}
                        onClick={() => handleExecute('set_value')}
                        className="gap-1 text-xs h-7 shrink-0"
                      >
                        <Edit3 className="h-3 w-3" />
                        Set Value
                      </Button>
                    </div>
                  )}

                  {actionResult && (
                    <div className="mt-2 rounded border border-emerald-500/40 bg-emerald-500/10 p-2 text-xs font-mono text-emerald-300">
                      <div className="flex items-center gap-1.5 font-bold">
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                        <span>Action: {actionResult.action_type} ({actionResult.status})</span>
                      </div>
                      <div className="text-[10px] text-muted-foreground mt-0.5">
                        Verification: {actionResult.verification_status} | Duration: {actionResult.duration_ms.toFixed(1)}ms
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
