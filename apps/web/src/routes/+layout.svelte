<script lang="ts">
  import '../app.css';
  import type { Snippet } from 'svelte';
  import { ParaglideJS } from '@inlang/paraglide-sveltekit';
  import { i18n } from '$lib/i18n';

  let { children }: { children: Snippet } = $props();
</script>

<svelte:head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin="anonymous" />
  <link
    rel="preload"
    href="https://cdn.jsdelivr.net/npm/geist@1.3.1/dist/fonts/geist-sans/Geist-Bold.woff2"
    as="font"
    type="font/woff2"
    crossorigin="anonymous"
  />
</svelte:head>

<ParaglideJS {i18n}>
  {@render children()}
</ParaglideJS>
