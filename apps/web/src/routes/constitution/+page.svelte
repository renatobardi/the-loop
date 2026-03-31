<script lang="ts">
  import ConstitutionHero from '$lib/components/ConstitutionHero.svelte';
  import MandatesGrid from '$lib/components/MandatesGrid.svelte';
  import TransparencySection from '$lib/components/TransparencySection.svelte';
  import WaitlistForm from '$lib/components/WaitlistForm.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { Section, Container } from '$lib/ui';
</script>

<svelte:head>
  <title>The Loop — 12 Immutable Engineering Mandates</title>
  <meta name="description" content="The engineering principles that govern The Loop. Trunk-based dev, rigorous CI, mandated security, clean code, and more." />

  <meta property="og:title" content="The Loop — 12 Immutable Engineering Mandates" />
  <meta property="og:description" content="The engineering principles that govern The Loop. Trunk-based dev, rigorous CI, mandated security, clean code, and more." />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://loop.oute.pro/constitution/" />
  <meta property="og:image" content="https://loop.oute.pro/og-image.png" />
  <meta name="twitter:card" content="summary_large_image" />
</svelte:head>

<main id="main-content">
  <ConstitutionHero />
  <MandatesGrid />
  <TransparencySection />

  <Section id="waitlist">
    <Container class="text-center">
      <h2 class="text-4xl md:text-5xl font-bold text-text">
        Be the first to close the loop.
      </h2>

      <p class="mt-4 text-lg md:text-xl text-text-muted">
        Join the waitlist and get early access when we launch.
      </p>

      <div class="mt-8 max-w-lg mx-auto">
        <WaitlistForm source="constitution" />
      </div>
    </Container>
  </Section>
</main>

<Footer />
