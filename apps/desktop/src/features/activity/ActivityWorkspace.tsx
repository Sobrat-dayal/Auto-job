import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { History, Activity, Eye } from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleToolbar,
  ModuleTabs,
  ModuleDetailPanel,
  ModuleLoadingState,
  ModuleEmptyState,
  ModuleErrorState,
} from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { apiClient } from '@/lib/api-client';
import type { DashboardActivityEvent } from '@/types/dashboard';

export const ActivityWorkspace: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const getInitialTab = (): string => {
    if (location.pathname.includes('/activity/agents')) return 'agents';
    if (location.pathname.includes('/activity/tasks')) return 'tasks';
    if (location.pathname.includes('/activity/events')) return 'events';
    if (location.pathname.includes('/activity/errors')) return 'errors';
    if (location.pathname.includes('/activity/audit')) return 'audit';
    return 'timeline';
  };

  const [activeTab, setActiveTab] = React.useState<string>(getInitialTab());
  const [searchQuery, setSearchQuery] = React.useState('');
  const [selectedEvent, setSelectedEvent] = React.useState<DashboardActivityEvent | null>(null);

  const [events, setEvents] = React.useState<DashboardActivityEvent[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [isRefreshing, setIsRefreshing] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    setActiveTab(getInitialTab());
  }, [location.pathname]);

  const loadData = React.useCallback(async () => {
    setError(null);
    try {
      const res = await apiClient.getDashboardActivity(100);
      setEvents(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to query activity events.');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  React.useEffect(() => {
    loadData();
  }, [loadData]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === 'timeline') navigate('/activity/timeline');
    else navigate(`/activity/${tabId}`);
  };

  const filteredEvents = events.filter((e) => {
    const matchesSearch =
      e.event_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.task_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (e.state_transition && e.state_transition.toLowerCase().includes(searchQuery.toLowerCase()));

    if (activeTab === 'errors') {
      return matchesSearch && (e.event_type.includes('fail') || e.event_type.includes('error'));
    }
    if (activeTab === 'tasks') {
      return matchesSearch && e.task_id;
    }
    return matchesSearch;
  });

  const tabs = [
    { id: 'timeline', label: 'Timeline & History', badge: events.length },
    { id: 'agents', label: 'Agent Actions' },
    { id: 'tasks', label: 'Task Lifecycle' },
    { id: 'events', label: 'Event Envelopes' },
    {
      id: 'errors',
      label: 'Failures & Diagnostics',
      badge: events.filter((e) => e.event_type.includes('fail')).length,
    },
    { id: 'audit', label: 'Security Audit' },
  ];

  return (
    <ModulePage
      isDetailOpen={!!selectedEvent}
      detailPanel={
        selectedEvent ? (
          <ModuleDetailPanel
            title={selectedEvent.event_type}
            subtitle={selectedEvent.id}
            onClose={() => setSelectedEvent(null)}
            actions={
              <Badge variant="outline" className="text-xs font-mono">
                {selectedEvent.task_id.substring(0, 8)}...
              </Badge>
            }
          >
            <div className="space-y-5">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Task Identifier
                </span>
                <p className="mt-1 font-mono text-xs text-foreground bg-muted/40 p-2 rounded break-all">
                  {selectedEvent.task_id}
                </p>
              </div>

              {selectedEvent.state_transition && (
                <div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    State Transition
                  </span>
                  <p className="mt-1 text-xs font-mono font-medium text-primary">
                    {selectedEvent.state_transition}
                  </p>
                </div>
              )}

              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Event Metadata Payload
                </span>
                <pre className="mt-1 max-h-64 overflow-y-auto rounded-lg border border-border/80 bg-background/80 p-3 text-[11px] font-mono text-foreground">
                  {JSON.stringify(selectedEvent.metadata || {}, null, 2)}
                </pre>
              </div>

              <div className="border-t border-border/40 pt-3 text-[11px] text-muted-foreground font-mono">
                Timestamp: {new Date(selectedEvent.timestamp).toLocaleString()}
              </div>
            </div>
          </ModuleDetailPanel>
        ) : null
      }
    >
      <ModuleHeader
        title="Activity Stream & Audit Logs"
        description="Immutable SQLite event ledger, state transition tracking, and execution audit history."
        icon={History}
        stageTag="Stage 03 / 04 Persistent"
        badgeLabel={`${events.length} Events`}
        badgeVariant="outline"
      />

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={handleTabChange} />

      <ModuleToolbar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        searchPlaceholder="Filter events by type, task ID, or state..."
        onRefresh={() => {
          setIsRefreshing(true);
          loadData();
        }}
        isRefreshing={isRefreshing}
      />

      {error ? (
        <ModuleErrorState
          title="Could not load event activity"
          message={error}
          onRetry={loadData}
          isRetrying={isRefreshing}
        />
      ) : isLoading ? (
        <ModuleLoadingState rows={5} layout="table" />
      ) : filteredEvents.length === 0 ? (
        <ModuleEmptyState
          icon={Activity}
          title="No activity events recorded yet"
          description="Task dispatches, worker transitions, and system lifecycle events will appear in this real-time ledger."
        />
      ) : (
        <div className="space-y-2.5">
          {filteredEvents.map((e) => (
            <Card
              key={e.id}
              className={`cursor-pointer border border-border/60 bg-card/60 transition-all hover:border-primary/50 hover:bg-card/90 ${
                selectedEvent?.id === e.id ? 'ring-2 ring-primary border-primary' : ''
              }`}
              onClick={() => setSelectedEvent(e)}
            >
              <CardContent className="flex flex-col gap-2 p-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-primary/20 bg-primary/10 text-primary">
                    <Activity className="h-4 w-4" />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-foreground">{e.event_type}</span>
                      {e.state_transition && (
                        <Badge variant="neutral" className="text-[10px] font-mono">
                          {e.state_transition}
                        </Badge>
                      )}
                    </div>
                    <p className="truncate text-[11px] text-muted-foreground font-mono">
                      Task: {e.task_id}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0 self-end sm:self-center">
                  <span className="text-[11px] text-muted-foreground font-mono">
                    {new Date(e.timestamp).toLocaleTimeString()}
                  </span>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7 text-muted-foreground hover:text-foreground"
                    onClick={(eBtn) => {
                      eBtn.stopPropagation();
                      setSelectedEvent(e);
                    }}
                  >
                    <Eye className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </ModulePage>
  );
};

export default ActivityWorkspace;
