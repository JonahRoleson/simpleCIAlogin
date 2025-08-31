from flask import Flask, request, session, jsonify, abort, render_template, redirect, url_for
from functools import wraps

app = Flask(__name__)
app.secret_key = "secret-not-for-production"

#List of users to access webpages
USERS = {
        "jonah": {"role": "admin"},
        "keeghan": {"role": "user"},
}

# function to get current users username from the active session
def current_user():
    username = session.get("username")
    if not username:
        return None
    return {"username": username, "role": session.get("role")}

# function to determine if the current user has the role associated with access to the page depending on the arguments given by the session and users role
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

# routes/pages to connect to

# This is the index or basic page that loads when no additional pages are requested
@app.get("/")
def index():
    return render_template("index.html", user=current_user())

# This is the login page and will authenticate based on the username argument supplied
@app.route("/login", methods=["GET", "POST"])
def login():
    username = request.form.get("username") if request.method == "POST" else request.args.get("username")
    username = (username or "").strip().lower()
    if username not in USERS:
        return redirect(url_for("index"))
    session["username"] = username
    session["role"] = USERS[username]["role"]
    return redirect(url_for("index"))

#This allows the user to clear the session and remove their credentials
@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# This is the admin only page and will require the active logged in user to have the admin role making it unavailable but confidential
@app.get("/admin-only")
@requires_role("admin")
def admin_only():
    return render_template("admin.html", user=current_user())

# This is the user only page and will require the active logged in user to have the user role making it also unavailable but confidential
@app.get("/user-only")
@requires_role("user")
def user_only():
     return render_template("user.html", user=current_user())

#This is the whoami page which allows the user to see if they are logged in and the current user information if they are
@app.get("/whoami")
def whoami():
    user = current_user()
    if not user:
        return jsonify({"authenticated": False}), 200
    return jsonify({"authenticated": True, "user": user}), 200

# This is the page to check to see if the connection is active and okay
@app.get("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
