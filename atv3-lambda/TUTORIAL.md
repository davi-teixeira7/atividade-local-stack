# Atividade 3 – Lambda (LocalStack)

```bash
docker compose up -d
python3 -m venv .venv
source .venv/bin/activate
pip install -r atv3-lambda/requirements.txt
python atv3-lambda/deploy.py
```

Logs: http://localhost:8001/logs

```bash
docker compose down
```
