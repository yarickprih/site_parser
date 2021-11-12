from werkzeug.utils import validate_arguments
from wtforms import Form, PasswordField, StringField, validators


class RegistrationForm(Form):
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
        "Repeat Password",
        [
            validators.DataRequired(),
            validators.InputRequired(),
        ],
    )


class LoginForm(Form):
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
