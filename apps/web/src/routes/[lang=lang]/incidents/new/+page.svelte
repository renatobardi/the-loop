<script lang="ts">
	import { goto } from '$app/navigation';
	import IncidentForm from '$lib/components/incidents/IncidentForm.svelte';
	import { createIncident } from '$lib/services/incidents';
	import type { IncidentCreate } from '$lib/types/incident';
	import * as m from '$lib/paraglide/messages.js';

	async function handleSubmit(data: IncidentCreate) {
		const incident = await createIncident(data);
		await goto(`../incidents/${incident.id}/`);
	}
</script>

<div class="mx-auto max-w-3xl py-8">
	<h1 class="mb-6 text-2xl font-bold text-text">{m.incident_create_title()}</h1>
	<IncidentForm onsubmit={handleSubmit} />
</div>
