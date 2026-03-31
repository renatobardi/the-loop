<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button } from '$lib/ui';
	import IncidentDetail from '$lib/components/incidents/IncidentDetail.svelte';
	import DeleteConfirmModal from '$lib/components/incidents/DeleteConfirmModal.svelte';
	import { deleteIncident } from '$lib/services/incidents';

	let { data } = $props();

	let showDelete = $state(false);
	let deleteError = $state('');

	async function handleDelete() {
		deleteError = '';
		try {
			await deleteIncident(data.incident.id);
			await goto('/incidents/');
		} catch (err) {
			deleteError = err instanceof Error ? err.message : 'Failed to save incident.';
		}
	}
</script>

<div class="py-8">
	<div class="mb-6 flex items-center justify-between">
		<a href="/incidents/" class="text-sm text-text-muted hover:text-text">&larr; Incidents</a>
		<div class="flex gap-2">
			<a href="/incidents/{data.incident.id}/edit/">
				<Button variant="secondary">Edit</Button>
			</a>
			<Button onclick={() => (showDelete = true)}>Delete</Button>
		</div>
	</div>

	<IncidentDetail incident={data.incident} />

	<DeleteConfirmModal bind:open={showDelete} onconfirm={handleDelete} error={deleteError} />
</div>
