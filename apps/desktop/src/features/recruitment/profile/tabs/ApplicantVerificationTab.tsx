/**
 * Stage 21: Applicant Claims & Conflict Resolution Tab.
 * Granular provenance claims, verification status pills, and interactive conflict resolution.
 */

import * as React from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Check,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { ApplicantClaim, ProfileConflict, ClaimVerificationStatus } from '@autonom/shared-types';

interface ApplicantVerificationTabProps {
  claims: ApplicantClaim[];
  conflicts: ProfileConflict[];
  onConfirmClaim: (claimId: string, notes?: string) => Promise<void>;
  onRejectClaim: (claimId: string, reason?: string) => Promise<void>;
  onResolveConflict: (
    conflictId: string,
    choice: string,
    chosenClaimId?: string,
    manualVal?: any,
    rationale?: string
  ) => Promise<void>;
  isProcessing: boolean;
}

export const ApplicantVerificationTab: React.FC<ApplicantVerificationTabProps> = ({
  claims,
  conflicts,
  onConfirmClaim,
  onRejectClaim,
  onResolveConflict,
  isProcessing,
}) => {
  const [statusFilter, setStatusFilter] = React.useState<string>('all');
  const [categoryFilter, setCategoryFilter] = React.useState<string>('all');

  const filteredClaims = claims.filter((c) => {
    if (statusFilter !== 'all' && c.status !== statusFilter) return false;
    if (categoryFilter !== 'all' && c.category !== categoryFilter) return false;
    return true;
  });

  const getStatusBadge = (status: ClaimVerificationStatus) => {
    switch (status) {
      case 'evidence_supported':
      case 'externally_verified':
        return (
          <Badge className="bg-emerald-600 hover:bg-emerald-700 text-[10px]">
            <ShieldCheck className="h-3 w-3 mr-1" /> {status.replace(/_/g, ' ')}
          </Badge>
        );
      case 'user_confirmed':
        return (
          <Badge variant="primary" className="text-[10px]">
            <CheckCircle2 className="h-3 w-3 mr-1" /> User Confirmed
          </Badge>
        );
      case 'user_reported':
        return (
          <Badge variant="neutral" className="text-[10px]">
            User Reported
          </Badge>
        );
      case 'conflicted':
        return (
          <Badge variant="error" className="text-[10px]">
            <AlertTriangle className="h-3 w-3 mr-1" /> Conflicted
          </Badge>
        );
      case 'rejected':
        return (
          <Badge variant="outline" className="text-[10px] text-status-error border-status-error/30">
            Rejected
          </Badge>
        );
      default:
        return (
          <Badge variant="outline" className="text-[10px]">
            {status}
          </Badge>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Claim Registry & Provenance Verification</h3>
        <p className="text-sm text-muted-foreground">
          Atomic facts tracked with audit provenance. Zero unverified claims are accepted as ground truth without human confirmation.
        </p>
      </div>

      {/* Active Conflicts Resolver Banner */}
      {conflicts.length > 0 && (
        <Card className="border-amber-500 bg-amber-50/20 dark:bg-amber-950/20">
          <CardHeader>
            <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400">
              <AlertTriangle className="h-5 w-5" />
              <CardTitle className="text-base font-semibold">
                Detected Profile Conflicts ({conflicts.length})
              </CardTitle>
            </div>
            <CardDescription>
              Multiple imported sources or manual edits disagree on authoritative values. Choose resolution to maintain single-source-of-truth integrity.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {conflicts.map((conf) => (
              <div key={conf.id} className="rounded-lg border bg-card p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-sm">
                    Conflict on: <code className="text-primary">{conf.field_path}</code>
                  </span>
                  <Badge variant="outline" className="capitalize text-xs">
                    {conf.category}
                  </Badge>
                </div>

                <div className="grid gap-3 md:grid-cols-2">
                  <div className="rounded border p-3 bg-muted/30">
                    <div className="text-xs font-semibold text-muted-foreground">Claim A</div>
                    <pre className="mt-1 text-xs font-mono break-all whitespace-pre-wrap">
                      {typeof conf.claim_a_value === 'object'
                        ? JSON.stringify(conf.claim_a_value, null, 2)
                        : String(conf.claim_a_value)}
                    </pre>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => onResolveConflict(conf.id, 'keep_a', conf.claim_a_id, undefined, 'Selected Claim A')}
                      disabled={isProcessing}
                      className="mt-3 w-full text-xs"
                    >
                      Keep Claim A
                    </Button>
                  </div>

                  <div className="rounded border p-3 bg-muted/30">
                    <div className="text-xs font-semibold text-muted-foreground">Claim B</div>
                    <pre className="mt-1 text-xs font-mono break-all whitespace-pre-wrap">
                      {typeof conf.claim_b_value === 'object'
                        ? JSON.stringify(conf.claim_b_value, null, 2)
                        : String(conf.claim_b_value)}
                    </pre>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => onResolveConflict(conf.id, 'keep_b', conf.claim_b_id, undefined, 'Selected Claim B')}
                      disabled={isProcessing}
                      className="mt-3 w-full text-xs"
                    >
                      Keep Claim B
                    </Button>
                  </div>
                </div>

                <div className="flex justify-end pt-1">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => onResolveConflict(conf.id, 'dismiss', undefined, undefined, 'Dismissed by user')}
                    disabled={isProcessing}
                    className="text-xs text-muted-foreground"
                  >
                    Dismiss Conflict
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Claims Registry Filter Header */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle className="text-base font-semibold">Registered Provenance Claims</CardTitle>
            <div className="flex flex-wrap items-center gap-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="h-8 rounded-md border border-input bg-background px-2 text-xs shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
              >
                <option value="all">All Statuses</option>
                <option value="user_confirmed">User Confirmed</option>
                <option value="user_reported">User Reported</option>
                <option value="evidence_supported">Evidence Supported</option>
                <option value="unverified">Unverified</option>
                <option value="conflicted">Conflicted</option>
                <option value="rejected">Rejected</option>
              </select>

              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="h-8 rounded-md border border-input bg-background px-2 text-xs shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
              >
                <option value="all">All Categories</option>
                <option value="identity">Identity</option>
                <option value="contact">Contact</option>
                <option value="eligibility">Eligibility</option>
                <option value="education">Education</option>
                <option value="employment">Employment</option>
                <option value="skill">Skill</option>
                <option value="project">Project</option>
                <option value="certification">Certification</option>
              </select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {filteredClaims.length === 0 ? (
            <p className="text-xs text-muted-foreground text-center py-8">
              No claims match the active filters.
            </p>
          ) : (
            <div className="space-y-3">
              {filteredClaims.map((claim) => (
                <div key={claim.id} className="rounded-lg border p-3 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-foreground font-mono">{claim.field_path}</span>
                      <Badge variant="outline" className="capitalize text-[10px]">
                        {claim.category}
                      </Badge>
                      {getStatusBadge(claim.status)}
                    </div>

                    <div className="font-mono text-muted-foreground bg-muted/40 p-1.5 rounded max-w-xl break-all">
                      {typeof claim.claimed_value === 'object'
                        ? JSON.stringify(claim.claimed_value)
                        : String(claim.claimed_value)}
                    </div>

                    <div className="flex items-center gap-3 text-[11px] text-muted-foreground">
                      <span>Source: {claim.provenance_source || 'direct_user_input'}</span>
                      <span>Confidence: {Math.round(claim.confidence_score * 100)}%</span>
                      {claim.evidence_ids && claim.evidence_ids.length > 0 && (
                        <span className="text-emerald-600 font-medium">
                          Backed by {claim.evidence_ids.length} doc(s)
                        </span>
                      )}
                    </div>
                  </div>

                  {claim.status === 'unverified' || claim.status === 'user_reported' ? (
                    <div className="flex items-center gap-1.5 self-end md:self-center">
                      <Button
                        size="sm"
                        variant="primary"
                        onClick={() => onConfirmClaim(claim.id)}
                        disabled={isProcessing}
                        className="h-7 text-xs bg-emerald-600 hover:bg-emerald-700"
                      >
                        <Check className="mr-1 h-3.5 w-3.5" /> Confirm
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => onRejectClaim(claim.id)}
                        disabled={isProcessing}
                        className="h-7 text-xs text-destructive hover:bg-destructive/10"
                      >
                        <XCircle className="mr-1 h-3.5 w-3.5" /> Reject
                      </Button>
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
