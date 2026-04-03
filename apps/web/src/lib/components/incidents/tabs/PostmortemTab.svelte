<script lang="ts">
	import type { Incident } from '$lib/types/incident';

	let { incident }: { incident: Incident } = $props();

	const statusColors: Record<string, string> = {
		draft: 'bg-bg-elevated text-text-muted',
		in_review: 'bg-yellow-500/20 text-yellow-400',
		approved: 'bg-green-500/20 text-green-400',
		published: 'bg-accent/20 text-accent'
	};

	const statusLabels: Record<string, string> = {
		draft: 'Rascunho',
		in_review: 'Em revisão',
		approved: 'Aprovado',
		published: 'Publicado'
	};

	function isDueDateUrgent(dateStr: string | null): boolean {
		if (!dateStr) return false;
		const due = new Date(dateStr);
		const now = new Date();
		const daysUntil = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
		return daysUntil <= 7;
	}

	let hasContent = $derived(
		(!!incident.postmortem_status && incident.postmortem_status !== 'draft') ||
			!!incident.postmortem_published_at ||
			!!incident.postmortem_due_date ||
			!!incident.lessons_learned ||
			!!incident.why_we_were_surprised
	);
</script>

{#if !hasContent}
	<p class="text-sm text-text-muted">Postmortem não iniciado.</p>
{:else}
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
					<span class="text-text-muted">Prazo: </span>
					<span
						class={isDueDateUrgent(incident.postmortem_due_date) ? 'font-medium text-error' : 'text-text'}
					>
						{new Date(incident.postmortem_due_date).toLocaleDateString('pt-BR')}
					</span>
				</div>
			{/if}
			{#if incident.postmortem_published_at}
				<div>
					<span class="text-text-muted">Publicado em: </span>
					<span class="text-text"
						>{new Date(incident.postmortem_published_at).toLocaleString('pt-BR')}</span
					>
				</div>
			{/if}
		</div>

		{#if incident.lessons_learned}
			<div>
				<h3 class="mb-1 font-medium text-text">Lições aprendidas</h3>
				<p class="whitespace-pre-wrap text-text-muted">{incident.lessons_learned}</p>
			</div>
		{/if}

		{#if incident.why_we_were_surprised}
			<div>
				<h3 class="mb-1 font-medium text-text">Por que fomos pegos de surpresa</h3>
				<p class="whitespace-pre-wrap text-text-muted">{incident.why_we_were_surprised}</p>
			</div>
		{/if}
	</div>
{/if}
