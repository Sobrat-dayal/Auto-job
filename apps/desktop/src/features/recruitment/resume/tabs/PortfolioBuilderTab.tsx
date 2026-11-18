/**
 * Stage 23: Developer Portfolio Builder & Showcase Tab.
 * Curates project evidence, architecture highlights, and individual contribution descriptions.
 * Enforces privacy scrubbing of private GitHub repository links and exports multi-page PDF & standalone HTML.
 */

import * as React from 'react';
import {
  Briefcase,
  Plus,
  Globe,
  Shield,
  ShieldCheck,
  CheckCircle2,
  Trash2,
  Download,
  FolderGit2,
  RefreshCw,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { apiClient } from '@/lib/api-client';
import type {
  PortfolioDocument,
  PortfolioProjectEntry,
  PortfolioCreateRequest,
} from '@autonom/shared-types';

interface PortfolioBuilderTabProps {
  onNavigateTab?: (tabId: string) => void;
}

export const PortfolioBuilderTab: React.FC<PortfolioBuilderTabProps> = ({
  onNavigateTab,
}) => {
  const [portfolios, setPortfolios] = React.useState<PortfolioDocument[]>([]);
  const [selectedPortfolio, setSelectedPortfolio] = React.useState<PortfolioDocument | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [isExporting, setIsExporting] = React.useState<boolean>(false);
  const [isSaving, setIsSaving] = React.useState<boolean>(false);
  const [statusMessage, setStatusMessage] = React.useState<string | null>(null);

  // Form states for active portfolio
  const [title, setTitle] = React.useState<string>('');
  const [intro, setIntro] = React.useState<string>('');
  const [skills, setSkills] = React.useState<string>('');
  const [projects, setProjects] = React.useState<PortfolioProjectEntry[]>([]);

  const fetchPortfolios = React.useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.listPortfolios();
      setPortfolios(data);
      if (data.length > 0 && !selectedPortfolio) {
        setSelectedPortfolio(data[0]);
        loadPortfolioForm(data[0]);
      } else if (selectedPortfolio) {
        const found = data.find((p) => p.id === selectedPortfolio.id);
        if (found) {
          setSelectedPortfolio(found);
          loadPortfolioForm(found);
        }
      }
    } catch (err: any) {
      console.error('Failed to fetch portfolios', err);
    } finally {
      setIsLoading(false);
    }
  }, [selectedPortfolio]);

  React.useEffect(() => {
    fetchPortfolios();
  }, []);

  const loadPortfolioForm = (portfolio: PortfolioDocument) => {
    setTitle(portfolio.title || '');
    setIntro(portfolio.professional_intro || '');
    setSkills(portfolio.selected_skills.join(', '));
    setProjects(portfolio.selected_projects || []);
  };

  const handleSelectPortfolio = (p: PortfolioDocument) => {
    setSelectedPortfolio(p);
    loadPortfolioForm(p);
    setStatusMessage(null);
  };

  const handleCreateNew = async () => {
    setIsLoading(true);
    try {
      const req: PortfolioCreateRequest = {
        title: 'Software Engineer Portfolio',
        professional_intro:
          'Full-stack and distributed systems engineer with strong experience in Python, TypeScript, and modern cloud architecture.',
      };
      const created = await apiClient.createPortfolio(req);
      await fetchPortfolios();
      setSelectedPortfolio(created);
      loadPortfolioForm(created);
      setStatusMessage('Created new portfolio successfully.');
    } catch (err: any) {
      setStatusMessage(`Error creating portfolio: ${err?.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSavePortfolio = async () => {
    if (!selectedPortfolio) return;
    setIsSaving(true);
    setStatusMessage(null);
    try {
      const updated = await apiClient.updatePortfolio(selectedPortfolio.id, {
        title,
        professional_intro: intro,
        selected_skills: skills
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean),
        selected_projects: projects,
      });
      setSelectedPortfolio(updated);
      setStatusMessage('Portfolio changes saved.');
      await fetchPortfolios();
    } catch (err: any) {
      setStatusMessage(`Save failed: ${err?.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleScrubPrivateUrls = () => {
    const scrubbed = projects.map((p) => {
      if (!p.is_public_eligible && p.repo_url) {
        return { ...p, repo_url: null };
      }
      return p;
    });
    setProjects(scrubbed);
    setStatusMessage('Private repository links scrubbed for external privacy.');
  };

  const handleExportPdf = async () => {
    if (!selectedPortfolio) return;
    setIsExporting(true);
    setStatusMessage(null);
    try {
      const res = await apiClient.exportPortfolioPdf(selectedPortfolio.id);
      setStatusMessage(`Exported PDF successfully to ${res.file_path}`);
    } catch (err: any) {
      setStatusMessage(`PDF export error: ${err?.message}`);
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportHtml = async () => {
    if (!selectedPortfolio) return;
    setIsExporting(true);
    setStatusMessage(null);
    try {
      const res = await apiClient.exportPortfolioHtml(selectedPortfolio.id);
      setStatusMessage(`Exported standalone HTML successfully to ${res.file_path}`);
    } catch (err: any) {
      setStatusMessage(`HTML export error: ${err?.message}`);
    } finally {
      setIsExporting(false);
    }
  };

  const addProjectEntry = () => {
    const newProj: PortfolioProjectEntry = {
      project_id: `proj_${Date.now()}`,
      title: 'New Highlight Project',
      summary: 'High-impact distributed system or application with verified architecture.',
      problem_addressed: 'Addressed latency and throughput bottlenecks in high-frequency data pipelines.',
      individual_contribution: 'Designed primary microservice APIs and automated integration testing pipelines.',
      tech_stack: ['Python', 'FastAPI', 'PostgreSQL', 'Docker'],
      architecture_highlights: ['Async event loop with Redis cache layer', 'Zero-downtime blue/green deployment strategy'],
      deliverables: ['Production REST API', 'Interactive documentation portal'],
      repo_url: 'https://github.com/applicant/sample-repo',
      is_public_eligible: true,
      attribution_level: 'author',
      ordering: projects.length,
    };
    setProjects([...projects, newProj]);
  };

  const removeProject = (index: number) => {
    const next = [...projects];
    next.splice(index, 1);
    setProjects(next);
  };

  const updateProject = (index: number, updates: Partial<PortfolioProjectEntry>) => {
    const next = [...projects];
    next[index] = { ...next[index], ...updates };
    setProjects(next);
  };

  return (
    <div className="space-y-6">
      {/* Portfolio Selector Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-md">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Briefcase className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-100">Professional Portfolios</h2>
            <p className="text-xs text-slate-400">
              Evidence-grounded project deliverables, architecture deep-dives, and verified GitHub contributions.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {portfolios.length > 0 && (
            <select
              className="h-8 text-xs bg-slate-950 border border-slate-800 rounded px-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
              value={selectedPortfolio?.id || ''}
              onChange={(e) => {
                const p = portfolios.find((item) => item.id === e.target.value);
                if (p) handleSelectPortfolio(p);
              }}
            >
              {portfolios.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title} ({p.selected_projects.length} projects)
                </option>
              ))}
            </select>
          )}
          <Button
            size="sm"
            onClick={handleCreateNew}
            disabled={isLoading}
            className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs"
          >
            <Plus className="w-3.5 h-3.5 mr-1" />
            New Portfolio
          </Button>
        </div>
      </div>

      {statusMessage && (
        <div className="p-3 rounded-md bg-indigo-950/40 border border-indigo-800/60 flex items-center justify-between text-indigo-300 text-xs">
          <span>{statusMessage}</span>
          <button onClick={() => setStatusMessage(null)} className="text-indigo-400 hover:text-indigo-200">
            &times;
          </button>
        </div>
      )}

      {selectedPortfolio ? (
        <div className="space-y-6">
          {/* Main Metadata Card */}
          <Card className="bg-slate-900/80 border-slate-800 shadow-md">
            <CardHeader className="pb-3 border-b border-slate-800/80 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-base font-semibold text-slate-100">
                  Portfolio Details & Narrative
                </CardTitle>
                <p className="text-xs text-slate-400 mt-0.5">
                  General headline, professional summary, and key skill highlights.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleSavePortfolio}
                  disabled={isSaving}
                  className="border-emerald-700 bg-emerald-950/40 text-emerald-300 hover:bg-emerald-900/50 text-xs"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
                  Save Changes
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-300">Portfolio Title</label>
                  <Input
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="e.g. Senior Backend & Systems Portfolio"
                    className="bg-slate-950 border-slate-800 text-xs"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-300">Highlighted Skills (comma separated)</label>
                  <Input
                    value={skills}
                    onChange={(e) => setSkills(e.target.value)}
                    placeholder="e.g. Python, Rust, PostgreSQL, Kubernetes, React"
                    className="bg-slate-950 border-slate-800 text-xs"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-300">Professional Summary Intro</label>
                <Textarea
                  value={intro}
                  onChange={(e) => setIntro(e.target.value)}
                  rows={3}
                  placeholder="Summarize your technical leadership, engineering focus, and key accomplishments..."
                  className="bg-slate-950 border-slate-800 text-xs leading-relaxed"
                />
              </div>
            </CardContent>
          </Card>

          {/* Privacy & Intellectual Property Review Box */}
          <Card className="bg-slate-900/80 border-slate-800 shadow-md">
            <CardHeader className="pb-3 border-b border-slate-800/80 flex flex-row items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <div>
                  <CardTitle className="text-sm font-semibold text-slate-100">
                    Privacy Review & Intellectual Property Safeguards
                  </CardTitle>
                  <p className="text-xs text-slate-400">
                    Zero-leakage policy: Ensure proprietary or private repository URLs are scrubbed before publishing.
                  </p>
                </div>
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={handleScrubPrivateUrls}
                className="border-slate-700 text-slate-300 text-xs hover:bg-slate-800"
              >
                <Shield className="w-3.5 h-3.5 mr-1 text-amber-400" />
                Scrub Private URLs
              </Button>
            </CardHeader>
            <CardContent className="pt-3 text-xs text-slate-400 leading-relaxed">
              When sharing portfolios externally, proprietary client repositories and non-public URLs
              should never be exposed. Projects marked as non-public will maintain their architectural
              descriptions while stripping direct source code URLs.
            </CardContent>
          </Card>

          {/* Project Deliverables List */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                  <FolderGit2 className="w-4 h-4 text-cyan-400" />
                  Showcased Projects ({projects.length})
                </h3>
                <p className="text-xs text-slate-400">
                  Detailed technical case studies with problem descriptions, solutions, and role attribution.
                </p>
              </div>
              <Button
                size="sm"
                onClick={addProjectEntry}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs"
              >
                <Plus className="w-3.5 h-3.5 mr-1 text-cyan-400" />
                Add Project
              </Button>
            </div>

            {projects.map((proj, idx) => (
              <Card key={proj.project_id || idx} className="bg-slate-900/80 border-slate-800 shadow-md">
                <CardContent className="pt-4 space-y-4">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-400 flex items-center justify-center text-[10px] font-mono">
                        {idx + 1}
                      </span>
                      <Input
                        value={proj.title}
                        onChange={(e) => updateProject(idx, { title: e.target.value })}
                        className="bg-slate-950 border-slate-800 text-xs font-semibold text-slate-200 h-8 max-w-sm"
                        placeholder="Project Title"
                      />
                    </div>
                    <div className="flex items-center gap-2">
                      <label className="flex items-center gap-1.5 text-xs text-slate-400 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={proj.is_public_eligible}
                          onChange={(e) => updateProject(idx, { is_public_eligible: e.target.checked })}
                          className="rounded border-slate-700 bg-slate-950 text-indigo-600 focus:ring-0"
                        />
                        <span>Public Eligible</span>
                      </label>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => removeProject(idx)}
                        className="h-8 w-8 p-0 text-slate-500 hover:text-rose-400"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-slate-300">Project Summary</label>
                      <Textarea
                        value={proj.summary}
                        onChange={(e) => updateProject(idx, { summary: e.target.value })}
                        rows={2}
                        className="bg-slate-950 border-slate-800 text-xs"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-slate-300">Individual Contribution</label>
                      <Textarea
                        value={proj.individual_contribution}
                        onChange={(e) => updateProject(idx, { individual_contribution: e.target.value })}
                        rows={2}
                        className="bg-slate-950 border-slate-800 text-xs"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-slate-300">Repository URL</label>
                      <Input
                        value={proj.repo_url || ''}
                        onChange={(e) => updateProject(idx, { repo_url: e.target.value || null })}
                        placeholder="https://github.com/user/repo"
                        className="bg-slate-950 border-slate-800 text-xs font-mono"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-xs font-medium text-slate-300">Technologies (comma separated)</label>
                      <Input
                        value={proj.tech_stack.join(', ')}
                        onChange={(e) =>
                          updateProject(idx, {
                            tech_stack: e.target.value.split(',').map((s) => s.trim()).filter(Boolean),
                          })
                        }
                        className="bg-slate-950 border-slate-800 text-xs"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Export Actions Bar */}
          <Card className="bg-slate-900/80 border-slate-800 shadow-md">
            <CardHeader className="pb-3 border-b border-slate-800/80">
              <CardTitle className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                <Download className="w-4 h-4 text-indigo-400" />
                Portfolio Export Formats
              </CardTitle>
              <p className="text-xs text-slate-400">
                Compile standalone static HTML or formatted multi-page PDF documents.
              </p>
            </CardHeader>
            <CardContent className="pt-4 flex flex-wrap gap-4">
              <Button
                onClick={handleExportPdf}
                disabled={isExporting}
                className="bg-rose-600 hover:bg-rose-500 text-white text-xs font-medium"
              >
                {isExporting ? <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <Download className="w-3.5 h-3.5 mr-1.5" />}
                Export Multi-Page PDF
              </Button>
              <Button
                onClick={handleExportHtml}
                disabled={isExporting}
                className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium"
              >
                {isExporting ? <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <Globe className="w-3.5 h-3.5 mr-1.5" />}
                Export Standalone HTML
              </Button>
            </CardContent>
          </Card>
        </div>
      ) : (
        <Card className="bg-slate-900/60 border-slate-800 text-center py-16">
          <CardContent className="space-y-3">
            <Briefcase className="w-12 h-12 text-slate-600 mx-auto" />
            <h3 className="text-base font-semibold text-slate-300">No Portfolios Found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Create a portfolio to showcase verified GitHub project evidence, architecture case studies, and engineering deliverables.
            </p>
            <div className="flex justify-center gap-2">
              <Button size="sm" onClick={handleCreateNew} className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs">
                <Plus className="w-3.5 h-3.5 mr-1" />
                Create First Portfolio
              </Button>
              {onNavigateTab && (
                <Button size="sm" variant="outline" onClick={() => onNavigateTab('my_resumes')} className="border-slate-700 text-slate-300 text-xs">
                  Back to Resumes
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
