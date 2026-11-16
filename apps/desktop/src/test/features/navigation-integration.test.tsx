import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import React, { Suspense } from 'react';
import { WorkspaceSuspenseFallback } from '@/App';

// Lazy imports
const CodingWorkspace = React.lazy(() => import('@/features/coding/CodingWorkspace'));
const CreativeWorkspace = React.lazy(() => import('@/features/creative/CreativeWorkspace'));
const ResearchWorkspace = React.lazy(() => import('@/features/research/ResearchWorkspace'));
const CommunicationsWorkspace = React.lazy(
  () => import('@/features/communications/CommunicationsWorkspace')
);
const InterviewsWorkspace = React.lazy(() => import('@/features/interviews/InterviewsWorkspace'));
const IntegrationsWorkspace = React.lazy(
  () => import('@/features/integrations/IntegrationsWorkspace')
);

describe('Cross-Module Route Integration', () => {
  it('renders CodingWorkspace on /coding route', async () => {
    render(
      <MemoryRouter initialEntries={['/coding/projects']}>
        <Suspense fallback={<WorkspaceSuspenseFallback />}>
          <Routes>
            <Route path="/coding/*" element={<CodingWorkspace />} />
          </Routes>
        </Suspense>
      </MemoryRouter>
    );

    await waitFor(
      () => {
        expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
          'Software Engineering & Coding Studio'
        );
      },
      { timeout: 5000 }
    );
  });

  it('renders CreativeWorkspace on /creative route', async () => {
    render(
      <MemoryRouter initialEntries={['/creative/3d']}>
        <Suspense fallback={<WorkspaceSuspenseFallback />}>
          <Routes>
            <Route path="/creative/*" element={<CreativeWorkspace />} />
          </Routes>
        </Suspense>
      </MemoryRouter>
    );

    await waitFor(
      () => {
        expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
          'Creative Studio & 3D Pipeline'
        );
      },
      { timeout: 5000 }
    );
  });

  it('renders ResearchWorkspace on /research route', async () => {
    render(
      <MemoryRouter initialEntries={['/research/projects']}>
        <Suspense fallback={<WorkspaceSuspenseFallback />}>
          <Routes>
            <Route path="/research/*" element={<ResearchWorkspace />} />
          </Routes>
        </Suspense>
      </MemoryRouter>
    );

    await waitFor(
      () => {
        expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
          'Market Intelligence & Research'
        );
      },
      { timeout: 5000 }
    );
  });

  it('renders CommunicationsWorkspace on /communications route', async () => {
    render(
      <MemoryRouter initialEntries={['/communications/inbox']}>
        <Suspense fallback={<WorkspaceSuspenseFallback />}>
          <Routes>
            <Route path="/communications/*" element={<CommunicationsWorkspace />} />
          </Routes>
        </Suspense>
      </MemoryRouter>
    );

    await waitFor(
      () => {
        expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
          'Communications & Messaging Hub'
        );
      },
      { timeout: 5000 }
    );
  });

  it('renders InterviewsWorkspace on /interviews route', async () => {
    render(
      <MemoryRouter initialEntries={['/interviews/upcoming']}>
        <Suspense fallback={<WorkspaceSuspenseFallback />}>
          <Routes>
            <Route path="/interviews/*" element={<InterviewsWorkspace />} />
          </Routes>
        </Suspense>
      </MemoryRouter>
    );

    await waitFor(
      () => {
        expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
          'Interview Coordination & Coaching'
        );
      },
      { timeout: 5000 }
    );
  });

  it('renders IntegrationsWorkspace on /integrations route', async () => {
    render(
      <MemoryRouter initialEntries={['/integrations/connected']}>
        <Suspense fallback={<WorkspaceSuspenseFallback />}>
          <Routes>
            <Route path="/integrations/*" element={<IntegrationsWorkspace />} />
          </Routes>
        </Suspense>
      </MemoryRouter>
    );

    await waitFor(
      () => {
        expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
          'Integrations & Service Connectors'
        );
      },
      { timeout: 5000 }
    );
  });
});
