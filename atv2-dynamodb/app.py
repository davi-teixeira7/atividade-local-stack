import hashlib
import boto3
from flask import Flask, redirect, render_template, request, session

db = boto3.resource("dynamodb", endpoint_url="http://localhost:4566", region_name="us-east-1",
                    aws_access_key_id="test", aws_secret_access_key="test")
try:
    db.create_table(TableName="usuarios",
                    KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
                    AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
                    BillingMode="PAY_PER_REQUEST")
except db.meta.client.exceptions.ResourceInUseException:
    pass  # tabela ja existe
tabela = db.Table("usuarios")

def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

app = Flask(__name__, template_folder="..")  # usa o index.html da raiz do repositorio
app.secret_key = "localstack-demo"            # mesma chave da atividade 1: compartilha o login

@app.route("/")
def inicio():
    return redirect("/login")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "GET":
        return render_template("index.html", pagina="cadastro")
    email, senha = request.form["email"], request.form["senha"]
    tabela.put_item(Item={"email": email, "nome": request.form["nome"], "senha": hash_senha(senha)})
    return redirect(f"/login?criado={email}")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        criado = request.args.get("criado")
        return render_template("index.html", pagina="login",
                               msg=f"Conta criada para {criado}. Faça login." if criado else "")
    item = tabela.get_item(Key={"email": request.form["email"]}).get("Item")
    if item and item["senha"] == hash_senha(request.form["senha"]):
        session["usuario"] = item["nome"]
        return redirect("http://localhost:8001/imagens")  # pagina de imagens (atividade 1)
    return render_template("index.html", pagina="login", erro="Email ou senha inválidos")

app.run(port=8002, debug=True)
