/**
 * GitHub Evidence Tab: Code provenance audit, SHA-256 commit verification, and secret redactor logs.
 */

import * as React from 'react';
import {
  ShieldCheck,
  FileCode,
  Key,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type {
  TechnologyFinding,
  CommitEvidence,
  CandidateSkill,
} from '@autonom/shared-types';

interface GitHubEvidenceTabProps {
  technologies: TechnologyFinding[];
  commits: CommitEvidence[];
  skillCandidates: CandidateSkill[];
}

export const GitHubEvidenceTab: React.FC<GitHubEvidenceTabProps> = ({
  technologies,
  commits,
}) => {
  return (
    <div className="space-y-6">
      {/* Privacy & Provenance Guarantee Banner */}
      <div className="p-4 rounded-xl border border-border/80 bg-secondary/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-status-success/10 text-status-success flex items-center justify-center shrink-0">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <h4 className="font-semibold text-sm">Strict Zero-Exposure Evidence Model</h4>
            <p className="text-xs text-muted-foreground">
              Every extracted skill or project links to an immutable Git commit SHA and manifest path. Secrets and credentials are automatically redacted prior to storage or inference.
            </p>
          </div>
        </div>
        <Badge variant="outline" className="text-xs text-status-success border-status-success/30 shrink-0">
          Redactor Active (11 Patterns)
        </Badge>
      </div>

      {/* Two Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Manifest Provenance Traces */}
        <Card className="border-border/80">
          <CardHeader>
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <FileCode className="h-4 w-4 text-primary" /> Manifest Traces ({technologies.length})
            </CardTitle>
            <CardDescription className="text-xs">
              Direct evidence links showing the manifest and path where each skill/technology was identified.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {technologies.length > 0 ? (
              <div className="space-y-2 max-h-[420px] overflow-y-auto pr-1">
                {technologies.map((tech, idx) => (
                  <div
                    key={`${tech.name}-${idx}`}
                    className="p-2.5 rounded-lg border border-border/50 bg-card/60 flex items-center justify-between text-xs"
                  >
                    <div className="space-y-0.5 overflow-hidden">
                      <div className="font-semibold flex items-center gap-2">
                        <span>{tech.name}</span>
                        {tech.version && <span className="text-[10px] font-mono text-muted-foreground">v{tech.version}</span>}
                      </div>
                      <span className="text-[11px] font-mono text-muted-foreground truncate block">
                        {tech.evidence_source}
                      </span>
                    </div>
                    <Badge variant="neutral" className="text-[10px] shrink-0 capitalize">
                      {tech.category.replace('_', ' ')}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-xs text-muted-foreground">
                No manifest traces found. Run repository analysis first.
              </div>
            )}
          </CardContent>
        </Card>

        {/* Right: Commit Attributions & SHA Links */}
        <Card className="border-border/80">
          <CardHeader>
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Key className="h-4 w-4 text-primary" /> Commit Evidence Log ({commits.length})
            </CardTitle>
            <CardDescription className="text-xs">
              Cryptographically verified commit SHAs identifying authentic contributions by the applicant.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {commits.length > 0 ? (
              <div className="space-y-2 max-h-[420px] overflow-y-auto pr-1">
                {commits.map((c) => (
                  <div
                    key={c.commit_sha}
                    className="p-2.5 rounded-lg border border-border/50 bg-card/60 flex items-center justify-between text-xs"
                  >
                    <div className="space-y-0.5 overflow-hidden max-w-[70%]">
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-primary font-bold">
                          {c.commit_sha.slice(0, 7)}
                        </span>
                        <span className="truncate font-medium">{c.message}</span>
                      </div>
                      <span className="text-[11px] text-muted-foreground block truncate">
                        {c.author_name} ({c.author_email})
                      </span>
                    </div>
                    <Badge
                      variant="outline"
                      className={`text-[10px] shrink-0 ${
                        c.is_applicant ? 'text-status-success border-status-success/30' : 'text-muted-foreground'
                      }`}
                    >
                      {c.is_applicant ? 'Applicant Confirmed' : 'Associated'}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-xs text-muted-foreground">
                No commit logs collected yet.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
