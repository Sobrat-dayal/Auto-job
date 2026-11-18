import * as React from 'react';
import {
  UserCheck,
  Plus,
  Lock,
  RefreshCw,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  BrowserProfileResponse,
  BrowserProfileCreateRequest,
} from '@autonom/shared-types';

interface BrowserProfilesTabProps {
  profiles: BrowserProfileResponse[];
  onCreateProfile: (req: BrowserProfileCreateRequest) => Promise<void>;
  onRefresh: () => void;
  isLoading: boolean;
}

export const BrowserProfilesTab: React.FC<BrowserProfilesTabProps> = ({
  profiles,
  onCreateProfile,
  onRefresh,
  isLoading,
}) => {
  const [isCreating, setIsCreating] = React.useState<boolean>(false);
  const [name, setName] = React.useState<string>('');
  const [description, setDescription] = React.useState<string>('');
  const [domainScopes, setDomainScopes] = React.useState<string>('linkedin.com, indeed.com, greenhouse.io');
  const [isSubmitting, setIsSubmitting] = React.useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setIsSubmitting(true);
    try {
      const scopes = domainScopes
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);
      await onCreateProfile({
        name: name.trim(),
        description: description.trim(),
        domain_scopes: scopes,
      });
      setName('');
      setDescription('');
      setIsCreating(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <Lock className="h-4 w-4 text-primary" />
                Browser Profiles & Authenticated Storage State
              </CardTitle>
              <CardDescription className="text-xs">
                Encrypted browser session cookies and local storage tokens backed by Windows DPAPI.
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={onRefresh}
                disabled={isLoading}
                className="gap-1.5 text-xs h-8"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button
                size="sm"
                onClick={() => setIsCreating(!isCreating)}
                className="gap-1.5 text-xs font-semibold h-8"
              >
                <Plus className="h-3.5 w-3.5" />
                New Profile
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isCreating && (
            <form onSubmit={handleSubmit} className="mb-6 p-4 rounded-lg border border-primary/30 bg-primary/5 space-y-3">
              <h4 className="text-xs font-bold text-foreground">Create Isolated Browser Profile</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-xs font-medium text-muted-foreground">Profile Name</label>
                  <Input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Primary Job Seeker"
                    required
                    className="h-8 text-xs font-medium"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium text-muted-foreground">Domain Scopes (comma-separated)</label>
                  <Input
                    value={domainScopes}
                    onChange={(e) => setDomainScopes(e.target.value)}
                    placeholder="linkedin.com, indeed.com"
                    className="h-8 text-xs font-mono"
                  />
                </div>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-muted-foreground">Description</label>
                <Input
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Optional profile notes..."
                  className="h-8 text-xs"
                />
              </div>
              <div className="flex justify-end gap-2 pt-1">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setIsCreating(false)}
                  className="h-7 text-xs"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  size="sm"
                  disabled={isSubmitting}
                  className="h-7 text-xs font-semibold"
                >
                  {isSubmitting ? 'Creating...' : 'Save Profile'}
                </Button>
              </div>
            </form>
          )}

          {profiles.length === 0 ? (
            <div className="py-12 text-center text-muted-foreground">
              <Lock className="h-10 w-10 mx-auto mb-3 opacity-30" />
              <p className="text-sm font-medium">No custom browser profiles created</p>
              <p className="text-xs mt-1">
                Default ephemeral contexts are used for browsing. Create a profile above to persist logins.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {profiles.map((p) => (
                <div
                  key={p.id}
                  className="p-3.5 rounded-lg border border-border/40 bg-background/40 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <UserCheck className="h-4 w-4 text-primary" />
                      <span className="font-semibold text-xs text-foreground">{p.name}</span>
                      <Badge
                        variant={p.is_authenticated ? 'success' : 'neutral'}
                        className="text-[10px] uppercase font-mono"
                      >
                        {p.is_authenticated ? 'Authenticated' : 'Pending Auth'}
                      </Badge>
                    </div>
                    <span className="text-[10px] text-muted-foreground font-mono">
                      {new Date(p.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  {p.description && (
                    <p className="text-xs text-muted-foreground">{p.description}</p>
                  )}

                  <div className="flex flex-wrap items-center gap-1.5 pt-1">
                    <span className="text-[11px] text-muted-foreground font-medium">Allowed Domains:</span>
                    {p.domain_scopes.map((d) => (
                      <Badge key={d} variant="outline" className="text-[10px] font-mono">
                        {d}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
