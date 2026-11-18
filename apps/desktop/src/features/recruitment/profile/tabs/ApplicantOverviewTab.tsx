/**
 * Stage 21: Applicant Profile Overview Tab.
 * Summary, recruitment readiness scorecard, data quality evaluation, and quick statistics.
 */

import * as React from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  FileCheck2,
  ShieldCheck,
  Award,
  RefreshCw,
  Download,
  AlertCircle,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { ApplicantProfile, DataQualityReport } from '@autonom/shared-types';

interface ApplicantOverviewTabProps {
  profile: ApplicantProfile | null;
  quality: DataQualityReport | null;
  isLoading: boolean;
  onRefresh: () => void;
  onExport: () => void;
}

export const ApplicantOverviewTab: React.FC<ApplicantOverviewTabProps> = ({
  profile,
  quality,
  isLoading,
  onRefresh,
  onExport,
}) => {
  if (!profile) {
    return (
      <div className="flex h-64 items-center justify-center text-muted-foreground">
        No active profile loaded.
      </div>
    );
  }

  const overallScore = quality?.overall_score ?? 0;
  const readiness = quality?.readiness_status ?? 'incomplete';

  const readinessBadgeVariant: 'success' | 'warning' | 'error' | 'primary' =
    readiness === 'comprehensive' || readiness === 'verified_for_agents'
      ? 'success'
      : readiness === 'ready_for_review'
        ? 'primary'
        : 'error';

  return (
    <div className="space-y-6">
      {/* Top Banner / Headline */}
      <div className="flex flex-col justify-between gap-4 rounded-lg border bg-card p-6 shadow-sm md:flex-row md:items-center">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold tracking-tight">{profile.display_label}</h2>
            <Badge variant="outline" className="font-mono text-xs">
              v{profile.version}
            </Badge>
            <Badge variant={readinessBadgeVariant} className="capitalize">
              {readiness.replace(/_/g, ' ')}
            </Badge>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">
            Authoritative Single Source of Truth for recruitment agents. All downstream resumes, applications, and job matches derive strictly from verified facts here.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={onRefresh} disabled={isLoading}>
            <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Re-evaluate
          </Button>
          <Button variant="primary" size="sm" onClick={onExport}>
            <Download className="mr-2 h-4 w-4" />
            Export Portable Profile
          </Button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Quality Score</CardTitle>
            <Award className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overallScore}%</div>
            <p className="text-xs text-muted-foreground">
              Completeness: {quality?.completeness_score ?? 0}% • Consistency: {quality?.consistency_score ?? 0}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Claims In Registry</CardTitle>
            <ShieldCheck className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{quality?.total_claims ?? 0}</div>
            <p className="text-xs text-muted-foreground">
              {quality?.verified_claims ?? 0} verified • {quality?.unverified_claims ?? 0} unverified
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Evidence Coverage</CardTitle>
            <FileCheck2 className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{quality?.evidence_coverage_score ?? 0}%</div>
            <p className="text-xs text-muted-foreground">
              Document provenance & SHA-256 backing
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Active Conflicts</CardTitle>
            <AlertTriangle className={`h-4 w-4 ${(quality?.conflicted_claims ?? 0) > 0 ? 'text-amber-500' : 'text-muted-foreground'}`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{quality?.conflicted_claims ?? 0}</div>
            <p className="text-xs text-muted-foreground">
              {(quality?.conflicted_claims ?? 0) > 0 ? 'Requires human resolution' : 'Zero conflicting claims'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Readiness Checklist & Profile Composition */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-semibold">Recruitment Agent Readiness Checklist</CardTitle>
            <CardDescription>
              Pre-flight validation required before autonomous job matching or resume tailoring begins.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between rounded-md border p-3">
              <div className="flex items-center gap-3">
                <CheckCircle2 className={`h-5 w-5 ${profile.contact?.legal_name ? 'text-emerald-500' : 'text-muted-foreground'}`} />
                <div>
                  <div className="text-sm font-medium">Identity & Legal Name</div>
                  <div className="text-xs text-muted-foreground">
                    {profile.contact?.legal_name ? profile.contact.legal_name : 'Missing legal name'}
                  </div>
                </div>
              </div>
              <Badge variant={profile.contact?.legal_name ? 'outline' : 'neutral'}>
                {profile.contact?.legal_name ? 'Provided' : 'Pending'}
              </Badge>
            </div>

            <div className="flex items-center justify-between rounded-md border p-3">
              <div className="flex items-center gap-3">
                <CheckCircle2 className={`h-5 w-5 ${profile.contact?.primary_email ? 'text-emerald-500' : 'text-muted-foreground'}`} />
                <div>
                  <div className="text-sm font-medium">Primary Contact Info</div>
                  <div className="text-xs text-muted-foreground">
                    {profile.contact?.primary_email ? profile.contact.primary_email : 'No email address registered'}
                  </div>
                </div>
              </div>
              <Badge variant={profile.contact?.primary_email ? 'outline' : 'neutral'}>
                {profile.contact?.primary_email ? 'Configured' : 'Missing'}
              </Badge>
            </div>

            <div className="flex items-center justify-between rounded-md border p-3">
              <div className="flex items-center gap-3">
                <CheckCircle2 className={`h-5 w-5 ${profile.eligibility?.citizenship_country ? 'text-emerald-500' : 'text-muted-foreground'}`} />
                <div>
                  <div className="text-sm font-medium">Employment Eligibility</div>
                  <div className="text-xs text-muted-foreground">
                    {profile.eligibility?.citizenship_country
                      ? `${profile.eligibility.citizenship_country} • ${profile.eligibility.requires_sponsorship ? 'Sponsorship required' : 'No sponsorship required'}`
                      : 'Attestation not completed'}
                  </div>
                </div>
              </div>
              <Badge variant={profile.eligibility?.citizenship_country ? 'outline' : 'neutral'}>
                {profile.eligibility?.citizenship_country ? 'Attested' : 'Incomplete'}
              </Badge>
            </div>

            <div className="flex items-center justify-between rounded-md border p-3">
              <div className="flex items-center gap-3">
                <CheckCircle2 className={`h-5 w-5 ${profile.education?.length > 0 ? 'text-emerald-500' : 'text-muted-foreground'}`} />
                <div>
                  <div className="text-sm font-medium">Education Credentials</div>
                  <div className="text-xs text-muted-foreground">
                    {profile.education?.length > 0 ? `${profile.education.length} degree(s) recorded` : 'No degrees listed'}
                  </div>
                </div>
              </div>
              <Badge variant={profile.education?.length > 0 ? 'outline' : 'neutral'}>
                {profile.education?.length > 0 ? `${profile.education.length} Degrees` : 'Empty'}
              </Badge>
            </div>

            <div className="flex items-center justify-between rounded-md border p-3">
              <div className="flex items-center gap-3">
                <CheckCircle2 className={`h-5 w-5 ${profile.employment?.length > 0 ? 'text-emerald-500' : 'text-muted-foreground'}`} />
                <div>
                  <div className="text-sm font-medium">Work History & Experience</div>
                  <div className="text-xs text-muted-foreground">
                    {profile.employment?.length > 0 ? `${profile.employment.length} positions recorded` : 'No work experience listed'}
                  </div>
                </div>
              </div>
              <Badge variant={profile.employment?.length > 0 ? 'outline' : 'neutral'}>
                {profile.employment?.length > 0 ? `${profile.employment.length} Roles` : 'Empty'}
              </Badge>
            </div>

            <div className="flex items-center justify-between rounded-md border p-3">
              <div className="flex items-center gap-3">
                <CheckCircle2 className={`h-5 w-5 ${profile.skills?.length > 0 ? 'text-emerald-500' : 'text-muted-foreground'}`} />
                <div>
                  <div className="text-sm font-medium">Skills Inventory</div>
                  <div className="text-xs text-muted-foreground">
                    {profile.skills?.length > 0 ? `${profile.skills.length} technical & domain skills` : 'No skills recorded'}
                  </div>
                </div>
              </div>
              <Badge variant={profile.skills?.length > 0 ? 'outline' : 'neutral'}>
                {profile.skills?.length > 0 ? `${profile.skills.length} Skills` : 'Empty'}
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Quality Issues / Recommendations */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-semibold">Data Quality & Validation Notices</CardTitle>
            <CardDescription>
              Deterministic audits and completeness checks preventing agent hallucinations.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {(!quality?.issues || quality.issues.length === 0) ? (
              <div className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground">
                <ShieldCheck className="mb-2 h-10 w-10 text-emerald-500" />
                <p className="text-sm font-medium">No Data Quality Issues Detected</p>
                <p className="text-xs">All records meet recruitment readiness standards.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {quality.issues.map((issue, idx) => (
                  <div key={idx} className="rounded-md border p-3 text-sm">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 font-medium">
                        <AlertCircle className={`h-4 w-4 ${issue.severity === 'critical' ? 'text-status-error' : issue.severity === 'high' ? 'text-status-warning' : 'text-primary'}`} />
                        <span className="capitalize">{issue.category}</span>
                      </div>
                      <Badge variant={issue.severity === 'critical' || issue.severity === 'high' ? 'error' : 'outline'} className="text-[10px]">
                        {issue.severity}
                      </Badge>
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">{issue.message}</p>
                    {issue.recommendation && (
                      <p className="mt-1 text-xs text-primary">Tip: {issue.recommendation}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
