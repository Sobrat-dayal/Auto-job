import * as React from 'react';
import { useState, useEffect, useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Compass, CornerDownLeft } from 'lucide-react';
import { useSidebarStore } from '@/stores/sidebarStore';
import { getAllNavigationItems } from '@/config/navigation';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';

export const CommandPalette: React.FC = () => {
  const navigate = useNavigate();
  const { isCommandPaletteOpen, setCommandPaletteOpen } = useSidebarStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  // All searchable entries
  const allEntries = useMemo(() => {
    const rawItems = getAllNavigationItems();
    return rawItems.map((item) => ({
      ...item,
      searchString: `${item.title} ${item.group} ${item.description || ''} ${
        item.roadmapStage || ''
      } ${item.path}`.toLowerCase(),
    }));
  }, []);

  // Filtered entries
  const filteredEntries = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) {
      return allEntries.slice(0, 15);
    }
    return allEntries.filter((entry) => entry.searchString.includes(query)).slice(0, 25);
  }, [allEntries, searchQuery]);

  // Reset selected index when query changes
  useEffect(() => {
    setSelectedIndex(0);
  }, [searchQuery]);

  // Keep selected item in view
  useEffect(() => {
    if (listRef.current) {
      const activeEl = listRef.current.querySelector('[data-selected="true"]');
      if (activeEl) {
        activeEl.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [selectedIndex]);

  // Global Ctrl+K / Cmd+K listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(!isCommandPaletteOpen);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isCommandPaletteOpen, setCommandPaletteOpen]);

  // Select item action
  const handleSelectItem = (path: string) => {
    setCommandPaletteOpen(false);
    setSearchQuery('');
    navigate(path);
  };

  // Keyboard navigation inside command palette
  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % Math.max(1, filteredEntries.length));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(
        (prev) => (prev - 1 + filteredEntries.length) % Math.max(1, filteredEntries.length)
      );
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filteredEntries[selectedIndex]) {
        handleSelectItem(filteredEntries[selectedIndex].path);
      }
    } else if (e.key === 'Escape') {
      e.preventDefault();
      setCommandPaletteOpen(false);
    }
  };

  return (
    <Dialog open={isCommandPaletteOpen} onOpenChange={setCommandPaletteOpen}>
      <DialogContent className="max-w-xl p-0 gap-0 overflow-hidden bg-surface-elevated/95 backdrop-blur-md border border-border shadow-2xl rounded-xl">
        {/* Search Input Bar */}
        <div className="flex items-center px-4 border-b border-border/60">
          <Search className="h-4 w-4 text-foreground-muted shrink-0 mr-3" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Type a module name, route, or capability... (e.g. Jobs, Agents, Storage)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleInputKeyDown}
            className="flex-1 h-12 bg-transparent text-sm text-foreground placeholder:text-foreground-muted/60 focus:outline-none"
            autoFocus
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="text-xs text-foreground-muted hover:text-foreground px-1.5 py-0.5 rounded bg-surface border border-border"
            >
              Clear
            </button>
          )}
        </div>

        {/* Results List */}
        <div ref={listRef} className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filteredEntries.length === 0 ? (
            <div className="py-8 text-center text-xs text-foreground-muted">
              No matching modules or routes found for &ldquo;{searchQuery}&rdquo;.
            </div>
          ) : (
            filteredEntries.map((entry, index) => {
              const isSelected = index === selectedIndex;
              const IconComponent = entry.icon || Compass;

              return (
                <div
                  key={`${entry.path}-${index}`}
                  data-selected={isSelected}
                  onClick={() => handleSelectItem(entry.path)}
                  onMouseEnter={() => setSelectedIndex(index)}
                  className={`flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-colors text-xs select-none ${
                    isSelected
                      ? 'bg-accent-primary/15 text-accent-primary'
                      : 'text-foreground-secondary hover:bg-surface'
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0 pr-2">
                    <div
                      className={`p-1.5 rounded-md border shrink-0 ${
                        isSelected
                          ? 'bg-accent-primary/20 border-accent-primary/30 text-accent-primary'
                          : 'bg-surface border-border/50 text-foreground-muted'
                      }`}
                    >
                      <IconComponent className="h-4 w-4" />
                    </div>
                    <div className="flex flex-col min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-foreground truncate">
                          {entry.title}
                        </span>
                        <span className="text-[10px] text-foreground-muted uppercase tracking-wider font-mono-tech">
                          [{entry.group}]
                        </span>
                      </div>
                      <span className="text-[11px] text-foreground-muted truncate">
                        {entry.description || entry.path}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    {entry.roadmapStage && (
                      <Badge
                        variant="outline"
                        className="text-[9px] py-0 px-1 border-accent-primary/40 text-accent-primary"
                      >
                        {entry.roadmapStage}
                      </Badge>
                    )}
                    {isSelected && <CornerDownLeft className="h-3.5 w-3.5 text-accent-primary" />}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer Keyboard Hints */}
        <div className="px-4 py-2 bg-surface/50 border-t border-border/50 flex items-center justify-between text-[11px] text-foreground-muted">
          <div className="flex items-center gap-3">
            <span>
              <kbd className="px-1.5 py-0.5 rounded bg-surface border border-border font-mono-tech text-[10px]">
                ↑↓
              </kbd>{' '}
              Navigate
            </span>
            <span>
              <kbd className="px-1.5 py-0.5 rounded bg-surface border border-border font-mono-tech text-[10px]">
                ↵
              </kbd>{' '}
              Select
            </span>
            <span>
              <kbd className="px-1.5 py-0.5 rounded bg-surface border border-border font-mono-tech text-[10px]">
                esc
              </kbd>{' '}
              Close
            </span>
          </div>
          <span className="font-mono-tech text-[10px]">AUTONOM Navigation</span>
        </div>
      </DialogContent>
    </Dialog>
  );
};
