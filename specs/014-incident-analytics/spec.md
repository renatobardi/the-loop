# Spec-014: Incident Analytics Dashboard

**Criado**: 2026-04-04  
**Branch**: `feat/spec-014-analytics`  
**Fase**: Phase C.2 — Incident Analytics & Observability  
**Status**: Ready for Implementation

---

## Objetivo

Fornecer visibilidade sobre padrões de incidentes através de um dashboard interativo que mostra:
- Distribuição de incidentes por categoria, severidade e time
- Timeline de quando padrões começam a aparecer
- Efetividade das regras Semgrep _(deferred — RF-005/Spec-015)_
- Hotspots de vulnerabilidade por time

Objetivo principal: **Identificar padrões sistêmicos e equipes com maior vulnerabilidade**.

---

## Contexto

**Pré-requisitos disponíveis**:
- Spec-013 ✅ (Postmortem Workflow com 15 templates, dados de raiz causa)
- Spec-012 ✅ (14 regras Phase B, versionamento de regras)
- Spec-010 ✅ (6 regras Phase A, GitHub Actions integration)

**Base de dados**:
- `incidents` table: categoria, severidade, resolved_at
- `postmortems` table: root_cause_category, team_responsible, severity_for_rule
- `rule_versions` table: versão, data publicação, data deprecação
- `timeline_events` table: tipo evento, data

**Dados disponíveis para análise**:
- 20+ incidentes em produção (Spec-007)
- 62 testes de integração com dados fixtures
- Schema bem definido com relacionamentos 1:N

---

## Requisitos Funcionais

### RF-001: Dashboard Principal
- Page `/incidents/analytics/` com 5 seções principais (RF-002, RF-003, RF-004, RF-006, RF-007)
- Período selecionável: Última semana, Mês, Trimestre, Custom (date picker)
- Auto-refresh: ❌ out of scope — deferred to Spec-C.X (WebSocket/real-time). MVP requires manual reload or filter re-apply.

### RF-002: Heatmap por Categoria
Card mostrando distribuição de incidentes por root_cause_category:
- Barra horizontal ou tabela com:
  - Categoria (code_pattern, infrastructure, process_breakdown, third_party, unknown)
  - Contagem absoluta
  - Percentual do total
  - Severidade média

### RF-003: Heatmap por Time
Card mostrando distribuição por team_responsible:
- Grid ou tabela com:
  - Nome do time
  - Número de incidentes atribuídos
  - Categorias mais comuns naquele time (top 3)
  - Média de tempo para resolução

### RF-004: Timeline de Padrões
Gráfico de série temporal mostrando:
- Eixo X: Semanas/Meses (últimos 12 meses)
- Eixo Y: Contagem de incidentes
- Linha por categoria (5 cores — uma por valor de RootCauseCategory)
- Hover mostra data e contagem

### RF-005: Rule Effectiveness _(deferred — Spec-015)_

> **Out of scope for MVP.** This card requires `rule_block` events in the `timeline_events` table, which no existing spec defines. Deferred to Spec-015 (Webhook Integrations), which will introduce CI-level event tracking via the `theloop-guard.yml` workflow.

### RF-006: Filtros Globais
- Período: Week, Month, Quarter, Custom
- Team: Dropdown single-select (todas as teams na BD) — multi-select deferred to Spec-C.X
- Categoria: Dropdown single-select — multi-select deferred to Spec-C.X
- Status incidente: Resolved, Unresolved, All
- Apply/Reset buttons

### RF-007: Summary Card
Card de resumo no topo do dashboard mostrando:
- Total de incidentes no período
- Incidentes resolvidos
- Incidentes não resolvidos
- Média de dias para resolução

---

## Critérios de Sucesso

### Funcionalidade
- [x] Dashboard carrega em <2s (mesmo com 1000 incidentes)
- [x] Filtros funcionam sem hard refresh (SPA behavior)
- [x] Todas 5 seções renderizam dados corretos (RF-002, RF-003, RF-004, RF-006, RF-007)
- [x] Períodos customizados funcionam (date picker)

### Qualidade de Código
- [x] mypy strict (0 Any values)
- [x] ruff lint (0 issues)
- [x] 80%+ test coverage (unit + integration)
- [x] TypeScript strict no frontend

### Observabilidade
- [x] Logs estruturados (category, team, period em cada query)
- [x] Métrica: "analytics_dashboard_load_time_ms" exportada
- [x] Métrica: "analytics_query_result_count" para cada tipo

### UX
- [x] Responsive design (mobile-first, funciona em tablet)
- [x] Accessibility: WCAG 2.1 AA (alt text, color contrast)
- [x] Carregamento: Cards mostram skeleton enquanto Promise.all resolve; todos os cards carregam juntos (incremental por card via loading skeleton — não SSR streaming)

---

## User Stories

### US-001: PM quer ver onde está maior concentração de incidentes
**Como** Product Manager  
**Quero** ver um dashboard mostrando quais categorias/times têm mais incidentes  
**Para** priorizar onde focar esforços de melhoria

**Aceitação**:
- Vejo 5 categorias principais ordenadas por frequência
- Vejo times com mais incidentes ordenados por frequência
- Posso filtrar por período

### US-002: Tech Lead quer entender padrões do seu time
**Como** Tech Lead da equipe Backend  
**Quero** filtrar analytics apenas para meu time  
**Para** identificar padrões específicos que afetam a gente

**Aceitação**:
- Filtro "Team" mostra todas 10+ teams
- Ao selecionar e clicar Apply, dashboard atualiza (re-fetch via URL param change)
- Vejo categorias mais comuns no meu time

### US-003: Security quer medir efetividade das regras _(deferred — Spec-015)_

> Deferred with RF-005. Requires `rule_block` event tracking infrastructure.

### US-004: DevOps quer acompanhar tendências
**Como** DevOps Lead  
**Quero** ver timeline de incidentes nos últimos 12 meses  
**Para** prever quando precisarei mais recursos

**Aceitação**:
- Gráfico de série temporal com 12 meses
- Posso ver por categoria (5 linhas coloridas — uma por categoria)
- Tooltip mostra data e contagem

---

## Arquitetura (Alto Nível)

> Detalhe completo em `plan.md`. Resumo aqui para referência rápida.

**Frontend**: `src/routes/incidents/analytics/+page.svelte` + `+page.ts` (universal load)  
**Components**: `src/lib/components/analytics/` — DashboardGrid, CategoryHeatmap, TeamHeatmap, PatternTimeline, AnalyticsFilters, SummaryCard  
**Backend**: `src/api/routes/analytics.py` — 4 endpoints (summary, by-category, by-team, timeline)  
**Service**: `src/domain/services.py` — AnalyticsService  
**Repository**: `src/adapters/postgres/analytics_repository.py` — raw SQL via `analytics_queries.py`

---

## Restrições

- **Performance**: Queries devem executar em <500ms mesmo com 10k incidentes
- **Sem breaking changes**: Spec-013 data schema intacto
- **Mobile-first**: Dashboard funciona em telas 375px+ (iPhone SE)
- **No OAuth**: Usa autenticação existente (Firebase)

---

## Out of Scope

- ❌ Rule Effectiveness card (RF-005) — requires `rule_block` events, deferred to Spec-015
- ❌ Webhooks / notificações (Spec-015)
- ❌ Admin UI para criar/editar analytics rules (Spec-C.X)
- ❌ Export (CSV, PDF) — Spec-D
- ❌ Predictions / ML (Spec-E)
- ❌ Real-time updates (WebSocket) — Spec-C.X

---

## Edge Cases

**E-001**: Período selecionado tem 0 incidentes
- Mostrar estado vazio com mensagem: "Nenhum incidente neste período"
- Sugerir expandir período

**E-002**: Team tem incidentes mas sem postmortem (draft)
- Incluir na contagem normalmente
- Badge "análise pendente" deferred — requer `postmortem.status` nas queries, fora do escopo MVP
- Não quebrar agregações

**E-003**: Regra deprecada no meio do período selecionado _(deferred — Spec-015 with RF-005)_

> Requires RF-005 rule effectiveness card. Deferred.

**E-004**: Múltiplos filtros selecionados (team=backend AND category=injection AND period=month)
- Queries devem usar AND lógico
- Resultado pode ser vazio (E-001)

---

## Próximos Passos

1. ✅ Aprovação de spec (você)
2. ✅ Criar plan.md (arquitetura detalhada, schema, queries SQL)
3. ✅ Criar tasks.md (139 tasks, 13 dias)
4. ✅ Especkit.analyze (validar consistências)
5. → Implementação (2-3 sprints de 5 dias cada)

