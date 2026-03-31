<script lang="ts">
  import { Section, Container } from '$lib/ui';
  import WaitlistForm from './WaitlistForm.svelte';
</script>

<Section id="waitlist">
  <Container class="text-center">
    <h2 class="text-4xl md:text-5xl font-bold text-text">
      Be the first to close the loop.
    </h2>

    <p class="mt-4 text-lg md:text-xl text-text-muted">
      Join the waitlist and get early access when we launch.
    </p>

    <div class="mt-8 max-w-lg mx-auto">
      <WaitlistForm source="cta-bottom" />
    </div>
  </Container>
</Section>
