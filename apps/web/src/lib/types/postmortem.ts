export interface RootCauseTemplate {
	id: string;
	category: string;
	title: string;
	description_template: string;
	pattern_example?: string;
	severity_default: string;
}

export interface Postmortem {
	id: string;
	incident_id: string;
	root_cause_category: string;
	description: string;
	suggested_pattern?: string;
	team_responsible: string;
	severity_for_rule: string;
	related_rule_id?: string;
	created_by: string;
	created_at: string;
	updated_by?: string;
	updated_at?: string;
	is_locked: boolean;
}

export interface PostmortumCreateRequest {
	root_cause_category: string;
	description: string;
	team_responsible: string;
	severity_for_rule: string;
	suggested_pattern?: string;
	related_rule_id?: string;
}

export interface PostmortumUpdateRequest {
	description?: string;
	team_responsible?: string;
	suggested_pattern?: string;
	root_cause_category?: string;
	severity_for_rule?: string;
	related_rule_id?: string;
}

export interface TemplateListResponse {
	templates: RootCauseTemplate[];
	count: number;
}

export interface PostmortumListResponse {
	items: Postmortem[];
	total: number;
}
