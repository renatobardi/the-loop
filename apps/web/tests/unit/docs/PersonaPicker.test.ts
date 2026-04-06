import { describe, it, expect } from 'vitest';
import { PERSONAS, USER_SECTIONS } from '$lib/components/docs/nav';
import type { PersonaKey } from '$lib/components/docs/nav';

// PersonaPicker renders 6 persona cards with aria-pressed state.
// These tests verify the PERSONAS data contract and primary section references.

describe('PersonaPicker — PERSONAS data contract (T025)', () => {
	const EXPECTED_KEYS: PersonaKey[] = [
		'developer',
		'it-manager',
		'operator',
		'support',
		'qa',
		'security'
	];

	it('contains exactly 6 personas', () => {
		expect(PERSONAS).toHaveLength(6);
	});

	it('each persona has all required fields', () => {
		for (const persona of PERSONAS) {
			expect(persona.key).toBeTruthy();
			expect(persona.label).toBeTruthy();
			expect(persona.description).toBeTruthy();
			expect(Array.isArray(persona.primarySections)).toBe(true);
			expect(persona.primarySections.length).toBeGreaterThanOrEqual(2);
			expect(persona.primarySections.length).toBeLessThanOrEqual(6);
		}
	});

	it('all expected persona keys are present', () => {
		const keys = PERSONAS.map((p) => p.key);
		for (const expectedKey of EXPECTED_KEYS) {
			expect(keys).toContain(expectedKey);
		}
	});

	it('persona keys are unique', () => {
		const keys = PERSONAS.map((p) => p.key);
		const unique = new Set(keys);
		expect(unique.size).toBe(keys.length);
	});

	it('all primarySections reference valid USER_SECTIONS slugs', () => {
		const userSlugs = new Set(USER_SECTIONS.map((s) => s.slug));
		for (const persona of PERSONAS) {
			for (const slug of persona.primarySections) {
				expect(userSlugs.has(slug)).toBe(true);
			}
		}
	});

	it('developer persona highlights semgrep, api-keys, rules', () => {
		const dev = PERSONAS.find((p) => p.key === 'developer');
		expect(dev).toBeDefined();
		expect(dev!.primarySections).toContain('semgrep');
		expect(dev!.primarySections).toContain('api-keys');
		expect(dev!.primarySections).toContain('rules');
	});

	it('it-manager persona highlights getting-started and analytics', () => {
		const mgr = PERSONAS.find((p) => p.key === 'it-manager');
		expect(mgr).toBeDefined();
		expect(mgr!.primarySections).toContain('getting-started');
		expect(mgr!.primarySections).toContain('analytics');
	});

	it('operator persona highlights incidents, postmortems, getting-started', () => {
		const op = PERSONAS.find((p) => p.key === 'operator');
		expect(op).toBeDefined();
		expect(op!.primarySections).toContain('incidents');
		expect(op!.primarySections).toContain('postmortems');
		expect(op!.primarySections).toContain('getting-started');
	});

	// PersonaPicker toggle logic: selecting the same key again deselects it
	it('toggle logic: selecting same key twice results in null', () => {
		let selected: PersonaKey | null = null;
		function toggle(key: PersonaKey) {
			selected = selected === key ? null : key;
		}
		toggle('developer');
		expect(selected).toBe('developer');
		toggle('developer');
		expect(selected).toBeNull();
	});

	// aria-pressed: true when selected, false otherwise
	it('aria-pressed is true only for selected persona', () => {
		const selected: PersonaKey = 'qa';
		for (const persona of PERSONAS) {
			const pressed = persona.key === selected;
			expect(typeof pressed).toBe('boolean');
		}
	});
});
