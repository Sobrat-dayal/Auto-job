import * as React from 'react';
import { Bot, Cpu } from 'lucide-react';
import { SectionHeader } from '@/components/layout/SectionHeader';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AgentOperationCard } from './AgentOperationCard';
import type { AgentOperationStatus, DashboardWorkersStatus } from '@/types/dashboard';

interface AgentOperationsPanelProps {
  agents: AgentOperationStatus[];
  workers?: DashboardWorkersStatus;
  isConnected: boolean;
  onInspectAgent?: (agentId: string) => void;
  onNavigateToDiagnostics?: () => void;
}

export const AgentOperationsPanel: React.FC<AgentOperationsPanelProps> = ({
  agents,
  workers,
  isConnected,
  onInspectAgent,
  onNavigateToDiagnostics,
}) => {
  return (
    <div className="space-y-3">
      <SectionHeader
        title="Autonomous Agent Fleet & Worker Pool"
        subtitle="Operational supervision across AI agent roles and active Python background worker execution threads"
        icon={<Bot className="w-4 h-4 text-accent-cyan" />}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3.5">
        {/* 3 Prominent Agent Cards */}
        {agents.map((agent) => (
          <AgentOperationCard key={agent.id} agent={agent} onInspect={onInspectAgent} />
        ))}

        {/* 4th Distinct Card: Real Background Worker Manager (Stage 03 / Real Execution) */}
        <Card className="border-border/60 bg-surface/50 flex flex-col justify-between select-none">
          <CardHeader className="p-4 pb-2 space-y-2">
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shrink-0">
                  <Cpu className="h-4 w-4" />
                </div>
                <div className="min-w-0">
                  <CardTitle className="text-sm font-semibold text-foreground truncate">
                    Worker Thread Pool
                  </CardTitle>
                  <CardDescription className="text-[11px] text-foreground-muted truncate">
                    Stage 03 Background Executor
                  </CardDescription>
                </div>
              </div>

              <Badge
                variant={isConnected ? 'success' : 'error'}
                dot
                pulse={isConnected}
                className="text-[10px]"
              >
                {isConnected ? 'ONLINE' : 'OFFLINE'}
              </Badge>
            </div>

            <p className="text-[11px] text-foreground-secondary/90 leading-relaxed line-clamp-2 pt-1 border-t border-border/30">
              Active concurrent execution workers handling non-blocking background tasks and SQLite
              state transitions.
            </p>
          </CardHeader>

          <CardContent className="p-4 pt-2 space-y-3">
            <div className="space-y-1.5 p-2 rounded-md bg-surface-elevated/40 border border-border/40 text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-foreground-muted">Worker Concurrency</span>
                <span className="font-mono-tech font-semibold text-foreground">
                  {workers ? `${workers.active} active / ${workers.total} total` : '4 workers'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-foreground-muted">Max Queue Depth</span>
                <span className="font-mono-tech text-accent-cyan font-medium">100 tasks</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="p-1.5 rounded bg-surface/60 border border-border/30">
                <span className="text-[10px] text-foreground-muted block">Worker State</span>
                <span className="font-mono-tech text-emerald-400 text-xs">READY</span>
              </div>
              <div className="p-1.5 rounded bg-surface/60 border border-border/30">
                <span className="text-[10px] text-foreground-muted block">Handlers</span>
                <span className="font-mono-tech font-semibold text-foreground">7 registered</span>
              </div>
            </div>

            <div className="flex items-center justify-between pt-1 border-t border-border/30 text-xs">
              <span className="text-[10px] text-foreground-muted font-mono-tech">
                FastAPI Async Engine
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={onNavigateToDiagnostics}
                className="h-7 px-2 text-[11px] text-accent-primary hover:text-accent-primary"
              >
                Inspect Telemetry
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
