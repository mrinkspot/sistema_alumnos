from flask_wtf import FlaskForm
from wtforms import * 
from wtforms.validators import * 

class NombreForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()], render_kw={ 'placeholder': 'Ingresá tu nombre', 'style':"color:red"})
    submit = SubmitField("Enviar", render_kw={'style':'background-color:lightgray'})