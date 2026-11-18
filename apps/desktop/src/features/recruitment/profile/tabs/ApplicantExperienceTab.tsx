/**
 * Stage 21: Applicant Work Experience & Employment History Tab.
 * Roles, verified quantifiable achievements, metrics, and technology stacks.
 */

import * as React from 'react';
import { Briefcase, Plus, Trash2, Calendar, MapPin, Sparkles, Code2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import type { EmploymentRecord, AchievementItem } from '@autonom/shared-types';

interface ApplicantExperienceTabProps {
  experienceList: EmploymentRecord[];
  onAdd: (exp: Partial<EmploymentRecord>) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  isProcessing: boolean;
}

export const ApplicantExperienceTab: React.FC<ApplicantExperienceTabProps> = ({
  experienceList,
  onAdd,
  onDelete,
  isProcessing,
}) => {
  const [isAdding, setIsAdding] = React.useState(false);
  const [employer, setEmployer] = React.useState('');
  const [jobTitle, setJobTitle] = React.useState('');
  const [employmentType, setEmploymentType] = React.useState('Full-time');
  const [location, setLocation] = React.useState('');
  const [isRemote, setIsRemote] = React.useState(false);
  const [startDate, setStartDate] = React.useState('');
  const [endDate, setEndDate] = React.useState('');
  const [isCurrent, setIsCurrent] = React.useState(false);
  const [summary, setSummary] = React.useState('');
  const [technologiesText, setTechnologiesText] = React.useState('');
  const [achievementsText, setAchievementsText] = React.useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!employer || !jobTitle) return;

    const technologies = technologiesText
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean);

    const achievements: AchievementItem[] = achievementsText
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
      .map((desc, idx) => ({
        id: `ach_${Date.now()}_${idx}`,
        description: desc,
      }));

    await onAdd({
      employer,
      job_title: jobTitle,
      employment_type: employmentType,
      location: location || undefined,
      is_remote: isRemote,
      start_date: startDate || undefined,
      end_date: isCurrent ? undefined : endDate || undefined,
      is_current: isCurrent,
      summary: summary || undefined,
      technologies_used: technologies,
      achievements,
    });

    setEmployer('');
    setJobTitle('');
    setEmploymentType('Full-time');
    setLocation('');
    setIsRemote(false);
    setStartDate('');
    setEndDate('');
    setIsCurrent(false);
    setSummary('');
    setTechnologiesText('');
    setAchievementsText('');
    setIsAdding(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">Work History & Professional Experience</h3>
          <p className="text-sm text-muted-foreground">
            Authoritative career timeline. Downstream Resume and Tailoring agents pull bullet points and metrics from here.
          </p>
        </div>
        {!isAdding && (
          <Button onClick={() => setIsAdding(true)} size="sm">
            <Plus className="mr-2 h-4 w-4" />
            Add Position
          </Button>
        )}
      </div>

      {/* Add Position Form */}
      {isAdding && (
        <Card className="border-primary/50">
          <CardHeader>
            <CardTitle className="text-base font-semibold">Add Work Experience</CardTitle>
            <CardDescription>Enter verified employer, title, dates, and achievements.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Employer / Company Name *
                  </label>
                  <Input
                    required
                    value={employer}
                    onChange={(e) => setEmployer(e.target.value)}
                    placeholder="e.g. Acme Cloud Corp"
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Job Title *
                  </label>
                  <Input
                    required
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    placeholder="e.g. Senior Software Engineer"
                    className="mt-1"
                  />
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Employment Type
                  </label>
                  <Input
                    value={employmentType}
                    onChange={(e) => setEmploymentType(e.target.value)}
                    placeholder="Full-time, Contract, Internship"
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Location
                  </label>
                  <Input
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g. Seattle, WA"
                    className="mt-1"
                  />
                </div>
                <div className="flex items-center pt-6">
                  <label className="flex items-center gap-2 text-sm font-medium cursor-pointer">
                    <input
                      type="checkbox"
                      checked={isRemote}
                      onChange={(e) => setIsRemote(e.target.checked)}
                      className="rounded border-gray-300"
                    />
                    Remote Position
                  </label>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Start Date
                  </label>
                  <Input
                    type="month"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    End Date
                  </label>
                  <Input
                    type="month"
                    disabled={isCurrent}
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="mt-1"
                  />
                  <label className="flex items-center gap-2 mt-2 text-xs text-muted-foreground cursor-pointer">
                    <input
                      type="checkbox"
                      checked={isCurrent}
                      onChange={(e) => setIsCurrent(e.target.checked)}
                      className="rounded border-gray-300"
                    />
                    Currently Working in Role
                  </label>
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Role Summary
                </label>
                <textarea
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  placeholder="Overview of scope, team, and mandate..."
                  rows={2}
                  className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                />
              </div>

              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Key Achievements & Quantifiable Impact (One per line)
                </label>
                <textarea
                  value={achievementsText}
                  onChange={(e) => setAchievementsText(e.target.value)}
                  placeholder="• Reduced API p99 latency from 450ms to 85ms across 12 distributed services&#10;• Designed high-throughput pipeline handling 14M events/day with 99.99% uptime"
                  rows={3}
                  className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                />
              </div>

              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Technologies Used (Comma separated)
                </label>
                <Input
                  value={technologiesText}
                  onChange={(e) => setTechnologiesText(e.target.value)}
                  placeholder="e.g. Python, FastAPI, Docker, Kubernetes, PostgreSQL, Kafka"
                  className="mt-1"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="ghost" onClick={() => setIsAdding(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isProcessing}>
                  {isProcessing ? 'Saving...' : 'Add Position'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* List of Experience Records */}
      {experienceList.length === 0 ? (
        <Card className="flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
          <Briefcase className="mb-2 h-10 w-10 text-muted-foreground" />
          <p className="font-medium text-foreground">No Work History Listed</p>
          <p className="text-xs text-muted-foreground mt-1 max-w-sm">
            Add full-time, contract, or startup roles with verifiable achievements and technologies.
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {experienceList.map((exp) => (
            <Card key={exp.id} className="relative overflow-hidden">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <h4 className="text-base font-semibold">{exp.job_title}</h4>
                      <span className="text-muted-foreground">at</span>
                      <span className="font-semibold text-foreground">{exp.employer}</span>
                      {exp.claim_id && (
                        <Badge variant="outline" className="border-emerald-500/50 text-emerald-600 text-[10px]">
                          Claim Verified
                        </Badge>
                      )}
                    </div>

                    <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground pt-1">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3.5 w-3.5" />
                        <span>
                          {exp.start_date || 'N/A'} — {exp.is_current ? 'Present' : exp.end_date || 'N/A'}
                        </span>
                      </div>
                      {exp.location && (
                        <div className="flex items-center gap-1">
                          <MapPin className="h-3.5 w-3.5" />
                          <span>{exp.location} {exp.is_remote ? '(Remote)' : ''}</span>
                        </div>
                      )}
                      {exp.employment_type && (
                        <Badge variant="neutral" className="text-[10px] font-normal">
                          {exp.employment_type}
                        </Badge>
                      )}
                    </div>
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete(exp.id)}
                    disabled={isProcessing}
                    className="text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>

                {exp.summary && (
                  <p className="mt-3 text-sm text-muted-foreground">{exp.summary}</p>
                )}

                {exp.achievements && exp.achievements.length > 0 && (
                  <div className="mt-3 space-y-1.5">
                    <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                      <Sparkles className="h-3.5 w-3.5 text-primary" /> Key Contributions & Metrics:
                    </div>
                    <ul className="list-inside list-disc space-y-1 text-sm text-foreground/90 pl-1">
                      {exp.achievements.map((ach) => (
                        <li key={ach.id} className="text-xs">
                          {ach.description}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {exp.technologies_used && exp.technologies_used.length > 0 && (
                  <div className="mt-4 flex flex-wrap gap-1.5 pt-3 border-t">
                    <span className="text-xs text-muted-foreground flex items-center mr-1">
                      <Code2 className="h-3 w-3 mr-1 text-primary" /> Stack:
                    </span>
                    {exp.technologies_used.map((tech, i) => (
                      <Badge key={i} variant="outline" className="text-xs font-mono">
                        {tech}
                      </Badge>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
