<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button } from '$lib/ui';
	import { i18n } from '$lib/i18n';
	import { languageTag } from '$lib/paraglide/runtime.js';
	import IncidentDetail from '$lib/components/incidents/IncidentDetail.svelte';
	import DeleteConfirmModal from '$lib/components/incidents/DeleteConfirmModal.svelte';
	import { deleteIncident } from '$lib/services/incidents';
	import * as m from '$lib/paraglide/messages.js';

	let { data } = $props();

	let showDelete = $state(false);
	let deleteError = $state('');

	async function handleDelete() {
		deleteError = '';
		try {
			await deleteIncident(data.incident.id);
			await goto(i18n.resolveRoute('/incidents', languageTag()) + '/'); // eslint-disable-line svelte/no-navigation-without-resolve -- resolved via i18n.resolveRoute
		} catch (err) {
			deleteError = err instanceof Error ? err.message : m.incident_error();
		}
	}
</script>

<div class="py-8">
	<div class="mb-6 flex items-center justify-between">
		<!-- eslint-disable svelte/no-navigation-without-resolve -- ParaglideJS translates href automatically -->
		<a href="/incidents/" class="text-sm text-text-muted hover:text-text">&larr; {m.incidents_title()}</a>
		<div class="flex gap-2">
			<a href="/incidents/{data.incident.id}/edit/">
				<Button variant="secondary">{m.incident_detail_edit()}</Button>
			</a>
			<Button onclick={() => (showDelete = true)}>{m.incident_detail_delete()}</Button>
		</div>
		<!-- eslint-enable svelte/no-navigation-without-resolve -->
	</div>

	<IncidentDetail incident={data.incident} />

	<DeleteConfirmModal bind:open={showDelete} onconfirm={handleDelete} error={deleteError} />
</div>
