import React from 'react';
import { Layers, Sparkles } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface SettingsUnavailableStateProps {
  title: string;
  roadmapStage: string;
  description: string;
  configurationNotes?: string;
}

export const SettingsUnavailableState: React.FC<SettingsUnavailableStateProps> = ({
  title,
  roadmapStage,
  description,
  configurationNotes,
}) => {
  return (
    <div className="flex flex-col gap-2 p-3.5 bg-secondary/30 border border-primary/20 rounded-lg text-xs">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 font-medium text-foreground">
          <Sparkles className="h-4 w-4 text-cyan" />
          <span>{title}</span>
        </div>
        <Badge variant="outline" className="border-cyan/40 text-cyan text-[10px] px-2 py-0">
          Planned — {roadmapStage}
        </Badge>
      </div>
      <p className="text-muted-foreground leading-relaxed">{description}</p>
      {configurationNotes && (
        <div className="flex items-start gap-1.5 mt-1 pt-1.5 border-t border-border/30 text-[11px] text-muted-foreground/80">
          <Layers className="h-3.5 w-3.5 text-primary shrink-0 mt-0.5" />
          <span>{configurationNotes}</span>
        </div>
      )}
    </div>
  );
};
