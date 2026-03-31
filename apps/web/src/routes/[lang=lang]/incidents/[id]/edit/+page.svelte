<script lang="ts">
	import { goto } from '$app/navigation';
	import { i18n } from '$lib/i18n';
	import { languageTag } from '$lib/paraglide/runtime.js';
	import IncidentForm from '$lib/components/incidents/IncidentForm.svelte';
	import { updateIncident } from '$lib/services/incidents';
	import type { IncidentCreate } from '$lib/types/incident';
	import * as m from '$lib/paraglide/messages.js';

	let { data } = $props();

	const initial: IncidentCreate = {
		title: data.incident.title,
		date: data.incident.date,
		source_url: data.incident.source_url,
		organization: data.incident.organization,
		category: data.incident.category,
		subcategory: data.incident.subcategory,
		failure_mode: data.incident.failure_mode,
		severity: data.incident.severity,
		affected_languages: data.incident.affected_languages,
		anti_pattern: data.incident.anti_pattern,
		code_example: data.incident.code_example,
		remediation: data.incident.remediation,
		static_rule_possible: data.incident.static_rule_possible,
		semgrep_rule_id: data.incident.semgrep_rule_id,
		tags: data.incident.tags
	};

	const incidentVersion = data.incident.version;
	const incidentId = data.incident.id;

	async function handleSubmit(formData: IncidentCreate & { version?: number }) {
		await updateIncident(incidentId, {
			...formData,
			version: formData.version ?? incidentVersion
		});
		await goto(i18n.resolveRoute('/incidents', languageTag()) + `/${incidentId}/`); // eslint-disable-line svelte/no-navigation-without-resolve -- resolved via i18n.resolveRoute
	}
</script>

<div class="mx-auto max-w-3xl py-8">
	<h1 class="mb-6 text-2xl font-bold text-text">{m.incident_edit_title()}</h1>
	<IncidentForm {initial} version={incidentVersion} onsubmit={handleSubmit} />
</div>
