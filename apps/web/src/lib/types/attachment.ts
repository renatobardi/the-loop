export interface Attachment {
	id: string;
	incident_id: string;
	uploaded_by: string | null;
	filename: string;
	mime_type: string;
	file_size_bytes: number;
	gcs_bucket: string;
	gcs_object_path: string;
	content_text: string | null;
	extraction_status: string;
	attachment_type: string;
	source_system: string | null;
	source_url: string | null;
	created_at: string;
	updated_at: string;
}

export interface AttachmentListResponse {
	items: Attachment[];
	total: number;
}
