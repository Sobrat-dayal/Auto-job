import * as React from 'react';
import { useLocation, NavLink } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import { getBreadcrumbsForPath } from '@/config/navigation';

export const NavigationBreadcrumbs: React.FC = () => {
  const location = useLocation();
  const breadcrumbs = getBreadcrumbsForPath(location.pathname);

  if (breadcrumbs.length === 0) return null;

  return (
    <nav aria-label="Breadcrumb" className="flex items-center min-w-0 select-none">
      <ol className="flex items-center flex-wrap gap-1 text-xs">
        {breadcrumbs.map((crumb, idx) => {
          const isLast = idx === breadcrumbs.length - 1;

          return (
            <li key={`${crumb.label}-${idx}`} className="flex items-center gap-1 min-w-0">
              {idx > 0 && (
                <ChevronRight
                  className="h-3 w-3 text-foreground-muted/60 shrink-0"
                  aria-hidden="true"
                />
              )}

              {crumb.path && !isLast ? (
                <NavLink
                  to={crumb.path}
                  className="text-foreground-secondary hover:text-foreground transition-colors truncate max-w-[140px]"
                >
                  {crumb.label}
                </NavLink>
              ) : (
                <span
                  aria-current={isLast ? 'page' : undefined}
                  className={`truncate max-w-[180px] ${
                    isLast ? 'font-medium text-foreground' : 'text-foreground-muted'
                  }`}
                >
                  {crumb.label}
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};
