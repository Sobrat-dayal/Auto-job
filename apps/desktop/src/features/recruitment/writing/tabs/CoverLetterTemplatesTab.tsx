/**
 * Stage 24: Cover Letter Templates Gallery Tab.
 * Displays the 6 core ATS-compatible styling templates with typography rules and recommended roles.
 */

import * as React from 'react';
import {
  Check,
  FileText,
  ShieldCheck,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type {
  CoverLetterDocument,
  CoverLetterTemplateDefinition,
} from '@autonom/shared-types';

interface CoverLetterTemplatesTabProps {
  templates: CoverLetterTemplateDefinition[];
  currentLetter: CoverLetterDocument | null;
  onApplyTemplate: (templateId: string) => Promise<void>;
}

export const CoverLetterTemplatesTab: React.FC<CoverLetterTemplatesTabProps> = ({
  templates,
  currentLetter,
  onApplyTemplate,
}) => {
  const [isApplying, setIsApplying] = React.useState<boolean>(false);

  const handleApply = async (tplId: string) => {
    setIsApplying(true);
    try {
      await onApplyTemplate(tplId);
    } finally {
      setIsApplying(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h3 className="text-sm font-semibold text-slate-200">
          Professional Cover Letter Templates
        </h3>
        <p className="text-xs text-slate-400">
          Standardized single-column ATS layouts verified for round-trip machine readability across Word and PDF.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.map((tpl) => {
          const isCurrent = currentLetter?.template_id === tpl.id;

          return (
            <Card
              key={tpl.id}
              className={`bg-slate-900/60 border transition-all ${
                isCurrent
                  ? 'border-cyan-500/80 ring-1 ring-cyan-500/20'
                  : 'border-slate-800 hover:border-slate-700'
              }`}
            >
              <CardHeader className="pb-3 space-y-1.5">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-cyan-400" />
                    <CardTitle className="text-xs font-semibold text-slate-200">
                      {tpl.name}
                    </CardTitle>
                  </div>
                  {isCurrent && (
                    <Badge variant="neutral" className="bg-cyan-950/60 text-cyan-400 border-cyan-800 text-[10px]">
                      Active
                    </Badge>
                  )}
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  {tpl.description}
                </p>
              </CardHeader>

              <CardContent className="space-y-3 pt-1 text-xs">
                {/* Visual Spec Matrix */}
                <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800 text-[11px] space-y-1 font-mono text-slate-400">
                  <div className="flex items-center justify-between">
                    <span>Category:</span>
                    <span className="text-slate-200">{tpl.category}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Primary Font:</span>
                    <span className="text-slate-200">{tpl.primary_font}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Heading Font:</span>
                    <span className="text-slate-200">{tpl.heading_font}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Base Size:</span>
                    <span className="text-slate-200">{tpl.base_font_size_pt}pt</span>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-1">
                  <div className="flex items-center gap-1 text-[11px] text-emerald-400">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    ATS Safe
                  </div>

                  <Button
                    size="sm"
                    variant={isCurrent ? 'outline' : 'cyan'}
                    className={`h-7 text-xs ${
                      isCurrent
                        ? 'border-cyan-500/40 text-cyan-400'
                        : 'bg-cyan-600 hover:bg-cyan-500 text-white'
                    }`}
                    onClick={() => handleApply(tpl.id)}
                    disabled={isApplying || isCurrent}
                  >
                    {isCurrent ? (
                      <span className="flex items-center gap-1">
                        <Check className="w-3 h-3" /> Selected
                      </span>
                    ) : (
                      'Apply Template'
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
