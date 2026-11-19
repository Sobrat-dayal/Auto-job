/**
 * Tab: Discovered Jobs (Stage 26).
 * Lists all discovered job observations with provenance and Stage 25 policy pre-filtering.
 */

import * as React from 'react';
import {
  Search,
  ExternalLink,
  MapPin,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import type { JobSourceObservation, JobSourceConfig } from '@autonom/shared-types';

interface DiscoveredJobsTabProps {
  postings: JobSourceObservation[];
  sources: JobSourceConfig[];
}

export const DiscoveredJobsTab: React.FC<DiscoveredJobsTabProps> = ({ postings, sources }) => {
  const [searchQuery, setSearchQuery] = React.useState('');
  const [selectedSourceId, setSelectedSourceId] = React.useState<string>('all');
  const [selectedPrefilter, setSelectedPrefilter] = React.useState<string>('all');
  const [selectedJob, setSelectedJob] = React.useState<JobSourceObservation | null>(null);

  const filtered = postings.filter((p) => {
    if (selectedSourceId !== 'all' && p.source_id !== selectedSourceId) return false;
    if (selectedPrefilter !== 'all' && p.prefilter_status !== selectedPrefilter) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        p.title.toLowerCase().includes(q) ||
        p.employer.toLowerCase().includes(q) ||
        p.description_text.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="space-y-4">
      {/* Filters Bar */}
      <div className="flex flex-col md:flex-row items-center gap-3 p-3 rounded-lg border bg-card text-xs">
        <div className="relative flex-1 w-full">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-muted-foreground" />
          <Input
            placeholder="Search discovered vacancies by title, employer, keywords..."
            className="pl-8 h-8 text-xs"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2 w-full md:w-auto">
          <select
            className="h-8 rounded-md border bg-background px-2 text-xs"
            value={selectedSourceId}
            onChange={(e) => setSelectedSourceId(e.target.value)}
          >
            <option value="all">All Sources ({sources.length})</option>
            {sources.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
          <select
            className="h-8 rounded-md border bg-background px-2 text-xs"
            value={selectedPrefilter}
            onChange={(e) => setSelectedPrefilter(e.target.value)}
          >
            <option value="all">All Policy Outcomes</option>
            <option value="prefilter_accepted">Accepted by Policy</option>
            <option value="prefilter_rejected">Rejected by Policy</option>
            <option value="needs_review">Needs Review</option>
          </select>
        </div>
      </div>

      {/* Postings Counter */}
      <div className="flex items-center justify-between text-xs text-muted-foreground px-1">
        <span>
          Showing {filtered.length} of {postings.length} observed job postings
        </span>
      </div>

      {/* Postings Roster */}
      {filtered.length === 0 ? (
        <Card className="border">
          <CardContent className="py-12 text-center text-sm text-muted-foreground">
            No job observations match your active filters.
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {filtered.map((job) => (
            <Card
              key={job.id}
              className="border hover:border-primary/50 transition-colors cursor-pointer"
              onClick={() => setSelectedJob(job)}
            >
              <CardContent className="p-4 space-y-2">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h4 className="font-semibold text-sm hover:text-primary transition-colors">
                      {job.title}
                    </h4>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
                      <span className="font-medium text-foreground">{job.employer}</span>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {job.location.city || (job.location.is_remote ? 'Remote' : 'Location Unspecified')}
                      </span>
                      {job.compensation?.min_amount && (
                        <>
                          <span>•</span>
                          <span className="text-emerald-700 dark:text-emerald-400 font-medium">
                            ${(job.compensation.min_amount / 1000).toFixed(0)}k - ${(job.compensation.max_amount! / 1000).toFixed(0)}k
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Badge
                      variant="outline"
                      className={`text-[10px] ${
                        job.prefilter_status === 'prefilter_accepted'
                          ? 'text-emerald-600 border-emerald-300'
                          : job.prefilter_status === 'prefilter_rejected'
                          ? 'text-rose-600 border-rose-300'
                          : 'text-amber-600 border-amber-300'
                      }`}
                    >
                      {job.prefilter_status.replace(/_/g, ' ')}
                    </Badge>
                    <Badge
                      variant="neutral"
                      className={`text-[10px] ${
                        job.availability === 'available' ? 'bg-emerald-950/20 text-emerald-400' : 'text-muted-foreground'
                      }`}
                    >
                      {job.availability}
                    </Badge>
                  </div>
                </div>

                {job.description_text && (
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {job.description_text}
                  </p>
                )}

                <div className="flex items-center justify-between pt-2 border-t text-[11px] text-muted-foreground">
                  <div>
                    Source: <span className="font-mono">{job.provider}</span> • Fetched: {new Date(job.last_fetched_at).toLocaleDateString()}
                  </div>
                  <div className="flex items-center gap-3">
                    <a
                      href={job.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-blue-500 hover:underline flex items-center gap-1"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <ExternalLink className="w-3 h-3" />
                      Original Listing
                    </a>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Posting Details Modal Dialog */}
      <Dialog open={!!selectedJob} onOpenChange={(open) => !open && setSelectedJob(null)}>
        <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
          {selectedJob && (
            <>
              <DialogHeader>
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <DialogTitle className="text-base font-semibold">{selectedJob.title}</DialogTitle>
                    <DialogDescription className="text-xs font-medium text-foreground mt-0.5">
                      {selectedJob.employer} • {selectedJob.location.city || 'Remote'}
                    </DialogDescription>
                  </div>
                  <Badge variant="outline" className="capitalize text-xs">
                    {selectedJob.prefilter_status.replace(/_/g, ' ')}
                  </Badge>
                </div>
              </DialogHeader>

              <div className="space-y-4 py-2 text-xs">
                {/* Policy evaluation box */}
                <div className="p-3 rounded border bg-muted/40 space-y-1">
                  <span className="font-semibold">Stage 25 Policy Pre-filter Evaluation:</span>
                  <div className="text-muted-foreground">
                    {selectedJob.prefilter_reasons.join('; ') || 'Standard criteria satisfied.'}
                  </div>
                </div>

                {/* Metadata details */}
                <div className="grid grid-cols-2 gap-3 border p-3 rounded text-muted-foreground">
                  <div>
                    <span className="font-medium text-foreground">Native Posting ID:</span>{' '}
                    <span className="font-mono">{selectedJob.native_posting_id}</span>
                  </div>
                  <div>
                    <span className="font-medium text-foreground">Connector:</span> {selectedJob.provider}
                  </div>
                  <div>
                    <span className="font-medium text-foreground">Availability:</span> {selectedJob.availability}
                  </div>
                  <div>
                    <span className="font-medium text-foreground">Work Arrangement:</span>{' '}
                    {selectedJob.location.workplace_type || 'Unspecified'}
                  </div>
                  {selectedJob.compensation?.min_amount && (
                    <div className="col-span-2">
                      <span className="font-medium text-foreground">Compensation:</span>{' '}
                      ${selectedJob.compensation.min_amount.toLocaleString()} - ${selectedJob.compensation.max_amount?.toLocaleString()} {selectedJob.compensation.currency}
                    </div>
                  )}
                </div>

                {/* Job Description */}
                <div className="space-y-1">
                  <h4 className="font-semibold text-xs">Job Description:</h4>
                  <div className="p-3 rounded border bg-card whitespace-pre-line max-h-60 overflow-y-auto font-sans text-xs leading-relaxed">
                    {selectedJob.description_text || 'No text description available.'}
                  </div>
                </div>

                {/* Direct Action Link */}
                <div className="flex items-center justify-end gap-3 pt-2">
                  <a
                    href={selectedJob.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center justify-center rounded-md text-xs font-medium h-8 px-4 py-2 bg-primary text-primary-foreground hover:bg-primary/90"
                  >
                    <ExternalLink className="w-3.5 h-3.5 mr-2" />
                    Open Source Job Page
                  </a>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};
