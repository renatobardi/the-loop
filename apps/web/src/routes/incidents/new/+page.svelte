<script lang="ts">
	import { goto } from '$app/navigation';
	import IncidentForm from '$lib/components/incidents/IncidentForm.svelte';
	import { createIncident } from '$lib/services/incidents';
	import type { IncidentCreate } from '$lib/types/incident';

	async function handleSubmit(data: IncidentCreate) {
		const incident = await createIncident(data);
		await goto(`/incidents/${incident.id}/`);
	}
</script>

<div class="mx-auto max-w-3xl py-8">
	<h1 class="mb-6 text-2xl font-bold text-text">New Incident</h1>
	<IncidentForm onsubmit={handleSubmit} />
</div>
