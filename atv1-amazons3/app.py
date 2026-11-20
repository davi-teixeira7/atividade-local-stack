import boto3
from flask import Flask, Response, redirect, render_template, request, session
from werkzeug.utils import secure_filename

BUCKET = "imagens"            # originais enviados pelo usuario
PROCESSADAS = "processadas"   # resultado da Lambda (atividade 3)
LOGIN = "http://localhost:8002/login"

cfg = dict(endpoint_url="http://localhost:4566", region_name="us-east-1",
           aws_access_key_id="test", aws_secret_access_key="test")
s3 = boto3.client("s3", **cfg)
logs = boto3.client("logs", **cfg)
for b in (BUCKET, PROCESSADAS):
    try:
        s3.create_bucket(Bucket=b)
    except s3.exceptions.BucketAlreadyOwnedByYou:
        pass  # bucket ja existe

app = Flask(__name__, template_folder="..")  # usa o index.html da raiz do repositorio
app.secret_key = "localstack-demo"            # mesma chave da atividade 2: compartilha o login


@app.before_request
def exige_login():
    if "usuario" not in session:
        return redirect(LOGIN)


@app.route("/")
def inicio():
    return redirect("/imagens")


@app.route("/imagens")
def imagens():
    objetos = s3.list_objects_v2(Bucket=BUCKET).get("Contents", [])
    prontas = {o["Key"] for o in s3.list_objects_v2(Bucket=PROCESSADAS).get("Contents", [])}
    return render_template("index.html", pagina="imagens", usuario=session["usuario"],
                           arquivos=objetos, prontas=prontas, msg=request.args.get("msg", ""))


@app.route("/upload", methods=["POST"])
def upload():
    arquivo = request.files["arquivo"]
    if not arquivo.mimetype.startswith("image/"):
        return redirect("/imagens?msg=Envie apenas imagens")
    nome = secure_filename(arquivo.filename)
    s3.upload_fileobj(arquivo, BUCKET, nome, ExtraArgs={"ContentType": arquivo.mimetype})
    return redirect(f"/imagens?msg={nome} enviado")


@app.route("/arquivo/<bucket>/<nome>")
def arquivo(bucket, nome):
    obj = s3.get_object(Bucket=bucket, Key=nome)
    headers = {}
    if "download" in request.args:
        headers["Content-Disposition"] = f'attachment; filename="{nome}"'
    return Response(obj["Body"].read(), mimetype=obj["ContentType"], headers=headers)


@app.route("/logs")
def ver_logs():
    try:
        eventos = logs.filter_log_events(logGroupName="/aws/lambda/processa-imagem")["events"]
    except logs.exceptions.ResourceNotFoundException:
        eventos = []  # a Lambda ainda nao rodou nenhuma vez
    return render_template("index.html", pagina="logs", usuario=session["usuario"],
                           eventos=list(reversed(eventos[-100:])))


@app.route("/sair")
def sair():
    session.clear()
    return redirect(LOGIN)


app.run(port=8001, debug=True)
