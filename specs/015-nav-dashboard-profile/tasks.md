# Tasks: Navigation, Dashboard & Perfil do Usuário (Spec-015)

## Phase Overview

**Total**: 83 tasks ativas | **Duração**: ~10 dias
**Coverage**: Backend (28) + Frontend (37) + Tests/A11y/Docs (18)

---

## Phase 1: Backend — DB & Models (T001–T011, 2 dias)

**Goal**: Migração, domain models, port. Zero breaking changes em tabelas existentes.

### Database
- [ ] T001 Criar `apps/api/alembic/versions/010_create_users.py` com tabela `users` e index `idx_users_firebase_uid`
- [ ] T002 Testar `alembic upgrade head` localmente com Cloud SQL Proxy
- [ ] T003 Testar `alembic downgrade -1` (rollback limpo — DROP TABLE users)

### Domain Models
- [ ] T004 Adicionar `UserPlan(StrEnum)` em `src/domain/models.py`
- [ ] T005 Adicionar `User(BaseModel, frozen=True)` em `src/domain/models.py` com todos os campos
- [ ] T006 Adicionar `UserNotFoundError` em `src/domain/exceptions.py`

### Port
- [ ] T007 Criar `src/ports/user_repo.py` com `UserRepoPort(Protocol)`: `get_or_create`, `update`

### ORM Row Model
- [ ] T008 Adicionar `UserRow` em `src/adapters/postgres/models.py` com todos os campos mapeados

### Unit Tests — Models
- [ ] T009 Testar `UserPlan` enum: valores corretos, não permite valor inválido
- [ ] T010 Testar `User` model: frozen, campos obrigatórios, defaults (`plan=beta`)
- [ ] T011 Testar `UserNotFoundError` instanciação

---

## Phase 2: Backend — Service & API (T012–T033, 2 dias)

**Goal**: Repository, service, endpoints GET/PATCH /users/me. Retrocompatível.

### Repository
- [ ] T012 Criar `src/adapters/postgres/user_repository.py`
- [ ] T013 Implementar `_row_to_domain()` helper
- [ ] T014 Implementar `get_or_create()` (SELECT + INSERT condicional com uuid5)
- [ ] T015 Implementar `update()` (UPDATE display_name, job_title, updated_at WHERE id)

### Adaptar Auth Dependency
- [ ] T016 Ajustar `src/adapters/firebase/auth.py` para retornar `firebase_uid` e `email` além do UUID
- [ ] T017 Criar `get_firebase_token_data` em `src/api/deps.py` retornando `{user_id, firebase_uid, email}`
- [ ] T018 Garantir que rotas existentes continuam usando `get_authenticated_user` sem alteração

### Service
- [ ] T019 Adicionar `UserService` em `src/domain/services.py`
- [ ] T020 Implementar `get_or_create(firebase_uid, email) -> User`
- [ ] T021 Implementar `update_profile(user_id, display_name, job_title) -> User`
- [ ] T022 Validar: `display_name` vazio string levanta `ValueError`

### API Models
- [ ] T023 Criar `src/api/models/users.py`: `UserResponse.from_domain()` e `UserUpdateRequest`

### API Routes
- [ ] T024 Criar `src/api/routes/users.py`
- [ ] T025 Implementar `GET /api/v1/users/me` com upsert + `@limiter.limit("60/minute")`
- [ ] T026 Implementar `PATCH /api/v1/users/me` com validação + `@limiter.limit("60/minute")`
- [ ] T027 Adicionar `get_user_service` em `src/api/deps.py`
- [ ] T028 Registrar router `/users` em `src/main.py`

### API Tests
- [ ] T029 `GET /api/v1/users/me` → 200 + campos corretos (upsert na primeira call)
- [ ] T030 `GET /api/v1/users/me` chamado 2x → mesmo `id` retornado (upsert idempotente)
- [ ] T031 `GET /api/v1/users/me` sem auth → 401
- [ ] T032 `PATCH /api/v1/users/me` com `display_name` válido → 200 + atualizado
- [ ] T033 `PATCH /api/v1/users/me` com `display_name=""` → 422
- [ ] T034 `PATCH /api/v1/users/me` sem auth → 401 [P]

---

## Phase 3: Frontend — Migração Analytics + Navbar & Avatar (T035–T057, 2 dias)

**Goal**: Mover rota `/analytics/`, refatorar Navbar, criar UserAvatar.

### Migração de Rota Analytics
- [ ] T035 Criar `src/routes/analytics/` e copiar `+page.svelte` e `+page.ts` de `incidents/analytics/`
- [ ] T036 Busca global e substituição: `/incidents/analytics/` → `/analytics/` em todo o projeto
  - `src/lib/ui/Navbar.svelte`, `ANALYTICS.md`, `README.md`, `CLAUDE.md`, specs, testes
- [ ] T037 Remover diretório `src/routes/incidents/analytics/`
- [ ] T038 Verificar que `/analytics/` carrega corretamente em dev (`npm run dev`)

### Navbar — Refatoração
- [ ] T039 Refatorar `src/lib/ui/Navbar.svelte`
- [ ] T040 Criar array `publicLinks`: Features, Pricing, Waitlist, Log in (`/login/`)
- [ ] T041 Criar array `authLinks`: Dashboard, Incidents, Analytics, Docs
- [ ] T042 Renderizar `publicLinks` quando `!$user`, `authLinks` quando `$user`
- [ ] T043 Remover Logout do menu principal (migrar para dropdown do avatar)

### Navbar — Ícones de Ação (área direita, apenas autenticado)
- [ ] T044 Adicionar botão **Upgrade**: borda `border-accent`, texto `text-accent`, ícone diamante SVG inline, placeholder sem ação
- [ ] T045 Adicionar ícone **Search** (`aria-label="Search"`, lupa SVG inline, placeholder)
- [ ] T046 Adicionar ícone **Bell** (`aria-label="Product News"`, sino SVG inline, placeholder)
- [ ] T047 Adicionar ícone **Help** (`aria-label="Help"`, círculo `?` SVG inline, placeholder)
- [ ] T048 Todos os ícones: `text-text-muted hover:text-text transition-colors` — zero cor ad-hoc

### UserAvatar — Componente
- [ ] T049 Criar `src/lib/ui/UserAvatar.svelte`
- [ ] T050 Implementar cálculo de iniciais (`displayName` → primeiras letras; fallback email)
- [ ] T051 Implementar botão circular com iniciais usando `bg-accent/20 text-accent font-semibold`
- [ ] T052 Implementar dropdown ao clicar: header (nome + email), "Minha conta" → `/settings/`, "Log out"
- [ ] T053 Implementar click-outside via `$effect` + `document.addEventListener`
- [ ] T054 Estilizar dropdown com `bg-bg-elevated border-border shadow-glow` e design tokens
- [ ] T055 Dropdown: `role="menu"`, `aria-expanded` no botão avatar

### Navbar — Mobile
- [ ] T056 Adaptar hamburger sheet para estado autenticado (authLinks + ícones + avatar)
- [ ] T057 Garantir que dropdown do avatar fecha corretamente em mobile

---

## Phase 4: Frontend — Dashboard, Docs & Settings (T058–T076, 2 dias)

**Goal**: Rotas /dashboard/, /docs/, /settings/ com auth guard e profile store.

### Store & Service de Perfil
- [ ] T058 Criar `src/lib/types/users.ts` com interfaces `UserProfile`, `UserPatch`
- [ ] T059 Criar `src/lib/services/users.ts` com `getMe()` e `updateMe(patch)`
- [ ] T060 Criar `src/lib/stores/profile.ts` com `profile` store + `loadProfile()`
- [ ] T061 Chamar `loadProfile()` em `UserAvatar.$effect` (após `$user` disponível)

### Redirect Pós-Login
- [ ] T062 Alterar `src/routes/login/+page.svelte`: redirect para `/dashboard/` após login bem-sucedido

### Dashboard
- [ ] T063 Criar `src/routes/dashboard/+page.ts` (`ssr = false`, auth guard)
- [ ] T064 Criar `src/routes/dashboard/+page.svelte` com banner "Em construção"
- [ ] T065 Estilizar com design tokens (`text-text`, `text-text-muted`, `bg-bg-surface`)

### Docs (Placeholder)
- [ ] T066 Criar `src/routes/docs/+page.ts` (`ssr = false`, auth guard)
- [ ] T067 Criar `src/routes/docs/+page.svelte` com banner "Em construção" (mesmo padrão do dashboard)

### Settings — Estrutura
- [ ] T068 Criar `src/routes/settings/+page.ts` (`ssr = false`, auth guard)
- [ ] T069 Criar `src/routes/settings/+page.svelte` com 3 seções usando `<Card>`

### Settings — Seção Perfil
- [ ] T070 Campos: `display_name` (`<Input>` editável), `job_title` (`<Input>` editável), email (read-only)
- [ ] T071 Botão "Salvar" → `updateMe()` → atualiza `profile` store localmente
- [ ] T072 Feedback visual: banner `text-success` (sucesso) ou `text-error` (erro)

### Settings — Seção Segurança
- [ ] T073 Badge "Verificado ✓" / "Não verificado" baseado em `$user.emailVerified`
- [ ] T074 Botão "Reenviar verificação" → `sendEmailVerification($user)`
- [ ] T075 Formulário alterar senha: campo atual + nova senha + confirmação → `updatePassword()`
- [ ] T076 Mapear erros Firebase: `auth/wrong-password`, `auth/weak-password`, `auth/requires-recent-login`

### Settings — Seção Plano
- [ ] T077 `<Badge>` com `$profile.plan` (design system)
- [ ] T078 "Membro desde" formatado em pt-BR com `Intl.DateTimeFormat`
- [ ] T079 CTA "Falar com a equipe" (`<Button variant="secondary">` — mailto placeholder)

---

## Phase 5: Testes, A11y & Docs (T080–T097, 2 dias)

### Testes Vitest — Navbar & Avatar
- [ ] T080 Avatar renderiza iniciais corretas a partir de `displayName` ("Renato Bardi" → "RB")
- [ ] T081 Avatar usa fallback de email quando `displayName` é null
- [ ] T082 Dropdown abre ao clicar no avatar
- [ ] T083 Dropdown fecha ao clicar fora

### Testes Vitest — Settings & Dashboard
- [ ] T084 Dashboard: renderiza banner "Em construção"
- [ ] T085 Settings Perfil: submit chama `updateMe()` com dados corretos
- [ ] T086 Settings Segurança: badge muda com `emailVerified`
- [ ] T087 Settings Plano: exibe plano e data formatada corretamente

### Acessibilidade
- [ ] T088 Todos os ícones de ação têm `aria-label`
- [ ] T089 Dropdown do avatar: `role="menu"`, `aria-expanded`, Esc fecha
- [ ] T090 Formulários de Settings: `<label>` associados, `aria-describedby` para mensagens de erro
- [ ] T091 Contraste mínimo 4.5:1 em todos os elementos novos (verificar com design tokens)

### Documentação
- [ ] T092 Atualizar `README.md`: adicionar `/dashboard/`, `/analytics/`, `/docs/`, `/settings/` na seção de rotas
- [ ] T093 Atualizar `CLAUDE.md`: atualizar seção de routes com novas rotas
- [ ] T094 JSDoc nos endpoints `GET /api/v1/users/me` e `PATCH /api/v1/users/me`

### CI & QA Final
- [ ] T095 `npm run check` — zero erros TypeScript
- [ ] T096 `npm run lint` — zero erros ESLint/Prettier
- [ ] T097 `npm run test -- --run` — todos os testes passam
- [ ] T098 `ruff check src/ tests/` — zero issues
- [ ] T099 `mypy src/` — strict, zero issues
- [ ] T100 `pytest tests/ --cov=src --cov-fail-under=80` — coverage ≥ 80%
- [ ] T101 `alembic upgrade head` aplicado localmente com Cloud SQL Proxy sem erro

---

## Dependências & Bloqueios

- Depende de: Spec-007 ✅ (Firebase auth + stores)
- Depende de: Spec-014 ✅ (Navbar base + design tokens)
- Sem dependências externas novas (sem Redis, sem Stripe)

**Bloqueios internos**:
- T016–T018 (ajuste auth dependency) devem preceder T025–T026 (endpoints /users/me)
- T058–T061 (store + service) devem preceder T071, T077 (Settings que usam profile store)
- T035–T038 (migração rota analytics) deve preceder qualquer merge que toque Navbar

---

## Ordem de Execução

1. → Phase 1 (DB + models) — base de tudo
2. → Phase 2 (service + API) — pode iniciar Phase 3 em paralelo após T018
3. → Phase 3 (Migração analytics + Navbar + Avatar)
4. → Phase 4 (Dashboard + Docs + Settings) — depende de T060 (service/store)
5. → Phase 5 (testes + a11y + docs + CI)

---

## Acceptance Criteria

- [ ] Todos os 101 tasks marcados `[x]`
- [ ] ≥ 80% coverage (backend + frontend)
- [ ] CI gates verdes: lint, type-check, test, build, Trivy, docs-check
- [ ] Mobile testado em 375px
- [ ] WCAG 2.1 AA
- [ ] Migração aplicada em produção sem erro
- [ ] `/analytics/` acessível; `/incidents/analytics/` retorna 404
- [ ] PR aprovado por @renatobardi
