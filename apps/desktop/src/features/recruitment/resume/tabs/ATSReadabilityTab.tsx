/**
 * Stage 23: ATS Readability & Structural Audit Tab.
 * Inspectable checklist of real structural properties without fabricated acceptance percentages.
 */

import * as React from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  RefreshCw,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api-client';
import type { ATSReadabilityReport, ResumeDocument } from '@autonom/shared-types';

interface ATSReadabilityTabProps {
  resume: ResumeDocument | null;
}

export const ATSReadabilityTab: React.FC<ATSReadabilityTabProps> = ({ resume }) => {
  const [report, setReport] = React.useState<ATSReadabilityReport | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);

  const fetchReport = React.useCallback(async () => {
    if (!resume) return;
    setIsLoading(true);
    try {
      const data = await apiClient.getResumeATSReport(resume.id);
      setReport(data);
    } finally {
      setIsLoading(false);
    }
  }, [resume]);

  React.useEffect(() => {
    fetchReport();
  }, [fetchReport]);

  if (!resume) {
    return (
      <Card className="bg-slate-900/60 border-slate-800 text-center py-16">
        <CardContent className="space-y-3">
          <ShieldCheck className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-semibold text-slate-300">No Resume Selected</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Select an active resume to run a deterministic ATS readability and machine-parsing audit.
          </p>
        </CardContent>
      </Card>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass':
        return <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />;
      default:
        return <HelpCircle className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-slate-900/60 border-slate-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-mono uppercase tracking-wider text-slate-400">
              Audit Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span className={`text-2xl font-bold font-mono ${
                report?.overall_status === 'pass' ? 'text-emerald-400' : report?.overall_status === 'warning' ? 'text-amber-400' : 'text-rose-400'
              }`}>
                {report?.overall_status ? report.overall_status.toUpperCase() : 'AUDITING'}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">Structural compliance</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-mono uppercase tracking-wider text-slate-400">
              Passed Checks
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-emerald-400">
              {report?.passed_count ?? 0}
            </div>
            <p className="text-xs text-slate-400 mt-1">Verified safe properties</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-mono uppercase tracking-wider text-slate-400">
              Warnings
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-amber-400">
              {report?.warning_count ?? 0}
            </div>
            <p className="text-xs text-slate-400 mt-1">Review recommendations</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-mono uppercase tracking-wider text-slate-400">
              Errors
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-rose-400">
              {report?.error_count ?? 0}
            </div>
            <p className="text-xs text-slate-400 mt-1">Critical parsing blocks</p>
          </CardContent>
        </Card>
      </div>

      {/* Transparent Checklist Panel */}
      <Card className="bg-slate-900/60 border-slate-800">
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <div>
            <CardTitle className="text-sm text-slate-200">Inspectable ATS Properties Checklist</CardTitle>
            <p className="text-xs text-slate-400">
              Evaluating machine-readability, standard headings, accessible contact data, and chronology.
            </p>
          </div>
          <Button
            size="sm"
            variant="outline"
            disabled={isLoading}
            onClick={fetchReport}
            className="border-slate-700 text-slate-300"
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isLoading ? 'animate-spin' : ''}`} />
            Re-Audit
          </Button>
        </CardHeader>
        <CardContent className="space-y-3">
          {report?.checks.map((check, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs space-y-2"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getStatusIcon(check.status)}
                  <span className="font-semibold text-slate-200">{check.check_name}</span>
                </div>
                <Badge
                  variant="neutral"
                  className={
                    check.status === 'pass'
                      ? 'bg-emerald-950/60 text-emerald-400 border-emerald-800/60 text-[10px]'
                      : check.status === 'warning'
                      ? 'bg-amber-950/60 text-amber-400 border-amber-800/60 text-[10px]'
                      : 'bg-rose-950/60 text-rose-400 border-rose-800/60 text-[10px]'
                  }
                >
                  {check.status.toUpperCase()}
                </Badge>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] pt-1 border-t border-slate-800/60 text-slate-400">
                <div>
                  <span className="text-slate-500 font-medium block">Observed Evidence:</span>
                  <span>{check.observed_evidence}</span>
                </div>
                <div>
                  <span className="text-slate-500 font-medium block">Parser Impact:</span>
                  <span>{check.impact_explanation}</span>
                </div>
              </div>

              {check.suggested_remediation && (
                <div className="p-2 rounded bg-amber-950/20 border border-amber-800/40 text-[11px] text-amber-300">
                  <strong>Suggested Fix:</strong> {check.suggested_remediation}
                </div>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Disclaimers & Ethics Notice */}
      <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs text-slate-400 space-y-1">
        <span className="font-semibold text-slate-300 block">ATS Audit Transparency Policy</span>
        <p className="text-[11px] leading-relaxed">
          AUTONOM reports only verified structural and machine-readability properties. It does not fabricate universal "95% ATS match scores", guarantee interview callbacks, or claim to replicate proprietary parsing engines of individual commercial vendors (Workday, Taleo, Greenhouse, iCIMS).
        </p>
      </div>
    </div>
  );
};
