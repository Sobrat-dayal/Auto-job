import React from 'react';
import { Badge } from '@/components/ui/badge';

interface SettingsFieldProps {
  label: string;
  description?: string;
  children: React.ReactNode;
  requiresRestart?: boolean;
  roadmapStage?: string;
  className?: string;
  vertical?: boolean;
}

export const SettingsField: React.FC<SettingsFieldProps> = ({
  label,
  description,
  children,
  requiresRestart,
  roadmapStage,
  className = '',
  vertical = false,
}) => {
  return (
    <div
      className={`flex ${
        vertical
          ? 'flex-col items-start gap-2'
          : 'flex-col sm:flex-row sm:items-center justify-between gap-4'
      } py-2 border-b border-border/20 last:border-b-0 ${className}`}
    >
      <div className="space-y-0.5 max-w-xl">
        <div className="flex items-center gap-2">
          <label className="text-xs font-medium text-foreground tracking-wide">{label}</label>
          {requiresRestart && (
            <Badge variant="warning" className="text-[10px] px-1.5 py-0">
              Restart Required
            </Badge>
          )}
          {roadmapStage && (
            <Badge variant="outline" className="text-[10px] px-1.5 py-0 border-cyan/40 text-cyan">
              {roadmapStage}
            </Badge>
          )}
        </div>
        {description && (
          <p className="text-[11px] text-muted-foreground leading-relaxed">{description}</p>
        )}
      </div>
      <div className="flex-shrink-0 flex items-center gap-2">{children}</div>
    </div>
  );
};
