import * as React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Settings, ShieldCheck, Wifi, WifiOff } from 'lucide-react';
import { useBackendHealth, ConnectionStatus } from '@/hooks/use-backend-health';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';

interface SidebarFooterProps {
  isExpanded: boolean;
}

export const SidebarFooter: React.FC<SidebarFooterProps> = ({ isExpanded }) => {
  const location = useLocation();
  const { connectionStatus, health } = useBackendHealth();
  const isSettingsActive = location.pathname.startsWith('/settings');

  const getStatusColor = (status: ConnectionStatus) => {
    switch (status) {
      case 'connected':
        return 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)]';
      case 'connecting':
        return 'bg-amber-400 animate-pulse';
      case 'disconnected':
      default:
        return 'bg-rose-500';
    }
  };

  const getStatusLabel = (status: ConnectionStatus) => {
    switch (status) {
      case 'connected':
        return 'CONNECTED (8765)';
      case 'connecting':
        return 'CONNECTING...';
      case 'disconnected':
      default:
        return 'DISCONNECTED';
    }
  };

  return (
    <div className="border-t border-border/60 bg-surface/80 p-2 select-none">
      {isExpanded ? (
        <div className="space-y-2">
          {/* Engine Status Bar */}
          <div className="flex items-center justify-between px-2 py-1.5 rounded bg-surface-elevated/70 border border-border/40 text-xs">
            <div className="flex items-center gap-2 min-w-0">
              <span
                className={`h-2 w-2 rounded-full shrink-0 ${getStatusColor(connectionStatus)}`}
                aria-hidden="true"
              />
              <span className="font-mono-tech text-[10px] tracking-wide text-foreground truncate">
                {getStatusLabel(connectionStatus)}
              </span>
            </div>

            {health && (
              <span className="text-[10px] text-foreground-muted font-mono-tech shrink-0">
                {Math.floor(health.uptime_seconds)}s
              </span>
            )}
          </div>

          {/* Quick Action Links */}
          <div className="flex items-center justify-between px-1">
            <NavLink
              to="/settings"
              className={({ isActive }) =>
                `flex items-center gap-2 text-xs py-1 px-2 rounded transition-colors ${
                  isActive
                    ? 'text-accent-primary bg-surface-elevated font-medium'
                    : 'text-foreground-secondary hover:text-foreground hover:bg-surface-elevated/60'
                }`
              }
            >
              <Settings className="h-3.5 w-3.5" />
              <span>Settings</span>
            </NavLink>

            <Tooltip>
              <TooltipTrigger asChild>
                <div className="flex items-center gap-1 text-[10px] text-foreground-muted cursor-default font-mono-tech">
                  <ShieldCheck className="h-3 w-3 text-accent-cyan" />
                  <span>AUTONOM</span>
                </div>
              </TooltipTrigger>
              <TooltipContent side="top">Desktop Multi-Agent System Core</TooltipContent>
            </Tooltip>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-2 py-1">
          {/* Collapsed Status Dot */}
          <Tooltip>
            <TooltipTrigger asChild>
              <div
                className="flex h-8 w-8 items-center justify-center rounded cursor-pointer hover:bg-surface-elevated"
                tabIndex={0}
                role="status"
                aria-label={`Backend ${connectionStatus}`}
              >
                {connectionStatus === 'connected' ? (
                  <span
                    className={`h-2.5 w-2.5 rounded-full ${getStatusColor(connectionStatus)}`}
                  />
                ) : connectionStatus === 'connecting' ? (
                  <Wifi className="h-4 w-4 text-amber-400 animate-pulse" />
                ) : (
                  <WifiOff className="h-4 w-4 text-rose-500" />
                )}
              </div>
            </TooltipTrigger>
            <TooltipContent side="right">
              <div className="text-xs font-mono-tech">
                Backend: {getStatusLabel(connectionStatus)}
              </div>
            </TooltipContent>
          </Tooltip>

          {/* Collapsed Settings Shortcut */}
          <Tooltip>
            <TooltipTrigger asChild>
              <NavLink
                to="/settings"
                className={`flex h-8 w-8 items-center justify-center rounded transition-colors ${
                  isSettingsActive
                    ? 'text-accent-primary bg-surface-elevated'
                    : 'text-foreground-secondary hover:text-foreground hover:bg-surface-elevated'
                }`}
                aria-label="Settings"
              >
                <Settings className="h-4 w-4" />
              </NavLink>
            </TooltipTrigger>
            <TooltipContent side="right">Settings</TooltipContent>
          </Tooltip>
        </div>
      )}
    </div>
  );
};
