import * as React from 'react';
import { Search, Play, RefreshCw, Cpu } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';
import type { DesktopApplicationInfo } from '@autonom/shared-types';

export const DesktopApplicationsTab: React.FC = () => {
  const [apps, setApps] = React.useState<DesktopApplicationInfo[]>([]);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [search, setSearch] = React.useState<string>('');
  const [launchingApp, setLaunchingApp] = React.useState<string | null>(null);
  const [message, setMessage] = React.useState<string | null>(null);

  const fetchApps = React.useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiClient.listDesktopApplications();
      setApps(data);
    } catch (err) {
      console.error('Failed to list applications:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchApps();
  }, [fetchApps]);

  const handleLaunch = async (exeName: string) => {
    try {
      setLaunchingApp(exeName);
      setMessage(null);
      const win = await apiClient.launchDesktopApplication(exeName);
      if (win) {
        setMessage(`Launched ${exeName} (${win.window_ref}: "${win.title}")`);
      } else {
        setMessage(`Launched ${exeName}, checking top-level windows...`);
      }
      fetchApps();
    } catch (err: unknown) {
      setMessage(`Launch error: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLaunchingApp(null);
    }
  };

  const filtered = React.useMemo(() => {
    if (!search.trim()) return apps;
    const q = search.toLowerCase();
    return apps.filter(
      (a) =>
        a.name.toLowerCase().includes(q) ||
        a.executable_name.toLowerCase().includes(q) ||
        a.publisher?.toLowerCase().includes(q)
    );
  }, [apps, search]);

  return (
    <div className="space-y-4">
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <CardTitle className="text-base font-semibold">Running Applications Directory</CardTitle>
              <CardDescription>
                Catalog of discovered interactive desktop processes, integrity levels, and automation allowlist status.
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <div className="relative w-64">
                <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Filter applications..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="h-8 pl-8 text-xs bg-background/50 border-border/80"
                />
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={fetchApps}
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
          {message && (
            <div className="mb-4 rounded-md border border-primary/30 bg-primary/10 p-2.5 text-xs font-mono text-foreground">
              {message}
            </div>
          )}

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-border/60 bg-muted/30 text-muted-foreground font-mono uppercase text-[10px]">
                <tr>
                  <th className="py-2.5 px-3">Application</th>
                  <th className="py-2.5 px-3">Executable</th>
                  <th className="py-2.5 px-3">Instances</th>
                  <th className="py-2.5 px-3">Integrity</th>
                  <th className="py-2.5 px-3">Risk Level</th>
                  <th className="py-2.5 px-3">Allowlist Status</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40 font-mono">
                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-muted-foreground">
                      No applications found matching query.
                    </td>
                  </tr>
                ) : (
                  filtered.map((app) => (
                    <tr key={app.id} className="hover:bg-muted/20 transition-colors">
                      <td className="py-2.5 px-3 font-sans font-medium text-foreground flex items-center gap-2">
                        <Cpu className="h-3.5 w-3.5 text-cyan-400 shrink-0" />
                        <span className="truncate max-w-[160px]">{app.name}</span>
                      </td>
                      <td className="py-2.5 px-3 text-muted-foreground">{app.executable_name}</td>
                      <td className="py-2.5 px-3">
                        <Badge variant="outline" className="text-[10px]">
                          {app.pids.length} PID{app.pids.length > 1 ? 's' : ''}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3">
                        <span className="capitalize">{app.integrity_level}</span>
                      </td>
                      <td className="py-2.5 px-3">
                        <Badge
                          variant={app.risk_level === 'HIGH' ? 'error' : 'neutral'}
                          className="text-[10px]"
                        >
                          {app.risk_level}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3">
                        {app.is_allowed ? (
                          <Badge variant="success" className="text-[10px]">
                            Allowed
                          </Badge>
                        ) : (
                          <Badge variant="warning" className="text-[10px]">
                            Restricted
                          </Badge>
                        )}
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        <Button
                          variant="outline"
                          size="sm"
                          disabled={launchingApp !== null}
                          onClick={() => handleLaunch(app.executable_name)}
                          className="h-6 gap-1 px-2 text-[10px] hover:bg-primary/10 hover:border-primary/40"
                        >
                          <Play className="h-2.5 w-2.5 text-cyan-400" />
                          Launch
                        </Button>
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
