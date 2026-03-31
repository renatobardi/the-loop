import { describe, it, expect } from 'vitest';
import { WaitlistSchema, VALID_SOURCES } from '$lib/server/schemas';

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

  it('accepts valid source "hero"', () => {
    const result = WaitlistSchema.safeParse({ email: 'test@example.com', source: 'hero' });
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.source).toBe('hero');
    }
  });

  it('accepts valid source "cta-bottom"', () => {
    const result = WaitlistSchema.safeParse({ email: 'test@example.com', source: 'cta-bottom' });
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.source).toBe('cta-bottom');
    }
  });

  it('defaults missing source to "unknown"', () => {
    const result = WaitlistSchema.safeParse({ email: 'test@example.com' });
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.source).toBe('unknown');
    }
  });

  it('defaults invalid source to "unknown"', () => {
    const result = WaitlistSchema.safeParse({ email: 'test@example.com', source: 'tampered' });
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.source).toBe('unknown');
    }
  });

  it('exports VALID_SOURCES constant', () => {
    expect(VALID_SOURCES).toContain('hero');
    expect(VALID_SOURCES).toContain('cta-bottom');
    expect(VALID_SOURCES).toHaveLength(2);
  });
});
