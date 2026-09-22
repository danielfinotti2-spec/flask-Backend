from pathlib import Path
import sqlite3
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "database.db"
SITENAME = "My Flask"
app = Flask(__name__)
app.config["SECRET_KEY"] = "troque-esta-chave-em-producao"

@app.context_processor
def inject_globals():
    return {"sitename": SITENAME}

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript((BASE_DIR / "schema.sql").read_text(encoding="utf-8"))
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(fbuser)")}
        if "u_password_hash" not in columns:
            conn.execute("ALTER TABLE fbuser ADD COLUMN u_password_hash TEXT")
        if "u_is_admin" not in columns:
            conn.execute("ALTER TABLE fbuser ADD COLUMN u_is_admin INTEGER DEFAULT 0")

@app.route("/")
@app.route("/index.html")
def home():
    with get_db() as conn:
        contents = conn.execute("SELECT c_id, c_title, substr(c_text, 1, 50) || '...' AS c_resume FROM content WHERE c_status = 'on' ORDER BY c_created_at DESC").fetchall()
    return render_template("index.html", tag_title=SITENAME, contents=contents, total=len(contents))

@app.route("/about")
@app.route("/sobre.html")
def sobre():
    return render_template("sobre.html", tag_title=f"{SITENAME} - Sobre")

@app.route("/conta", methods=["GET", "POST"])
def conta():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Preencha nome, e-mail e uma senha com pelo menos 6 caracteres.", "error")
        else:
            try:
                with get_db() as conn:
                    is_first_admin = conn.execute("SELECT COUNT(*) FROM fbuser WHERE u_is_admin = 1").fetchone()[0] == 0
                    conn.execute("INSERT INTO fbuser (u_uid, u_email, u_name, u_password_hash, u_is_admin) VALUES (?, ?, ?, ?, ?)", (email, email, name, generate_password_hash(password), is_first_admin))
                flash("Conta criada. Agora faça login.", "success")
                return redirect(url_for("conta"))
            except sqlite3.IntegrityError:
                flash("Este e-mail já possui uma conta.", "error")
    return render_template("conta.html", tag_title=f"{SITENAME} - Conta")

@app.post("/entrar")
def entrar():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    with get_db() as conn:
        user = conn.execute("SELECT * FROM fbuser WHERE u_email = ?", (email,)).fetchone()
    if user and user["u_password_hash"] and check_password_hash(user["u_password_hash"], password):
        session["user_id"] = user["u_id"]
        session["user_name"] = user["u_name"]
        session["is_admin"] = bool(user["u_is_admin"])
        flash("Login realizado com sucesso.", "success")
    else:
        flash("E-mail ou senha inválidos.", "error")
    return redirect(url_for("conta"))

@app.post("/sair")
def sair():
    session.clear()
    return redirect(url_for("home"))

@app.route("/admin")
def admin():
    if not session.get("is_admin"):
        abort(403)
    with get_db() as conn:
        users = conn.execute("SELECT u_id, u_created_at, u_name, u_email FROM fbuser ORDER BY u_created_at DESC").fetchall()
        contacts = conn.execute("SELECT id, created_at, email, message, status FROM contact ORDER BY created_at DESC").fetchall()
    return render_template("admin.html", tag_title=f"{SITENAME} - Administração", users=users, contacts=contacts)

@app.route("/contacts", methods=["GET", "POST"])
@app.route("/faz-contato.html", methods=["GET", "POST"])
@app.route("/fazcontato.html", methods=["GET", "POST"])
def fazcontato():
    sent = False
    if request.method == "POST":
        with get_db() as conn:
            conn.execute("INSERT INTO contact (email, message) VALUES (?, ?)", (request.form.get("email", ""), request.form.get("mensagem", "")))
        sent = True
    return render_template("fazcontato.html", tag_title=f"{SITENAME} - Faça contato", sent=sent)

@app.route("/Contatos.html")
def contatos(): return redirect(url_for("fazcontato"))

@app.route("/Wiki.html")
def wiki(): return redirect(url_for("sobre"))

init_db()

if __name__ == "__main__":
    app.run(debug=True)
