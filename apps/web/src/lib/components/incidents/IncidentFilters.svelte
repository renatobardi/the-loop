<script lang="ts">
	import { CATEGORIES, SEVERITIES } from '$lib/types/incident';
	import type { Category, Severity } from '$lib/types/incident';
	import * as m from '$lib/paraglide/messages.js';

	let {
		category = $bindable(null),
		severity = $bindable(null),
		keyword = $bindable('')
	}: {
		category: Category | null;
		severity: Severity | null;
		keyword: string;
	} = $props();

	let searchTimeout: ReturnType<typeof setTimeout>;

	function onSearchInput(e: Event) {
		clearTimeout(searchTimeout);
		const value = (e.target as HTMLInputElement).value;
		searchTimeout = setTimeout(() => {
			keyword = value;
		}, 300);
	}

	function clearFilters() {
		category = null;
		severity = null;
		keyword = '';
	}
</script>

<div class="flex flex-wrap items-end gap-3">
	<div>
		<label for="filter-category" class="block text-xs font-medium text-text-muted">{m.incidents_filter_category()}</label>
		<select id="filter-category" bind:value={category} class="rounded-md border border-border bg-bg-surface px-3 py-1.5 text-sm text-text">
			<option value={null}>All</option>
			{#each CATEGORIES as cat}
				<option value={cat}>{cat}</option>
			{/each}
		</select>
	</div>

	<div>
		<label for="filter-severity" class="block text-xs font-medium text-text-muted">{m.incidents_filter_severity()}</label>
		<select id="filter-severity" bind:value={severity} class="rounded-md border border-border bg-bg-surface px-3 py-1.5 text-sm text-text">
			<option value={null}>All</option>
			{#each SEVERITIES as sev}
				<option value={sev}>{sev}</option>
			{/each}
		</select>
	</div>

	<div class="flex-1">
		<label for="filter-search" class="block text-xs font-medium text-text-muted">{m.incidents_search_placeholder()}</label>
		<input
			id="filter-search"
			type="search"
			value={keyword}
			oninput={onSearchInput}
			placeholder={m.incidents_search_placeholder()}
			class="w-full rounded-md border border-border bg-bg-surface px-3 py-1.5 text-sm text-text"
		/>
	</div>

	<button onclick={clearFilters} class="rounded-md px-3 py-1.5 text-sm text-text-muted hover:text-text">
		{m.incidents_filter_clear()}
	</button>
</div>
