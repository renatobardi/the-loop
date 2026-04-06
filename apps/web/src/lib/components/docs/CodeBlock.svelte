<script lang="ts">
	let {
		code,
		language,
		label
	}: {
		code: string;
		language?: string;
		label?: string;
	} = $props();

	let copied = $state(false);

	async function copy() {
		await navigator.clipboard.writeText(code);
		copied = true;
		setTimeout(() => {
			copied = false;
		}, 2000);
	}
</script>

<div class="rounded-lg border border-border overflow-hidden">
	{#if label}
		<div class="flex items-center justify-between px-4 py-2 bg-bg-elevated border-b border-border">
			<span class="text-xs text-text-muted font-mono">{label}</span>
			{#if language}
				<span class="text-xs text-text-subtle uppercase tracking-wide">{language}</span>
			{/if}
		</div>
	{/if}
	<div class="relative group">
		<pre
			class="p-4 overflow-x-auto text-sm text-text font-mono bg-bg-surface leading-relaxed"
		><code>{code}</code></pre>
		<button
			onclick={copy}
			aria-label="Copy code"
			class="absolute top-3 right-3 p-1.5 rounded bg-bg-elevated border border-border text-text-muted hover:text-text opacity-0 group-hover:opacity-100 transition-opacity focus:opacity-100"
		>
			{#if copied}
				<svg class="w-4 h-4 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
					<path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
				</svg>
				<span class="sr-only">Copied!</span>
			{:else}
				<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
					<rect x="9" y="9" width="13" height="13" rx="2" ry="2" /><path stroke-linecap="round" stroke-linejoin="round" d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
				</svg>
			{/if}
		</button>
	</div>
</div>
