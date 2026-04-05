<script lang="ts">
	let {
		id,
		label,
		options,
		selected = [],
		placeholder = 'All',
		onchange
	}: {
		id: string;
		label: string;
		options: { value: string; label: string }[];
		selected?: string[];
		placeholder?: string;
		onchange: (_: string[]) => void; // eslint-disable-line no-unused-vars
	} = $props();

	let open = $state(false);

	const displayLabel = $derived(
		selected.length === 0
			? placeholder
			: selected.length === 1
				? (options.find((o) => o.value === selected[0])?.label ?? selected[0])
				: `${selected.length} selected`
	);

	function toggle(value: string) {
		const next = selected.includes(value)
			? selected.filter((v) => v !== value)
			: [...selected, value];
		onchange(next);
	}

	function clearAll() {
		onchange([]);
		open = false;
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') open = false;
	}
</script>

<svelte:window onkeydown={handleKeydown} />

<div class="relative flex flex-col gap-1">
	<label for="{id}-btn" class="text-xs text-text-muted">{label}</label>
	<button
		id="{id}-btn"
		type="button"
		onclick={() => (open = !open)}
		aria-haspopup="listbox"
		aria-expanded={open}
		aria-label="Select {label}"
		class="flex min-w-[120px] items-center justify-between gap-2 rounded border border-border bg-bg px-2 py-1.5 text-sm text-text focus:outline-none focus:ring-1 focus:ring-accent"
	>
		<span class="truncate {selected.length === 0 ? 'text-text-muted' : ''}">{displayLabel}</span>
		<svg
			class="h-3 w-3 shrink-0 text-text-muted transition-transform {open ? 'rotate-180' : ''}"
			viewBox="0 0 12 12"
			fill="none"
		>
			<path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
		</svg>
	</button>

	{#if open}
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div
			class="absolute left-0 top-full z-30 mt-1 min-w-full overflow-hidden rounded border border-border bg-bg-elevated shadow-md"
			onclick={(e) => e.stopPropagation()}
		>
			<ul role="listbox" aria-multiselectable="true" aria-label="{label} options">
				{#each options as opt (opt.value)}
					<li role="option" aria-selected={selected.includes(opt.value)}>
						<button
							type="button"
							onclick={() => toggle(opt.value)}
							class="flex w-full items-center gap-2 px-3 py-2 text-left text-sm hover:bg-bg-surface focus:outline-none focus:ring-1 focus:ring-inset focus:ring-accent"
						>
							<span
								class="flex h-4 w-4 shrink-0 items-center justify-center rounded border {selected.includes(opt.value) ? 'border-accent bg-accent' : 'border-border bg-bg'}"
							>
								{#if selected.includes(opt.value)}
									<svg viewBox="0 0 10 8" fill="none" class="h-2.5 w-2.5">
										<path
											d="M1 4l3 3 5-6"
											stroke="white"
											stroke-width="1.5"
											stroke-linecap="round"
											stroke-linejoin="round"
										/>
									</svg>
								{/if}
							</span>
							<span class="text-text">{opt.label}</span>
						</button>
					</li>
				{/each}
			</ul>
			{#if selected.length > 0}
				<div class="border-t border-border px-3 py-1.5">
					<button
						type="button"
						onclick={clearAll}
						class="text-xs text-text-muted hover:text-text focus:outline-none"
					>
						Clear all
					</button>
				</div>
			{/if}
		</div>
	{/if}
</div>

{#if open}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="fixed inset-0 z-20" onclick={() => (open = false)}></div>
{/if}
