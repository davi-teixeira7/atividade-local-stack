# Atividade 1 – S3 (LocalStack)

```bash
docker compose up -d
cd atv1-amazons3
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

http://localhost:8001/imagens (exige login pela atividade 2, em http://localhost:8002/login)

```bash
docker compose down
```
