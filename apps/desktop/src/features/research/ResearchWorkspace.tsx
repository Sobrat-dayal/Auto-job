import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ChartNoAxesCombined, Globe } from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleToolbar,
  ModuleTabs,
  ModuleUnavailableState,
  ModuleEmptyState,
} from '@/components/module';

export const ResearchWorkspace: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const getInitialTab = (): string => {
    if (location.pathname.includes('/research/web')) return 'web';
    if (location.pathname.includes('/research/companies')) return 'companies';
    if (location.pathname.includes('/research/markets')) return 'markets';
    if (location.pathname.includes('/research/reports')) return 'reports';
    if (location.pathname.includes('/research/watchlists')) return 'watchlists';
    return 'projects';
  };

  const [activeTab, setActiveTab] = React.useState<string>(getInitialTab());
  const [searchQuery, setSearchQuery] = React.useState('');

  React.useEffect(() => {
    setActiveTab(getInitialTab());
  }, [location.pathname]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === 'projects') navigate('/research/projects');
    else navigate(`/research/${tabId}`);
  };

  const tabs = [
    { id: 'projects', label: 'Research Dossiers' },
    { id: 'web', label: 'Web Intelligence Queries' },
    { id: 'companies', label: 'Company Profiles' },
    { id: 'markets', label: 'Market Compensation' },
    { id: 'reports', label: 'Synthesized Briefs', badge: 0 },
    { id: 'watchlists', label: 'Target Watchlists' },
  ];

  return (
    <ModulePage>
      <ModuleHeader
        title="Market Intelligence & Research"
        description="Deep company investigation, industry salary benchmarks, and cited competitive dossiers."
        icon={ChartNoAxesCombined}
        stageTag="Stage 44 Planned"
        badgeLabel="0 Active Dossiers"
        badgeVariant="outline"
      />

      <ModuleUnavailableState
        moduleName="Autonomous Market Intelligence & Research Engine"
        stageTag="Stage 44"
        stageName="Deep Research & Synthesis"
        description="Autonomous multi-source research, recursive query expansion, citation verification, and executive briefing compilation activate in Stage 44."
        plannedCapabilities={[
          'Multi-hop recursive web search & citation verification (Stage 44)',
          'Company technology stack & hiring velocity analysis (Stage 44)',
          'Verified compensation band aggregation (Stage 44)',
          'Automated research dossier export to PDF and Markdown (Stage 44)',
        ]}
      />

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={handleTabChange} />

      <ModuleToolbar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        searchPlaceholder="Filter dossiers or search company research..."
      />

      <ModuleEmptyState
        icon={Globe}
        title="No research dossiers created yet"
        description="Launch an autonomous research project to investigate target employers, market compensation, or engineering architectures."
      />
    </ModulePage>
  );
};

export default ResearchWorkspace;
