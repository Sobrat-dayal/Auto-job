/**
 * Tab: Sources Manager (Stage 26).
 * Manage official job boards, feeds, and APIs.
 */

import * as React from 'react';
import {
  Plus,
  RefreshCw,
  Trash2,
  Power,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { apiClient } from '@/lib/api-client';
import type {
  JobSourceConfig,
  ConnectorManifest,
  JobSourceCreateRequest,
  ConnectorId,
  SourceCategory,
} from '@autonom/shared-types';

interface SourcesManagerTabProps {
  sources: JobSourceConfig[];
  connectors?: ConnectorManifest[];
  onRefreshList: () => void;
}

export const SourcesManagerTab: React.FC<SourcesManagerTabProps> = ({
  sources,
  onRefreshList,
}) => {
  const [isAddOpen, setIsAddOpen] = React.useState(false);
  const [testingSourceId, setTestingSourceId] = React.useState<string | null>(null);
  const [refreshingSourceId, setRefreshingSourceId] = React.useState<string | null>(null);
  const [validationMessage, setValidationMessage] = React.useState<string | null>(null);

  // New source form state
  const [newName, setNewName] = React.useState('');
  const [newConnectorId, setNewConnectorId] = React.useState<ConnectorId>('greenhouse');
  const [newDomain, setNewDomain] = React.useState('boards-api.greenhouse.io');
  const [newBoardToken, setNewBoardToken] = React.useState('');
  const [newEmployerName, setNewEmployerName] = React.useState('');
  const [newRpm, setNewRpm] = React.useState(30);

  const handleValidate = async (sourceId: string) => {
    try {
      setTestingSourceId(sourceId);
      setValidationMessage(null);
      const res = await apiClient.validateJobSource(sourceId);
      setValidationMessage(`[${res.is_valid ? 'SUCCESS' : 'FAILED'}] ${res.message}`);
      onRefreshList();
    } catch (err: any) {
      setValidationMessage(`Validation error: ${err.message || String(err)}`);
    } finally {
      setTestingSourceId(null);
    }
  };

  const handleRefresh = async (sourceId: string) => {
    try {
      setRefreshingSourceId(sourceId);
      const snapshot = await apiClient.refreshJobSource(sourceId);
      setValidationMessage(
        `Synchronized ${snapshot.total_observed} postings (${snapshot.new_count} new, ${snapshot.updated_count} updated, ${snapshot.closed_count} closed)`
      );
      onRefreshList();
    } catch (err: any) {
      setValidationMessage(`Sync error: ${err.message || String(err)}`);
    } finally {
      setRefreshingSourceId(null);
    }
  };

  const handleToggle = async (source: JobSourceConfig) => {
    try {
      await apiClient.updateJobSource(source.id, { is_enabled: !source.is_enabled });
      onRefreshList();
    } catch (err: any) {
      alert(`Failed to toggle source: ${err.message}`);
    }
  };

  const handleDelete = async (sourceId: string) => {
    if (!window.confirm('Delete this job source configuration?')) return;
    try {
      await apiClient.deleteJobSource(sourceId);
      onRefreshList();
    } catch (err: any) {
      alert(`Failed to delete source: ${err.message}`);
    }
  };

  const handleCreate = async () => {
    if (!newName.trim() || !newDomain.trim()) {
      alert('Name and Domain are required.');
      return;
    }
    try {
      const payload: JobSourceCreateRequest = {
        name: newName.trim(),
        connector_id: newConnectorId,
        official_domain: newDomain.trim(),
        board_token: newBoardToken.trim() || undefined,
        employer_name: newEmployerName.trim() || undefined,
        category: 'employer_ats_board' as SourceCategory,
        is_enabled: true,
        rate_limit_rpm: newRpm,
      };
      await apiClient.createJobSource(payload);
      setIsAddOpen(false);
      // Reset
      setNewName('');
      setNewBoardToken('');
      setNewEmployerName('');
      onRefreshList();
    } catch (err: any) {
      alert(`Failed to create source: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Action Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold">Configured Job Sources</h3>
          <p className="text-sm text-muted-foreground">
            Manage provider connections, test API health, and tune request rate limits.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={onRefreshList}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Reload Sources
          </Button>
          <Button size="sm" onClick={() => setIsAddOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add Job Source
          </Button>
        </div>
      </div>

      {validationMessage && (
        <div className="p-3 text-xs rounded-md bg-blue-950/20 border border-blue-800 text-blue-200">
          {validationMessage}
        </div>
      )}

      {/* Sources List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sources.map((src) => (
          <Card key={src.id} className="relative overflow-hidden border">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-sm font-semibold">{src.name}</CardTitle>
                  <CardDescription className="text-xs">{src.employer_name || 'Broad Provider'}</CardDescription>
                </div>
                <Badge
                  variant="outline"
                  className={`text-[10px] capitalize ${
                    src.is_enabled ? 'text-emerald-600 border-emerald-300' : 'text-muted-foreground'
                  }`}
                >
                  {src.is_enabled ? 'Enabled' : 'Disabled'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2 text-muted-foreground">
                <div>
                  <span className="font-medium text-foreground">Connector:</span> {src.connector_id}
                </div>
                <div>
                  <span className="font-medium text-foreground">Domain:</span> {src.official_domain}
                </div>
                {src.board_token && (
                  <div>
                    <span className="font-medium text-foreground">Token/Site:</span> {src.board_token}
                  </div>
                )}
                <div>
                  <span className="font-medium text-foreground">Rate Limit:</span> {src.rate_limit_rpm} RPM
                </div>
              </div>

              <div className="pt-2 border-t flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-7 text-xs"
                    disabled={testingSourceId === src.id}
                    onClick={() => handleValidate(src.id)}
                  >
                    {testingSourceId === src.id ? 'Validating...' : 'Test API'}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-7 text-xs"
                    disabled={refreshingSourceId === src.id || !src.is_enabled}
                    onClick={() => handleRefresh(src.id)}
                  >
                    {refreshingSourceId === src.id ? 'Syncing...' : 'Sync Now'}
                  </Button>
                </div>
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    title={src.is_enabled ? 'Disable source' : 'Enable source'}
                    onClick={() => handleToggle(src)}
                  >
                    <Power className={`w-3.5 h-3.5 ${src.is_enabled ? 'text-emerald-500' : 'text-muted-foreground'}`} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7 text-destructive"
                    title="Delete source"
                    onClick={() => handleDelete(src.id)}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Add Source Modal Dialog */}
      <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="text-base font-semibold">Register New Job Source</DialogTitle>
            <DialogDescription className="text-xs">
              Connect a public job board API (Greenhouse, Lever, Ashby, USAJOBS) or syndicate feed.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2 text-xs">
            <div className="space-y-1">
              <label className="font-medium">Source Name</label>
              <Input
                placeholder="e.g. Cloudflare Careers"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <label className="font-medium">Connector Provider</label>
              <select
                className="w-full h-9 rounded-md border bg-background px-3 py-1 text-xs"
                value={newConnectorId}
                onChange={(e) => {
                  const val = e.target.value as ConnectorId;
                  setNewConnectorId(val);
                  if (val === 'greenhouse') setNewDomain('boards-api.greenhouse.io');
                  else if (val === 'lever') setNewDomain('api.lever.co');
                  else if (val === 'ashby') setNewDomain('api.ashbyhq.com');
                  else if (val === 'usajobs') setNewDomain('data.usajobs.gov');
                }}
              >
                <option value="greenhouse">Greenhouse Job Board API</option>
                <option value="lever">Lever Published Postings API</option>
                <option value="ashby">Ashby Public Job Postings API</option>
                <option value="usajobs">USAJOBS Federal Opportunities</option>
                <option value="rss_atom">RSS / Atom Job Feed</option>
                <option value="json_feed">Structured JSON Endpoint</option>
                <option value="career_page">Employer Career Page</option>
              </select>
            </div>
            <div className="space-y-1">
              <label className="font-medium">Official Domain</label>
              <Input
                placeholder="e.g. boards-api.greenhouse.io"
                value={newDomain}
                onChange={(e) => setNewDomain(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <label className="font-medium">Board Token / Site ID</label>
              <Input
                placeholder="e.g. cloudflare or stripe"
                value={newBoardToken}
                onChange={(e) => setNewBoardToken(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <label className="font-medium">Employer Name (Optional)</label>
              <Input
                placeholder="e.g. Cloudflare"
                value={newEmployerName}
                onChange={(e) => setNewEmployerName(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <label className="font-medium">Rate Limit (Requests per minute)</label>
              <Input
                type="number"
                min={5}
                max={120}
                value={newRpm}
                onChange={(e) => setNewRpm(Number(e.target.value))}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setIsAddOpen(false)}>
              Cancel
            </Button>
            <Button size="sm" onClick={handleCreate}>
              Save Source
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
