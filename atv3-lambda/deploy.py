"""Empacota a Lambda (com Pillow), cria a funcao e liga o gatilho do bucket 'imagens'."""
import os, platform, shutil, subprocess, sys
import boto3

os.chdir(os.path.dirname(os.path.abspath(__file__)))
cfg = dict(endpoint_url="http://localhost:4566", region_name="us-east-1",
           aws_access_key_id="test", aws_secret_access_key="test")
s3, lam = boto3.client("s3", **cfg), boto3.client("lambda", **cfg)
NOME = "processa-imagem"

# 1. buckets: imagens (originais, da atividade 1) e processadas (resultado da Lambda)
for b in ("imagens", "processadas"):
    try:
        s3.create_bucket(Bucket=b)
    except s3.exceptions.BucketAlreadyOwnedByYou:
        pass

# 2. pacote zip: handler.py + Pillow compilado para Linux na arquitetura da maquina
arm = platform.machine() in ("arm64", "aarch64")
shutil.rmtree("build", ignore_errors=True)
subprocess.run([sys.executable, "-m", "pip", "install", "pillow", "-t", "build", "-q",
                "--platform", "manylinux2014_aarch64" if arm else "manylinux2014_x86_64",
                "--only-binary=:all:", "--python-version", "3.12"], check=True)
shutil.copy("handler.py", "build/")
shutil.make_archive("funcao", "zip", "build")

# 3. cria (ou recria) a funcao
try:
    lam.delete_function(FunctionName=NOME)
except lam.exceptions.ResourceNotFoundException:
    pass
lam.create_function(FunctionName=NOME, Runtime="python3.12", Handler="handler.handler",
                    Role="arn:aws:iam::000000000000:role/lambda", Timeout=30,
                    Architectures=["arm64" if arm else "x86_64"],
                    Code={"ZipFile": open("funcao.zip", "rb").read()})
lam.get_waiter("function_active_v2").wait(FunctionName=NOME)

# 4. gatilho: todo upload no bucket "imagens" chama a Lambda
arn = lam.get_function(FunctionName=NOME)["Configuration"]["FunctionArn"]
s3.put_bucket_notification_configuration(Bucket="imagens", NotificationConfiguration={
    "LambdaFunctionConfigurations": [{"LambdaFunctionArn": arn, "Events": ["s3:ObjectCreated:*"]}]})
print("Lambda pronta: uploads em 'imagens' viram preto e branco em 'processadas'")
