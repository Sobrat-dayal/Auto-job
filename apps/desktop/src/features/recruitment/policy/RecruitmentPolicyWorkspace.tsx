/**
 * Stage 25: Career Preference Intelligence, Job Eligibility Rules & Autonomous Decision Engine
 * Master Desktop Workspace Container.
 */

import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Compass,
  Briefcase,
  MapPin,
  DollarSign,
  Building2,
  GraduationCap,
  OctagonX,
  Sliders,
  ShieldCheck,
  Zap,
  Play,
  Layers,
} from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleTabs,
} from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type {
  CareerStrategy,
  RecruitmentBudget,
  AutonomyStatusResponse,
  StandingGrantRecord,
  ReviewQueueItem,
  RecruitmentDecision,
  CareerStrategyCreateRequest,
  CareerStrategyUpdateRequest,
  PolicySimulationRequest,
  PolicySimulationResponse,
  StandingGrantCreateRequest,
  AutonomyMode,
} from '@autonom/shared-types';

import { CareerOverviewTab } from './tabs/CareerOverviewTab';
import { CareerStrategiesTab } from './tabs/CareerStrategiesTab';
import { TargetRolesTab } from './tabs/TargetRolesTab';
import { LocationsGeographyTab } from './tabs/LocationsGeographyTab';
import { CompensationPreferencesTab } from './tabs/CompensationPreferencesTab';
import { EmployerRestrictionsTab } from './tabs/EmployerRestrictionsTab';
import { EligibilityRulesTab } from './tabs/EligibilityRulesTab';
import { HardConstraintsTab } from './tabs/HardConstraintsTab';
import { SoftPreferencesTab } from './tabs/SoftPreferencesTab';
import { AutonomyGrantsTab } from './tabs/AutonomyGrantsTab';
import { ApplicationBudgetsTab } from './tabs/ApplicationBudgetsTab';
import { PolicySimulatorTab } from './tabs/PolicySimulatorTab';

export const RecruitmentPolicyWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState<string>('overview');

  // 1. Fetch Strategies
  const { data: strategies = [], refetch: refetchStrategies } = useQuery<CareerStrategy[]>({
    queryKey: ['career-strategies-list'],
    queryFn: () => apiClient.listCareerStrategies(),
  });

  const activeStrategy = strategies.find((s) => s.is_active) || strategies[0] || null;

  // 2. Fetch Autonomy Status
  const { data: autonomyStatus = null, refetch: refetchAutonomy } = useQuery<AutonomyStatusResponse>({
    queryKey: ['recruitment-autonomy-status'],
    queryFn: () => apiClient.getAutonomyStatus(),
  });

  // 3. Fetch Budgets
  const { data: budget = null, refetch: refetchBudgets } = useQuery<RecruitmentBudget>({
    queryKey: ['recruitment-budgets'],
    queryFn: () => apiClient.getRecruitmentBudget(),
  });

  // 4. Fetch Standing Grants
  const { data: standingGrants = [], refetch: refetchGrants } = useQuery<StandingGrantRecord[]>({
    queryKey: ['standing-grants-list'],
    queryFn: () => apiClient.listStandingGrants(),
  });

  // 5. Fetch Review Queue
  const { data: reviewQueue = [], refetch: refetchQueue } = useQuery<ReviewQueueItem[]>({
    queryKey: ['recruitment-review-queue'],
    queryFn: () => apiClient.listReviewQueue(),
  });

  // 6. Fetch Recent Decisions
  const { data: recentDecisions = [] } = useQuery<RecruitmentDecision[]>({
    queryKey: ['recruitment-decisions-list'],
    queryFn: () => apiClient.listPolicyDecisions(20),
  });

  // Strategy Mutations
  const handleActivateStrategy = async (id: string) => {
    await apiClient.activateCareerStrategy(id);
    await refetchStrategies();
    await refetchAutonomy();
  };

  const handleCreateStrategy = async (req: CareerStrategyCreateRequest) => {
    await apiClient.createCareerStrategy(req);
    await refetchStrategies();
  };

  const handleUpdateStrategy = async (id: string, req: CareerStrategyUpdateRequest) => {
    await apiClient.updateCareerStrategy(id, req);
    await refetchStrategies();
  };

  const handleDeleteStrategy = async (id: string) => {
    await apiClient.deleteCareerStrategy(id);
    await refetchStrategies();
  };

  const handleFetchVersions = async (id: string) => {
    return apiClient.getStrategyVersions(id);
  };

  // Autonomy Mutations
  const handleSetAutonomyMode = async (mode: AutonomyMode) => {
    if (!activeStrategy) return;
    await apiClient.updateCareerStrategy(activeStrategy.id, { autonomy_mode: mode });
    await refetchStrategies();
    await refetchAutonomy();
  };

  const handleCreateStandingGrant = async (req: StandingGrantCreateRequest) => {
    await apiClient.createStandingGrant(req);
    await refetchGrants();
    await refetchAutonomy();
  };

  const handleRevokeStandingGrant = async (id: string, reason?: string) => {
    await apiClient.revokeStandingGrant(id, reason);
    await refetchGrants();
    await refetchAutonomy();
  };

  const handleResolveReviewItem = async (id: string, action: 'approve' | 'reject' | 'dismiss') => {
    await apiClient.resolveReviewQueueItem(id, { action });
    await refetchQueue();
  };

  // Budget Mutation
  const handleUpdateBudget = async (req: Partial<RecruitmentBudget>) => {
    await apiClient.updateRecruitmentBudget(req);
    await refetchBudgets();
  };

  // Simulation
  const handleSimulate = async (req: PolicySimulationRequest): Promise<PolicySimulationResponse> => {
    return apiClient.simulatePolicy(req);
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Compass },
    { id: 'strategies', label: 'Strategies', icon: Layers },
    { id: 'target-roles', label: 'Target Roles', icon: Briefcase },
    { id: 'locations', label: 'Locations', icon: MapPin },
    { id: 'compensation', label: 'Compensation', icon: DollarSign },
    { id: 'employers', label: 'Employers', icon: Building2 },
    { id: 'eligibility', label: 'Eligibility', icon: GraduationCap },
    { id: 'hard-constraints', label: 'Precedence', icon: OctagonX },
    { id: 'soft-preferences', label: 'Soft Scores', icon: Sliders },
    { id: 'autonomy', label: 'Autonomy', icon: ShieldCheck },
    { id: 'budgets', label: 'Budgets', icon: Zap },
    { id: 'simulator', label: 'Simulator', icon: Play },
  ];

  return (
    <ModulePage>
      <ModuleHeader
        title="Career Preferences, Eligibility Rules & Policy Engine"
        description="Autonomous recruitment governance: target role taxonomy, location & compensation floors, employer blocklists, factual eligibility invariants, multi-agent shared budgets, and explainable decision precedence."
        actions={
          <div className="flex items-center gap-2">
            <Badge variant="neutral" className="bg-cyan-950/80 text-cyan-400 border-cyan-800 text-xs font-mono">
              Strategy: {activeStrategy?.title || 'None'}
            </Badge>
            {reviewQueue.length > 0 && (
              <Badge variant="neutral" className="bg-amber-950/80 text-amber-400 border-amber-800 text-xs">
                {reviewQueue.length} Reviews Pending
              </Badge>
            )}
          </div>
        }
      />

      <ModuleTabs
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      <div className="mt-6">
        {activeTab === 'overview' && (
          <CareerOverviewTab
            activeStrategy={activeStrategy}
            autonomyStatus={autonomyStatus}
            budget={budget}
            recentDecisions={recentDecisions}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'strategies' && (
          <CareerStrategiesTab
            strategies={strategies}
            activeStrategy={activeStrategy}
            onActivateStrategy={handleActivateStrategy}
            onCreateStrategy={handleCreateStrategy}
            onDeleteStrategy={handleDeleteStrategy}
            onFetchVersions={handleFetchVersions}
          />
        )}

        {activeTab === 'target-roles' && (
          <TargetRolesTab
            strategy={activeStrategy}
            onUpdateStrategy={handleUpdateStrategy}
          />
        )}

        {activeTab === 'locations' && (
          <LocationsGeographyTab
            strategy={activeStrategy}
            onUpdateStrategy={handleUpdateStrategy}
          />
        )}

        {activeTab === 'compensation' && (
          <CompensationPreferencesTab
            strategy={activeStrategy}
            onUpdateStrategy={handleUpdateStrategy}
          />
        )}

        {activeTab === 'employers' && (
          <EmployerRestrictionsTab
            strategy={activeStrategy}
            onUpdateStrategy={handleUpdateStrategy}
          />
        )}

        {activeTab === 'eligibility' && (
          <EligibilityRulesTab
            strategy={activeStrategy}
            onUpdateStrategy={handleUpdateStrategy}
          />
        )}

        {activeTab === 'hard-constraints' && <HardConstraintsTab />}

        {activeTab === 'soft-preferences' && <SoftPreferencesTab />}

        {activeTab === 'autonomy' && (
          <AutonomyGrantsTab
            autonomyStatus={autonomyStatus}
            standingGrants={standingGrants}
            reviewQueue={reviewQueue}
            onSetAutonomyMode={handleSetAutonomyMode}
            onCreateStandingGrant={handleCreateStandingGrant}
            onRevokeStandingGrant={handleRevokeStandingGrant}
            onResolveReviewItem={handleResolveReviewItem}
          />
        )}

        {activeTab === 'budgets' && (
          <ApplicationBudgetsTab
            budget={budget}
            onUpdateBudget={handleUpdateBudget}
          />
        )}

        {activeTab === 'simulator' && (
          <PolicySimulatorTab onSimulate={handleSimulate} />
        )}
      </div>
    </ModulePage>
  );
};

export default RecruitmentPolicyWorkspace;
