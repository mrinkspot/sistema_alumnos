from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, Length

class FormLogin(FlaskForm):
 email = EmailField('Email', validators=[DataRequired(), Length(1, 64)])
 username = StringField('Nombre de Usuario', validators=[DataRequired()])
 password = PasswordField('Contraseña', validators=[DataRequired()])
 remember_me = BooleanField('Mantener sesión iniciada')
 submit = SubmitField('Ingresar')