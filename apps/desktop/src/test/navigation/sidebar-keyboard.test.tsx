import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TooltipProvider } from '@/components/ui/tooltip';
import { ThemeProvider } from '@/design-system/ThemeContext';
import { AppSidebar } from '@/components/navigation/AppSidebar';
import { CommandPalette } from '@/components/navigation/CommandPalette';
import { useSidebarStore } from '@/stores/sidebarStore';

const renderAppWithNavigation = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <TooltipProvider>
          <MemoryRouter initialEntries={['/dashboard']}>
            <div>
              <AppSidebar />
              <CommandPalette />
            </div>
          </MemoryRouter>
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

describe('Navigation Keyboard Shortcuts & Accessibility', () => {
  beforeEach(() => {
    localStorage.clear();
    useSidebarStore.getState().resetToDefaults();
  });

  it('toggles sidebar on Ctrl+B key press', async () => {
    renderAppWithNavigation();
    expect(useSidebarStore.getState().isExpanded).toBe(true);

    // Fire Ctrl+B
    fireEvent.keyDown(window, { key: 'b', ctrlKey: true });
    expect(useSidebarStore.getState().isExpanded).toBe(false);

    // Fire Ctrl+B again to expand
    fireEvent.keyDown(window, { key: 'b', ctrlKey: true });
    expect(useSidebarStore.getState().isExpanded).toBe(true);
  });

  it('opens Command Palette on Ctrl+K and filters results', async () => {
    renderAppWithNavigation();
    expect(useSidebarStore.getState().isCommandPaletteOpen).toBe(false);

    // Fire Ctrl+K
    fireEvent.keyDown(window, { key: 'k', ctrlKey: true });
    expect(useSidebarStore.getState().isCommandPaletteOpen).toBe(true);

    const searchInput = screen.getByPlaceholderText(/Type a module name/i);
    expect(searchInput).toBeInTheDocument();

    // Type query "Diagnostics"
    fireEvent.change(searchInput, { target: { value: 'Diagnostics' } });

    await waitFor(() => {
      expect(screen.getByText('Backend Diagnostics')).toBeInTheDocument();
    });
  });

  it('navigates list with arrow keys and selects entry with Enter in Command Palette', async () => {
    renderAppWithNavigation();

    // Open palette
    fireEvent.keyDown(window, { key: 'k', ctrlKey: true });
    const searchInput = screen.getByPlaceholderText(/Type a module name/i);

    // Filter to "Design System"
    fireEvent.change(searchInput, { target: { value: 'Design System' } });

    await waitFor(() => {
      expect(screen.getAllByText('Design System').length).toBeGreaterThan(0);
    });

    // Press ArrowDown and then Enter
    fireEvent.keyDown(searchInput, { key: 'ArrowDown' });
    fireEvent.keyDown(searchInput, { key: 'Enter' });

    // Command palette should close
    await waitFor(() => {
      expect(useSidebarStore.getState().isCommandPaletteOpen).toBe(false);
    });
  });

  it('closes Command Palette on Escape key', async () => {
    renderAppWithNavigation();

    // Open palette
    fireEvent.keyDown(window, { key: 'k', ctrlKey: true });
    expect(useSidebarStore.getState().isCommandPaletteOpen).toBe(true);

    const searchInput = screen.getByPlaceholderText(/Type a module name/i);
    fireEvent.keyDown(searchInput, { key: 'Escape' });

    await waitFor(() => {
      expect(useSidebarStore.getState().isCommandPaletteOpen).toBe(false);
    });
  });
});
