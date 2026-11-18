import * as React from 'react';
import {
  BookOpen,
  Play,
  GitBranch,
  ShieldAlert,
  ShieldCheck,
  Download,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Search,
  Eye,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type { ReusableProcedure, PreflightReport } from '@autonom/shared-types';

interface ProcedureLibraryTabProps {
  onSelectProcedure?: (procedure: ReusableProcedure) => void;
  onRunProcedure?: (procedureId: string, version: number) => void;
}

export const ProcedureLibraryTab: React.FC<ProcedureLibraryTabProps> = ({
  onSelectProcedure,
  onRunProcedure,
}) => {
  const [procedures, setProcedures] = React.useState<ReusableProcedure[]>([]);
  const [searchTerm, setSearchTerm] = React.useState<string>('');
  const [selectedCategory, setSelectedCategory] = React.useState<string>('all');
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [preflightResults, setPreflightResults] = React.useState<Record<string, PreflightReport>>({});
  const [message, setMessage] = React.useState<string | null>(null);

  const loadProcedures = React.useCallback(async () => {
    setIsLoading(true);
    try {
      const list = await apiClient.listProcedures(
        selectedCategory === 'all' ? undefined : selectedCategory,
        true
      );
      setProcedures(list);
    } catch (err: any) {
      console.error('Failed to load procedures:', err);
      setMessage(`Failed to load procedures: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [selectedCategory]);

  React.useEffect(() => {
    loadProcedures();
  }, [loadProcedures]);

  const handlePreflight = async (procedureId: string, version: number) => {
    try {
      const report = await apiClient.preflightProcedure(procedureId, {}, version);
      setPreflightResults((prev) => ({ ...prev, [procedureId]: report }));
      setMessage(
        report.can_execute
          ? `Preflight passed for ${procedureId} v${version}`
          : `Preflight flagged issues: ${report.issues.join(', ')}`
      );
    } catch (err: any) {
      setMessage(`Preflight error: ${err.message}`);
    }
  };

  const handleBranch = async (procedureId: string) => {
    try {
      const branched = await apiClient.branchProcedureDraft(procedureId);
      setMessage(`Branched new draft v${branched.version} for ${procedureId}`);
      await loadProcedures();
    } catch (err: any) {
      setMessage(`Branch error: ${err.message}`);
    }
  };

  const handleExport = (proc: ReusableProcedure) => {
    const jsonStr = JSON.stringify(proc, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `procedure-${proc.name.toLowerCase().replace(/\s+/g, '-')}-v${proc.version}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredProcedures = procedures.filter((p) => {
    const matchesSearch =
      p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.procedure_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.category.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  return (
    <div className="space-y-6" data-testid="procedure-library-tab">
      {/* Header & Controls */}
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <BookOpen className="h-4 w-4 text-blue-400" />
                Reusable Procedure Library
              </CardTitle>
              <CardDescription className="text-xs">
                Parameterized, versioned automation procedures compiled from verified recordings.
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={loadProcedures}
                disabled={isLoading}
                className="h-8 gap-1 text-xs"
              >
                <RefreshCw className={`h-3 w-3 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row items-center gap-3">
            <div className="relative flex-1 w-full">
              <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-400" />
              <Input
                placeholder="Search procedures by name, ID, or category..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 h-8 text-xs bg-slate-900/60"
                data-testid="procedure-search-input"
              />
            </div>
            <div className="flex items-center gap-1.5 w-full sm:w-auto">
              {['all', 'general', 'recruitment', 'browser', 'desktop'].map((cat) => (
                <Button
                  key={cat}
                  variant={selectedCategory === cat ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory(cat)}
                  className="h-7 text-xs capitalize"
                >
                  {cat}
                </Button>
              ))}
            </div>
          </div>

          {message && (
            <div className="mt-3 text-xs p-2 rounded bg-slate-800/80 border border-slate-700 text-slate-300 font-mono">
              {message}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Procedures Grid / List */}
      <div className="space-y-3">
        {filteredProcedures.length === 0 ? (
          <Card className="border-border/60 bg-card/60">
            <CardContent className="py-12 text-center text-slate-400 text-xs">
              No procedures found. Record computer actions in the Studio to compile your first procedure.
            </CardContent>
          </Card>
        ) : (
          filteredProcedures.map((proc) => {
            const preflight = preflightResults[proc.procedure_id];
            return (
              <Card
                key={`${proc.procedure_id}-v${proc.version}`}
                className="border-border/60 bg-card/60 hover:border-slate-700 transition-colors"
                data-testid={`procedure-card-${proc.procedure_id}`}
              >
                <CardContent className="p-4">
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div className="space-y-1.5 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-semibold text-sm text-slate-100">{proc.name}</span>
                        <Badge variant="outline" className="font-mono text-[10px] bg-slate-800/60 text-slate-300">
                          v{proc.version}
                        </Badge>
                        <Badge variant="outline" className="text-[10px] capitalize text-slate-300">
                          {proc.category}
                        </Badge>
                        {proc.is_draft ? (
                          <Badge variant="outline" className="border-amber-500/40 text-amber-400 bg-amber-500/10 text-[10px]">
                            DRAFT
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="border-emerald-500/40 text-emerald-400 bg-emerald-500/10 text-[10px]">
                            PUBLISHED
                          </Badge>
                        )}
                        {proc.validation_status === 'valid' ? (
                          <Badge variant="outline" className="border-emerald-500/30 text-emerald-400 text-[10px] flex items-center gap-1">
                            <CheckCircle2 className="h-2.5 w-2.5" /> Valid
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="border-red-500/30 text-red-400 text-[10px] flex items-center gap-1">
                            <AlertTriangle className="h-2.5 w-2.5" /> {proc.validation_status}
                          </Badge>
                        )}
                        <span className="text-slate-400 text-[11px] font-mono">
                          Risk: {proc.static_risk_score} / 100
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 line-clamp-1">{proc.description || 'No description provided.'}</p>
                      <div className="flex flex-wrap items-center gap-4 text-[11px] text-slate-400 pt-1">
                        <span>
                          <strong className="text-slate-300">{proc.steps.length}</strong> steps
                        </span>
                        <span>
                          <strong className="text-slate-300">{proc.parameters.length}</strong> parameters
                        </span>
                        <span>
                          Created: <span className="font-mono">{new Date(proc.created_at).toLocaleDateString()}</span>
                        </span>
                        {proc.allowed_applications.length > 0 && (
                          <span className="font-mono text-slate-400">
                            Apps: {proc.allowed_applications.join(', ')}
                          </span>
                        )}
                      </div>

                      {preflight && (
                        <div className={`mt-2 p-2 rounded text-xs border ${
                          preflight.can_execute
                            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                            : 'bg-red-500/10 border-red-500/30 text-red-300'
                        }`}>
                          <div className="font-semibold flex items-center gap-1.5">
                            {preflight.can_execute ? <ShieldCheck className="h-3.5 w-3.5" /> : <ShieldAlert className="h-3.5 w-3.5" />}
                            Preflight: {preflight.can_execute ? 'Ready for Replay' : 'Blocked'}
                          </div>
                          {preflight.issues.length > 0 && (
                            <div className="text-[11px] mt-0.5">Issues: {preflight.issues.join('; ')}</div>
                          )}
                        </div>
                      )}
                    </div>

                    <div className="flex flex-wrap items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onSelectProcedure?.(proc)}
                        className="h-8 text-xs gap-1"
                        data-testid={`inspect-procedure-${proc.procedure_id}`}
                      >
                        <Eye className="h-3 w-3" />
                        Inspect / Edit
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePreflight(proc.procedure_id, proc.version)}
                        className="h-8 text-xs gap-1 border-slate-700"
                        data-testid={`preflight-procedure-${proc.procedure_id}`}
                      >
                        <ShieldCheck className="h-3 w-3" />
                        Preflight
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleBranch(proc.procedure_id)}
                        className="h-8 text-xs gap-1"
                      >
                        <GitBranch className="h-3 w-3" />
                        Branch Draft
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleExport(proc)}
                        className="h-8 text-xs gap-1"
                      >
                        <Download className="h-3 w-3" />
                        Export
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => onRunProcedure?.(proc.procedure_id, proc.version)}
                        className="h-8 text-xs gap-1 bg-emerald-600 hover:bg-emerald-700 text-white font-medium"
                        data-testid={`run-procedure-${proc.procedure_id}`}
                      >
                        <Play className="h-3 w-3 fill-current" />
                        Execute
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
};
