<script lang="ts">
	import { goto } from '$app/navigation';
	import { i18n } from '$lib/i18n';
	import { languageTag } from '$lib/paraglide/runtime.js';
	import IncidentForm from '$lib/components/incidents/IncidentForm.svelte';
	import { createIncident } from '$lib/services/incidents';
	import type { IncidentCreate } from '$lib/types/incident';
	import * as m from '$lib/paraglide/messages.js';

	async function handleSubmit(data: IncidentCreate) {
		const incident = await createIncident(data);
		await goto(i18n.resolveRoute('/incidents', languageTag()) + `/${incident.id}/`); // eslint-disable-line svelte/no-navigation-without-resolve -- resolved via i18n.resolveRoute
	}
</script>

<div class="mx-auto max-w-3xl py-8">
	<h1 class="mb-6 text-2xl font-bold text-text">{m.incident_create_title()}</h1>
	<IncidentForm onsubmit={handleSubmit} />
</div>
