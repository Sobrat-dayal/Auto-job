/**
 * Stage 15: Agent Memory & Hybrid Retrieval Engine Workspace.
 */

import * as React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Brain,
  Search,
  Sparkles,
  FileCode,
  AlertTriangle,
  RefreshCw,
  Database,
  Trash2,
} from 'lucide-react';
import { ModulePage, ModuleHeader, ModuleTabs } from '@/components/module';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';
import type {
  MemoryRecord,
  MemorySearchResultItem,
  MemoryStatsResponse,
  MemoryConflict,
  ProceduralMemory,
  SearchMode,
  MemoryType,
} from '@autonom/shared-types';

export const MemoryWorkspace: React.FC = () => {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = React.useState<string>('overview');

  // Search state
  const [searchQuery, setSearchQuery] = React.useState<string>('');
  const [searchMode, setSearchMode] = React.useState<SearchMode>('hybrid');
  const [searchResults, setSearchResults] = React.useState<MemorySearchResultItem[]>([]);
  const [isSearching, setIsSearching] = React.useState<boolean>(false);

  // Filter state
  const [filterType, setFilterType] = React.useState<string>('all');
  const [selectedMemory, setSelectedMemory] = React.useState<MemoryRecord | null>(null);

  // Queries
  const { data: stats } = useQuery<MemoryStatsResponse>({
    queryKey: ['memory-stats'],
    queryFn: () => apiClient.getMemoryStatus(),
    refetchInterval: 5000,
  });

  const { data: memories = [], isLoading: memoriesLoading } = useQuery<MemoryRecord[]>({
    queryKey: ['memories-list', filterType],
    queryFn: () =>
      apiClient.listMemories(
        filterType !== 'all' ? { memory_type: filterType as MemoryType } : undefined
      ),
  });

  const { data: conflicts = [] } = useQuery<MemoryConflict[]>({
    queryKey: ['memory-conflicts'],
    queryFn: () => apiClient.listMemoryConflicts(),
  });

  const { data: procedures = [] } = useQuery<ProceduralMemory[]>({
    queryKey: ['memory-procedures'],
    queryFn: () => apiClient.listProceduralMemories(),
  });

  // Mutations
  const rebuildIndexMutation = useMutation({
    mutationFn: () => apiClient.rebuildMemoryIndex(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memory-stats'] });
      queryClient.invalidateQueries({ queryKey: ['memories-list'] });
    },
  });

  const deleteMemoryMutation = useMutation({
    mutationFn: (id: string) => apiClient.deleteMemory(id),
    onSuccess: () => {
      setSelectedMemory(null);
      queryClient.invalidateQueries({ queryKey: ['memories-list'] });
      queryClient.invalidateQueries({ queryKey: ['memory-stats'] });
    },
  });

  const resolveConflictMutation = useMutation({
    mutationFn: ({ conflictId, action }: { conflictId: string; action: string }) =>
      apiClient.resolveMemoryConflict(conflictId, { resolution_action: action }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memory-conflicts'] });
      queryClient.invalidateQueries({ queryKey: ['memory-stats'] });
    },
  });

  // Handle hybrid search
  const handleExecuteSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const res = await apiClient.searchMemory({
        query: searchQuery,
        search_mode: searchMode,
        limit: 15,
      });
      setSearchResults(res.results);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', badge: stats?.total_records },
    { id: 'explorer', label: 'Memory Explorer', badge: memories.length },
    { id: 'search', label: 'Semantic & Hybrid Search' },
    { id: 'procedural', label: 'Procedural Knowledge', badge: procedures.length },
    { id: 'conflicts', label: 'Conflict Review', badge: conflicts.length || undefined },
    { id: 'diagnostics', label: 'Index & Vector Diagnostics' },
  ];

  return (
    <ModulePage>
      <ModuleHeader
        title="Agent Memory & Knowledge Engine"
        description="Persistent episodic, semantic, working, and procedural memory with hybrid retrieval and local vector search."
        icon={Brain}
        stageTag="Stage 15 Memory Engine"
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => rebuildIndexMutation.mutate()}
              disabled={rebuildIndexMutation.isPending}
              className="text-xs h-8"
            >
              <RefreshCw
                className={`h-3.5 w-3.5 mr-1.5 ${rebuildIndexMutation.isPending ? 'animate-spin' : ''}`}
              />
              Rebuild Index
            </Button>
          </div>
        }
      />

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="p-6 space-y-6">
        {/* 1. OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="bg-card/50">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-semibold text-muted-foreground uppercase">
                    Total Stored Memories
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <span className="text-3xl font-bold font-mono text-primary">
                      {stats?.total_records ?? 0}
                    </span>
                    <Database className="h-7 w-7 text-primary/40" />
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    Durable facts across all agent scopes
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-card/50">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-semibold text-muted-foreground uppercase">
                    Active Vector Index
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <span className="text-3xl font-bold font-mono text-emerald-400">
                      {stats?.indexed_records ?? 0}
                    </span>
                    <Sparkles className="h-7 w-7 text-emerald-400/40" />
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    {stats?.vector_dimension ?? 384}-dimensional normalized vectors
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-card/50">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-semibold text-muted-foreground uppercase">
                    Reusable Procedures
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <span className="text-3xl font-bold font-mono text-indigo-400">
                      {stats?.active_procedures ?? 0}
                    </span>
                    <FileCode className="h-7 w-7 text-indigo-400/40" />
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    Validated workflow execution templates
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-card/50">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-semibold text-muted-foreground uppercase">
                    Detected Conflicts
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <span
                      className={`text-3xl font-bold font-mono ${
                        (stats?.conflicts_unresolved ?? 0) > 0 ? 'text-amber-400' : 'text-slate-400'
                      }`}
                    >
                      {stats?.conflicts_unresolved ?? 0}
                    </span>
                    <AlertTriangle className="h-7 w-7 text-amber-400/40" />
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    Contradictory claims pending review
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Memory breakdown by type */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-semibold">Memory Distribution by Type</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {[
                    {
                      label: 'Semantic Memory (Verified Facts & Skills)',
                      key: 'semantic',
                      color: 'bg-emerald-500',
                    },
                    {
                      label: 'Episodic Memory (Workflow Experiences & Lessons)',
                      key: 'episodic',
                      color: 'bg-blue-500',
                    },
                    {
                      label: 'Procedural Memory (Reusable Workflow Methods)',
                      key: 'procedural',
                      color: 'bg-indigo-500',
                    },
                    {
                      label: 'Working Memory (Ephemeral Session Context)',
                      key: 'working',
                      color: 'bg-amber-500',
                    },
                  ].map((item) => {
                    const count = stats?.by_type?.[item.key] ?? 0;
                    const total = Math.max(1, stats?.total_records ?? 1);
                    const pct = Math.round((count / total) * 100);
                    return (
                      <div key={item.key} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="font-medium text-foreground">{item.label}</span>
                          <span className="font-mono text-muted-foreground">
                            {count} ({pct}%)
                          </span>
                        </div>
                        <div className="h-2 w-full rounded-full bg-secondary/40 overflow-hidden">
                          <div
                            className={`h-full ${item.color} rounded-full transition-all`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-semibold">
                    Epistemic Verification Distribution
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {[
                    { label: 'Fully Verified & Proven', key: 'verified', color: 'bg-emerald-500' },
                    {
                      label: 'User-Confirmed Explicit Facts',
                      key: 'user_confirmed',
                      color: 'bg-blue-500',
                    },
                    {
                      label: 'Evidence-Supported Inferences',
                      key: 'evidence_supported',
                      color: 'bg-teal-500',
                    },
                    {
                      label: 'Unverified Candidate Claims',
                      key: 'unverified',
                      color: 'bg-amber-500',
                    },
                    { label: 'Superseded by Newer Records', key: 'superseded', color: 'bg-slate-500' },
                  ].map((item) => {
                    const count = stats?.by_verification_status?.[item.key] ?? 0;
                    const total = Math.max(1, stats?.total_records ?? 1);
                    const pct = Math.round((count / total) * 100);
                    return (
                      <div key={item.key} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="font-medium text-foreground">{item.label}</span>
                          <span className="font-mono text-muted-foreground">
                            {count} ({pct}%)
                          </span>
                        </div>
                        <div className="h-2 w-full rounded-full bg-secondary/40 overflow-hidden">
                          <div
                            className={`h-full ${item.color} rounded-full transition-all`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* 2. MEMORY EXPLORER TAB */}
        {activeTab === 'explorer' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-muted-foreground uppercase">Filter:</span>
                {['all', 'semantic', 'episodic', 'procedural', 'working'].map((t) => (
                  <Button
                    key={t}
                    size="sm"
                    variant={filterType === t ? 'secondary' : 'ghost'}
                    onClick={() => setFilterType(t)}
                    className="capitalize text-xs h-7"
                  >
                    {t}
                  </Button>
                ))}
              </div>
              <span className="text-xs font-mono text-muted-foreground">
                Showing {memories.length} records
              </span>
            </div>

            <div className="border border-border/40 rounded-lg overflow-hidden bg-card/30">
              <table className="w-full text-left text-xs">
                <thead className="bg-secondary/30 text-muted-foreground font-semibold border-b border-border/40">
                  <tr>
                    <th className="p-3">Title & Summary</th>
                    <th className="p-3">Type</th>
                    <th className="p-3">Scope</th>
                    <th className="p-3">Verification</th>
                    <th className="p-3">Sensitivity</th>
                    <th className="p-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/20">
                  {memoriesLoading ? (
                    <tr>
                      <td colSpan={6} className="p-8 text-center text-muted-foreground">
                        Loading memories...
                      </td>
                    </tr>
                  ) : memories.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="p-8 text-center text-muted-foreground">
                        No memories found for current filter.
                      </td>
                    </tr>
                  ) : (
                    memories.map((m) => (
                      <tr
                        key={m.id}
                        className="hover:bg-secondary/20 transition-colors cursor-pointer"
                        onClick={() => setSelectedMemory(m)}
                      >
                        <td className="p-3 max-w-md">
                          <div className="font-semibold text-foreground">{m.title}</div>
                          <div className="text-muted-foreground truncate">{m.summary || m.content}</div>
                        </td>
                        <td className="p-3">
                          <Badge variant="outline" className="text-xs uppercase font-mono">
                            {m.memory_type}
                          </Badge>
                        </td>
                        <td className="p-3">
                          <span className="font-mono text-[11px] text-muted-foreground">
                            {m.owner_scope}:{m.scope_id}
                          </span>
                        </td>
                        <td className="p-3">
                          <Badge
                            className={
                              m.verification_status === 'verified' ||
                              m.verification_status === 'user_confirmed'
                                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 uppercase font-mono text-[10px]'
                                : m.verification_status === 'superseded'
                                  ? 'bg-slate-500/20 text-slate-300 border-slate-500/40 uppercase font-mono text-[10px]'
                                  : 'bg-amber-500/20 text-amber-300 border-amber-500/40 uppercase font-mono text-[10px]'
                            }
                          >
                            {m.verification_status}
                          </Badge>
                        </td>
                        <td className="p-3">
                          <span className="font-mono text-[11px] uppercase text-slate-400">
                            {m.sensitivity_category}
                          </span>
                        </td>
                        <td className="p-3 text-right" onClick={(e) => e.stopPropagation()}>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => deleteMemoryMutation.mutate(m.id)}
                            className="h-7 w-7 p-0 text-red-400 hover:text-red-300"
                            title="Delete memory"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 3. SEMANTIC & HYBRID SEARCH TAB */}
        {activeTab === 'search' && (
          <div className="space-y-6">
            <form onSubmit={handleExecuteSearch} className="space-y-3">
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search memories via semantic intent or exact keywords (e.g. 'Rust asynchronous programming', 'salary preferences')..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9 h-10 bg-card/60"
                  />
                </div>
                <Button type="submit" disabled={isSearching || !searchQuery.trim()} className="h-10 px-6">
                  {isSearching ? 'Searching...' : 'Search'}
                </Button>
              </div>

              <div className="flex items-center gap-4 text-xs">
                <span className="font-semibold text-muted-foreground">Search Mode:</span>
                {(['hybrid', 'semantic', 'keyword'] as SearchMode[]).map((mode) => (
                  <label key={mode} className="flex items-center gap-1.5 cursor-pointer capitalize">
                    <input
                      type="radio"
                      name="searchMode"
                      value={mode}
                      checked={searchMode === mode}
                      onChange={() => setSearchMode(mode)}
                      className="text-primary"
                    />
                    <span>{mode}</span>
                  </label>
                ))}
              </div>
            </form>

            <div className="space-y-3">
              <div className="text-xs font-semibold text-muted-foreground uppercase">
                {searchResults.length > 0
                  ? `Found ${searchResults.length} relevant memories`
                  : searchQuery && !isSearching
                    ? 'No matching memories found'
                    : 'Enter a query above to test hybrid retrieval'}
              </div>

              <div className="space-y-3">
                {searchResults.map((item) => (
                  <div
                    key={item.memory_id}
                    className="p-4 rounded-lg border border-border/40 bg-card/40 hover:border-primary/50 transition-colors space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <div className="font-semibold text-foreground flex items-center gap-2">
                        {item.title}
                        <Badge
                          className={
                            item.verification_status === 'verified' ||
                            item.verification_status === 'user_confirmed'
                              ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 text-[10px]'
                              : 'bg-amber-500/20 text-amber-300 border-amber-500/40 text-[10px]'
                          }
                        >
                          {item.verification_status}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono bg-primary/20 text-primary px-2 py-0.5 rounded">
                          Score: {Math.round(item.combined_score * 100)}%
                        </span>
                        {item.similarity_score > 0 && (
                          <span className="text-[10px] font-mono text-muted-foreground">
                            Vec: {Math.round(item.similarity_score * 100)}%
                          </span>
                        )}
                        {item.keyword_score > 0 && (
                          <span className="text-[10px] font-mono text-muted-foreground">
                            KW: {Math.round(item.keyword_score * 100)}%
                          </span>
                        )}
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      {item.content_snippet}
                    </p>
                    <div className="flex items-center gap-4 text-[11px] text-muted-foreground/70 font-mono">
                      <span>Scope: {item.owner_scope}:{item.scope_id}</span>
                      <span>Type: {item.memory_type}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 4. PROCEDURAL KNOWLEDGE TAB */}
        {activeTab === 'procedural' && (
          <div className="space-y-4">
            <div className="text-xs text-muted-foreground">
              Procedural memories are validated, reusable workflow patterns extracted from successful agent executions.
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {procedures.length === 0 ? (
                <div className="p-8 text-center text-muted-foreground col-span-2 border border-border/30 rounded-lg">
                  No procedural memories registered yet. Procedures are extracted automatically from successful workflows.
                </div>
              ) : (
                procedures.map((proc) => (
                  <Card key={proc.id} className="space-y-3 bg-card/40">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-semibold">{proc.name}</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <p className="text-xs text-muted-foreground">{proc.description}</p>
                      <div className="space-y-1.5 pt-2 border-t border-border/20">
                        <div className="text-[11px] font-semibold text-slate-300">
                          Capability: <span className="font-mono text-primary">{proc.capability_id}</span>
                        </div>
                        <div className="text-[11px] font-semibold text-slate-300">
                          Workflow Steps ({proc.steps.length}):
                        </div>
                        <ol className="list-decimal list-inside text-xs text-muted-foreground space-y-1 pl-1">
                          {proc.steps.map((st, i) => (
                            <li key={i} className="truncate">
                              {String(st.name || st.action || `Step ${i + 1}`)}
                            </li>
                          ))}
                        </ol>
                      </div>
                      <div className="flex items-center justify-between text-[11px] font-mono text-muted-foreground/70 pt-2">
                        <span>Version: v{proc.version}</span>
                        <Badge variant="outline" className="text-[10px]">
                          {proc.validation_status}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </div>
        )}

        {/* 5. CONFLICT REVIEW TAB */}
        {activeTab === 'conflicts' && (
          <div className="space-y-4">
            <div className="text-xs text-muted-foreground">
              Review contradictions and differing statements detected across agent memories.
            </div>
            {conflicts.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground border border-border/30 rounded-lg">
                No active memory conflicts detected. The knowledge base is consistent.
              </div>
            ) : (
              conflicts.map((cnf) => (
                <div
                  key={cnf.id}
                  className="p-4 rounded-lg border border-amber-500/30 bg-amber-500/5 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <div className="font-semibold text-amber-400 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4" />
                      {cnf.conflict_type.toUpperCase()}: {cnf.description}
                    </div>
                    <Badge variant="outline" className="border-amber-500/40 text-amber-300 text-[10px]">
                      {cnf.status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() =>
                        resolveConflictMutation.mutate({
                          conflictId: cnf.id,
                          action: 'supersede',
                        })
                      }
                      className="text-xs h-7"
                    >
                      Supersede Older Record
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() =>
                        resolveConflictMutation.mutate({
                          conflictId: cnf.id,
                          action: 'dismiss',
                        })
                      }
                      className="text-xs h-7 text-muted-foreground"
                    >
                      Dismiss Conflict
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* 6. DIAGNOSTICS TAB */}
        {activeTab === 'diagnostics' && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-semibold">Search & Storage Subsystem Health</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 text-xs">
                  <div className="space-y-2 p-3 bg-secondary/20 rounded">
                    <div className="text-muted-foreground font-semibold">Vector Index Dimension</div>
                    <div className="text-lg font-mono text-foreground font-bold">
                      {stats?.vector_dimension ?? 384} dims (Normalized Unit Cosine)
                    </div>
                  </div>
                  <div className="space-y-2 p-3 bg-secondary/20 rounded">
                    <div className="text-muted-foreground font-semibold">SQLite FTS5 Full-Text Status</div>
                    <div className="text-lg font-mono text-emerald-400 font-bold">
                      Active & Porter-Stemmed
                    </div>
                  </div>
                  <div className="space-y-2 p-3 bg-secondary/20 rounded">
                    <div className="text-muted-foreground font-semibold">Active Local Embedding Model</div>
                    <div className="text-lg font-mono text-primary font-bold">
                      Deterministic Local MiniLM-L6 (Zero Network)
                    </div>
                  </div>
                  <div className="space-y-2 p-3 bg-secondary/20 rounded">
                    <div className="text-muted-foreground font-semibold">Pending Embedding Calculations</div>
                    <div className="text-lg font-mono text-foreground font-bold">
                      {stats?.pending_embeddings ?? 0}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      {/* Memory Detail Modal */}
      {selectedMemory && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
          onClick={() => setSelectedMemory(null)}
        >
          <div
            className="w-full max-w-2xl bg-card border border-border rounded-xl p-6 space-y-4 shadow-xl max-h-[85vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-border/40 pb-3">
              <div>
                <h3 className="text-base font-semibold text-foreground">{selectedMemory.title}</h3>
                <div className="text-xs font-mono text-muted-foreground">{selectedMemory.id}</div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedMemory(null)}
                className="h-7 w-7 p-0"
              >
                ✕
              </Button>
            </div>

            <div className="space-y-2">
              <div className="text-xs font-semibold text-muted-foreground">Content:</div>
              <div className="p-3 bg-secondary/30 rounded text-xs text-foreground whitespace-pre-wrap leading-relaxed">
                {selectedMemory.content}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <span className="text-muted-foreground">Type: </span>
                <span className="font-semibold text-foreground">{selectedMemory.memory_type}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Scope: </span>
                <span className="font-mono text-foreground">
                  {selectedMemory.owner_scope}:{selectedMemory.scope_id}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground">Verification: </span>
                <span className="font-semibold text-foreground">
                  {selectedMemory.verification_status}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground">Sensitivity: </span>
                <span className="font-semibold uppercase text-foreground">
                  {selectedMemory.sensitivity_category}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground">Created: </span>
                <span className="text-foreground">
                  {new Date(selectedMemory.created_at).toLocaleString()}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground">Version: </span>
                <span className="text-foreground">v{selectedMemory.version}</span>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t border-border/40">
              <Button
                variant="destructive"
                size="sm"
                onClick={() => deleteMemoryMutation.mutate(selectedMemory.id)}
              >
                Delete Memory
              </Button>
              <Button variant="outline" size="sm" onClick={() => setSelectedMemory(null)}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </ModulePage>
  );
};

export default MemoryWorkspace;
