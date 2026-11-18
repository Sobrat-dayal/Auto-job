import * as React from 'react';
import {
  ShieldBan,
  Plus,
  Trash2,
} from 'lucide-react';
import { Card, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type {
  CareerStrategy,
  BlockedEmployerItem,
  AllowlistMode,
  CareerStrategyUpdateRequest,
} from '@autonom/shared-types';

interface EmployerRestrictionsTabProps {
  strategy: CareerStrategy | null;
  onUpdateStrategy: (id: string, req: CareerStrategyUpdateRequest) => Promise<void>;
}

export const EmployerRestrictionsTab: React.FC<EmployerRestrictionsTabProps> = ({
  strategy,
  onUpdateStrategy,
}) => {
  const [allowlistMode, setAllowlistMode] = React.useState<AllowlistMode>(
    strategy?.employers.allowlist_mode || 'no_allowlist'
  );
  const [blockedEmployers, setBlockedEmployers] = React.useState<BlockedEmployerItem[]>(
    strategy?.employers.blocked_employers || []
  );
  const [blockedIndustries, setBlockedIndustries] = React.useState(
    strategy?.employers.blocked_industries.join(', ') || ''
  );
  const [newBlockedName, setNewBlockedName] = React.useState('');
  const [newBlockedReason, setNewBlockedReason] = React.useState('');
  const [newBlockedDomain, setNewBlockedDomain] = React.useState('');

  React.useEffect(() => {
    if (strategy) {
      setAllowlistMode(strategy.employers.allowlist_mode);
      setBlockedEmployers(strategy.employers.blocked_employers);
      setBlockedIndustries(strategy.employers.blocked_industries.join(', '));
    }
  }, [strategy]);

  const handleAddBlocked = async () => {
    if (!newBlockedName.trim() || !strategy) return;
    const item: BlockedEmployerItem = {
      name: newBlockedName.trim(),
      reason: newBlockedReason.trim() || 'User specified block',
      domain: newBlockedDomain.trim() || undefined,
      blocked_at: new Date().toISOString(),
    };
    const updated = [...blockedEmployers, item];
    setBlockedEmployers(updated);
    await onUpdateStrategy(strategy.id, {
      employers: {
        ...strategy.employers,
        blocked_employers: updated,
      },
    });
    setNewBlockedName('');
    setNewBlockedReason('');
    setNewBlockedDomain('');
  };

  const handleRemoveBlocked = async (index: number) => {
    if (!strategy) return;
    const updated = blockedEmployers.filter((_, idx) => idx !== index);
    setBlockedEmployers(updated);
    await onUpdateStrategy(strategy.id, {
      employers: {
        ...strategy.employers,
        blocked_employers: updated,
      },
    });
  };

  const handleSaveMode = async (mode: AllowlistMode) => {
    if (!strategy) return;
    setAllowlistMode(mode);
    await onUpdateStrategy(strategy.id, {
      employers: {
        ...strategy.employers,
        allowlist_mode: mode,
      },
    });
  };

  const handleSaveIndustries = async () => {
    if (!strategy) return;
    await onUpdateStrategy(strategy.id, {
      employers: {
        ...strategy.employers,
        blocked_industries: blockedIndustries.split(',').map((i) => i.trim()).filter(Boolean),
      },
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-semibold text-slate-200">Employer Blocklists, Allowlists & Industry Restrictions</h3>
        <p className="text-xs text-slate-400">
          Strictly veto companies you never want AUTONOM to apply to (e.g. current employer, toxic workplaces, spam agencies), manage target employer allowlists, and filter out undesirable industries.
        </p>
      </div>

      {/* Allowlist Mode Selector */}
      <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-3">
        <CardTitle className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">
          Employer Filtering Mode
        </CardTitle>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          {[
            {
              mode: 'no_allowlist' as AllowlistMode,
              title: 'No Allowlist (Open Market)',
              desc: 'Apply to any legitimate company unless explicitly listed on the Blocklist.',
            },
            {
              mode: 'prefer_allowlist' as AllowlistMode,
              title: 'Prefer Allowlist',
              desc: 'Prioritize allowed companies with high score multipliers, but consider other employers.',
            },
            {
              mode: 'strict_allowlist' as AllowlistMode,
              title: 'Strict Allowlist Only',
              desc: 'Veto all companies that are not explicitly approved on your Allowed Employers list.',
            },
          ].map((item) => (
            <button
              key={item.mode}
              type="button"
              onClick={() => handleSaveMode(item.mode)}
              className={`p-3 rounded border text-left transition-all ${
                allowlistMode === item.mode
                  ? 'bg-cyan-950/60 border-cyan-500 text-cyan-200'
                  : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              <span className="font-semibold block text-xs">{item.title}</span>
              <span className="text-[11px] text-slate-400 mt-1 block">{item.desc}</span>
            </button>
          ))}
        </div>
      </Card>

      {/* Add Blocked Employer */}
      <Card className="bg-slate-900/60 border-rose-950/80 p-4 space-y-3">
        <CardTitle className="text-xs font-semibold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
          <ShieldBan className="w-4 h-4" />
          Add Company to Hard Blocklist
        </CardTitle>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div>
            <label className="text-xs text-slate-300 font-medium block mb-1">Company Name</label>
            <Input
              value={newBlockedName}
              onChange={(e) => setNewBlockedName(e.target.value)}
              placeholder="e.g. Current Employer Corp"
              className="bg-slate-950 border-slate-700 text-xs"
            />
          </div>
          <div>
            <label className="text-xs text-slate-300 font-medium block mb-1">Domain (Optional)</label>
            <Input
              value={newBlockedDomain}
              onChange={(e) => setNewBlockedDomain(e.target.value)}
              placeholder="e.g. currentemployer.com"
              className="bg-slate-950 border-slate-700 text-xs"
            />
          </div>
          <div>
            <label className="text-xs text-slate-300 font-medium block mb-1">Reason for Blocking</label>
            <Input
              value={newBlockedReason}
              onChange={(e) => setNewBlockedReason(e.target.value)}
              placeholder="e.g. Current employer privacy / NDA"
              className="bg-slate-950 border-slate-700 text-xs"
            />
          </div>
        </div>

        <div className="flex justify-end">
          <Button
            size="sm"
            className="bg-rose-700 hover:bg-rose-600 text-white text-xs flex items-center gap-1"
            onClick={handleAddBlocked}
            disabled={!newBlockedName.trim()}
          >
            <Plus className="w-3.5 h-3.5" />
            Block Company
          </Button>
        </div>
      </Card>

      {/* Blocked Employers List */}
      <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-3">
        <CardTitle className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
          Blocked Employers ({blockedEmployers.length})
        </CardTitle>

        {blockedEmployers.length === 0 ? (
          <p className="text-xs text-slate-500 py-3 text-center">
            No companies blocked. Enter your current employer or restricted firms above.
          </p>
        ) : (
          <div className="space-y-2 text-xs">
            {blockedEmployers.map((emp, idx) => (
              <div
                key={idx}
                className="p-2.5 rounded bg-slate-950/60 border border-slate-800/80 flex items-center justify-between"
              >
                <div>
                  <span className="font-bold text-rose-300">{emp.name}</span>
                  {emp.domain && <span className="text-slate-500 ml-2 font-mono">({emp.domain})</span>}
                  <p className="text-slate-400 text-[11px] mt-0.5">{emp.reason}</p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 text-xs text-slate-400 hover:text-rose-400 p-1"
                  onClick={() => handleRemoveBlocked(idx)}
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Blocked Industries */}
      <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-3">
        <CardTitle className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
          Blocked Industries
        </CardTitle>
        <div>
          <label className="text-xs text-slate-400 block mb-1">
            Industries to exclude (comma-separated, e.g. gambling, tobacco, defense, crypto)
          </label>
          <Input
            value={blockedIndustries}
            onChange={(e) => setBlockedIndustries(e.target.value)}
            className="bg-slate-950 border-slate-700 text-xs"
          />
        </div>
        <div className="flex justify-end">
          <Button
            size="sm"
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs"
            onClick={handleSaveIndustries}
          >
            Save Industries
          </Button>
        </div>
      </Card>
    </div>
  );
};
