from flask import Flask, redirect, render_template, url_for

# Criação do objeto Flask e iniciando a aplicação
app = Flask(__name__)


# Página inicial
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/sobre.html")
def sobre():
    return render_template("sobre.html")


# Página Wiki
@app.route("/Wiki.html")
def wiki():
    return redirect(url_for("sobre"))


# Página Contatos
@app.route("/Contatos.html")
def contatos():
    return redirect(f"{url_for('home')}#contato")


# Página index.html
@app.route("/index.html")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)

