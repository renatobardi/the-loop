<script lang="ts">
	import { Button } from '$lib/ui';
	import * as m from '$lib/paraglide/messages.js';

	let {
		page = $bindable(1),
		perPage = $bindable(20),
		total
	}: {
		page: number;
		perPage: number;
		total: number;
	} = $props();

	let totalPages = $derived(Math.max(1, Math.ceil(total / perPage)));

	function prev() {
		if (page > 1) page--;
	}

	function next() {
		if (page < totalPages) page++;
	}
</script>

<div class="flex items-center justify-between text-sm text-text-muted">
	<span>{m.incidents_pagination_total({ count: String(total) })}</span>

	<div class="flex items-center gap-2">
		<label for="per-page" class="text-xs">{m.incidents_per_page()}</label>
		<select id="per-page" bind:value={perPage} class="rounded border border-border bg-bg-surface px-2 py-1 text-xs text-text">
			<option value={10}>10</option>
			<option value={20}>20</option>
			<option value={50}>50</option>
			<option value={100}>100</option>
		</select>
	</div>

	<div class="flex items-center gap-2">
		<Button variant="secondary" onclick={prev} disabled={page <= 1}>&#8592;</Button>
		<span>{m.incidents_pagination_page({ page: String(page), pages: String(totalPages) })}</span>
		<Button variant="secondary" onclick={next} disabled={page >= totalPages}>&#8594;</Button>
	</div>
</div>
