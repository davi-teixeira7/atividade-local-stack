import boto3
from flask import Flask, Response, redirect, render_template, request
from werkzeug.utils import secure_filename

BUCKET = "imagens"

s3 = boto3.client("s3", endpoint_url="http://localhost:4566", region_name="us-east-1",
                  aws_access_key_id="test", aws_secret_access_key="test")
try:
    s3.create_bucket(Bucket=BUCKET)
except s3.exceptions.BucketAlreadyOwnedByYou:
    pass  # bucket ja existe

app = Flask(__name__, template_folder=".")

@app.route("/")
def index():
    objetos = s3.list_objects_v2(Bucket=BUCKET).get("Contents", [])
    return render_template("index.html", arquivos=objetos, msg=request.args.get("msg", ""))

@app.route("/upload", methods=["POST"])
def upload():
    arquivo = request.files["arquivo"]
    if not arquivo.mimetype.startswith("image/"):
        return redirect("/?msg=Envie apenas imagens")
    nome = secure_filename(arquivo.filename)
    s3.upload_fileobj(arquivo, BUCKET, nome, ExtraArgs={"ContentType": arquivo.mimetype})
    return redirect(f"/?msg={nome} enviado")

@app.route("/arquivo/<nome>")
def arquivo(nome):
    obj = s3.get_object(Bucket=BUCKET, Key=nome)
    headers = {}
    if "download" in request.args:
        headers["Content-Disposition"] = f'attachment; filename="{nome}"'
    return Response(obj["Body"].read(), mimetype=obj["ContentType"], headers=headers)

app.run(port=8001, debug=True)
