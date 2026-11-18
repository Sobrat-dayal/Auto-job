/**
 * Stage 23: Resume Template Gallery Tab.
 * Interactive catalog of the 6 core professional resume templates with typography and ATS notes.
 */

import * as React from 'react';
import {
  Check,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { ResumeDocument, ResumeTemplateDefinition } from '@autonom/shared-types';

interface TemplateGalleryTabProps {
  templates: ResumeTemplateDefinition[];
  currentResume: ResumeDocument | null;
  onApplyTemplate: (templateId: string) => Promise<void>;
  onNavigateTab?: (tabId: string) => void;
}

export const TemplateGalleryTab: React.FC<TemplateGalleryTabProps> = ({
  templates,
  currentResume,
  onApplyTemplate,
  onNavigateTab: _onNavigateTab,
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
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold text-slate-200">Standard Resume Template Collection</h2>
          <p className="text-xs text-slate-400">
            All templates produce real, selectable-text PDF and editable Word DOCX files with zero placeholder content.
          </p>
        </div>
        {currentResume && (
          <Badge variant="neutral" className="bg-cyan-950/60 text-cyan-400 border-cyan-800/60 font-mono text-xs">
            Current: {currentResume.template_id}
          </Badge>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((tpl) => {
          const isCurrent = currentResume?.template_id === tpl.id;
          return (
            <Card
              key={tpl.id}
              className={`bg-slate-900/60 border-slate-800 flex flex-col justify-between transition-all ${
                isCurrent ? 'ring-2 ring-cyan-500 border-cyan-800' : 'hover:border-slate-700'
              }`}
            >
              <div>
                {/* Visual Specimen Card */}
                <div className="h-36 bg-slate-950 border-b border-slate-800 p-4 flex flex-col justify-between rounded-t-lg relative overflow-hidden">
                  <div className="space-y-1.5">
                    <div className="w-24 h-3 rounded bg-slate-800" />
                    <div className="w-48 h-2 rounded bg-slate-800/60" />
                    <div className="w-full h-px bg-slate-800/80 my-2" />
                    <div className="space-y-1">
                      <div className="w-16 h-2 rounded bg-cyan-900/60" />
                      <div className="w-4/5 h-1.5 rounded bg-slate-800/40" />
                      <div className="w-3/5 h-1.5 rounded bg-slate-800/40" />
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
                    <span>{tpl.primary_font}</span>
                    <span>{tpl.base_font_size_pt}pt</span>
                  </div>
                </div>

                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base text-slate-200">{tpl.name}</CardTitle>
                    {tpl.ats_friendly && (
                      <Badge variant="neutral" className="bg-emerald-950/60 text-emerald-400 text-[10px] py-0">
                        ATS Safe
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed mt-1">{tpl.description}</p>
                </CardHeader>

                <CardContent className="space-y-3 pt-2 text-xs">
                  <div className="grid grid-cols-2 gap-2 p-2 rounded bg-slate-950/60 border border-slate-800/80 text-[11px] font-mono">
                    <div>
                      <span className="text-slate-500 block">Category</span>
                      <span className="text-slate-300">{tpl.category}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Margins</span>
                      <span className="text-slate-300">{tpl.margin_top_in}" all sides</span>
                    </div>
                  </div>
                </CardContent>
              </div>

              <div className="p-4 pt-0">
                {isCurrent ? (
                  <Button
                    size="sm"
                    variant="outline"
                    disabled
                    className="w-full border-cyan-800/60 text-cyan-400 bg-cyan-950/30"
                  >
                    <Check className="w-4 h-4 mr-1.5" />
                    Active Template
                  </Button>
                ) : (
                  <Button
                    size="sm"
                    variant="primary"
                    disabled={isApplying || !currentResume}
                    onClick={() => handleApply(tpl.id)}
                    className="w-full bg-cyan-600 hover:bg-cyan-500 text-white"
                  >
                    {isApplying ? 'Applying...' : 'Apply Template'}
                  </Button>
                )}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

