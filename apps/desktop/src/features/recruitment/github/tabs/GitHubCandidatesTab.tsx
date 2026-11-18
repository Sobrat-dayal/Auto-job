/**
 * GitHub Candidates Tab: Explicit Human Review Queue for extracted skills and projects.
 * Guarantees zero silent mutation of the applicant profile.
 */

import * as React from 'react';
import {
  CheckCircle2,
  FolderGit2,
  Cpu,
  Sparkles,
  Check,
  X,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type {
  CandidateSkill,
  CandidateProject,
  ConfirmCandidateRequest,
} from '@autonom/shared-types';

interface GitHubCandidatesTabProps {
  skillCandidates: CandidateSkill[];
  projectCandidates: CandidateProject[];
  onConfirmSkill: (candidateId: string, payload?: ConfirmCandidateRequest) => Promise<void>;
  onConfirmProject: (candidateId: string, payload?: ConfirmCandidateRequest) => Promise<void>;
  onRejectCandidate: (candidateId: string) => Promise<void>;
  isLoading: boolean;
}

export const GitHubCandidatesTab: React.FC<GitHubCandidatesTabProps> = ({
  skillCandidates,
  projectCandidates,
  onConfirmSkill,
  onConfirmProject,
  onRejectCandidate,
}) => {
  const [activeSubTab, setActiveSubTab] = React.useState<'skills' | 'projects' | 'history'>('skills');
  const [processingId, setProcessingId] = React.useState<string | null>(null);

  const pendingSkills = skillCandidates.filter((s) => s.status === 'awaiting_review');
  const pendingProjects = projectCandidates.filter((p) => p.status === 'awaiting_review');
  const confirmedSkills = skillCandidates.filter((s) => s.status === 'confirmed');
  const confirmedProjects = projectCandidates.filter((p) => p.status === 'confirmed');

  const handleConfirmSkill = async (candidateId: string) => {
    try {
      setProcessingId(candidateId);
      await onConfirmSkill(candidateId, { profile_id: 'prof_primary_applicant' });
    } finally {
      setProcessingId(null);
    }
  };

  const handleConfirmProject = async (candidateId: string) => {
    try {
      setProcessingId(candidateId);
      await onConfirmProject(candidateId, { profile_id: 'prof_primary_applicant' });
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (candidateId: string) => {
    try {
      setProcessingId(candidateId);
      await onRejectCandidate(candidateId);
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Banner / Explainer */}
      <div className="p-4 rounded-xl border border-primary/20 bg-primary/5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <h4 className="font-semibold text-sm">Human-in-the-Loop Review Queue</h4>
            <p className="text-xs text-muted-foreground">
              Candidate skills and projects extracted from repository manifests remain in this review queue until you confirm them. Only confirmed candidates are promoted into your authoritative Stage 21 profile.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <Badge variant="outline" className="text-xs bg-background">
            {pendingSkills.length} Pending Skills
          </Badge>
          <Badge variant="outline" className="text-xs bg-background">
            {pendingProjects.length} Pending Projects
          </Badge>
        </div>
      </div>

      {/* Sub-tab Switcher */}
      <div className="flex items-center gap-2 border-b border-border pb-2">
        <Button
          variant={activeSubTab === 'skills' ? 'primary' : 'ghost'}
          size="sm"
          onClick={() => setActiveSubTab('skills')}
          className="text-xs h-8 gap-1.5"
        >
          <Cpu className="h-3.5 w-3.5" />
          Skill Candidates ({pendingSkills.length})
        </Button>
        <Button
          variant={activeSubTab === 'projects' ? 'primary' : 'ghost'}
          size="sm"
          onClick={() => setActiveSubTab('projects')}
          className="text-xs h-8 gap-1.5"
        >
          <FolderGit2 className="h-3.5 w-3.5" />
          Project Candidates ({pendingProjects.length})
        </Button>
        <Button
          variant={activeSubTab === 'history' ? 'primary' : 'ghost'}
          size="sm"
          onClick={() => setActiveSubTab('history')}
          className="text-xs h-8 gap-1.5"
        >
          <CheckCircle2 className="h-3.5 w-3.5" />
          Promoted to Profile ({confirmedSkills.length + confirmedProjects.length})
        </Button>
      </div>

      {/* View 1: Skill Candidates */}
      {activeSubTab === 'skills' && (
        <div className="space-y-3">
          {pendingSkills.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {pendingSkills.map((skill) => {
                const isProcessing = processingId === skill.id;

                return (
                  <Card key={skill.id} className="border-border/70 hover:border-border transition-colors">
                    <CardHeader className="pb-2">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <CardTitle className="text-sm font-bold flex items-center gap-1.5">
                            {skill.name}
                            {skill.version && (
                              <span className="font-mono text-xs text-muted-foreground font-normal">
                                v{skill.version}
                              </span>
                            )}
                          </CardTitle>
                          <CardDescription className="text-xs capitalize">
                            {skill.category.replace('_', ' ')}
                          </CardDescription>
                        </div>
                        <Badge variant="outline" className="text-[10px] text-primary border-primary/30">
                          {skill.confidence}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-1.5 text-xs">
                      <div className="p-2 rounded bg-secondary/30 text-[11px] space-y-0.5">
                        <span className="text-muted-foreground block">Evidence Source:</span>
                        <span className="font-mono font-medium block truncate">
                          {skill.evidence_repo_name}
                          {skill.evidence_file_path && ` / ${skill.evidence_file_path}`}
                        </span>
                      </div>
                      <div className="flex justify-between text-muted-foreground text-[11px] pt-1">
                        <span>Suggested Proficiency</span>
                        <span className="font-semibold text-foreground capitalize">
                          {skill.proficiency_hint}
                        </span>
                      </div>
                    </CardContent>
                    <CardFooter className="pt-2 flex justify-end gap-2 border-t border-border/50">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleReject(skill.id)}
                        disabled={isProcessing}
                        className="text-xs h-7 text-muted-foreground hover:text-status-error gap-1"
                      >
                        <X className="h-3 w-3" /> Reject
                      </Button>
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleConfirmSkill(skill.id)}
                        disabled={isProcessing}
                        className="text-xs h-7 gap-1"
                      >
                        <Check className="h-3 w-3" />
                        {isProcessing ? 'Promoting...' : 'Confirm & Add to Profile'}
                      </Button>
                    </CardFooter>
                  </Card>
                );
              })}
            </div>
          ) : (
            <div className="p-8 border border-dashed border-border rounded-xl text-center space-y-2">
              <CheckCircle2 className="h-8 w-8 text-status-success/50 mx-auto" />
              <p className="text-sm font-medium">All skill candidates reviewed!</p>
              <p className="text-xs text-muted-foreground">
                Run analysis on new repositories to extract additional candidate skills.
              </p>
            </div>
          )}
        </div>
      )}

      {/* View 2: Project Candidates */}
      {activeSubTab === 'projects' && (
        <div className="space-y-3">
          {pendingProjects.length > 0 ? (
            <div className="grid grid-cols-1 gap-3.5">
              {pendingProjects.map((project) => {
                const isProcessing = processingId === project.id;

                return (
                  <Card key={project.id} className="border-border/70 hover:border-border transition-colors">
                    <CardHeader className="pb-2">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <CardTitle className="text-base font-bold">{project.title}</CardTitle>
                          <CardDescription className="text-xs">{project.repo_url}</CardDescription>
                        </div>
                        <Badge variant="outline" className="text-xs capitalize">
                          {project.architecture_type.replace('_', ' ')}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3 text-xs">
                      <p className="text-muted-foreground">{project.description}</p>
                      {project.technologies.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {project.technologies.map((t) => (
                            <Badge key={t} variant="neutral" className="text-[10px] py-0">
                              {t}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </CardContent>
                    <CardFooter className="pt-2 flex justify-end gap-2 border-t border-border/50">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleReject(project.id)}
                        disabled={isProcessing}
                        className="text-xs h-7 text-muted-foreground hover:text-status-error gap-1"
                      >
                        <X className="h-3 w-3" /> Reject
                      </Button>
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleConfirmProject(project.id)}
                        disabled={isProcessing}
                        className="text-xs h-7 gap-1"
                      >
                        <Check className="h-3 w-3" />
                        {isProcessing ? 'Promoting...' : 'Confirm & Add to Profile'}
                      </Button>
                    </CardFooter>
                  </Card>
                );
              })}
            </div>
          ) : (
            <div className="p-8 border border-dashed border-border rounded-xl text-center space-y-2">
              <CheckCircle2 className="h-8 w-8 text-status-success/50 mx-auto" />
              <p className="text-sm font-medium">All project candidates reviewed!</p>
            </div>
          )}
        </div>
      )}

      {/* View 3: Promoted History */}
      {activeSubTab === 'history' && (
        <div className="space-y-4">
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Confirmed Skills ({confirmedSkills.length})
            </h4>
            {confirmedSkills.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                {confirmedSkills.map((s) => (
                  <div
                    key={s.id}
                    className="p-2.5 rounded-lg border border-status-success/30 bg-status-success/5 flex items-center justify-between text-xs"
                  >
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-status-success shrink-0" />
                      <span className="font-semibold">{s.name}</span>
                    </div>
                    <Badge variant="outline" className="text-[10px] text-status-success">
                      Verified
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">No skills promoted yet.</p>
            )}
          </div>

          <div className="space-y-2 pt-3 border-t border-border/60">
            <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Confirmed Projects ({confirmedProjects.length})
            </h4>
            {confirmedProjects.length > 0 ? (
              <div className="space-y-2">
                {confirmedProjects.map((p) => (
                  <div
                    key={p.id}
                    className="p-3 rounded-lg border border-status-success/30 bg-status-success/5 flex items-center justify-between text-xs"
                  >
                    <div className="space-y-1">
                      <span className="font-semibold">{p.title}</span>
                      <p className="text-muted-foreground line-clamp-1">{p.description}</p>
                    </div>
                    <Badge variant="outline" className="text-[10px] text-status-success shrink-0">
                      Profile Active
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">No projects promoted yet.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
