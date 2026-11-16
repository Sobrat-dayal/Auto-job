import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export interface SidebarState {
  // Mode A (expanded = true, width ~ 240px) vs Mode B (collapsed = false, rail ~ 56px)
  isExpanded: boolean;

  // Set of group IDs currently expanded in the sidebar (e.g. 'main', 'recruitment', etc.)
  expandedGroups: string[];

  // Set of top-level item IDs whose child submenus are expanded in expanded mode
  expandedItems: string[];

  // Active flyout menu ID when in collapsed mode (null if none open)
  activeFlyout: string | null;

  // Global command palette modal open state (Ctrl+K)
  isCommandPaletteOpen: boolean;

  // Actions
  toggleSidebar: () => void;
  setExpanded: (expanded: boolean) => void;
  toggleGroup: (groupId: string) => void;
  setGroupExpanded: (groupId: string, expanded: boolean) => void;
  toggleItemExpanded: (itemId: string) => void;
  setItemExpanded: (itemId: string, expanded: boolean) => void;
  setActiveFlyout: (itemId: string | null) => void;
  setCommandPaletteOpen: (open: boolean) => void;
  resetToDefaults: () => void;
}

const DEFAULT_EXPANDED_GROUPS = ['main', 'recruitment', 'workspace', 'management', 'development'];
const DEFAULT_EXPANDED_ITEMS = ['jobs', 'applications', 'system-settings'];

export const useSidebarStore = create<SidebarState>()(
  persist(
    (set) => ({
      isExpanded: true,
      expandedGroups: DEFAULT_EXPANDED_GROUPS,
      expandedItems: DEFAULT_EXPANDED_ITEMS,
      activeFlyout: null,
      isCommandPaletteOpen: false,

      toggleSidebar: () =>
        set((state) => ({
          isExpanded: !state.isExpanded,
          // Close any open flyout when toggling sidebar mode
          activeFlyout: null,
        })),

      setExpanded: (expanded: boolean) =>
        set(() => ({
          isExpanded: expanded,
          activeFlyout: null,
        })),

      toggleGroup: (groupId: string) =>
        set((state) => ({
          expandedGroups: state.expandedGroups.includes(groupId)
            ? state.expandedGroups.filter((id) => id !== groupId)
            : [...state.expandedGroups, groupId],
        })),

      setGroupExpanded: (groupId: string, expanded: boolean) =>
        set((state) => ({
          expandedGroups: expanded
            ? Array.from(new Set([...state.expandedGroups, groupId]))
            : state.expandedGroups.filter((id) => id !== groupId),
        })),

      toggleItemExpanded: (itemId: string) =>
        set((state) => ({
          expandedItems: state.expandedItems.includes(itemId)
            ? state.expandedItems.filter((id) => id !== itemId)
            : [...state.expandedItems, itemId],
        })),

      setItemExpanded: (itemId: string, expanded: boolean) =>
        set((state) => ({
          expandedItems: expanded
            ? Array.from(new Set([...state.expandedItems, itemId]))
            : state.expandedItems.filter((id) => id !== itemId),
        })),

      setActiveFlyout: (itemId: string | null) =>
        set(() => ({
          activeFlyout: itemId,
        })),

      setCommandPaletteOpen: (open: boolean) =>
        set(() => ({
          isCommandPaletteOpen: open,
        })),

      resetToDefaults: () =>
        set(() => ({
          isExpanded: true,
          expandedGroups: DEFAULT_EXPANDED_GROUPS,
          expandedItems: DEFAULT_EXPANDED_ITEMS,
          activeFlyout: null,
          isCommandPaletteOpen: false,
        })),
    }),
    {
      name: 'autonom_sidebar_state',
      storage: createJSONStorage(() => localStorage),
      // Only persist durable user preferences; avoid persisting modal dialog or flyout transient states
      partialize: (state) => ({
        isExpanded: state.isExpanded,
        expandedGroups: state.expandedGroups,
        expandedItems: state.expandedItems,
      }),
    }
  )
);
