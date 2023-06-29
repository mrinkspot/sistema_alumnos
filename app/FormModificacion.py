from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class FormModificacion(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired()])
    apellido = StringField("Apellido", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    submit = SubmitField("Modificar")