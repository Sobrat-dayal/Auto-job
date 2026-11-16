import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Code2, FolderGit2 } from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleTabs,
  ModuleUnavailableState,
  ModuleEmptyState,
} from '@/components/module';

export const CodingWorkspace: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const getInitialTab = (): string => {
    if (location.pathname.includes('/coding/agents')) return 'agents';
    if (location.pathname.includes('/coding/repos')) return 'repos';
    if (location.pathname.includes('/coding/builds')) return 'builds';
    if (location.pathname.includes('/coding/reviews')) return 'reviews';
    return 'projects';
  };

  const [activeTab, setActiveTab] = React.useState<string>(getInitialTab());

  React.useEffect(() => {
    setActiveTab(getInitialTab());
  }, [location.pathname]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === 'projects') navigate('/coding/projects');
    else navigate(`/coding/${tabId}`);
  };

  const tabs = [
    { id: 'projects', label: 'Local Projects' },
    { id: 'agents', label: 'Coding Personas' },
    { id: 'repos', label: 'Git Repositories' },
    { id: 'builds', label: 'Build & Test Runs', badge: 0 },
    { id: 'reviews', label: 'Code Review Diffs' },
  ];

  return (
    <ModulePage>
      <ModuleHeader
        title="Software Engineering & Coding Studio"
        description="Autonomous code writing, repository maintenance, bug fixing, and test execution."
        icon={Code2}
        stageTag="Stage 41 Planned"
        badgeLabel="0 Active Builds"
        badgeVariant="outline"
      />

      <ModuleUnavailableState
        moduleName="Autonomous Coding & Git Workflow Suite"
        stageTag="Stage 41"
        stageName="Software Development & Test Engine"
        description="Autonomous multi-file editing, AST transformations, automated test execution, and Git branch management will activate in Stage 41. All filesystem modifications execute in sandboxed environments with clean commit staging."
        plannedCapabilities={[
          'Multi-file architectural feature generation (Stage 41)',
          'Automated test runner and self-correcting fix loops (Stage 41)',
          'Local Git branch creation and verified diff previews (Stage 41)',
          'Multi-repo dependency graph visualization (Stage 41)',
        ]}
      />

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={handleTabChange} />

      <ModuleEmptyState
        icon={FolderGit2}
        title="No active coding projects"
        description="Add a repository or workspace directory to allow AUTONOM coding agents to assist with architecture, features, and test coverage."
        actionLabel="Configure Workspace"
        onAction={() => navigate('/settings/storage')}
      />
    </ModulePage>
  );
};

export default CodingWorkspace;
