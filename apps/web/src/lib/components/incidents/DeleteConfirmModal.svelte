<script lang="ts">
	import { Button } from '$lib/ui';
	import * as m from '$lib/paraglide/messages.js';

	let {
		open = $bindable(false),
		onconfirm,
		error = ''
	}: {
		open: boolean;
		onconfirm: () => Promise<void>;
		error?: string;
	} = $props();

	let deleting = $state(false);

	async function handleConfirm() {
		deleting = true;
		try {
			await onconfirm();
		} finally {
			deleting = false;
		}
	}
</script>

{#if open}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" role="dialog" aria-modal="true">
		<div class="mx-4 w-full max-w-md rounded-lg bg-bg-surface p-6 shadow-xl">
			<h2 class="text-lg font-semibold text-text">{m.incident_delete_confirm_title()}</h2>
			<p class="mt-2 text-sm text-text-muted">{m.incident_delete_confirm_body()}</p>

			{#if error}
				<p class="mt-3 text-sm text-error">{error}</p>
			{/if}

			<div class="mt-6 flex justify-end gap-3">
				<Button variant="secondary" onclick={() => (open = false)} disabled={deleting}>
					{m.incident_delete_confirm_cancel()}
				</Button>
				<Button onclick={handleConfirm} disabled={deleting}>
					{deleting ? '...' : m.incident_delete_confirm_submit()}
				</Button>
			</div>
		</div>
	</div>
{/if}
