# Spec-015: Navigation, Dashboard & Perfil do Usuário

**Criado**: 2026-04-04
**Branch**: `feat/015-nav-dashboard-profile`
**Fase**: Phase 2 — UX & Identity
**Status**: Ready for Implementation

---

## Objetivo

Refinar a navegação pública e autenticada do The Loop, criar uma página de Dashboard
placeholder pós-login, e implementar perfil de usuário com avatar interativo e página
de configurações (Profile, Security, Plan).

---

## Clarifications

### Session 2026-04-04

- Q: Quando `GET /api/v1/users/me` cria o user via upsert, `display_name` deve ser auto-populado do claim `name` do Firebase token? → A: Sim — auto-popular do claim `name` no `get_or_create`; se ausente, fica `null`
- Q: Ao remover `/incidents/analytics/`, adicionar redirect 301 em `hooks.ts` ou deixar 404? → A: Deixar 404 — rota antiga simplesmente removida, sem redirect
- Q: Settings: Tabs (`<Tabs>` de lib/ui), seções empilhadas ou sub-rotas separadas? → A: Tabs usando componente `<Tabs>` de lib/ui (Profile / Security / Plan)
- Q: `PATCH /api/v1/users/me` com `display_name: null` — limpa o campo ou 422? → A: 422 — tanto `null` quanto string vazia são rejeitados; `display_name` nunca é apagado via PATCH

---

## Contexto

**Pré-requisitos disponíveis**:
- Spec-007 ✅ (auth Firebase email/password + rotas autenticadas)
- Spec-014 ✅ (navbar existente com links Analytics e Constitution)

**Situação atual**:
- Navbar pública exibe link "Incidents" (inacessível a visitantes)
- Não existe rota `/dashboard/` nem `/settings/` nem `/docs/`
- Não existe tabela `users` nem endpoint de perfil no backend
- Avatar não existe — logout está exposto diretamente no menu
- Analytics está em `/incidents/analytics/` — deve migrar para `/analytics/`

---

## Requisitos Funcionais

### RF-001: Navbar Pública
O link "Incidents" é substituído por "Log in" apontando para `/login/`.
Quando o usuário já está autenticado, esse link não aparece — a navbar autenticada
toma seu lugar inteiramente.

### RF-002: Redirect Pós-Login
Após login bem-sucedido, o usuário é redirecionado para `/dashboard/` (em vez de `/incidents/`).

### RF-003: Página Dashboard (Placeholder)
A rota `/dashboard/` exibe um banner "Em construção" usando os design tokens do projeto.
Protegida por auth guard (redireciona para `/login/` se não autenticado).

### RF-004: Navbar Autenticada — Links de Navegação
Quando `$user` está presente, o menu exibe exclusivamente:
- **Dashboard** → `/dashboard/`
- **Incidents** → `/incidents/`
- **Analytics** → `/analytics/`
- **Docs** → `/docs/` (placeholder "Em construção")

### RF-005: Navbar Autenticada — Área de Ações (direita)
À direita dos links de navegação, em ordem:
1. **Upgrade** — botão com borda `border-accent` + ícone diamante SVG + texto `text-accent`; placeholder sem modal
2. **Search** — ícone lupa, `aria-label="Search"`, placeholder
3. **Bell** — ícone sino, `aria-label="Product News"`, placeholder
4. **Help** — ícone interrogação, `aria-label="Help"`, placeholder
5. **Avatar** — círculo com iniciais do usuário

Todos os estilos usam exclusivamente design tokens de `app.css`. Nenhuma cor ou fonte ad-hoc.

### RF-006: Avatar — Iniciais
Iniciais calculadas a partir de `displayName` (ex: "Renato Bardi" → "RB").
Fallback: primeiras duas letras do email antes do `@` (ex: "re").

### RF-007: Avatar — Dropdown ao Clicar
Clicar no avatar abre um dropdown posicionado abaixo-direita com:

```
┌──────────────────────────────┐
│ Renato Bardi                 │
│ renato@email.com             │
├──────────────────────────────┤
│ Minha conta          → /settings/
├──────────────────────────────┤
│ Log out              → handleLogout()
└──────────────────────────────┘
```

Fecha ao clicar fora (click-outside). Logout chama `handleLogout()` e redireciona para `/`.

### RF-008: Migração de Rota Analytics
A rota `/incidents/analytics/` é movida para `/analytics/`. Todas as referências no
projeto (Navbar, docs, specs, testes, CLAUDE.md, README.md, ANALYTICS.md) devem ser
atualizadas. O diretório antigo é removido.

### RF-009: Página Docs (Placeholder)
A rota `/docs/` exibe um banner "Em construção" (mesmo padrão do dashboard).
Protegida por auth guard.

### RF-009b: Página Settings — Estrutura
A rota `/settings/` usa o componente `<Tabs>` de `lib/ui` com 3 abas: **Profile**, **Security**, **Plan**. Sem sub-rotas separadas.

### RF-010: Página Settings — Perfil
Campos editáveis via `PATCH /api/v1/users/me`:
- **Nome completo** (`display_name`) — texto livre
- **Cargo / Função** (`job_title`) — texto livre, opcional

Campos read-only:
- **Email** — vem do Firebase Auth

`display_name` é auto-populado na criação do user a partir do claim `name` do Firebase token (se presente). Se ausente, fica `null` e o avatar usa fallback de email. Após criação, só é atualizado via `PATCH`.

### RF-011: Página Settings — Segurança
- **Alterar senha** — chama `updatePassword()` do Firebase SDK client
- **Status de verificação de email** — badge "Verificado" / "Não verificado" + botão "Reenviar verificação"

### RF-012: Página Settings — Plano
Exibição read-only:
- **Tipo de plano**: `beta | free | starter | pro | enterprise` (default: `beta`)
- **Membro desde**: `created_at` do registro do usuário
- **CTA**: "Falar com a equipe" (link mailto futuro)

---

## Critérios de Sucesso

### Funcionalidade
- [ ] Visitante vê "Log in" na navbar pública
- [ ] Após login, redirect para `/dashboard/`
- [ ] Dashboard exibe banner "Em construção"
- [ ] Navbar autenticada: Dashboard, Incidents, Analytics, Docs + ações + avatar
- [ ] Avatar exibe iniciais corretas com fallback
- [ ] Dropdown abre/fecha corretamente com click-outside
- [ ] Analytics acessível em `/analytics/` (rota antiga inexistente)
- [ ] Settings salva display_name e job_title via API
- [ ] Alteração de senha funciona via Firebase SDK

### Qualidade de Código
- [ ] mypy strict (0 Any values)
- [ ] ruff lint (0 issues)
- [ ] ≥ 80% test coverage
- [ ] TypeScript strict
- [ ] Design tokens exclusivamente (sem cor ad-hoc)

### UX
- [ ] Responsive (mobile-first, 375px+)
- [ ] WCAG 2.1 AA (contraste, aria-labels, keyboard nav)
- [ ] Loading states e error states nas seções de Settings

---

## User Stories

### US-001: Visitante — Acesso ao Login
**Como** visitante do The Loop
**Quero** ver um link "Log in" na navbar
**Para** acessar minha conta facilmente

**Aceitação**:
- Link visível na navbar pública
- Aponta para `/login/`
- Não aparece quando já estou logado

### US-002: Usuário — Redirect Pós-Login
**Como** usuário autenticado
**Quero** ser redirecionado para o Dashboard após o login
**Para** ter um ponto de entrada claro na área logada

**Aceitação**:
- Login bem-sucedido → `/dashboard/`
- Dashboard mostra banner "Em construção"

### US-003: Usuário — Navegação Autenticada
**Como** usuário autenticado
**Quero** uma navbar limpa com as seções principais
**Para** navegar entre Dashboard, Incidents, Analytics e Docs rapidamente

**Aceitação**:
- Links corretos e funcionais
- Avatar com iniciais visível
- Ícones de ação presentes

### US-004: Usuário — Dropdown do Avatar
**Como** usuário autenticado
**Quero** clicar no avatar e ver um menu com minhas opções
**Para** acessar minhas configurações ou sair da conta

**Aceitação**:
- Dropdown exibe nome e email
- "Minha conta" navega para `/settings/`
- "Log out" encerra a sessão e redireciona para `/`
- Fecha ao clicar fora

### US-005: Usuário — Editar Perfil
**Como** usuário autenticado
**Quero** editar meu nome e cargo na página de configurações
**Para** manter meu perfil atualizado

**Aceitação**:
- Formulário salva via PATCH /api/v1/users/me
- Feedback visual de sucesso/erro
- Email permanece read-only

---

## Arquitetura (Alto Nível)

> Detalhe completo em `plan.md`.

**Frontend**:
- `src/lib/ui/Navbar.svelte` — refatoração completa
- `src/lib/ui/UserAvatar.svelte` — componente novo (avatar + dropdown)
- `src/routes/dashboard/+page.svelte` — página nova
- `src/routes/analytics/` — movido de `incidents/analytics/`
- `src/routes/docs/+page.svelte` — placeholder nova
- `src/routes/settings/+page.svelte` — página nova
- `src/lib/services/users.ts` — API client novo
- `src/lib/stores/profile.ts` — store novo

**Backend**:
- `alembic/versions/010_create_users.py` — migração nova
- `src/domain/models.py` — User, UserPlan adicionados
- `src/ports/user_repo.py` — UserRepoPort novo
- `src/adapters/postgres/user_repository.py` — UserRepository novo
- `src/domain/services.py` — UserService adicionado
- `src/api/routes/users.py` — /users/me endpoints novos
- `src/api/models/users.py` — request/response models novos

---

## Restrições

- **Design tokens**: todo estilo via `app.css` tokens — sem cor ou fonte ad-hoc
- **Sem Organization**: conceito de org fora do escopo desta spec
- **Sem billing automatizado**: plano é campo read-only gerenciado manualmente
- **Mobile-first**: 375px+
- **Firebase Auth**: alteração de senha via SDK client (não backend)

---

## Out of Scope

- ❌ Organizations / teams (deferred — Spec-futura)
- ❌ Upload de foto de perfil (deferred)
- ❌ Preferências de notificação (deferred)
- ❌ Tema light/dark (deferred)
- ❌ Billing automatizado / Stripe (deferred)
- ❌ Funcionalidade real dos ícones Search, Bell, Help (deferred)
- ❌ Funcionalidade real do botão Upgrade (deferred)

---

## Edge Cases

**E-001**: Usuário sem `displayName` no Firebase
- Fallback para 2 primeiras letras do email antes do `@`
- Salvar display_name via PATCH atualiza o avatar imediatamente

**E-002**: Primeiro acesso — nenhum registro na tabela `users`
- GET /api/v1/users/me faz upsert: cria registro com `plan=beta` se não existir

**E-003**: PATCH com display_name inválido
- `display_name: ""` (string vazia) → 422
- `display_name: null` → 422
- Campo nunca é apagado via PATCH; para "limpar", omitir o campo do body

**E-004**: Alteração de senha com senha atual incorreta
- Firebase SDK retorna `auth/wrong-password`; frontend exibe "Senha atual incorreta"

**E-005**: Acesso direto à URL antiga `/incidents/analytics/`
- Rota antiga removida sem redirect — retorna 404 (SvelteKit default)

---

## Próximos Passos

1. ✅ Aprovação da spec
2. ✅ plan.md (arquitetura detalhada)
3. ✅ tasks.md (task breakdown)
4. → Implementação (5 fases, ~10 dias)
