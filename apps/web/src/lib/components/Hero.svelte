<script lang="ts">
  import { Section, Container } from '$lib/ui';
  import WaitlistForm from './WaitlistForm.svelte';
  import { hero_headline, hero_subheadline, hero_branding, hero_product_name, hero_scroll_hint } from '$lib/paraglide/messages.js';
  import { onMount } from 'svelte';

  let showChevron = $state(true);
  let heroEl: HTMLElement | undefined = $state();

  onMount(() => {
    if (!heroEl) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        showChevron = entry.isIntersecting;
      },
      { threshold: 0.1 }
    );
    observer.observe(heroEl);
    return () => observer.disconnect();
  });
</script>

<div bind:this={heroEl}>
  <Section id="hero" hero>
    <Container class="text-center">
      <p class="text-lg md:text-xl font-semibold text-accent tracking-wide uppercase">
        {hero_product_name()}
      </p>

      <h1 class="mt-4 text-5xl md:text-6xl lg:text-7xl font-bold text-text leading-tight">
        {hero_headline()}
      </h1>

      <p class="mt-6 text-lg md:text-xl text-text-muted max-w-3xl mx-auto">
        {hero_subheadline()}
      </p>

      <div class="mt-10 max-w-lg mx-auto">
        <WaitlistForm />
      </div>

      <p class="mt-6 text-sm text-text-muted">{hero_branding()}</p>

      {#if showChevron}
        <button
          onclick={() => document.getElementById('problem')?.scrollIntoView({ behavior: 'smooth' })}
          aria-label={hero_scroll_hint()}
          class="mt-8 animate-bounce text-text-subtle hover:text-text transition-colors"
        >
          <svg class="w-6 h-6 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      {/if}
    </Container>
  </Section>
</div>
