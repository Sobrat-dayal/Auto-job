import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import {
  ModulePage,
  ModuleHeader,
  ModuleToolbar,
  ModuleTabs,
  ModuleEmptyState,
  ModuleUnavailableState,
  ModuleErrorState,
  ModuleDetailPanel,
} from '@/components/module';
import { Bot } from 'lucide-react';

describe('Shared Module Components', () => {
  it('renders ModulePage with detail panel when open', () => {
    render(
      <ModulePage
        isDetailOpen={true}
        detailPanel={<div data-testid="detail-content">Inspector Info</div>}
      >
        <div data-testid="main-content">Main Body</div>
      </ModulePage>
    );

    expect(screen.getByTestId('main-content')).toBeInTheDocument();
    expect(screen.getByTestId('detail-content')).toBeInTheDocument();
    expect(screen.getByRole('complementary', { name: /detail inspector/i })).toBeInTheDocument();
  });

  it('renders ModuleHeader with stageTag and badge', () => {
    render(
      <ModuleHeader
        title="Agent Swarm Operations"
        description="Autonomous multi-agent coordination"
        icon={Bot}
        stageTag="Stage 12"
        badgeLabel="Active"
        badgeVariant="primary"
      />
    );

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Agent Swarm Operations');
    expect(screen.getByText('Stage 12')).toBeInTheDocument();
    expect(screen.getByText('Active')).toBeInTheDocument();
    expect(screen.getByText('Autonomous multi-agent coordination')).toBeInTheDocument();
  });

  it('renders ModuleToolbar and handles search input and view toggles', () => {
    const handleSearch = vi.fn();
    const handleRefresh = vi.fn();
    const handleViewChange = vi.fn();

    render(
      <ModuleToolbar
        searchQuery="agent-1"
        onSearchChange={handleSearch}
        onRefresh={handleRefresh}
        viewMode="list"
        onViewModeChange={handleViewChange}
      />
    );

    const searchInput = screen.getByRole('searchbox');
    expect(searchInput).toHaveValue('agent-1');

    fireEvent.change(searchInput, { target: { value: 'agent-2' } });
    expect(handleSearch).toHaveBeenCalledWith('agent-2');

    const refreshBtn = screen.getByRole('button', { name: /refresh list/i });
    fireEvent.click(refreshBtn);
    expect(handleRefresh).toHaveBeenCalled();

    const gridBtn = screen.getByRole('button', { name: /grid view/i });
    fireEvent.click(gridBtn);
    expect(handleViewChange).toHaveBeenCalledWith('grid');
  });

  it('renders ModuleTabs and switches active tab', () => {
    const handleTabChange = vi.fn();
    const tabs = [
      { id: 'all', label: 'All Jobs', badge: 12 },
      { id: 'active', label: 'Active', badge: 4 },
    ];

    render(<ModuleTabs tabs={tabs} activeTab="all" onTabChange={handleTabChange} />);

    const activeTab = screen.getByRole('tab', { name: /all jobs/i });
    expect(activeTab).toHaveAttribute('aria-selected', 'true');

    const nextTab = screen.getByRole('tab', { name: /active/i });
    fireEvent.click(nextTab);
    expect(handleTabChange).toHaveBeenCalledWith('active');
  });

  it('renders ModuleEmptyState with actions', () => {
    const handleAction = vi.fn();
    render(
      <ModuleEmptyState
        title="No jobs discovered yet"
        description="Launch an autonomous search or add a custom listing."
        actionLabel="Start Discovery"
        onAction={handleAction}
      />
    );

    expect(screen.getByRole('region', { name: 'No jobs discovered yet' })).toBeInTheDocument();
    const actionBtn = screen.getByRole('button', { name: 'Start Discovery' });
    fireEvent.click(actionBtn);
    expect(handleAction).toHaveBeenCalled();
  });

  it('renders ModuleUnavailableState with planned capabilities', () => {
    render(
      <ModuleUnavailableState
        moduleName="Job Discovery"
        stageTag="Stage 26"
        stageName="Multi-Source Job Scouting"
        description="Autonomous job scouter and feed parser."
        plannedCapabilities={['LinkedIn ATS crawling', 'Indeed hourly refresh']}
      />
    );

    expect(screen.getByText('Scheduled for Stage 26')).toBeInTheDocument();
    expect(screen.getByText('LinkedIn ATS crawling')).toBeInTheDocument();
  });

  it('renders ModuleErrorState with retry action', () => {
    const handleRetry = vi.fn();
    render(
      <ModuleErrorState
        title="Connection Lost"
        message="Could not reach SQLite backend."
        onRetry={handleRetry}
      />
    );

    expect(screen.getByRole('alert')).toBeInTheDocument();
    const retryBtn = screen.getByRole('button', { name: /retry connection/i });
    fireEvent.click(retryBtn);
    expect(handleRetry).toHaveBeenCalled();
  });

  it('renders ModuleDetailPanel and handles close', () => {
    const handleClose = vi.fn();
    render(
      <ModuleDetailPanel
        title="Job Inspector: Principal Architect"
        subtitle="Acme Robotics"
        onClose={handleClose}
      >
        <p>Job Details Content</p>
      </ModuleDetailPanel>
    );

    expect(screen.getByText('Job Inspector: Principal Architect')).toBeInTheDocument();
    expect(screen.getByText('Acme Robotics')).toBeInTheDocument();
    const closeBtn = screen.getByRole('button', { name: /close details/i });
    fireEvent.click(closeBtn);
    expect(handleClose).toHaveBeenCalled();
  });
});
