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
from werkzeug.utils import secure_filename

from project import db

from .forms import FileUploadForm, LoginForm, RegistrationForm
from .models import Site, User
from .parser import create_site_list
from .utils import create_xml_report, get_user_uploads_folder


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


@app.route("/files")
@login_required
def list_user_files():
    """List of files uploaded by the user route."""
    files = list(get_user_uploads_folder(current_user).glob("*.txt"))
    return render_template("files.html", files=files)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    """Route for uploading txt files with site urls.

    Files uploaded with this route would be saved to the folder
    assigned to UPLOADS config variable truncating a folder for specific user."""
    form = FileUploadForm()

    if form.validate_on_submit():
        file = form.document.data
        file_name = secure_filename(file.filename)
        save_path = get_user_uploads_folder(current_user) / file_name

        if save_path.exists():
            flash(f"File with name {file_name} already exists", category="danger")
            return render_template("upload_file.html", form=form)

        file.save(save_path)
        flash("File uploaded successfully", category="success")
        return redirect(url_for("list_user_files"))

    for field, error in form.errors.items():
        flash(f"{field.title()}: {error[0]}", category="danger")
    return render_template("upload_file.html", form=form)


@app.route("/parse/<file_name>")
@login_required
def parse_links(file_name: str):
    """Parse sites from the file and create corresponding records to the database.

    This route takes a file name as a parameter and searches for that
    file in the current user uploads folder.
    After the file is being processed, created file instances
    are commited to the database."""
    file_path = get_user_uploads_folder(current_user) / file_name
    if not file_path.exists():
        flash(
            f"File {file_name} doesn't exist. You have to upload it first",
            category="danger",
        )
        return redirect(url_for("upload_file"))

    with db.session.no_autoflush:
        for site in create_site_list(current_user, file_path):
            site_to_update = Site.query.filter_by(url=site["url"])
            if site_to_update.first():
                site_to_update.update(
                    dict(
                        user_id=site["user"].id,
                        scrapping_time=site["scrapping_time"],
                        created_at=site["created_at"],
                    )
                )
            else:
                site_to_create = Site(**site)
                db.session.add(site_to_create)
        db.session.commit()
    flash("Sites have been added successfully!", category="success")
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Flask-Login User login route."""
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
        if not user.check_password(form.password.data):
            flash("Incorrect password!", category="danger")
        else:
            login_user(user)
            flash(
                "User has been authenticated successfully!",
                category="success",
            )
            return redirect("/login?next=" + request.path)
    for field, error in form.errors.items():
        flash(f"{field.title()}: {error[0]}", category="danger")
    return render_template("login.html", title="Login Page", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration route."""
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
    """User logout route.

    Before logout updates current user last_login field with logout datetime.utcnow.
    """
    user = User.query.filter_by(username=current_user.username).first()
    user.last_login = datetime.utcnow()
    user.commit_to_db()
    logout_user()
    flash("You've been logged out successfully!", category="warning")
    return redirect(url_for("login"))
