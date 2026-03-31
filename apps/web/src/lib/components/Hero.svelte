<script lang="ts">
  import { Section, Container } from '$lib/ui';
  import WaitlistForm from './WaitlistForm.svelte';
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
        The Loop
      </p>

      <h1 class="mt-4 text-5xl md:text-6xl lg:text-7xl font-bold text-text leading-tight">
        Eliminate production incidents before they happen.
      </h1>

      <p class="mt-6 text-lg md:text-xl text-text-muted max-w-3xl mx-auto">
        Close the loop between post-mortems and code. The Loop transforms incident knowledge into active guardrails in your CI/CD pipeline.
      </p>

      <div class="mt-10 max-w-lg mx-auto">
        <WaitlistForm source="hero" />
      </div>

      <p class="mt-6 text-sm text-text-muted">by Oute</p>

      {#if showChevron}
        <button
          onclick={() => document.getElementById('problem')?.scrollIntoView({ behavior: 'smooth' })}
          aria-label="Scroll down"
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
