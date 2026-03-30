import { describe, it, expect } from 'vitest';
import { WaitlistSchema } from '$lib/server/schemas';

describe('Waitlist Form Validation', () => {
	it('accepts a valid email and normalizes it', () => {
		const result = WaitlistSchema.safeParse({ email: 'User@Example.COM' });
		expect(result.success).toBe(true);
		if (result.success) {
			expect(result.data.email).toBe('user@example.com');
		}
	});

	it('trims whitespace from email', () => {
		const result = WaitlistSchema.safeParse({ email: '  test@test.com  ' });
		expect(result.success).toBe(true);
		if (result.success) {
			expect(result.data.email).toBe('test@test.com');
		}
	});

	it('rejects missing email', () => {
		const result = WaitlistSchema.safeParse({});
		expect(result.success).toBe(false);
	});

	it('rejects empty string email', () => {
		const result = WaitlistSchema.safeParse({ email: '' });
		expect(result.success).toBe(false);
	});

	it('rejects invalid email format', () => {
		const result = WaitlistSchema.safeParse({ email: 'not-an-email' });
		expect(result.success).toBe(false);
	});

	it('rejects email without domain', () => {
		const result = WaitlistSchema.safeParse({ email: 'user@' });
		expect(result.success).toBe(false);
	});

	it('rejects email over 254 characters', () => {
		const longEmail = 'a'.repeat(250) + '@b.co';
		const result = WaitlistSchema.safeParse({ email: longEmail });
		expect(result.success).toBe(false);
	});

	it('accepts email with subdomain', () => {
		const result = WaitlistSchema.safeParse({ email: 'user@mail.example.com' });
		expect(result.success).toBe(true);
	});

	it('accepts email with plus addressing', () => {
		const result = WaitlistSchema.safeParse({ email: 'user+tag@example.com' });
		expect(result.success).toBe(true);
		if (result.success) {
			expect(result.data.email).toBe('user+tag@example.com');
		}
	});
});
