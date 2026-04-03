export interface TimelineEvent {
	id: string;
	incident_id: string;
	event_type: string;
	description: string;
	occurred_at: string;
	recorded_by: string;
	duration_minutes: number | null;
	external_reference_url: string | null;
	created_at: string;
	updated_at: string;
}

export interface TimelineEventListResponse {
	items: TimelineEvent[];
	total: number;
}
