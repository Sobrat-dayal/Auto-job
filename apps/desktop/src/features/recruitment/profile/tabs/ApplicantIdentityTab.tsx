/**
 * Stage 21: Applicant Identity & Contact Information Tab.
 * Legal name, contact points, location preferences, and work authorization eligibility.
 */

import * as React from 'react';
import { UserCheck, Save, MapPin, Briefcase } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { ApplicantProfile, ContactInfo, LocationInfo, EmploymentEligibility } from '@autonom/shared-types';

interface ApplicantIdentityTabProps {
  profile: ApplicantProfile | null;
  onSave: (payload: { contact: ContactInfo; location: LocationInfo; eligibility: EmploymentEligibility }) => Promise<void>;
  isSaving: boolean;
}

export const ApplicantIdentityTab: React.FC<ApplicantIdentityTabProps> = ({
  profile,
  onSave,
  isSaving,
}) => {
  const [contact, setContact] = React.useState<ContactInfo>(profile?.contact || {});
  const [location, setLocation] = React.useState<LocationInfo>(profile?.location || {});
  const [eligibility, setEligibility] = React.useState<EmploymentEligibility>(profile?.eligibility || {});
  const [hasChanges, setHasChanges] = React.useState<boolean>(false);

  React.useEffect(() => {
    if (profile) {
      setContact(profile.contact || {});
      setLocation(profile.location || {});
      setEligibility(profile.eligibility || {});
    }
  }, [profile]);

  const handleContactChange = (field: keyof ContactInfo, value: any) => {
    setContact((prev) => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  const handleLocationChange = (field: keyof LocationInfo, value: any) => {
    setLocation((prev) => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  const handleEligibilityChange = (field: keyof EmploymentEligibility, value: any) => {
    setEligibility((prev) => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSave({ contact, location, eligibility });
    setHasChanges(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">Verified Identity & Employment Eligibility</h3>
          <p className="text-sm text-muted-foreground">
            Strictly user-confirmed identity data. Redacted from downstream agent reasoning unless explicitly scoped.
          </p>
        </div>
        <Button type="submit" disabled={!hasChanges || isSaving}>
          <Save className="mr-2 h-4 w-4" />
          {isSaving ? 'Saving...' : 'Save Changes'}
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Contact Information */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <UserCheck className="h-4 w-4 text-primary" />
                Legal & Contact Information
              </CardTitle>
              {contact.is_verified && (
                <Badge variant="outline" className="border-emerald-500 text-emerald-600">
                  Verified Contact
                </Badge>
              )}
            </div>
            <CardDescription>
              Legal name for official submissions and verified direct contact channels.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Legal Full Name
              </label>
              <Input
                value={contact.legal_name || ''}
                onChange={(e) => handleContactChange('legal_name', e.target.value)}
                placeholder="e.g. Jane Marie Doe"
                className="mt-1"
              />
            </div>

            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Preferred Name / Display Name
              </label>
              <Input
                value={contact.preferred_name || ''}
                onChange={(e) => handleContactChange('preferred_name', e.target.value)}
                placeholder="e.g. Jane Doe"
                className="mt-1"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Primary Email
                </label>
                <Input
                  type="email"
                  value={contact.primary_email || ''}
                  onChange={(e) => handleContactChange('primary_email', e.target.value)}
                  placeholder="jane.doe@example.com"
                  className="mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Phone Number
                </label>
                <Input
                  value={contact.phone_number || ''}
                  onChange={(e) => handleContactChange('phone_number', e.target.value)}
                  placeholder="+1 (555) 019-2834"
                  className="mt-1"
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                LinkedIn Profile URL
              </label>
              <Input
                value={contact.linkedin_url || ''}
                onChange={(e) => handleContactChange('linkedin_url', e.target.value)}
                placeholder="https://linkedin.com/in/janedoe"
                className="mt-1"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  GitHub Profile URL
                </label>
                <Input
                  value={contact.github_url || ''}
                  onChange={(e) => handleContactChange('github_url', e.target.value)}
                  placeholder="https://github.com/janedoe"
                  className="mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Portfolio / Personal Site
                </label>
                <Input
                  value={contact.portfolio_url || ''}
                  onChange={(e) => handleContactChange('portfolio_url', e.target.value)}
                  placeholder="https://janedoe.dev"
                  className="mt-1"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Location & Geographic Preferences */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <MapPin className="h-4 w-4 text-primary" />
              Location & Mobility
            </CardTitle>
            <CardDescription>
              Geographic residency, timezone coordination, and remote work preferences.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  City
                </label>
                <Input
                  value={location.city || ''}
                  onChange={(e) => handleLocationChange('city', e.target.value)}
                  placeholder="San Francisco"
                  className="mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  State / Province
                </label>
                <Input
                  value={location.state_or_province || ''}
                  onChange={(e) => handleLocationChange('state_or_province', e.target.value)}
                  placeholder="CA"
                  className="mt-1"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Country
                </label>
                <Input
                  value={location.country || ''}
                  onChange={(e) => handleLocationChange('country', e.target.value)}
                  placeholder="United States"
                  className="mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Timezone
                </label>
                <Input
                  value={location.timezone || ''}
                  onChange={(e) => handleLocationChange('timezone', e.target.value)}
                  placeholder="America/Los_Angeles"
                  className="mt-1"
                />
              </div>
            </div>

            <div className="space-y-2 pt-2 border-t">
              <label className="flex items-center gap-2 text-sm font-medium cursor-pointer">
                <input
                  type="checkbox"
                  checked={location.is_remote_open ?? true}
                  onChange={(e) => handleLocationChange('is_remote_open', e.target.checked)}
                  className="rounded border-gray-300"
                />
                Open to 100% Remote Opportunities
              </label>

              <label className="flex items-center gap-2 text-sm font-medium cursor-pointer">
                <input
                  type="checkbox"
                  checked={location.willing_to_relocate ?? false}
                  onChange={(e) => handleLocationChange('willing_to_relocate', e.target.checked)}
                  className="rounded border-gray-300"
                />
                Willing to Relocate for Position
              </label>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Employment Eligibility & Authorization */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Briefcase className="h-4 w-4 text-primary" />
            Legal Employment Eligibility & Work Authorization
          </CardTitle>
          <CardDescription>
            Zero-hallucination compliance. Used to prevent applying to roles where visa sponsorship criteria cannot be fulfilled.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Citizenship Country
              </label>
              <Input
                value={eligibility.citizenship_country || ''}
                onChange={(e) => handleEligibilityChange('citizenship_country', e.target.value)}
                placeholder="United States"
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Work Authorization Status
              </label>
              <Input
                value={eligibility.work_authorization_status || ''}
                onChange={(e) => handleEligibilityChange('work_authorization_status', e.target.value)}
                placeholder="e.g. Citizen, Permanent Resident, STEM OPT"
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Notice Period (Days)
              </label>
              <Input
                type="number"
                value={eligibility.notice_period_days ?? ''}
                onChange={(e) => handleEligibilityChange('notice_period_days', e.target.value ? parseInt(e.target.value, 10) : null)}
                placeholder="14"
                className="mt-1"
              />
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2 pt-2">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Security Clearance Level
              </label>
              <Input
                value={eligibility.security_clearance || ''}
                onChange={(e) => handleEligibilityChange('security_clearance', e.target.value)}
                placeholder="e.g. None, Secret, Top Secret / SCI"
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Earliest Available Start Date
              </label>
              <Input
                value={eligibility.available_start_date || ''}
                onChange={(e) => handleEligibilityChange('available_start_date', e.target.value)}
                placeholder="YYYY-MM-DD or Immediately"
                className="mt-1"
              />
            </div>
          </div>

          <div className="pt-2 border-t">
            <label className="flex items-center gap-2 text-sm font-medium cursor-pointer">
              <input
                type="checkbox"
                checked={eligibility.requires_sponsorship ?? false}
                onChange={(e) => handleEligibilityChange('requires_sponsorship', e.target.checked)}
                className="rounded border-gray-300"
              />
              Requires Current or Future Visa Sponsorship (e.g. H-1B, TN, O-1)
            </label>
          </div>
        </CardContent>
      </Card>
    </form>
  );
};
