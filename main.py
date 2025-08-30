from flask import Flask, request, session, jsonify, abort, render_template, redirect, url_for
from functools import wraps

app = Flask(__name__)
app.secret_key = "secret-not-for-production"

USERS = {
        "jonah": {"role": "admin"},
        "keeghan": {"role": "user"},
}

def current_user():
    username = session.get("username")
    if not username:
        return None
    return {"username": username, "role": session.get("role")}

def requires_role(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = current_user()
            if user is None:
                return redirect(url_for("index"))
            if user["role"] != required_role:
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# Routes

@app.get("/")
def index():
    return render_template("index.html", user=current_user())

@app.route("/login", methods=["GET", "POST"])
def login():
    username = request.form.get("username") if request.method == "POST" else request.args.get("username")
    username = (username or "").strip().lower()
    if username not in USERS:
        return redirect(url_for("index"))
    session["username"] = username
    session["role"] = USERS[username]["role"]
    return redirect(url_for("index"))

@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.get("/admin-only")
@requires_role("admin")
def admin_only():
    return render_template("admin.html", user=current_user())

@app.get("/user-only")
@requires_role("user")
def user_only():
     return render_template("user.html", user=current_user())

@app.get("/whoami")
def whoami():
    user = current_user()
    if not user:
        return jsonify({"authenticated": False}), 200
    return jsonify({"authenticated": True, "user": user}), 200

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
