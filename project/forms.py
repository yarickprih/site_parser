from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import PasswordField, StringField, validators


class RegistrationForm(FlaskForm):
    """WTForms User registration form."""

    username = StringField(
        "Username",
        [
            validators.Length(min=4, max=25),
            validators.DataRequired(),
            validators.InputRequired(),
        ],
    )
    password = PasswordField(
        "New Password",
        [
            validators.DataRequired(),
            validators.InputRequired(),
            validators.EqualTo("confirm", message="Passwords must match"),
            validators.Length(min=8),
        ],
    )
    confirm = PasswordField(
        "Confirm Password",
        [
            validators.DataRequired(),
            validators.InputRequired(),
        ],
    )


class LoginForm(FlaskForm):
    """WTForms User login form."""

    username = StringField(
        "Username",
        [
            validators.Length(min=4, max=25),
            validators.DataRequired(),
            validators.InputRequired(),
        ],
    )
    password = PasswordField(
        "Password",
        [
            validators.DataRequired(),
            validators.InputRequired(),
        ],
    )


class FileUploadForm(FlaskForm):
    """WTForms File upload form."""
    document = FileField(
        "Document",
        validators=[
            FileRequired(),
            FileAllowed(["txt"], "TXT files only!"),
        ],
    )
