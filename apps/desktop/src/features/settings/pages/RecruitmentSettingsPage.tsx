import React, { useState } from 'react';
import type { RecruitmentSettings } from '@autonom/shared-types';
import { Plus, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  SettingsSection,
  SettingsField,
  SettingsToggle,
  SettingsUnavailableState,
  SettingsSaveBar,
} from '../components';

interface RecruitmentSettingsPageProps {
  settings: RecruitmentSettings;
  isDirty: boolean;
  isSaving: boolean;
  saveSuccess?: boolean;
  errorMessage?: string | null;
  onChange: (updated: Partial<RecruitmentSettings>) => void;
  onSave: () => void;
  onReset: () => void;
}

export const RecruitmentSettingsPage: React.FC<RecruitmentSettingsPageProps> = ({
  settings,
  isDirty,
  isSaving,
  saveSuccess,
  errorMessage,
  onChange,
  onSave,
  onReset,
}) => {
  const [newTitle, setNewTitle] = useState('');
  const [newCompany, setNewCompany] = useState('');

  const handleAddTitle = () => {
    if (!newTitle.trim()) return;
    if (!settings.desired_job_titles.includes(newTitle.trim())) {
      onChange({ desired_job_titles: [...settings.desired_job_titles, newTitle.trim()] });
    }
    setNewTitle('');
  };

  const handleRemoveTitle = (title: string) => {
    onChange({ desired_job_titles: settings.desired_job_titles.filter((t) => t !== title) });
  };

  const handleAddExcludedCompany = () => {
    if (!newCompany.trim()) return;
    if (!settings.excluded_companies.includes(newCompany.trim())) {
      onChange({ excluded_companies: [...settings.excluded_companies, newCompany.trim()] });
    }
    setNewCompany('');
  };

  const handleRemoveExcludedCompany = (comp: string) => {
    onChange({ excluded_companies: settings.excluded_companies.filter((c) => c !== comp) });
  };

  return (
    <div className="space-y-6">
      <SettingsUnavailableState
        title="Autonomous Recruitment Scout & Submission Pipeline"
        roadmapStage="Stage 25 / Stage 26 / Stage 31"
        description="Stage 10 establishes the career preference models, ATS matching thresholds, and human review boundaries. Automated job application submission and intelligent resume tailoring activate in Stages 25 through 35."
        configurationNotes="Zero-Fake-Data compliance: Real user preferences are saved and used by Stage 09 Recruitment workspace."
      />

      <SettingsSection
        title="Target Job Profiles & Search Criteria"
        description="Specify job titles, seniority levels, and geographic locations to scout."
      >
        <SettingsField
          label="Desired Job Titles"
          description="Primary target titles matched against scraped job postings."
          vertical
        >
          <div className="w-full space-y-2">
            <div className="flex flex-wrap gap-1.5">
              {settings.desired_job_titles.map((title) => (
                <span
                  key={title}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-primary/10 border border-primary/30 text-xs text-primary font-medium"
                >
                  {title}
                  <button
                    type="button"
                    onClick={() => handleRemoveTitle(title)}
                    className="hover:text-rose-400"
                    aria-label={`Remove ${title}`}
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>

            <div className="flex items-center gap-2 max-w-sm pt-1">
              <input
                type="text"
                placeholder="Add job title (e.g. Senior Backend Engineer)"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTitle())}
                className="h-8 flex-1 rounded-md border border-input bg-card px-2.5 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={handleAddTitle}
                className="h-8 text-xs px-2.5"
              >
                <Plus className="h-3.5 w-3.5 mr-1" />
                Add
              </Button>
            </div>
          </div>
        </SettingsField>

        <SettingsField
          label="Minimum ATS Match Score Threshold"
          description="Minimum semantic relevance score required before queuing a job for application preparation."
        >
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={50}
              max={100}
              step={5}
              value={settings.minimum_match_threshold}
              onChange={(e) =>
                onChange({ minimum_match_threshold: parseInt(e.target.value, 10) || 75 })
              }
              className="h-8 w-20 rounded-md border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
              aria-label="Minimum ATS Match Score"
            />
            <span className="text-xs text-muted-foreground font-mono">% match</span>
          </div>
        </SettingsField>

        <SettingsField
          label="Resume Tailoring Depth"
          description="How aggressively tailored documents align with detected job keywords and ATS phrasing."
        >
          <select
            value={settings.resume_tailoring_mode}
            onChange={(e) =>
              onChange({
                resume_tailoring_mode: e.target
                  .value as RecruitmentSettings['resume_tailoring_mode'],
              })
            }
            className="h-8 rounded-md border border-input bg-card px-2.5 py-1 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            aria-label="Resume Tailoring Depth"
          >
            <option value="subtle">Subtle (Reorder bullets, keep standard wording)</option>
            <option value="focused">
              Focused (Highlight matching technologies & achievements)
            </option>
            <option value="comprehensive">
              Comprehensive (Tailor full summary, skills, and projects)
            </option>
          </select>
        </SettingsField>
      </SettingsSection>

      <SettingsSection
        title="Application Velocity & Submission Governance"
        description="Strict application quotas and human sign-off rules."
      >
        <SettingsField
          label="Require Human Approval for Every Submission"
          description="Mandatory sign-off gate (Tier 2 Supervised). Previews completed form and answers before submitting."
        >
          <SettingsToggle
            checked={settings.require_human_approval_for_submission}
            onCheckedChange={(checked) =>
              onChange({ require_human_approval_for_submission: checked })
            }
            ariaLabel="Require Approval for Submissions"
          />
        </SettingsField>

        <SettingsField
          label="Maximum Daily Applications Ceiling"
          description="Daily safety limit to avoid spamming job boards or triggering anti-bot protections."
        >
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={1}
              max={25}
              value={settings.max_daily_applications}
              onChange={(e) =>
                onChange({ max_daily_applications: parseInt(e.target.value, 10) || 5 })
              }
              className="h-8 w-20 rounded-md border border-input bg-card px-2 text-xs font-mono text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
              aria-label="Max Daily Applications"
            />
            <span className="text-xs text-muted-foreground font-mono">apps / day</span>
          </div>
        </SettingsField>

        <SettingsField
          label="Duplicate Application Prevention"
          description="Strictly prevent submitting applications to the same employer and title within a 90-day window."
        >
          <SettingsToggle
            checked={settings.prevent_duplicate_applications}
            onCheckedChange={(checked) => onChange({ prevent_duplicate_applications: checked })}
            ariaLabel="Duplicate Prevention"
          />
        </SettingsField>

        <SettingsField
          label="Fully Autonomous Submission Authorization"
          description="Authorize agent to submit directly without human review (Stage 31). Disabled by default."
        >
          <SettingsToggle
            checked={settings.auto_submission_authorized}
            onCheckedChange={(checked) => onChange({ auto_submission_authorized: checked })}
            disabled={true}
            activeLabel="Authorized"
            inactiveLabel="Unauthorized (Planned S31)"
            ariaLabel="Auto Submission Authorization"
          />
        </SettingsField>
      </SettingsSection>

      <SettingsSection
        title="Excluded Companies & Employers"
        description="Filter out specific employers (e.g. current company or agencies)."
      >
        <div className="space-y-2">
          <div className="flex flex-wrap gap-1.5">
            {settings.excluded_companies.length === 0 ? (
              <span className="text-xs text-muted-foreground italic">
                No companies currently excluded.
              </span>
            ) : (
              settings.excluded_companies.map((comp) => (
                <span
                  key={comp}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300 font-medium"
                >
                  {comp}
                  <button
                    type="button"
                    onClick={() => handleRemoveExcludedCompany(comp)}
                    className="hover:text-rose-100"
                    aria-label={`Remove ${comp}`}
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              ))
            )}
          </div>

          <div className="flex items-center gap-2 max-w-sm pt-2">
            <input
              type="text"
              placeholder="Add company name to exclude"
              value={newCompany}
              onChange={(e) => setNewCompany(e.target.value)}
              onKeyDown={(e) =>
                e.key === 'Enter' && (e.preventDefault(), handleAddExcludedCompany())
              }
              className="h-8 flex-1 rounded-md border border-input bg-card px-2.5 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            />
            <Button
              variant="outline"
              size="sm"
              onClick={handleAddExcludedCompany}
              className="h-8 text-xs px-2.5"
            >
              <Plus className="h-3.5 w-3.5 mr-1" />
              Exclude
            </Button>
          </div>
        </div>
      </SettingsSection>

      <SettingsSaveBar
        isDirty={isDirty}
        isSaving={isSaving}
        saveSuccess={saveSuccess}
        errorMessage={errorMessage}
        onSave={onSave}
        onReset={onReset}
      />
    </div>
  );
};
