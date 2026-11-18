import * as React from 'react';
import {
  Award,
  Plus,
  AlertTriangle,
} from 'lucide-react';
import { Card, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type {
  AutonomyMode,
  AutonomyStatusResponse,
  StandingGrantRecord,
  ReviewQueueItem,
  StandingGrantCreateRequest,
} from '@autonom/shared-types';

interface AutonomyGrantsTabProps {
  autonomyStatus: AutonomyStatusResponse | null;
  standingGrants: StandingGrantRecord[];
  reviewQueue: ReviewQueueItem[];
  onSetAutonomyMode: (mode: AutonomyMode) => Promise<void>;
  onCreateStandingGrant: (req: StandingGrantCreateRequest) => Promise<void>;
  onRevokeStandingGrant: (id: string, reason?: string) => Promise<void>;
  onResolveReviewItem: (id: string, action: 'approve' | 'reject' | 'dismiss') => Promise<void>;
}

export const AutonomyGrantsTab: React.FC<AutonomyGrantsTabProps> = ({
  autonomyStatus,
  standingGrants,
  reviewQueue,
  onSetAutonomyMode,
  onCreateStandingGrant,
  onRevokeStandingGrant,
  onResolveReviewItem,
}) => {
  const [showGrantModal, setShowGrantModal] = React.useState(false);
  const [grantRole, setGrantRole] = React.useState('application_agent');
  const [grantScope, setGrantScope] = React.useState('prepare_application');
  const [grantDailyCap, setGrantDailyCap] = React.useState(5);

  const activeMode = autonomyStatus?.active_autonomy_mode || 'mode_2_prepare_and_review';

  const modes: { mode: AutonomyMode; title: string; desc: string; color: string }[] = [
    {
      mode: 'mode_1_research_only',
      title: 'Mode 1: Research Only',
      desc: 'Agents discover and evaluate listings; zero document drafting or submission permitted.',
      color: 'border-blue-800 text-blue-300',
    },
    {
      mode: 'mode_2_prepare_and_review',
      title: 'Mode 2: Prepare & Review (Default)',
      desc: 'Agents tailor resumes, generate cover letters, and prepare screening answers. Every submission requires explicit human review and click.',
      color: 'border-emerald-600 text-emerald-300',
    },
    {
      mode: 'mode_3_preauthorized_preparation',
      title: 'Mode 3: Preauthorized Preparation',
      desc: 'Preparation occurs continuously under scoped standing grants without human review interruptions.',
      color: 'border-purple-600 text-purple-300',
    },
    {
      mode: 'mode_4_bounded_autonomous_applications',
      title: 'Mode 4: Bounded Autonomous',
      desc: 'Submissions proceed autonomously only when all 10 precedence invariants pass with 100% confidence, zero sensitive questions, and within daily budgets.',
      color: 'border-amber-600 text-amber-300',
    },
  ];

  const handleCreateGrant = async () => {
    await onCreateStandingGrant({
      grantee_role: grantRole,
      scope: grantScope,
      max_actions_per_day: Number(grantDailyCap),
    });
    setShowGrantModal(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-semibold text-slate-200">Recruitment Autonomy Modes & Scoped Standing Grants</h3>
        <p className="text-xs text-slate-400">
          Control the exact boundary of what specialist agents can do autonomously. Scoped standing grants permit routine preparation while keeping critical decisions under human control.
        </p>
      </div>

      {/* Mode Selector */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {modes.map((m) => {
          const isSelected = activeMode === m.mode;
          return (
            <div
              key={m.mode}
              onClick={() => onSetAutonomyMode(m.mode)}
              className={`p-4 rounded-lg border cursor-pointer transition-all ${
                isSelected
                  ? `bg-slate-900 ${m.color} ring-1 ring-cyan-500`
                  : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-bold text-xs">{m.title}</span>
                {isSelected && (
                  <Badge variant="neutral" className="bg-cyan-950/80 text-cyan-400 border-cyan-700 text-[10px]">
                    ACTIVE
                  </Badge>
                )}
              </div>
              <p className="text-[11px] opacity-80 leading-relaxed">{m.desc}</p>
            </div>
          );
        })}
      </div>

      {/* Review Queue */}
      <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xs font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            Human Review Queue ({reviewQueue.length} Pending)
          </CardTitle>
        </div>

        {reviewQueue.length === 0 ? (
          <p className="text-xs text-slate-500 py-4 text-center">
            Review queue is empty. No job applications currently require manual sign-off.
          </p>
        ) : (
          <div className="space-y-2 text-xs">
            {reviewQueue.map((item) => (
              <div
                key={item.id}
                className="p-3 rounded bg-slate-950/60 border border-slate-800 flex items-center justify-between"
              >
                <div>
                  <div className="font-bold text-slate-200">
                    {item.job_title} &bull; {item.employer_name}
                  </div>
                  <p className="text-slate-400 text-[11px] mt-0.5">{item.decision_summary}</p>
                  <div className="flex items-center gap-1.5 mt-1.5">
                    {item.triggers.map((t, idx) => (
                      <Badge
                        key={idx}
                        variant="neutral"
                        className="bg-amber-950/60 text-amber-400 border-amber-800 text-[10px]"
                      >
                        {t.replace(/_/g, ' ')}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    className="h-7 text-xs bg-emerald-700 hover:bg-emerald-600 text-white"
                    onClick={() => onResolveReviewItem(item.id, 'approve')}
                  >
                    Approve
                  </Button>
                  <Button
                    size="sm"
                    className="h-7 text-xs bg-rose-800 hover:bg-rose-700 text-white"
                    onClick={() => onResolveReviewItem(item.id, 'reject')}
                  >
                    Reject
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Standing Grants Management */}
      <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xs font-semibold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
            <Award className="w-4 h-4" />
            Active Standing Grants ({standingGrants.filter((g) => !g.is_revoked).length})
          </CardTitle>
          <Button
            size="sm"
            className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs h-7 flex items-center gap-1"
            onClick={() => setShowGrantModal(true)}
          >
            <Plus className="w-3.5 h-3.5" />
            Issue Grant
          </Button>
        </div>

        {/* Issue Grant Modal */}
        {showGrantModal && (
          <div className="p-3 bg-slate-950 border border-cyan-800 rounded space-y-3 text-xs">
            <span className="font-bold text-cyan-300 block">Issue New Standing Grant</span>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label className="text-slate-400 block mb-1">Grantee Role</label>
                <select
                  value={grantRole}
                  onChange={(e) => setGrantRole(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-200"
                >
                  <option value="application_agent">Application Agent</option>
                  <option value="research_agent">Research Agent</option>
                  <option value="resume_agent">Resume Tailoring Agent</option>
                </select>
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Scope</label>
                <Input
                  value={grantScope}
                  onChange={(e) => setGrantScope(e.target.value)}
                  className="bg-slate-900 border-slate-700 text-xs"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Daily Cap</label>
                <Input
                  type="number"
                  value={grantDailyCap}
                  onChange={(e) => setGrantDailyCap(Number(e.target.value))}
                  className="bg-slate-900 border-slate-700 text-xs"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-1">
              <Button
                variant="ghost"
                size="sm"
                className="text-xs text-slate-400 h-6"
                onClick={() => setShowGrantModal(false)}
              >
                Cancel
              </Button>
              <Button
                size="sm"
                className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs h-6"
                onClick={handleCreateGrant}
              >
                Confirm Grant
              </Button>
            </div>
          </div>
        )}

        <div className="space-y-2 text-xs">
          {standingGrants.map((g) => (
            <div
              key={g.id}
              className={`p-2.5 rounded border flex items-center justify-between ${
                g.is_revoked
                  ? 'bg-slate-950/30 border-slate-800/40 text-slate-500'
                  : 'bg-slate-950/60 border-slate-800 text-slate-300'
              }`}
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-bold">{g.grantee_role}</span>
                  <Badge variant="neutral" className="text-[10px] font-mono">
                    Scope: {g.scope}
                  </Badge>
                  {g.is_revoked && (
                    <Badge variant="neutral" className="bg-rose-950/60 text-rose-400 border-rose-800 text-[10px]">
                      REVOKED
                    </Badge>
                  )}
                </div>
                <div className="text-[11px] text-slate-400 mt-0.5">
                  Usage: {g.actions_taken_today} / {g.max_actions_per_day} actions today
                </div>
              </div>

              {!g.is_revoked && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-xs text-rose-400 hover:text-rose-300 h-6"
                  onClick={() => onRevokeStandingGrant(g.id, 'User manual revocation')}
                >
                  Revoke
                </Button>
              )}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
