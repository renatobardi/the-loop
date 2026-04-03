<script lang="ts">
	import type { Incident } from '$lib/types/incident';

	let { incident }: { incident: Incident } = $props();

	function formatDate(iso: string | null): string {
		if (!iso) return '';
		return new Date(iso).toLocaleString();
	}

	// Check if tab has any content to show
	let hasContent = $derived(
		!!incident.started_at ||
			!!incident.detected_at ||
			!!incident.ended_at ||
			!!incident.resolved_at ||
			!!incident.impact_summary ||
			(incident.customers_affected != null && incident.customers_affected > 0) ||
			incident.sla_breached ||
			incident.slo_breached ||
			!!incident.detection_method ||
			!!incident.slack_channel_id ||
			!!incident.external_tracking_id
	);
</script>

{#if !hasContent}
	<p class="text-sm text-text-muted">No operational data recorded.</p>
{:else}
	<dl class="grid gap-4 text-sm md:grid-cols-2">
		{#if incident.started_at}
			<div>
				<dt class="text-text-muted">Start</dt>
				<dd class="text-text">{formatDate(incident.started_at)}</dd>
			</div>
		{/if}
		{#if incident.detected_at}
			<div>
				<dt class="text-text-muted">Detected</dt>
				<dd class="text-text">{formatDate(incident.detected_at)}</dd>
			</div>
		{/if}
		{#if incident.ended_at}
			<div>
				<dt class="text-text-muted">End</dt>
				<dd class="text-text">{formatDate(incident.ended_at)}</dd>
			</div>
		{/if}
		{#if incident.resolved_at}
			<div>
				<dt class="text-text-muted">Resolved</dt>
				<dd class="text-text">{formatDate(incident.resolved_at)}</dd>
			</div>
		{/if}
		{#if incident.impact_summary}
			<div class="md:col-span-2">
				<dt class="text-text-muted">Impact</dt>
				<dd class="whitespace-pre-wrap text-text">{incident.impact_summary}</dd>
			</div>
		{/if}
		{#if incident.customers_affected != null && incident.customers_affected > 0}
			<div>
				<dt class="text-text-muted">Customers affected</dt>
				<dd class="text-text">{incident.customers_affected.toLocaleString()}</dd>
			</div>
		{/if}
		{#if incident.sla_breached || incident.slo_breached}
			<div class="flex gap-2 md:col-span-2">
				{#if incident.sla_breached}
					<span
						class="inline-flex items-center gap-1 rounded bg-error/20 px-2 py-1 text-xs font-medium text-error"
					>
						&#9888; SLA breached
					</span>
				{/if}
				{#if incident.slo_breached}
					<span
						class="inline-flex items-center gap-1 rounded bg-error/20 px-2 py-1 text-xs font-medium text-error"
					>
						&#9888; SLO breached
					</span>
				{/if}
			</div>
		{/if}
		{#if incident.detection_method}
			<div>
				<dt class="text-text-muted">Detection method</dt>
				<dd class="text-text">{incident.detection_method}</dd>
			</div>
		{/if}
		{#if incident.slack_channel_id}
			<div>
				<dt class="text-text-muted">Slack</dt>
				<dd class="text-text">{incident.slack_channel_id}</dd>
			</div>
		{/if}
		{#if incident.external_tracking_id}
			<div>
				<dt class="text-text-muted">External tracking</dt>
				<dd class="text-text">{incident.external_tracking_id}</dd>
			</div>
		{/if}
	</dl>
{/if}
