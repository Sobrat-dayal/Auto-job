import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TooltipProvider } from '@/components/ui/tooltip';
import { ThemeProvider } from '@/design-system/ThemeContext';
import { AppSidebar } from '@/components/navigation/AppSidebar';
import { useSidebarStore } from '@/stores/sidebarStore';

const renderSidebar = (initialPath = '/dashboard') => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <TooltipProvider>
          <MemoryRouter initialEntries={[initialPath]}>
            <AppSidebar />
          </MemoryRouter>
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

describe('AppSidebar Component', () => {
  beforeEach(() => {
    localStorage.clear();
    useSidebarStore.getState().resetToDefaults();
  });

  it('renders expanded mode by default with header, groups, and brand', () => {
    const { container } = renderSidebar();
    const sidebar = container.querySelector('aside');
    expect(sidebar).toHaveClass('w-60');

    expect(screen.getAllByText('AUTONOM').length).toBeGreaterThan(0);
    expect(screen.getByText('MAIN')).toBeInTheDocument();
    expect(screen.getByText('RECRUITMENT')).toBeInTheDocument();
    expect(screen.getByText('WORKSPACE')).toBeInTheDocument();
    expect(screen.getByText('MANAGEMENT')).toBeInTheDocument();
    expect(screen.getByText('DEVELOPMENT')).toBeInTheDocument();

    expect(screen.getByText('Command Center')).toBeInTheDocument();
    expect(screen.getByText('Agents')).toBeInTheDocument();
    expect(screen.getByText('Jobs & Applications')).toBeInTheDocument();
  });

  it('toggles to collapsed mode when collapse button is clicked', () => {
    const { container } = renderSidebar();
    const collapseButton = screen.getByRole('button', { name: /collapse sidebar/i });
    fireEvent.click(collapseButton);

    const sidebar = container.querySelector('aside');
    expect(sidebar).toHaveClass('w-14');
    expect(useSidebarStore.getState().isExpanded).toBe(false);
  });

  it('collapses and expands navigation groups in expanded mode', () => {
    renderSidebar();
    expect(screen.getByText('Command Center')).toBeInTheDocument();

    // Click MAIN group header to collapse it
    const mainHeader = screen.getByRole('button', { name: /main category/i });
    fireEvent.click(mainHeader);

    // Command Center should no longer be rendered under the collapsed group
    expect(screen.queryByText('Command Center')).not.toBeInTheDocument();

    // Click again to expand
    fireEvent.click(mainHeader);
    expect(screen.getByText('Command Center')).toBeInTheDocument();
  });

  it('toggles nested item submenu in expanded mode', () => {
    renderSidebar();
    // In default state, jobs accordion is open, so 'Job Discovery' is visible
    expect(screen.getByText('Job Discovery')).toBeInTheDocument();

    // Toggle Jobs accordion via disclosure button
    const jobsToggle = screen.getByRole('button', { name: /toggle jobs & applications sub-menu/i });
    fireEvent.click(jobsToggle);

    // Child items should now be hidden
    expect(screen.queryByText('Job Discovery')).not.toBeInTheDocument();

    // Toggle back open
    fireEvent.click(jobsToggle);
    expect(screen.getByText('Job Discovery')).toBeInTheDocument();
  });

  it('indicates active navigation link matching current route', () => {
    renderSidebar('/dashboard');
    const commandCenterLink = screen.getByRole('button', { name: /command center/i });
    expect(commandCenterLink).toHaveAttribute('aria-current', 'page');
  });
});
