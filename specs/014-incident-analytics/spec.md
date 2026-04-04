# Spec-014: Incident Analytics Dashboard

**Criado**: 2026-04-04  
**Branch**: `feat/spec-014-analytics`  
**Fase**: Phase C.2 — Incident Analytics & Observability  
**Status**: Planning

---

## Objetivo

Fornecer visibilidade sobre padrões de incidentes através de um dashboard interativo que mostra:
- Distribuição de incidentes por categoria, severidade e time
- Timeline de quando padrões começam a aparecer
- Efetividade das regras Semgrep (quantas detecções, quantas bloqueadas)
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
- Page `/incidents/analytics` com 4 seções principais
- Período selecionável: Última semana, Mês, Trimestre, Custom (date picker)
- Auto-refresh a cada 5 min (WebSocket opcional — Spec-C.X)

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
- Linha por categoria (6 cores diferentes)
- Hover mostra data e contagem

### RF-005: Rule Effectiveness
Card mostrando para cada regra Semgrep:
- Nome da regra
- Quantas PRs bloqueou (semana/mês)
- Quantas detecções gerou
- Taxa de "accepted merge" (foi feito override?)
- Status: ativo, deprecado, novo

### RF-006: Filtros Globais
- Período: Week, Month, Quarter, Custom
- Team: Dropdown multi-select (todas as teams na BD)
- Categoria: Dropdown multi-select
- Status incidente: Resolved, Unresolved, All
- Apply/Reset buttons

---

## Critérios de Sucesso

### Funcionalidade
- [x] Dashboard carrega em <2s (mesmo com 1000 incidentes)
- [x] Filtros funcionam sem hard refresh (SPA behavior)
- [x] Todas 5 seções renderizam dados corretos
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
- [x] Carregamento incremental: Cards aparecem conforme prontos (não wait all)

---

## User Stories

### US-001: PM quer ver onde está maior concentração de incidentes
**Como** Product Manager  
**Quero** ver um dashboard mostrando quais categorias/times têm mais incidentes  
**Para** priorizar onde focar esforços de melhoria

**Aceitação**:
- Vejo 5 categorias principais ordenadas por frequência
- Vejo top 5 times com mais incidentes
- Posso filtrar por período

### US-002: Tech Lead quer entender padrões do seu time
**Como** Tech Lead da equipe Backend  
**Quero** filtrar analytics apenas para meu time  
**Para** identificar padrões específicos que afetam a gente

**Aceitação**:
- Filtro "Team" mostra todas 10+ teams
- Ao selecionar, dashboard atualiza em tempo real
- Vejo categorias mais comuns no meu time

### US-003: Security quer medir efetividade das regras
**Como** Security Engineer  
**Quero** ver quantas regras Semgrep bloquearam PRs  
**Para** decidir se regras estão bem calibradas

**Aceitação**:
- Vejo tabela: Regra | Bloqueios (semana) | Taxa aceitos
- Regras novas ficam destacadas
- Regras deprecadas ficam cinzas

### US-004: DevOps quer acompanhar tendências
**Como** DevOps Lead  
**Quero** ver timeline de incidentes nos últimos 12 meses  
**Para** prever quando precisarei mais recursos

**Aceitação**:
- Gráfico de série temporal com 12 meses
- Posso ver por categoria (6 linhas coloridas)
- Tooltip mostra data e contagem

---

## Arquitetura (Alto Nível)

### Frontend (SvelteKit)
```
src/routes/incidents/analytics/
  +page.svelte          # Master component
  +page.ts             # Data loading (load function)
  
src/lib/components/analytics/
  DashboardGrid.svelte       # Layout (2x2 + 1 wide)
  CategoryHeatmap.svelte     # RF-002
  TeamHeatmap.svelte         # RF-003
  PatternTimeline.svelte     # RF-004
  RuleEffectiveness.svelte   # RF-005
  AnalyticsFilters.svelte    # RF-006
```

### Backend (FastAPI)
```
src/api/routes/analytics.py
  GET /api/v1/incidents/analytics/summary
    → {total, by_category, by_team}
    
  GET /api/v1/incidents/analytics/by-category
    → [{category, count, avg_severity, percentage}]
    
  GET /api/v1/incidents/analytics/by-team
    → [{team, count, top_categories, avg_resolution_days}]
    
  GET /api/v1/incidents/analytics/timeline
    → [{week, count, by_category: {code_pattern: 5, ...}}]
    
  GET /api/v1/rules/effectiveness
    → [{rule_id, blocks_week, blocks_month, override_rate}]

src/domain/services.py
  AnalyticsService:
    - compute_category_stats(period, filters)
    - compute_team_stats(period, filters)
    - compute_timeline(period, filters)
    
src/adapters/postgres/analytics_queries.py
  Raw SQL queries (GROUP BY, aggregate functions)
  Indexes on created_at, root_cause_category, team_responsible
```

### Data Layer
- Raw SQL aggregates (no ORM overhead for analytics)
- Indexes: `(created_at, root_cause_category)`, `(team_responsible, created_at)`
- Query results cached (5-min TTL) via Redis (deferred to Spec-C.X)

---

## Restrições

- **Performance**: Queries devem executar em <500ms mesmo com 10k incidentes
- **Sem breaking changes**: Spec-013 data schema intacto
- **Mobile-first**: Dashboard funciona em telas 375px+ (iPhone SE)
- **No OAuth**: Usa autenticação existente (Firebase)

---

## Out of Scope

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
- Incluir na contagem mas marcar como "análise pendente"
- Não quebrar agregações

**E-003**: Regra deprecada no meio do período selecionado
- Mostrar em cinza na tabela
- Separar bloqueios "pré-deprecação" dos "pós-deprecação"

**E-004**: Múltiplos filtros selecionados (team=backend AND category=injection AND period=month)
- Queries devem usar AND lógico
- Resultado pode ser vazio (E-001)

---

## Próximos Passos

1. ✅ Aprovação de spec (você)
2. → Criar plan.md (arquitetura detalhada, schema, queries SQL)
3. → Criar tasks.md (75-100 tasks, 2-3 semanas)
4. → Especkit.analyze (validar consistências)
5. → Implementação (2-3 sprints de 5 dias cada)

