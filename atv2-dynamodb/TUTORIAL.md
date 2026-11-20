# Atividade 2 – DynamoDB (LocalStack)

```bash
cd atv2-dynamodb
docker compose up -d
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir http://localhost:8002 → criar conta → fazer login.

Para desligar: `Ctrl+C` e `docker compose down`
