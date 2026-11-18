/**
 * Stage 21: Applicant History, Versions & Agent Scoped Snapshot Tab.
 * Immutable audit logs and privacy-preserving downstream agent snapshot generator.
 */

import * as React from 'react';
import { History, Eye, Sparkles, Clock, Copy, Check } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { ProfileVersionRecord, ProfileSnapshot } from '@autonom/shared-types';

interface ApplicantHistoryTabProps {
  versionHistory: ProfileVersionRecord[];
  onGenerateSnapshot: (targetAgent: string) => Promise<ProfileSnapshot | null>;
  isProcessing: boolean;
}

export const ApplicantHistoryTab: React.FC<ApplicantHistoryTabProps> = ({
  versionHistory,
  onGenerateSnapshot,
  isProcessing,
}) => {
  const [selectedAgent, setSelectedAgent] = React.useState<string>('JobMatchingAgent');
  const [snapshot, setSnapshot] = React.useState<ProfileSnapshot | null>(null);
  const [copied, setCopied] = React.useState<boolean>(false);

  const agents = [
    {
      id: 'JobMatchingAgent',
      name: 'Job Matching Agent',
      desc: 'Scoped to skills, location, eligibility, and education. Contact info strictly redacted.',
    },
    {
      id: 'ResumeAgent',
      name: 'Resume Tailoring Agent',
      desc: 'Scoped to verified employment achievements, metrics, and technology stacks.',
    },
    {
      id: 'ApplicationAgent',
      name: 'Application Form Agent',
      desc: 'Scoped to authorized contact points and legal work eligibility for portal autofill.',
    },
    {
      id: 'InterviewPrepAgent',
      name: 'Interview Prep Agent',
      desc: 'Scoped to technical project architectures, code repositories, and career highlights.',
    },
  ];

  const handleGenerate = async () => {
    const res = await onGenerateSnapshot(selectedAgent);
    if (res) {
      setSnapshot(res);
    }
  };

  const handleCopy = () => {
    if (!snapshot) return;
    navigator.clipboard.writeText(JSON.stringify(snapshot.filtered_data, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Audit History & Agent Snapshot Generator</h3>
        <p className="text-sm text-muted-foreground">
          Audit trail of immutable profile revisions and live simulation of scoped data delivery to specialist agents.
        </p>
      </div>

      {/* Downstream Agent Scoped Snapshot Simulator */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <Eye className="h-4 w-4 text-primary" />
              Privacy-Preserving Agent Snapshot Simulator
            </CardTitle>
            <Badge variant="outline" className="border-primary/50 text-primary text-xs">
              Zero PII Leakage Test
            </Badge>
          </div>
          <CardDescription>
            Simulate exact payload provided to downstream agents. Note that unconfirmed legal attestations and private contact points are redacted unless explicitly authorized.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-4">
            {agents.map((agent) => (
              <div
                key={agent.id}
                onClick={() => setSelectedAgent(agent.id)}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${selectedAgent === agent.id ? 'border-primary bg-primary/5 shadow-sm' : 'hover:border-muted-foreground/30'}`}
              >
                <div className="font-semibold text-xs text-foreground">{agent.name}</div>
                <div className="mt-1 text-[11px] text-muted-foreground line-clamp-2">
                  {agent.desc}
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button onClick={handleGenerate} disabled={isProcessing} size="sm">
              <Sparkles className="mr-2 h-4 w-4" />
              {isProcessing ? 'Generating Snapshot...' : `Generate ${selectedAgent} Snapshot`}
            </Button>
          </div>

          {snapshot && (
            <div className="mt-4 space-y-2 rounded-lg border bg-muted/30 p-4">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="font-semibold">Target Agent:</span>
                  <Badge variant="primary" className="text-[10px]">
                    {snapshot.target_agent}
                  </Badge>
                  <span className="text-muted-foreground">
                    (Version {snapshot.version} • {new Date(snapshot.generated_at).toLocaleTimeString()})
                  </span>
                </div>
                <Button size="sm" variant="ghost" onClick={handleCopy} className="h-7 text-xs">
                  {copied ? <Check className="mr-1 h-3.5 w-3.5" /> : <Copy className="mr-1 h-3.5 w-3.5" />}
                  {copied ? 'Copied' : 'Copy JSON'}
                </Button>
              </div>

              <div className="flex flex-wrap gap-1 text-[10px] text-muted-foreground pt-1">
                <span>Authorized Scopes:</span>
                {snapshot.authorized_scopes.map((sc, i) => (
                  <Badge key={i} variant="outline" className="text-[10px] font-mono">
                    {sc}
                  </Badge>
                ))}
              </div>

              <pre className="mt-3 max-h-80 overflow-auto rounded bg-background p-3 font-mono text-xs text-foreground">
                {JSON.stringify(snapshot.filtered_data, null, 2)}
              </pre>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Audit Versions Timeline */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <History className="h-4 w-4 text-primary" />
            Immutable Version Audit Trail
          </CardTitle>
          <CardDescription>
            Audit log of all profile modifications, field mutations, and provenance synchronizations.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {versionHistory.length === 0 ? (
            <p className="text-xs text-muted-foreground text-center py-6">
              Initial revision active. Subsequent edits will append immutable audit records here.
            </p>
          ) : (
            <div className="space-y-3">
              {versionHistory.map((ver) => (
                <div key={ver.id} className="rounded-lg border p-3 flex items-start justify-between text-xs">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-foreground">Revision v{ver.version}</span>
                      <span className="text-muted-foreground">• by {ver.changed_by}</span>
                    </div>

                    {ver.change_reason && (
                      <p className="text-muted-foreground">{ver.change_reason}</p>
                    )}

                    <div className="flex flex-wrap gap-1 pt-1">
                      <span className="text-muted-foreground mr-1">Modified:</span>
                      {ver.modified_fields.map((f, i) => (
                        <Badge key={i} variant="neutral" className="text-[10px] font-mono">
                          {f}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-1 text-muted-foreground text-[11px]">
                    <Clock className="h-3 w-3" />
                    <span>{new Date(ver.created_at).toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
