<script lang="ts">
  import { Section, Container } from '$lib/ui';
  import {
    how_headline,
    how_description,
    how_flow_incident,
    how_flow_kb,
    how_flow_rule,
    how_flow_protected,
    how_flow_closes,
  } from '$lib/paraglide/messages.js';
</script>

<Section id="how-it-works">
  <Container>
    <h2 class="text-4xl md:text-5xl font-bold text-text">
      {how_headline()}
    </h2>

    <!-- Desktop: horizontal flow -->
    <div class="mt-12 hidden md:block">
      <svg viewBox="0 0 960 160" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto">
        <!-- Step 1: Incident -->
        <rect x="10" y="40" width="150" height="60" rx="12" fill="#141416" stroke="#0066FF" stroke-width="2" />
        <text x="85" y="76" text-anchor="middle" fill="#f5f5f7" font-size="14" font-weight="600" font-family="var(--font-sans)">{how_flow_incident()}</text>

        <!-- Arrow 1→2 -->
        <line x1="160" y1="70" x2="195" y2="70" stroke="#0066FF" stroke-width="2" />
        <polygon points="195,65 205,70 195,75" fill="#0066FF" />

        <!-- Step 2: Knowledge Base -->
        <rect x="205" y="40" width="150" height="60" rx="12" fill="#141416" stroke="#0066FF" stroke-width="2" />
        <text x="280" y="76" text-anchor="middle" fill="#f5f5f7" font-size="14" font-weight="600" font-family="var(--font-sans)">{how_flow_kb()}</text>

        <!-- Arrow 2→3 -->
        <line x1="355" y1="70" x2="390" y2="70" stroke="#0066FF" stroke-width="2" />
        <polygon points="390,65 400,70 390,75" fill="#0066FF" />

        <!-- Step 3: Rule / Advisory -->
        <rect x="400" y="40" width="150" height="60" rx="12" fill="#141416" stroke="#0066FF" stroke-width="2" />
        <text x="475" y="76" text-anchor="middle" fill="#f5f5f7" font-size="14" font-weight="600" font-family="var(--font-sans)">{how_flow_rule()}</text>

        <!-- Arrow 3→4 -->
        <line x1="550" y1="70" x2="585" y2="70" stroke="#0066FF" stroke-width="2" />
        <polygon points="585,65 595,70 585,75" fill="#0066FF" />

        <!-- Step 4: Code Protected -->
        <rect x="595" y="40" width="150" height="60" rx="12" fill="#141416" stroke="#0066FF" stroke-width="2" />
        <text x="670" y="76" text-anchor="middle" fill="#f5f5f7" font-size="14" font-weight="600" font-family="var(--font-sans)">{how_flow_protected()}</text>

        <!-- Arrow 4→5 -->
        <line x1="745" y1="70" x2="780" y2="70" stroke="#0066FF" stroke-width="2" />
        <polygon points="780,65 790,70 780,75" fill="#0066FF" />

        <!-- Step 5: Loop Closes -->
        <rect x="790" y="40" width="150" height="60" rx="12" fill="#141416" stroke="#0066FF" stroke-width="2" />
        <text x="865" y="76" text-anchor="middle" fill="#f5f5f7" font-size="14" font-weight="600" font-family="var(--font-sans)">{how_flow_closes()}</text>

        <!-- Return arrow (loop back) -->
        <path d="M865,100 L865,140 Q865,150 855,150 L95,150 Q85,150 85,140 L85,100"
              fill="none" stroke="#0066FF" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.5" />
        <polygon points="80,105 85,95 90,105" fill="#0066FF" opacity="0.5" />
      </svg>
    </div>

    <!-- Mobile: vertical flow -->
    <div class="mt-10 block md:hidden">
      <svg viewBox="0 0 240 520" xmlns="http://www.w3.org/2000/svg" class="w-full max-w-[240px] mx-auto h-auto">
        <!-- Step 1: Incident -->
        <rect x="20" y="10" width="200" height="50" rx="12" fill="#141416" stroke="#0066FF" stroke-width="2" />
        <text x="120" y="41" text-anchor="middle" fill="#f5f5f7" font-size="14" font-weight="600" font-family="var(--font-sans)">{how_flow_incident()}</text>

        <!-- Arrow 1→2 -->
        <line x1="120" y1="60" x2="120" y2="85" stroke="#0066FF" stroke-width="2" />
        <polygon points="115,85 120,95 125,85" fill="#0066FF" />

        <!-- Step 2: Knowledge Base -->
        <rect x="20" y="95" width="200" height="50" rx="12" fill="#141416" stroke="#0066FF" stroke-width="2" />
        <text x="120" y="126" text-anchor="middle" fill="#f5f5f7" font-size="14" font-weight="600" font-family="var(--font-sans)">{how_flow_kb()}</text>

        <!-- Arrow 2→3 -->
        <line x1="120" y1="145" x2="120" y2="170" stroke="#0066FF" stroke-width="2" />
        <polygon points="115,170 120,180 125,170" fill="#0066FF" />

        <!-- Step 3: Rule / Advisory -->
        <rect x="20" y="180" width="200" height="50" rx="12" fill="#141416" stroke="#0066FF" stroke-width="2" />
        <text x="120" y="211" text-anchor="middle" fill="#f5f5f7" font-size="14" font-weight="600" font-family="var(--font-sans)">{how_flow_rule()}</text>

        <!-- Arrow 3→4 -->
        <line x1="120" y1="230" x2="120" y2="255" stroke="#0066FF" stroke-width="2" />
        <polygon points="115,255 120,265 125,255" fill="#0066FF" />

        <!-- Step 4: Code Protected -->
        <rect x="20" y="265" width="200" height="50" rx="12" fill="#141416" stroke="#0066FF" stroke-width="2" />
        <text x="120" y="296" text-anchor="middle" fill="#f5f5f7" font-size="14" font-weight="600" font-family="var(--font-sans)">{how_flow_protected()}</text>

        <!-- Arrow 4→5 -->
        <line x1="120" y1="315" x2="120" y2="340" stroke="#0066FF" stroke-width="2" />
        <polygon points="115,340 120,350 125,340" fill="#0066FF" />

        <!-- Step 5: Loop Closes -->
        <rect x="20" y="350" width="200" height="50" rx="12" fill="#141416" stroke="#0066FF" stroke-width="2" />
        <text x="120" y="381" text-anchor="middle" fill="#f5f5f7" font-size="14" font-weight="600" font-family="var(--font-sans)">{how_flow_closes()}</text>

        <!-- Return arrow (loop back) -->
        <path d="M20,375 L10,375 Q5,375 5,365 L5,25 Q5,15 15,15 L20,15"
              fill="none" stroke="#0066FF" stroke-width="1.5" stroke-dasharray="6,4" opacity="0.5" />
        <polygon points="15,20 20,10 25,20" fill="#0066FF" opacity="0.5" />
      </svg>
    </div>

    <p class="mt-10 text-lg text-text-muted max-w-3xl">
      {how_description()}
    </p>
  </Container>
</Section>
