# The Loop — Product Roadmap

**Last Updated**: 2026-04-03  
**Status**: Phase B complete, Phase C.1 in progress (Postmortem Workflow)

---

## Phase Status

### ✅ Phase 0: Foundation (Complete)
- Landing page (SvelteKit)
- Waitlist (Firebase Firestore)
- Constitution (13 mandamentos)

### ✅ Phase 1: Incident CRUD (Complete)
- Incident creation/update/delete
- 7-tab detail view with lazy-loading
- Sub-resources: timeline, responders, action items, attachments
- Firebase Auth (email/password + signup)
- Full hexagonal architecture (domain/ports/adapters)

### ✅ Phase 2-B: Semgrep Integration (Complete)

#### Phase A: Static Rules (Shipped 2026-02-01)
- 6 base rules (injection, unsafe-api-usage, missing-safety-check, missing-error-handling, unsafe-regex)
- GitHub Actions workflow
- Fallback to `.bak` file

#### Phase B: Versioned API (Shipped 2026-04-03)
- Semantic versioning (X.Y.Z)
- 6 endpoints (4 public, 2 admin)
- Cache layer (5-min TTL on /latest)
- Fallback to Phase A rules
- Instant deprecation + rollback
- 51 tests, 80%+ coverage
- Full documentation (API, versioning, migration, troubleshooting)

### 📅 Phase C: Incident Knowledge Capture (In Progress)

**Timeline**: Q2 2026 (6-8 weeks)

#### C.1: Postmortem Workflow (🔄 In Progress — Spec-013)
- Long-form incident analysis (why it happened, impact analysis)
- Root cause templates + patterns (15 hardcoded MVP)
- Read-only locking after incident resolution
- Links to Semgrep rules triggered by incident pattern

#### C.2: Incident Analytics Dashboard (Next — Spec-014)
- Top incident categories (by frequency, severity)
- Team vulnerability heatmap (which teams hit which patterns most?)
- Rule effectiveness (how many times caught pattern in PRs?)
- Incident timeline (when did patterns start appearing?)

#### C.3: Webhook Integrations (Spec-015)
- Slack: Post incident detection + analysis to team channels
- GitHub: Auto-comment on PRs with related past incidents
- PagerDuty: Create incidents when critical patterns found
- Custom webhooks for third-party integrations

#### C.4: Phase B Rules Expansion (Spec-012 — Shipped)
- 14 additional rules (injection, crypto, security, performance, infrastructure, config, dependencies)
- Semantic versioning (X.Y.Z)
- Cache layer (5-min TTL on /latest)
- Version comparison API (`GET /compare?v1=x&v2=y`)
- Deprecation notifications (email/Slack)

---

### 🔮 Phase C.X: Future Optimization (Deferred)

**Decision**: Defer Redis + advanced features until high-volume data warrants complexity.

#### C.X.1: Redis Caching (When >10 replicas needed)
- Shared cache across API replicas (survives restarts)
- Multi-region failover
- Cache invalidation <100ms across fleet

#### C.X.2: Admin Dashboard
- Rule management UI (create/edit/publish/deprecate)
- Version history timeline
- Deprecation analytics

#### C.X.3: Advanced Features
- Rate limit headers (X-RateLimit-*)
- Version migration tool (CLI to detect breaking changes)
- Custom rule builder (no-code UI)
- Rule performance profiling
---

### 📋 Phase D: Observability & Compliance (Later)

**Timeline**: Q3 2026+

- **Metrics**: Dashboard for rule adoption, scan latency, false positive rate
- **Logging**: Audit trail for all publish/deprecate operations
- **Compliance**: GDPR/SOC2 compliance reporting
- **Analytics**: Organization stats (rules scanned, vulnerabilities found, etc.)

---

### 🚀 Phase E: Advanced Features (Future)

**Timeline**: Q4 2026+

- **ML-Based Rules**: Auto-generate rules from incident clusters
- **Custom Rule Builder**: No-code UI for organizations to create custom rules
- **Integrations**: Jira, Slack, GitHub, GitLab, Bitbucket webhooks
- **Remediation Engine**: Auto-fix suggestions + testing in PR comments
- **Incident Forecasting**: ML model to predict high-risk code patterns

---

## Current Priorities (Phase C)

### High Priority (In Progress)
1. **Postmortem Workflow (C.1 — Spec-013)** — Incident analysis, templates, read-only locking ✅ SHIPPED
2. **Analytics Dashboard (C.2 — Spec-014)** — Category heatmap, team vulnerability analysis
3. **Webhook Integrations (C.3 — Spec-015)** — Slack, GitHub, PagerDuty notifications
4. **Dynamic Templates (C.1 — Spec-015)** — Admin UI to create/edit root cause templates

### Medium Priority
1. **Admin Dashboard (C.X.2)** — Manual version management UI
2. **Version Migration Tool (C.X.3)** — CLI to detect breaking changes (helpful for ops teams)
3. **Metrics Dashboard (Phase D)** — Rule adoption, scan latency, false positive rate

### Deferred (Until >10 API Replicas)
1. **Redis Caching (C.X.1)** — Scaling readiness, shared state across replicas
2. **Rate Limit Headers (C.X.3)** — Standard HTTP rate limit feedback
3. **Analytics (Phase D)** — Organization stats

---

## Beyond Phase C (Backlog)

### Tech Debt
- [ ] Move `is_admin` check from Firebase claims to Firestore custom claims
- [ ] Add API versioning (`/api/v2/...`) for backward compatibility
- [ ] Optimize Semgrep scan speed (currently 30-50s per repo)

### Infrastructure
- [ ] Multi-region deployment (Edge locations for global latency)
- [ ] Disaster recovery (automated backup/restore)
- [ ] Load testing (5x, 10x current traffic)

### Compliance
- [ ] SOC2 certification
- [ ] GDPR data retention policy
- [ ] Security audit (annual)

---

## Success Metrics

### Phase B (Now)
- ✅ API latency <300ms on cache miss
- ✅ >80% cache hit rate
- ✅ 0 production incidents
- ✅ Zero false positives in Phase A rules (6/6 high-precision)

### Phase C (Goal)
- Cache hit rate >90% (Redis shared state)
- 14 new rules with >95% precision
- Deprecation workflow <5 minutes (publish → notification → all PRs updated)
- Admin dashboard adoption: 100% of organizations using version management

### Phase D (Goal)
- Compliance certifications (SOC2, GDPR ready)
- Audit trail: 100% of operations logged
- Metrics: Dashboard with >50 queries per week (adoption signal)

---

## Known Risks & Mitigations

### Risk: API becomes bottleneck
**Mitigation**: Phase C Redis cache reduces DB hits by 90%

### Risk: Rules produce false positives
**Mitigation**: Community feedback loop, rule refinement, automated precision testing

### Risk: Adoption plateaus
**Mitigation**: Admin dashboard lowers barrier to entry, integrations (Slack/Jira) increase visibility

### Risk: Compliance requirements increase
**Mitigation**: Build compliance infrastructure in Phase D proactively

---

## Success Stories (Tracking)

**2026-04-03**: Phase B shipped, 80%+ test coverage, zero production incidents during deploy
**2026-Q2**: Phase C rules + Redis caching (expected)
**2026-Q3**: Admin dashboard + compliance foundation (expected)

---

## Decision Log

- **2026-03-01**: Approved Phase B API versioning (decision: semantic versioning strict X.Y.Z)
- **2026-02-01**: Approved Phase A static rules (decision: 6 multilingual rules for MVP)
- **2026-01-15**: Approved Phase 1 incident CRUD (decision: hexagonal architecture)

---

**Owne r**: @renatobardi  
**Last Reviewed**: 2026-04-03  
**Next Review**: 2026-05-01
