import React, { createContext, useContext, useEffect, useState } from 'react';
import type { DensityMode } from './tokens';

interface ThemeContextValue {
  density: DensityMode;
  setDensity: (mode: DensityMode) => void;
  toggleDensity: () => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [density, setDensityState] = useState<DensityMode>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('autonom_density');
      if (saved === 'compact' || saved === 'comfortable') return saved;
    }
    return 'comfortable';
  });

  const setDensity = (mode: DensityMode) => {
    setDensityState(mode);
    if (typeof window !== 'undefined') {
      localStorage.setItem('autonom_density', mode);
      document.documentElement.setAttribute('data-density', mode);
    }
  };

  const toggleDensity = () => {
    setDensity(density === 'comfortable' ? 'compact' : 'comfortable');
  };

  useEffect(() => {
    document.documentElement.setAttribute('data-density', density);
  }, [density]);

  return (
    <ThemeContext.Provider value={{ density, setDensity, toggleDensity }}>
      {children}
    </ThemeContext.Provider>
  );
};

export function useDensity(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    return {
      density: 'comfortable',
      setDensity: () => {},
      toggleDensity: () => {},
    };
  }
  return context;
}

