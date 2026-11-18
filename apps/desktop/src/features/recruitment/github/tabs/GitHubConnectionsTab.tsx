/**
 * GitHub Connections Tab: Manage connected accounts, PAT auth, DPAPI vault status, and scopes.
 */

import * as React from 'react';
import {
  Github,
  Key,
  ShieldCheck,
  Lock,
  Globe,
  Trash2,
  ExternalLink,
  AlertCircle,
  Eye,
  EyeOff,
  Plus,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import type {
  GitHubConnection,
  GitHubConnectionMode,
  ConnectGitHubRequest,
} from '@autonom/shared-types';

interface GitHubConnectionsTabProps {
  connections: GitHubConnection[];
  onConnect: (payload: ConnectGitHubRequest) => Promise<void>;
  onDisconnect: (connectionId: string) => Promise<void>;
  isLoading: boolean;
}

export const GitHubConnectionsTab: React.FC<GitHubConnectionsTabProps> = ({
  connections,
  onConnect,
  onDisconnect,
  isLoading,
}) => {
  const [username, setUsername] = React.useState('');
  const [mode, setMode] = React.useState<GitHubConnectionMode>('public_only');
  const [accessToken, setAccessToken] = React.useState('');
  const [showToken, setShowToken] = React.useState(false);
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) {
      setErrorMsg('GitHub username is required.');
      return;
    }
    if (mode === 'personal_access_token' && !accessToken.trim()) {
      setErrorMsg('Personal Access Token is required for PAT mode.');
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMsg(null);
      await onConnect({
        username: username.trim(),
        mode,
        access_token: mode === 'personal_access_token' ? accessToken.trim() : undefined,
        profile_id: 'prof_primary_applicant',
      });
      setUsername('');
      setAccessToken('');
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to connect GitHub account.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Existing Connected Accounts */}
      <div className="space-y-4">
        <h3 className="text-base font-semibold tracking-tight">Active Connections</h3>
        {connections.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {connections.map((conn) => (
              <Card key={conn.id} className="border-border/80 relative overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary to-emerald-500" />
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {conn.avatar_url ? (
                        <img
                          src={conn.avatar_url}
                          alt={conn.login}
                          className="h-11 w-11 rounded-full border border-border"
                        />
                      ) : (
                        <div className="h-11 w-11 rounded-full bg-primary/20 flex items-center justify-center font-bold text-primary">
                          {conn.login.slice(0, 2).toUpperCase()}
                        </div>
                      )}
                      <div>
                        <CardTitle className="text-sm font-semibold flex items-center gap-1.5">
                          {conn.name || conn.login}
                          <a
                            href={`https://github.com/${conn.login}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-muted-foreground hover:text-foreground"
                          >
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        </CardTitle>
                        <CardDescription className="text-xs">@{conn.login}</CardDescription>
                      </div>
                    </div>
                    <Badge
                      variant="outline"
                      className="bg-emerald-500/10 text-emerald-500 border-emerald-500/30 text-xs"
                    >
                      {conn.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-2.5 text-xs">
                  <div className="grid grid-cols-2 gap-2 bg-secondary/30 p-2.5 rounded-lg border border-border/50">
                    <div>
                      <span className="text-muted-foreground block text-[11px]">Mode</span>
                      <span className="font-medium capitalize">{conn.mode.replace('_', ' ')}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block text-[11px]">Private Repos</span>
                      <span className="font-medium flex items-center gap-1">
                        {conn.can_access_private ? (
                          <>
                            <Lock className="h-3 w-3 text-emerald-500" /> Enabled
                          </>
                        ) : (
                          <>
                            <Globe className="h-3 w-3 text-muted-foreground" /> Disabled
                          </>
                        )}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block text-[11px]">Public Repos</span>
                      <span className="font-medium">{conn.public_repos_count}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block text-[11px]">Followers</span>
                      <span className="font-medium">{conn.followers_count}</span>
                    </div>
                  </div>

                  {conn.scopes.length > 0 && (
                    <div>
                      <span className="text-[11px] text-muted-foreground block mb-1">Granted Token Scopes:</span>
                      <div className="flex flex-wrap gap-1">
                        {conn.scopes.map((s) => (
                          <Badge key={s} variant="neutral" className="text-[10px] py-0 px-1.5">
                            {s}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="pt-1 flex items-center justify-between text-[11px] text-muted-foreground">
                    <span>Connected: {new Date(conn.connected_at).toLocaleDateString()}</span>
                    <span className="text-emerald-500 flex items-center gap-1">
                      <ShieldCheck className="h-3 w-3" /> DPAPI Encrypted
                    </span>
                  </div>
                </CardContent>
                <CardFooter className="pt-1 flex justify-end">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDisconnect(conn.id)}
                    className="text-status-error hover:bg-status-error/10 text-xs gap-1 h-8"
                  >
                    <Trash2 className="h-3.5 w-3.5" /> Disconnect & Revoke
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        ) : (
          <div className="p-6 border border-dashed border-border rounded-xl text-center space-y-2">
            <Github className="h-8 w-8 text-muted-foreground/40 mx-auto" />
            <p className="text-sm text-muted-foreground">No accounts connected yet. Add an account below.</p>
          </div>
        )}
      </div>

      {/* Connect Account Form */}
      <Card className="border-border/80">
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Plus className="h-4 w-4 text-primary" /> Connect GitHub Account
          </CardTitle>
          <CardDescription className="text-xs">
            Connect using your public profile (read-only) or supply a fine-grained Personal Access Token to include selected private repositories.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4 max-w-xl">
            {errorMsg && (
              <div className="p-3 rounded-lg bg-status-error/10 border border-status-error/20 text-status-error text-xs flex items-center gap-2">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Username */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold">GitHub Username or Organization</label>
              <Input
                placeholder="e.g. torvalds or octocat"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={isSubmitting}
                className="text-xs"
              />
            </div>

            {/* Connection Mode Selector */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold">Authentication Mode</label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setMode('public_only')}
                  className={`p-3 rounded-lg border text-left text-xs transition-colors flex flex-col gap-1 ${
                    mode === 'public_only'
                      ? 'border-primary bg-primary/5 text-primary'
                      : 'border-border hover:bg-secondary/40'
                  }`}
                >
                  <span className="font-semibold flex items-center gap-1.5">
                    <Globe className="h-3.5 w-3.5" /> Public Only
                  </span>
                  <span className="text-[11px] text-muted-foreground">
                    Discover public repositories, commits, and language stats. No token needed.
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => setMode('personal_access_token')}
                  className={`p-3 rounded-lg border text-left text-xs transition-colors flex flex-col gap-1 ${
                    mode === 'personal_access_token'
                      ? 'border-primary bg-primary/5 text-primary'
                      : 'border-border hover:bg-secondary/40'
                  }`}
                >
                  <span className="font-semibold flex items-center gap-1.5">
                    <Key className="h-3.5 w-3.5" /> Personal Access Token (PAT)
                  </span>
                  <span className="text-[11px] text-muted-foreground">
                    Access selected private repositories and 5,000 req/hr rate limit budget.
                  </span>
                </button>
              </div>
            </div>

            {/* Token Input (Only for PAT mode) */}
            {mode === 'personal_access_token' && (
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-semibold flex items-center gap-1">
                    <Key className="h-3 w-3 text-primary" /> Personal Access Token (PAT)
                  </label>
                  <a
                    href="https://github.com/settings/tokens?type=beta"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[11px] text-primary hover:underline inline-flex items-center gap-0.5"
                  >
                    Generate fine-grained token <ExternalLink className="h-2.5 w-2.5" />
                  </a>
                </div>
                <div className="relative">
                  <Input
                    type={showToken ? 'text' : 'password'}
                    placeholder="github_pat_... or ghp_..."
                    value={accessToken}
                    onChange={(e) => setAccessToken(e.target.value)}
                    disabled={isSubmitting}
                    className="text-xs pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowToken(!showToken)}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showToken ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                <p className="text-[11px] text-muted-foreground">
                  Recommended scopes: <code className="bg-secondary px-1 py-0.5 rounded text-[10px]">repo:status</code>, <code className="bg-secondary px-1 py-0.5 rounded text-[10px]">public_repo</code>, or Read-only Contents.
                </p>
              </div>
            )}

            {/* Security Guarantee Banner */}
            <div className="p-3 bg-secondary/30 rounded-lg border border-border/50 text-[11px] text-muted-foreground flex items-start gap-2.5">
              <ShieldCheck className="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-foreground">Zero-Exposure Credential Vault:</span> Tokens are encrypted at rest using Windows DPAPI (Data Protection API) and scoped authenticated associated data. Plaintext tokens are never stored, logged, or sent to AI models.
              </div>
            </div>

            <Button type="submit" disabled={isSubmitting || isLoading} variant="primary" className="gap-1.5 text-xs">
              <Github className="h-4 w-4" />
              {isSubmitting ? 'Validating & Connecting...' : 'Connect GitHub Account'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};
