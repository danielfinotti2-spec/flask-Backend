from flask import Flask, render_template

# Criação do objeto Flask e iniciando a aplicação
app = Flask(__name__)

# Flask Rota Pagina Inicial

@app.route("/Wiki.html")
def Wiki():
    return render_template("Wiki.html")

@app.route("/Contatos.html")
def contatos():
    return render_template("Contatos.html")

@app.route("/index.html")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
