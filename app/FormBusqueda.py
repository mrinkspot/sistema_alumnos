from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class FormBusqueda(FlaskForm):
    padron = IntegerField("Ingrese el padrón", validators=[DataRequired()])
    submit = SubmitField("Buscar")