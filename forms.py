from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4, max=20)])
    password_confirm = PasswordField("Confirm password", validators=[DataRequired(), Length(min=4, max=20)])
    submit = SubmitField("Sign up")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class ChangePasswordForm(FlaskForm):
    prev_password = PasswordField("Previous password", validators=[DataRequired(), Length(min=4, max=20)])
    new_password = PasswordField("New password", validators=[DataRequired(), Length(min=4, max=20)])
    password_confirm = PasswordField("Confirm password", validators=[DataRequired(), Length(min=4, max=20)])
    submit = SubmitField("Change")

class AdminForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")
