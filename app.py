from flask import Flask, render_template

# Criação do objeto Flask e iniciando a aplicação
app = Flask(__name__)


# Página inicial
@app.route("/")
def home():
    return render_template("index.html")


# Página Wiki
@app.route("/Wiki.html")
def wiki():
    return render_template("Wiki.html")


# Página Contatos
@app.route("/Contatos.html")
def contatos():
    return render_template("Contatos.html")


# Página index.html
@app.route("/index.html")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)

