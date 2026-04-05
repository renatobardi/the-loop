# Spec-019 Validation Plan — Analytics Dashboard

**Status:** Dashboard deployed, needs test data for validation  
**Created:** 2026-04-05  
**Target:** Full dashboard validation before closure

---

## Phase 1: Seed Test Data (LOCAL FIRST, then PRODUCTION)

### 1a. Test locally first

```bash
# Set local DATABASE_URL (Cloud SQL Proxy)
export DATABASE_URL="postgresql+asyncpg://theloop:theloop@localhost:5433/theloop"

# Run seed script with 200 test incidents
cd /Users/bardi/Projetos/the-loop
python3 scripts/seed_analytics_testdata.py --count 200

# Expected output:
# ✅ Seeded 200 incidents + 200 postmortems
# Distribution by team: Backend: 40, Frontend: 40, DevOps: 40, Platform: 40, QA: 40
# Distribution by category: code_pattern: 40, infrastructure: 40, ...
# Timeline: 2025-12-15 to 2026-04-05
```

### 1b. Verify data seeded locally

```bash
# Check incident count
curl "http://localhost:5173/api/v1/incidents/analytics/summary?period=quarter" \
  -H "Authorization: Bearer $LOCAL_TOKEN" | jq '.total'
# Should show ≥ 200

# Check percentages are correct (QUERY_BY_CATEGORY fix)
curl "http://localhost:5173/api/v1/incidents/analytics/by-category?period=quarter" \
  -H "Authorization: Bearer $LOCAL_TOKEN" | jq '.[] | select(.category=="code_pattern") | .percentage'
# Should be ~20% (40 out of 200)
```

### 1c. Deploy to production (run same seed script)

```bash
# Authenticate to production
gcloud auth application-default login

# Set production DATABASE_URL via Secret Manager
export DATABASE_URL=$(gcloud secrets versions access latest --secret=THELOOP_API_DATABASE_URL)

# Run seed script with 200 test incidents on PRODUCTION
python3 scripts/seed_analytics_testdata.py --count 200

# Verify (using production Cloud Run API URL)
curl "https://api.loop.oute.pro/api/v1/incidents/analytics/summary?period=quarter" \
  -H "Authorization: Bearer $PROD_TOKEN" | jq '.total'
# Should show ≥ 200
```

---

## Phase 2: Dashboard Validation Checklist (PRODUCTION)

### 2a. Page Load & Rendering
- [ ] https://loop.oute.pro/analytics/ loads without 404/500
- [ ] Page load time < 2s (check DevTools Network tab)
- [ ] No console errors
- [ ] All 8 KPI cards render:
  - [ ] Total
  - [ ] Resolved
  - [ ] Unresolved
  - [ ] MTTR (Avg Resolution Days)
  - [ ] Errors (from severity trend)
  - [ ] Warnings (from severity trend)
  - [ ] Top Category (e.g., "code_pattern")
  - [ ] Top Team (e.g., "Backend")

### 2b. Data Correctness (QUERY_BY_CATEGORY Fix)
- [ ] By Root Cause heatmap shows correct percentages
  - [ ] Total should be 200
  - [ ] Each category ~20% (40/200)
  - [ ] Percentages sum to ~100%
- [ ] By Team heatmap shows:
  - [ ] Backend: 40, Frontend: 40, DevOps: 40, Platform: 40, QA: 40
  - [ ] Top categories for each team show (e.g., Backend shows code_pattern, infrastructure, etc.)
- [ ] Timeline chart (Pattern Timeline):
  - [ ] Shows weekly data over 52 weeks
  - [ ] 5 colored lines (1 per category)
  - [ ] Data distributed across timeline

### 2c. New Components
- [ ] **Severity Trend chart** (stacked area) renders:
  - [ ] Two-color stacked area (error + warning)
  - [ ] X-axis labels show months (no duplicate labels)
  - [ ] Tooltip shows week, error count, warning count
- [ ] **Rule Effectiveness card** (top-5 rules) renders:
  - [ ] Top 5 rules listed in table
  - [ ] Incident count shows for each rule
  - [ ] Severity badge (ERROR or WARNING) shows for each

### 2d. Multi-Select Team Filter
- [ ] Click "Team" dropdown
  - [ ] Shows list: Backend, Frontend, DevOps, Platform, QA
  - [ ] Can select multiple teams
  - [ ] "Clear all" button visible
  - [ ] Click background closes dropdown
- [ ] Select `Backend + Platform` → Apply
  - [ ] Page re-renders
  - [ ] Total incidents ≈ 80 (40+40)
  - [ ] By Team table shows only Backend + Platform
- [ ] Select `Frontend → Apply`
  - [ ] Total incidents ≈ 40
  - [ ] All heatmaps/charts update

### 2e. Drill-Down Navigation
- [ ] Click "code_pattern" bar in heatmap
  - [ ] Page re-renders (URL has `category=code_pattern`)
  - [ ] Filter UI updates to show "code_pattern" selected (**state desync fix**)
  - [ ] Total incidents ≈ 40 (all code_pattern)
  - [ ] Heatmap now shows only code_pattern (100% of universe)
- [ ] Click "Backend" in By Team table
  - [ ] Filter UI updates to show "Backend" selected in team dropdown (**state desync fix**)
  - [ ] Total incidents ≈ 40 (all Backend)

### 2f. Filter State Sync (After Drill-Down)
- [ ] Apply multi-select: Backend + Platform
- [ ] Click "infrastructure" category bar
- [ ] **Critical:** Filter UI must show:
  - [ ] `Team`: Backend + Platform (not reset to "All Teams")
  - [ ] `Category`: infrastructure (selected)
  - [ ] Both filters remain active
- [ ] Total = ~16 incidents (40% of 40 Backend)

### 2g. Cache Performance
- [ ] Open DevTools → Network tab
- [ ] Apply filter: `period=quarter, team=Backend`
  - [ ] First request to `/analytics/by-category`: ~200-500ms
  - [ ] Cache header check (if using ETags/Cache-Control): confirm cache miss
- [ ] Reapply same filter (or refresh page with same URL)
  - [ ] Request time < 50ms (cache hit)
  - [ ] No database query logged
- [ ] Change filter order: select `Platform → Backend` (different order)
  - [ ] Still gets cache hit (both show same data)

### 2h. Mobile Responsiveness (DevTools 375px viewport)
- [ ] Filter bar wraps correctly
- [ ] Heatmaps render (no horizontal overflow)
- [ ] Tooltips render in-bounds (not overflow off-screen)
- [ ] Severity Trend chart X-axis labels visible
- [ ] Rule Effectiveness card scrollable horizontally if needed
- [ ] All KPI cards stack vertically (4 rows of 2)

### 2i. Edge Cases
- [ ] Select category `unknown` (empty results)
  - [ ] Shows "No incidents in this period" message
  - [ ] Heatmaps empty
- [ ] Custom date range: `2026-01-01` to `2026-01-31`
  - [ ] Returns fewer incidents (only January data)
  - [ ] Percentages still correct
- [ ] Filter to empty result set
  - [ ] All numbers show 0
  - [ ] No charts render
  - [ ] Empty state message visible

---

## Phase 3: Cleanup & Deletion

### 3a. Delete test data from production

```bash
# Authenticate
gcloud auth application-default login
export DATABASE_URL=$(gcloud secrets versions access latest --secret=THELOOP_API_DATABASE_URL)

# Connect to production database
psql "$DATABASE_URL"

# Delete postmortems first (foreign key)
DELETE FROM postmortems WHERE incident_id IN (
  SELECT id FROM incidents WHERE title LIKE 'Test Incident%'
);

-- Delete incidents
DELETE FROM incidents WHERE title LIKE 'Test Incident%';

-- Verify deleted
SELECT COUNT(*) FROM incidents WHERE title LIKE 'Test Incident%';
-- Should return 0
```

### 3b. Verify dashboard still works (post-deletion)

```bash
# Check analytics still loads
curl "https://api.loop.oute.pro/api/v1/incidents/analytics/summary?period=quarter" \
  -H "Authorization: Bearer $PROD_TOKEN" | jq '.total'
# Should show remaining real data count

# Visit https://loop.oute.pro/analytics/ in browser
# Should load successfully with real data (if exists)
```

---

## Phase 4: Remaining Tests (After Phase 3 Cleanup)

### 4a. Real Data Validation
- [ ] If production has real incidents, repeat Phase 2 with real data
- [ ] Verify percentages match real distribution
- [ ] Check cache still works with real data

### 4b. Performance Under Load (Optional)
```bash
# Install Apache Bench
brew install httpd

# Load test analytics endpoint (50 concurrent requests)
ab -n 100 -c 50 -H "Authorization: Bearer $TOKEN" \
  "https://api.loop.oute.pro/api/v1/incidents/analytics/summary?period=month"

# Expected: <500ms median response time, <50ms for cached requests
```

### 4c. Error Handling
- [ ] Invalid `team` param: should be ignored (empty filter)
- [ ] Invalid `category`: should return 400 error
- [ ] Missing auth token: should return 401
- [ ] Custom date with `start > end`: should return 400

### 4d. Browser Compatibility
- [ ] Chrome/Safari/Firefox: dashboard renders identically
- [ ] Dark mode (if supported): colors readable

---

## Validation Checkpoints

| Phase | Checkpoint | Status |
|-------|-----------|--------|
| 1a | Seed data locally | ⏳ Ready to run |
| 1b | Verify local data | ⏳ Ready to run |
| 1c | Seed production + verify | ⏳ Ready to run |
| 2a-2i | Dashboard validation | ⏳ Pending test data |
| 3a-3b | Cleanup & verify | ⏳ After Phase 2 |
| 4a-4d | Additional tests | ⏳ Optional |

---

## Commands Reference

### Seed test data (LOCAL)
```bash
cd /Users/bardi/Projetos/the-loop
export DATABASE_URL="postgresql+asyncpg://theloop:theloop@localhost:5433/theloop"
python3 scripts/seed_analytics_testdata.py --count 200
```

### Seed test data (PRODUCTION)
```bash
cd /Users/bardi/Projetos/the-loop
export DATABASE_URL=$(gcloud secrets versions access latest --secret=THELOOP_API_DATABASE_URL)
python3 scripts/seed_analytics_testdata.py --count 200
```

### Delete test data (PRODUCTION)
```bash
gcloud sql connect theloop-db --user=theloop --database=theloop
# Then run DELETE statements from Phase 3a
```

### Quick API test
```bash
curl "https://api.loop.oute.pro/api/v1/incidents/analytics/summary?period=month&team=Backend" \
  -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" | jq '.'
```

---

## Summary

**Total time estimate:**
- Phase 1 (seed): 10 min
- Phase 2 (validation): 30 min  
- Phase 3 (cleanup): 5 min
- **Total: ~45 minutes**

**Success criteria:** All Phase 2 checklist items ✅

**Closure:** After all items pass, close Spec-019 and update CLAUDE.md phase status to ✅ COMPLETE.
