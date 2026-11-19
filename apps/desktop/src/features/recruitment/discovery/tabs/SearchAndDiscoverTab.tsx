/**
 * Tab: Search & Discover (Stage 26).
 * Trigger multi-source parallel job discovery runs.
 */

import * as React from 'react';
import { Play, CheckSquare, Square, Loader2, CheckCircle2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';
import type { JobSourceConfig, DiscoveryTaskRecord } from '@autonom/shared-types';

interface SearchAndDiscoverTabProps {
  sources: JobSourceConfig[];
  onTaskLaunched: (task: DiscoveryTaskRecord) => void;
}

export const SearchAndDiscoverTab: React.FC<SearchAndDiscoverTabProps> = ({
  sources,
  onTaskLaunched,
}) => {
  const [selectedSourceIds, setSelectedSourceIds] = React.useState<string[]>(
    sources.filter((s) => s.is_enabled).map((s) => s.id)
  );
  const [keywords, setKeywords] = React.useState('Backend, Systems, Distributed');
  const [maxPostings, setMaxPostings] = React.useState(100);
  const [isRunning, setIsRunning] = React.useState(false);
  const [lastTask, setLastTask] = React.useState<DiscoveryTaskRecord | null>(null);

  const toggleSource = (id: string) => {
    setSelectedSourceIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const selectAll = () => {
    setSelectedSourceIds(sources.filter((s) => s.is_enabled).map((s) => s.id));
  };

  const deselectAll = () => {
    setSelectedSourceIds([]);
  };

  const handleStartDiscovery = async () => {
    if (selectedSourceIds.length === 0) {
      alert('Please select at least one job source.');
      return;
    }
    try {
      setIsRunning(true);
      const kwList = keywords
        .split(',')
        .map((k) => k.trim())
        .filter(Boolean);
      const task = await apiClient.createDiscoveryTask({
        source_ids: selectedSourceIds,
        keywords: kwList,
        max_postings: maxPostings,
      });
      setLastTask(task);
      onTaskLaunched(task);
    } catch (err: any) {
      alert(`Failed to launch discovery: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold">Initiate Job Discovery Run</CardTitle>
          <CardDescription className="text-xs">
            Poll selected sources in parallel with polite rate-limiting, conditional headers, and Stage 25 policy pre-filtering.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 text-xs">
          {/* Controls */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="font-medium">Target Keywords / Roles (Informational)</label>
              <Input
                placeholder="e.g. Backend Engineer, Systems Architect"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <label className="font-medium">Max Postings per Source</label>
              <Input
                type="number"
                min={10}
                max={500}
                value={maxPostings}
                onChange={(e) => setMaxPostings(Number(e.target.value))}
              />
            </div>
          </div>

          {/* Sources Selection */}
          <div className="space-y-2 pt-2">
            <div className="flex items-center justify-between">
              <span className="font-medium">Target Sources ({selectedSourceIds.length} of {sources.length} selected)</span>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" className="h-6 text-[11px]" onClick={selectAll}>
                  Select All
                </Button>
                <Button variant="ghost" size="sm" className="h-6 text-[11px]" onClick={deselectAll}>
                  Deselect All
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 border p-3 rounded-md max-h-60 overflow-y-auto">
              {sources.map((src) => {
                const isSelected = selectedSourceIds.includes(src.id);
                return (
                  <div
                    key={src.id}
                    onClick={() => toggleSource(src.id)}
                    className={`flex items-center justify-between p-2 rounded cursor-pointer border transition-colors ${
                      isSelected ? 'bg-primary/5 border-primary/40' : 'hover:bg-muted/50 border-transparent'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      {isSelected ? (
                        <CheckSquare className="w-4 h-4 text-primary" />
                      ) : (
                        <Square className="w-4 h-4 text-muted-foreground" />
                      )}
                      <div>
                        <div className="font-medium">{src.name}</div>
                        <div className="text-[10px] text-muted-foreground">
                          {src.connector_id} • {src.official_domain}
                        </div>
                      </div>
                    </div>
                    <Badge variant="outline" className="text-[10px]">
                      {src.rate_limit_rpm} RPM
                    </Badge>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="pt-3 border-t flex items-center justify-between">
            <span className="text-muted-foreground text-[11px]">
              Invariant Notice: Partial snapshots will NOT remove or mass-close postings.
            </span>
            <Button size="sm" disabled={isRunning} onClick={handleStartDiscovery}>
              {isRunning ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Launch Discovery Task
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {lastTask && (
        <Card className="border-blue-900/50 bg-blue-950/10">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                Discovery Task Queued
              </CardTitle>
              <Badge variant="outline">{lastTask.id}</Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-1 text-xs">
            <div>
              Status: <span className="font-semibold capitalize">{lastTask.status}</span>
            </div>
            <div>
              Selected Sources: {lastTask.selected_sources.length} sources
            </div>
            <div className="text-muted-foreground">
              Monitor progress in the Tasks tab or view live discoveries in Discovered Jobs.
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
