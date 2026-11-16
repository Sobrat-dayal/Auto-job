import * as React from 'react';
import { useEffect } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { useSidebarStore } from '@/stores/sidebarStore';
import { NAVIGATION_GROUPS } from '@/config/navigation';
import { SidebarHeader } from './SidebarHeader';
import { SidebarFooter } from './SidebarFooter';
import { SidebarItem } from './SidebarItem';

export const AppSidebar: React.FC = () => {
  const { isExpanded, toggleSidebar, expandedGroups, toggleGroup } = useSidebarStore();

  // Global Ctrl+B / Cmd+B keyboard shortcut to toggle sidebar
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
        e.preventDefault();
        toggleSidebar();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [toggleSidebar]);

  return (
    <aside
      className={`h-full border-r border-border/80 bg-surface flex flex-col justify-between transition-all duration-200 ease-in-out z-20 select-none ${
        isExpanded ? 'w-60 min-w-[240px]' : 'w-14 min-w-[56px]'
      }`}
      aria-label="Main Navigation"
    >
      {/* Region A: Header */}
      <SidebarHeader isExpanded={isExpanded} onToggle={toggleSidebar} />

      {/* Region B & C: Primary and Secondary Nav Items */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden py-2 px-1.5 space-y-3 scrollbar-thin">
        {NAVIGATION_GROUPS.map((group) => {
          const isGroupOpen = expandedGroups.includes(group.id);

          return (
            <div key={group.id} className="space-y-1">
              {/* Group Header in Expanded Mode */}
              {isExpanded ? (
                <button
                  onClick={() => toggleGroup(group.id)}
                  className="w-full flex items-center justify-between px-2 py-1 text-[10px] font-bold tracking-wider text-foreground-muted/80 uppercase hover:text-foreground transition-colors group select-none"
                  aria-expanded={isGroupOpen}
                  aria-label={`${group.title} category`}
                >
                  <span>{group.title}</span>
                  <span className="text-foreground-muted group-hover:text-foreground">
                    {isGroupOpen ? (
                      <ChevronDown className="h-3 w-3" />
                    ) : (
                      <ChevronRight className="h-3 w-3" />
                    )}
                  </span>
                </button>
              ) : (
                /* Group Divider in Collapsed Mode */
                <div className="my-1.5 border-t border-border/40 mx-1" aria-hidden="true" />
              )}

              {/* Group Items */}
              {(!isExpanded || isGroupOpen) && (
                <div
                  className={`space-y-0.5 ${
                    isExpanded
                      ? 'animate-in slide-in-from-top-1 duration-150'
                      : 'flex flex-col items-center'
                  }`}
                >
                  {group.items.map((item) => (
                    <SidebarItem key={item.id} item={item} isExpanded={isExpanded} />
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Region D: Footer */}
      <SidebarFooter isExpanded={isExpanded} />
    </aside>
  );
};
