# EVENTECH V2 — Matriz de permissões

✅ permitido · ⛔ negado (403) · 👤 somente o próprio recurso · 🔓 sem autenticação

| Endpoint / ação | Anônimo | Participante | Administrador/Organizador |
|---|---|---|---|
| POST /login | 🔓 | ✅ | ✅ |
| POST /usuarios (cadastro) | 🔓 só participante | — | — (admin nasce via script local) |
| GET /me | 401 | ✅ | ✅ |
| GET /usuarios | 401 | ⛔ | ✅ |
| GET /usuarios/{id} | 401 | 👤 | ✅ todos |
| PUT/DELETE /usuarios/{id} | 401 | ⛔ | ✅ |
| GET /eventos, GET /eventos/{id} | 401 | ✅ | ✅ |
| POST/PUT/DELETE /eventos | 401 | ⛔ | ✅ |
| POST /inscricoes | 401 | 👤 | ✅ |
| GET /inscricoes | 401 | ⛔ | ✅ |
| GET /inscricoes/{id} | 401 | 👤 | ✅ |
| PUT /inscricoes/{id} | 401 | ⛔ | ✅ |
| DELETE /inscricoes/{id} | 401 | 👤 | ✅ |
| /participacoes (todas) | 401 | ⛔ | ✅ |
| /certificados (todas) | 401 | ⛔ | ✅ |
| GET /health | 🔓 | ✅ | ✅ |

Perfis administrativos reconhecidos: `administrador`, `organizador`, `administrador/organizador`.

**401**: token ausente, inválido ou expirado. **403**: autenticado sem permissão. Cada linha acima é verificada em `tests/test_autorizacao.py` e nos demais arquivos de teste.
