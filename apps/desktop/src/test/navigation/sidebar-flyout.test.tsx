import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TooltipProvider } from '@/components/ui/tooltip';
import { ThemeProvider } from '@/design-system/ThemeContext';
import { AppSidebar } from '@/components/navigation/AppSidebar';
import { useSidebarStore } from '@/stores/sidebarStore';

const renderCollapsedSidebar = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  // Start with collapsed mode
  useSidebarStore.getState().setExpanded(false);

  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <TooltipProvider>
          <MemoryRouter initialEntries={['/dashboard']}>
            <AppSidebar />
          </MemoryRouter>
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

describe('SidebarFlyout Component in Collapsed Mode', () => {
  beforeEach(() => {
    localStorage.clear();
    useSidebarStore.getState().resetToDefaults();
  });

  it('renders collapsed rail without expanded text labels', () => {
    renderCollapsedSidebar();
    expect(screen.queryByText('MAIN')).not.toBeInTheDocument();
    expect(screen.queryByText('Command Center')).not.toBeInTheDocument();
  });

  it('opens flyout menu when a multi-child icon button is clicked in collapsed mode', async () => {
    renderCollapsedSidebar();

    // In collapsed mode, Jobs & Applications has a flyout trigger button
    const jobsTrigger = screen.getByRole('button', { name: 'Jobs & Applications' });
    expect(jobsTrigger).toBeInTheDocument();
    expect(jobsTrigger).toHaveAttribute('aria-expanded', 'false');

    // Click to open flyout
    fireEvent.click(jobsTrigger);

    await waitFor(() => {
      expect(jobsTrigger).toHaveAttribute('aria-expanded', 'true');
    });

    // Flyout content should now be visible in DOM
    expect(screen.getByText('Job Discovery')).toBeInTheDocument();
    expect(screen.getByText('Recommended Jobs')).toBeInTheDocument();
    expect(screen.getAllByText('Stage 26').length).toBeGreaterThan(0);
  });

  it('closes flyout menu when Escape is pressed or trigger is clicked', async () => {
    renderCollapsedSidebar();

    const jobsTrigger = screen.getByRole('button', { name: 'Jobs & Applications' });
    fireEvent.click(jobsTrigger);

    await waitFor(() => {
      expect(screen.getByText('Job Discovery')).toBeInTheDocument();
    });

    // Press Escape on the flyout content
    const jobDiscovery = screen.getByText('Job Discovery');
    fireEvent.keyDown(jobDiscovery, { key: 'Escape' });

    await waitFor(() => {
      expect(useSidebarStore.getState().activeFlyout).toBeNull();
    });
  });

  it('closes flyout menu when a child item is clicked', async () => {
    renderCollapsedSidebar();

    const jobsTrigger = screen.getByRole('button', { name: 'Jobs & Applications' });
    fireEvent.click(jobsTrigger);

    await waitFor(() => {
      expect(screen.getByText('Job Discovery')).toBeInTheDocument();
    });

    const childLink = screen.getByText('Job Discovery');
    fireEvent.click(childLink);

    await waitFor(() => {
      expect(useSidebarStore.getState().activeFlyout).toBeNull();
    });
  });
});
