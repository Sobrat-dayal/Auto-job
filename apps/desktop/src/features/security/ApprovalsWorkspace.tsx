import * as React from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Pause,
  Play,
  KeyRound,
  ChevronRight,
} from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleToolbar,
  ModuleTabs,
  ModuleLoadingState,
  ModuleEmptyState,
} from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';
import type {
  ApprovalMode,
  ApprovalRequest,
  AuthorizationGrant,
  AuthorizationPolicy,
  EmergencyStopState,
  RiskLevel,
  SecurityAuditEntry,
} from '@autonom/shared-types';

export const ApprovalsWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState<string>('pending');
  const [searchQuery, setSearchQuery] = React.useState('');

  // Data states
  const [approvals, setApprovals] = React.useState<ApprovalRequest[]>([]);
  const [policies, setPolicies] = React.useState<AuthorizationPolicy[]>([]);
  const [grants, setGrants] = React.useState<AuthorizationGrant[]>([]);
  const [auditLogs, setAuditLogs] = React.useState<SecurityAuditEntry[]>([]);
  const [emergencyState, setEmergencyState] = React.useState<EmergencyStopState | null>(null);

  const [isLoading, setIsLoading] = React.useState(true);
  const [isRefreshing, setIsRefreshing] = React.useState(false);
  const [actionInProgress, setActionInProgress] = React.useState<string | null>(null);
  const [selectedApproval, setSelectedApproval] = React.useState<ApprovalRequest | null>(null);

  // Emergency stop confirmation dialog
  const [showEmergencyModal, setShowEmergencyModal] = React.useState(false);
  const [emergencyReason, setEmergencyReason] = React.useState('');

  const loadData = React.useCallback(async () => {
    try {
      const [apprRes, polRes, grantRes, auditRes, emRes] = await Promise.all([
        apiClient.listApprovals().catch(() => []),
        apiClient.listPolicies().catch(() => []),
        apiClient.listGrants().catch(() => []),
        apiClient.listSecurityAuditLogs({ limit: 50 }).catch(() => []),
        apiClient.getEmergencyStopStatus().catch(() => null),
      ]);
      setApprovals(apprRes);
      setPolicies(polRes);
      setGrants(grantRes);
      setAuditLogs(auditRes);
      if (emRes) setEmergencyState(emRes);
    } catch (err) {
      console.error('Failed to load security data', err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  React.useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, [loadData]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadData();
  };

  const handleApprove = async (id: string, mode: ApprovalMode = 'one_time') => {
    setActionInProgress(id);
    try {
      await apiClient.approveRequest(id, {
        approval_mode: mode,
        reason: `Approved by user from Approvals Workspace (${mode})`,
        valid_until_seconds: mode === 'session' ? 3600 : undefined,
      });
      await loadData();
      if (selectedApproval?.id === id) {
        setSelectedApproval(null);
      }
    } catch (err) {
      console.error('Failed to approve request', err);
    } finally {
      setActionInProgress(null);
    }
  };

  const handleDeny = async (id: string) => {
    setActionInProgress(id);
    try {
      await apiClient.denyRequest(id, {
        reason: 'Denied by user from Approvals Workspace',
      });
      await loadData();
      if (selectedApproval?.id === id) {
        setSelectedApproval(null);
      }
    } catch (err) {
      console.error('Failed to deny request', err);
    } finally {
      setActionInProgress(null);
    }
  };

  const handleEmergencyStopToggle = async () => {
    if (!emergencyState) return;
    setActionInProgress('emergency');
    try {
      if (emergencyState.is_active) {
        const state = await apiClient.clearEmergencyStop();
        setEmergencyState(state);
      } else {
        const state = await apiClient.activateEmergencyStop(emergencyReason || 'Operator Emergency Stop');
        setEmergencyState(state);
      }
      setShowEmergencyModal(false);
      setEmergencyReason('');
      await loadData();
    } catch (err) {
      console.error('Emergency stop toggle failed', err);
    } finally {
      setActionInProgress(null);
    }
  };

  const handleAutomationPauseToggle = async () => {
    if (!emergencyState) return;
    setActionInProgress('pause');
    try {
      if (emergencyState.is_paused) {
        const state = await apiClient.resumeAutomation();
        setEmergencyState(state);
      } else {
        const state = await apiClient.pauseAutomation('Operator manual pause');
        setEmergencyState(state);
      }
      await loadData();
    } catch (err) {
      console.error('Pause toggle failed', err);
    } finally {
      setActionInProgress(null);
    }
  };

  const handleRevokeGrant = async (grantId: string) => {
    setActionInProgress(grantId);
    try {
      await apiClient.revokeGrant(grantId, 'Revoked by user');
      await loadData();
    } catch (err) {
      console.error('Failed to revoke grant', err);
    } finally {
      setActionInProgress(null);
    }
  };

  const handleRevokePolicy = async (policyId: string) => {
    setActionInProgress(policyId);
    try {
      await apiClient.revokePolicy(policyId);
      await loadData();
    } catch (err) {
      console.error('Failed to revoke policy', err);
    } finally {
      setActionInProgress(null);
    }
  };

  const pendingApprovals = approvals.filter((a) => a.status === 'pending');
  const approvedApprovals = approvals.filter((a) => a.status === 'approved' || a.status === 'consumed');
  const deniedApprovals = approvals.filter((a) => a.status === 'denied');

  const filteredApprovals = (
    activeTab === 'pending'
      ? pendingApprovals
      : activeTab === 'approved'
        ? approvedApprovals
        : activeTab === 'denied'
          ? deniedApprovals
          : approvals
  ).filter((a) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      a.capability_id.toLowerCase().includes(q) ||
      a.action.toLowerCase().includes(q) ||
      (a.agent_id && a.agent_id.toLowerCase().includes(q)) ||
      (a.workflow_id && a.workflow_id.toLowerCase().includes(q)) ||
      a.reason.toLowerCase().includes(q)
    );
  });

  const getRiskBadge = (risk: RiskLevel) => {
    switch (risk) {
      case 'critical':
        return <Badge className="bg-rose-500/20 text-rose-300 border-rose-500/40 uppercase font-mono">Critical</Badge>;
      case 'high':
        return <Badge className="bg-amber-500/20 text-amber-300 border-amber-500/40 uppercase font-mono">High Risk</Badge>;
      case 'moderate':
        return <Badge className="bg-sky-500/20 text-sky-300 border-sky-500/40 uppercase font-mono">Moderate</Badge>;
      default:
        return <Badge className="bg-emerald-500/20 text-emerald-300 border-emerald-500/40 uppercase font-mono">Low Risk</Badge>;
    }
  };

  return (
    <ModulePage>
      {/* Global Emergency Stop Pulsing Banner */}
      {emergencyState?.is_active && (
        <div className="bg-rose-600/90 text-white p-3 px-4 flex items-center justify-between shadow-lg animate-pulse">
          <div className="flex items-center gap-3">
            <ShieldAlert className="h-6 w-6 shrink-0" />
            <div>
              <p className="font-bold text-sm">EMERGENCY STOP ACTIVE</p>
              <p className="text-xs text-rose-100">
                All autonomous background workflows and sensitive operations are completely blocked.
                Reason: {emergencyState.reason || 'Manual user trigger'}
              </p>
            </div>
          </div>
          <Button
            size="sm"
            variant="outline"
            className="bg-white text-rose-700 hover:bg-rose-50 border-transparent font-semibold text-xs"
            onClick={() => handleEmergencyStopToggle()}
            disabled={actionInProgress === 'emergency'}
          >
            Disengage Emergency Stop
          </Button>
        </div>
      )}

      {/* Automation Paused Notification Banner */}
      {!emergencyState?.is_active && emergencyState?.is_paused && (
        <div className="bg-amber-500/20 border-b border-amber-500/40 text-amber-200 p-2.5 px-4 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <Pause className="h-4 w-4 text-amber-400" />
            <span>Automation dispatch is paused. Running workflows will finish, but no new tasks will execute.</span>
          </div>
          <Button
            size="sm"
            variant="ghost"
            className="h-7 text-amber-300 hover:bg-amber-500/20 text-xs"
            onClick={handleAutomationPauseToggle}
            disabled={actionInProgress === 'pause'}
          >
            Resume Automation
          </Button>
        </div>
      )}

      <ModuleHeader
        title="Authorization & Approvals Engine"
        description="Deterministic policy enforcement, human-in-the-loop approval queue, standing grants, and hard emergency stop controls."
        icon={ShieldAlert}
        stageTag="Stage 14 Authorization Engine"
        actions={
          <div className="flex items-center gap-2">
            {/* Automation Pause Button */}
            <Button
              size="sm"
              variant="outline"
              onClick={handleAutomationPauseToggle}
              disabled={actionInProgress === 'pause' || emergencyState?.is_active}
              className={`h-8 text-xs gap-1.5 ${
                emergencyState?.is_paused
                  ? 'border-amber-500/40 bg-amber-500/10 text-amber-300'
                  : 'text-muted-foreground'
              }`}
            >
              {emergencyState?.is_paused ? <Play className="h-3.5 w-3.5" /> : <Pause className="h-3.5 w-3.5" />}
              {emergencyState?.is_paused ? 'Resume Dispatch' : 'Pause Dispatch'}
            </Button>

            {/* Emergency Stop Button */}
            <Button
              size="sm"
              variant={emergencyState?.is_active ? 'primary' : 'destructive'}
              onClick={() => setShowEmergencyModal(true)}
              disabled={actionInProgress === 'emergency'}
              className="h-8 text-xs gap-1.5 font-semibold"
            >
              <ShieldAlert className="h-3.5 w-3.5" />
              {emergencyState?.is_active ? 'Disengage Stop' : 'Emergency Stop'}
            </Button>

            {/* Sync Button */}
            <Button
              size="sm"
              variant="outline"
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="h-8 text-xs gap-1"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
              Sync
            </Button>
          </div>
        }
      />

      <ModuleToolbar
        searchPlaceholder="Search action, agent, capability..."
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />

      <ModuleTabs
        tabs={[
          { id: 'pending', label: 'Pending Approvals', badge: pendingApprovals.length },
          { id: 'approved', label: 'Approved', badge: approvedApprovals.length },
          { id: 'denied', label: 'Denied', badge: deniedApprovals.length },
          { id: 'all', label: 'All Requests', badge: approvals.length },
          { id: 'policies', label: 'Security Policies', badge: policies.length },
          { id: 'grants', label: 'Standing Grants', badge: grants.length },
          { id: 'audit', label: 'Audit Ledger', badge: auditLogs.length },
        ]}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {/* Main Content Area */}
      <div className="p-6">
        {isLoading ? (
          <ModuleLoadingState rows={4} layout="cards" />
        ) : activeTab === 'policies' ? (
          /* Policies Tab */
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-sm font-semibold">Configured Authorization Policies</h3>
                <p className="text-xs text-muted-foreground">
                  Baseline system policies and user rules evaluated deterministically before any tool or agent action.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {policies.map((pol) => (
                <Card key={pol.id} className="border-border/60 bg-card/60 backdrop-blur">
                  <CardHeader className="p-4 pb-2">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-sm font-medium">{pol.name}</CardTitle>
                          {pol.is_system && (
                            <Badge variant="outline" className="text-[10px] bg-primary/10 text-primary border-primary/20">
                              System Baseline
                            </Badge>
                          )}
                        </div>
                        <CardDescription className="text-xs mt-1">{pol.description}</CardDescription>
                      </div>
                      <Badge
                        variant={pol.effect === 'allow' ? 'outline' : pol.effect === 'deny' ? 'error' : 'warning'}
                        className="uppercase text-[10px] font-mono shrink-0"
                      >
                        {pol.effect}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="p-4 pt-2 space-y-2 text-xs">
                    <div className="grid grid-cols-2 gap-2 text-muted-foreground">
                      <div>Subject: <span className="text-foreground font-mono">{pol.subject_scope}</span></div>
                      <div>Category: <span className="text-foreground font-mono">{pol.category_scope}</span></div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Action Scope:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {pol.action_scope.slice(0, 5).map((act) => (
                          <Badge key={act} variant="outline" className="text-[9px] font-mono">
                            {act}
                          </Badge>
                        ))}
                        {pol.action_scope.length > 5 && (
                          <span className="text-[10px] text-muted-foreground self-center">
                            +{pol.action_scope.length - 5} more
                          </span>
                        )}
                      </div>
                    </div>
                    {!pol.is_system && pol.is_enabled && (
                      <div className="pt-2 flex justify-end">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleRevokePolicy(pol.id)}
                          disabled={actionInProgress === pol.id}
                          className="h-7 text-xs text-rose-400 hover:bg-rose-500/10"
                        >
                          Revoke Policy
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ) : activeTab === 'grants' ? (
          /* Grants Tab */
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold">Preauthorized Autonomy Grants</h3>
              <p className="text-xs text-muted-foreground">
                Standing or workflow-scoped authorizations allowing specialist agents bounded autonomy without repeated human prompts.
              </p>
            </div>

            {grants.length === 0 ? (
              <ModuleEmptyState
                icon={KeyRound}
                title="No Active Autonomy Grants"
                description="Create standing grants to authorize recurring low/moderate operations."
              />
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {grants.map((grant) => (
                  <Card key={grant.id} className="border-border/60 bg-card/60 backdrop-blur">
                    <CardHeader className="p-4 pb-2">
                      <div className="flex items-start justify-between gap-2">
                        <CardTitle className="text-sm font-semibold">{grant.name}</CardTitle>
                        <Badge variant={grant.is_revoked ? 'error' : 'outline'} className="text-[10px] font-mono">
                          {grant.is_revoked ? 'Revoked' : grant.grant_type}
                        </Badge>
                      </div>
                      {grant.description && (
                        <CardDescription className="text-xs">{grant.description}</CardDescription>
                      )}
                    </CardHeader>
                    <CardContent className="p-4 pt-2 space-y-2 text-xs">
                      <div className="text-muted-foreground">
                        Subject: <span className="text-foreground font-mono">{grant.subject_id}</span>
                      </div>
                      <div className="text-muted-foreground">
                        Usage: <span className="text-foreground font-mono">{grant.use_count} / {grant.max_uses ?? '∞'}</span>
                      </div>
                      {grant.expires_at && (
                        <div className="text-muted-foreground">
                          Expires: <span className="text-foreground font-mono">{new Date(grant.expires_at).toLocaleString()}</span>
                        </div>
                      )}
                      {!grant.is_revoked && (
                        <div className="pt-2 flex justify-end">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleRevokeGrant(grant.id)}
                            disabled={actionInProgress === grant.id}
                            className="h-7 text-xs text-rose-400 border-rose-500/30 hover:bg-rose-500/10"
                          >
                            Revoke Grant
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        ) : activeTab === 'audit' ? (
          /* Audit Ledger Tab */
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold">Security & Authorization Audit Ledger</h3>
              <p className="text-xs text-muted-foreground">
                Tamper-evident log of all deterministic authorization decisions, policy triggers, and emergency stop actions.
              </p>
            </div>

            <div className="border border-border/60 rounded-lg overflow-hidden bg-card/60">
              <table className="w-full text-xs">
                <thead className="bg-muted/40 border-b border-border/60 text-muted-foreground text-left">
                  <tr>
                    <th className="p-2.5 font-medium">Timestamp</th>
                    <th className="p-2.5 font-medium">Actor</th>
                    <th className="p-2.5 font-medium">Capability / Action</th>
                    <th className="p-2.5 font-medium">Outcome</th>
                    <th className="p-2.5 font-medium">Reason Code</th>
                    <th className="p-2.5 font-medium">Explanation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/40">
                  {auditLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-muted/20">
                      <td className="p-2.5 font-mono text-[11px] text-muted-foreground whitespace-nowrap">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="p-2.5 font-mono text-foreground font-medium">
                        {log.agent_id || log.actor_id}
                      </td>
                      <td className="p-2.5 font-mono text-muted-foreground truncate max-w-xs">
                        {log.action || log.capability_id}
                      </td>
                      <td className="p-2.5">
                        <Badge
                          variant={log.outcome === 'allow' ? 'outline' : log.outcome === 'deny' ? 'error' : 'warning'}
                          className="text-[10px] uppercase font-mono"
                        >
                          {log.outcome}
                        </Badge>
                      </td>
                      <td className="p-2.5 font-mono text-[11px] text-amber-300">
                        {log.reason_code}
                      </td>
                      <td className="p-2.5 text-muted-foreground truncate max-w-sm">
                        {log.explanation}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          /* Approvals Queue Cards (Pending, Approved, Denied, All) */
          <div className="space-y-4">
            {filteredApprovals.length === 0 ? (
              <ModuleEmptyState
                icon={ShieldCheck}
                title={
                  activeTab === 'pending'
                    ? 'No Pending Approvals'
                    : 'No Approval Requests Found'
                }
                description={
                  activeTab === 'pending'
                    ? 'All autonomous multi-agent tasks are operating within authorized bounds.'
                    : 'No requests matched the current filter criteria.'
                }
              />
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {filteredApprovals.map((req) => (
                  <Card
                    key={req.id}
                    className={`border transition-all ${
                      req.status === 'pending'
                        ? 'border-amber-500/40 bg-amber-500/5 hover:border-amber-500/60'
                        : req.status === 'approved'
                          ? 'border-emerald-500/40 bg-card/60'
                          : req.status === 'consumed'
                            ? 'border-border/60 bg-muted/10 opacity-75'
                            : 'border-rose-500/40 bg-rose-500/5'
                    }`}
                  >
                    <CardHeader className="p-4 pb-2">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="flex items-center gap-2">
                            <CardTitle className="text-sm font-semibold font-mono">
                              {req.capability_id}
                            </CardTitle>
                            {getRiskBadge(req.risk_level)}
                          </div>
                          <CardDescription className="text-xs mt-1 text-foreground/90">
                            {req.reason}
                          </CardDescription>
                        </div>
                        <Badge
                          variant={
                            req.status === 'pending'
                              ? 'warning'
                              : req.status === 'approved'
                                ? 'outline'
                                : req.status === 'consumed'
                                  ? 'neutral'
                                  : 'error'
                          }
                          className="uppercase text-[10px] font-mono shrink-0"
                        >
                          {req.status}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="p-4 pt-2 space-y-3 text-xs">
                      {/* Context metadata */}
                      <div className="grid grid-cols-2 gap-2 text-muted-foreground p-2 rounded bg-muted/30 border border-border/40 font-mono text-[11px]">
                        <div>Agent: <span className="text-foreground">{req.agent_id || 'System'}</span></div>
                        <div>Workflow: <span className="text-foreground">{req.workflow_id || 'Standalone'}</span></div>
                        <div>Requested: <span className="text-foreground">{new Date(req.requested_at).toLocaleTimeString()}</span></div>
                        <div>Expires: <span className="text-foreground">{new Date(req.expires_at).toLocaleTimeString()}</span></div>
                      </div>

                      {/* Parameters digest preview */}
                      <div className="text-[11px] text-muted-foreground font-mono flex items-center justify-between">
                        <span>Digest: {req.parameters_digest.slice(0, 16)}...</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedApproval(req)}
                          className="h-6 text-[11px] text-primary p-1"
                        >
                          Inspect Payload <ChevronRight className="h-3 w-3 ml-1" />
                        </Button>
                      </div>

                      {/* Pending Action Buttons */}
                      {req.status === 'pending' && (
                        <div className="flex items-center gap-2 pt-1 border-t border-border/30">
                          <Button
                            size="sm"
                            onClick={() => handleApprove(req.id, 'one_time')}
                            disabled={actionInProgress === req.id || emergencyState?.is_active}
                            className="h-7 text-xs bg-emerald-600 hover:bg-emerald-700 text-white flex-1"
                          >
                            <CheckCircle2 className="h-3.5 w-3.5 mr-1" />
                            Approve (One-Time)
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleApprove(req.id, 'session')}
                            disabled={actionInProgress === req.id || emergencyState?.is_active}
                            className="h-7 text-xs border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/10"
                          >
                            Approve (1h Session)
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDeny(req.id)}
                            disabled={actionInProgress === req.id}
                            className="h-7 text-xs border-rose-500/40 text-rose-400 hover:bg-rose-500/10"
                          >
                            <XCircle className="h-3.5 w-3.5 mr-1" />
                            Deny
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Payload Inspector Modal / Dialog */}
      {selectedApproval && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-card border border-border/80 rounded-xl max-w-xl w-full p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-base font-semibold">Approval Parameter Inspector</h3>
                <p className="text-xs text-muted-foreground font-mono">
                  ID: {selectedApproval.id} | Action: {selectedApproval.action}
                </p>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setSelectedApproval(null)}>✕</Button>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-muted-foreground uppercase">Cryptographic Digest (SHA-256)</label>
              <div className="p-2 rounded bg-muted/40 font-mono text-[11px] break-all border border-border/40">
                {selectedApproval.parameters_digest}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-muted-foreground uppercase">Parameters Payload</label>
              <pre className="p-3 rounded bg-muted/40 font-mono text-xs max-h-56 overflow-y-auto border border-border/40">
                {JSON.stringify(selectedApproval.parameters_payload, null, 2)}
              </pre>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-border/40">
              {selectedApproval.status === 'pending' && (
                <>
                  <Button
                    size="sm"
                    variant="outline"
                    className="border-rose-500/40 text-rose-400 hover:bg-rose-500/10 text-xs"
                    onClick={() => handleDeny(selectedApproval.id)}
                  >
                    Deny Request
                  </Button>
                  <Button
                    size="sm"
                    className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs"
                    onClick={() => handleApprove(selectedApproval.id, 'one_time')}
                  >
                    Approve Once
                  </Button>
                </>
              )}
              <Button size="sm" variant="secondary" onClick={() => setSelectedApproval(null)}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Emergency Stop Confirmation Modal */}
      {showEmergencyModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-card border border-rose-500/60 rounded-xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center gap-3 text-rose-500">
              <ShieldAlert className="h-8 w-8 shrink-0" />
              <div>
                <h3 className="text-base font-bold text-foreground">
                  {emergencyState?.is_active ? 'Disengage Emergency Stop?' : 'Trigger Global Emergency Stop?'}
                </h3>
                <p className="text-xs text-muted-foreground">Fail-closed operator execution boundary</p>
              </div>
            </div>

            <p className="text-xs text-muted-foreground leading-relaxed">
              {emergencyState?.is_active
                ? 'Clearing Emergency Stop will allow autonomous dispatches and tool executions to resume. Ensure all unexpected agent actions have been resolved.'
                : 'Engaging Emergency Stop immediately aborts all active workflow steps, terminates background agent tools, freezes the approval queue, and halts all autonomous operations. This persists across restarts.'}
            </p>

            {!emergencyState?.is_active && (
              <div className="space-y-1">
                <label className="text-xs font-medium">Reason for Stop (Audit Ledger)</label>
                <Input
                  placeholder="e.g. Unintended external email draft detected..."
                  value={emergencyReason}
                  onChange={(e) => setEmergencyReason(e.target.value)}
                  className="text-xs bg-muted/40"
                />
              </div>
            )}

            <div className="flex justify-end gap-2 pt-2 border-t border-border/40">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowEmergencyModal(false)}
                disabled={actionInProgress === 'emergency'}
              >
                Cancel
              </Button>
              <Button
                size="sm"
                variant={emergencyState?.is_active ? 'primary' : 'destructive'}
                onClick={handleEmergencyStopToggle}
                disabled={actionInProgress === 'emergency'}
                className="font-bold text-xs"
              >
                {emergencyState?.is_active ? 'Confirm Disengage' : 'ENGAGE EMERGENCY STOP'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </ModulePage>
  );
};

export default ApprovalsWorkspace;
