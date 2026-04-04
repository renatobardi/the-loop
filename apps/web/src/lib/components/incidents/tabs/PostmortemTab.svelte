<script lang="ts">
	import type { Incident } from '$lib/types/incident';
	import type { Postmortem } from '$lib/types/postmortem';
	import { getPostmortemByIncident } from '$lib/services/incidents';
	import PostmortemForm from '../PostmortemForm.svelte';
	import RootCauseView from '../RootCauseView.svelte';

	let { incident }: { incident: Incident } = $props();

	let postmortem: Postmortem | null = $state(null);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let loaded = $state(false);

	// Lazy load postmortem when tab becomes active
	async function loadPostmortem() {
		if (loaded || loading) return;
		loading = true;
		error = null;

		try {
			postmortem = await getPostmortemByIncident(incident.id);
		} catch (e) {
			// 404 is expected when no postmortem exists yet
			if (e instanceof Error && e.message.includes('404')) {
				postmortem = null;
			} else {
				error = e instanceof Error ? e.message : 'Failed to load postmortem';
			}
		} finally {
			loading = false;
			loaded = true;
		}
	}

	$effect(() => {
		loadPostmortem();
	});

	const statusColors: Record<string, string> = {
		draft: 'bg-bg-elevated text-text-muted',
		in_review: 'bg-accent/20 text-accent',
		approved: 'bg-success/20 text-success',
		published: 'bg-accent/20 text-accent'
	};

	const statusLabels: Record<string, string> = {
		draft: 'Draft',
		in_review: 'In review',
		approved: 'Approved',
		published: 'Published'
	};

	function isDueDateUrgent(dateStr: string | null): boolean {
		if (!dateStr) return false;
		const due = new Date(dateStr);
		const now = new Date();
		const daysUntil = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
		return daysUntil <= 7;
	}

	let hasLegacyContent = $derived(
		(!!incident.postmortem_status && incident.postmortem_status !== 'draft') ||
			!!incident.postmortem_published_at ||
			!!incident.postmortem_due_date ||
			!!incident.lessons_learned ||
			!!incident.why_we_were_surprised
	);
</script>

{#if loading}
	<div class="flex items-center justify-center py-12">
		<p class="text-sm text-text-muted">Loading postmortem...</p>
	</div>
{:else if error}
	<div class="rounded bg-error/10 p-4 text-sm text-error">
		<p class="font-medium">Error loading postmortem</p>
		<p class="mt-1">{error}</p>
	</div>
{:else if postmortem}
	{#if postmortem.is_locked}
		<RootCauseView {postmortem} />
	{:else}
		<PostmortemForm {incident} {postmortem} />
	{/if}
{:else if hasLegacyContent}
	<!-- Legacy postmortem status display -->
	<div class="space-y-6 text-sm">
		<div class="flex flex-wrap gap-4">
			{#if incident.postmortem_status}
				<div>
					<span class="text-text-muted">Status: </span>
					<span
						class="inline-block rounded px-2 py-0.5 text-xs font-medium {statusColors[incident.postmortem_status] ?? 'bg-bg-elevated text-text-muted'}"
					>
						{statusLabels[incident.postmortem_status] ?? incident.postmortem_status}
					</span>
				</div>
			{/if}
			{#if incident.postmortem_due_date}
				<div>
					<span class="text-text-muted">Due date: </span>
					<span
						class={isDueDateUrgent(incident.postmortem_due_date) ? 'font-medium text-error' : 'text-text'}
					>
						{new Date(incident.postmortem_due_date).toLocaleDateString()}
					</span>
				</div>
			{/if}
			{#if incident.postmortem_published_at}
				<div>
					<span class="text-text-muted">Published: </span>
					<span class="text-text"
						>{new Date(incident.postmortem_published_at).toLocaleString()}</span
					>
				</div>
			{/if}
		</div>

		{#if incident.lessons_learned}
			<div>
				<h3 class="mb-1 font-medium text-text">Lessons learned</h3>
				<p class="whitespace-pre-wrap text-text-muted">{incident.lessons_learned}</p>
			</div>
		{/if}

		{#if incident.why_we_were_surprised}
			<div>
				<h3 class="mb-1 font-medium text-text">Why we were surprised</h3>
				<p class="whitespace-pre-wrap text-text-muted">{incident.why_we_were_surprised}</p>
			</div>
		{/if}
	</div>
{:else}
	<PostmortemForm {incident} />
{/if}
