import * as React from 'react';
import { Search, RotateCw, LayoutGrid, List } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export interface ModuleToolbarProps extends React.HTMLAttributes<HTMLDivElement> {
  searchQuery?: string;
  onSearchChange?: (query: string) => void;
  searchPlaceholder?: string;
  onRefresh?: () => void;
  isRefreshing?: boolean;
  viewMode?: 'list' | 'grid' | 'table';
  onViewModeChange?: (mode: 'list' | 'grid' | 'table') => void;
  filters?: React.ReactNode;
  actions?: React.ReactNode;
}

export const ModuleToolbar = React.forwardRef<HTMLDivElement, ModuleToolbarProps>(
  (
    {
      className,
      searchQuery,
      onSearchChange,
      searchPlaceholder = 'Filter or search items...',
      onRefresh,
      isRefreshing = false,
      viewMode,
      onViewModeChange,
      filters,
      actions,
      ...props
    },
    ref
  ) => {
    return (
      <div
        ref={ref}
        role="toolbar"
        aria-label="Module toolbar"
        className={cn(
          'flex flex-col gap-3 rounded-lg border border-border/60 bg-card/60 p-3 backdrop-blur-sm sm:flex-row sm:items-center sm:justify-between',
          className
        )}
        {...props}
      >
        <div className="flex flex-1 flex-wrap items-center gap-2.5">
          {onSearchChange !== undefined && (
            <div className="relative min-w-[200px] flex-1 max-w-sm">
              <Search
                className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
                aria-hidden="true"
              />
              <Input
                type="search"
                value={searchQuery ?? ''}
                onChange={(e) => onSearchChange(e.target.value)}
                placeholder={searchPlaceholder}
                className="h-9 pl-9 text-xs sm:text-sm"
                aria-label={searchPlaceholder}
              />
            </div>
          )}

          {filters}
        </div>

        <div className="flex shrink-0 items-center gap-2 self-end sm:self-center">
          {viewMode && onViewModeChange && (
            <div className="flex items-center rounded-md border border-border bg-background p-0.5">
              <Button
                variant={viewMode === 'list' ? 'secondary' : 'ghost'}
                size="icon"
                className="h-7 w-7 rounded-sm"
                onClick={() => onViewModeChange('list')}
                title="List view"
                aria-label="List view"
              >
                <List className="h-3.5 w-3.5" />
              </Button>
              <Button
                variant={viewMode === 'grid' ? 'secondary' : 'ghost'}
                size="icon"
                className="h-7 w-7 rounded-sm"
                onClick={() => onViewModeChange('grid')}
                title="Grid view"
                aria-label="Grid view"
              >
                <LayoutGrid className="h-3.5 w-3.5" />
              </Button>
            </div>
          )}

          {onRefresh && (
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8 text-muted-foreground hover:text-foreground"
              onClick={onRefresh}
              disabled={isRefreshing}
              title="Refresh"
              aria-label="Refresh list"
            >
              <RotateCw className={cn('h-3.5 w-3.5', isRefreshing && 'animate-spin')} />
            </Button>
          )}

          {actions}
        </div>
      </div>
    );
  }
);

ModuleToolbar.displayName = 'ModuleToolbar';
