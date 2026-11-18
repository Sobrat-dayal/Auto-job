/**
 * Stage 21: Applicant Education Credentials Tab.
 * Formal academic background, degree records, dates, GPA, and academic honors.
 */

import * as React from 'react';
import { GraduationCap, Plus, Trash2, Award, Calendar, Building2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import type { EducationRecord } from '@autonom/shared-types';

interface ApplicantEducationTabProps {
  educationList: EducationRecord[];
  onAdd: (edu: Partial<EducationRecord>) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  isProcessing: boolean;
}

export const ApplicantEducationTab: React.FC<ApplicantEducationTabProps> = ({
  educationList,
  onAdd,
  onDelete,
  isProcessing,
}) => {
  const [isAdding, setIsAdding] = React.useState(false);
  const [institution, setInstitution] = React.useState('');
  const [degree, setDegree] = React.useState('');
  const [fieldOfStudy, setFieldOfStudy] = React.useState('');
  const [startDate, setStartDate] = React.useState('');
  const [endDate, setEndDate] = React.useState('');
  const [isCurrent, setIsCurrent] = React.useState(false);
  const [gpa, setGpa] = React.useState('');
  const [honorsText, setHonorsText] = React.useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!institution || !degree || !fieldOfStudy) return;

    const honors = honorsText
      .split(',')
      .map((h) => h.trim())
      .filter(Boolean);

    await onAdd({
      institution,
      degree,
      field_of_study: fieldOfStudy,
      start_date: startDate || undefined,
      end_date: isCurrent ? undefined : endDate || undefined,
      is_current: isCurrent,
      gpa: gpa || undefined,
      honors,
    });

    setInstitution('');
    setDegree('');
    setFieldOfStudy('');
    setStartDate('');
    setEndDate('');
    setIsCurrent(false);
    setGpa('');
    setHonorsText('');
    setIsAdding(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">Academic Education & Degrees</h3>
          <p className="text-sm text-muted-foreground">
            Verified academic credentials. Each record establishes an authoritative provenance claim.
          </p>
        </div>
        {!isAdding && (
          <Button onClick={() => setIsAdding(true)} size="sm">
            <Plus className="mr-2 h-4 w-4" />
            Add Degree
          </Button>
        )}
      </div>

      {/* Add Education Form */}
      {isAdding && (
        <Card className="border-primary/50">
          <CardHeader>
            <CardTitle className="text-base font-semibold">Add Education Record</CardTitle>
            <CardDescription>Enter details of the degree or academic certificate.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Institution / University *
                  </label>
                  <Input
                    required
                    value={institution}
                    onChange={(e) => setInstitution(e.target.value)}
                    placeholder="e.g. Stanford University"
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Degree Level *
                  </label>
                  <Input
                    required
                    value={degree}
                    onChange={(e) => setDegree(e.target.value)}
                    placeholder="e.g. Bachelor of Science, Master of Science"
                    className="mt-1"
                  />
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Field of Study / Major *
                  </label>
                  <Input
                    required
                    value={fieldOfStudy}
                    onChange={(e) => setFieldOfStudy(e.target.value)}
                    placeholder="e.g. Computer Science, Electrical Engineering"
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    GPA (Optional)
                  </label>
                  <Input
                    value={gpa}
                    onChange={(e) => setGpa(e.target.value)}
                    placeholder="e.g. 3.9 / 4.0"
                    className="mt-1"
                  />
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
                    End Date / Expected Graduation
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
                    Currently Enrolled
                  </label>
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Honors / Awards (Comma separated)
                </label>
                <Input
                  value={honorsText}
                  onChange={(e) => setHonorsText(e.target.value)}
                  placeholder="e.g. Summa Cum Laude, Dean's Honor Roll, Tau Beta Pi"
                  className="mt-1"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="ghost" onClick={() => setIsAdding(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isProcessing}>
                  {isProcessing ? 'Saving...' : 'Add Degree'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* List of Education Records */}
      {educationList.length === 0 ? (
        <Card className="flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
          <GraduationCap className="mb-2 h-10 w-10 text-muted-foreground" />
          <p className="font-medium text-foreground">No Education Records Listed</p>
          <p className="text-xs text-muted-foreground mt-1 max-w-sm">
            Add undergraduate, graduate, or vocational degree credentials to support autonomous job matching.
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {educationList.map((edu) => (
            <Card key={edu.id} className="relative overflow-hidden">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <h4 className="text-base font-semibold">{edu.degree} in {edu.field_of_study}</h4>
                      {edu.claim_id && (
                        <Badge variant="outline" className="border-emerald-500/50 text-emerald-600 text-[10px]">
                          Claim Verified
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Building2 className="h-4 w-4" />
                      <span>{edu.institution}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground pt-1">
                      <Calendar className="h-3.5 w-3.5" />
                      <span>
                        {edu.start_date || 'N/A'} — {edu.is_current ? 'Present' : edu.end_date || 'N/A'}
                      </span>
                      {edu.gpa && <span>• GPA: {edu.gpa}</span>}
                    </div>
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete(edu.id)}
                    disabled={isProcessing}
                    className="text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>

                {edu.honors && edu.honors.length > 0 && (
                  <div className="mt-4 flex flex-wrap gap-1.5 pt-3 border-t">
                    <span className="text-xs text-muted-foreground flex items-center mr-1">
                      <Award className="h-3 w-3 mr-1 text-primary" /> Honors:
                    </span>
                    {edu.honors.map((h, i) => (
                      <Badge key={i} variant="neutral" className="text-xs font-normal">
                        {h}
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
