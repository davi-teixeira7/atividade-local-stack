import hashlib
import boto3
from flask import Flask, render_template, request

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

app = Flask(__name__, template_folder=".")

@app.route("/")
def index():
    return render_template("index.html", msg="")

@app.route("/cadastro", methods=["POST"])
def cadastro():
    email, senha = request.form["email"], request.form["senha"]
    tabela.put_item(Item={"email": email, "nome": request.form["nome"], "senha": hash_senha(senha)})
    return render_template("index.html", msg=f"Conta criada para {email}")

@app.route("/login", methods=["POST"])
def login():
    item = tabela.get_item(Key={"email": request.form["email"]}).get("Item")
    if item and item["senha"] == hash_senha(request.form["senha"]):
        msg = f"Bem-vindo, {item['nome']}!"
    else:
        msg = "Email ou senha invalidos"
    return render_template("index.html", msg=msg)

app.run(port=8002, debug=True)
