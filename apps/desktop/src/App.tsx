import React, { Suspense } from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@/design-system/ThemeContext';
import { ToastProvider } from '@/components/feedback/Toast';
import { TooltipProvider } from '@/components/ui/tooltip';
import { Header } from '@/components/Header';
import { AppSidebar } from '@/components/navigation/AppSidebar';
import { CommandPalette } from '@/components/navigation/CommandPalette';
import { Overview } from '@/pages/Overview';
import { Diagnostics } from '@/pages/Diagnostics';
import { DesktopDiagnostics } from '@/pages/DesktopDiagnostics';
import { Storage } from '@/pages/Storage';
import { DesignSystemShowcase } from '@/pages/DesignSystemShowcase';
import { ModulePlaceholder } from '@/pages/ModulePlaceholder';

// Lazy-loaded Stage 09 Workspace Modules
const AgentsWorkspace = React.lazy(() => import('@/features/agents/AgentsWorkspace'));
const RecruitmentWorkspace = React.lazy(
  () => import('@/features/recruitment/RecruitmentWorkspace')
);
const ComputerWorkspace = React.lazy(() => import('@/features/computer/ComputerWorkspace'));
const CommunicationsWorkspace = React.lazy(
  () => import('@/features/communications/CommunicationsWorkspace')
);
const InterviewsWorkspace = React.lazy(() => import('@/features/interviews/InterviewsWorkspace'));
const DocumentsWorkspace = React.lazy(() => import('@/features/documents/DocumentsWorkspace'));
const CodingWorkspace = React.lazy(() => import('@/features/coding/CodingWorkspace'));
const CreativeWorkspace = React.lazy(() => import('@/features/creative/CreativeWorkspace'));
const ResearchWorkspace = React.lazy(() => import('@/features/research/ResearchWorkspace'));
const WorkflowsWorkspace = React.lazy(() => import('@/features/workflows/WorkflowsWorkspace'));
const AnalyticsWorkspace = React.lazy(() => import('@/features/analytics/AnalyticsWorkspace'));
const ActivityWorkspace = React.lazy(() => import('@/features/activity/ActivityWorkspace'));
const IntegrationsWorkspace = React.lazy(
  () => import('@/features/integrations/IntegrationsWorkspace')
);
const AIWorkspace = React.lazy(() => import('@/features/ai/AIWorkspace'));
const SettingsWorkspace = React.lazy(() => import('@/features/settings/SettingsWorkspace'));
const ApprovalsWorkspace = React.lazy(() => import('@/features/security/ApprovalsWorkspace'));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 2000,
    },
  },
});

export const WorkspaceSuspenseFallback = () => (
  <div className="flex h-full w-full items-center justify-center p-12 text-muted-foreground">
    <div className="flex flex-col items-center gap-3">
      <div className="h-7 w-7 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      <span className="text-xs font-medium">Loading workspace module...</span>
    </div>
  </div>
);

export const AppContent: React.FC = () => {
  return (
    <div className="flex flex-col h-screen w-screen bg-background overflow-hidden text-foreground font-sans">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <AppSidebar />
        <main className="flex-1 overflow-y-auto bg-background">
          <Suspense fallback={<WorkspaceSuspenseFallback />}>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Overview />} />

              {/* 13 Core Stage 09 Workspace Modules */}
              <Route path="/agents" element={<AgentsWorkspace />} />
              <Route path="/agents/*" element={<AgentsWorkspace />} />

              <Route path="/recruitment" element={<RecruitmentWorkspace />} />
              <Route path="/recruitment/*" element={<RecruitmentWorkspace />} />

              <Route path="/computer" element={<ComputerWorkspace />} />
              <Route path="/computer/*" element={<ComputerWorkspace />} />

              <Route path="/communications" element={<CommunicationsWorkspace />} />
              <Route path="/communications/*" element={<CommunicationsWorkspace />} />

              <Route path="/interviews" element={<InterviewsWorkspace />} />
              <Route path="/interviews/*" element={<InterviewsWorkspace />} />

              <Route path="/documents" element={<DocumentsWorkspace />} />
              <Route path="/documents/*" element={<DocumentsWorkspace />} />

              <Route path="/coding" element={<CodingWorkspace />} />
              <Route path="/coding/*" element={<CodingWorkspace />} />

              <Route path="/creative" element={<CreativeWorkspace />} />
              <Route path="/creative/*" element={<CreativeWorkspace />} />

              <Route path="/research" element={<ResearchWorkspace />} />
              <Route path="/research/*" element={<ResearchWorkspace />} />

              <Route path="/workflows" element={<WorkflowsWorkspace />} />
              <Route path="/workflows/*" element={<WorkflowsWorkspace />} />

              <Route path="/analytics" element={<AnalyticsWorkspace />} />
              <Route path="/analytics/*" element={<AnalyticsWorkspace />} />

              <Route path="/activity" element={<ActivityWorkspace />} />
              <Route path="/activity/*" element={<ActivityWorkspace />} />

              <Route path="/integrations" element={<IntegrationsWorkspace />} />
              <Route path="/integrations/*" element={<IntegrationsWorkspace />} />

              {/* AI Model Gateway (Stage 11) */}
              <Route path="/ai" element={<AIWorkspace />} />
              <Route path="/ai/*" element={<AIWorkspace />} />

              {/* Centralized Settings Workspace (Stage 10) */}
              <Route path="/settings" element={<SettingsWorkspace />} />
              <Route path="/settings/*" element={<SettingsWorkspace />} />

              {/* Authorization & Approvals Engine (Stage 14) */}
              <Route path="/approvals" element={<ApprovalsWorkspace />} />
              <Route path="/approvals/*" element={<ApprovalsWorkspace />} />

              {/* Standalone System Diagnostics & Development Tools */}
              <Route path="/diagnostics" element={<Diagnostics />} />
              <Route path="/desktop-diagnostics" element={<DesktopDiagnostics />} />
              <Route path="/storage" element={<Storage />} />
              <Route path="/design-system" element={<DesignSystemShowcase />} />

              {/* Fallback */}
              <Route path="*" element={<ModulePlaceholder />} />
            </Routes>
          </Suspense>
        </main>
      </div>
      <CommandPalette />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <TooltipProvider>
          <ToastProvider>
            <HashRouter>
              <AppContent />
            </HashRouter>
          </ToastProvider>
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;
