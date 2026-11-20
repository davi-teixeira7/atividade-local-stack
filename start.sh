#!/usr/bin/env bash
# Sobe tudo: LocalStack (DynamoDB, S3, Lambda, Logs), publica a Lambda e roda os dois apps.
# Uso: ./start.sh   |   Parar: Ctrl+C   |   Desligar o LocalStack: docker compose down
set -e
cd "$(dirname "$0")"
export PIP_DISABLE_PIP_VERSION_CHECK=1

command -v docker >/dev/null || { echo "Erro: Docker não encontrado."; exit 1; }
docker info >/dev/null 2>&1 || { echo "Erro: abra o Docker Desktop antes de rodar."; exit 1; }
command -v python3 >/dev/null || { echo "Erro: Python 3 não encontrado."; exit 1; }

echo "[1/4] Subindo o LocalStack..."
docker compose up -d --quiet-pull
until curl -s localhost:4566/_localstack/health | grep -qE '"lambda": "(available|running)"'; do sleep 1; done

echo "[2/4] Preparando o ambiente Python..."
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q -r atv1-amazons3/requirements.txt -r atv2-dynamodb/requirements.txt -r atv3-lambda/requirements.txt

echo "[3/4] Publicando a Lambda..."
.venv/bin/python atv3-lambda/deploy.py

echo "[4/4] Subindo os apps..."
trap 'echo; echo "Parando os apps..."; kill 0' EXIT   # Ctrl+C derruba os dois apps
(cd atv2-dynamodb && ../.venv/bin/python app.py) &
(cd atv1-amazons3 && ../.venv/bin/python app.py) &
until curl -s -o /dev/null localhost:8002/login && curl -s -o /dev/null localhost:8001; do sleep 1; done

echo
echo "Pronto!"
echo "  Login e cadastro: http://localhost:8002/login"
echo "  Imagens:          http://localhost:8001/imagens"
echo "  Logs da Lambda:   http://localhost:8001/logs"
echo "Ctrl+C para parar."
(open http://localhost:8002/login 2>/dev/null || xdg-open http://localhost:8002/login 2>/dev/null) || true
wait
