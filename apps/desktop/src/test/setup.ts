import '@testing-library/jest-dom';

// Polyfill ResizeObserver for jsdom test environment (used by Recharts and Radix UI)
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Polyfill EventSource for jsdom test environment (used by SSE real-time stream)
class MockEventSource {
  url: string;
  onopen: (() => void) | null = null;
  onmessage: ((ev: any) => void) | null = null;
  onerror: ((err: any) => void) | null = null;
  readyState = 1;
  addEventListener() {}
  removeEventListener() {}
  close() {}
  constructor(url: string) {
    this.url = url;
  }
}
(global as any).EventSource = MockEventSource;
