from flask import Flask, flash, redirect, request, url_for, jsonify # Importamos Flask
from flask import render_template
from flask import g
from flask import abort
from flask import session
from sqlalchemy.exc import IntegrityError


from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash

from NombreForm import NombreForm
from FormBusqueda import FormBusqueda
from FormAlta import FormAlta
from FormLogin import FormLogin
from FormRegistro import FormRegistro

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import *

from FormModificacion import FormModificacion

app = Flask(__name__) # Creamos una instancia de Flask, es decir, inicializando la app
bootstrap = Bootstrap(app)

login_manager = LoginManager() # Para asociar la funcionalidad de autenticación y gestión de usuarios con la app Flask (inicio de sesión, cierre de sesión, gestión de sesiones, protección de rutas...)
login_manager.init_app(app)


# Configuraciones
app.config['SECRET_KEY'] = 'patatasconquesodepapas'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///primer_proyecto_flask.db'

# Instancia de nuestra base de datos
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modelos
class Alumno(db.Model):
    __tablename__ = "Alumnos"
    padron = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), nullable=False)
    apellido = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)

class Materia(db.Model):
    __tablename__ = "Materias"
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(50), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'descripcion': self.descripcion
        }

class Cursada(db.Model): # tabla de relacion materia-alumno
    __tablename__ = "Cursadas"
    id = db.Column(db.Integer, primary_key=True)
    alumno_padron = db.Column(db.Integer, db.ForeignKey('Alumnos.padron'), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey('Materias.id'), nullable=False)
    nota = db.Column(db.Float)
    
    # Relaciones
    alumno = db.relationship('Alumno', backref='cursadas')
    materia = db.relationship('Materia', backref='cursadas')

# ==== LOGIN CLASSES ====
class Usuario(UserMixin, db.Model): # User Model
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    nombre_usuario = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


# # Definimos que, en contexto de la aplicación, se creen todas las tablas que no hayan sido creadas
# with app.app_context():
#     # db.drop_all()
#     db.create_all()

# Exclusivo para rol Alumno
@app.route('/inscripcion', methods=['GET'])
def mostrar_inscripcion():
    return render_template('inscripcion.html')


@app.route('/notas', methods=['GET'])
def mostrar_notas():
    return render_template('notas.html')

@app.route('/alumno/<int:alumno_padron>/materias', methods=['GET'])
def obtener_materias_inscriptas(alumno_padron):
    alumno = Alumno.query.get_or_404(alumno_padron)

    cursadas = Cursada.query.filter_by(alumno=alumno).all()
    materias = [cursada.materia for cursada in cursadas]

    return jsonify({'materias': [materia.serialize() for materia in materias]})

@app.route('/get_materias', methods=['GET'])
def obtener_materias():
    materias = Materia.query.all()
    materias_serializadas = [materia.serialize() for materia in materias]
    return jsonify(materias=materias_serializadas)

@app.route('/materias', methods=['GET'])
def ver_materias():
    return render_template('materias.html')

@app.route("/nombre", methods=['GET', 'POST'])
def nombre():
    form = NombreForm()
    if form.validate_on_submit():
        session['username'] = form.nombre.data
        form.nombre.data = ''
        return redirect(url_for('nombre'))
    try:
        return render_template("nombre.html", form=form, nombre=session['username'])
    except:
        return render_template("nombre.html", form=form, nombre=None)


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template("index.html")

@app.route('/nuevo', methods=['GET', 'POST'])
def nuevo_alumno():
    alta = FormAlta()
    if request.method == 'POST':
        if alta.validate_on_submit():
            nuevo_alumno = Alumno(nombre=alta.nombre.data, apellido=alta.apellido.data, email=alta.email.data)
            db.session.add(nuevo_alumno)
            db.session.commit()
            flash(f"Alumno {nuevo_alumno.padron} creado exitosamente")
            return redirect(url_for('mostrar_alumno', padron=nuevo_alumno.padron))
        else:
            flash("Los datos enviados no son válidos. Revisar el formulario.")
    return render_template("nuevo.html", form=alta)

@app.route('/busqueda', methods=['GET', 'POST'])
def buscar_alumno():
    busqueda = FormBusqueda()
    if request.method == 'POST':
        if busqueda.padron.data:
            return redirect(url_for('mostrar_alumno', padron=busqueda.padron.data))
        else:
            flash("Se debe ingresar un padrón")
    return render_template("busqueda.html", form=busqueda)

@app.route('/modificar/<int:padron>', methods=['GET', 'POST'])
def modificar(padron):
    modificar = FormModificacion()

    alumno_modificar = Alumno.query.get_or_404(padron)

    if request.method == 'POST':
        if modificar.validate_on_submit():

            alumno_modificar.nombre = modificar.nombre.data
            alumno_modificar.apellido = modificar.apellido.data
            alumno_modificar.email = modificar.email.data
            
            db.session.add(alumno_modificar)
            db.session.commit()

            flash(f"Alumno {alumno_modificar.padron} modificado exitosamente.")
            return redirect(url_for('mostrar_alumno', padron=alumno_modificar.padron))
        else:
            flash("Los datos enviados no son válidos. Revisar el formulario.")
    
    modificar.nombre.data = alumno_modificar.nombre
    modificar.email.data = alumno_modificar.email
    modificar.apellido.data = alumno_modificar.apellido

    return render_template("modificar.html", form=modificar, alumno_modificar=alumno_modificar)

# @app.route('/eliminar/<padron>')
# def eliminar(padron):
#     alumno = Alumno.query.get_or_404(padron)
#     db.session.delete(alumno)
#     db.session.commit()
#     flash(f"Alumno {padron} eliminado exitosamente")
#     return redirect(url_for('mostrar_listado_alumnos'))
    

@app.route('/eliminar/<int:padron>', methods=['DELETE'])
def eliminar(padron):
    if request.method == 'DELETE':
        # Verificar si el alumno existe
        alumno = Alumno.query.get_or_404(padron)

        # Realizar la eliminación del alumno
        db.session.delete(alumno)
        db.session.commit()

        # Retornar una respuesta JSON indicando éxito
        return jsonify({'message': f'Alumno {padron} eliminado exitosamente'}), 200
    else:
        # La solicitud no es de tipo DELETE, retornar un error
        return jsonify({'error': 'Método no permitido'}), 405


@app.route('/alumnos')
def mostrar_listado_alumnos():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    alumnos = Alumno.query.all() # SELECT * FROM Alumnos
    return render_template('alumnos.html', lista_alumnos=alumnos)

@app.route('/alumno/<int:padron>')
def mostrar_alumno(padron):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    # Buscamos el alumno por padrón, devolvemos None si el mismo no se encuentra
    
    alumno_buscado = Alumno.query.get(padron)

    if not alumno_buscado:
        return abort(404)
    return render_template("alumno.html", alumno_buscado=alumno_buscado)

@app.route('/inscribir_api', methods=['POST'])
def inscribir_api():
    data = request.json
    alumno_padron = data.get('alumno_padron')
    materia_id = data.get('materia_id')

    if not alumno_padron:
        return jsonify({'error': 'Alumno no encontrado.'}), 400
    
    if not materia_id:
        return jsonify({'error': 'Materia no encontrada.'}), 400

    alumno = Alumno.query.get_or_404(alumno_padron)
    materia = Materia.query.get_or_404(materia_id)

    cursada_existente = Cursada.query.filter_by(alumno=alumno, materia=materia).first()
    if cursada_existente:
        return jsonify({'message': 'El alumno ya está inscrito en esta materia.'}), 200

    cursada = Cursada(alumno=alumno, materia=materia)
    db.session.add(cursada)
    db.session.commit()

    return jsonify({'message': 'Inscripción exitosa.'}), 200


@app.route('/cargar_notas_api', methods=['POST'])
def cargar_notas_api():
    data = request.json
    alumno_padron = data.get('alumno_padron')
    materia_id = data.get('materia_id')
    nota = data.get('nota')

    if not alumno_padron:
        return jsonify({'error': 'Alumno no encontrado.'}), 400
    
    if not materia_id:
        return jsonify({'error': 'Materia no encontrada.'}), 400
        
    if nota is None:
        return jsonify({'error': 'Se debe especificar una nota.'}), 400

    alumno = Alumno.query.get_or_404(alumno_padron)
    materia = Materia.query.get_or_404(materia_id)

    cursada = Cursada.query.filter_by(alumno=alumno, materia=materia).first()
    if not cursada:
        return jsonify({'error': 'El alumno no está inscrito en esta materia.'}), 404

    cursada.nota = nota
    db.session.commit()

    return jsonify({'message': 'Nota cargada exitosamente.'}), 200

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# ==== LOGIN / REGISTRO VIEW FUNCTIONS ====
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Verificar si el usuario ya está autenticado
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for('index'))

    form = FormLogin()

    if request.method == "POST":
        if form.validate_on_submit():
            user = Usuario.query.filter_by(email=form.email.data).first()
            if user is not None and user.verify_password(form.password.data):
                login_user(user, form.remember_me.data) # de Flask-Login. Establece la sesión del usuario para rastrear y gestionar la identidad del mismo.
                return redirect(url_for('index'))
        flash('Error al iniciar sesión')

    return render_template('login.html', form=form)

@app.route('/registro', methods=['GET', 'POST'])
def register():
    form = FormRegistro()

    if request.method == "POST":
        if form.validate_on_submit():
            user = Usuario(email=form.email.data,
            nombre_usuario=form.username.data,
            password=form.password.data)
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash('Ya existe un Usuario con esas credenciales')
                return render_template('registro.html', form=form)
            flash('Ya podés ingresar al sistema.')
            return redirect(url_for('login'))

    return render_template('registro.html', form=form)

@app.route('/logout')
@login_required # Sólo usuarios autenticados pueden acceder a esta ruta
def logout(): 
    logout_user() # de Flask-Login. Elimina la sesión y cualquier información asociada al usuario actual
    flash('Se ha cerrado la sesión.')
    return redirect(url_for('login'))

if __name__ == '__main__': # Comprobamos que, si estamos en el archivo principal (main), entonces ejecutamos la aplicación
    app.run(debug=True) # el método run ejecuta la aplicación Flask
