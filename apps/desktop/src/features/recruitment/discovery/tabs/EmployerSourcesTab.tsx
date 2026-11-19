/**
 * Tab: Employer Sources Registry (Stage 26).
 * Manages verified employer career pages, origins, and detected ATS portals.
 */

import * as React from 'react';
import { Plus, ExternalLink, Trash2, Building } from 'lucide-react';
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
import type { EmployerCareerSource } from '@autonom/shared-types';

interface EmployerSourcesTabProps {
  employers: EmployerCareerSource[];
  onRefresh: () => void;
}

export const EmployerSourcesTab: React.FC<EmployerSourcesTabProps> = ({ employers, onRefresh }) => {
  const [isAddOpen, setIsAddOpen] = React.useState(false);
  const [empName, setEmpName] = React.useState('');
  const [careerUrl, setCareerUrl] = React.useState('');

  const handleAdd = async () => {
    if (!empName.trim() || !careerUrl.trim()) {
      alert('Employer Name and Career URL are required.');
      return;
    }
    try {
      await apiClient.addEmployerCareerSource({
        employer_name: empName.trim(),
        career_url: careerUrl.trim(),
      });
      setIsAddOpen(false);
      setEmpName('');
      setCareerUrl('');
      onRefresh();
    } catch (err: any) {
      alert(`Failed to add employer: ${err.message}`);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Delete this employer from the career registry?')) return;
    try {
      await apiClient.deleteEmployerCareerSource(id);
      onRefresh();
    } catch (err: any) {
      alert(`Failed to delete employer: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold">Employer Career Portal Registry</h3>
          <p className="text-sm text-muted-foreground">
            Curate direct employer career URLs. AUTONOM inspects origins and detects underlying ATS platforms.
          </p>
        </div>
        <Button size="sm" onClick={() => setIsAddOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Company Portal
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {employers.map((emp) => (
          <Card key={emp.id} className="border">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-semibold flex items-center gap-2">
                  <Building className="w-4 h-4 text-blue-500" />
                  {emp.employer_name}
                </CardTitle>
                <Badge variant="outline" className="text-[10px] capitalize text-emerald-600 border-emerald-300">
                  {emp.access_status.replace(/_/g, ' ')}
                </Badge>
              </div>
              <CardDescription className="text-xs truncate">{emp.career_url}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 text-xs">
              <div className="flex items-center justify-between text-muted-foreground">
                <span>Detected ATS:</span>
                <span className="font-medium text-foreground capitalize">{emp.provider_type || 'Generic Schema'}</span>
              </div>
              <div className="flex items-center justify-between text-muted-foreground">
                <span>Approved Origin:</span>
                <span className="font-medium text-foreground">{emp.approved_origin}</span>
              </div>
              {emp.board_token && (
                <div className="flex items-center justify-between text-muted-foreground">
                  <span>Board Token:</span>
                  <span className="font-mono text-foreground">{emp.board_token}</span>
                </div>
              )}
              <div className="pt-2 border-t flex items-center justify-between">
                <a
                  href={emp.career_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-blue-500 hover:underline flex items-center gap-1"
                >
                  <ExternalLink className="w-3 h-3" />
                  Visit Site
                </a>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 text-destructive"
                  onClick={() => handleDelete(emp.id)}
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="text-base font-semibold">Add Employer Career Portal</DialogTitle>
            <DialogDescription className="text-xs">
              Provide the direct career page URL. AUTONOM will detect the ATS platform automatically.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2 text-xs">
            <div className="space-y-1">
              <label className="font-medium">Employer Name</label>
              <Input
                placeholder="e.g. Figma or Snowflake"
                value={empName}
                onChange={(e) => setEmpName(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <label className="font-medium">Career Page URL</label>
              <Input
                placeholder="e.g. https://boards.greenhouse.io/figma"
                value={careerUrl}
                onChange={(e) => setCareerUrl(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setIsAddOpen(false)}>
              Cancel
            </Button>
            <Button size="sm" onClick={handleAdd}>
              Save Employer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
