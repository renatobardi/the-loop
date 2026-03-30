<script lang="ts">
  import '../app.css';
  import type { Snippet } from 'svelte';
  import { ParaglideJS } from '@inlang/paraglide-sveltekit';
  import { i18n } from '$lib/i18n';
  import { languageTag } from '$lib/paraglide/runtime.js';
  import LanguageSelector from '$lib/components/LanguageSelector.svelte';

  let { children }: { children: Snippet } = $props();

  const titles: Record<string, string> = {
    en: 'The Loop — Eliminate production incidents before they happen',
    pt: 'The Loop — Elimine incidentes de produção antes que aconteçam',
    es: 'The Loop — Elimina incidentes de producción antes de que ocurran'
  };
  const descriptions: Record<string, string> = {
    en: 'Close the loop between post-mortems and code. Transform incident knowledge into active guardrails in your CI/CD pipeline.',
    pt: 'Feche o ciclo entre post-mortems e código. Transforme conhecimento de incidentes em guardrails ativos no seu pipeline de CI/CD.',
    es: 'Cierra el ciclo entre post-mortems y código. Transforma el conocimiento de incidentes en guardrails activos en tu pipeline de CI/CD.'
  };
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

  <title>{titles[languageTag()] ?? titles.en}</title>
  <meta name="description" content={descriptions[languageTag()] ?? descriptions.en} />

  <meta property="og:title" content={titles[languageTag()] ?? titles.en} />
  <meta property="og:description" content={descriptions[languageTag()] ?? descriptions.en} />
  <meta property="og:type" content="website" />
  <meta property="og:url" content={`https://loop.oute.pro/${languageTag()}/`} />
  <meta property="og:image" content="https://loop.oute.pro/og-image.png" />
  <meta name="twitter:card" content="summary_large_image" />
</svelte:head>

<ParaglideJS {i18n}>
  <div class="fixed top-4 right-4 z-50">
    <LanguageSelector />
  </div>
  {@render children()}
</ParaglideJS>
