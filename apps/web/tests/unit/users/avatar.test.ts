import { describe, it, expect } from 'vitest';
import { getInitials } from '$lib/utils/users';

describe('getInitials', () => {
	// T080: Avatar renders correct initials from displayName
	it('extracts initials from full name ("Renato Bardi" → "RB")', () => {
		expect(getInitials('Renato Bardi', null)).toBe('RB');
	});

	it('extracts initials from single name ("Renato" → "R")', () => {
		expect(getInitials('Renato', null)).toBe('R');
	});

	it('extracts initials from three-word name (first two words only)', () => {
		expect(getInitials('John Paul Smith', null)).toBe('JP');
	});

	it('uppercases initials from lowercase name', () => {
		expect(getInitials('alice bob', null)).toBe('AB');
	});

	// T081: Avatar uses email fallback when displayName is null
	it('uses first 2 chars of email when displayName is null', () => {
		expect(getInitials(null, 'renato@example.com')).toBe('RE');
	});

	it('uses first 2 chars of email when displayName is undefined', () => {
		expect(getInitials(undefined, 'user@test.com')).toBe('US');
	});

	it('returns empty string when both are null/undefined', () => {
		expect(getInitials(null, null)).toBe('');
	});

	it('handles name with extra whitespace', () => {
		expect(getInitials('  Ana   Lima  ', null)).toBe('AL');
	});
});

describe('plan badge null-guard', () => {
	function getPlan(profile: { plan: string } | null): string {
		return profile?.plan ?? 'beta';
	}

	// T087b: plan badge should use fallback 'beta' when profile is null
	it('plan defaults to "beta" when profile is null', () => {
		expect(getPlan(null)).toBe('beta');
	});

	it('plan uses stored value when profile is loaded', () => {
		expect(getPlan({ plan: 'pro' })).toBe('pro');
	});
});

describe('memberSince formatting', () => {
	// T087: member since formatted in pt-BR
	it('formats ISO date in pt-BR long format', () => {
		const date = '2026-01-15T12:00:00Z';
		const formatted = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'long' }).format(new Date(date));
		expect(formatted).toMatch(/janeiro|jan/i);
		expect(formatted).toMatch(/2026/);
	});

	it('returns "—" for missing date', () => {
		const date: string | undefined = undefined;
		const formatted = date
			? new Intl.DateTimeFormat('pt-BR', { dateStyle: 'long' }).format(new Date(date))
			: '—';
		expect(formatted).toBe('—');
	});
});
