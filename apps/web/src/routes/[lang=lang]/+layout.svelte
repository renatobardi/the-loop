<script lang="ts">
  import type { Snippet } from 'svelte';
  import { page } from '$app/stores';
  import LanguageSelector from '$lib/components/LanguageSelector.svelte';

  let { children }: { children: Snippet } = $props();

  const locales = ['en', 'pt', 'es'];
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
  <title>{titles[$page.params.lang] ?? titles.en}</title>
  <meta name="description" content={descriptions[$page.params.lang] ?? descriptions.en} />

  <meta property="og:title" content={titles[$page.params.lang] ?? titles.en} />
  <meta property="og:description" content={descriptions[$page.params.lang] ?? descriptions.en} />
  <meta property="og:type" content="website" />
  <meta property="og:url" content={`https://loop.oute.pro/${$page.params.lang}/`} />
  <meta property="og:image" content="https://loop.oute.pro/og-image.png" />
  <meta name="twitter:card" content="summary_large_image" />

  {#each locales as locale (locale)}
    <link rel="alternate" hreflang={locale} href={`https://loop.oute.pro/${locale}/`} />
  {/each}
  <link rel="alternate" hreflang="x-default" href="https://loop.oute.pro/en/" />

  <html lang={$page.params.lang} />
</svelte:head>

<div class="fixed top-4 right-4 z-50">
  <LanguageSelector />
</div>

{@render children()}
