import '@testing-library/jest-dom';

// Polyfill ResizeObserver for jsdom test environment (used by Recharts and Radix UI)
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};
