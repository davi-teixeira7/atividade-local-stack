import hashlib
import boto3
from flask import Flask, redirect, render_template, request

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
        # depois: trocar por redirect para a pagina de upload (atividade 1)
        return redirect(f"/bem-vindo?nome={item['nome']}")
    return render_template("index.html", pagina="login", erro="Email ou senha inválidos")

@app.route("/bem-vindo")
def bem_vindo():
    return render_template("index.html", pagina="logado", nome=request.args.get("nome", ""))

app.run(port=8002, debug=True)
