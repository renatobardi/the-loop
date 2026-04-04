# Analytics Dashboard — User Guide

The Loop's analytics dashboard turns incident postmortem data into actionable insights. It answers: *which root causes keep recurring, which teams are most affected, and is the trend improving or worsening?*

## Navigation

Go to **Incidents → Analytics** (top nav) or navigate directly to `/incidents/analytics/`.

Authentication is required. If you're not logged in, you'll be redirected to `/login/`.

---

## Filters

All four charts update simultaneously when you change any filter. Filters are persisted in the URL — you can bookmark or share a filtered view.

| Filter | Options | Notes |
|--------|---------|-------|
| **Period** | Week / Month / Quarter / Custom | Defaults to last month |
| **Team** | Any team with incidents in the current period | List updates with period changes |
| **Category** | Code Pattern / Infrastructure / Process Breakdown / Third Party / Unknown | |
| **Status** | All / Resolved / Unresolved | |
| **Custom dates** | Start + End (YYYY-MM-DD) | Available when Period = Custom |

Click **Apply** to run the query. Click **Reset** to clear all filters back to defaults.

While filters are loading, skeleton cards pulse — no blank flash or stale data shown.

---

## Summary Card

Shows four numbers for the selected period and filters:

- **Total** — number of postmortems in the period
- **Resolved** — incidents with a `resolved_at` timestamp
- **Unresolved** — incidents still open
- **Avg Resolution** — mean days from postmortem creation to incident resolution; shows `N/A` when no incidents are resolved in the period

---

## Category Heatmap

Horizontal bar chart with one row per root cause category.

**Columns:**
- Bar length = percentage share of total incidents in the period
- Count and percentage shown on the right
- Bar color: red = avg severity ≥ 0.9 (mostly `error` severity postmortems), yellow = below threshold

**5 root cause categories:**

| Category | Meaning |
|----------|---------|
| `code_pattern` | Anti-pattern in application code (SQL injection, bare except, etc.) |
| `infrastructure` | Platform/infra failure (network, database, disk) |
| `process_breakdown` | Missing runbook, unclear ownership, process gap |
| `third_party` | External dependency failure (SaaS, vendor API) |
| `unknown` | Not yet categorized |

---

## Team Heatmap

Table of teams sorted by incident count (descending by default). Click the **Count** header to reverse sort.

**Columns:**
- **Team** — `team_responsible` from the postmortem
- **Count** — total postmortems for the team in the period
- **Top Categories** — up to 3 most frequent root causes as badge pills
- **Avg Resolution** — mean days to resolve; `N/A` if no resolved incidents

---

## Pattern Timeline

Line chart showing weekly incident counts over the selected period, with one colored line per root cause category.

- **X-axis** — calendar weeks; tick labels shown every ~4 weeks (monthly)
- **Y-axis** — incident count
- **Hover / focus a dot** — tooltip shows the exact week, total count, and per-category breakdown
- All 5 categories are always plotted; lines with zero incidents are flat along the x-axis

**Color legend** (displayed above the chart):

| Color | Category |
|-------|----------|
| Blue | Code Pattern |
| Red | Infrastructure |
| Yellow | Process Breakdown |
| Purple | Third Party |
| Gray | Unknown |

---

## Empty State

When no incidents match the selected filters, the dashboard shows:

> **No incidents in this period**
> Try expanding the selected period or removing filters.

This is expected behavior — it means your team had zero qualifying incidents in that window.

---

## Error State

If the API fails to load, an error banner appears with a **Retry** button. This is rare; the most common cause is an expired auth session. Try refreshing the page to re-authenticate.

---

## API Access

All four charts are powered by dedicated endpoints that can also be queried directly:

```bash
TOKEN="<firebase-id-token>"
BASE="https://theloop-api-1090621437043.us-central1.run.app/api/v1/incidents/analytics"

curl -H "Authorization: Bearer $TOKEN" "$BASE/summary?period=quarter"
curl -H "Authorization: Bearer $TOKEN" "$BASE/by-category?period=month&status=resolved"
curl -H "Authorization: Bearer $TOKEN" "$BASE/by-team?period=quarter&team=backend"
curl -H "Authorization: Bearer $TOKEN" "$BASE/timeline?period=custom&start_date=2026-01-01&end_date=2026-03-31"
```

See [README.md](./README.md#analytics-dashboard) for the full parameter reference.
