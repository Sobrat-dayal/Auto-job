import * as React from 'react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

export interface ModuleTabItem {
  id: string;
  label: string;
  badge?: number | string;
  icon?: React.ComponentType<{ className?: string }>;
}

export interface ModuleTabsProps {
  tabs: ModuleTabItem[];
  activeTab: string;
  onTabChange: (id: string) => void;
  className?: string;
}

export const ModuleTabs: React.FC<ModuleTabsProps> = ({
  tabs,
  activeTab,
  onTabChange,
  className,
}) => {
  return (
    <nav
      role="tablist"
      aria-label="Module sections"
      className={cn(
        'flex flex-wrap items-center gap-1.5 border-b border-border/60 pb-px text-sm font-medium',
        className
      )}
    >
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab;
        const Icon = tab.icon;

        return (
          <button
            key={tab.id}
            role="tab"
            aria-selected={isActive}
            aria-controls={`tabpanel-${tab.id}`}
            id={`tab-${tab.id}`}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              'group relative flex items-center gap-2 px-3.5 py-2 text-xs font-medium transition-all sm:text-sm',
              'rounded-t-md border-b-2 outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
              isActive
                ? 'border-primary bg-primary/5 text-primary shadow-sm'
                : 'border-transparent text-muted-foreground hover:bg-muted/40 hover:text-foreground'
            )}
          >
            {Icon && (
              <Icon
                className={cn(
                  'h-4 w-4 shrink-0 transition-colors',
                  isActive ? 'text-primary' : 'text-muted-foreground group-hover:text-foreground'
                )}
              />
            )}
            <span>{tab.label}</span>
            {tab.badge !== undefined && (
              <Badge
                variant={isActive ? 'primary' : 'neutral'}
                className="ml-1 h-4 min-w-4 px-1.5 py-0 text-[10px] font-semibold"
              >
                {tab.badge}
              </Badge>
            )}
          </button>
        );
      })}
    </nav>
  );
};

ModuleTabs.displayName = 'ModuleTabs';
