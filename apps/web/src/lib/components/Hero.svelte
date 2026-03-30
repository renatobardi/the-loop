<script lang="ts">
  import { Section, Container } from '$lib/ui';
  import WaitlistForm from './WaitlistForm.svelte';
</script>

<Section id="hero" class="min-h-screen">
  <Container class="text-center">
    <h1 class="text-5xl md:text-6xl lg:text-7xl font-bold text-text leading-tight">
      Eliminate production incidents before they happen.
    </h1>

    <p class="mt-6 text-lg md:text-xl text-text-muted max-w-3xl mx-auto">
      Close the loop between post-mortems and code. The Loop transforms incident knowledge into active guardrails in your CI/CD pipeline.
    </p>

    <div class="mt-10 max-w-lg mx-auto">
      <WaitlistForm />
    </div>

    <p class="mt-6 text-sm text-text-subtle">by Oute</p>
  </Container>
</Section>
