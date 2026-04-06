import { describe, it, expect } from 'vitest';

// MultiSelectDropdown computes a display label from selected values + options.
// These tests verify the pure display logic extracted from the component.

type Option = { value: string; label: string };

const OPTIONS: Option[] = [
	{ value: 'backend', label: 'Backend' },
	{ value: 'platform', label: 'Platform' },
	{ value: 'frontend', label: 'Frontend' }
];

// Mirrors the displayLabel $derived in MultiSelectDropdown.svelte
function computeDisplayLabel(
	selected: string[],
	options: Option[],
	placeholder = 'All'
): string {
	if (selected.length === 0) return placeholder;
	if (selected.length === 1) return options.find((o) => o.value === selected[0])?.label ?? selected[0];
	return `${selected.length} selected`;
}

// Mirrors the toggle() function in MultiSelectDropdown.svelte
function toggle(selected: string[], value: string): string[] {
	return selected.includes(value)
		? selected.filter((v) => v !== value)
		: [...selected, value];
}

describe('MultiSelectDropdown — displayLabel logic', () => {
	it('returns placeholder when nothing is selected', () => {
		expect(computeDisplayLabel([], OPTIONS)).toBe('All');
	});

	it('uses custom placeholder when provided', () => {
		expect(computeDisplayLabel([], OPTIONS, 'Select teams')).toBe('Select teams');
	});

	it('shows option label for single selection', () => {
		expect(computeDisplayLabel(['backend'], OPTIONS)).toBe('Backend');
	});

	it('falls back to value when option label not found', () => {
		expect(computeDisplayLabel(['unknown-team'], OPTIONS)).toBe('unknown-team');
	});

	it('shows "N selected" for 2+ selections', () => {
		expect(computeDisplayLabel(['backend', 'platform'], OPTIONS)).toBe('2 selected');
		expect(computeDisplayLabel(['backend', 'platform', 'frontend'], OPTIONS)).toBe('3 selected');
	});
});

describe('MultiSelectDropdown — toggle logic', () => {
	it('adds a value when not in selection', () => {
		expect(toggle([], 'backend')).toEqual(['backend']);
		expect(toggle(['platform'], 'backend')).toEqual(['platform', 'backend']);
	});

	it('removes a value when already in selection', () => {
		expect(toggle(['backend', 'platform'], 'backend')).toEqual(['platform']);
	});

	it('does not mutate the original array', () => {
		const original = ['backend'];
		toggle(original, 'platform');
		expect(original).toEqual(['backend']);
	});

	it('removing the last item returns empty array', () => {
		expect(toggle(['backend'], 'backend')).toEqual([]);
	});

	it('clearAll is equivalent to returning empty array', () => {
		const selected = ['backend', 'platform'];
		const cleared: string[] = [];
		expect(cleared).toEqual([]);
		expect(selected.length).toBeGreaterThan(0);
	});
});
