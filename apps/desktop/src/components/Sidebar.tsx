import React, { useState } from 'react';
import {
  LayoutDashboard,
  Activity,
  Briefcase,
  Users,
  Monitor,
  Mail,
  Video,
  FileText,
  Code,
  Sparkles,
  Search,
  Workflow,
  BarChart3,
  FileClock,
  Puzzle,
  Settings,
  Database,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

interface NavItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  isDevelopmentOnly?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { id: 'command-center', label: 'Command Center', icon: LayoutDashboard },
  { id: 'diagnostics', label: 'Diagnostics & Tasks', icon: Activity },
  { id: 'desktop-diagnostics', label: 'Desktop Shell', icon: Monitor },
  { id: 'storage', label: 'Storage & Database', icon: Database },
  { id: 'jobs', label: 'Jobs & Applications', icon: Briefcase, isDevelopmentOnly: true },
  { id: 'agents', label: 'Agents (Swarm)', icon: Users, isDevelopmentOnly: true },
  { id: 'computer-control', label: 'Computer Control', icon: Monitor, isDevelopmentOnly: true },
  { id: 'communications', label: 'Communications', icon: Mail, isDevelopmentOnly: true },
  { id: 'interviews', label: 'Interviews', icon: Video, isDevelopmentOnly: true },
  { id: 'documents', label: 'Documents', icon: FileText, isDevelopmentOnly: true },
  { id: 'coding', label: 'Coding', icon: Code, isDevelopmentOnly: true },
  { id: 'creative', label: 'Creative Studio', icon: Sparkles, isDevelopmentOnly: true },
  { id: 'research', label: 'Research & Markets', icon: Search, isDevelopmentOnly: true },
  { id: 'workflows', label: 'Workflows', icon: Workflow, isDevelopmentOnly: true },
  { id: 'analytics', label: 'Analytics', icon: BarChart3, isDevelopmentOnly: true },
  { id: 'activity-logs', label: 'Activity Logs', icon: FileClock, isDevelopmentOnly: true },
  { id: 'integrations', label: 'Integrations', icon: Puzzle, isDevelopmentOnly: true },
  { id: 'settings', label: 'Settings', icon: Settings },
];

interface SidebarProps {
  activeModule: string;
  onSelectModule: (id: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeModule, onSelectModule }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <aside
      className={`border-r border-border bg-surface transition-all duration-200 flex flex-col justify-between ${
        isCollapsed ? 'w-14' : 'w-56'
      }`}
    >
      <div className="flex-1 overflow-y-auto py-2">
        <div className="px-3 pb-2 mb-2 border-b border-border/50 flex items-center justify-between">
          {!isCollapsed && (
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Navigation
            </span>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-surface-elevated transition-colors"
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>
        </div>

        <nav className="space-y-0.5 px-2">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activeModule === item.id;

            return (
              <button
                key={item.id}
                onClick={() => onSelectModule(item.id)}
                title={isCollapsed ? item.label : undefined}
                className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded text-xs transition-colors text-left ${
                  isActive
                    ? 'bg-primary/20 text-primary-light font-medium border border-primary/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-surface-elevated'
                }`}
              >
                <Icon
                  className={`w-4 h-4 shrink-0 ${isActive ? 'text-primary-light' : 'text-slate-400'}`}
                />
                {!isCollapsed && (
                  <span className="truncate flex-1">
                    {item.label}
                    {item.isDevelopmentOnly && (
                      <span className="ml-1.5 text-[9px] px-1 py-0.2 rounded bg-surface-elevated text-slate-500 font-mono">
                        v2
                      </span>
                    )}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {!isCollapsed && (
        <div className="p-3 border-t border-border bg-surface-muted text-[11px] text-slate-500">
          <p className="font-semibold text-slate-400">AUTONOM v0.1.0</p>
          <p>Stage 02 Foundation</p>
        </div>
      )}
    </aside>
  );
};
