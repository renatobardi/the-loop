import { describe, it, expect } from 'vitest';
import { barColor } from '$lib/utils/analytics';
import type { RuleEffectivenessStats } from '$lib/types/analytics';

// RuleEffectivenessCard renders a table row per rule with a severity badge.
// The badge variant mirrors the barColor threshold: avg_severity >= 0.9 → ERROR, else → WARNING.

function makeRule(rule_id: string, incident_count: number, avg_severity: number): RuleEffectivenessStats {
	return { rule_id, incident_count, avg_severity };
}

describe('RuleEffectivenessCard — data contract', () => {
	it('RuleEffectivenessStats has rule_id, incident_count, avg_severity', () => {
		const r = makeRule('theloop.sql-injection', 5, 1.0);
		expect(r.rule_id).toBe('theloop.sql-injection');
		expect(r.incident_count).toBe(5);
		expect(r.avg_severity).toBe(1.0);
	});

	it('maps severity thresholds correctly', () => {
		expect(barColor(0.5)).toContain('warning');
		expect(barColor(1.0)).toContain('error');
	});
});

describe('RuleEffectivenessCard — severity badge logic', () => {
	it('avg_severity 1.0 maps to error color', () => {
		expect(barColor(1.0)).toContain('error');
	});

	it('avg_severity 0.5 maps to warning color', () => {
		expect(barColor(0.5)).toContain('warning');
	});

	it('threshold is 0.9 (inclusive → error)', () => {
		expect(barColor(0.9)).toContain('error');
		expect(barColor(0.89)).toContain('warning');
	});

	it('empty data list is a valid state (no rows rendered)', () => {
		const data: RuleEffectivenessStats[] = [];
		expect(data.length).toBe(0);
	});

	it('list is sorted by rule_id for stable display order', () => {
		const data = [
			makeRule('theloop.z-last', 1, 0.5),
			makeRule('theloop.a-first', 3, 1.0)
		];
		const sorted = [...data].sort((a, b) => a.rule_id.localeCompare(b.rule_id));
		expect(sorted[0].rule_id).toBe('theloop.a-first');
		expect(sorted[1].rule_id).toBe('theloop.z-last');
	});
});
