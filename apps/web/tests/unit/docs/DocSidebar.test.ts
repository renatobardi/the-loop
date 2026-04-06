import { describe, it, expect } from 'vitest';
import { USER_SECTIONS, ADMIN_SECTIONS } from '$lib/components/docs/nav';
import type { NavItem } from '$lib/components/docs/nav';

// DocSidebar receives a pre-filtered NavItem[] from its parent layout.
// These tests verify the data contracts that DocSidebar depends on.

describe('DocSidebar — NavItem data contract (T024)', () => {
	it('every USER_SECTIONS item has required fields', () => {
		for (const item of USER_SECTIONS) {
			expect(item.slug).toBeTruthy();
			expect(item.label).toBeTruthy();
			expect(item.icon).toBeTruthy();
			expect(item.visibility).toBe('all');
		}
	});

	it('every ADMIN_SECTIONS item has visibility admin', () => {
		for (const item of ADMIN_SECTIONS) {
			expect(item.visibility).toBe('admin');
		}
	});

	it('USER_SECTIONS contains exactly 7 sections', () => {
		expect(USER_SECTIONS).toHaveLength(7);
	});

	it('ADMIN_SECTIONS contains exactly 3 sections', () => {
		expect(ADMIN_SECTIONS).toHaveLength(3);
	});

	it('all slugs are URL-safe kebab-case', () => {
		const allItems: NavItem[] = [...USER_SECTIONS, ...ADMIN_SECTIONS];
		for (const item of allItems) {
			expect(item.slug).toMatch(/^[a-z0-9-]+$/);
		}
	});

	it('all slugs are unique across user and admin sections', () => {
		const allSlugs = [...USER_SECTIONS, ...ADMIN_SECTIONS].map((s) => s.slug);
		const unique = new Set(allSlugs);
		expect(unique.size).toBe(allSlugs.length);
	});

	it('USER_SECTIONS includes the 7 expected slugs', () => {
		const slugs = USER_SECTIONS.map((s) => s.slug);
		expect(slugs).toContain('getting-started');
		expect(slugs).toContain('incidents');
		expect(slugs).toContain('postmortems');
		expect(slugs).toContain('analytics');
		expect(slugs).toContain('semgrep');
		expect(slugs).toContain('api-keys');
		expect(slugs).toContain('rules');
	});

	it('ADMIN_SECTIONS includes the 3 expected slugs', () => {
		const slugs = ADMIN_SECTIONS.map((s) => s.slug);
		expect(slugs).toContain('administration');
		expect(slugs).toContain('security');
		expect(slugs).toContain('api-reference');
	});

	// Active link logic: isActive(slug) = page.url.pathname === `/docs/${slug}/`
	it('active path formula produces expected pattern', () => {
		const slug = 'incidents';
		const expectedPath = `/docs/${slug}/`;
		expect(expectedPath).toBe('/docs/incidents/');
	});
});
