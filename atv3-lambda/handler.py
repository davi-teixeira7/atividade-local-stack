import io
import boto3
from PIL import Image, ImageOps

s3 = boto3.client("s3")  # dentro do LocalStack, AWS_ENDPOINT_URL ja vem configurado


def handler(event, context):
    for r in event["Records"]:
        bucket = r["s3"]["bucket"]["name"]
        nome = r["s3"]["object"]["key"]
        print(f"Recebido: {nome} (bucket {bucket})")

        original = s3.get_object(Bucket=bucket, Key=nome)["Body"].read()
        imagem = ImageOps.grayscale(Image.open(io.BytesIO(original)))

        saida = io.BytesIO()
        imagem.save(saida, format="PNG")
        s3.put_object(Bucket="processadas", Key=nome, Body=saida.getvalue(), ContentType="image/png")
        print(f"Processada: {nome} -> preto e branco salvo em processadas/{nome}")
