export interface ActionItem {
	id: string;
	incident_id: string;
	title: string;
	description: string | null;
	owner_id: string | null;
	status: string;
	priority: string;
	due_date: string | null;
	completed_at: string | null;
	completed_by: string | null;
	created_at: string;
	updated_at: string;
}

export interface ActionItemListResponse {
	items: ActionItem[];
	total: number;
}
