<script lang="ts">
	let {
		tabs,
		active = $bindable()
	}: { tabs: { id: string; label: string }[]; active: string } = $props();
</script>

<div role="tablist" class="flex border-b border-border">
	{#each tabs as tab (tab.id)}
		<button
			role="tab"
			aria-selected={active === tab.id}
			onclick={() => (active = tab.id)}
			class="px-4 py-2 text-sm font-medium transition-colors
             {active === tab.id
				? 'border-b-2 border-accent text-text'
				: 'text-text-muted hover:text-text'}"
		>
			{tab.label}
		</button>
	{/each}
</div>
