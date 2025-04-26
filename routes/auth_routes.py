from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from models.user import User
from extensions import db
from services.auth_service import hash_password, check_password

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and check_password(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("main_routes.index"))  # Redirect to dashboard
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = hash_password(password)  # Ensure password hashing

        if User.query.filter_by(email=email).first():
            flash("Email already exists. Please login.", "warning")
            return redirect(url_for("auth_bp.login"))

        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth_bp.login"))  #  Redirect to login

    return render_template("register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for("auth_bp.login"))
