<script lang="ts">
  import { Section, Container } from '$lib/ui';
  import WaitlistForm from './WaitlistForm.svelte';
  import { waitlist_headline, waitlist_subheadline } from '$lib/paraglide/messages.js';
</script>

<Section id="waitlist">
  <Container class="text-center">
    <h2 class="text-4xl md:text-5xl font-bold text-text">
      {waitlist_headline()}
    </h2>

    <p class="mt-4 text-lg md:text-xl text-text-muted">
      {waitlist_subheadline()}
    </p>

    <div class="mt-8 max-w-lg mx-auto">
      <WaitlistForm />
    </div>
  </Container>
</Section>
