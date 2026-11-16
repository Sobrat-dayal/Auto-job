import * as React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Info, X } from 'lucide-react';
import { cn } from '@/lib/utils';

export type ToastType = 'success' | 'warning' | 'error' | 'info';

export interface ToastItem {
  id: string;
  type: ToastType;
  title?: string;
  message: string;
  duration?: number;
}

interface ToastContextValue {
  toasts: ToastItem[];
  addToast: (toast: Omit<ToastItem, 'id'>) => void;
  removeToast: (id: string) => void;
  success: (message: string, title?: string) => void;
  error: (message: string, title?: string) => void;
  warning: (message: string, title?: string) => void;
  info: (message: string, title?: string) => void;
}

const ToastContext = React.createContext<ToastContextValue | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<ToastItem[]>([]);

  const removeToast = React.useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = React.useCallback(
    (toast: Omit<ToastItem, 'id'>) => {
      const id = `toast-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;
      const duration = toast.duration ?? 4000;

      setToasts((prev) => [...prev.slice(-4), { ...toast, id }]);

      if (duration > 0) {
        setTimeout(() => {
          removeToast(id);
        }, duration);
      }
    },
    [removeToast]
  );

  const success = React.useCallback(
    (message: string, title?: string) => addToast({ type: 'success', message, title }),
    [addToast]
  );
  const error = React.useCallback(
    (message: string, title?: string) =>
      addToast({ type: 'error', message, title, duration: 6000 }),
    [addToast]
  );
  const warning = React.useCallback(
    (message: string, title?: string) => addToast({ type: 'warning', message, title }),
    [addToast]
  );
  const info = React.useCallback(
    (message: string, title?: string) => addToast({ type: 'info', message, title }),
    [addToast]
  );

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast, success, error, warning, info }}>
      {children}
      {/* Toast Viewport */}
      <div
        role="region"
        aria-label="Notifications"
        className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none"
      >
        {toasts.map((t) => (
          <div
            key={t.id}
            role="status"
            aria-live={t.type === 'error' ? 'assertive' : 'polite'}
            className={cn(
              'pointer-events-auto flex items-start gap-3 p-3.5 rounded-lg border shadow-dialog transition-all duration-200 animate-in fade-in-50 slide-in-from-bottom-2',
              t.type === 'success' &&
                'bg-surface-elevated border-status-success/40 text-foreground',
              t.type === 'error' && 'bg-surface-elevated border-status-error/40 text-foreground',
              t.type === 'warning' &&
                'bg-surface-elevated border-status-warning/40 text-foreground',
              t.type === 'info' && 'bg-surface-elevated border-cyan/40 text-foreground'
            )}
          >
            <div className="shrink-0 mt-0.5">
              {t.type === 'success' && <CheckCircle2 className="w-4 h-4 text-status-success" />}
              {t.type === 'error' && <AlertCircle className="w-4 h-4 text-status-error" />}
              {t.type === 'warning' && <AlertTriangle className="w-4 h-4 text-status-warning" />}
              {t.type === 'info' && <Info className="w-4 h-4 text-cyan" />}
            </div>

            <div className="flex-1 min-w-0">
              {t.title && (
                <h5 className="text-xs font-semibold text-foreground mb-0.5">{t.title}</h5>
              )}
              <p className="text-xs text-foreground-secondary leading-snug break-words">
                {t.message}
              </p>
            </div>

            <button
              onClick={() => removeToast(t.id)}
              className="shrink-0 p-1 rounded-sm text-foreground-muted hover:text-foreground hover:bg-surface-hover focus:outline-none focus:ring-1 focus:ring-primary"
              aria-label="Dismiss notification"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const context = React.useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}
