"""Raw SQL queries for analytics aggregations (Phase C.2 + Spec-019).

All queries use parameterized bindings to prevent SQL injection (T020).
Parameters are always passed via the `params` dict, never interpolated.

Multi-select team filter: team_array is a TEXT[] passed via ARRAY(String()) binding.
  - Empty array → no filter (cardinality(:team_array) = 0)
  - Non-empty   → p.team_responsible = ANY(:team_array)
"""

from __future__ import annotations

# ─── Q1: Incidents by root cause category ────────────────────────────────────
#
# Returns per-category stats for the given period + filters.
# avg_severity: error=1.0, warning=0.5 (from severity_for_rule field).
# avg_resolution_days: NULL when status=unresolved (no resolved_at values).
# percentage: computed against the filtered universe (same status condition).

QUERY_BY_CATEGORY = """
SELECT
    p.root_cause_category,
    COUNT(*) AS count,
    ROUND(
        100.0 * COUNT(*) / NULLIF((
            SELECT COUNT(*)
            FROM postmortems p2
            LEFT JOIN incidents i2 ON p2.incident_id = i2.id
            WHERE p2.created_at >= :start AND p2.created_at < :end
              AND (i2.deleted_at IS NULL)
              AND (
                  :status = 'all'
                  OR (:status = 'resolved' AND i2.resolved_at IS NOT NULL)
                  OR (:status = 'unresolved' AND i2.resolved_at IS NULL)
              )
        ), 0),
        2
    ) AS percentage,
    ROUND(
        AVG(CASE WHEN p.severity_for_rule = 'error' THEN 1.0 ELSE 0.5 END)::numeric,
        2
    ) AS avg_severity,
    ROUND(
        AVG(EXTRACT(DAY FROM i.resolved_at - p.created_at))::numeric,
        1
    ) AS avg_resolution_days
FROM postmortems p
LEFT JOIN incidents i ON p.incident_id = i.id
WHERE p.created_at >= :start AND p.created_at < :end
  AND (i.deleted_at IS NULL)
  AND (cardinality(:team_array) = 0 OR p.team_responsible = ANY(:team_array))
  AND (:category IS NULL OR p.root_cause_category = :category)
  AND (
      :status = 'all'
      OR (:status = 'resolved' AND i.resolved_at IS NOT NULL)
      OR (:status = 'unresolved' AND i.resolved_at IS NULL)
  )
GROUP BY p.root_cause_category
ORDER BY count DESC
"""

# ─── Q1-summary: Summary stats (total/resolved/unresolved/avg_resolution_days) ─

QUERY_SUMMARY = """
SELECT
    COUNT(*) AS total,
    COUNT(i.resolved_at) AS resolved,
    COUNT(*) - COUNT(i.resolved_at) AS unresolved,
    ROUND(
        AVG(EXTRACT(DAY FROM i.resolved_at - p.created_at))::numeric,
        1
    ) AS avg_resolution_days
FROM postmortems p
LEFT JOIN incidents i ON p.incident_id = i.id
WHERE p.created_at >= :start AND p.created_at < :end
  AND (i.deleted_at IS NULL)
  AND (cardinality(:team_array) = 0 OR p.team_responsible = ANY(:team_array))
  AND (:category IS NULL OR p.root_cause_category = :category)
  AND (
      :status = 'all'
      OR (:status = 'resolved' AND i.resolved_at IS NOT NULL)
      OR (:status = 'unresolved' AND i.resolved_at IS NULL)
  )
"""

# ─── Q1-team: Incidents by team ───────────────────────────────────────────────
#
# Returns per-team stats. top_categories computed in Python (top 3 by count).

QUERY_BY_TEAM = """
SELECT
    p.team_responsible AS team,
    COUNT(*) AS count,
    ROUND(
        AVG(EXTRACT(DAY FROM i.resolved_at - p.created_at))::numeric,
        1
    ) AS avg_resolution_days,
    -- Category counts as JSON for top-3 extraction in Python
    jsonb_object_agg(
        p.root_cause_category,
        cat_count.cnt
    ) AS category_counts
FROM postmortems p
LEFT JOIN incidents i ON p.incident_id = i.id
LEFT JOIN (
    SELECT
        pm.team_responsible,
        pm.root_cause_category,
        COUNT(*) AS cnt
    FROM postmortems pm
    LEFT JOIN incidents inc ON pm.incident_id = inc.id
    WHERE pm.created_at >= :start AND pm.created_at < :end
      AND (inc.deleted_at IS NULL)
      AND (cardinality(:team_array) = 0 OR pm.team_responsible = ANY(:team_array))
      AND (:category IS NULL OR pm.root_cause_category = :category)
      AND (
          :status = 'all'
          OR (:status = 'resolved' AND inc.resolved_at IS NOT NULL)
          OR (:status = 'unresolved' AND inc.resolved_at IS NULL)
      )
    GROUP BY pm.team_responsible, pm.root_cause_category
) cat_count ON p.team_responsible = cat_count.team_responsible
          AND p.root_cause_category = cat_count.root_cause_category
WHERE p.created_at >= :start AND p.created_at < :end
  AND (i.deleted_at IS NULL)
  AND (cardinality(:team_array) = 0 OR p.team_responsible = ANY(:team_array))
  AND (:category IS NULL OR p.root_cause_category = :category)
  AND (
      :status = 'all'
      OR (:status = 'resolved' AND i.resolved_at IS NOT NULL)
      OR (:status = 'unresolved' AND i.resolved_at IS NULL)
  )
GROUP BY p.team_responsible
ORDER BY count DESC
"""

# ─── Q2: Timeline — weekly buckets ────────────────────────────────────────────
#
# Returns one row per week with total count + per-category breakdown.
# by_category is merged in Python to always include all 5 RootCauseCategory keys.

QUERY_TIMELINE = """
SELECT
    DATE_TRUNC('week', p.created_at) AS week,
    COUNT(*) AS count,
    jsonb_object_agg(
        p.root_cause_category,
        COALESCE(breakdown.cnt, 0)
    ) AS by_category
FROM postmortems p
LEFT JOIN incidents i ON p.incident_id = i.id
LEFT JOIN (
    SELECT
        DATE_TRUNC('week', pm.created_at) AS week,
        pm.root_cause_category,
        COUNT(*) AS cnt
    FROM postmortems pm
    LEFT JOIN incidents inc ON pm.incident_id = inc.id
    WHERE pm.created_at >= :start AND pm.created_at < :end
      AND (inc.deleted_at IS NULL)
      AND (cardinality(:team_array) = 0 OR pm.team_responsible = ANY(:team_array))
      AND (:category IS NULL OR pm.root_cause_category = :category)
      AND (
          :status = 'all'
          OR (:status = 'resolved' AND inc.resolved_at IS NOT NULL)
          OR (:status = 'unresolved' AND inc.resolved_at IS NULL)
      )
    GROUP BY DATE_TRUNC('week', pm.created_at), pm.root_cause_category
) breakdown
    ON DATE_TRUNC('week', p.created_at) = breakdown.week
   AND p.root_cause_category = breakdown.root_cause_category
WHERE p.created_at >= :start AND p.created_at < :end
  AND (i.deleted_at IS NULL)
  AND (cardinality(:team_array) = 0 OR p.team_responsible = ANY(:team_array))
  AND (:category IS NULL OR p.root_cause_category = :category)
  AND (
      :status = 'all'
      OR (:status = 'resolved' AND i.resolved_at IS NOT NULL)
      OR (:status = 'unresolved' AND i.resolved_at IS NULL)
  )
GROUP BY DATE_TRUNC('week', p.created_at)
ORDER BY week ASC
"""

# ─── Q3: Severity trend — weekly ERROR vs WARNING counts ──────────────────────
#
# Counts postmortems by week split on severity_for_rule (error / warning).
# Respects team, category, and status filters.

QUERY_SEVERITY_TREND = """
SELECT
    DATE_TRUNC('week', p.created_at) AS week,
    COUNT(*) FILTER (WHERE p.severity_for_rule = 'error') AS error_count,
    COUNT(*) FILTER (WHERE p.severity_for_rule = 'warning') AS warning_count
FROM postmortems p
LEFT JOIN incidents i ON p.incident_id = i.id
WHERE p.created_at >= :start AND p.created_at < :end
  AND (i.deleted_at IS NULL)
  AND (cardinality(:team_array) = 0 OR p.team_responsible = ANY(:team_array))
  AND (:category IS NULL OR p.root_cause_category = :category)
  AND (
      :status = 'all'
      OR (:status = 'resolved' AND i.resolved_at IS NOT NULL)
      OR (:status = 'unresolved' AND i.resolved_at IS NULL)
  )
GROUP BY DATE_TRUNC('week', p.created_at)
ORDER BY week ASC
"""

# ─── Q4: Top rules — most triggered rules by incident count ───────────────────
#
# Aggregates postmortems by related_rule_id (non-null only).
# avg_severity: error=1.0, warning=0.5.
# :top_n limits the result set (default 5).

QUERY_TOP_RULES = """
SELECT
    p.related_rule_id AS rule_id,
    COUNT(*) AS incident_count,
    ROUND(
        AVG(CASE WHEN p.severity_for_rule = 'error' THEN 1.0 ELSE 0.5 END)::numeric,
        2
    ) AS avg_severity
FROM postmortems p
LEFT JOIN incidents i ON p.incident_id = i.id
WHERE p.created_at >= :start AND p.created_at < :end
  AND (i.deleted_at IS NULL)
  AND p.related_rule_id IS NOT NULL
  AND (cardinality(:team_array) = 0 OR p.team_responsible = ANY(:team_array))
  AND (:category IS NULL OR p.root_cause_category = :category)
  AND (
      :status = 'all'
      OR (:status = 'resolved' AND i.resolved_at IS NOT NULL)
      OR (:status = 'unresolved' AND i.resolved_at IS NULL)
  )
GROUP BY p.related_rule_id
ORDER BY incident_count DESC
LIMIT :top_n
"""
