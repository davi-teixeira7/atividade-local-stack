# Atividade 2 – DynamoDB (LocalStack)

```bash
docker compose up -d        # na raiz do repositório
cd atv2-dynamodb
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir http://localhost:8002 → criar conta → fazer login.

Para desligar: `Ctrl+C` e `docker compose down` (na raiz)
