<script lang="ts">
	export interface Rule {
		id: string;
		languages: string[];
		message: string;
		severity: string;
		metadata: Record<string, unknown>;
		patterns: Array<Record<string, unknown>>;
	}

	let { rule }: { rule: Rule } = $props();

	const severityClass = $derived(
		rule.severity === 'ERROR'
			? 'bg-error/10 text-error border border-error/20'
			: 'bg-warning/10 text-warning border border-warning/20'
	);

	const codeExample = $derived(
		(() => {
			for (const p of rule.patterns) {
				const val = p.pattern ?? p['pattern-either'] ?? p['pattern-inside'];
				if (typeof val === 'string') return val;
				if (Array.isArray(val)) {
					const first = val[0];
					return typeof first === 'object'
						? (first as Record<string, string>).pattern ?? ''
						: String(first);
				}
			}
			return '';
		})()
	);
</script>

<div class="rounded-lg border border-border bg-bg-surface p-5">
	<div class="flex items-start justify-between gap-3">
		<div class="min-w-0 flex-1">
			<div class="flex flex-wrap items-center gap-2">
				<code class="font-mono text-sm text-accent">{rule.id}</code>
				<span class="rounded px-1.5 py-0.5 text-xs font-semibold {severityClass}">
					{rule.severity}
				</span>
				{#each rule.languages as lang (lang)}
					<span class="rounded border border-border bg-bg px-1.5 py-0.5 text-xs text-text-muted">
						{lang}
					</span>
				{/each}
			</div>
			<p class="mt-2 text-sm text-text">{rule.message}</p>
		</div>
	</div>

	{#if codeExample}
		<div class="mt-3 overflow-x-auto rounded border border-border bg-bg">
			<pre class="p-3 font-mono text-xs text-text-muted whitespace-pre-wrap"><code>{codeExample}</code></pre>
		</div>
	{/if}
</div>
