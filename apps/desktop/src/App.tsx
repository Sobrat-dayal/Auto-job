import React from 'react';
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

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 2000,
    },
  },
});

export const AppContent: React.FC = () => {
  return (
    <div className="flex flex-col h-screen w-screen bg-background overflow-hidden text-foreground font-sans">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <AppSidebar />
        <main className="flex-1 overflow-y-auto bg-background">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Overview />} />
            <Route path="/diagnostics" element={<Diagnostics />} />
            <Route path="/desktop-diagnostics" element={<DesktopDiagnostics />} />
            <Route path="/storage" element={<Storage />} />
            <Route path="/design-system" element={<DesignSystemShowcase />} />
            <Route path="/settings/diagnostics" element={<Diagnostics />} />
            <Route path="/settings/desktop" element={<DesktopDiagnostics />} />
            <Route path="/settings/desktop-diagnostics" element={<DesktopDiagnostics />} />
            <Route path="/settings/storage" element={<Storage />} />
            {/* All other routes render the honest ModulePlaceholder */}
            <Route path="*" element={<ModulePlaceholder />} />
          </Routes>
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
