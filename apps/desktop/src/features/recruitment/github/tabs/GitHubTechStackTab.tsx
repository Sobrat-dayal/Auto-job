/**
 * GitHub Tech Stack Tab: Consolidated view of all technologies detected across repositories.
 * Grouped into canonical categories: Languages, Frameworks, Databases, Testing, CI/CD, Containerization, and AI/ML.
 */

import * as React from 'react';
import {
  Code2,
  Layers,
  Database,
  ShieldCheck,
  Box,
  Terminal,
  Cpu,
  Workflow,
  Search,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import type {
  TechnologyFinding,
  GitHubTechCategory,
} from '@autonom/shared-types';

interface GitHubTechStackTabProps {
  technologies: TechnologyFinding[];
  onReviewCandidate?: (techName: string) => void;
}

const CATEGORY_LABELS: Record<GitHubTechCategory, { title: string; icon: React.ElementType }> = {
  programming_language: { title: 'Programming Languages', icon: Code2 },
  framework: { title: 'Frameworks & Engines', icon: Layers },
  library: { title: 'Libraries & Utilities', icon: Box },
  database: { title: 'Databases & Storage', icon: Database },
  orm: { title: 'ORMs & Query Builders', icon: Terminal },
  testing: { title: 'Testing & QA Automation', icon: ShieldCheck },
  build_tool: { title: 'Build & Bundling Tools', icon: Cpu },
  package_manager: { title: 'Package Managers', icon: Box },
  ci_cd: { title: 'CI/CD Pipelines', icon: Workflow },
  cloud: { title: 'Cloud Services & Infrastructure', icon: Layers },
  containerization: { title: 'Containerization & Docker', icon: Box },
  ai_ml: { title: 'AI & Machine Learning', icon: Cpu },
  other: { title: 'Other Dependencies', icon: Box },
};

export const GitHubTechStackTab: React.FC<GitHubTechStackTabProps> = ({ technologies }) => {
  const [selectedCategory, setSelectedCategory] = React.useState<string>('all');
  const [searchTerm, setSearchTerm] = React.useState<string>('');

  // Group technologies by name and collect evidence sources
  const groupedTechs = React.useMemo(() => {
    const map = new Map<string, { finding: TechnologyFinding; repos: Set<string>; versions: Set<string> }>();

    for (const tech of technologies) {
      const key = `${tech.name.toLowerCase()}:${tech.category}`;
      if (!map.has(key)) {
        map.set(key, { finding: tech, repos: new Set([tech.repo_id]), versions: new Set() });
      } else {
        const item = map.get(key)!;
        item.repos.add(tech.repo_id);
      }
      if (tech.version) {
        map.get(key)!.versions.add(tech.version);
      }
    }

    return Array.from(map.values());
  }, [technologies]);

  const filteredTechs = React.useMemo(() => {
    return groupedTechs.filter(({ finding }) => {
      if (selectedCategory !== 'all' && finding.category !== selectedCategory) return false;
      if (searchTerm) {
        const query = searchTerm.toLowerCase();
        return finding.name.toLowerCase().includes(query) || finding.category.toLowerCase().includes(query);
      }
      return true;
    });
  }, [groupedTechs, selectedCategory, searchTerm]);

  // Aggregate counts per category
  const categoryCounts = React.useMemo(() => {
    const counts: Record<string, number> = {};
    for (const { finding } of groupedTechs) {
      counts[finding.category] = (counts[finding.category] || 0) + 1;
    }
    return counts;
  }, [groupedTechs]);

  const categories = Object.keys(CATEGORY_LABELS) as GitHubTechCategory[];

  return (
    <div className="space-y-6">
      {/* Top Banner & Search */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="h-4 w-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
          <Input
            placeholder="Search technologies or frameworks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 text-xs"
          />
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>Total Technologies Identified: <strong className="text-foreground">{groupedTechs.length}</strong></span>
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex flex-wrap gap-1.5 pb-2">
        <Button
          variant={selectedCategory === 'all' ? 'primary' : 'outline'}
          size="sm"
          onClick={() => setSelectedCategory('all')}
          className="text-xs h-7 px-2.5"
        >
          All Categories ({groupedTechs.length})
        </Button>
        {categories.map((cat) => {
          const count = categoryCounts[cat] || 0;
          if (count === 0 && selectedCategory !== cat) return null;
          return (
            <Button
              key={cat}
              variant={selectedCategory === cat ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory(cat)}
              className="text-xs h-7 px-2.5 capitalize"
            >
              {CATEGORY_LABELS[cat]?.title || cat} ({count})
            </Button>
          );
        })}
      </div>

      {/* Technology Findings Cards */}
      {filteredTechs.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {filteredTechs.map(({ finding, repos, versions }) => {
            const CatIcon = CATEGORY_LABELS[finding.category]?.icon || Box;
            const versionStr = Array.from(versions).join(', ');

            return (
              <Card key={`${finding.name}-${finding.category}`} className="border-border/70 hover:border-border transition-colors">
                <CardContent className="p-4 space-y-2.5">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <div className="h-8 w-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                        <CatIcon className="h-4 w-4" />
                      </div>
                      <div>
                        <h4 className="font-bold text-sm tracking-tight">{finding.name}</h4>
                        <span className="text-[11px] text-muted-foreground capitalize">
                          {finding.category.replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                    <Badge variant="outline" className="text-[10px] text-status-success border-status-success/30">
                      {finding.confidence}
                    </Badge>
                  </div>

                  <div className="space-y-1 text-xs pt-1 border-t border-border/50">
                    {versionStr && (
                      <div className="flex justify-between text-muted-foreground text-[11px]">
                        <span>Version</span>
                        <span className="font-mono text-foreground font-medium">v{versionStr}</span>
                      </div>
                    )}
                    <div className="flex justify-between text-muted-foreground text-[11px]">
                      <span>Evidence Source</span>
                      <span className="truncate max-w-[150px] font-mono text-[10px]" title={finding.evidence_source}>
                        {finding.evidence_source}
                      </span>
                    </div>
                    <div className="flex justify-between text-muted-foreground text-[11px]">
                      <span>Repositories</span>
                      <span className="font-medium text-foreground">{repos.size} repo(s)</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : (
        <div className="p-12 border border-dashed border-border rounded-xl text-center space-y-2">
          <Layers className="h-8 w-8 text-muted-foreground/40 mx-auto" />
          <p className="text-sm font-medium">No technologies found in this filter.</p>
          <p className="text-xs text-muted-foreground">
            Select repositories and run analysis to populate technology intelligence.
          </p>
        </div>
      )}
    </div>
  );
};
