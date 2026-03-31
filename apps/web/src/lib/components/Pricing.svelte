<script lang="ts">
  import { Section, Container, Card, Button, Badge } from '$lib/ui';

  const plans = [
    {
      name: 'Free',
      price: '$0',
      scans: '100 scans/month',
      features: ['L1 + L2 + L3', 'Community'],
      highlighted: false,
      popular: false,
      cta: { text: 'Join the waitlist', href: '#waitlist' },
    },
    {
      name: 'Pay-as-you-go',
      price: 'Pay per scan batch',
      scans: 'Buy in batches',
      features: ['L1 + L2 + L3', 'Email'],
      highlighted: true,
      popular: true,
      cta: { text: 'Join the waitlist', href: '#waitlist' },
    },
    {
      name: 'Enterprise',
      price: 'Contact us',
      scans: 'Unlimited',
      features: ['L1 + L2 + L3', 'Dedicated', 'SSO/SAML', 'Audit logs'],
      highlighted: false,
      popular: false,
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
      {#each plans as plan (plan.name)}
        <Card class={plan.highlighted ? 'border-accent shadow-glow' : ''}>
          {#if plan.popular}
            <Badge variant="accent" class="mb-4">Most popular</Badge>
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
            <a href={plan.cta.href}>
              <Button variant={plan.highlighted ? 'primary' : 'secondary'} class="w-full">{plan.cta.text}</Button>
            </a>
          </div>
        </Card>
      {/each}
    </div>
  </Container>
</Section>
