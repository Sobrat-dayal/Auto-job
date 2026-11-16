import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  BriefcaseBusiness,
  Building2,
  MapPin,
  Clock,
  ExternalLink,
  DollarSign,
  Eye,
} from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleToolbar,
  ModuleTabs,
  ModuleUnavailableState,
  ModuleDetailPanel,
  ModuleLoadingState,
  ModuleEmptyState,
  ModuleErrorState,
} from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { Button, buttonVariants } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { apiClient } from '@/lib/api-client';
import type { ApplicationItem, JobListingItem } from '@/types/modules';

export const RecruitmentWorkspace: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const getInitialTab = (): string => {
    if (location.pathname.includes('/recruitment/recommended')) return 'recommended';
    if (location.pathname.includes('/recruitment/pipeline')) return 'pipeline';
    if (location.pathname.includes('/recruitment/submitted')) return 'submitted';
    if (location.pathname.includes('/recruitment/history')) return 'history';
    if (location.pathname.includes('/recruitment/excluded')) return 'excluded';
    if (location.pathname.includes('/recruitment/analytics')) return 'analytics';
    return 'discovery';
  };

  const [activeTab, setActiveTab] = React.useState<string>(getInitialTab());
  const [searchQuery, setSearchQuery] = React.useState('');
  const [viewMode, setViewMode] = React.useState<'list' | 'grid' | 'table'>('list');
  const [selectedJob, setSelectedJob] = React.useState<JobListingItem | null>(null);
  const [selectedApplication, setSelectedApplication] = React.useState<ApplicationItem | null>(
    null
  );

  const [jobs, setJobs] = React.useState<JobListingItem[]>([]);
  const [applications, setApplications] = React.useState<ApplicationItem[]>([]);
  const [totalJobs, setTotalJobs] = React.useState(0);
  const [totalApplications, setTotalApplications] = React.useState(0);
  const [isLoading, setIsLoading] = React.useState(true);
  const [isRefreshing, setIsRefreshing] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    setActiveTab(getInitialTab());
  }, [location.pathname]);

  const loadData = React.useCallback(async () => {
    setError(null);
    try {
      const [jobsRes, appsRes] = await Promise.allSettled([
        apiClient.listJobs(),
        apiClient.listApplications(),
      ]);

      if (jobsRes.status === 'fulfilled') {
        setJobs(jobsRes.value.items);
        setTotalJobs(jobsRes.value.total);
      }
      if (appsRes.status === 'fulfilled') {
        setApplications(appsRes.value.items);
        setTotalApplications(appsRes.value.total);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to query recruitment records.');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  React.useEffect(() => {
    loadData();
  }, [loadData]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === 'discovery') navigate('/recruitment/discovery');
    else navigate(`/recruitment/${tabId}`);
  };

  const filteredJobs = jobs.filter((job) => {
    const matchesSearch =
      job.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (job.location && job.location.toLowerCase().includes(searchQuery.toLowerCase()));

    if (activeTab === 'submitted') return false;
    return matchesSearch;
  });

  const filteredApplications = applications.filter((app) => {
    const matchesSearch =
      (app.company && app.company.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (app.job_title && app.job_title.toLowerCase().includes(searchQuery.toLowerCase())) ||
      app.status.toLowerCase().includes(searchQuery.toLowerCase());

    if (activeTab === 'submitted') {
      return matchesSearch && app.status === 'submitted';
    }
    return matchesSearch;
  });

  const tabs = [
    { id: 'discovery', label: 'Discovered Jobs', badge: totalJobs },
    { id: 'recommended', label: 'Recommended', badge: 0 },
    { id: 'pipeline', label: '10-Stage Pipeline', badge: totalApplications },
    {
      id: 'submitted',
      label: 'Submitted',
      badge: applications.filter((a) => a.status === 'submitted').length,
    },
    { id: 'history', label: 'Attempts & History' },
    { id: 'analytics', label: 'Recruitment Funnel' },
  ];

  return (
    <ModulePage
      isDetailOpen={!!selectedJob || !!selectedApplication}
      detailPanel={
        selectedJob ? (
          <ModuleDetailPanel
            title={selectedJob.title}
            subtitle={selectedJob.company}
            onClose={() => setSelectedJob(null)}
            actions={
              <a
                href={selectedJob.application_url}
                target="_blank"
                rel="noreferrer"
                className={cn(
                  buttonVariants({ variant: 'outline', size: 'sm' }),
                  'h-8 gap-1.5 text-xs'
                )}
              >
                Visit Portal
                <ExternalLink className="h-3 w-3" />
              </a>
            }
          >
            <div className="space-y-5">
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline" className="text-xs font-mono">
                  {selectedJob.status.toUpperCase()}
                </Badge>
                {selectedJob.work_arrangement && (
                  <Badge variant="neutral" className="text-xs">
                    {selectedJob.work_arrangement}
                  </Badge>
                )}
                {selectedJob.employment_type && (
                  <Badge variant="neutral" className="text-xs">
                    {selectedJob.employment_type}
                  </Badge>
                )}
              </div>

              {selectedJob.salary_range && (
                <div className="rounded-lg border border-border/80 bg-background/60 p-3">
                  <span className="text-[11px] font-semibold text-muted-foreground uppercase">
                    Salary Compensation
                  </span>
                  <p className="mt-0.5 text-sm font-semibold text-emerald-400 font-mono">
                    {selectedJob.salary_range}
                  </p>
                </div>
              )}

              {selectedJob.location && (
                <div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Location
                  </span>
                  <p className="mt-1 text-xs text-foreground flex items-center gap-1.5">
                    <MapPin className="h-3.5 w-3.5 text-muted-foreground" />
                    {selectedJob.location}
                  </p>
                </div>
              )}

              {selectedJob.description && (
                <div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Description
                  </span>
                  <p className="mt-1 text-xs text-muted-foreground whitespace-pre-wrap leading-relaxed">
                    {selectedJob.description}
                  </p>
                </div>
              )}

              {selectedJob.requirements && (
                <div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Requirements
                  </span>
                  <p className="mt-1 text-xs text-muted-foreground whitespace-pre-wrap leading-relaxed">
                    {selectedJob.requirements}
                  </p>
                </div>
              )}

              <div className="border-t border-border/40 pt-3 text-[11px] text-muted-foreground font-mono">
                Discovered: {new Date(selectedJob.discovered_at).toLocaleString()}
              </div>
            </div>
          </ModuleDetailPanel>
        ) : selectedApplication ? (
          <ModuleDetailPanel
            title={selectedApplication.job_title || 'Application'}
            subtitle={selectedApplication.company || selectedApplication.id}
            onClose={() => setSelectedApplication(null)}
            actions={
              <Badge variant="neutral" className="text-xs">
                {selectedApplication.status.toUpperCase()}
              </Badge>
            }
          >
            <div className="space-y-5">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Status
                </span>
                <p className="mt-1 text-sm font-medium text-foreground">
                  {selectedApplication.status}
                </p>
              </div>

              {selectedApplication.notes && (
                <div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Notes
                  </span>
                  <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
                    {selectedApplication.notes}
                  </p>
                </div>
              )}

              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Submission Attempts ({selectedApplication.attempts?.length || 0})
                </span>
                {selectedApplication.attempts && selectedApplication.attempts.length > 0 ? (
                  <div className="mt-2 space-y-2">
                    {selectedApplication.attempts.map((att) => (
                      <div
                        key={att.id}
                        className="rounded-md border border-border/60 bg-muted/30 p-2.5 text-xs"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-foreground">
                            {att.execution_status}
                          </span>
                          <span className="text-[10px] text-muted-foreground font-mono">
                            {new Date(att.attempted_at).toLocaleTimeString()}
                          </span>
                        </div>
                        {att.error_summary && (
                          <p className="mt-1 text-[11px] text-status-error font-mono">
                            {att.error_summary}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="mt-1 text-xs text-muted-foreground">No attempts logged yet.</p>
                )}
              </div>
            </div>
          </ModuleDetailPanel>
        ) : null
      }
    >
      <ModuleHeader
        title="Jobs & Application Pipeline"
        description="Autonomous job discovery, resume matching, and human-authorized application management."
        icon={BriefcaseBusiness}
        stageTag="Stage 26 / 31 Planned"
        badgeLabel={`${totalJobs} Opportunities`}
        badgeVariant="outline"
        actions={
          <Button
            size="sm"
            onClick={() => {
              setIsRefreshing(true);
              loadData();
            }}
            className="text-xs gap-1.5"
          >
            <Clock className="h-3.5 w-3.5" />
            Sync Feeds
          </Button>
        }
      />

      <ModuleUnavailableState
        moduleName="Autonomous Job Discovery & Application Tailor"
        stageTag="Stage 26 & 31"
        stageName="Recruitment Automation Suite"
        description="Autonomous multi-source job harvesting (LinkedIn, Indeed, Greenhouse, Lever) goes live in Stage 26. Automated resume tailoring and form-filling submission scribe activate in Stage 31 under human safety authorization gates. Real SQLite storage and data contracts are active below."
        plannedCapabilities={[
          'Hourly multi-source ATS crawler and deduping (Stage 26)',
          'Candidate career match scoring & gap analysis (Stage 27)',
          'Evidence-grounded ATS resume generator (Stage 31)',
          'Deterministic idempotency submission attempts (Stage 32)',
        ]}
      />

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={handleTabChange} />

      <ModuleToolbar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        searchPlaceholder="Filter listings by company, title, or location..."
        onRefresh={() => {
          setIsRefreshing(true);
          loadData();
        }}
        isRefreshing={isRefreshing}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
      />

      {error ? (
        <ModuleErrorState
          title="Could not query recruitment records"
          message={error}
          onRetry={loadData}
          isRetrying={isRefreshing}
        />
      ) : isLoading ? (
        <ModuleLoadingState rows={5} layout="table" />
      ) : activeTab === 'submitted' ? (
        filteredApplications.length === 0 ? (
          <ModuleEmptyState
            title="No submitted applications yet"
            description="When authorized applications are submitted through the autonomous engine, verified receipts will appear here."
          />
        ) : (
          <div className="space-y-3">
            {filteredApplications.map((app) => (
              <Card
                key={app.id}
                className="cursor-pointer border border-border/60 bg-card/60 transition-all hover:border-primary/50"
                onClick={() => {
                  setSelectedJob(null);
                  setSelectedApplication(app);
                }}
              >
                <CardContent className="flex items-center justify-between p-4">
                  <div>
                    <h4 className="text-sm font-semibold text-foreground">
                      {app.job_title || 'Application'}
                    </h4>
                    <p className="text-xs text-muted-foreground">{app.company || app.id}</p>
                  </div>
                  <Badge variant="neutral" className="text-xs">
                    {app.status}
                  </Badge>
                </CardContent>
              </Card>
            ))}
          </div>
        )
      ) : filteredJobs.length === 0 ? (
        <ModuleEmptyState
          title="No job listings found in database"
          description="Autonomous discovery will populate listings in Stage 26. Currently there are zero synthetic listings per Zero-Fake-Data rules."
        />
      ) : (
        <div className="space-y-3">
          {filteredJobs.map((job) => (
            <Card
              key={job.id}
              className={`cursor-pointer border border-border/60 bg-card/60 transition-all hover:border-primary/50 hover:bg-card/90 ${
                selectedJob?.id === job.id ? 'ring-2 ring-primary border-primary' : ''
              }`}
              onClick={() => {
                setSelectedApplication(null);
                setSelectedJob(job);
              }}
            >
              <CardContent className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-semibold text-foreground hover:text-primary transition-colors">
                      {job.title}
                    </h3>
                    <Badge variant="outline" className="text-[10px]">
                      {job.status}
                    </Badge>
                  </div>
                  <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1 font-medium text-foreground/90">
                      <Building2 className="h-3.5 w-3.5 text-muted-foreground" />
                      {job.company}
                    </span>
                    {job.location && (
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5 text-muted-foreground" />
                        {job.location}
                      </span>
                    )}
                    {job.salary_range && (
                      <span className="flex items-center gap-1 text-emerald-400 font-mono">
                        <DollarSign className="h-3.5 w-3.5" />
                        {job.salary_range}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2.5 self-end sm:self-center">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 gap-1.5 text-xs text-muted-foreground hover:text-foreground"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedJob(job);
                    }}
                  >
                    <Eye className="h-3.5 w-3.5" />
                    Details
                  </Button>
                  <a
                    href={job.application_url}
                    target="_blank"
                    rel="noreferrer"
                    className={cn(
                      buttonVariants({ variant: 'outline', size: 'sm' }),
                      'h-8 gap-1.5 text-xs'
                    )}
                    onClick={(e) => e.stopPropagation()}
                  >
                    Open <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </ModulePage>
  );
};

export default RecruitmentWorkspace;
