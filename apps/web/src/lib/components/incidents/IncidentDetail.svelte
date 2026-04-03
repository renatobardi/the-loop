<script lang="ts">
	import { Badge, Tabs } from '$lib/ui';
	import type { Incident } from '$lib/types/incident';
	import DetailsTab from './tabs/DetailsTab.svelte';
	import OperationalTab from './tabs/OperationalTab.svelte';
	import PostmortemTab from './tabs/PostmortemTab.svelte';
	import TimelineTab from './tabs/TimelineTab.svelte';
	import RespondersTab from './tabs/RespondersTab.svelte';
	import ActionItemsTab from './tabs/ActionItemsTab.svelte';
	import AttachmentsTab from './tabs/AttachmentsTab.svelte';

	let { incident }: { incident: Incident } = $props();

	const tabs = [
		{ id: 'details', label: 'Details' },
		{ id: 'operational', label: 'Operational' },
		{ id: 'postmortem', label: 'Postmortem' },
		{ id: 'timeline', label: 'Timeline' },
		{ id: 'responders', label: 'Responders' },
		{ id: 'actions', label: 'Action Items' },
		{ id: 'attachments', label: 'Attachments' }
	];

	let activeTab = $state('details');

	const severityColors: Record<string, string> = {
		critical: 'bg-error text-white',
		high: 'bg-accent text-white',
		medium: 'bg-accent/20 text-text',
		low: 'bg-bg-elevated text-text-muted'
	};
</script>

<div class="space-y-4">
	<!-- Fixed header -->
	<div>
		<h1 class="text-2xl font-bold text-text">{incident.title}</h1>
		<div class="mt-2 flex gap-2">
			<Badge>{incident.category}</Badge>
			<Badge class={severityColors[incident.severity] ?? ''}>{incident.severity}</Badge>
		</div>
	</div>

	<Tabs {tabs} bind:active={activeTab} />

	<div class="pt-2">
		{#if activeTab === 'details'}
			<DetailsTab {incident} />
		{:else if activeTab === 'operational'}
			<OperationalTab {incident} />
		{:else if activeTab === 'postmortem'}
			<PostmortemTab {incident} />
		{:else if activeTab === 'timeline'}
			<TimelineTab incidentId={incident.id} active={activeTab === 'timeline'} />
		{:else if activeTab === 'responders'}
			<RespondersTab incidentId={incident.id} active={activeTab === 'responders'} />
		{:else if activeTab === 'actions'}
			<ActionItemsTab incidentId={incident.id} active={activeTab === 'actions'} />
		{:else if activeTab === 'attachments'}
			<AttachmentsTab incidentId={incident.id} active={activeTab === 'attachments'} />
		{/if}
	</div>
</div>
