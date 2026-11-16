import React, { useEffect, useState } from 'react';
import { Activity, ShieldCheck, Terminal, Cpu, Sliders, Search } from 'lucide-react';
import { useBackendHealth, ConnectionStatus } from '@/hooks/use-backend-health';
import { getNativeAppInfo, AppInfo } from '@/services/tauri';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Button } from '@/components/ui/button';
import { useDensity } from '@/design-system/ThemeContext';
import { NavigationBreadcrumbs } from '@/components/navigation/NavigationBreadcrumbs';
import { useSidebarStore } from '@/stores/sidebarStore';

export const Header: React.FC = () => {
  const { connectionStatus, health } = useBackendHealth();
  const [appInfo, setAppInfo] = useState<AppInfo | null>(null);
  const { density, toggleDensity } = useDensity();
  const { setCommandPaletteOpen } = useSidebarStore();

  useEffect(() => {
    getNativeAppInfo().then(setAppInfo);
  }, []);

  const renderStatusBadge = (status: ConnectionStatus) => {
    switch (status) {
      case 'connected':
        return (
          <Badge variant="success" dot pulse>
            CONNECTED (8765)
          </Badge>
        );
      case 'connecting':
        return (
          <Badge variant="warning" dot pulse>
            CONNECTING...
          </Badge>
        );
      case 'disconnected':
      default:
        return (
          <Badge variant="error" dot>
            DISCONNECTED
          </Badge>
        );
    }
  };

  return (
    <TooltipProvider>
      <header className="h-12 border-b border-border bg-surface px-4 flex items-center justify-between select-none z-10">
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex items-center gap-2 shrink-0">
            <Terminal className="w-5 h-5 text-primary" />
            <span className="font-bold tracking-wider text-sm text-foreground">AUTONOM</span>
            <Badge variant="neutral" className="text-[10px] py-0 px-1.5 font-mono-tech">
              v0.1.0-dev
            </Badge>
          </div>

          <div className="h-4 w-px bg-border mx-1 shrink-0" />

          {/* Breadcrumbs Navigation */}
          <div className="hidden md:flex items-center min-w-0">
            <NavigationBreadcrumbs />
          </div>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          {/* Quick Search / Command Palette Pill */}
          <button
            onClick={() => setCommandPaletteOpen(true)}
            className="flex items-center gap-2 px-2.5 py-1 rounded-md bg-surface-elevated/70 border border-border/60 hover:border-accent-primary/50 text-foreground-muted hover:text-foreground text-xs transition-colors"
            title="Open command palette (Ctrl+K)"
            aria-label="Open command palette (Ctrl+K)"
          >
            <Search className="h-3.5 w-3.5" />
            <span className="hidden sm:inline text-[11px]">Search commands...</span>
            <kbd className="hidden sm:inline font-mono-tech text-[9px] px-1 py-0.5 rounded bg-surface border border-border">
              Ctrl+K
            </kbd>
          </button>

          <div className="hidden sm:flex items-center gap-2 text-xs text-foreground-secondary">
            <Cpu className="w-3.5 h-3.5 text-cyan" />
            <span className="font-mono-tech">
              {appInfo ? `${appInfo.os} (${appInfo.arch})` : 'Windows x64'}
            </span>
          </div>

          <div className="hidden lg:flex items-center gap-2 text-xs text-foreground-secondary">
            <ShieldCheck className="w-3.5 h-3.5 text-primary" />
            <span>Stage 07 Navigation</span>
          </div>

          {health && (
            <span className="text-[11px] font-tabular text-foreground-muted hidden xl:inline">
              Uptime: {Math.floor(health.uptime_seconds)}s
            </span>
          )}

          {renderStatusBadge(connectionStatus)}

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleDensity}
                className="h-7 w-7 text-foreground-secondary hover:text-foreground hover:bg-surface-elevated"
                aria-label={`Toggle density mode. Current: ${density}`}
              >
                <Sliders className="w-3.5 h-3.5" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              Density:{' '}
              {density === 'comfortable'
                ? 'Comfortable (Click for Compact)'
                : 'Compact (Click for Comfortable)'}
            </TooltipContent>
          </Tooltip>

          <div className="flex items-center gap-1 text-[11px] text-foreground-muted font-mono-tech bg-surface-elevated px-2 py-1 rounded border border-border">
            <Activity className="w-3 h-3 text-cyan" />
            <span>24 AGENTS</span>
          </div>
        </div>
      </header>
    </TooltipProvider>
  );
};
