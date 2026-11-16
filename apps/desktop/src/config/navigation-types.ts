import * as React from 'react';

export type NavigationAvailability = 'implemented' | 'development' | 'planned';

export type NavigationGroupId = 'main' | 'recruitment' | 'workspace' | 'management' | 'development';

export interface NavigationChildItem {
  id: string;
  title: string;
  path: string;
  availability: NavigationAvailability;
  roadmapStage?: string;
  description?: string;
  badge?: string;
  requiredPermission?: string;
}

export interface NavigationItem {
  id: string;
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  path: string;
  group: NavigationGroupId;
  availability: NavigationAvailability;
  roadmapStage?: string;
  description?: string;
  badge?: string;
  shortcut?: string;
  requiredPermission?: string;
  children?: NavigationChildItem[];
}

export interface NavigationGroup {
  id: NavigationGroupId;
  title: string;
  order: number;
  items: NavigationItem[];
}

export interface BreadcrumbItem {
  label: string;
  path?: string;
  isCurrent?: boolean;
}
