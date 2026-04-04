import { describe, it, expect } from 'vitest';
import { formatCategory, barColor } from '$lib/utils/analytics';

describe('formatCategory (CategoryHeatmap display logic)', () => {
	it('converts snake_case to Title Case', () => {
		expect(formatCategory('code_pattern')).toBe('Code Pattern');
		expect(formatCategory('process_breakdown')).toBe('Process Breakdown');
	});

	it('handles single words', () => {
		expect(formatCategory('unknown')).toBe('Unknown');
		expect(formatCategory('infrastructure')).toBe('Infrastructure');
	});

	it('handles third_party correctly', () => {
		expect(formatCategory('third_party')).toBe('Third Party');
	});
});

describe('barColor (CategoryHeatmap severity coloring)', () => {
	it('returns error color (red) for high avg_severity (>= 0.9)', () => {
		const color = barColor(1.0);
		expect(color).toContain('error');
	});

	it('returns warning color (amber) for low avg_severity (< 0.9)', () => {
		const color = barColor(0.5);
		expect(color).toContain('warning');
	});

	it('uses 0.9 as the threshold (inclusive)', () => {
		expect(barColor(0.9)).toContain('error');
		expect(barColor(0.89)).toContain('warning');
	});
});
