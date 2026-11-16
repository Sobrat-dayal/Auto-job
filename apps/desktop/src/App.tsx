import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Header } from '@/components/Header';
import { Sidebar } from '@/components/Sidebar';
import { Overview } from '@/pages/Overview';

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
      <div className="flex flex-col h-screen w-screen bg-background overflow-hidden text-slate-100 font-sans">
        <Header />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar activeModule={activeModule} onSelectModule={setActiveModule} />
          <main className="flex-1 overflow-y-auto bg-background">
            <Overview />
          </main>
        </div>
      </div>
    </QueryClientProvider>
  );
};

export default App;
