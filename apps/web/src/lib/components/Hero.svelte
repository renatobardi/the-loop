<script lang="ts">
  import { Section, Container } from '$lib/ui';
  import WaitlistForm from './WaitlistForm.svelte';
  import { hero_headline, hero_subheadline, hero_branding } from '$lib/paraglide/messages.js';
</script>

<Section id="hero" class="min-h-screen">
  <Container class="text-center">
    <h1 class="text-5xl md:text-6xl lg:text-7xl font-bold text-text leading-tight">
      {hero_headline()}
    </h1>

    <p class="mt-6 text-lg md:text-xl text-text-muted max-w-3xl mx-auto">
      {hero_subheadline()}
    </p>

    <div class="mt-10 max-w-lg mx-auto">
      <WaitlistForm />
    </div>

    <p class="mt-6 text-sm text-text-subtle">{hero_branding()}</p>
  </Container>
</Section>
