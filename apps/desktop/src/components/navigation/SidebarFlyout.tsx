import * as React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import type { NavigationItem } from '@/config/navigation-types';
import { Badge } from '@/components/ui/badge';
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover';
import { ChevronRight } from 'lucide-react';

interface SidebarFlyoutProps {
  item: NavigationItem;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
}

export const SidebarFlyout: React.FC<SidebarFlyoutProps> = ({
  item,
  isOpen,
  onOpenChange,
  children,
}) => {
  const navigate = useNavigate();
  const Icon = item.icon;

  const handleChildClick = (path: string) => {
    onOpenChange(false);
    navigate(path);
  };

  return (
    <Popover open={isOpen} onOpenChange={onOpenChange}>
      <PopoverTrigger asChild>{children}</PopoverTrigger>
      <PopoverContent
        side="right"
        align="start"
        sideOffset={8}
        avoidCollisions
        className="w-64 p-2 bg-surface-elevated/95 backdrop-blur-md border border-border shadow-2xl rounded-lg z-50 text-foreground"
        onKeyDown={(e) => {
          if (e.key === 'Escape') {
            onOpenChange(false);
          }
        }}
      >
        {/* Flyout Header */}
        <div className="px-2.5 py-2 border-b border-border/50 mb-1">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-md bg-accent-primary/10 text-accent-primary border border-accent-primary/20">
                <Icon className="h-4 w-4" />
              </div>
              <span className="font-semibold text-xs tracking-wide text-foreground">
                {item.title}
              </span>
            </div>

            {item.roadmapStage && (
              <Badge
                variant="outline"
                className="text-[9px] py-0 px-1 border-accent-primary/40 text-accent-primary"
              >
                {item.roadmapStage}
              </Badge>
            )}
          </div>

          {item.description && (
            <p className="text-[11px] text-foreground-muted mt-1.5 leading-snug line-clamp-2">
              {item.description}
            </p>
          )}
        </div>

        {/* Child Items List */}
        <div className="space-y-0.5 py-1 max-h-72 overflow-y-auto">
          {/* Main parent link */}
          <NavLink
            to={item.path}
            onClick={() => onOpenChange(false)}
            className={({ isActive }) =>
              `flex items-center justify-between px-2.5 py-1.5 rounded text-xs transition-colors group ${
                isActive
                  ? 'bg-accent-primary/15 text-accent-primary font-medium'
                  : 'text-foreground-secondary hover:text-foreground hover:bg-surface'
              }`
            }
          >
            <span className="text-[11px] font-medium">Overview</span>
            <ChevronRight className="h-3 w-3 text-foreground-muted group-hover:text-accent-primary group-hover:translate-x-0.5 transition-all" />
          </NavLink>

          {item.children?.map((child) => (
            <NavLink
              key={child.id}
              to={child.path}
              onClick={() => handleChildClick(child.path)}
              className={({ isActive }) =>
                `flex items-center justify-between px-2.5 py-1.5 rounded text-xs transition-colors group ${
                  isActive
                    ? 'bg-accent-primary/15 text-accent-primary font-medium'
                    : 'text-foreground-secondary hover:text-foreground hover:bg-surface'
                }`
              }
            >
              <div className="flex flex-col min-w-0 pr-2">
                <span className="text-[11px] truncate">{child.title}</span>
                {child.description && (
                  <span className="text-[9px] text-foreground-muted truncate">
                    {child.description}
                  </span>
                )}
              </div>

              {child.badge ? (
                <Badge variant="neutral" className="text-[9px] py-0 px-1 shrink-0">
                  {child.badge}
                </Badge>
              ) : child.roadmapStage ? (
                <span className="text-[9px] font-mono-tech text-foreground-muted shrink-0">
                  {child.roadmapStage}
                </span>
              ) : (
                <ChevronRight className="h-3 w-3 text-foreground-muted group-hover:text-accent-primary group-hover:translate-x-0.5 transition-all shrink-0" />
              )}
            </NavLink>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
};
