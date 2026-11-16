import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@/design-system/ThemeContext';
import { ToastProvider } from '@/components/feedback/Toast';
import { Header } from '@/components/Header';
import { Sidebar } from '@/components/Sidebar';
import { Overview } from '@/pages/Overview';
import { Diagnostics } from '@/pages/Diagnostics';
import { DesktopDiagnostics } from '@/pages/DesktopDiagnostics';
import { Storage } from '@/pages/Storage';
import { DesignSystemShowcase } from '@/pages/DesignSystemShowcase';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 2000,
    },
  },
});

export const App: React.FC = () => {
  const [activeModule, setActiveModule] = useState('command-center');

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <ToastProvider>
          <div className="flex flex-col h-screen w-screen bg-background overflow-hidden text-foreground font-sans">
            <Header />
            <div className="flex flex-1 overflow-hidden">
              <Sidebar activeModule={activeModule} onSelectModule={setActiveModule} />
              <main className="flex-1 overflow-y-auto bg-background">
                {activeModule === 'diagnostics' ? (
                  <Diagnostics />
                ) : activeModule === 'desktop-diagnostics' ? (
                  <DesktopDiagnostics />
                ) : activeModule === 'storage' ? (
                  <Storage />
                ) : activeModule === 'design-system' ? (
                  <DesignSystemShowcase />
                ) : (
                  <Overview />
                )}
              </main>
            </div>
          </div>
        </ToastProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;
