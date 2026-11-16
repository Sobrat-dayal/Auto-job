import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { AlertTriangle } from 'lucide-react';

interface SettingsConfirmationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'destructive' | 'primary';
  isConfirming?: boolean;
  onConfirm: () => void;
}

export const SettingsConfirmationDialog: React.FC<SettingsConfirmationDialogProps> = ({
  open,
  onOpenChange,
  title,
  description,
  confirmLabel = 'Confirm Action',
  cancelLabel = 'Cancel',
  variant = 'destructive',
  isConfirming = false,
  onConfirm,
}) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md bg-card border-border shadow-xl">
        <DialogHeader>
          <div className="flex items-center gap-2.5">
            {variant === 'destructive' && (
              <div className="h-8 w-8 rounded-full bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400 shrink-0">
                <AlertTriangle className="h-4 w-4" />
              </div>
            )}
            <DialogTitle className="text-sm font-semibold text-foreground">{title}</DialogTitle>
          </div>
          <DialogDescription className="text-xs text-muted-foreground pt-2 leading-relaxed">
            {description}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="mt-4 gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onOpenChange(false)}
            disabled={isConfirming}
            className="text-xs h-8"
          >
            {cancelLabel}
          </Button>
          <Button
            variant={variant === 'destructive' ? 'destructive' : 'primary'}
            size="sm"
            onClick={onConfirm}
            disabled={isConfirming}
            className="text-xs h-8"
          >
            {isConfirming ? 'Processing...' : confirmLabel}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
