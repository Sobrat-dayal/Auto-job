import React from 'react';
import {
  Sliders,
  Palette,
  Sparkles,
  Bot,
  Zap,
  ShieldCheck,
  MousePointerClick,
  Boxes,
  Briefcase,
  Database,
  Bell,
  Monitor,
  Lock,
  Activity,
  Info,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export interface SettingsCategoryItem {
  id: string;
  label: string;
  icon: React.ElementType;
  badge?: string;
  badgeVariant?: 'primary' | 'cyan' | 'warning' | 'outline' | 'neutral';
  isDirty?: boolean;
}

export const SETTINGS_CATEGORIES: SettingsCategoryItem[] = [
  { id: 'general', label: 'General', icon: Sliders },
  { id: 'appearance', label: 'Appearance', icon: Palette },
  {
    id: 'ai',
    label: 'AI Providers & Models',
    icon: Sparkles,
    badge: 'Stage 11',
    badgeVariant: 'outline',
  },
  {
    id: 'agents',
    label: 'Agent Preferences',
    icon: Bot,
    badge: 'Stage 12',
    badgeVariant: 'outline',
  },
  { id: 'automation', label: 'Automation & Tasks', icon: Zap },
  { id: 'permissions', label: 'Permissions & Autonomy', icon: ShieldCheck },
  {
    id: 'computer',
    label: 'Computer Control',
    icon: MousePointerClick,
    badge: 'Stage 16',
    badgeVariant: 'outline',
  },
  { id: 'integrations', label: 'Connected Services & MCP', icon: Boxes },
  { id: 'recruitment', label: 'Recruitment Preferences', icon: Briefcase },
  { id: 'storage', label: 'Storage & Data', icon: Database },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'desktop', label: 'Desktop & Startup', icon: Monitor },
  { id: 'security', label: 'Security & Privacy', icon: Lock },
  { id: 'diagnostics', label: 'Diagnostics & Health', icon: Activity },
  { id: 'about', label: 'About & Updates', icon: Info },
];

interface SettingsNavigationProps {
  selectedCategoryId: string;
  onSelectCategory: (id: string) => void;
  dirtyCategories?: string[];
  searchFilter?: string;
}

export const SettingsNavigation: React.FC<SettingsNavigationProps> = ({
  selectedCategoryId,
  onSelectCategory,
  dirtyCategories = [],
  searchFilter = '',
}) => {
  const filteredCategories = SETTINGS_CATEGORIES.filter((cat) =>
    cat.label.toLowerCase().includes(searchFilter.toLowerCase())
  );

  return (
    <nav className="space-y-0.5 p-2" aria-label="Settings Categories">
      {filteredCategories.map((cat) => {
        const Icon = cat.icon;
        const isSelected = selectedCategoryId === cat.id;
        const isDirty = dirtyCategories.includes(cat.id);

        return (
          <button
            key={cat.id}
            onClick={() => onSelectCategory(cat.id)}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-colors ${
              isSelected
                ? 'bg-primary/20 text-primary border border-primary/40 shadow-xs'
                : 'text-muted-foreground hover:bg-muted/40 hover:text-foreground'
            }`}
            aria-current={isSelected ? 'page' : undefined}
          >
            <div className="flex items-center gap-2.5 min-w-0">
              <Icon
                className={`h-4 w-4 shrink-0 ${isSelected ? 'text-primary' : 'text-muted-foreground'}`}
              />
              <span className="truncate">{cat.label}</span>
            </div>

            <div className="flex items-center gap-1.5 shrink-0">
              {isDirty && (
                <span
                  className="h-1.5 w-1.5 rounded-full bg-amber-400"
                  title="Unsaved changes in this category"
                />
              )}
              {cat.badge && (
                <Badge
                  variant={cat.badgeVariant || 'outline'}
                  className="text-[9px] px-1.5 py-0 font-mono tracking-tighter"
                >
                  {cat.badge}
                </Badge>
              )}
            </div>
          </button>
        );
      })}
    </nav>
  );
};
