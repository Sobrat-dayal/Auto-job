import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { findNavigationByPath } from '../config/navigation';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';
import {
  Compass,
  ArrowRight,
  LayoutDashboard,
  Palette,
  Activity,
  Layers,
  Calendar,
  ShieldAlert,
} from 'lucide-react';

export const ModulePlaceholder: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const { item, child, group } = findNavigationByPath(location.pathname);

  const displayTitle = child?.title || item?.title || 'Planned Module';
  const displayDescription =
    child?.description ||
    item?.description ||
    'This capability is scheduled for implementation in upcoming stages of the AUTONOM 50-stage development roadmap.';
  const roadmapStage = child?.roadmapStage || item?.roadmapStage || 'Roadmap Phase';
  const availability = child?.availability || item?.availability || 'planned';
  const IconComponent = item?.icon || Compass;

  return (
    <div className="flex-1 p-6 max-w-6xl mx-auto space-y-6">
      {/* Top Banner Card */}
      <Card className="border-border-default/60 bg-bg-surface/80 shadow-md">
        <CardHeader className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent-primary/10 text-accent-primary border border-accent-primary/20">
                <IconComponent className="h-6 w-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <CardTitle className="text-2xl font-bold tracking-tight text-text-primary">
                    {displayTitle}
                  </CardTitle>
                  <Badge variant="outline" className="border-accent-primary/40 text-accent-primary">
                    {roadmapStage}
                  </Badge>
                  <Badge
                    variant={availability === 'development' ? 'warning' : 'neutral'}
                    className="capitalize"
                  >
                    {availability}
                  </Badge>
                </div>
                {group && (
                  <p className="text-xs uppercase tracking-wider text-text-muted mt-0.5">
                    Category: {group.title}
                  </p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/dashboard')}
                className="gap-1.5"
              >
                <LayoutDashboard className="h-4 w-4" />
                Command Center
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/design-system')}
                className="gap-1.5"
              >
                <Palette className="h-4 w-4" />
                Design System
              </Button>
            </div>
          </div>

          <CardDescription className="text-sm text-text-secondary leading-relaxed pt-2">
            {displayDescription}
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Roadmap & Architecture Information */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2 border-border-default/50 bg-bg-surface/40">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Layers className="h-5 w-5 text-accent-cyan" />
              <CardTitle className="text-base font-semibold text-text-primary">
                Roadmap Integration Notice
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4 text-sm text-text-secondary">
            <p>
              In accordance with the AUTONOM engineering discipline, this screen is an explicit
              architectural placeholder for <strong>{displayTitle}</strong>. AUTONOM strictly avoids
              fabricating mock data or deceptive UI states.
            </p>
            <div className="rounded-lg border border-border-default/60 bg-bg-canvas/60 p-4 space-y-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-text-muted uppercase tracking-wider">
                <Calendar className="h-4 w-4 text-accent-primary" />
                Target Stage
              </div>
              <p className="text-text-primary font-medium">
                {roadmapStage} — Automated Capabilities & Backend Integration
              </p>
              <p className="text-xs text-text-muted">
                Route:{' '}
                <code className="px-1.5 py-0.5 rounded bg-bg-surface text-accent-cyan font-mono text-xs">
                  {location.pathname}
                </code>
              </p>
            </div>

            {item?.children && item.children.length > 0 && (
              <div className="space-y-2 pt-2">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-text-muted">
                  Planned Sub-Capabilities ({item.children.length})
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {item.children.map((sub) => (
                    <div
                      key={sub.id}
                      onClick={() => navigate(sub.path)}
                      className="cursor-pointer group flex items-start justify-between p-3 rounded-lg border border-border-default/40 bg-bg-surface/60 hover:bg-bg-hover hover:border-accent-primary/40 transition-all"
                    >
                      <div className="space-y-1">
                        <div className="font-medium text-xs text-text-primary group-hover:text-accent-primary transition-colors">
                          {sub.title}
                        </div>
                        <div className="text-[11px] text-text-muted line-clamp-1">
                          {sub.description || sub.roadmapStage}
                        </div>
                      </div>
                      <ArrowRight className="h-3.5 w-3.5 text-text-muted group-hover:text-accent-primary group-hover:translate-x-0.5 transition-all mt-0.5 ml-2 shrink-0" />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Operational Diagnostics Quick-Link */}
        <Card className="border-border-default/50 bg-bg-surface/40 flex flex-col justify-between">
          <CardHeader>
            <div className="flex items-center gap-2">
              <ShieldAlert className="h-5 w-5 text-accent-primary" />
              <CardTitle className="text-base font-semibold text-text-primary">
                Supervision Status
              </CardTitle>
            </div>
            <CardDescription className="text-xs text-text-muted">
              Active engine and background workers are supervised from the operational diagnostics
              consoles.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Button
                variant="outline"
                className="w-full justify-start text-xs gap-2"
                onClick={() => navigate('/diagnostics')}
              >
                <Activity className="h-4 w-4 text-accent-primary" />
                Backend Telemetry & Tasks
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start text-xs gap-2"
                onClick={() => navigate('/desktop-diagnostics')}
              >
                <Layers className="h-4 w-4 text-accent-cyan" />
                Tauri Desktop Supervision
              </Button>
            </div>
            <div className="p-3 rounded-lg border border-border-default/40 bg-bg-canvas/50 text-[11px] text-text-muted">
              All backend endpoints, persistent storage engines, and worker managers implemented in
              Stages 01–05 remain fully operational.
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
