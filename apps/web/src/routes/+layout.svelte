<script lang="ts">
  import '../app.css';
  import type { Snippet } from 'svelte';
  import { ParaglideJS } from '@inlang/paraglide-sveltekit';
  import { i18n } from '$lib/i18n';
  import { languageTag } from '$lib/paraglide/runtime.js';
  import { meta_title, meta_description } from '$lib/paraglide/messages.js';
  import { SkipLink, Navbar } from '$lib/ui';

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

  <title>{meta_title()}</title>
  <meta name="description" content={meta_description()} />

  <meta property="og:title" content={meta_title()} />
  <meta property="og:description" content={meta_description()} />
  <meta property="og:type" content="website" />
  <meta property="og:url" content={`https://loop.oute.pro/${languageTag()}/`} />
  <meta property="og:image" content="https://loop.oute.pro/og-image.png" />
  <meta name="twitter:card" content="summary_large_image" />

  <link rel="alternate" hreflang="x-default" href="https://loop.oute.pro/en/" />
</svelte:head>

<ParaglideJS {i18n}>
  <SkipLink />
  <Navbar />
  <div class="pt-14">
    {@render children()}
  </div>
</ParaglideJS>
