/**
 * AUTONOM Design System Tokens (TypeScript Constants)
 */

export const PALETTE = {
  bgApp: '#0B1220',
  surfacePrimary: '#0F1828',
  surfaceSecondary: '#121E30',
  surfaceElevated: '#1B2B42',
  surfaceHover: '#1E314D',
  surfaceSelected: '#1E3A5F',
  surfaceDisabled: '#0E1522',

  textPrimary: '#F0F5FC',
  textSecondary: '#A7B6CB',
  textMuted: '#8495AC',
  textDisabled: '#54657D',

  primary: '#338BDF',
  primaryHover: '#4A9AED',
  primaryActive: '#2270BD',

  cyan: '#51C8E8',
  cyanHover: '#38B8DB',

  borderDefault: '#2A3A52',
  borderFocused: '#4A6388',

  status: {
    success: '#37B89A',
    warning: '#E3AA54',
    error: '#E36E78',
    info: '#51C8E8',
    inactive: '#64748B',
  },
} as const;

export const SPACING_SCALE = [4, 8, 12, 16, 20, 24, 32, 40] as const;

export type DensityMode = 'comfortable' | 'compact';

export const DENSITY_CONFIG: Record<
  DensityMode,
  {
    controlHeight: string;
    cardPadding: string;
    tableRowHeight: string;
    gap: string;
  }
> = {
  comfortable: {
    controlHeight: 'h-9',
    cardPadding: 'p-4',
    tableRowHeight: 'h-10',
    gap: 'gap-4',
  },
  compact: {
    controlHeight: 'h-7',
    cardPadding: 'p-3',
    tableRowHeight: 'h-8',
    gap: 'gap-2.5',
  },
};
