# Plan: Navigation, Dashboard & Perfil do Usuário (Spec-015)

**Tech Stack**: SvelteKit 2 + Svelte 5 runes, Tailwind 4, Firebase SDK 11, FastAPI, SQLAlchemy 2.0 async, Pydantic v2, PostgreSQL 16

---

## Phase Overview

| Phase | Título | Dias | Tasks | Entregável |
|-------|--------|------|-------|------------|
| 1 | Backend: DB & Models | 2 | 11 | Migração, User model, port |
| 2 | Backend: Service & API | 2 | 17 | UserService, /users/me endpoints |
| 3 | Frontend: Navbar & Avatar | 2 | 18 | Navbar refatorada, UserAvatar.svelte |
| 4 | Frontend: Dashboard & Settings | 2 | 19 | /dashboard/, /docs/, /settings/ |
| 5 | Testes, A11y & Docs | 2 | 18 | Coverage ≥80%, CI verde |

**Total**: ~83 tasks | ~10 dias

---

## Architecture

### Backend — Tabela `users`

**Migration**: `alembic/versions/010_create_users.py`

```sql
CREATE TABLE users (
    id           UUID PRIMARY KEY,            -- uuid5(NAMESPACE_URL, "firebase:{uid}")
    firebase_uid VARCHAR(128) NOT NULL UNIQUE,
    email        VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    job_title    VARCHAR(255),
    plan         VARCHAR(32) NOT NULL DEFAULT 'beta',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_users_firebase_uid ON users(firebase_uid);
```

### Backend — Domain Models

```python
# domain/models.py (adições)

class UserPlan(StrEnum):
    FREE = "free"
    BETA = "beta"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class User(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    firebase_uid: str
    email: str
    display_name: str | None = None
    job_title: str | None = None
    plan: UserPlan = UserPlan.BETA
    created_at: datetime
    updated_at: datetime
```

### Backend — Port

```python
# ports/user_repo.py
class UserRepoPort(Protocol):
    async def get_or_create(self, firebase_uid: str, email: str) -> User: ...
    async def update(self, user_id: UUID, display_name: str | None, job_title: str | None) -> User: ...
```

### Backend — Repository

`adapters/postgres/user_repository.py`:
- `get_or_create()`: SELECT pelo firebase_uid; se não existir, INSERT com uuid5 + plan=beta
- `update()`: UPDATE display_name, job_title, updated_at WHERE id = user_id
- `_row_to_domain()`: mapper Row → User

```python
# Padrão uuid5 (mesmo já usado no domínio)
import uuid
user_id = uuid.uuid5(uuid.NAMESPACE_URL, f"firebase:{firebase_uid}")
```

### Backend — Service

```python
# domain/services.py (adição)
class UserService:
    def __init__(self, repo: UserRepoPort): ...

    async def get_or_create(self, firebase_uid: str, email: str) -> User:
        return await self._repo.get_or_create(firebase_uid, email)

    async def update_profile(
        self, user_id: UUID, display_name: str | None, job_title: str | None
    ) -> User:
        if display_name is not None and len(display_name.strip()) == 0:
            raise ValueError("display_name cannot be empty string")
        return await self._repo.update(user_id, display_name, job_title)
```

### Backend — Adaptar Auth Dependency

O `get_authenticated_user` atual retorna apenas `UUID`. Precisamos também de
`firebase_uid` e `email` para o upsert do perfil.

**Opção escolhida**: criar dependência auxiliar `get_firebase_token_data` em `api/deps.py`
que retorna `{"user_id": UUID, "firebase_uid": str, "email": str}`. As rotas existentes
continuam usando `get_authenticated_user` sem alteração — retrocompatível.

`adapters/firebase/auth.py` — ajustar para retornar também `uid` e `email` do token
decodificado além do UUID.

### Backend — API Models

```python
# api/models/users.py
class UserResponse(BaseModel):
    id: UUID
    email: str
    display_name: str | None
    job_title: str | None
    plan: str
    created_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse": ...

class UserUpdateRequest(BaseModel):
    display_name: str | None = None
    job_title: str | None = None
```

### Backend — API Routes

`api/routes/users.py`:

**GET /api/v1/users/me**
- Usa `get_firebase_token_data` para obter uid + email + UUID
- Chama `UserService.get_or_create(firebase_uid, email)` — upsert automático
- Retorna `UserResponse`
- Rate limit: 60/minute

**PATCH /api/v1/users/me**
- Body: `UserUpdateRequest { display_name?, job_title? }`
- Chama `UserService.update_profile(user_id, display_name, job_title)`
- Retorna `UserResponse` atualizado
- 422 se display_name = ""
- Rate limit: 60/minute

### Backend — Deps

```python
# api/deps.py (adição)
async def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    repo = UserRepository(session)
    return UserService(repo)
```

---

### Frontend — Migração de Rota Analytics

Antes: `src/routes/incidents/analytics/`
Depois: `src/routes/analytics/`

1. Copiar `+page.svelte` e `+page.ts` para `src/routes/analytics/`
2. Busca global por `/incidents/analytics/` → `/analytics/` em todo o projeto
3. Remover `src/routes/incidents/analytics/`
4. Verificar se `src/routes/incidents/` ainda tem outros filhos (sim: list, [id]/, new/)

Arquivos afetados confirmados:
- `src/lib/ui/Navbar.svelte`
- `ANALYTICS.md`, `README.md`, `CLAUDE.md`
- `specs/014-incident-analytics/` (docs históricos — atualizar referências)
- Testes que referenciem a URL

### Frontend — Navbar Refatoração

`apps/web/src/lib/ui/Navbar.svelte` — estrutura final:

**Estado não autenticado** (`!$user`):
```
[The Loop]  Features · Pricing · Waitlist · Log in
```

**Estado autenticado** (`$user`):
```
[The Loop]  Dashboard · Incidents · Analytics · Docs     [Upgrade] 🔍 🔔 ? [RB]
```

Mobile: hamburger abre sheet com links + seção de ações. Avatar no topo do sheet.

**Implementação**:
- Array `publicLinks` = Features, Pricing, Waitlist, Log in (`/login/`)
- Array `authLinks` = Dashboard (`/dashboard/`), Incidents (`/incidents/`), Analytics (`/analytics/`), Docs (`/docs/`)
- Componente `<UserAvatar />` importado de `$lib/ui/UserAvatar.svelte`
- Ícones inline SVG (sem dependência externa) com `text-text-muted hover:text-text transition-colors`

### Frontend — UserAvatar.svelte

Novo componente `apps/web/src/lib/ui/UserAvatar.svelte`:

```svelte
<script lang="ts">
  import { user } from '$lib/stores/auth';
  import { profile } from '$lib/stores/profile';
  import { goto } from '$app/navigation';

  let open = $state(false);
  let avatarEl = $state<HTMLButtonElement | null>(null);

  const initials = $derived(() => {
    const name = $profile?.display_name ?? $user?.displayName;
    if (name) {
      return name.split(' ').slice(0, 2).map((w: string) => w[0]).join('').toUpperCase();
    }
    return ($user?.email ?? 'U').slice(0, 2).toUpperCase();
  });

  function handleClickOutside(e: MouseEvent) {
    if (avatarEl && !avatarEl.contains(e.target as Node)) open = false;
  }

  $effect(() => {
    if (open) document.addEventListener('click', handleClickOutside);
    else document.removeEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  });

  async function handleLogout() {
    const { logout } = await import('$lib/firebase');
    await logout();
    await goto('/');
  }
</script>
```

Dropdown: `bg-bg-elevated border border-border rounded-lg shadow-glow`
Header: nome `text-text font-semibold`, email `text-text-muted text-sm`
Items: `text-text hover:bg-bg-surface transition-colors`

### Frontend — Stores & Service de Perfil

**`lib/stores/profile.ts`**:
```typescript
import { writable } from 'svelte/store';
import type { UserProfile } from '$lib/types/users';

export const profile = writable<UserProfile | null>(null);

export async function loadProfile(): Promise<void> {
  const { getMe } = await import('$lib/services/users');
  const data = await getMe();
  profile.set(data);
}
```

**`lib/services/users.ts`**:
```typescript
// Segue padrão de analytics.ts: anexa Firebase ID token
export async function getMe(): Promise<UserProfile> { ... }    // GET /api/v1/users/me
export async function updateMe(patch: UserPatch): Promise<UserProfile> { ... }  // PATCH
```

`loadProfile()` é chamado em `UserAvatar.$effect` na primeira montagem do componente
(após `$user` disponível), mantendo o store atualizado.

### Frontend — Dashboard

`routes/dashboard/+page.ts`:
```typescript
export const ssr = false;
// Auth guard: mesmo padrão de incidents/+layout.ts
```

`routes/dashboard/+page.svelte`:
- Container centralizado com `<Section>`
- Ícone SVG de construção + heading "Em construção" + subtítulo informativo
- Estilo: `text-text`, `text-text-muted`, `bg-bg-surface`

### Frontend — Docs (Placeholder)

Idêntico ao Dashboard — banner "Em construção" com auth guard.

### Frontend — Settings

`routes/settings/+page.svelte` — 3 seções com `<Card>` do design system:

**Seção Perfil**:
- `<Input>` para `display_name` e `job_title`
- Email como `<p class="text-text-muted">` (read-only)
- Botão `<Button variant="primary">Salvar</Button>` → `updateMe()` → atualiza `profile` store
- Feedback: banner `text-success` (sucesso) ou `text-error` (erro)

**Seção Segurança**:
- Badge `text-success`/`text-error` baseado em `$user.emailVerified`
- Botão "Reenviar verificação" → `sendEmailVerification($user)`
- Formulário: senha atual + nova senha + confirmação → `updatePassword()`
- Erros Firebase mapeados: `auth/wrong-password`, `auth/weak-password`, `auth/requires-recent-login`

**Seção Plano**:
- `<Badge>` com `$profile.plan` (design system)
- "Membro desde" formatado: `new Intl.DateTimeFormat('pt-BR').format(created_at)`
- CTA `<Button variant="secondary">Falar com a equipe</Button>` (mailto placeholder)

---

## Testing Strategy

### Unit Tests (Backend)
- `UserPlan` enum values corretos
- `User` model: frozen, campos obrigatórios, defaults
- `UserService.update_profile()` rejeita display_name vazio ("")
- `UserService.get_or_create()` retorna user existente na segunda chamada

### API Tests
- `GET /api/v1/users/me` → 200 + UserResponse (upsert na primeira call)
- `GET /api/v1/users/me` chamado 2x → mesmo id retornado
- `GET /api/v1/users/me` sem auth → 401
- `PATCH /api/v1/users/me` com display_name válido → 200
- `PATCH /api/v1/users/me` com display_name="" → 422
- `PATCH /api/v1/users/me` sem auth → 401

### Frontend Tests (Vitest)
- `UserAvatar` renderiza iniciais de displayName ("Renato Bardi" → "RB")
- `UserAvatar` usa fallback de email (null displayName → "re" de "renato@...")
- Dropdown abre ao clicar no avatar
- Dropdown fecha ao clicar fora
- Dashboard renderiza banner "Em construção"
- Settings Perfil: submit chama `updateMe()` com dados corretos
- Settings Segurança: badge muda com `emailVerified`
- Settings Plano: exibe plano e data formatada

---

## Deployment

**Ordem obrigatória**:
1. Migração DB (`alembic upgrade head` — sem breaking changes em tabelas existentes)
2. Backend API (nova rota `/users/me` — backward compatible)
3. Frontend (novo Navbar, Dashboard, Settings, migração de rota Analytics)

**Rollback**:
- API: reverter Docker image
- Frontend: reverter build SvelteKit
- DB: `alembic downgrade -1` (DROP TABLE users — sem FK em outras tabelas)

---

## Risco & Mitigação

| Risco | Severidade | Mitigação |
|-------|-----------|-----------|
| `get_authenticated_user` só retorna UUID | Alta | Criar `get_firebase_token_data` auxiliar; rotas existentes intocadas |
| Profile store desatualizado após PATCH | Baixa | Atualizar store localmente com resposta da API |
| Dropdown sem click-outside no mobile | Média | Testar em iOS/Android; adicionar backdrop overlay se necessário |
| Migração falha em produção | Baixa | Testar com Cloud SQL Proxy localmente antes do merge |
| Links para `/incidents/analytics/` externos | Baixa | Adicionar redirect 301 em `hooks.ts` se necessário |

---

## Success Criteria

- [ ] Todos os CI gates verdes (ruff, mypy, ESLint, Prettier, pytest, Vitest, build, Trivy)
- [ ] Coverage ≥ 80% (backend + frontend)
- [ ] Mobile testado em 375px
- [ ] WCAG 2.1 AA validado
- [ ] Migração aplicada em produção sem erro
- [ ] `/analytics/` acessível; `/incidents/analytics/` retorna 404 ou redirect
- [ ] PR aprovado por @renatobardi
