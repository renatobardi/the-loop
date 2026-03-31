<script lang="ts">
  import '../app.css';
  import type { Snippet } from 'svelte';
  import { SkipLink, Navbar } from '$lib/ui';

  let { children }: { children: Snippet } = $props();

  const META_TITLE = 'The Loop — Eliminate production incidents before they happen';
  const META_DESCRIPTION =
    'Close the loop between post-mortems and code. The Loop turns lessons learned into prevention rules enforced at merge time.';
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

  <title>{META_TITLE}</title>
  <meta name="description" content={META_DESCRIPTION} />

  <meta property="og:title" content={META_TITLE} />
  <meta property="og:description" content={META_DESCRIPTION} />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://loop.oute.pro/" />
  <meta property="og:image" content="https://loop.oute.pro/og-image.png" />
  <meta name="twitter:card" content="summary_large_image" />
</svelte:head>

<SkipLink />
<Navbar />
<div class="pt-14">
  {@render children()}
</div>
