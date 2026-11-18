import * as React from 'react';
import {
  Layers,
  Search,
  RefreshCw,
  ExternalLink,
  Minimize2,
  Maximize2,
  XSquare,
  Sparkles,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';
import type { WindowInfo, WindowManageAction } from '@autonom/shared-types';

interface DesktopWindowsTabProps {
  onSelectWindowForTree?: (windowRef: string) => void;
}

export const DesktopWindowsTab: React.FC<DesktopWindowsTabProps> = ({ onSelectWindowForTree }) => {
  const [windows, setWindows] = React.useState<WindowInfo[]>([]);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [search, setSearch] = React.useState<string>('');
  const [operatingRef, setOperatingRef] = React.useState<string | null>(null);
  const [feedback, setFeedback] = React.useState<string | null>(null);

  const fetchWindows = React.useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiClient.listDesktopWindows();
      setWindows(data);
    } catch (err) {
      console.error('Failed to list windows:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchWindows();
  }, [fetchWindows]);

  const handleManage = async (windowRef: string, action: WindowManageAction) => {
    try {
      setOperatingRef(windowRef);
      setFeedback(null);
      await apiClient.manageDesktopWindow(windowRef, action);
      setFeedback(`Action '${action}' dispatched to window ${windowRef}`);
      fetchWindows();
    } catch (err: unknown) {
      setFeedback(`Error: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setOperatingRef(null);
    }
  };

  const filtered = React.useMemo(() => {
    if (!search.trim()) return windows;
    const q = search.toLowerCase();
    return windows.filter(
      (w) =>
        w.title.toLowerCase().includes(q) ||
        w.process_name.toLowerCase().includes(q) ||
        w.window_class.toLowerCase().includes(q) ||
        w.window_ref.toLowerCase().includes(q)
    );
  }, [windows, search]);

  return (
    <div className="space-y-4">
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <CardTitle className="text-base font-semibold">Active Top-Level Windows</CardTitle>
              <CardDescription>
                Live window manager for interactive Default desktop. Inspect accessibility trees or dispatch focus and window state actions.
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <div className="relative w-64">
                <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Filter windows..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="h-8 pl-8 text-xs bg-background/50 border-border/80"
                />
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={fetchWindows}
                disabled={loading}
                className="gap-1.5 text-xs h-8"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {feedback && (
            <div className="mb-4 rounded-md border border-primary/30 bg-primary/10 p-2.5 text-xs font-mono text-foreground">
              {feedback}
            </div>
          )}

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-border/60 bg-muted/30 text-muted-foreground font-mono uppercase text-[10px]">
                <tr>
                  <th className="py-2.5 px-3">Window Title</th>
                  <th className="py-2.5 px-3">Process</th>
                  <th className="py-2.5 px-3">Class</th>
                  <th className="py-2.5 px-3">Dimensions</th>
                  <th className="py-2.5 px-3">State</th>
                  <th className="py-2.5 px-3 text-right">Window Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40 font-mono">
                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-muted-foreground">
                      No windows found matching query.
                    </td>
                  </tr>
                ) : (
                  filtered.map((win) => (
                    <tr key={win.window_ref} className="hover:bg-muted/20 transition-colors">
                      <td className="py-2.5 px-3 font-sans font-medium text-foreground max-w-[240px]">
                        <div className="flex items-center gap-1.5 truncate">
                          <Layers className="h-3.5 w-3.5 text-cyan-400 shrink-0" />
                          <span className="truncate" title={win.title}>
                            {win.title}
                          </span>
                        </div>
                        <div className="text-[10px] text-muted-foreground font-mono">{win.window_ref}</div>
                      </td>
                      <td className="py-2.5 px-3 text-muted-foreground">{win.process_name}</td>
                      <td className="py-2.5 px-3 text-muted-foreground truncate max-w-[120px]">{win.window_class}</td>
                      <td className="py-2.5 px-3 text-muted-foreground">
                        {win.bounds.width}x{win.bounds.height}
                      </td>
                      <td className="py-2.5 px-3">
                        <div className="flex flex-wrap gap-1">
                          {win.is_foreground && (
                            <Badge variant="success" className="text-[9px] px-1 py-0">
                              Foreground
                            </Badge>
                          )}
                          {win.is_minimized && (
                            <Badge variant="neutral" className="text-[9px] px-1 py-0">
                              Minimized
                            </Badge>
                          )}
                          {win.is_maximized && (
                            <Badge variant="primary" className="text-[9px] px-1 py-0">
                              Maximized
                            </Badge>
                          )}
                        </div>
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        <div className="flex items-center justify-end gap-1">
                          {onSelectWindowForTree && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => onSelectWindowForTree(win.window_ref)}
                              className="h-6 gap-1 px-1.5 text-[10px] text-cyan-400 border-cyan-500/30 hover:bg-cyan-500/10"
                              title="Inspect UI Automation Tree"
                            >
                              <Sparkles className="h-2.5 w-2.5" />
                              Inspect
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            disabled={operatingRef === win.window_ref}
                            onClick={() => handleManage(win.window_ref, 'activate')}
                            className="h-6 px-1.5 text-[10px]"
                            title="Activate Window"
                          >
                            <ExternalLink className="h-2.5 w-2.5" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            disabled={operatingRef === win.window_ref}
                            onClick={() => handleManage(win.window_ref, 'minimize')}
                            className="h-6 px-1.5 text-[10px]"
                            title="Minimize Window"
                          >
                            <Minimize2 className="h-2.5 w-2.5" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            disabled={operatingRef === win.window_ref}
                            onClick={() => handleManage(win.window_ref, 'maximize')}
                            className="h-6 px-1.5 text-[10px]"
                            title="Maximize Window"
                          >
                            <Maximize2 className="h-2.5 w-2.5" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            disabled={operatingRef === win.window_ref}
                            onClick={() => handleManage(win.window_ref, 'close')}
                            className="h-6 px-1.5 text-[10px] text-rose-400 hover:text-rose-300"
                            title="Close Window Gracefully (WM_CLOSE)"
                          >
                            <XSquare className="h-2.5 w-2.5" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
