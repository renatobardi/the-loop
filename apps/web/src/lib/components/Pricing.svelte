<script lang="ts">
  import { Section, Container, Card, Button } from '$lib/ui';

  const plans = [
    {
      name: 'Free',
      price: '$0',
      scans: '100 scans/month',
      features: ['L1 + L2 + L3', 'Community support'],
      highlighted: false,
      cta: null,
    },
    {
      name: 'Pay-as-you-go',
      price: 'Pay per scan batch',
      scans: 'Buy in batches',
      features: ['L1 + L2 + L3', 'Email support'],
      highlighted: false,
      cta: null,
    },
    {
      name: 'Enterprise',
      price: 'Contact us',
      scans: 'Unlimited',
      features: ['L1 + L2 + L3', 'Dedicated support', 'SSO / SAML', 'Audit logs'],
      highlighted: true,
      cta: { text: 'Contact us', href: 'mailto:loop@oute.pro' },
    },
  ];
</script>

<Section id="pricing">
  <Container>
    <h2 class="text-4xl md:text-5xl font-bold text-center mb-12 lg:mb-16">
      Start free. Pay as you grow.
    </h2>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
      {#each plans as plan}
        <Card class={plan.highlighted ? 'border-accent/30 shadow-[0_0_24px_rgba(99,102,241,0.08)]' : ''}>
          <h3 class="text-xl font-semibold">{plan.name}</h3>
          <p class="text-3xl font-bold mt-2">{plan.price}</p>
          <p class="text-text-muted text-sm mt-1">{plan.scans}</p>

          <ul class="mt-6 space-y-3">
            {#each plan.features as feature}
              <li class="flex items-center gap-2 text-text-muted">
                <svg class="w-5 h-5 text-accent shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                {feature}
              </li>
            {/each}
          </ul>

          {#if plan.cta}
            <div class="mt-8">
              <a href={plan.cta.href}>
                <Button variant="secondary" class="w-full">{plan.cta.text}</Button>
              </a>
            </div>
          {/if}
        </Card>
      {/each}
    </div>
  </Container>
</Section>
