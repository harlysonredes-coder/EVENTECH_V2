# Como testar e entregar

1. **Preserve a pasta original**. Extraia esta versão em outra pasta.
2. Abra o terminal dentro da pasta extraída e instale `python -m pip install -r requirements.txt`.
3. Crie `.env` (não envie ao GitHub) com `JWT_SECRET_KEY=` seguido de uma chave nova gerada por `python -c "import secrets; print(secrets.token_hex(32))"`.
4. Execute `python -m pytest -v` e salve um print do resultado real. Os testes usam banco temporário e não alteram `eventech.db`.
5. Execute `python -m uvicorn main:app --reload` e acesse `http://127.0.0.1:8000/docs`.
6. Para criar um administrador **somente no banco local**, execute `python criar_admin_local.py` e siga as instruções.
7. Capture prints de 401 sem token, 403 com participante, 200/201 com administrador, e `pytest -v`.
8. Revise a matriz de permissões frente à Primeira Unidade e só então atualize o GitHub e o relatório.

**Atenção**: esta versão não inclui o banco de dados original, `.env` ou repositório `.git`. Não copie esses arquivos para GitHub. Exclusões podem depender de relações do banco e devem ser testadas com dados descartáveis.
