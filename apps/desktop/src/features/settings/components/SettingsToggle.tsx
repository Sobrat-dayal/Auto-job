import React from 'react';
import { Switch } from '@/components/ui/switch';

interface SettingsToggleProps {
  id?: string;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  disabled?: boolean;
  activeLabel?: string;
  inactiveLabel?: string;
  ariaLabel?: string;
}

export const SettingsToggle: React.FC<SettingsToggleProps> = ({
  id,
  checked,
  onCheckedChange,
  disabled = false,
  activeLabel = 'Enabled',
  inactiveLabel = 'Disabled',
  ariaLabel,
}) => {
  return (
    <div className="flex items-center gap-2">
      <Switch
        id={id}
        checked={checked}
        onCheckedChange={onCheckedChange}
        disabled={disabled}
        aria-label={ariaLabel || id}
      />
      <span className="text-[11px] font-mono text-muted-foreground w-14">
        {checked ? activeLabel : inactiveLabel}
      </span>
    </div>
  );
};
