import React from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface SettingsRestartNoticeProps {
  onRestartBackend?: () => void;
  isRestarting?: boolean;
  message?: string;
}

export const SettingsRestartNotice: React.FC<SettingsRestartNoticeProps> = ({
  onRestartBackend,
  isRestarting = false,
  message = 'Changes to worker concurrency, background daemon, or hardware allocation require restarting the backend sidecar service.',
}) => {
  return (
    <div className="flex items-center justify-between gap-3 p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg text-amber-200">
      <div className="flex items-center gap-2.5">
        <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0" />
        <span className="text-xs leading-relaxed">{message}</span>
      </div>
      {onRestartBackend && (
        <Button
          variant="outline"
          size="sm"
          onClick={onRestartBackend}
          disabled={isRestarting}
          className="h-7 text-xs border-amber-500/40 text-amber-300 hover:bg-amber-500/20 shrink-0 gap-1.5"
        >
          <RotateCcw className={`h-3 w-3 ${isRestarting ? 'animate-spin' : ''}`} />
          <span>Restart Backend</span>
        </Button>
      )}
    </div>
  );
};
