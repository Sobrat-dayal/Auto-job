import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TooltipProvider } from '@/components/ui/tooltip';
import { ApplicationPipeline } from '@/features/dashboard/ApplicationPipeline';
import { JobDiscoveryOverview } from '@/features/dashboard/JobDiscoveryOverview';
import type { RecruitmentSummary } from '@/types/dashboard';

const mockRecruitment: RecruitmentSummary = {
  jobs_discovered: 5,
  jobs_discovered_today: 2,
  active_listings: 3,
  applications_total: 1,
  applications_submitted: 1,
  pipeline_stages: {
    discovered: 5,
    evaluated: 2,
    matched: 1,
    queued: 0,
    preparing: 0,
    submitted: 1,
    recruiter_response: 0,
    interview: 0,
    offer: 0,
    rejected: 0,
  },
  automated_scouting_enabled: false,
  automated_scouting_message: 'Autonomous job scraping scheduled for activation in Stage 26.',
};

describe('Recruitment & Pipeline Components', () => {
  describe('ApplicationPipeline', () => {
    it('renders 10-stage application pipeline with counts', () => {
      render(
        <TooltipProvider>
          <ApplicationPipeline recruitment={mockRecruitment} isConnected={true} />
        </TooltipProvider>
      );

      expect(screen.getByText('Recruitment Application Pipeline')).toBeInTheDocument();
      expect(screen.getByText('Discovered')).toBeInTheDocument();
      expect(screen.getByText('Evaluated')).toBeInTheDocument();
      expect(screen.getByText('Matched')).toBeInTheDocument();
      expect(screen.getByText('Submitted')).toBeInTheDocument();
      expect(screen.getByText('Interview')).toBeInTheDocument();
      expect(screen.getByText('Offer')).toBeInTheDocument();
      expect(screen.getByText('Closed')).toBeInTheDocument();

      // Stage counts and active status badge
      expect(screen.getByText('ACTIVE PIPELINE')).toBeInTheDocument();
      expect(screen.getByText(/1 active application records in SQLite/)).toBeInTheDocument();
    });

    it('displays honest roadmap notice when applications are zero', () => {
      render(
        <TooltipProvider>
          <ApplicationPipeline
            recruitment={{
              ...mockRecruitment,
              applications_total: 0,
              applications_submitted: 0,
              pipeline_stages: {
                ...mockRecruitment.pipeline_stages,
                submitted: 0,
              },
            }}
            isConnected={true}
          />
        </TooltipProvider>
      );

      expect(
        screen.getByText('Application Tracking Inactive (Scheduled Stage 31)')
      ).toBeInTheDocument();
      expect(
        screen.getByText(/No applications have been drafted or submitted yet/)
      ).toBeInTheDocument();
    });

    it('navigates to applications page when clicking view kanban board', () => {
      const onNavigate = vi.fn();
      render(
        <TooltipProvider>
          <ApplicationPipeline
            recruitment={mockRecruitment}
            isConnected={true}
            onNavigateToApplications={onNavigate}
          />
        </TooltipProvider>
      );

      fireEvent.click(screen.getByText('View Kanban Board'));
      expect(onNavigate).toHaveBeenCalled();
    });
  });

  describe('JobDiscoveryOverview', () => {
    it('renders job discovery counts and active listings', () => {
      render(
        <TooltipProvider>
          <JobDiscoveryOverview recruitment={mockRecruitment} isConnected={true} />
        </TooltipProvider>
      );

      expect(screen.getByText('Job Discovery Engine')).toBeInTheDocument();
      expect(screen.getByText('Total Discovered')).toBeInTheDocument();
      expect(screen.getByText('5')).toBeInTheDocument();
      expect(screen.getByText('Discovered Today')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
      expect(screen.getByText('Active Listings')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
    });

    it('displays honest roadmap attribution when jobs count is zero', () => {
      render(
        <TooltipProvider>
          <JobDiscoveryOverview
            recruitment={{
              ...mockRecruitment,
              jobs_discovered: 0,
              jobs_discovered_today: 0,
              active_listings: 0,
            }}
            isConnected={true}
          />
        </TooltipProvider>
      );

      expect(screen.getByText('Awaiting Autonomous Discovery (Stage 26)')).toBeInTheDocument();
    });
  });
});
