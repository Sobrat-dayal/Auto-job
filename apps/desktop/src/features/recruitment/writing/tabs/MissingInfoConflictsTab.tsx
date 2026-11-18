/**
 * Stage 24: Missing Information & Conflicts Tab.
 * Surfaces unanswered application requirements and flags discrepancies between profile claims and written materials.
 */

import * as React from 'react';
import {
  AlertTriangle,
  ShieldCheck,
  CheckCircle2,
  FileQuestion,
  ArrowRight,
  RefreshCw,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type {
  MissingInformationItem,
  ConflictItem,
} from '@autonom/shared-types';

interface MissingInfoConflictsTabProps {
  missingItems: MissingInformationItem[];
  conflicts: ConflictItem[];
  onRefresh: () => Promise<void>;
  onNavigateTab: (tabId: string) => void;
}

export const MissingInfoConflictsTab: React.FC<MissingInfoConflictsTabProps> = ({
  missingItems,
  conflicts,
  onRefresh,
  onNavigateTab,
}) => {
  const [isRefreshing, setIsRefreshing] = React.useState<boolean>(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await onRefresh();
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/80 border border-slate-800">
        <div>
          <h3 className="text-xs font-semibold text-slate-200">
            Factual Completeness & Contradiction Auditing
          </h3>
          <p className="text-[11px] text-slate-400">
            Identifies gaps in your canonical profile needed by application questions, and prevents contradictory claims.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="h-7 text-xs border-slate-700 text-slate-300"
        >
          <RefreshCw className={`w-3.5 h-3.5 mr-1 ${isRefreshing ? 'animate-spin' : ''}`} />
          Run Audit
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Missing Profile Information Queue */}
        <div className="space-y-4">
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-3 flex flex-row items-center justify-between">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                  <FileQuestion className="w-4 h-4 text-cyan-400" />
                  <CardTitle className="text-xs font-semibold text-slate-200">
                    Missing Information Items ({missingItems.length})
                  </CardTitle>
                </div>
                <p className="text-[11px] text-slate-400">
                  Data points required by application questions that are absent from your profile.
                </p>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {missingItems.length === 0 ? (
                <div className="py-8 text-center text-xs text-slate-500 space-y-1">
                  <CheckCircle2 className="w-6 h-6 text-emerald-500 mx-auto" />
                  <p>All required factual fields are populated in your profile.</p>
                </div>
              ) : (
                missingItems.map((item) => (
                  <div
                    key={item.id}
                    className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 space-y-2 text-xs"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="space-y-0.5">
                        <span className="font-semibold text-slate-200 block">
                          {item.required_field}
                        </span>
                        <p className="text-[11px] text-slate-400">{item.field_description}</p>
                      </div>
                      {item.is_mandatory && (
                        <Badge variant="neutral" className="bg-rose-950/60 text-rose-400 border-rose-800 text-[10px]">
                          Mandatory
                        </Badge>
                      )}
                    </div>

                    <div className="p-2 rounded bg-slate-900/60 border border-slate-800/80 text-[11px] text-slate-400 italic">
                      Question: "{item.question_text}"
                    </div>

                    {item.suggested_profile_destination && (
                      <div className="flex items-center justify-between pt-1 text-[11px] text-cyan-400">
                        <span>Profile Target: {item.suggested_profile_destination}</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 text-[11px] text-cyan-400 hover:text-cyan-200 p-0"
                          onClick={() => onNavigateTab('studio')}
                        >
                          Add to Profile <ArrowRight className="w-3 h-3 ml-0.5" />
                        </Button>
                      </div>
                    )}
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Contradiction & Conflict Tracker */}
        <div className="space-y-4">
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-3 flex flex-row items-center justify-between">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <CardTitle className="text-xs font-semibold text-slate-200">
                    Contradictions & Conflicts ({conflicts.length})
                  </CardTitle>
                </div>
                <p className="text-[11px] text-slate-400">
                  Discrepancies between profile records and generated/manual claims.
                </p>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {conflicts.length === 0 ? (
                <div className="py-8 text-center text-xs text-slate-500 space-y-1">
                  <ShieldCheck className="w-6 h-6 text-emerald-500 mx-auto" />
                  <p>Zero contradictions detected across profile and application documents.</p>
                </div>
              ) : (
                conflicts.map((conf) => (
                  <div
                    key={conf.id}
                    className="p-3 rounded-lg bg-amber-950/20 border border-amber-500/30 space-y-2 text-xs"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <span className="font-semibold text-amber-300">{conf.title}</span>
                      <Badge variant="neutral" className="bg-amber-950 text-amber-400 border-amber-700 text-[10px]">
                        Contradiction
                      </Badge>
                    </div>

                    <p className="text-[11px] text-slate-300 leading-relaxed">{conf.description}</p>

                    <div className="grid grid-cols-2 gap-2 text-[10px] font-mono p-2 rounded bg-slate-950/80 border border-slate-800">
                      <div>
                        <span className="text-slate-500 block">{conf.source_a}</span>
                        <span className="text-slate-200">{conf.claim_a_value}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">{conf.source_b}</span>
                        <span className="text-slate-200">{conf.claim_b_value}</span>
                      </div>
                    </div>

                    {conf.resolution_note && (
                      <p className="text-[11px] text-cyan-300 italic pt-1">
                        Recommendation: {conf.resolution_note}
                      </p>
                    )}
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
