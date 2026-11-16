import React, { useState } from 'react';
import { Search, Download, Upload, RefreshCw } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { SettingsNavigation } from './SettingsNavigation';

interface SettingsLayoutProps {
  selectedCategoryId: string;
  onSelectCategory: (categoryId: string) => void;
  title: string;
  description?: string;
  dirtyCategories?: string[];
  onExportSettings?: () => void;
  onImportSettings?: () => void;
  onResetAll?: () => void;
  children: React.ReactNode;
}

export const SettingsLayout: React.FC<SettingsLayoutProps> = ({
  selectedCategoryId,
  onSelectCategory,
  title,
  description,
  dirtyCategories = [],
  onExportSettings,
  onImportSettings,
  onResetAll,
  children,
}) => {
  const [search, setSearch] = useState('');

  return (
    <div className="flex flex-col h-full w-full bg-background overflow-hidden">
      {/* Top Header Bar */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-card/40 backdrop-blur-sm">
        <div>
          <h1 className="text-lg font-bold text-foreground tracking-tight flex items-center gap-2">
            Settings & Operational Controls
          </h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            Configure autonomous agents, local storage, Windows integration, security policies, and
            hardware limits.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {onResetAll && (
            <Button
              variant="outline"
              size="sm"
              onClick={onResetAll}
              className="text-xs h-8 px-2.5 gap-1.5 text-muted-foreground hover:text-foreground"
              title="Reset all settings to system defaults"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Reset Defaults</span>
            </Button>
          )}
          {onExportSettings && (
            <Button
              variant="outline"
              size="sm"
              onClick={onExportSettings}
              className="text-xs h-8 px-2.5 gap-1.5"
              title="Export non-sensitive configuration JSON"
            >
              <Download className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Export</span>
            </Button>
          )}
          {onImportSettings && (
            <Button
              variant="outline"
              size="sm"
              onClick={onImportSettings}
              className="text-xs h-8 px-2.5 gap-1.5"
              title="Import configuration JSON"
            >
              <Upload className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Import</span>
            </Button>
          )}
        </div>
      </div>

      {/* Main Two-Pane Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Category Sidebar */}
        <aside className="w-64 border-r border-border bg-card/20 flex flex-col shrink-0">
          <div className="p-3 border-b border-border/40">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
              <Input
                placeholder="Search settings..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-8 h-8 text-xs bg-card/50"
              />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto">
            <SettingsNavigation
              selectedCategoryId={selectedCategoryId}
              onSelectCategory={onSelectCategory}
              dirtyCategories={dirtyCategories}
              searchFilter={search}
            />
          </div>
        </aside>

        {/* Right Content Pane */}
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          <div className="border-b border-border/40 pb-3">
            <h2 className="text-base font-semibold text-foreground tracking-tight">{title}</h2>
            {description && <p className="text-xs text-muted-foreground mt-0.5">{description}</p>}
          </div>

          <div className="space-y-6 max-w-4xl pb-12">{children}</div>
        </main>
      </div>
    </div>
  );
};
