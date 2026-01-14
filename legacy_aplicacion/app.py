8002349105


from typing import Text
from urllib import response
from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from aplicacion import config
#from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length
from aplicacion.forms import LoginForm, UploadForm,alumno,campeonato,buscapac,campeonato_combate\
    ,campeonato_pommse,horario_ent,fechas_buscar
from wtforms import SubmitField
from flask_wtf.file import FileField, FileRequired
from jinja2 import Environment, FileSystemLoader
#from os import listdir
from flask_login import LoginManager, login_user, logout_user, login_required,\
    current_user

from sqlalchemy import create_engine
from aplicacion.forms import LoginForm, FormUsuario
import pdfkit
import os
import pymysql
import csv
import pandas as pd


UPLOAD_FOLDER = os.path.abspath("./static/uploads/")
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpge"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config.from_object(config)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# Mysql Connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'apolo'
#mysql = MySQL(app)

# setting
app.secret_key = 'millave'


@login_manager.user_loader
def load_user(user_id):
    return (user_id)


@app.route('/')
def inicio():
    return render_template("home.html")


@app.route('/inicio_1')
@app.route('/inicio_1/<id>')
def inicio_1(id='0'):
    from aplicacion.models import Articulos, Categorias
    categoria = Categorias.query.get(id)
    if id == '0':
        articulos = Articulos.query.all()
    else:
        articulos = Articulos.query.filter_by(CategoriaId=id)
    categorias = Categorias.query.all()
    return render_template("inicio_1.html", articulos=articulos, categorias=categorias, categoria=categoria)


@app.route('/inicio_new')
@app.route('/inicio_new/<id>')
def inicio_new(id='0'):
    from aplicacion.models import Articulos, Categorias
    categoria = Categorias.query.get(id)
    if id == '0':
        articulos = Articulos.query.all()
    else:
        articulos = Articulos.query.filter_by(CategoriaId=id)
    categorias = Categorias.query.all()
    return render_template("inicio_new.html", articulos=articulos, categorias=categorias, categoria=categoria)

@app.route('/nosotros')
def nosotros():
    return render_template("nosotros.html")



@app.route('/historia')
def historia():
    return render_template("historia.html")


@app.route('/ocupa')
def ocupa():
    return render_template("ocupa.html")



@app.route('/resumen')
@login_required
def resumen():
    datos = request.cookies.get('cookie_pac')
    cursor = mysql.connection.cursor()
    cursor.execute(
        "select apellido1,nombres from paciente a  inner join pruebas b on  a.iden = b.id_paci where iden = %s;" , [datos])
    nom_pac = cursor.fetchone()
    cursor.execute(
        "select medico from paciente a inner join pruebas b on  a.iden = b.id_paci where iden = %s;" , [datos])
    med = cursor.fetchone()
    cursor.execute(
        "SELECT (TIMESTAMPDIFF(YEAR,fec_nac,CURDATE())) AS edad FROM paciente a  inner join pruebas b on  a.iden = b.id_paci where iden = %s;" , [datos])
    edad = cursor.fetchone()
    cursor.execute("select CURDATE();")
    fec_hoy = cursor.fetchone()
    cursor.execute(
        "select iden from paciente a  inner join pruebas b on  a.iden = b.id_paci where iden = %s;" , [datos])
    ci = cursor.fetchone()
    cursor.execute(
        "select * from pruebas where id = (select MAX(id) from pruebas);")
    datos = cursor.fetchall()
    print(datos)
    cursor.close()

    return render_template('resumen.html', nom_pac=nom_pac, med=med, edad=edad, fec_hoy=fec_hoy, ci=ci, datos=datos)


@login_manager.user_loader
def load_user(user_id):
    from aplicacion.models import Usuarios
    return Usuarios.query.get(int(user_id))


@app.route('/upload', methods=['get', 'post'])
def upload():
    form = UploadForm()  # carga request.from y request.file
    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)
        f.save(app.root_path+"/static/img/subidas/"+filename)
        return redirect(url_for('home'))
    return render_template('upload.html', form=form)


@app.route('/upload_1', methods=['get', 'post'])
def upload_1():
    form = UploadForm()  # carga request.from y request.file
    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)
        f.save(app.root_path+"/static/img/subidas/"+filename)
        return redirect(url_for('reporte_foto'))
    return render_template('upload_1.html', form=form)


@app.route('/inicio_foto')
@login_required
def inicio_foto():
    lista = []
    for file in listdir(app.root_path+"/static/img/subidas/"):
        lista.append(file)
    return render_template("inicio_foto.html", lista=lista)


@app.route('/reporte_foto')
@login_required
def reporte_foto():
    lista = []
    for file in listdir(app.root_path+"/static/img/subidas/"):
        lista.append(file)
    return render_template("reporte_foto.html", lista=lista)


@app.route('/reporte_foto1')
@login_required
def reporte_foto1():
    lista = []
    for file in listdir(app.root_path+"/static/img/subidas/"):
        lista.append(file)
    return render_template("reporte_foto1.html", lista=lista)


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = fechas_buscar()
    if form.validate_on_submit():
        return redirect(url_for('inicio'))
    return render_template('home.html', form=form)


@app.route('/home_alumn', methods=['GET', 'POST'])
@login_required
def home_alumn():

    return render_template('home_alumn.html')


@app.route('/home_campeonato', methods=['GET', 'POST'])
@login_required
def home_campeonato():

    return render_template('home_campeonato.html')

@app.route('/cate_peso', methods=['GET', 'POST'])
@login_required
def cate_peso():
    cur = mysql.connection.cursor()
    cur.execute('SELECT a.nombre,b.nombre,a.genero,a.rango,b.rango FROM cat_peso a inner JOIN cat_edad b on a.id_edad = b.id ')
    data = cur.fetchall()
    cur.close()

    return render_template('cate_peso.html', data=data)


@app.route('/horario_entrena', methods=['GET', 'POST'])
@login_required
def horario_entrena():
    form = horario_ent()
    if request.method == 'POST':
        iden = request.form['iden']
        horario = request.form['horario']
        cursor = mysql.connection.cursor()
        cursor.execute('select CURDATE()')
        fecha_log = cursor.fetchone()
        cursor.execute('insert into horario (id_alumno,valor_horario,fecha) VALUES (%s,%s,%s)',
                       (iden, horario, fecha_log))
        mysql.connection.commit()
        return render_template("home.html", form=form)
    return render_template('horario_entrena.html', form=form)

@app.route('/listar_paci/<id>', methods=['POST', 'GET'])
@login_required
def listar_paci(id):
    cur = mysql.connection.cursor()
    cur.execute(
        'SELECT * FROM paciente a inner join cat_examenes b on  a.id_examen = b.id  WHERE a.iden = %s )',  [id])
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('listar-paci.html', contact=data[0])



@app.route('/alumno_new', methods=["get", "post"])
@login_required
def alumno_new():
    form = alumno()
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        iden = request.form['iden']
        tipo_iden = request.form['tipo_iden']
        apellido1 = request.form['apellido1']
        apellido2 = request.form['apellido2']
        nombres = request.form['nombres']
        est_civil = request.form['est_civil']
        fec_nac = request.form['fec_nac']
        fec_ingreso = request.form['fec_ingreso']
        sexo = request.form['sexo']
        direccion = request.form['direccion']
        ocupacion = request.form['ocupacion']
        tipo_s = request.form['tipo_s']
        Nivel_edu = request.form['Nivel_edu']
        telefono1 = request.form['telefono1']
        telefono2 = request.form['telefono2']
        status = request.form['status']
        email = request.form['email']
        cinturon = request.form['cinturon']
        horario = request.form['horario']
        peso = request.form['peso']
        estatura = request.form['estatura']
        flexibilidad = request.form['flexibilidad']
        cursor = mysql.connection.cursor()
        cursor.execute('select CURDATE()')
        fecha_log = cursor.fetchone()
        foto = request.files['foto']
        filename = secure_filename(foto.filename)
        foto.save(app.root_path+"/static/fotos/"+filename)
        foto = filename
        cursor = mysql.connection.cursor()
        cursor.execute('insert into alumno_foto (iden,foto) VALUES (%s,%s)',(iden,foto))
        mysql.connection.commit()
        cursor.execute('insert into alumno (apellido_p,apellido_m,identificacion,tipo_iden,nombres,est_civil,fecha_nacimiento,fecha_ingreso,genero, ocupacion, status, tipo_sangre, nivel_educacion,direccion,telefono1,telefono2,mail,fecha_log) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                       (apellido1, apellido2, iden, tipo_iden, nombres, est_civil, fec_nac,fec_ingreso, sexo,ocupacion, status,tipo_s,Nivel_edu,direccion, telefono1, telefono2, email,fecha_log))
        mysql.connection.commit()
        cursor.execute('select CURDATE()')
        fecha = cursor.fetchone()
        cursor.execute('insert into cinturon (id_alumno,color,fecha) VALUES (%s,%s,%s)',(iden, cinturon, fecha))
        cursor.execute('insert into horario (id_alumno,valor_horario,fecha) VALUES (%s,%s,%s)',(iden, horario, fecha))
        cursor.execute('insert into peso (id_alumno,valor_peso,fecha) VALUES (%s,%s,%s)',(iden, peso, fecha))
        cursor.execute('insert into estatura (id_alumno,valor_estatura,fecha) VALUES (%s,%s,%s)',(iden, estatura, fecha))
        cursor.execute('insert into flexibilidad (id_alumno,valor_flexibilidad,fecha) VALUES (%s,%s,%s)',(iden, flexibilidad, fecha))
        mysql.connection.commit()
        return render_template("home.html", form=form)
    return render_template("alumno_new.html", form=form)

@app.route('/busc_alumno', methods = ['POST', 'GET'])
@login_required
def busc_alumno():
    form = buscapac()
    if request.method == 'POST':
        iden = request.form['iden']
        print(iden)
        cursor = mysql.connection.cursor()
        cursor.execute("""select a.identificacion,a.nombres,a.apellido_p,a.apellido_m,b.color,c.valor_peso,d.valor_estatura from alumno a 
                            inner join cinturon b on b.id_alumno = a.identificacion 
                            inner join peso c on c.id_alumno = a.identificacion 
                            inner join estatura d on d.id_alumno = a.identificacion 
                            WHERE identificacion = %s 
                            and b.fecha = (select max(fecha) from cinturon where id_alumno = %s) 
                            and c.fecha = (select max(fecha) from peso where id_alumno = %s) 
                            and d.fecha = (select max(fecha) from estatura where id_alumno = %s)""", [iden,iden,iden,iden])
        data = cursor.fetchone()
        cursor.execute("""select id_alumno,nombre,fecha,ubicacion,num_participantes from camp_combate a 
                            WHERE id_alumno = %s""",[iden])
        data1 = cursor.fetchall()
        cursor.execute("""select id_alumno,nombre,fecha,ubicacion,num_participantes from camp_pommse  
                            WHERE id_alumno = %s""",[iden])
        data2 = cursor.fetchall()
        cursor.execute("""select foto from alumno_foto WHERE iden = %s""",[iden])
        data3 = cursor.fetchone()
        print(data3)
        return render_template('listar-alumno.html', data=data,data1=data1,data2=data2,data3=data3)
    return render_template("bus_alumno.html", form=form)


@app.route('/busc_alumno1', methods = ['POST', 'GET'])
@login_required
def busc_alumno1():
    form = buscapac()
    if request.method == 'POST':
        iden = request.form['iden']
        print(iden)
        cursor = mysql.connection.cursor()
        cursor.execute("""select a.identificacion,a.nombres,a.apellido_p,a.apellido_m,b.color,c.valor_peso,d.valor_estatura from alumno a 
                            inner join cinturon b on b.id_alumno = a.identificacion 
                            inner join peso c on c.id_alumno = a.identificacion 
                            inner join estatura d on d.id_alumno = a.identificacion 
                            WHERE identificacion = %s 
                            and b.fecha = (select max(fecha) from cinturon where id_alumno = %s) 
                            and c.fecha = (select max(fecha) from peso where id_alumno = %s) 
                            and d.fecha = (select max(fecha) from estatura where id_alumno = %s)""", [iden,iden,iden,iden])
        data = cursor.fetchone()
        cursor.execute("""select id_alumno,valor_estatura,fecha from estatura a 
                            WHERE id_alumno = %s""",[iden])
        data1 = cursor.fetchall()
        cursor.execute("""select id_alumno,valor_peso,fecha from peso  
                            WHERE id_alumno = %s""",[iden])
        data2 = cursor.fetchall()
        cursor.execute("""select id_alumno,valor_flexibilidad from flexibilidad  
                            WHERE id_alumno = %s""",[iden])
        data4 = cursor.fetchall()
        cursor.execute("""select foto from alumno_foto WHERE iden = %s""",[iden])
        data3 = cursor.fetchone()
        print(data3)
        cursor.execute("""SELECT color FROM cinturon
                            where fecha = (SELECT MAX(fecha) FROM cinturon where id_alumno = %s)
                            limit 1 ;""",[iden])
        color = cursor.fetchone()
        print(color)
        cursor.execute("""SELECT (TIMESTAMPDIFF(YEAR,fecha_nacimiento,CURDATE())) AS edad FROM alumno
                            where identificacion = %s;""",[iden])
        edad = cursor.fetchone()
        cursor.execute("""select valor_peso from peso where fecha = (SELECT MAX(fecha) FROM peso where id_alumno = %s)
                            limit 1 ;""",[iden])
        peso = cursor.fetchone()
        cursor.execute("""select genero from alumno WHERE identificacion = %s""",[iden])
        genero = cursor.fetchone()
        cursor.execute('SELECT nombre_cat FROM categorias WHERE genero = %s AND edad_min <= %s AND edad_max >= %s AND peso_min <= %s AND peso_max >= %s',(genero, edad, edad, peso, peso))
        categoria = cursor.fetchone()
        cursor.execute('SELECT nombre_cat1 FROM categorias WHERE genero = %s AND edad_min <= %s AND edad_max >= %s AND peso_min <= %s AND peso_max >= %s',(genero, edad, edad, peso, peso))
        cate1 = cursor.fetchone()
        print(edad,categoria,cate1)
        print(edad)
        print(peso)
        return render_template('listar-alumno1.html', data=data,data1=data1,data2=data2,data4=data4,data3=data3,color=color,edad=edad,categoria=categoria,cate1=cate1)
    return render_template("bus_alumno1.html", form=form)



@app.route('/busc_asistencia', methods = ['POST', 'GET'])
@login_required
def busc_asistencia():
    form = fechas_buscar()
    if request.method == 'POST':
        iden = request.form['iden']
        mes = request.form['mes']
        print(iden)
        cursor = mysql.connection.cursor()
        cursor.execute("""select a.identificacion,a.nombres,a.apellido_p,a.apellido_m,b.color,c.valor_peso,d.valor_estatura from alumno a 
                            inner join cinturon b on b.id_alumno = a.identificacion 
                            inner join peso c on c.id_alumno = a.identificacion 
                            inner join estatura d on d.id_alumno = a.identificacion 
                            WHERE identificacion = %s 
                            and b.fecha = (select max(fecha) from cinturon where id_alumno = %s) 
                            and c.fecha = (select max(fecha) from peso where id_alumno = %s) 
                            and d.fecha = (select max(fecha) from estatura where id_alumno = %s)""", [iden,iden,iden,iden])
        data = cursor.fetchone()
        cursor.execute("""select id_alumno,valor_horario,fecha from horario a 
                            WHERE id_alumno = %s and EXTRACT(MONTH FROM fecha) = %s""",[iden,mes])
        data1 = cursor.fetchall()
        cursor.execute("""select foto from alumno_foto WHERE iden = %s""",[iden])
        data3 = cursor.fetchone()
        print(data3)
        return render_template('listar-asistencia.html', data=data,data1=data1,data3=data3)
    return render_template("busc_asistencia.html", form=form)



@app.route('/datos_cinturon', methods=["get", "post"])
@login_required
def datos_cinturon():
    form = alumno()
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        iden = request.form['iden']
        cinturon = request.form['cinturon']
        cin_aval = request.form['cin_aval']
        cin_aval1 = request.form['cin_aval1']
        cursor = mysql.connection.cursor()
        cursor.execute('select CURDATE()')
        fecha = cursor.fetchone()
        cursor.execute('insert into cinturon (id_alumno,color,fecha) VALUES (%s,%s,%s)',(iden, cinturon, fecha))
        cursor.execute('insert into cintu_nacional (iden,dan,fecha) VALUES (%s,%s,%s)',(iden, cin_aval, fecha))
        cursor.execute('insert into cintu_internacional (id_alumno,dan,fecha) VALUES (%s,%s,%s)',(iden, cin_aval1, fecha))
        mysql.connection.commit()
        return render_template("home_alumn.html", form=form)
    return render_template("datos_cinturon.html", form=form)


@app.route('/datos_peso', methods=["get", "post"])
@login_required
def datos_peso():
    form = alumno()
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        iden = request.form['iden']
        peso = request.form['peso']
        cursor = mysql.connection.cursor()
        cursor.execute('select CURDATE()')
        fecha = cursor.fetchone()
        cursor.execute('insert into peso (id_alumno,valor_peso,fecha) VALUES (%s,%s,%s)',(iden, peso, fecha))
        mysql.connection.commit()
        return render_template("home_alumn.html", form=form)
    return render_template("datos_peso.html", form=form)


@app.route('/datos_activo', methods=["get", "post"])
@login_required
def datos_activo():
    form = alumno()
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        iden = request.form['iden']
        status = request.form['status']
        cursor = mysql.connection.cursor()
        cursor.execute('update alumno SET status = %s where identificacion = %s',(status,iden))
        mysql.connection.commit()
        return render_template("home_alumn.html", form=form)
    return render_template("datos_activo.html", form=form)


@app.route('/listar_alumno', methods=["get", "post"])
@login_required
def listar_alumno():
    cursor = mysql.connection.cursor()
    cursor.execute('select identificacion, nombres, apellido_p,apellido_m,status from alumno where status = "ACTIVO"')
    data = cursor.fetchall()
    return render_template("listar_alumno.html", data=data)

@app.route('/datos_estatura', methods=["get", "post"])
@login_required
def datos_estatura():
    form = alumno()
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        iden = request.form['iden']
        estatura = request.form['estatura']
        cursor = mysql.connection.cursor()
        cursor.execute('select CURDATE()')
        fecha = cursor.fetchone()
        cursor.execute('insert into estatura (id_alumno,valor_estatura,fecha) VALUES (%s,%s,%s)',(iden, estatura, fecha))
        mysql.connection.commit()
        return render_template("home_alumn.html", form=form)
    return render_template("datos_estatura.html", form=form)


@app.route('/datos_flexibilidad', methods=["get", "post"])
@login_required
def datos_flexibilidad():
    form = alumno()
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        iden = request.form['iden']
        flexibilidad = request.form['flexibilidad']
        cursor = mysql.connection.cursor()
        cursor.execute('select CURDATE()')
        fecha = cursor.fetchone()
        cursor.execute('insert into flexibilidad (id_alumno,valor_flexibilidad,fecha) VALUES (%s,%s,%s)',(iden, flexibilidad, fecha))
        mysql.connection.commit()
        return render_template("home_alumn.html", form=form)
    return render_template("datos_flexibilidad.html", form=form)

@app.route('/campeonato_new', methods=["get", "post"])
@login_required
def campeonato_new():
    form = campeonato()
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        puntua = request.form['puntua']
        fecha = request.form['fecha']
        obs = request.form['obs']
        cursor = mysql.connection.cursor()
        cursor.execute('insert into campeonato (nombre,puntua,fecha,obs) VALUES (%s,%s,%s,%s)',
                       (nombre, puntua, fecha, obs,))
        mysql.connection.commit()
        flash('Campeonato guardado correctamente')
        return render_template("home.html", form=form)
    return render_template("campeonato_new.html", form=form)


@app.route('/alumno_foto')
@login_required
def alumno_foto():
    lista = []
    for file in listdir(app.root_path+"/static/img/fotos/"):
        lista.append(file)
    return render_template("home.html", lista=lista)


@app.route('/upload_foto', methods=['get', 'post'])
def upload_foto():
    form = UploadForm()  # carga request.from y request.file
    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)
        f.save(app.root_path+"/static/fotos/"+filename)
        foto = filename
        cursor = mysql.connection.cursor()
        cursor.execute('select identificacion from alumno where fecha_log = (select max(fecha_log) from alumno);')
        ident = cursor.fetchone()
        cursor.execute('insert into alumno_foto (iden,foto) VALUES (%s,%s)',(ident,foto))
        mysql.connection.commit()
        return redirect(url_for('home'))
    return render_template('upload_foto.html', form=form)

@app.route('/campeonato_combate_new', methods=["get", "post"])
@login_required
def campeonato_combate_new():
    form = campeonato_combate()
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        iden = request.form['iden']
        ubicacion = request.form['ubicacion']
        nombre = request.form['nombre']
        puntua = request.form['puntua']
        fecha = request.form['fecha']
        cinturon = request.form['cinturon']
        edad = request.form['edad']
        peso = request.form['peso']
        num_part = request.form['num_part']
        obs = request.form['obs']
        cursor = mysql.connection.cursor()
        cursor.execute('insert into camp_combate (id_alumno,nombre,puntua,fecha,ubicacion,cat_cinturon,cat_edad,cat_peso,num_participantes,obs) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                       (iden, nombre,puntua,fecha,ubicacion,cinturon,edad,peso,num_part,obs,))
        mysql.connection.commit()
        flash('Campeonato guardado correctamente')
        return render_template("home.html", form=form)
    return render_template("campeonato_combate_new.html", form=form)


@app.route('/campeonato_pommse_new', methods=["get", "post"])
@login_required
def campeonato_pommse_new():
    form = campeonato_pommse()
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        iden = request.form['iden']
        ubicacion = request.form['ubicacion']
        nombre = request.form['nombre']
        puntua = request.form['puntua']
        fecha = request.form['fecha']
        cinturon = request.form['cinturon']
        edad = request.form['edad']
        num_part = request.form['num_part']
        obs = request.form['obs']
        cursor = mysql.connection.cursor()
        cursor.execute('insert into camp_pommse (id_alumno,nombre,puntua,fecha,ubicacion,cat_cinturon,cat_edad,num_participantes,obs) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                       (iden, nombre,puntua,fecha,ubicacion,cinturon,edad,num_part,obs,))
        mysql.connection.commit()
        flash('Campeonato guardado correctamente')
        return render_template("home.html", form=form)
    return render_template("campeonato_pommse_new.html", form=form)

@app.route('/busc_campeonato', methods = ['POST', 'GET'])
@login_required
def busc_campeonato():
    form = buscapac()
    if request.method == 'POST':
        iden = request.form['iden']
        print(iden)
        cursor = mysql.connection.cursor()
        cursor.execute("""select a.identificacion,a.nombres,a.apellido_p,a.apellido_m,b.color,c.valor_peso,d.valor_estatura from alumno a 
                            inner join cinturon b on b.id_alumno = a.identificacion 
                            inner join peso c on c.id_alumno = a.identificacion 
                            inner join estatura d on d.id_alumno = a.identificacion 
                            WHERE identificacion = %s 
                            and b.fecha = (select max(fecha) from cinturon where id_alumno = %s) 
                            and c.fecha = (select max(fecha) from peso where id_alumno = %s) 
                            and d.fecha = (select max(fecha) from estatura where id_alumno = %s)""", [iden,iden,iden,iden])
        data = cursor.fetchall()
        cursor.execute("""select b.id_alumno,a.nombre,a.fecha,b.ubicacion,b.num_participantes from campeonato a 
                            inner join camp_combate b
                            on a.id = b.id
                            WHERE b.id_alumno = %s""",[iden])
        data1 = cursor.fetchall()
        cursor.execute("""select b.id_alumno,a.nombre,a.fecha,b.ubicacion,b.num_participantes from campeonato a 
                            inner join camp_pommse b
                            on a.id = b.id
                            WHERE b.id_alumno = %s""",[iden])
        data2 = cursor.fetchall()
        #print(data[0])
        return render_template('listar-alumno.html', data=data,data1=data1,data2=data2)
    return render_template("busc_campeonato.html", form=form)


@app.route('/edit_pac/<string:id>', methods = ['POST', 'GET'])
def get_pac(id):
    cur = mysql.connection.cursor()
    #cur.execute("SELECT * FROM paciente WHERE ci = %s", (id))
    cur.execute("SELECT * FROM paciente WHERE ci = '1711459816'")
    data = cur.fetchone()
    cur.close()
    print(id)
    print(data[2])
    return render_template('edit_pac.html', paciente = data)






@app.route('/update_pac/<id>', methods=['POST'])
def update_contact(id):
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE contacts
            SET fullname = %s,
                email = %s,
                phone = %s
            WHERE id = %s
        """, (fullname, email, phone, id))
        flash('Contact Updated Successfully')
        mysql.connection.commit()
        return redirect(url_for('Index'))





@app.route('/pruebas_lab', methods=['GET', 'POST'])
@login_required
def pruebas_lab():
    cursor = mysql.connection.cursor()
    cursor.execute("select * from cat_examenes;")
    prulab = cursor.fetchall()
    datos = request.cookies.get('cookie_pac')
    print(datos)
    return render_template('pruebas_lab.html', prulab=prulab)
    


@app.route('/genera_pdf')
@login_required
def genera_pdf():
    env = Environment(loader=FileSystemLoader('templates'))
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None
    }
    pdfkit.from_file('resumen.html', 'out.pdf', options=options)
    return 'OK'


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error="Página no encontrada..."), 404


@app.route('/cons_404', methods=['GET', 'POST'])
def cons_404():
    return render_template('404_cons.html')


@app.route('/login', methods=['get', 'post'])
def login():
    from aplicacion.models import Usuarios
    # Control de permisos
    if current_user.is_authenticated:
        # return 'OK'
        return redirect(url_for("home_alumn"))
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuarios.query.filter_by(username=form.username.data).first()
        print(user)
        pas1 = Usuarios.query.filter_by(password=form.password.data).first()
        print(pas1)
        pas = user.verify_password(form.password.data)
        print(pas)
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        form.username.errors.append("Usuario o contraseña incorrectas.")
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('inicio'))


@app.route('/perfil/<username>', methods=["get", "post"])
@login_required
def perfil(username):
    from aplicacion.models import Usuarios
    user = Usuarios.query.filter_by(username=username).first()
    if user is None:
        render_template("404.html")
    form = FormUsuario(request.form, obj=user)
    del form.password
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("usuarios_new.html", form=form, perfil=True)


@login_manager.user_loader
def load_user(user_id):
    from aplicacion.models import Usuarios
    return Usuarios.query.get(int(user_id))




@app.route('/import_csv')
def import_csv():
    with open('test.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        print(reader)
        for row in reader:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO posicion_camp (nombres, academia, ubicacion, puntos, obs) VALUES (%s, %s, %s, %s, %s)'%(str(row[0]),str(row[0]),str(row[2]),str(row[3]),str(row[4])))
            mysql.connection.commit()
    return 'CSV importado successfully'


@app.route('/import_csv_p')
@login_required
def import_csv_p():
    df = pd.read_excel("articulos.xlsx")
    df1 = pd.read_excel("data1.xlsx")
    engine = create_engine("mysql://root:1234@localhost/apolo")
    engine1 = create_engine("mysql://root:1234@localhost/apolo")
    df.to_sql(name='articulos', con=engine, if_exists='replace', index=False)
    df1.to_sql(name='posicion_test', con=engine1, if_exists='replace', index=False)
    return redirect(url_for("inicio"))

if __name__ == "__main__":
    app.run(debug=True)


