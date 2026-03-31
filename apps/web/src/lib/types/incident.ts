/** TypeScript types matching the API contract for incidents. */

export const CATEGORIES = [
	'unsafe-regex',
	'injection',
	'deployment-error',
	'missing-safety-check',
	'race-condition',
	'unsafe-api-usage',
	'resource-exhaustion',
	'data-consistency',
	'missing-error-handling',
	'cascading-failure',
	'authentication-bypass',
	'configuration-drift'
] as const;

export type Category = (typeof CATEGORIES)[number];

export const SEVERITIES = ['critical', 'high', 'medium', 'low'] as const;

export type Severity = (typeof SEVERITIES)[number];

export interface Incident {
	id: string;
	title: string;
	date: string | null;
	source_url: string | null;
	organization: string | null;
	category: Category;
	subcategory: string | null;
	failure_mode: string | null;
	severity: Severity;
	affected_languages: string[];
	anti_pattern: string;
	code_example: string | null;
	remediation: string;
	static_rule_possible: boolean;
	semgrep_rule_id: string | null;
	embedding: number[] | null;
	tags: string[];
	version: number;
	deleted_at: string | null;
	created_at: string;
	updated_at: string;
	created_by: string;
}

export interface IncidentCreate {
	title: string;
	date?: string | null;
	source_url?: string | null;
	organization?: string | null;
	category: Category;
	subcategory?: string | null;
	failure_mode?: string | null;
	severity: Severity;
	affected_languages?: string[];
	anti_pattern: string;
	code_example?: string | null;
	remediation: string;
	static_rule_possible?: boolean;
	semgrep_rule_id?: string | null;
	tags?: string[];
}

export interface IncidentUpdate extends Partial<IncidentCreate> {
	version: number;
}

export interface PaginatedResponse {
	items: Incident[];
	total: number;
	page: number;
	per_page: number;
}

export interface ListFilters {
	page?: number;
	per_page?: number;
	category?: Category | null;
	severity?: Severity | null;
	q?: string | null;
}

export interface ApiError {
	detail: string | { detail: string; [key: string]: unknown };
}
