# EVENTECH V2

API REST para gestão de **eventos acadêmicos**: usuários, eventos, inscrições, participações e emissão de certificados, com autenticação JWT e controle de acesso por perfil.

> Projeto acadêmico da disciplina de Desenvolvimento Back-End.

![testes](https://img.shields.io/badge/testes-91%20passando-brightgreen) ![cobertura](https://img.shields.io/badge/cobertura-95%25-brightgreen)

## Sumário
[Tecnologias](#tecnologias) · [Instalação](#instalação-e-execução) · [Variáveis de ambiente](#variáveis-de-ambiente) · [Estrutura](#estrutura-do-projeto) · [Endpoints](#endpoints) · [Regras de negócio](#regras-de-negócio) · [Erros](#padrão-de-erros-e-status-codes) · [Testes](#testes) · [Deploy](#deploy-e-persistência) · [Documentação extra](#documentação-complementar)

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Framework web | FastAPI (OpenAPI/Swagger automático) |
| Persistência | SQLAlchemy 2 · SQLite (local) · PostgreSQL (produção) |
| Autenticação | JWT (PyJWT, HS256, 30 min) · senhas com Argon2 (pwdlib) |
| Validação | Pydantic 2 |
| Testes | pytest · pytest-cov · httpx/TestClient |
| Entrega | Docker · Render (`render.yaml`) · GitHub Actions |

## Instalação e execução

Requer **Python 3.12+**.

```bash
git clone <url-do-repositorio> && cd EVENTECH_V2
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

cp .env.example .env                                   # Windows: copy .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # cole o resultado em JWT_SECRET_KEY no .env

python -m uvicorn main:app --reload
```

- Swagger UI: <http://127.0.0.1:8000/docs> · ReDoc: <http://127.0.0.1:8000/redoc> · Health: `/health`
- As tabelas são criadas automaticamente na primeira execução.

**Criar o primeiro administrador** (não existe cadastro de admin pela API, por segurança):

```bash
python -m scripts.criar_admin_local          # interativo (a senha não aparece na tela)
python -m scripts.alterar_senha_admin <email> # redefinir senha
```

**Usando o Swagger:** `POST /login` → copie o `access_token` → botão **Authorize** → cole o token.

## Variáveis de ambiente

Nenhum segredo está no código. Use `.env` localmente (ignorado pelo Git) e o painel do provedor em produção.

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `JWT_SECRET_KEY` | **sim** | – | Segredo de assinatura do JWT (mín. 32 caracteres). A aplicação recusa autenticar sem ele. |
| `DATABASE_URL` | não | `sqlite:///./eventech.db` | URL SQLAlchemy. Em produção: `postgresql://user:senha@host:5432/db` (`postgres://` também é aceito). |
| `TOKEN_EXPIRE_MINUTES` | não | `30` | Validade do token. |
| `CORS_ORIGINS` | não | vazio | Origens permitidas, separadas por vírgula. Vazio = CORS desativado. |
| `ADMIN_EMAIL` / `ADMIN_NOME` / `ADMIN_SENHA` | não | – | Só para `scripts.criar_admin_local` sem interação (deploy). |

## Estrutura do projeto

```
main.py                 # create_app(): rotas, CORS, handlers de erro, OpenAPI
api/
  deps.py               # autenticação/autorização (JWT, perfis)
  docs.py               # respostas de erro reutilizadas no Swagger
  routers/              # rotas finas por recurso (auth, usuarios, eventos, inscricoes, participacoes, certificados)
services/               # REGRAS DE NEGÓCIO (sem HTTP): vagas, duplicidade, horas, elegibilidade...
models/entities.py      # entidades SQLAlchemy + restrições de integridade
schemas/schemas.py      # contratos Pydantic de entrada/saída
core/
  config.py             # leitura de variáveis de ambiente
  database.py           # engine, sessão, get_db, criar_tabelas
  security.py           # hash de senha e JWT
  exceptions.py         # exceções de domínio (401/403/404/409/422)
  errors.py             # handlers globais -> formato único de erro
scripts/                # utilitários administrativos
tests/                  # 91 testes automatizados
docs/                   # matriz de permissões, melhorias, deploy, openapi.json, evidências
```

Fluxo de uma requisição: **router** (HTTP + permissão) → **service** (regra de negócio) → **models** (banco). Violações viram exceções de domínio, convertidas em resposta padronizada por `core/errors.py`.

## Endpoints

🔓 público · 🔑 qualquer usuário autenticado · 👤 próprio recurso (ou admin) · 🛡️ somente administrador/organizador

| Método | Rota | Acesso | Descrição | Sucesso | Erros possíveis |
|---|---|---|---|---|---|
| POST | `/login` | 🔓 | Autentica e devolve JWT (corpo JSON) | 200 | 401, 422 |
| GET | `/me` | 🔑 | Dados do usuário logado | 200 | 401 |
| POST | `/usuarios` | 🔓 | Cadastro público (somente `participante`) | 201 | 403, 409, 422 |
| GET | `/usuarios` | 🛡️ | Lista usuários | 200 | 401, 403 |
| GET | `/usuarios/{id}` | 👤 | Busca usuário | 200 | 401, 403, 404 |
| PUT | `/usuarios/{id}` | 🛡️ | Atualiza usuário/perfil | 200 | 401, 403, 404, 409, 422 |
| DELETE | `/usuarios/{id}` | 🛡️ | Exclui usuário sem inscrições | 200 | 401, 403, 404, 409 |
| POST | `/eventos` | 🛡️ | Cria evento | 201 | 401, 403, 422 |
| GET | `/eventos` · `/eventos/{id}` | 🔑 | Lista / busca evento | 200 | 401, 404 |
| PUT | `/eventos/{id}` | 🛡️ | Atualiza evento | 200 | 401, 403, 404, 422 |
| DELETE | `/eventos/{id}` | 🛡️ | Exclui evento sem inscrições | 200 | 401, 403, 404, 409 |
| POST | `/inscricoes` | 👤 | Inscreve em evento | 201 | 401, 403, 404, 409, 422 |
| GET | `/inscricoes` | 🛡️ | Lista inscrições | 200 | 401, 403 |
| GET | `/inscricoes/{id}` | 👤 | Busca inscrição | 200 | 401, 403, 404 |
| PUT | `/inscricoes/{id}` | 🛡️ | Atualiza inscrição | 200 | 401, 403, 404, 409, 422 |
| DELETE | `/inscricoes/{id}` | 👤 | Cancela inscrição | 200 | 401, 403, 404, 409 |
| POST/GET/PUT/DELETE | `/participacoes[/{id}]` | 🛡️ | Presença e horas obtidas | 200/201 | 401, 403, 404, 409, 422 |
| POST/GET/PUT/DELETE | `/certificados[/{id}]` | 🛡️ | Emissão e gestão de certificados | 200/201 | 401, 403, 404, 409, 422 |
| GET | `/health` | 🔓 | Verificação de saúde | 200 | – |

Detalhes completos (schemas, exemplos, respostas): Swagger em `/docs` ou [`docs/openapi.json`](docs/openapi.json). Matriz por perfil: [`docs/MATRIZ_PERMISSOES.md`](docs/MATRIZ_PERMISSOES.md).

## Regras de negócio

| # | Regra | Resposta ao violar |
|---|---|---|
| RN01 | Cadastro público só cria `participante`; administradores nascem por script local | 403 |
| RN02 | E-mail único (sem diferenciar maiúsculas/minúsculas) | 409 |
| RN03 | Capacidade e carga horária do evento devem ser > 0 | 422 |
| RN04 | Um usuário só pode se inscrever **uma vez** por evento | 409 |
| RN05 | Inscrição não pode exceder a **capacidade** do evento | 409 |
| RN06 | Participante só inscreve/cancela/consulta **a si mesmo** | 403 |
| RN07 | Capacidade não pode ser reduzida abaixo do nº de inscritos | 422 |
| RN08 | Horas obtidas entre 0 e a carga horária do evento | 422 |
| RN09 | Uma participação por inscrição | 409 |
| RN10 | Certificado exige **presença** confirmada | 422 |
| RN11 | Certificado exige horas obtidas ≥ carga horária | 422 |
| RN12 | Um certificado por participação | 409 |
| RN13 | Não exclui registro com dependentes (usuário/evento → inscrições; inscrição → participação; participação → certificado) | 409 |

## Padrão de erros e status codes

Todo erro, de qualquer endpoint, tem o mesmo corpo:

```json
{ "status": 409, "codigo": "CONFLITO", "mensagem": "Evento sem vagas disponíveis", "detalhes": null }
```

| Status | `codigo` | Quando |
|---|---|---|
| 401 | `NAO_AUTENTICADO` | Token ausente, inválido ou expirado; login incorreto |
| 403 | `ACESSO_NEGADO` | Autenticado, mas sem permissão |
| 404 | `NAO_ENCONTRADO` | Recurso ou rota inexistente |
| 409 | `CONFLITO` | Duplicidade, sem vagas, registro com dependências |
| 422 | `REGRA_DE_NEGOCIO` / `REQUISICAO_INVALIDA` | Regra violada / corpo inválido (com `detalhes` por campo) |
| 500 | `ERRO_INTERNO` | Falha inesperada (detalhes só no log, nunca na resposta) |

## Testes

```bash
python -m pytest -v                                # executa os 91 testes
python -m pytest --cov=. --cov-report=term-missing # com cobertura (95%)
```

Os testes usam **SQLite em memória isolado por teste**: não tocam em `eventech.db` nem exigem `.env`. Cobrem autenticação/RBAC, todas as regras RN01–RN13 (cenários positivos e negativos), formato padronizado de erros, regras unitárias dos serviços, configuração e fidelidade do OpenAPI. Execução registrada em [`docs/evidencias/pytest.txt`](docs/evidencias/pytest.txt). A pipeline do GitHub Actions (`.github/workflows/ci.yml`) roda a suíte a cada push.

## Deploy e persistência

Resumo (guia completo em [`docs/DEPLOY.md`](docs/DEPLOY.md)):

- **Persistência:** SQLite apenas para desenvolvimento. Em produção use **PostgreSQL** via `DATABASE_URL` (o disco de contêineres/PaaS é efêmero e o SQLite seria perdido a cada deploy).
- **Render:** `render.yaml` provisiona web service + PostgreSQL e gera `JWT_SECRET_KEY` automaticamente.
- **Docker:** `docker build -t eventech . && docker run -p 8000:8000 -e JWT_SECRET_KEY=... -e DATABASE_URL=... eventech`
- **Segredos:** só em variáveis de ambiente do provedor; `.env` está no `.gitignore`.

## Documentação complementar

- [`docs/MELHORIAS.md`](docs/MELHORIAS.md) — as melhorias de qualidade, com antes/depois
- [`docs/DEPLOY.md`](docs/DEPLOY.md) — passo a passo de publicação
- [`docs/MATRIZ_PERMISSOES.md`](docs/MATRIZ_PERMISSOES.md) — permissões por perfil
