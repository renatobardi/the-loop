# Spec-017: Rules Expansion — Multi-Language Pack

**Status:** Stub — aguardando conclusão da spec-016  
**Branch:** `feat/017-rules-expansion`  
**Depende de:** spec-016 (semgrep-platform) concluída e mergeada

---

## Contexto

A spec-016 entrega as regras para Python (20, já existentes), JS/TS e Go. Esta spec expande a cobertura para as demais linguagens do top 10 mais usadas no mercado, tornando o The Loop um produto multi-linguagem completo.

---

## Escopo

### Linguagens alvo

| Linguagem | Regras estimadas | Esforço |
|-----------|-----------------|---------|
| Java      | 15              | Médio   |
| C#        | 15              | Médio   |
| PHP       | 10              | Fácil-Médio |
| Ruby      | 10              | Fácil   |
| Kotlin    | 10              | Médio   |
| Rust      | 8               | Fácil-Médio |
| C/C++     | 10              | Difícil |

**Total:** ~78 novas regras

### Categorias por linguagem (padrão)
- Injection (SQL, command, path traversal)
- Crypto (algoritmos fracos, secrets hardcoded)
- Security (TLS, CORS, JWT)
- Performance (N+1, timeouts)
- Error handling
- Linguagem-específico (ex: JDBC para Java, unsafe blocks para Rust)

### Entregáveis por linguagem
- Regras Semgrep validadas (`semgrep --validate`)
- Test data: `tests/test-data/bad/<lang>/` e `tests/test-data/good/<lang>/`
- Publicação como nova versão (ex: v0.3.0)

### Melhorias UX na web
- Dashboard: link rápido para browse de rules ativas (concluído em PR #79)
- `/rules/[version]/` já acessível publicamente
- Links no Footer já existem

---

## Fora do escopo
- Regras customizadas por projeto (spec futura)
- Regras sugeridas por AI (spec futura)
- Swift, Scala, Dart (fase posterior)

---

## Estimativa
~30–35 dias | ~7 linguagens | publicação como v0.3.0

---

## Próxima revisão
Detalhar após merge da spec-016.
