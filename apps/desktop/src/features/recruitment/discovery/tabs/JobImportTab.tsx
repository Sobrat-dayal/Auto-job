/**
 * Tab: Single Job Import (Stage 26).
 * Import a posting via direct URL or manual description entry.
 */

import * as React from 'react';
import { Link2, FileText, CheckCircle2, Loader2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type { JobSourceObservation } from '@autonom/shared-types';

interface JobImportTabProps {
  onImportSuccess: (obs: JobSourceObservation) => void;
}

export const JobImportTab: React.FC<JobImportTabProps> = ({ onImportSuccess }) => {
  const [mode, setMode] = React.useState<'url' | 'manual'>('url');
  const [isLoading, setIsLoading] = React.useState(false);
  const [result, setResult] = React.useState<JobSourceObservation | null>(null);

  // URL mode state
  const [targetUrl, setTargetUrl] = React.useState('');
  const [urlEmployer, setUrlEmployer] = React.useState('');
  const [targetRole, setTargetRole] = React.useState('');

  // Manual mode state
  const [manualTitle, setManualTitle] = React.useState('');
  const [manualEmployer, setManualEmployer] = React.useState('');
  const [manualLocation, setManualLocation] = React.useState('');
  const [manualSalary, setManualSalary] = React.useState('');
  const [manualDesc, setManualDesc] = React.useState('');

  const handleUrlImport = async () => {
    if (!targetUrl.trim()) {
      alert('Please enter a valid job URL.');
      return;
    }
    try {
      setIsLoading(true);
      setResult(null);
      const obs = await apiClient.importJobUrl({
        url: targetUrl.trim(),
        employer_name: urlEmployer.trim() || undefined,
        target_role: targetRole.trim() || undefined,
      });
      setResult(obs);
      onImportSuccess(obs);
      setTargetUrl('');
    } catch (err: any) {
      alert(`Import failed: ${err.message || String(err)}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleManualImport = async () => {
    if (!manualTitle.trim() || !manualEmployer.trim() || !manualDesc.trim()) {
      alert('Title, Employer, and Description are required.');
      return;
    }
    try {
      setIsLoading(true);
      setResult(null);
      const obs = await apiClient.importJobManual({
        title: manualTitle.trim(),
        employer_name: manualEmployer.trim(),
        description: manualDesc.trim(),
        location: manualLocation.trim() || undefined,
        compensation_text: manualSalary.trim() || undefined,
      });
      setResult(obs);
      onImportSuccess(obs);
      setManualTitle('');
      setManualDesc('');
    } catch (err: any) {
      alert(`Manual import failed: ${err.message || String(err)}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Mode Selection */}
      <div className="flex items-center gap-2 border-b pb-3">
        <Button
          variant={mode === 'url' ? 'primary' : 'outline'}
          size="sm"
          className="text-xs"
          onClick={() => setMode('url')}
        >
          <Link2 className="w-3.5 h-3.5 mr-2" />
          Import from Job URL
        </Button>
        <Button
          variant={mode === 'manual' ? 'primary' : 'outline'}
          size="sm"
          className="text-xs"
          onClick={() => setMode('manual')}
        >
          <FileText className="w-3.5 h-3.5 mr-2" />
          Manual Job Posting Entry
        </Button>
      </div>

      {mode === 'url' ? (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold">Import Job from Web URL</CardTitle>
            <CardDescription className="text-xs">
              Supports Greenhouse, Lever, Ashby, Schema.org JobPosting, or company career URLs. Strict SSRF checks protect your host.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            <div className="space-y-1">
              <label className="font-medium">Job Posting URL *</label>
              <Input
                placeholder="https://boards.greenhouse.io/stripe/jobs/12345 or https://jobs.lever.co/netflix/abc-123"
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="font-medium">Employer Name (Optional Override)</label>
                <Input
                  placeholder="e.g. Stripe"
                  value={urlEmployer}
                  onChange={(e) => setUrlEmployer(e.target.value)}
                />
              </div>
              <div className="space-y-1">
                <label className="font-medium">Role Title (Optional Override)</label>
                <Input
                  placeholder="e.g. Staff Backend Engineer"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                />
              </div>
            </div>
            <div className="pt-2 flex justify-end">
              <Button size="sm" disabled={isLoading} onClick={handleUrlImport}>
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Fetching & Extracting...
                  </>
                ) : (
                  <>
                    <Link2 className="w-4 h-4 mr-2" />
                    Import Opportunity
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold">Manually Supply Job Posting</CardTitle>
            <CardDescription className="text-xs">
              Paste or type in a job description received from a recruiter, email, or unlisted portal.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="font-medium">Job Title *</label>
                <Input
                  placeholder="e.g. Distributed Systems Engineer"
                  value={manualTitle}
                  onChange={(e) => setManualTitle(e.target.value)}
                />
              </div>
              <div className="space-y-1">
                <label className="font-medium">Employer / Company *</label>
                <Input
                  placeholder="e.g. OpenAI"
                  value={manualEmployer}
                  onChange={(e) => setManualEmployer(e.target.value)}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="font-medium">Location / Work Arrangement</label>
                <Input
                  placeholder="e.g. Remote (US) or San Francisco, CA"
                  value={manualLocation}
                  onChange={(e) => setManualLocation(e.target.value)}
                />
              </div>
              <div className="space-y-1">
                <label className="font-medium">Published Salary (Optional)</label>
                <Input
                  placeholder="e.g. $180,000 - $220,000 / year"
                  value={manualSalary}
                  onChange={(e) => setManualSalary(e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-1">
              <label className="font-medium">Job Description Text *</label>
              <textarea
                className="w-full min-h-[140px] rounded-md border bg-background p-3 text-xs font-sans"
                placeholder="Paste the full job description here..."
                value={manualDesc}
                onChange={(e) => setManualDesc(e.target.value)}
              />
            </div>
            <div className="pt-2 flex justify-end">
              <Button size="sm" disabled={isLoading} onClick={handleManualImport}>
                {isLoading ? 'Processing...' : 'Save Job Posting'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Imported Result Box */}
      {result && (
        <Card className="border-emerald-900/40 bg-emerald-950/10">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                Successfully Observed Posting
              </CardTitle>
              <Badge variant="outline">{result.id}</Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-2 text-xs">
            <div>
              <span className="font-medium text-foreground">{result.title}</span> at{' '}
              <span className="font-medium text-foreground">{result.employer}</span>
            </div>
            <div className="flex items-center gap-2">
              <span>Policy Evaluation:</span>
              <Badge
                variant="outline"
                className={`text-[10px] ${
                  result.prefilter_status === 'prefilter_accepted'
                    ? 'text-emerald-600 border-emerald-300'
                    : 'text-amber-600 border-amber-300'
                }`}
              >
                {result.prefilter_status.replace(/_/g, ' ')}
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
