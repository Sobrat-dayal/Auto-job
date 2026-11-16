import { describe, it, expect, beforeEach } from 'vitest';
import { useSidebarStore } from '@/stores/sidebarStore';

describe('Sidebar State Persistence', () => {
  beforeEach(() => {
    localStorage.clear();
    useSidebarStore.getState().resetToDefaults();
  });

  it('persists sidebar state to localStorage under key autonom_sidebar_state', () => {
    useSidebarStore.getState().setExpanded(false);
    useSidebarStore.getState().toggleGroup('recruitment');
    useSidebarStore.getState().toggleItemExpanded('jobs');

    const storedRaw = localStorage.getItem('autonom_sidebar_state');
    expect(storedRaw).not.toBeNull();

    const parsed = JSON.parse(storedRaw!);
    expect(parsed.state.isExpanded).toBe(false);
    expect(parsed.state.expandedGroups).not.toContain('recruitment');
  });

  it('does NOT persist transient modal states (activeFlyout, isCommandPaletteOpen)', () => {
    useSidebarStore.getState().setActiveFlyout('jobs');
    useSidebarStore.getState().setCommandPaletteOpen(true);

    const storedRaw = localStorage.getItem('autonom_sidebar_state');
    const parsed = JSON.parse(storedRaw!);

    expect(parsed.state.activeFlyout).toBeUndefined();
    expect(parsed.state.isCommandPaletteOpen).toBeUndefined();
  });

  it('handles corrupted localStorage data without crashing by falling back to defaults', () => {
    // Inject corrupt JSON into storage
    localStorage.setItem('autonom_sidebar_state', '{ invalid json [!!]');

    // Resetting or reading the store does not throw
    expect(() => {
      useSidebarStore.getState().resetToDefaults();
    }).not.toThrow();

    expect(useSidebarStore.getState().isExpanded).toBe(true);
    expect(useSidebarStore.getState().expandedGroups.length).toBeGreaterThan(0);
  });
});
