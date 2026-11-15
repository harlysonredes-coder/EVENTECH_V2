# EVENTECH V2 — Matriz de permissões proposta

| Endpoint / ação | Participante | Administrador/Organizador |
|---|---|---|
| POST /usuarios (cadastro público) | Criar apenas participante | Criar apenas participante (admin via script local) |
| GET /usuarios | Negado (403) | Permitido |
| GET /usuarios/{id} | Somente próprio | Todos |
| PUT/DELETE /usuarios/{id} | Negado (403) | Permitido |
| GET /eventos e GET /eventos/{id} | Permitido com JWT | Permitido |
| POST/PUT/DELETE /eventos | Negado (403) | Permitido |
| POST /inscricoes | Apenas própria | Permitido |
| GET /inscricoes | Negado (403) | Permitido |
| GET /inscricoes/{id} | Apenas própria | Permitido |
| PUT /inscricoes/{id} | Negado (403) | Permitido |
| DELETE /inscricoes/{id} | Apenas própria | Permitido |
| Participações e certificados (consultas e alterações) | Negado (403) | Permitido |
| GET /me | Permitido | Permitido |

**401**: ausente, inválido ou expirado. **403**: autenticado sem permissão.

Esta matriz é uma proposta para revisão frente à matriz original da Primeira Unidade, antes de entregar.
