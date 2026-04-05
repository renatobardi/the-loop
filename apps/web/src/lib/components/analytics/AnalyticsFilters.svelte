<script lang="ts">
	import type { AnalyticsFilter, Period, StatusFilter, RootCauseCategory } from '$lib/types/analytics';
	import type { TeamStats } from '$lib/types/analytics';
	import MultiSelectDropdown from './MultiSelectDropdown.svelte';

	let {
		filters,
		teamOptions,
		onApply
	}: {
		filters: AnalyticsFilter;
		teamOptions: TeamStats[];
		onApply: (_: AnalyticsFilter) => void; // eslint-disable-line no-unused-vars
	} = $props();

	let period = $state<Period>(filters.period);
	let selectedTeams = $state<string[]>(filters.teams ?? []);
	let category = $state<string>(filters.category ?? '');
	let status = $state<StatusFilter>(filters.status);
	let startDate = $state<string>(filters.start_date ?? '');
	let endDate = $state<string>(filters.end_date ?? '');

	// Sync local state when filters prop changes (e.g., after drill-down navigation)
	$effect(() => {
		period = filters.period;
		selectedTeams = filters.teams ?? [];
		category = filters.category ?? '';
		status = filters.status;
		startDate = filters.start_date ?? '';
		endDate = filters.end_date ?? '';
	});

	const teamOptionsList = $derived(teamOptions.map((t) => ({ value: t.team, label: t.team })));

	const CATEGORIES: { value: RootCauseCategory; label: string }[] = [
		{ value: 'code_pattern', label: 'Code Pattern' },
		{ value: 'infrastructure', label: 'Infrastructure' },
		{ value: 'process_breakdown', label: 'Process Breakdown' },
		{ value: 'third_party', label: 'Third Party' },
		{ value: 'unknown', label: 'Unknown' }
	];

	function apply() {
		const f: AnalyticsFilter = {
			period,
			teams: selectedTeams,
			category: (category as RootCauseCategory) || null,
			status,
			start_date: period === 'custom' ? startDate || null : null,
			end_date: period === 'custom' ? endDate || null : null
		};
		onApply(f);
	}

	function reset() {
		period = 'month';
		selectedTeams = [];
		category = '';
		status = 'all';
		startDate = '';
		endDate = '';
		onApply({ period: 'month', teams: [], category: null, status: 'all' });
	}
</script>

<div class="flex flex-wrap items-end gap-3 rounded-lg border border-border bg-bg-surface px-4 py-3">
	<!-- Period -->
	<div class="flex flex-col gap-1">
		<label for="af-period" class="text-xs text-text-muted">Period</label>
		<select
			id="af-period"
			bind:value={period}
			class="rounded border border-border bg-bg px-2 py-1.5 text-sm text-text focus:outline-none focus:ring-1 focus:ring-accent"
			aria-label="Select period"
		>
			<option value="week">This Week</option>
			<option value="month">This Month</option>
			<option value="quarter">This Quarter</option>
			<option value="custom">Custom</option>
		</select>
	</div>

	<!-- Custom date range -->
	{#if period === 'custom'}
		<div class="flex flex-col gap-1">
			<label for="af-start" class="text-xs text-text-muted">Start Date</label>
			<input
				id="af-start"
				type="date"
				bind:value={startDate}
				class="rounded border border-border bg-bg px-2 py-1.5 text-sm text-text focus:outline-none focus:ring-1 focus:ring-accent"
				aria-label="Start date"
			/>
		</div>
		<div class="flex flex-col gap-1">
			<label for="af-end" class="text-xs text-text-muted">End Date</label>
			<input
				id="af-end"
				type="date"
				bind:value={endDate}
				class="rounded border border-border bg-bg px-2 py-1.5 text-sm text-text focus:outline-none focus:ring-1 focus:ring-accent"
				aria-label="End date"
			/>
		</div>
	{/if}

	<!-- Team (multi-select) -->
	<MultiSelectDropdown
		id="af-team"
		label="Team"
		options={teamOptionsList}
		selected={selectedTeams}
		placeholder="All Teams"
		onchange={(vals) => (selectedTeams = vals)}
	/>

	<!-- Category -->
	<div class="flex flex-col gap-1">
		<label for="af-category" class="text-xs text-text-muted">Category</label>
		<select
			id="af-category"
			bind:value={category}
			class="rounded border border-border bg-bg px-2 py-1.5 text-sm text-text focus:outline-none focus:ring-1 focus:ring-accent"
			aria-label="Filter by root cause category"
		>
			<option value="">All Categories</option>
			{#each CATEGORIES as c (c.value)}
				<option value={c.value}>{c.label}</option>
			{/each}
		</select>
	</div>

	<!-- Status -->
	<div class="flex flex-col gap-1">
		<label for="af-status" class="text-xs text-text-muted">Status</label>
		<select
			id="af-status"
			bind:value={status}
			class="rounded border border-border bg-bg px-2 py-1.5 text-sm text-text focus:outline-none focus:ring-1 focus:ring-accent"
			aria-label="Filter by status"
		>
			<option value="all">All</option>
			<option value="resolved">Resolved</option>
			<option value="unresolved">Unresolved</option>
		</select>
	</div>

	<!-- Actions -->
	<div class="flex gap-2">
		<button
			onclick={apply}
			class="rounded bg-accent px-3 py-1.5 text-sm font-medium text-white hover:bg-accent/90 focus:outline-none focus:ring-2 focus:ring-accent"
			aria-label="Apply filters"
		>
			Apply
		</button>
		<button
			onclick={reset}
			class="rounded border border-border px-3 py-1.5 text-sm text-text-muted hover:text-text focus:outline-none focus:ring-2 focus:ring-accent"
			aria-label="Reset filters"
		>
			Reset
		</button>
	</div>
</div>
