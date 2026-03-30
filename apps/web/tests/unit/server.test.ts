import { describe, it, expect } from 'vitest';
import { WaitlistSchema } from '$lib/server/schemas';

describe('WaitlistSchema', () => {
  it('validates a correct email', () => {
    const result = WaitlistSchema.safeParse({ email: 'test@example.com' });
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.email).toBe('test@example.com');
    }
  });

  it('trims and lowercases email', () => {
    const result = WaitlistSchema.safeParse({ email: '  Test@Example.COM  ' });
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.email).toBe('test@example.com');
    }
  });

  it('rejects invalid email', () => {
    const result = WaitlistSchema.safeParse({ email: 'not-an-email' });
    expect(result.success).toBe(false);
  });

  it('rejects empty email', () => {
    const result = WaitlistSchema.safeParse({ email: '' });
    expect(result.success).toBe(false);
  });

  it('rejects email over 254 chars', () => {
    const longEmail = 'a'.repeat(250) + '@b.co';
    const result = WaitlistSchema.safeParse({ email: longEmail });
    expect(result.success).toBe(false);
  });
});
