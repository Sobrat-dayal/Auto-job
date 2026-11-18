/**
 * Stage 21: Applicant Projects & Portfolio Tab.
 * Technical repositories, open-source contributions, demos, and project highlights.
 */

import * as React from 'react';
import { FolderGit2, Plus, Trash2, ExternalLink, Github } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import type { ProjectRecord } from '@autonom/shared-types';

interface ApplicantProjectsTabProps {
  projectsList: ProjectRecord[];
  onAdd: (proj: Partial<ProjectRecord>) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  isProcessing: boolean;
}

export const ApplicantProjectsTab: React.FC<ApplicantProjectsTabProps> = ({
  projectsList,
  onAdd,
  onDelete,
  isProcessing,
}) => {
  const [isAdding, setIsAdding] = React.useState(false);
  const [title, setTitle] = React.useState('');
  const [role, setRole] = React.useState('');
  const [summary, setSummary] = React.useState('');
  const [repoUrl, setRepoUrl] = React.useState('');
  const [demoUrl, setDemoUrl] = React.useState('');
  const [technologiesText, setTechnologiesText] = React.useState('');
  const [highlightsText, setHighlightsText] = React.useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    const technologies = technologiesText
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean);

    const highlights = highlightsText
      .split('\n')
      .map((h) => h.trim())
      .filter(Boolean);

    await onAdd({
      title: title.trim(),
      role: role || undefined,
      summary: summary || undefined,
      repository_url: repoUrl || undefined,
      demo_url: demoUrl || undefined,
      technologies,
      highlights,
    });

    setTitle('');
    setRole('');
    setSummary('');
    setRepoUrl('');
    setDemoUrl('');
    setTechnologiesText('');
    setHighlightsText('');
    setIsAdding(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">Technical Projects & Portfolio</h3>
          <p className="text-sm text-muted-foreground">
            Verifiable projects and implementations. Interview preparation and technical matching agents reference these items.
          </p>
        </div>
        {!isAdding && (
          <Button onClick={() => setIsAdding(true)} size="sm">
            <Plus className="mr-2 h-4 w-4" />
            Add Project
          </Button>
        )}
      </div>

      {/* Add Project Form */}
      {isAdding && (
        <Card className="border-primary/50">
          <CardHeader>
            <CardTitle className="text-base font-semibold">Add Portfolio Project</CardTitle>
            <CardDescription>Enter project details, role, repo, and technical stack.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Project Title *
                  </label>
                  <Input
                    required
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="e.g. Distributed Task Orchestrator"
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Role / Capacity
                  </label>
                  <Input
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    placeholder="e.g. Lead Architect, Core Contributor"
                    className="mt-1"
                  />
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Repository URL (GitHub / GitLab)
                  </label>
                  <Input
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    placeholder="https://github.com/janedoe/orchestrator"
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Live Demo / Documentation URL
                  </label>
                  <Input
                    value={demoUrl}
                    onChange={(e) => setDemoUrl(e.target.value)}
                    placeholder="https://orchestrator-demo.dev"
                    className="mt-1"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Project Description / Summary
                </label>
                <textarea
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  placeholder="Architectural overview, problem solved, and system impact..."
                  rows={2}
                  className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                />
              </div>

              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Technologies Used (Comma separated)
                </label>
                <Input
                  value={technologiesText}
                  onChange={(e) => setTechnologiesText(e.target.value)}
                  placeholder="e.g. Rust, Tokio, SQLite, gRPC, React"
                  className="mt-1"
                />
              </div>

              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Key Accomplishments / Features (One per line)
                </label>
                <textarea
                  value={highlightsText}
                  onChange={(e) => setHighlightsText(e.target.value)}
                  placeholder="• Implemented lock-free concurrent ring buffer handling 100k msgs/sec&#10;• Designed automated fault injection test suite with 98% branch coverage"
                  rows={3}
                  className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="ghost" onClick={() => setIsAdding(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isProcessing}>
                  {isProcessing ? 'Saving...' : 'Add Project'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Projects List */}
      {projectsList.length === 0 ? (
        <Card className="flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
          <FolderGit2 className="mb-2 h-10 w-10 text-muted-foreground" />
          <p className="font-medium text-foreground">No Projects Listed</p>
          <p className="text-xs text-muted-foreground mt-1 max-w-sm">
            Showcase key personal or open-source engineering projects with repository and live links.
          </p>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {projectsList.map((proj) => (
            <Card key={proj.id} className="relative overflow-hidden flex flex-col justify-between">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <h4 className="text-base font-semibold">{proj.title}</h4>
                    {proj.role && (
                      <p className="text-xs text-muted-foreground">{proj.role}</p>
                    )}
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete(proj.id)}
                    disabled={isProcessing}
                    className="text-destructive hover:bg-destructive/10 h-8 w-8 p-0"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>

                {proj.summary && (
                  <p className="mt-3 text-sm text-muted-foreground line-clamp-3">
                    {proj.summary}
                  </p>
                )}

                {proj.highlights && proj.highlights.length > 0 && (
                  <ul className="mt-3 list-inside list-disc space-y-1 text-xs text-foreground/90">
                    {proj.highlights.slice(0, 2).map((h, i) => (
                      <li key={i}>{h}</li>
                    ))}
                  </ul>
                )}

                {proj.technologies && proj.technologies.length > 0 && (
                  <div className="mt-4 flex flex-wrap gap-1 pt-3 border-t">
                    {proj.technologies.map((t, i) => (
                      <Badge key={i} variant="neutral" className="text-[10px] font-mono">
                        {t}
                      </Badge>
                    ))}
                  </div>
                )}

                <div className="mt-4 flex items-center gap-3 pt-2 text-xs">
                  {proj.repository_url && (
                    <a
                      href={proj.repository_url}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-1 text-primary hover:underline"
                    >
                      <Github className="h-3.5 w-3.5" /> Code Repo
                    </a>
                  )}
                  {proj.demo_url && (
                    <a
                      href={proj.demo_url}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-1 text-primary hover:underline"
                    >
                      <ExternalLink className="h-3.5 w-3.5" /> Live Demo
                    </a>
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
