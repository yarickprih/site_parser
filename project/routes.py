from flask import current_app as app
from flask import (
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required, login_user
from werkzeug.utils import secure_filename

from .forms import FileUploadForm, LoginForm, RegistrationForm
from .models import Site, User
from .parser import commit_parsed
from .utils import (
    create_xml_report,
    flash_form_errors,
    get_user_uploads_folder,
    user_authenticated,
)


@app.route("/")
@login_required
def index():
    """Index application route.

    It includes 'sites' context variable which consists Site DB records.

    Returns:
        Template with given context
    """
    sites = Site.query.all()
    return (
        render_template(
            "index.html",
            title="Home Page",
            sites=sites or None,
            user=current_user,
        ),
        200,
    )


@app.route("/<user_name>")
@login_required
def links_user_specific(user_name: str):
    """Sites filtered by current user.

    It includes 'sites' context variable which consists Site DB
    records filtered by current user.

    Args:
        user_name (str): current user username

    Returns:
        Template with given context
    """
    sites = Site.query.filter_by(user=current_user).all()
    return (
        render_template(
            "links_list.html",
            title="Parsed Links",
            sites=sites or None,
            user=current_user,
        ),
        200,
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
    try:
        report = create_xml_report(sites)
    except ValueError as e:
        app.logger.error({"error": str(e)})
        flash(str(e), category="danger")
        return redirect(request.path), 404
    print(request.path)
    return (
        send_from_directory(
            app.config["FILES_DIR"],
            report,
            as_attachment=True,
        ),
        200,
    )


@app.route("/files")
@login_required
def list_user_files():
    """List of files uploaded by the user route."""
    files = list(get_user_uploads_folder(current_user).glob("*.txt"))
    return render_template("files.html", files=files), 200


@app.route("/upload", methods=["GET"])
@login_required
def upload_file_view():
    """Route for uploading txt files with site urls.

    Files uploaded with this route would be saved to the folder
    assigned to UPLOADS config variable truncating a folder for
    specific user."""
    form = FileUploadForm()
    return render_template("upload_file.html", title="Upload File", form=form)


@app.route("/upload", methods=["POST"])
@login_required
def upload_file():
    form = FileUploadForm()
    if form.validate_on_submit():

        file = form.document.data
        file_name = secure_filename(file.filename)
        save_path = get_user_uploads_folder(current_user) / file_name

        if save_path.exists():
            flash(
                f"File with name {file_name} already exists",
                category="danger",
            )
            return redirect(url_for("upload_file"))

        file.save(save_path)
        flash("File uploaded successfully", category="success")
        return redirect(url_for("list_user_files"))

    flash_form_errors(form)
    return redirect(url_for("upload_file_view"))


@app.route("/delete/<file_name>")
@login_required
def delete_file(file_name):
    file_path = get_user_uploads_folder(current_user) / file_name
    try:
        file_path.unlink()
    except OSError as e:
        app.logger.error({"error": e.strerror})
        flash(f"Error! {e.strerror}: {file_name}", category="danger")
    else:
        flash("File has been deleted successfully", category="success")
    return redirect(url_for("list_user_files"))


@app.route("/parse/<file_name>")
@login_required
def parse_links(file_name: str):
    """Parse sites from the file and create corresponding
    records to the database.

    Args:
        file_name (str): name of the file containing links to parse

    This route takes a file name as a parameter and searches for that
    file in the current user uploads folder.
    After the file is being processed, created file instances
    are committed to the database.
    """
    file_path = get_user_uploads_folder(current_user) / file_name
    if not file_path.exists():
        flash(
            f"File {file_name} doesn't exist. You have to upload it first",
            category="danger",
        )
        return redirect(url_for("upload_file"))
    commit_parsed(current_user, file_path)
    flash("Sites have been added successfully!", category="success")
    return redirect(url_for("index"))


@app.route("/login", methods=["GET"])
@user_authenticated
def login_view():
    """Flask-Login User login route."""

    form = LoginForm()
    return render_template("login.html", title="Login Page", form=form)


@app.route("/login", methods=["POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash(
                f"User with username '{form.username.data}' doesn't exists!",
                category="danger",
            )
            return redirect(url_for("login_view"))
        if not user.check_password(form.password.data):
            flash("Incorrect password!", category="danger")
        else:
            login_user(user)
            flash(
                "User has been authenticated successfully!",
                category="success",
            )
            return redirect("/login?next=" + request.path)
    flash_form_errors(form)
    return redirect(url_for("login_view"))


@app.route("/register", methods=["GET"])
def register_view():
    """User registration route."""
    form = RegistrationForm()

    return render_template(
        "register.html",
        title="Registration Page",
        form=form,
    )


@app.route("/register", methods=["POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            User.create(
                username=form.username.data,
                password=form.password.data,
            )
        except Exception as e:
            app.logger.error(str(e))
        else:
            flash("User has been created successfully!", category="success")
            return redirect(url_for("login"))
    flash_form_errors(form)
    return redirect(url_for("register_view"))


@app.route("/logout")
def logout():
    """User logout route.

    Before logout updates current user last_login field
    with logout datetime.utcnow.
    """
    User.logout(current_user.username)
    flash("You've been logged out successfully!", category="warning")
    return redirect(url_for("login"))
