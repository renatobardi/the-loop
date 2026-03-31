<script lang="ts">
	import { Container } from '$lib/ui';

	let { children } = $props();
</script>

<Container>
	{@render children?.()}
</Container>
