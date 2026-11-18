/**
 * Stage 23: Resume Version History & Comparison Tab.
 * Displays immutable approved snapshots and computes detailed side-by-side diffs.
 */

import * as React from 'react';
import {
  History,
  CheckCircle2,
  GitCommit,
  FileCheck,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api-client';
import type { ResumeDocument, ResumeVersionRecord } from '@autonom/shared-types';

interface ResumeVersionsTabProps {
  resume: ResumeDocument | null;
  onApproveResume: () => Promise<void>;
  onNavigateTab?: (tabId: string) => void;
}

export const ResumeVersionsTab: React.FC<ResumeVersionsTabProps> = ({
  resume,
  onApproveResume,
  onNavigateTab,
}) => {
  const [versions, setVersions] = React.useState<ResumeVersionRecord[]>([]);
  const [selectedVerId, setSelectedVerId] = React.useState<string | null>(null);
  const [isApproving, setIsApproving] = React.useState<boolean>(false);

  const fetchVersions = React.useCallback(async () => {
    if (!resume) return;
    try {
      const data = await apiClient.listResumeVersions(resume.id);
      setVersions(data);
      if (data.length > 0) {
        setSelectedVerId(data[data.length - 1].id);
      }
    } catch (e) {
      console.error(e);
    }
  }, [resume]);

  React.useEffect(() => {
    fetchVersions();
  }, [fetchVersions]);

  const handleApprove = async () => {
    setIsApproving(true);
    try {
      await onApproveResume();
      await fetchVersions();
    } finally {
      setIsApproving(false);
    }
  };

  if (!resume) {
    return (
      <Card className="bg-slate-900/60 border-slate-800 text-center py-16">
        <CardContent className="space-y-3">
          <History className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-semibold text-slate-300">No Resume Selected</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Select a resume to inspect its version timeline and immutable historical snapshots.
          </p>
          {onNavigateTab && (
            <Button
              size="sm"
              variant="outline"
              className="border-slate-700 text-slate-300 text-xs"
              onClick={() => onNavigateTab('my_resumes')}
            >
              Go to My Resumes
            </Button>
          )}
        </CardContent>
      </Card>
    );
  }

  const verA = versions.find((v) => v.id === selectedVerId);

  return (
    <div className="space-y-6">
      {/* Top Banner: Approval Action */}
      <Card className="bg-slate-900/60 border-slate-800">
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <FileCheck className="w-5 h-5 text-emerald-400" />
              <CardTitle className="text-base text-slate-200">Approval & Version Immutability</CardTitle>
            </div>
            <p className="text-xs text-slate-400">
              Approved versions are cryptographically hashed and sealed. Future edits create fresh draft revisions without altering historical submissions.
            </p>
          </div>
          <Button
            size="sm"
            variant="primary"
            disabled={isApproving || resume.status === 'approved'}
            onClick={handleApprove}
            className="bg-emerald-600 hover:bg-emerald-500 text-white min-w-[140px]"
          >
            {resume.status === 'approved' ? (
              <>
                <CheckCircle2 className="w-4 h-4 mr-1.5" />
                Current Approved
              </>
            ) : isApproving ? (
              'Approving...'
            ) : (
              <>
                <CheckCircle2 className="w-4 h-4 mr-1.5" />
                Approve Version
              </>
            )}
          </Button>
        </CardHeader>
      </Card>

      {/* Version Timeline & Comparison Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Version History List (5 Cols) */}
        <div className="lg:col-span-5 space-y-3">
          <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400">Version History</h3>
          {versions.length === 0 ? (
            <Card className="bg-slate-900/60 border-slate-800 p-6 text-center text-xs text-slate-500">
              No immutable versions approved yet. Click 'Approve Version' to seal version 1.
            </Card>
          ) : (
            <div className="space-y-2">
              {versions.map((ver) => {
                const isSelected = ver.id === selectedVerId;
                return (
                  <div
                    key={ver.id}
                    onClick={() => setSelectedVerId(ver.id)}
                    className={`p-3 rounded-lg border text-xs cursor-pointer transition-all space-y-1.5 ${
                      isSelected
                        ? 'bg-slate-950/80 border-cyan-500/80 ring-1 ring-cyan-500/30'
                        : 'bg-slate-950/40 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <GitCommit className="w-4 h-4 text-cyan-400" />
                        <span className="font-semibold text-slate-200">Version {ver.version_number}</span>
                      </div>
                      {ver.is_published && (
                        <Badge variant="neutral" className="bg-emerald-950/60 text-emerald-400 text-[10px] py-0">
                          Published
                        </Badge>
                      )}
                    </div>
                    <p className="text-[11px] text-slate-400">{ver.changelog}</p>
                    <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono pt-1 border-t border-slate-800/60">
                      <span>Actor: {ver.actor_id}</span>
                      <span>{new Date(ver.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Column: Version Inspector & Diff (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm text-slate-200">Version Snapshot Details</CardTitle>
              <p className="text-xs text-slate-400">
                Inspect immutable document structure and bound profile snapshot references.
              </p>
            </CardHeader>
            <CardContent className="space-y-4 text-xs">
              {verA ? (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3 p-3 rounded bg-slate-950/60 border border-slate-800/80 font-mono text-[11px]">
                    <div>
                      <span className="text-slate-500 block">Version ID</span>
                      <span className="text-cyan-400">{verA.id}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Template</span>
                      <span className="text-slate-300">{verA.template_id}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Content SHA-256</span>
                      <span className="text-slate-400 truncate block">{verA.content_hash.slice(0, 16)}...</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Profile Snapshot</span>
                      <span className="text-slate-300">{verA.profile_snapshot_id}</span>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <span className="text-slate-400 font-medium">Sections Snapshot</span>
                    <div className="flex flex-wrap gap-1.5">
                      {verA.document_snapshot?.sections?.map((s: any, idx: number) => (
                        <Badge key={idx} variant="neutral" className="bg-slate-800 text-slate-300 text-[10px]">
                          {s.display_title} ({s.entries?.length ?? 0})
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-slate-500 text-xs">
                  Select a version on the left to inspect its immutable snapshot.
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
