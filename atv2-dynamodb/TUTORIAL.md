# Atividade 2 – DynamoDB (LocalStack)

## 1. Subir e rodar

```bash
docker compose up -d
curl localhost:4566/_localstack/health

cd atv2-dynamodb
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

http://localhost:8002

## 2. Ver em tempo real

```bash
docker compose logs -f localstack
```

```bash
cd atv2-dynamodb && source .venv/bin/activate
python -c "
import boto3, time, os
t = boto3.resource('dynamodb', endpoint_url='http://localhost:4566', region_name='us-east-1',
                   aws_access_key_id='test', aws_secret_access_key='test').Table('usuarios')
while True:
    os.system('clear')
    for i in t.scan()['Items']:
        print(i['email'], '|', i['nome'], '|', i['senha'][:16] + '...')
    time.sleep(2)
"
```

## 3. Desligar

```bash
docker compose down
```
