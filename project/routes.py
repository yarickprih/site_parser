from datetime import datetime

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
    """Index application route.

    It includes 'sites' context variable which consists Site DB records.

    Returns:
        Template with given context
    """
    sites = Site.query.all()
    return render_template(
        "index.html",
        title="Home Page",
        sites=sites or None,
        user=current_user,
    )


@app.route("/<user_name>")
@login_required
def links_user_specific(user_name: str):
    """Sites filtered by current user.

    It includes 'sites' context variable which consists Site DB records filtered by current user.

    Args:
        user_name (str): current user username

    Returns:
        Template with given context
    """
    sites = Site.query.filter_by(user=current_user).all()
    return render_template(
        "links_list.html",
        title="Parsed Links",
        sites=sites or None,
        user=current_user,
    )


@app.route("/download")
@login_required
def download():
    """Download XML report route.

    Generates an XML report on list of parsed sites
    and creates an XML report file as an attachment.

    Returns:
        Redirect to 'index' route, XML report file.
    """
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
    sites = list(create_site_list(current_user))
    db.session.flush(Site.query.all())
    Site.query.filter_by(user=current_user).merge_result(sites, load=False)

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
            return render_template("login.html", title="Login Page", form=form)
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
