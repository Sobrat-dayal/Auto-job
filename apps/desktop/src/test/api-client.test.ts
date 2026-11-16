import { describe, it, expect } from 'vitest';
import { ApiClient } from '../lib/api-client';

describe('ApiClient', () => {
  it('initializes with default base URL', () => {
    const client = new ApiClient();
    expect(client.baseUrl).toBe('http://127.0.0.1:8765');
  });

  it('allows overriding base URL and timeout', () => {
    const client = new ApiClient({
      baseUrl: 'http://localhost:9000',
      timeoutMs: 1000,
    });
    expect(client.baseUrl).toBe('http://localhost:9000');
  });
});
