from flask import current_app as app
from flask import flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from .forms import LoginForm, RegistrationForm
from .models import Site, User


@app.route("/")
def index():
    user = User.query.get(2)
    sites = Site.query.filter_by(user_id=user.id)
    return render_template("test.html", title="Test Page", sites=sites, user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash(
                f"User with username '{form.username.data}' doesn't exists!",
                category="danger",
            )
            return render_template("login.html", title="Login Page", **request.form)
        if user.check_password(form.password.data):
            flash(
                f"User has been authenticated successfully!",
                category="success",
            )
        else:
            flash("Incorrect password!", category="danger")
        print(form.errors)
    for field, error in form.errors.items():
        flash(f"{field.title()}: {error[0]}", category="danger")
    return render_template("login.html", title="Login Page", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        try:
            user = User(username=form.username.data, password=form.password.data)
            user.session_add()
            user.session_commit()
        except IntegrityError:
            flash(
                f"User with username '{user.username}' already exists!",
                category="danger",
            )
        else:
            flash("User has been created successfully!", category="success")
            return redirect(url_for("login"))
    for field, error in form.errors.items():
        flash(f"{field.title()}: {error[0]}", category="danger")
    return render_template("register.html", title="Registration Page", form=form)
