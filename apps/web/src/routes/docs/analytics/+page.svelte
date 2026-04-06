<script lang="ts">
	import DocSection from '$lib/components/docs/DocSection.svelte';
</script>

<svelte:head>
	<title>Analytics — The Loop Docs</title>
	<meta
		name="description"
		content="Understand the Analytics dashboard: 8 KPI cards, filters, trend charts, and the Rule Effectiveness table."
	/>
</svelte:head>

<h1 class="text-3xl font-bold text-text mb-2">Analytics</h1>
<p class="text-text-muted mb-8">
	The Analytics dashboard gives your team a unified view of incident trends, response performance,
	and scanner effectiveness. All data updates in real time when filters change.
</p>

<DocSection title="Dashboard Overview" id="overview">
	<p class="text-text-muted">
		Navigate to <a href="/analytics/" class="text-accent hover:underline">Analytics</a> from the
		top navigation bar. The dashboard is divided into four areas: KPI cards at the top, filter
		controls, trend charts, and the Rule Effectiveness table at the bottom.
	</p>
	<p class="text-text-muted">
		All charts and cards respond to the same filter set. Changing a filter updates every component
		simultaneously.
	</p>
</DocSection>

<DocSection title="KPI Cards" id="kpi-cards">
	<p class="text-text-muted mb-4">
		The top section shows 8 cards summarizing your incident data for the selected period:
	</p>
	<div class="space-y-4">
		<div class="p-4 rounded-lg bg-bg-surface border border-border">
			<div class="font-semibold text-text mb-1">MTTR — Mean Time to Resolve</div>
			<p class="text-text-muted text-sm">
				The average time from incident creation to the
				<code class="text-accent">closed</code> status. Measured in hours. Lower is better. This is
				your primary indicator of resolution efficiency.
			</p>
		</div>
		<div class="p-4 rounded-lg bg-bg-surface border border-border">
			<div class="font-semibold text-text mb-1">MTTD — Mean Time to Detect</div>
			<p class="text-text-muted text-sm">
				The average time from when an incident is estimated to have started to when it was created in
				The Loop. Lower values indicate faster detection. Requires the incident's
				<em>started_at</em> field to be set.
			</p>
		</div>
		<div class="p-4 rounded-lg bg-bg-surface border border-border">
			<div class="font-semibold text-text mb-1">Total Incidents</div>
			<p class="text-text-muted text-sm">
				Count of all incidents created during the selected period, regardless of status. Use this to
				understand overall incident volume and spot regressions over time.
			</p>
		</div>
		<div class="p-4 rounded-lg bg-bg-surface border border-border">
			<div class="font-semibold text-text mb-1">Open Incidents</div>
			<p class="text-text-muted text-sm">
				Incidents currently in <code class="text-accent">open</code> or
				<code class="text-accent">investigating</code> status. A high open count relative to resolved
				may indicate capacity or process issues.
			</p>
		</div>
		<div class="p-4 rounded-lg bg-bg-surface border border-border">
			<div class="font-semibold text-text mb-1">Resolved Incidents</div>
			<p class="text-text-muted text-sm">
				Incidents in <code class="text-accent">resolved</code> or
				<code class="text-accent">closed</code> status. Together with Open Incidents, this gives you
				your resolution rate.
			</p>
		</div>
		<div class="p-4 rounded-lg bg-bg-surface border border-border">
			<div class="font-semibold text-text mb-1">SLA Breach Rate</div>
			<p class="text-text-muted text-sm">
				Percentage of incidents that exceeded the expected resolution time for their severity level.
				Track this alongside MTTR to understand whether breaches are isolated or systemic.
			</p>
		</div>
		<div class="p-4 rounded-lg bg-bg-surface border border-border">
			<div class="font-semibold text-text mb-1">Severity Distribution</div>
			<p class="text-text-muted text-sm">
				Breakdown of incidents by severity (critical, high, medium, low). A rising proportion of
				critical incidents is a leading indicator of systemic risk.
			</p>
		</div>
		<div class="p-4 rounded-lg bg-bg-surface border border-border">
			<div class="font-semibold text-text mb-1">Team Workload</div>
			<p class="text-text-muted text-sm">
				Distribution of incidents across teams. Use this to identify overloaded teams and balance
				on-call responsibilities. Drill into a specific team using the Team filter.
			</p>
		</div>
	</div>
</DocSection>

<DocSection title="Filters" id="filters">
	<p class="text-text-muted mb-2">Five filters are available, all applied simultaneously:</p>
	<ul class="list-disc list-inside text-text-muted space-y-2 ml-2">
		<li>
			<strong class="text-text">Period</strong> — preset time ranges: Last 7 days, Last 30 days, Last
			90 days, or Custom. Custom period lets you pick a start and end date.
		</li>
		<li>
			<strong class="text-text">Team</strong> — filter to incidents owned by one or more teams.
			Multi-select. Leave empty to include all teams.
		</li>
		<li>
			<strong class="text-text">Category</strong> — filter by root cause category: code pattern,
			infrastructure, process breakdown, third-party, or unknown.
		</li>
		<li>
			<strong class="text-text">Severity</strong> — filter by severity level: critical, high,
			medium, low. Multi-select.
		</li>
		<li>
			<strong class="text-text">Status</strong> — filter by incident status: open, investigating,
			resolved, closed.
		</li>
	</ul>
	<p class="text-text-muted">
		To filter MTTR by team: open the <strong class="text-text">Team</strong> dropdown, select the
		team, and all KPI cards (including MTTR) update to reflect only that team's incidents.
	</p>
</DocSection>

<DocSection title="Trend Charts" id="charts">
	<p class="text-text-muted">
		<strong class="text-text">Pattern Timeline</strong> — a weekly bar chart showing incident count
		over time, color-coded by root cause category. Use this to detect recurring patterns (e.g., a
		spike every deployment week).
	</p>
	<p class="text-text-muted">
		<strong class="text-text">Severity Trend</strong> — a stacked area chart showing how severity
		distribution changes week by week. A growing critical area suggests increasing systemic risk.
	</p>
</DocSection>

<DocSection title="Rule Effectiveness Table" id="rule-effectiveness">
	<p class="text-text-muted">
		The table at the bottom lists each Semgrep rule that has triggered a finding in your
		repositories, along with the number of findings and the incidents those findings preceded. This
		connects scanner output to real incident impact — rules with many findings and subsequent
		incidents are the highest-ROI rules to enforce strictly.
	</p>
</DocSection>
