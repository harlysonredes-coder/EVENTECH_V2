# Melhorias de qualidade realizadas

O requisito pedia **no mínimo três** melhorias. Foram feitas **cinco**; as três primeiras são as principais e as duas últimas complementam.

Todas as demonstrações abaixo foram **executadas**, não apenas descritas. A comparação lado a lado (mesmos 7 cenários rodados no commit inicial `3ca2091` e na versão final) está em [`evidencias/antes_depois.txt`](evidencias/antes_depois.txt) e pode ser reproduzida com `docs/evidencias/demo_antes_depois.py`.

| # | Melhoria | Commit |
|---|---|---|
| 1 | Separação de responsabilidades (rotas × regras × dados) | `refactor(services)`, `refactor(api)` |
| 2 | Tratamento de erros e status codes padronizados | `feat(erros)` |
| 3 | Integridade de dados e validação de entrada | `feat(erros)`, `refactor(services)` |
| 4 | Segurança e configuração por ambiente | `refactor(config)`, `refactor(api)` |
| 5 | Remoção de código morto/duplicado | `refactor(config)` |

---

## 1. Separação de responsabilidades

**Problema.** `api/routes.py` tinha **844 linhas** misturando HTTP, autenticação, regras de negócio e acesso a dados. Havia **49 consultas** `db.query(...)` repetidas nas rotas; as regras de certificado estavam escritas duas vezes (POST e PUT), assim como as de participação e inscrição, e a checagem de perfis administrativos existia em dois lugares (`PERFIS_ADMIN` e uma tupla local em `excluir_inscricao`).

**Solução.** Arquitetura em camadas:

```
api/routers/*  →  services/*  →  models/*
 (HTTP, perfis)   (regras)        (persistência)
```

| Métrica | Antes | Depois |
|---|---|---|
| Arquivo único de rotas | 844 linhas | 6 routers (260 linhas no total) |
| `db.query(...)` dentro das rotas | 49 | 5 (apenas as listagens simples) |
| Regras de negócio duplicadas (POST/PUT) | sim | 1 função por regra |
| Regras testáveis sem HTTP | 0 | `garantir_vaga`, `validar_horas`, `validar_elegibilidade`... |

Exemplo (regra de elegibilidade do certificado): antes, ~25 linhas copiadas em `criar_certificado` e `atualizar_certificado`; depois, uma função reutilizada pelos dois fluxos:

```python
def validar_elegibilidade(participacao, evento) -> None:
    if not participacao.presente:
        raise RegraDeNegocio("Participante não esteve presente no evento")
    if participacao.horas_obtidas < evento.carga_horaria:
        raise RegraDeNegocio("Carga horária insuficiente para emissão do certificado")
```

> Honestidade nos números: o total de linhas de código **aumentou** (routers + services ≈ 530 vs 844 em routes.py, mais docstrings e documentação OpenAPI por endpoint). O ganho está na ausência de duplicação, na testabilidade e em cada arquivo ter uma única responsabilidade.

## 2. Tratamento de erros e status codes padronizados

**Problema.** 62 `raise HTTPException` espalhados; **22 usos de 400 genérico** para situações diferentes (duplicidade, sem vagas, regra violada); o formato do erro mudava conforme a origem (`{"detail": "..."}` vs lista do Pydantic).

**Solução.** Exceções de domínio (`core/exceptions.py`) e handlers globais (`core/errors.py`). Zero `HTTPException` em rotas e serviços; um único corpo de erro:

```json
{ "status": 409, "codigo": "CONFLITO", "mensagem": "Evento sem vagas disponíveis", "detalhes": null }
```

| Situação | Antes | Depois |
|---|---|---|
| Inscrição duplicada / sem vagas / certificado repetido | 400 | **409** `CONFLITO` |
| Capacidade ≤ 0, horas inválidas, sem presença | 400 | **422** `REGRA_DE_NEGOCIO` / `REQUISICAO_INVALIDA` |
| Rota inexistente, 405 | corpo do framework | mesmo formato padronizado |
| Erro inesperado | stack trace possível | **500** genérico (detalhe só no log) |

Evidência: cenários 2–5 de `antes_depois.txt`; testes em `tests/test_erros_padronizados.py`.

## 3. Integridade de dados e validação de entrada

**Problema (reproduzido).** No código original, `DELETE /eventos/{id}` com inscrições retornava **200** e deixava a **inscrição órfã** no banco (cenário 6). O cadastro aceitava `"email": "invalido"` e senha de 1 caractere (**201**, cenário 7). A unicidade "um usuário por evento" dependia só de um `if` (condição de corrida possível).

**Solução.**
- Restrições no banco: `UniqueConstraint(id_usuario, id_evento)`, `unique` em `participacoes.id_inscricao` e `certificados.id_participacao`; `PRAGMA foreign_keys=ON` no SQLite.
- Exclusão com dependentes → **409** (usuário/evento → inscrições; inscrição → participação; participação → certificado).
- Nova regra: capacidade não pode ficar abaixo do nº de inscritos (422).
- Validação declarativa no schema (`Field(gt=0)`, e-mail por padrão, senha ≥ 8, e-mail normalizado em minúsculas, perfil restrito a valores válidos).
- `presente` passou de `Integer` para `Boolean` (coerente com o schema).

## 4. Segurança e configuração por ambiente

- **Login**: credenciais iam na *query string* (`POST /login?email=..&senha=..`), que aparece em logs de acesso e histórico. Agora só no **corpo JSON** — a versão antiga é rejeitada com 422 (cenário 1; teste de regressão `test_login_nao_aceita_credenciais_na_url`).
- `core/config.py` centraliza variáveis de ambiente; `DATABASE_URL` configurável (antes, SQLite fixo no código); `JWT_SECRET_KEY` exige ≥ 32 caracteres.
- Usuário do token removido do banco → 401 (antes seria 404 em `/me`).
- `scripts/alterar_senha_admin.py` tinha um e-mail fixo no código; agora recebe o e-mail como argumento.

## 5. Código morto e duplicado

- `database.py` e `models.py` na raiz duplicavam `core/database.py` e `models/` (o `models.py` era sombreado pelo pacote `models/`, nunca executado). Removidos.
- `main.py` importava módulos que não usava e definia um `get_db` próprio; agora é um `create_app()` enxuto.
- `Base.metadata.create_all` rodava como efeito colateral do `import models`; agora é explícito no *startup* (`lifespan`).

---

## Como reproduzir a demonstração

```bash
# versão final
PYTHONPATH=. python docs/evidencias/demo_antes_depois.py
# versão original (para comparar)
git worktree add /tmp/antes 3ca2091 && (cd /tmp/antes && PYTHONPATH=/tmp/antes python <caminho>/demo_antes_depois.py)
```
