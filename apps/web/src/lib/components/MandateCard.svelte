<script lang="ts">
  import { Card } from '$lib/ui';

  let {
    number,
    title,
    description
  }: {
    number: string;
    title: string;
    description: string;
  } = $props();
</script>

<Card>
  <p class="text-3xl font-bold text-accent">{number}</p>
  <h3 class="mt-2 text-lg font-bold text-text">{title}</h3>
  <p class="mt-2 text-sm text-text-muted leading-relaxed">{description}</p>
</Card>
