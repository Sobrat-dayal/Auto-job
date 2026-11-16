import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface SettingsSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  headerAction?: React.ReactNode;
  className?: string;
}

export const SettingsSection: React.FC<SettingsSectionProps> = ({
  title,
  description,
  children,
  headerAction,
  className = '',
}) => {
  return (
    <Card className={`border-border bg-card/60 backdrop-blur-sm shadow-sm ${className}`}>
      <CardHeader className="p-4 pb-3 border-b border-border/40">
        <div className="flex items-center justify-between gap-4">
          <div>
            <CardTitle className="text-sm font-semibold text-foreground tracking-tight">
              {title}
            </CardTitle>
            {description && (
              <CardDescription className="text-xs text-muted-foreground mt-0.5">
                {description}
              </CardDescription>
            )}
          </div>
          {headerAction && <div className="flex items-center gap-2">{headerAction}</div>}
        </div>
      </CardHeader>
      <CardContent className="p-4 space-y-4">{children}</CardContent>
    </Card>
  );
};
