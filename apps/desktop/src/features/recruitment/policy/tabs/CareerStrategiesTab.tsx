import * as React from 'react';
import {
  Plus,
  Check,
  History,
  Trash2,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import type {
  CareerStrategy,
  PolicyVersionSnapshot,
  CareerStrategyCreateRequest,
} from '@autonom/shared-types';

interface CareerStrategiesTabProps {
  strategies: CareerStrategy[];
  activeStrategy: CareerStrategy | null;
  onActivateStrategy: (id: string) => Promise<void>;
  onCreateStrategy: (req: CareerStrategyCreateRequest) => Promise<void>;
  onDeleteStrategy: (id: string) => Promise<void>;
  onFetchVersions: (id: string) => Promise<PolicyVersionSnapshot[]>;
}

export const CareerStrategiesTab: React.FC<CareerStrategiesTabProps> = ({
  strategies,
  activeStrategy,
  onActivateStrategy,
  onCreateStrategy,
  onDeleteStrategy,
  onFetchVersions,
}) => {
  const [showCreateModal, setShowCreateModal] = React.useState(false);
  const [newTitle, setNewTitle] = React.useState('');
  const [newDescription, setNewDescription] = React.useState('');
  const [selectedVersions, setSelectedVersions] = React.useState<PolicyVersionSnapshot[] | null>(null);
  const [viewingVersionStratId, setViewingVersionStratId] = React.useState<string | null>(null);

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    await onCreateStrategy({
      title: newTitle.trim(),
      description: newDescription.trim(),
      is_active: false,
    });
    setNewTitle('');
    setNewDescription('');
    setShowCreateModal(false);
  };

  const handleViewVersions = async (id: string) => {
    setViewingVersionStratId(id);
    const vers = await onFetchVersions(id);
    setSelectedVersions(vers);
  };

  return (
    <div className="space-y-6">
      {/* Header and Actions */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">Career Strategies Portfolio</h3>
          <p className="text-xs text-slate-400">
            Define independent targeted strategies (e.g. Backend Focus vs. AI/ML vs. Full-Stack). Exactly one strategy is active at any time.
          </p>
        </div>
        <Button
          size="sm"
          className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs flex items-center gap-1.5"
          onClick={() => setShowCreateModal(true)}
        >
          <Plus className="w-3.5 h-3.5" />
          Create New Strategy
        </Button>
      </div>

      {/* Create Strategy Modal/Drawer */}
      {showCreateModal && (
        <Card className="bg-slate-900 border-cyan-800/80 p-4 space-y-4">
          <CardTitle className="text-sm text-cyan-300 font-semibold">New Career Strategy</CardTitle>
          <div className="space-y-3">
            <div>
              <label className="text-xs text-slate-300 font-medium block mb-1">Strategy Title</label>
              <Input
                placeholder="e.g. Distributed Systems & Infrastructure"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                className="bg-slate-950 border-slate-700 text-xs"
              />
            </div>
            <div>
              <label className="text-xs text-slate-300 font-medium block mb-1">Description / Focus</label>
              <Textarea
                placeholder="Targeting mid-to-senior backend roles in distributed systems, high throughput APIs, or cloud platforms..."
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                className="bg-slate-950 border-slate-700 text-xs"
                rows={2}
              />
            </div>
            <div className="flex items-center justify-end gap-2 pt-2">
              <Button
                variant="ghost"
                size="sm"
                className="text-xs text-slate-400"
                onClick={() => setShowCreateModal(false)}
              >
                Cancel
              </Button>
              <Button
                size="sm"
                className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs"
                onClick={handleCreate}
                disabled={!newTitle.trim()}
              >
                Save Strategy
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Strategies Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {strategies.map((strat) => {
          const isActive = strat.is_active || strat.id === activeStrategy?.id;
          return (
            <Card
              key={strat.id}
              className={`border transition-all ${
                isActive
                  ? 'bg-slate-900/90 border-cyan-500/80 shadow-lg shadow-cyan-950/20'
                  : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
              }`}
            >
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <CardTitle className="text-sm font-bold text-slate-100">{strat.title}</CardTitle>
                      {isActive && (
                        <Badge variant="neutral" className="bg-cyan-950/80 text-cyan-400 border-cyan-700 text-[10px]">
                          ACTIVE
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 mt-1">{strat.description || 'No description provided'}</p>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500">v{strat.version}</span>
                </div>
              </CardHeader>

              <CardContent className="space-y-3 pt-1 text-xs">
                {/* Summary Metadata */}
                <div className="grid grid-cols-2 gap-2 p-2.5 rounded bg-slate-950/40 border border-slate-800/60 text-slate-300">
                  <div>
                    <span className="text-slate-500 block text-[11px]">Roles</span>
                    <span className="font-semibold">{strat.target_roles.length} roles defined</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[11px]">Floor Salary</span>
                    <span className="font-mono text-emerald-400 font-semibold">
                      {strat.compensation.hard_floor_amount
                        ? `$${strat.compensation.hard_floor_amount.toLocaleString()}`
                        : 'None'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[11px]">Work Mode</span>
                    <span className="capitalize">{strat.work_arrangement.allowed_arrangements.join(', ')}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[11px]">Autonomy</span>
                    <span className="text-amber-400 capitalize">
                      {strat.autonomy_mode.replace('mode_', '').replace(/_/g, ' ')}
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between pt-2 border-t border-slate-800/80">
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 text-xs text-slate-400 hover:text-slate-200 p-1 flex items-center gap-1"
                      onClick={() => handleViewVersions(strat.id)}
                    >
                      <History className="w-3.5 h-3.5" />
                      Versions
                    </Button>
                    {!isActive && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs text-rose-400 hover:text-rose-300 p-1 flex items-center gap-1"
                        onClick={() => onDeleteStrategy(strat.id)}
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                        Delete
                      </Button>
                    )}
                  </div>

                  {!isActive ? (
                    <Button
                      size="sm"
                      className="h-7 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 flex items-center gap-1"
                      onClick={() => onActivateStrategy(strat.id)}
                    >
                      <Check className="w-3.5 h-3.5" />
                      Activate
                    </Button>
                  ) : (
                    <span className="text-xs text-cyan-400 font-semibold flex items-center gap-1">
                      <Check className="w-3.5 h-3.5" />
                      Currently Active
                    </span>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Version History Drawer / Section */}
      {selectedVersions && (
        <Card className="bg-slate-900/90 border-slate-800 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-xs font-semibold text-slate-300 flex items-center gap-2">
              <History className="w-4 h-4 text-cyan-400" />
              Policy Version History for Strategy {viewingVersionStratId}
            </CardTitle>
            <Button
              variant="ghost"
              size="sm"
              className="text-xs text-slate-400 h-6 p-0"
              onClick={() => setSelectedVersions(null)}
            >
              Close
            </Button>
          </div>
          <div className="space-y-2">
            {selectedVersions.length === 0 ? (
              <p className="text-xs text-slate-500">No previous version snapshots available.</p>
            ) : (
              selectedVersions.map((v) => (
                <div
                  key={v.version}
                  className="p-2.5 rounded bg-slate-950/50 border border-slate-800 flex items-center justify-between text-xs"
                >
                  <div>
                    <span className="font-bold text-slate-200">Version {v.version}</span>
                    <p className="text-slate-400 text-[11px] mt-0.5">{v.change_summary}</p>
                    <span className="text-[10px] font-mono text-slate-500">SHA-256: {v.snapshot_hash.slice(0, 16)}...</span>
                  </div>
                  <span className="text-[10px] text-slate-500">{new Date(v.created_at).toLocaleString()}</span>
                </div>
              ))
            )}
          </div>
        </Card>
      )}
    </div>
  );
};
