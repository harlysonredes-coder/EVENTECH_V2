# Guia de deploy

## Decisões
| Tema | Decisão | Motivo |
|---|---|---|
| Banco em produção | PostgreSQL (`DATABASE_URL`) | Discos de PaaS/contêiner são efêmeros: um SQLite em arquivo seria apagado a cada deploy/reinício. |
| Banco local/testes | SQLite | Zero configuração. |
| Segredos | Variáveis de ambiente | Nada sensível no repositório ou na imagem Docker. |
| Esquema do banco | `create_all` no startup | Cria tabelas ausentes. **Não migra** tabelas existentes (ver limitações). |
| Servidor | `uvicorn main:app --host 0.0.0.0 --port $PORT` | Porta injetada pelo provedor. |
| Verificação de saúde | `GET /health` | Usado por Render e pelo `HEALTHCHECK` do Docker. |

## Opção A — Render (recomendada)
1. Suba o repositório ao GitHub.
2. Render → **New → Blueprint** → selecione o repositório (usa o `render.yaml`).
3. O Render cria o PostgreSQL, injeta `DATABASE_URL` e **gera** `JWT_SECRET_KEY`.
4. Após o primeiro deploy, abra o **Shell** do serviço e crie o administrador:
   ```bash
   python -m scripts.criar_admin_local
   ```
5. Valide: `https://<seu-app>.onrender.com/health` e `/docs`.

## Opção B — Docker
```bash
docker build -t eventech .
docker run -p 8000:8000 \
  -e JWT_SECRET_KEY="$(python -c 'import secrets;print(secrets.token_hex(32))')" \
  -e DATABASE_URL="postgresql://usuario:senha@host:5432/eventech" \
  eventech
```
Para SQLite em contêiner (só demonstração), monte um volume: `-v eventech-data:/data -e DATABASE_URL=sqlite:////data/eventech.db`.

## Checklist antes de publicar
- [ ] `.env` **não** está no Git (`git ls-files | grep -E '^\.env$'` não retorna nada)
- [ ] `JWT_SECRET_KEY` de produção diferente da de desenvolvimento
- [ ] `DATABASE_URL` aponta para PostgreSQL
- [ ] `CORS_ORIGINS` restrito às origens reais do front-end (ou vazio)
- [ ] `python -m pytest` verde
- [ ] Administrador criado por script, com senha forte

## Limitações conhecidas
- **Sem migrações (Alembic).** Bancos criados em versões anteriores (ex.: um `eventech.db` antigo) não recebem as novas restrições `UNIQUE` nem a coluna booleana; recrie o banco local (`rm eventech.db`) ou adote Alembic antes de evoluir o esquema em produção.
- Tokens não são revogáveis antes de expirar (30 min por padrão).
- Sem *rate limiting* no `/login`; em produção, considere um proxy/WAF na frente.
