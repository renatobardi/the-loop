<script lang="ts">
  import { Section, Container, Card, Button, Badge } from '$lib/ui';
  import {
    pricing_headline,
    pricing_free_name,
    pricing_free_price,
    pricing_free_scans,
    pricing_payg_name,
    pricing_payg_price,
    pricing_payg_scans,
    pricing_enterprise_name,
    pricing_enterprise_price,
    pricing_enterprise_scans,
    pricing_layers,
    pricing_support_community,
    pricing_support_email,
    pricing_support_dedicated,
    pricing_sso,
    pricing_audit,
    pricing_contact_cta,
    pricing_join_waitlist,
    pricing_popular_badge,
  } from '$lib/paraglide/messages.js';

  let plans = $derived([
    {
      name: pricing_free_name(),
      price: pricing_free_price(),
      scans: pricing_free_scans(),
      features: [pricing_layers(), pricing_support_community()],
      highlighted: false,
      popular: false,
      cta: { text: pricing_join_waitlist(), href: '#waitlist' },
    },
    {
      name: pricing_payg_name(),
      price: pricing_payg_price(),
      scans: pricing_payg_scans(),
      features: [pricing_layers(), pricing_support_email()],
      highlighted: true,
      popular: true,
      cta: { text: pricing_join_waitlist(), href: '#waitlist' },
    },
    {
      name: pricing_enterprise_name(),
      price: pricing_enterprise_price(),
      scans: pricing_enterprise_scans(),
      features: [pricing_layers(), pricing_support_dedicated(), pricing_sso(), pricing_audit()],
      highlighted: false,
      popular: false,
      cta: { text: pricing_contact_cta(), href: 'mailto:loop@oute.pro' },
    },
  ]);
</script>

<Section id="pricing">
  <Container>
    <h2 class="text-4xl md:text-5xl font-bold text-center mb-12 lg:mb-16">
      {pricing_headline()}
    </h2>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
      {#each plans as plan (plan.name)}
        <Card class={plan.highlighted ? 'border-accent shadow-glow' : ''}>
          {#if plan.popular}
            <Badge variant="accent" class="mb-4">{pricing_popular_badge()}</Badge>
          {/if}
          <h3 class="text-xl font-semibold">{plan.name}</h3>
          <p class="text-3xl font-bold mt-2">{plan.price}</p>
          <p class="text-text-muted text-sm mt-1">{plan.scans}</p>

          <ul class="mt-6 space-y-3">
            {#each plan.features as feature (feature)}
              <li class="flex items-center gap-2 text-text-muted">
                <svg class="w-5 h-5 text-accent shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                {feature}
              </li>
            {/each}
          </ul>

          <div class="mt-8">
            <!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- anchor/mailto link -->
            <a href={plan.cta.href}>
              <Button variant={plan.highlighted ? 'primary' : 'secondary'} class="w-full">{plan.cta.text}</Button>
            </a>
          </div>
        </Card>
      {/each}
    </div>
  </Container>
</Section>
