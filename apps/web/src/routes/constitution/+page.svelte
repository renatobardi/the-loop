<script lang="ts">
  import { languageTag } from '$lib/paraglide/runtime.js';
  import { i18n } from '$lib/i18n';
  import {
    constitution_meta_title,
    constitution_meta_description
  } from '$lib/paraglide/messages.js';
  import { waitlist_headline, waitlist_subheadline } from '$lib/paraglide/messages.js';
  import ConstitutionHero from '$lib/components/ConstitutionHero.svelte';
  import MandatesGrid from '$lib/components/MandatesGrid.svelte';
  import TransparencySection from '$lib/components/TransparencySection.svelte';
  import WaitlistForm from '$lib/components/WaitlistForm.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { Section, Container } from '$lib/ui';

  const BASE_URL = 'https://loop.oute.pro';
</script>

<svelte:head>
  <title>{constitution_meta_title()}</title>
  <meta name="description" content={constitution_meta_description()} />

  <meta property="og:title" content={constitution_meta_title()} />
  <meta property="og:description" content={constitution_meta_description()} />
  <meta property="og:type" content="website" />
  <meta property="og:url" content={`${BASE_URL}${i18n.resolveRoute('/constitution', languageTag())}/`} />
  <meta property="og:image" content={`${BASE_URL}/og-image.png`} />
  <meta name="twitter:card" content="summary_large_image" />

  <link rel="alternate" hreflang="en" href={`${BASE_URL}${i18n.resolveRoute('/constitution', 'en')}/`} />
  <link rel="alternate" hreflang="pt" href={`${BASE_URL}${i18n.resolveRoute('/constitution', 'pt')}/`} />
  <link rel="alternate" hreflang="es" href={`${BASE_URL}${i18n.resolveRoute('/constitution', 'es')}/`} />
  <link rel="alternate" hreflang="x-default" href={`${BASE_URL}${i18n.resolveRoute('/constitution', 'en')}/`} />
</svelte:head>

<main id="main-content">
  <ConstitutionHero />
  <MandatesGrid />
  <TransparencySection />

  <Section id="waitlist">
    <Container class="text-center">
      <h2 class="text-4xl md:text-5xl font-bold text-text">
        {waitlist_headline()}
      </h2>

      <p class="mt-4 text-lg md:text-xl text-text-muted">
        {waitlist_subheadline()}
      </p>

      <div class="mt-8 max-w-lg mx-auto">
        <WaitlistForm source="constitution" />
      </div>
    </Container>
  </Section>
</main>

<Footer />
