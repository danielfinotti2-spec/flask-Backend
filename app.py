from pathlib import Path
from collections import defaultdict, deque
import hmac
import os
import secrets
import sqlite3
import time
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "database.db"
SITENAME = "My Flask"
app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get("SECRET_KEY", secrets.token_hex(32)), SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=os.environ.get("FLASK_HTTPS") == "1")
LOGIN_ATTEMPTS = defaultdict(deque)

@app.context_processor
def inject_globals():
    return {"sitename": SITENAME, "csrf_token": session.setdefault("csrf_token", secrets.token_urlsafe(32))}

def valid_csrf():
    return hmac.compare_digest(request.form.get("csrf_token", ""), session.get("csrf_token", ""))

@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

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

@app.route("/")
@app.route("/index.html")
def home():
    with get_db() as conn:
        contents = conn.execute("SELECT c_id, c_title, substr(c_text, 1, 50) || '...' AS c_resume FROM content WHERE c_status = 'on' ORDER BY c_created_at DESC").fetchall()
    return render_template("index.html", tag_title=SITENAME, contents=contents, total=len(contents))

@app.route("/view/<int:content_id>")
def view(content_id):
    with get_db() as conn:
        content = conn.execute(
            """
            SELECT c_id, c_created_at, c_title, c_text, u_id, u_name, u_photo
            FROM content
            INNER JOIN fbuser ON c_owner = u_id
            WHERE c_status = 'on' AND c_id = ?
            """,
            (content_id,),
        ).fetchone()
    if content is None:
        abort(404)
    return render_template("view.html", tag_title=content["c_title"], content=content)

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
        if not name or len(name) > 100 or "@" not in email or len(email) > 254 or len(password) < 12:
            flash("Use nome e e-mail válidos e senha com pelo menos 12 caracteres.", "error")
        else:
            try:
                with get_db() as conn:
                    conn.execute("INSERT INTO fbuser (u_uid, u_email, u_name, u_password_hash) VALUES (?, ?, ?, ?)", (email, email, name, generate_password_hash(password)))
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
        flash("Login realizado com sucesso.", "success")
    else:
        flash("E-mail ou senha inválidos.", "error")
    return redirect(url_for("conta"))

@app.post("/sair")
def sair():
    session.clear()
    return redirect(url_for("home"))

@app.route("/contacts", methods=["GET", "POST"])
@app.route("/faz-contato.html", methods=["GET", "POST"])
@app.route("/fazcontato.html", methods=["GET", "POST"])
def fazcontato():
    sent = False
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        message = request.form.get("mensagem", "").strip()
        if "@" not in email or len(email) > 254 or not message or len(message) > 5000:
            flash("Informe e-mail e mensagem válidos.", "error")
            return redirect(url_for("fazcontato"))
        with get_db() as conn:
            conn.execute("INSERT INTO contact (email, message) VALUES (?, ?)", (email, message))
        sent = True
    return render_template("fazcontato.html", tag_title=f"{SITENAME} - Faça contato", sent=sent)

@app.route("/Contatos.html")
def contatos(): return redirect(url_for("fazcontato"))

@app.route("/Wiki.html")
def wiki(): return redirect(url_for("sobre"))

init_db()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
