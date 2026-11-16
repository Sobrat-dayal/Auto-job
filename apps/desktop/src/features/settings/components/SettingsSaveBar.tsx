import React from 'react';
import { Button } from '@/components/ui/button';
import { Check, RefreshCw, AlertCircle } from 'lucide-react';

interface SettingsSaveBarProps {
  isDirty: boolean;
  isSaving: boolean;
  saveSuccess?: boolean;
  errorMessage?: string | null;
  onSave: () => void;
  onReset: () => void;
  className?: string;
}

export const SettingsSaveBar: React.FC<SettingsSaveBarProps> = ({
  isDirty,
  isSaving,
  saveSuccess,
  errorMessage,
  onSave,
  onReset,
  className = '',
}) => {
  if (!isDirty && !saveSuccess && !errorMessage) {
    return null;
  }

  return (
    <div
      className={`sticky bottom-4 z-20 flex items-center justify-between gap-4 p-3.5 bg-card/95 backdrop-blur-md border border-primary/30 rounded-lg shadow-lg animate-in fade-in slide-in-from-bottom-2 duration-200 ${className}`}
      role="region"
      aria-label="Save Settings Bar"
    >
      <div className="flex items-center gap-2">
        {saveSuccess ? (
          <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
            <Check className="h-4 w-4" />
            <span>Settings saved successfully to persistent storage.</span>
          </div>
        ) : errorMessage ? (
          <div className="flex items-center gap-1.5 text-xs text-rose-400 font-medium">
            <AlertCircle className="h-4 w-4" />
            <span>{errorMessage}</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-xs text-amber-300 font-medium">
            <span className="h-2 w-2 rounded-full bg-amber-400 animate-pulse" />
            <span>You have unsaved changes.</span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={onReset}
          disabled={isSaving || !isDirty}
          className="text-xs h-7 px-3"
        >
          Discard Changes
        </Button>
        <Button
          variant="primary"
          size="sm"
          onClick={onSave}
          disabled={isSaving || !isDirty}
          className="text-xs h-7 px-3 gap-1.5"
        >
          {isSaving ? (
            <>
              <RefreshCw className="h-3 w-3 animate-spin" />
              <span>Saving...</span>
            </>
          ) : (
            <span>Save Preferences</span>
          )}
        </Button>
      </div>
    </div>
  );
};
