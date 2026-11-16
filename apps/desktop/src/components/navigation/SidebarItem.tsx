import * as React from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import type { NavigationItem } from '@/config/navigation-types';
import { useSidebarStore } from '@/stores/sidebarStore';
import { SidebarFlyout } from './SidebarFlyout';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { ChevronDown, ChevronRight } from 'lucide-react';

interface SidebarItemProps {
  item: NavigationItem;
  isExpanded: boolean;
}

export const SidebarItem: React.FC<SidebarItemProps> = ({ item, isExpanded }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { expandedItems, toggleItemExpanded, activeFlyout, setActiveFlyout } = useSidebarStore();

  const Icon = item.icon;
  const hasChildren = item.children && item.children.length > 0;
  const isItemSubmenuOpen = expandedItems.includes(item.id);

  // Check if current route matches item or any of its children
  const isCurrentActive =
    location.pathname === item.path || (item.path === '/dashboard' && location.pathname === '/');
  const hasActiveChild =
    hasChildren &&
    item.children?.some(
      (c) =>
        location.pathname === c.path || (location.pathname.startsWith(c.path) && c.path !== '/')
    );
  const isActive = isCurrentActive || hasActiveChild;

  // --------------------------------------------------------------------------
  // MODE A: Expanded Sidebar
  // --------------------------------------------------------------------------
  if (isExpanded) {
    return (
      <div className="space-y-0.5">
        <div
          className={`group flex items-center justify-between rounded-md px-2.5 py-1.5 text-xs font-medium transition-all select-none ${
            isCurrentActive
              ? 'bg-accent-primary/15 text-accent-primary font-semibold shadow-sm border-l-2 border-accent-primary'
              : isActive
                ? 'bg-surface-elevated/70 text-accent-primary font-medium border-l-2 border-accent-primary/60'
                : 'text-foreground-secondary hover:text-foreground hover:bg-surface-elevated/50 border-l-2 border-transparent'
          }`}
        >
          {/* Main click target for navigation */}
          <button
            onClick={() => {
              navigate(item.path);
              if (hasChildren && !isItemSubmenuOpen) {
                toggleItemExpanded(item.id);
              }
            }}
            className="flex flex-1 items-center gap-2.5 text-left min-w-0 focus:outline-none focus-visible:ring-1 focus-visible:ring-accent-primary rounded"
            aria-current={isCurrentActive ? 'page' : undefined}
          >
            <Icon
              className={`h-4 w-4 shrink-0 transition-colors ${
                isActive
                  ? 'text-accent-primary'
                  : 'text-foreground-muted group-hover:text-foreground'
              }`}
            />
            <span className="truncate">{item.title}</span>
          </button>

          {/* Right badge / chevron */}
          <div className="flex items-center gap-1 shrink-0 ml-1">
            {item.badge ? (
              <Badge variant="neutral" className="text-[9px] py-0 px-1">
                {item.badge}
              </Badge>
            ) : item.availability === 'planned' ? (
              <span className="text-[9px] font-mono-tech text-foreground-muted">
                {item.roadmapStage || 'v2'}
              </span>
            ) : null}

            {hasChildren && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  toggleItemExpanded(item.id);
                }}
                className="p-0.5 rounded text-foreground-muted hover:text-foreground hover:bg-surface focus:outline-none focus-visible:ring-1 focus-visible:ring-accent-primary"
                aria-expanded={isItemSubmenuOpen}
                aria-label={`Toggle ${item.title} sub-menu`}
              >
                {isItemSubmenuOpen ? (
                  <ChevronDown className="h-3.5 w-3.5" />
                ) : (
                  <ChevronRight className="h-3.5 w-3.5" />
                )}
              </button>
            )}
          </div>
        </div>

        {/* Nested Children Accordion */}
        {hasChildren && isItemSubmenuOpen && (
          <div
            className="ml-4 pl-2 border-l border-border/40 space-y-0.5 pt-0.5 pb-1 animate-in slide-in-from-top-1 duration-150"
            role="group"
            aria-label={`${item.title} sub-pages`}
          >
            {item.children?.map((child) => (
              <NavLink
                key={child.id}
                to={child.path}
                className={({ isActive: isChildActive }) =>
                  `flex items-center justify-between px-2 py-1 rounded text-[11px] transition-colors ${
                    isChildActive
                      ? 'bg-accent-primary/10 text-accent-primary font-medium'
                      : 'text-foreground-muted hover:text-foreground hover:bg-surface-elevated/40'
                  }`
                }
              >
                <span className="truncate">{child.title}</span>
                {child.badge ? (
                  <Badge variant="neutral" className="text-[8px] py-0 px-1 shrink-0 ml-1">
                    {child.badge}
                  </Badge>
                ) : child.availability === 'planned' ? (
                  <span className="text-[8px] font-mono-tech text-foreground-muted shrink-0 ml-1">
                    {child.roadmapStage}
                  </span>
                ) : null}
              </NavLink>
            ))}
          </div>
        )}
      </div>
    );
  }

  // --------------------------------------------------------------------------
  // MODE B: Collapsed Sidebar (Rail)
  // --------------------------------------------------------------------------
  const isFlyoutOpen = activeFlyout === item.id;

  if (hasChildren) {
    return (
      <SidebarFlyout
        item={item}
        isOpen={isFlyoutOpen}
        onOpenChange={(open) => setActiveFlyout(open ? item.id : null)}
      >
        <button
          className={`flex h-9 w-9 items-center justify-center rounded-md transition-all relative group focus:outline-none focus-visible:ring-1 focus-visible:ring-accent-primary ${
            isActive
              ? 'bg-accent-primary/15 text-accent-primary shadow-sm'
              : 'text-foreground-secondary hover:text-foreground hover:bg-surface-elevated'
          }`}
          aria-label={item.title}
          aria-expanded={isFlyoutOpen}
          aria-current={isActive ? 'page' : undefined}
        >
          <Icon className="h-4 w-4" />
          {/* Active indicator pip */}
          {isActive && (
            <span
              className="absolute left-0 top-2 bottom-2 w-0.5 rounded-r bg-accent-primary"
              aria-hidden="true"
            />
          )}
          {/* Has-children subtle dot indicator */}
          <span
            className="absolute bottom-1 right-1 h-1 w-1 rounded-full bg-accent-cyan/80"
            aria-hidden="true"
          />
        </button>
      </SidebarFlyout>
    );
  }

  // Item with no children in collapsed mode -> simple NavLink with Tooltip
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <NavLink
          to={item.path}
          className={`flex h-9 w-9 items-center justify-center rounded-md transition-all relative focus:outline-none focus-visible:ring-1 focus-visible:ring-accent-primary ${
            isCurrentActive
              ? 'bg-accent-primary/15 text-accent-primary shadow-sm'
              : 'text-foreground-secondary hover:text-foreground hover:bg-surface-elevated'
          }`}
          aria-label={item.title}
        >
          <Icon className="h-4 w-4" />
          {isCurrentActive && (
            <span
              className="absolute left-0 top-2 bottom-2 w-0.5 rounded-r bg-accent-primary"
              aria-hidden="true"
            />
          )}
        </NavLink>
      </TooltipTrigger>
      <TooltipContent side="right">
        {item.title}
        {item.shortcut && (
          <span className="ml-1 text-[10px] text-foreground-muted font-mono-tech">
            {item.shortcut}
          </span>
        )}
      </TooltipContent>
    </Tooltip>
  );
};
