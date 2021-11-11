from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length, DataRequired, Email
from wtforms.fields.html5 import EmailField


class RegisterForm(FlaskForm):
    """Form for registering a user."""

    email = EmailField("Email", validators=[InputRequired()])
    username = StringField("Username", validators=[InputRequired(), Length(min=5, max=15)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=5, max=15)])


class LoginForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class AddCrypto(FlaskForm):
    """Form for adding crypto to inventory."""
    type = StringField("Crypto Type:", validators=[InputRequired()], default="BTC")
    amount = FloatField("Amount:", validators=[InputRequired()])

    
class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL')
    password = PasswordField('Password', validators=[Length(min=6)])