<script lang="ts">
  import type { Snippet } from 'svelte';
  import { type Action } from 'svelte/action';

  let {
    children,
    id = '',
    class: className = '',
    ...restProps
  }: {
    children: Snippet;
    id?: string;
    class?: string;
    [key: string]: unknown;
  } = $props();

  const reveal: Action = (node) => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
      node.classList.add('revealed');
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            node.classList.add('revealed');
            observer.unobserve(node);
          }
        });
      },
      { threshold: 0.1 }
    );

    observer.observe(node);
    return {
      destroy() {
        observer.disconnect();
      }
    };
  };
</script>

<section
  {id}
  class="section-reveal min-h-screen flex items-center py-20 lg:py-32 {className}"
  use:reveal
  {...restProps}
>
  {@render children()}
</section>

<style>
  .section-reveal {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.6s ease-out, transform 0.6s ease-out;
  }

  .section-reveal:global(.revealed) {
    opacity: 1;
    transform: translateY(0);
  }

  @media (prefers-reduced-motion: reduce) {
    .section-reveal {
      opacity: 1;
      transform: none;
      transition: none;
    }
  }
</style>
