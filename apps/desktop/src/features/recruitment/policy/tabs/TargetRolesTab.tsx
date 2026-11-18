import * as React from 'react';
import {
  Plus,
  Trash2,
  Star,
} from 'lucide-react';
import { Card, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type {
  CareerStrategy,
  TargetRoleItem,
  RoleFamily,
  SeniorityLevel,
  CareerStrategyUpdateRequest,
} from '@autonom/shared-types';

interface TargetRolesTabProps {
  strategy: CareerStrategy | null;
  onUpdateStrategy: (id: string, req: CareerStrategyUpdateRequest) => Promise<void>;
}

const ROLE_FAMILIES: { value: RoleFamily; label: string }[] = [
  { value: 'backend', label: 'Backend Engineering' },
  { value: 'software_engineering', label: 'General Software Engineering' },
  { value: 'frontend', label: 'Frontend Engineering' },
  { value: 'fullstack', label: 'Full-Stack Engineering' },
  { value: 'cloud_devops', label: 'Cloud & DevOps / SRE' },
  { value: 'ai_ml_engineering', label: 'AI / ML Engineering' },
  { value: 'ai_research', label: 'AI / ML Research' },
  { value: 'data_engineering', label: 'Data Engineering' },
  { value: 'data_science', label: 'Data Science & Analytics' },
  { value: 'systems_embedded', label: 'Systems & Embedded' },
  { value: 'cybersecurity', label: 'Cybersecurity & InfoSec' },
  { value: 'product_management', label: 'Product Management' },
  { value: 'engineering_management', label: 'Engineering Management' },
  { value: 'mobile', label: 'Mobile Engineering' },
  { value: 'other', label: 'Other' },
];

const SENIORITY_LEVELS: { value: SeniorityLevel; label: string }[] = [
  { value: 'internship', label: 'Internship' },
  { value: 'entry_level', label: 'Entry Level / Associate' },
  { value: 'junior', label: 'Junior (1-2 yrs)' },
  { value: 'mid_level', label: 'Mid-Level (3-5 yrs)' },
  { value: 'senior', label: 'Senior (5-8 yrs)' },
  { value: 'staff', label: 'Staff' },
  { value: 'principal', label: 'Principal' },
  { value: 'lead', label: 'Tech Lead' },
  { value: 'manager', label: 'Manager' },
  { value: 'director', label: 'Director' },
];

export const TargetRolesTab: React.FC<TargetRolesTabProps> = ({
  strategy,
  onUpdateStrategy,
}) => {
  const [roles, setRoles] = React.useState<TargetRoleItem[]>(strategy?.target_roles || []);
  const [newTitle, setNewTitle] = React.useState('');
  const [newFamily, setNewFamily] = React.useState<RoleFamily>('backend');
  const [newSeniority, setNewSeniority] = React.useState<SeniorityLevel>('mid_level');
  const [newKeywords, setNewKeywords] = React.useState('');
  const [newExclusions, setNewExclusions] = React.useState('');

  React.useEffect(() => {
    if (strategy) {
      setRoles(strategy.target_roles);
    }
  }, [strategy]);

  const handleAddRole = async () => {
    if (!newTitle.trim() || !strategy) return;

    const roleItem: TargetRoleItem = {
      title: newTitle.trim(),
      role_family: newFamily,
      seniority: newSeniority,
      keywords: newKeywords.split(',').map((k) => k.trim()).filter(Boolean),
      excluded_keywords: newExclusions.split(',').map((k) => k.trim()).filter(Boolean),
      is_primary: roles.length === 0,
      priority_weight: 1.0,
    };

    const updated = [...roles, roleItem];
    setRoles(updated);
    await onUpdateStrategy(strategy.id, { target_roles: updated });

    setNewTitle('');
    setNewKeywords('');
    setNewExclusions('');
  };

  const handleRemoveRole = async (index: number) => {
    if (!strategy) return;
    const updated = roles.filter((_, idx) => idx !== index);
    setRoles(updated);
    await onUpdateStrategy(strategy.id, { target_roles: updated });
  };

  const handleTogglePrimary = async (index: number) => {
    if (!strategy) return;
    const updated = roles.map((r, idx) => ({
      ...r,
      is_primary: idx === index,
    }));
    setRoles(updated);
    await onUpdateStrategy(strategy.id, { target_roles: updated });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">Target Roles & Specialization Taxonomy</h3>
          <p className="text-xs text-slate-400">
            Define target job titles, maps to the 11 role families, allowed seniority levels, and title keyword triggers/exclusions.
          </p>
        </div>
      </div>

      {/* Add New Role Form */}
      <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-4">
        <CardTitle className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">
          Add Target Role
        </CardTitle>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <label className="text-xs text-slate-300 font-medium block mb-1">Target Title</label>
            <Input
              placeholder="e.g. Distributed Systems Engineer"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              className="bg-slate-950 border-slate-700 text-xs"
            />
          </div>

          <div>
            <label className="text-xs text-slate-300 font-medium block mb-1">Role Family</label>
            <select
              value={newFamily}
              onChange={(e) => setNewFamily(e.target.value as RoleFamily)}
              className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              {ROLE_FAMILIES.map((rf) => (
                <option key={rf.value} value={rf.value}>
                  {rf.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs text-slate-300 font-medium block mb-1">Target Seniority</label>
            <select
              value={newSeniority}
              onChange={(e) => setNewSeniority(e.target.value as SeniorityLevel)}
              className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              {SENIORITY_LEVELS.map((sl) => (
                <option key={sl.value} value={sl.value}>
                  {sl.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-slate-300 font-medium block mb-1">
              Required Title Keywords (comma-separated)
            </label>
            <Input
              placeholder="e.g. backend, distributed, systems, golang"
              value={newKeywords}
              onChange={(e) => setNewKeywords(e.target.value)}
              className="bg-slate-950 border-slate-700 text-xs"
            />
          </div>

          <div>
            <label className="text-xs text-slate-300 font-medium block mb-1">
              Excluded Title Keywords (immediate rejection)
            </label>
            <Input
              placeholder="e.g. lead, manager, frontend, sales"
              value={newExclusions}
              onChange={(e) => setNewExclusions(e.target.value)}
              className="bg-slate-950 border-slate-700 text-xs"
            />
          </div>
        </div>

        <div className="flex justify-end">
          <Button
            size="sm"
            className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs flex items-center gap-1.5"
            onClick={handleAddRole}
            disabled={!newTitle.trim()}
          >
            <Plus className="w-3.5 h-3.5" />
            Add Role to Strategy
          </Button>
        </div>
      </Card>

      {/* Target Roles List */}
      <div className="space-y-3">
        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
          Configured Roles ({roles.length})
        </h4>

        {roles.length === 0 ? (
          <div className="text-center py-6 text-slate-500 text-xs bg-slate-950/40 border border-slate-800 rounded">
            No target roles defined for this strategy. Add at least one target role above.
          </div>
        ) : (
          roles.map((r, idx) => (
            <Card key={idx} className="bg-slate-900/50 border-slate-800">
              <CardContent className="p-3.5 flex items-center justify-between text-xs">
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-200 text-sm">{r.title}</span>
                    <Badge variant="neutral" className="bg-blue-950/60 text-blue-400 border-blue-800 text-[10px]">
                      {r.role_family.replace(/_/g, ' ')}
                    </Badge>
                    <Badge variant="neutral" className="bg-purple-950/60 text-purple-400 border-purple-800 text-[10px]">
                      {r.seniority.replace(/_/g, ' ')}
                    </Badge>
                    {r.is_primary && (
                      <Badge variant="neutral" className="bg-amber-950/60 text-amber-400 border-amber-800 text-[10px] flex items-center gap-1">
                        <Star className="w-2.5 h-2.5 fill-current" />
                        PRIMARY
                      </Badge>
                    )}
                  </div>

                  <div className="flex items-center gap-4 text-slate-400 text-[11px]">
                    {r.keywords.length > 0 && (
                      <div>
                        <span className="text-slate-500">Keywords: </span>
                        <span className="text-slate-300 font-mono">{r.keywords.join(', ')}</span>
                      </div>
                    )}
                    {r.excluded_keywords.length > 0 && (
                      <div>
                        <span className="text-rose-500">Excluded: </span>
                        <span className="text-rose-400 font-mono">{r.excluded_keywords.join(', ')}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {!r.is_primary && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-xs text-slate-400 hover:text-amber-400 h-7"
                      onClick={() => handleTogglePrimary(idx)}
                    >
                      Make Primary
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-xs text-rose-400 hover:text-rose-300 h-7 p-1"
                    onClick={() => handleRemoveRole(idx)}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};
