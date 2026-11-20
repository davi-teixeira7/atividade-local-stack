# Atividade 1 – S3 (LocalStack)

```bash
cd atv1-amazons3
docker compose up -d
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir http://localhost:8001 → escolher uma imagem → Enviar → ver na lista e clicar em Download.

Para desligar: `Ctrl+C` e `docker compose down`
