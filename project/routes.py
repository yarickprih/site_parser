from flask import current_app as app
from flask import (
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from project import db

from .forms import LoginForm, RegistrationForm
from .models import Site, User
from .parser import create_site_list
from .utils import create_xml_report


@app.route("/")
@login_required
def index():
    user = current_user
    sites = Site.query.filter_by(user_id=user.id)
    return render_template(
        "index.html",
        title="Home Page",
        sites=sites if len(sites.all()) else None,
        user=user,
    )


@app.route("/download")
@login_required
def download():
    sites = Site.query.all()
    file_name = create_xml_report(sites)
    return send_from_directory(
        app.config["FILES_DIR"],
        file_name,
        as_attachment=True,
    )


@app.route("/parse")
@login_required
def parse_links():
    sites = create_site_list(current_user)
    for site in sites:
        try:
            db.session.add(site)
        except IntegrityError:
            continue
    db.session.commit()
    flash("Sites have been added successfully!", category="success")
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
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
            login_user(user)
            flash(
                f"User has been authenticated successfully!",
                category="success",
            )
            return redirect("/login?next=" + request.path)
        else:
            flash("Incorrect password!", category="danger")
    for field, error in form.errors.items():
        flash(f"{field.title()}: {error[0]}", category="danger")
    return render_template("login.html", title="Login Page", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        try:
            user = User(username=form.username.data, password=form.password.data)
            user.commit_to_db()
        except IntegrityError:
            flash(
                f"User with username '{user.username}' already registered!",
                category="danger",
            )
        else:
            flash("User has been created successfully!", category="success")
            return redirect(url_for("login"))
    for field, error in form.errors.items():
        flash(f"{field.title()}: {error[0]}", category="danger")
    return render_template("register.html", title="Registration Page", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash("You've been logged out successfully!", category="warning")
    return redirect(url_for("login"))
