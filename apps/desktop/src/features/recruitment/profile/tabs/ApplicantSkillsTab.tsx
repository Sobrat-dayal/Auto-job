/**
 * Stage 21: Applicant Skills Inventory Tab.
 * Categorized technical, domain, and soft skills with verified proficiency and evidence badges.
 */

import * as React from 'react';
import { Code2, Plus, Trash2, ShieldCheck, Star } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import type { SkillItem, SkillProficiency } from '@autonom/shared-types';

interface ApplicantSkillsTabProps {
  skillsList: SkillItem[];
  onUpsert: (skill: Partial<SkillItem>) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  isProcessing: boolean;
}

export const ApplicantSkillsTab: React.FC<ApplicantSkillsTabProps> = ({
  skillsList,
  onUpsert,
  onDelete,
  isProcessing,
}) => {
  const [selectedCategory, setSelectedCategory] = React.useState<string>('all');
  const [isAdding, setIsAdding] = React.useState(false);
  const [name, setName] = React.useState('');
  const [category, setCategory] = React.useState<SkillItem['category']>('technical');
  const [proficiency, setProficiency] = React.useState<SkillProficiency>('advanced');
  const [yearsExperience, setYearsExperience] = React.useState<number | ''>(3);
  const [lastUsedYear, setLastUsedYear] = React.useState<number | ''>(new Date().getFullYear());
  const [isPrimary, setIsPrimary] = React.useState(false);

  const categories = ['all', 'technical', 'framework', 'tool', 'domain', 'language', 'soft'];

  const filteredSkills = skillsList.filter((s) => {
    if (selectedCategory === 'all') return true;
    return s.category.toLowerCase() === selectedCategory.toLowerCase();
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    await onUpsert({
      name: name.trim(),
      category,
      proficiency,
      years_experience: yearsExperience === '' ? undefined : Number(yearsExperience),
      last_used_year: lastUsedYear === '' ? undefined : Number(lastUsedYear),
      is_primary: isPrimary,
    });

    setName('');
    setIsPrimary(false);
    setIsAdding(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-lg font-medium">Skills Inventory & Capabilities</h3>
          <p className="text-sm text-muted-foreground">
            Authoritative competency taxonomy. Automatically referenced during job requirement matching and keyword extraction.
          </p>
        </div>
        {!isAdding && (
          <Button onClick={() => setIsAdding(true)} size="sm">
            <Plus className="mr-2 h-4 w-4" />
            Add Skill
          </Button>
        )}
      </div>

      {/* Add / Upsert Skill Form */}
      {isAdding && (
        <Card className="border-primary/50">
          <CardHeader>
            <CardTitle className="text-base font-semibold">Add or Upsert Skill</CardTitle>
            <CardDescription>Enter skill name, domain category, and verified proficiency.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Skill Name *
                  </label>
                  <Input
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Python, React, PostgreSQL"
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Category
                  </label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value as any)}
                    className="mt-1 flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  >
                    <option value="technical">Technical</option>
                    <option value="framework">Framework</option>
                    <option value="tool">Tool / DevOps</option>
                    <option value="domain">Domain / Specialization</option>
                    <option value="language">Language</option>
                    <option value="soft">Soft / Leadership</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Proficiency
                  </label>
                  <select
                    value={proficiency}
                    onChange={(e) => setProficiency(e.target.value as any)}
                    className="mt-1 flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  >
                    <option value="expert">Expert</option>
                    <option value="advanced">Advanced</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="beginner">Beginner</option>
                  </select>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Years of Experience
                  </label>
                  <Input
                    type="number"
                    min="0"
                    step="0.5"
                    value={yearsExperience}
                    onChange={(e) => setYearsExperience(e.target.value === '' ? '' : parseFloat(e.target.value))}
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Last Used Year
                  </label>
                  <Input
                    type="number"
                    min="2000"
                    max={new Date().getFullYear()}
                    value={lastUsedYear}
                    onChange={(e) => setLastUsedYear(e.target.value === '' ? '' : parseInt(e.target.value, 10))}
                    className="mt-1"
                  />
                </div>
                <div className="flex items-center pt-6">
                  <label className="flex items-center gap-2 text-sm font-medium cursor-pointer">
                    <input
                      type="checkbox"
                      checked={isPrimary}
                      onChange={(e) => setIsPrimary(e.target.checked)}
                      className="rounded border-gray-300"
                    />
                    Mark as Core Primary Skill
                  </label>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="ghost" onClick={() => setIsAdding(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isProcessing}>
                  {isProcessing ? 'Saving...' : 'Save Skill'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Category Filter Pills */}
      <div className="flex flex-wrap gap-2">
        {categories.map((cat) => (
          <Button
            key={cat}
            variant={selectedCategory === cat ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setSelectedCategory(cat)}
            className="capitalize text-xs"
          >
            {cat} {cat === 'all' ? `(${skillsList.length})` : ''}
          </Button>
        ))}
      </div>

      {/* Skills Grid */}
      {filteredSkills.length === 0 ? (
        <Card className="flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
          <Code2 className="mb-2 h-10 w-10 text-muted-foreground" />
          <p className="font-medium text-foreground">No Skills Found in Category</p>
          <p className="text-xs text-muted-foreground mt-1 max-w-sm">
            Add core skills or import a resume to automatically extract technical competencies.
          </p>
        </Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {filteredSkills.map((skill) => (
            <Card key={skill.id} className="relative group overflow-hidden hover:border-primary/50 transition-colors">
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-1.5">
                      <span className="font-semibold text-sm">{skill.name}</span>
                      {skill.is_primary && (
                        <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-500" />
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Badge variant="neutral" className="capitalize text-[10px] px-1.5 py-0">
                        {skill.category}
                      </Badge>
                      {skill.proficiency && (
                        <span className="capitalize">{skill.proficiency}</span>
                      )}
                    </div>
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete(skill.id)}
                    disabled={isProcessing}
                    className="opacity-0 group-hover:opacity-100 transition-opacity h-7 w-7 p-0 text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>

                <div className="mt-3 flex items-center justify-between text-[11px] text-muted-foreground pt-2 border-t">
                  <span>{skill.years_experience ? `${skill.years_experience} yrs` : 'Proficient'}</span>
                  {skill.claim_id ? (
                    <span className="flex items-center gap-1 text-emerald-600 font-medium">
                      <ShieldCheck className="h-3 w-3" /> Provenance
                    </span>
                  ) : (
                    <span>Self-attested</span>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
