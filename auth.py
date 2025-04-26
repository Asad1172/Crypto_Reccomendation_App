from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import register_user, authenticate_user

auth_bp = Blueprint("auth", __name__)

# --- User Registration Route ---
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if register_user(username, email, password):
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("Username or email already exists.", "danger")

    return render_template("register.html")

# --- User Login Route ---
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = authenticate_user(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials. Please try again.", "danger")

    return render_template("login.html")

# --- User Logout Route ---
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))
