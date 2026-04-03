export interface Responder {
	id: string;
	incident_id: string;
	user_id: string;
	role: string;
	joined_at: string;
	left_at: string | null;
	contribution_summary: string | null;
	created_at: string;
	updated_at: string;
}

export interface ResponderListResponse {
	items: Responder[];
	total: number;
}
