/**
 * Tab: Discovery Settings (Stage 26).
 * Tune discovery engine concurrency, network timeout, and SSRF security policies.
 */

import * as React from 'react';
import { Sliders, Shield, Save, CheckCircle2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';
import type { DiscoverySettingsConfig } from '@autonom/shared-types';

interface DiscoverySettingsTabProps {
  settings: DiscoverySettingsConfig | null;
  onRefresh: () => void;
}

export const DiscoverySettingsTab: React.FC<DiscoverySettingsTabProps> = ({
  settings,
  onRefresh,
}) => {
  const [maxConcurrent, setMaxConcurrent] = React.useState(settings?.max_concurrent_sources ?? 4);
  const [requestTimeout, setRequestTimeout] = React.useState(settings?.request_timeout_seconds ?? 20);
  const [defaultRpm, setDefaultRpm] = React.useState(settings?.per_source_request_rpm ?? 30);
  const [maxPostings, setMaxPostings] = React.useState(settings?.max_postings_per_task ?? 200);
  const [enforceSsrf, setEnforceSsrf] = React.useState(settings?.enforce_ssrf_protection ?? true);
  const [isSaved, setIsSaved] = React.useState(false);

  React.useEffect(() => {
    if (settings) {
      setMaxConcurrent(settings.max_concurrent_sources);
      setRequestTimeout(settings.request_timeout_seconds);
      setDefaultRpm(settings.per_source_request_rpm);
      setMaxPostings(settings.max_postings_per_task);
      setEnforceSsrf(settings.enforce_ssrf_protection);
    }
  }, [settings]);

  const handleSave = async () => {
    try {
      await apiClient.updateDiscoverySettings({
        max_concurrent_sources: maxConcurrent,
        per_source_request_rpm: defaultRpm,
        request_timeout_seconds: requestTimeout,
        max_postings_per_task: maxPostings,
        max_browser_sessions: settings?.max_browser_sessions ?? 1,
        cache_duration_minutes: settings?.cache_duration_minutes ?? 60,
        allow_browser_fallback: settings?.allow_browser_fallback ?? true,
        enforce_ssrf_protection: enforceSsrf,
        local_only_preference: settings?.local_only_preference ?? false,
      });
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 3000);
      onRefresh();
    } catch (err: any) {
      alert(`Failed to save settings: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <Sliders className="w-4 h-4 text-blue-500" />
            Discovery Concurrency & Network Throttling
          </CardTitle>
          <CardDescription className="text-xs">
            Govern request volumes and timeout behavior when communicating with provider APIs.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 text-xs">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="font-medium">Max Concurrent Sources</label>
              <Input
                type="number"
                min={1}
                max={16}
                value={maxConcurrent}
                onChange={(e) => setMaxConcurrent(Number(e.target.value))}
              />
              <span className="text-[10px] text-muted-foreground">Parallel worker pool size</span>
            </div>
            <div className="space-y-1">
              <label className="font-medium">HTTP Request Timeout (seconds)</label>
              <Input
                type="number"
                min={5}
                max={120}
                value={requestTimeout}
                onChange={(e) => setRequestTimeout(Number(e.target.value))}
              />
              <span className="text-[10px] text-muted-foreground">Socket connect & read ceiling</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="font-medium">Default Rate Limit (RPM)</label>
              <Input
                type="number"
                min={5}
                max={120}
                value={defaultRpm}
                onChange={(e) => setDefaultRpm(Number(e.target.value))}
              />
              <span className="text-[10px] text-muted-foreground">Sliding window requests/min</span>
            </div>
            <div className="space-y-1">
              <label className="font-medium">Max Postings per Task</label>
              <Input
                type="number"
                min={20}
                max={1000}
                value={maxPostings}
                onChange={(e) => setMaxPostings(Number(e.target.value))}
              />
              <span className="text-[10px] text-muted-foreground">Safety limit for batch runs</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <Shield className="w-4 h-4 text-emerald-500" />
            Security & Boundary Controls
          </CardTitle>
          <CardDescription className="text-xs">
            Protect local workspace and metadata services from Server-Side Request Forgery.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-xs">
          <div className="flex items-center justify-between p-3 rounded border">
            <div>
              <div className="font-medium">Strict SSRF Protection</div>
              <div className="text-[11px] text-muted-foreground">
                Block requests resolving to loopback (127.0.0.1), private RFC1918 subnets, and cloud metadata (169.254.169.254).
              </div>
            </div>
            <input
              type="checkbox"
              className="w-4 h-4 rounded cursor-pointer"
              checked={enforceSsrf}
              onChange={(e) => setEnforceSsrf(e.target.checked)}
            />
          </div>

          <div className="pt-2 flex items-center justify-between">
            {isSaved && (
              <span className="text-emerald-500 flex items-center gap-1.5 text-xs">
                <CheckCircle2 className="w-4 h-4" />
                Settings saved successfully!
              </span>
            )}
            <div className="ml-auto">
              <Button size="sm" onClick={handleSave}>
                <Save className="w-3.5 h-3.5 mr-2" />
                Save Settings
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
