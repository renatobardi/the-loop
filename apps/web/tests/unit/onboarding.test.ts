import { describe, it, expect } from 'vitest';
import { generateWorkflowYaml } from '$lib/utils/workflow-generator';

describe('workflow YAML generator', () => {
	it('generates YAML containing the API key', () => {
		const yaml = generateWorkflowYaml('tlp_abc123');
		expect(yaml).toContain('tlp_abc123');
	});

	it('references THELOOP_API_TOKEN secret', () => {
		const yaml = generateWorkflowYaml('tlp_test');
		expect(yaml).toContain('THELOOP_API_TOKEN');
	});

	it('references theloop-guard workflow name', () => {
		const yaml = generateWorkflowYaml('tlp_test');
		expect(yaml).toContain('theloop-guard');
	});

	it('returns a non-empty string longer than 100 characters', () => {
		const yaml = generateWorkflowYaml('tlp_test');
		expect(yaml.length).toBeGreaterThan(100);
	});

	it('includes the API endpoint URL', () => {
		const yaml = generateWorkflowYaml('tlp_any');
		expect(yaml).toContain('api.loop.oute.pro');
	});
});
