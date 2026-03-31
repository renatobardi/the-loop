<script lang="ts">
  import Hero from '$lib/components/Hero.svelte';
  import Problem from '$lib/components/Problem.svelte';
  import Layers from '$lib/components/Layers.svelte';
  import HowItWorks from '$lib/components/HowItWorks.svelte';
  import Integrations from '$lib/components/Integrations.svelte';
  import Pricing from '$lib/components/Pricing.svelte';
  import WaitlistCta from '$lib/components/WaitlistCta.svelte';
  import Footer from '$lib/components/Footer.svelte';
</script>

<main id="main-content">
  <Hero />
  <Problem />
  <Layers />
  <HowItWorks />
  <Integrations />
  <Pricing />
  <WaitlistCta />
</main>

<Footer />
