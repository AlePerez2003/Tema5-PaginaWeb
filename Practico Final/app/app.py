from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy, query
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Preceptor, Curso, Estudiante, Asistencia, Padre
    
@app.route('/')
def inicio():
	return render_template('inicio.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        if  not request.form['email'] or not request.form['password'] or not request.form['user_type']:
            return render_template('error.html', error="Por favor ingrese los datos requeridos")
        else:
            if request.form['user_type'] == 'Preceptor':
                user= Preceptor.query.filter_by(correo = request.form['email']).first()
            elif request.form['user_type'] == 'Padre':
                user= Padre.query.filter_by(correo= request.form['email']).first()

            if user is None:
                return render_template('error.html', error="El correo no está registrado")
            else:
                c = request.form['password']
                result = hashlib.md5(c.encode()).hexdigest()
                if result == user.clave:
                    verificacion = True
                elif result != user.clave:
                    verificacion = False
                if verificacion and request.form['user_type'] == 'Preceptor':
                    session['user_id'] = user.id
                    session['user_type'] = request.form['user_type']
                    return render_template('preceptor_home.html', usuario = user)
                elif verificacion and request.form['user_type'] == 'Padre':
                    return render_template('inicio_padre.html')
                else:
                    return render_template('error.html', error="La contraseña no es válida")
    else:
        return render_template('login.html')



@app.route('/preceptor_home')
def preceptor_home():
    return render_template('preceptor_home.html', usuario = Preceptor.query.filter_by(id = session['user_id']).first())

@app.route('/registrar_asistencia')
def seleccionar_curso():
    if request.method == 'POST':
        curso_actual = request.form['curso']
        curso = Curso.query.filter_by(id = curso_actual).first()
        estudiantes= Estudiante.query.filter_by(idcurso=curso.id).order_by(text('apellido, nombre')).all()
        session['curso']=curso
        session['estudiantes']=estudiantes
        return render_template('cargar_asistencias.html', curso= curso, estudiantes=estudiantes)
    else:
        return render_template('registrar_asistencia.html', usuario=Preceptor.query.filter_by(id= session['user_id']))

@app.route('/cargar_asistencia', methods=['GET', 'POST'])
def registrar_asistencia():

    if request.method == 'POST':
        
            clase = int(request.form['clase'])
            fecha = request.form['fecha']
            
            for estudiante in estudiantes:
                asistencia = request.form.get(f'asistencia_{estudiante.id}') 
                justificacion = request.form.get(f'justificacion_{estudiante.id}', '')
                registro_asistencia = Asistencia(
                    idestudiante=estudiante.id,
                    fecha=datetime.strptime(fecha, "%Y-%m-%d").date(),
                    codigoclase=clase,
                    asistio=asistencia,
                    justificacion=justificacion if asistencia == 'n' else ''
                )

                db.session.add(registro_asistencia)
            db.session.commit()
            
            return render_template("error.html", message="Asistencia registrada con exito", tipo="")
        
    else:

        curso = session['curso']
        estudiantes = session['estudiantes']
        
        return render_template('cargar_asistencia.html', curso = curso, estudiantes = estudiantes)
    
    

@app.route('/obtener_informe_detallado', methods=['GET','POST'])
def obtener_informe_detallado():
    
    if request.method == 'POST':
        curso_actual=request.form['curso']
        curso_obtenido=Curso.query.filter_by(id=curso_actual).first()
        estudiantes_obtenidos=Estudiante.query.filter_by(idcurso=curso_obtenido.id).order_by(text('apellido, nombre')).all()
        print(estudiantes_obtenidos)
        lista_asistencias=[]
        
        for estudiante in estudiantes_obtenidos:
            contadores=['%s %s'%(estudiante.apellido, estudiante.nombre),0,0,0,0,0,0,0.0]
            asistencias_obtenidas=estudiante.asistencia
            
            for asistencia in asistencias_obtenidas:
                
                if asistencia.codigoclase==1:
                    
                    if asistencia.asistio=='s':
                        contadores[1]+=1
                        
                    elif asistencia.asistio=='n':
                        
                        if asistencia.justificacion=='':
                            contadores[2]+=1
                            
                        else:
                            contadores[3]+=1
                            
                elif asistencia.codigoclase==2:
                    
                    if asistencia.asistio=='s':
                        contadores[4]+=1
                        
                    elif asistencia.asistio=='n':
                        
                        if asistencia.justificacion=='':
                            contadores[5]+=1
                            
                        else:
                            contadores[6]+=1
            contadores[7]=float(contadores[2]+contadores[3])+contadores[5]/2+contadores[6]/2
            lista_asistencias.append(contadores)
                
        return render_template('listado_asistencias.html',informe=lista_asistencias)
    else:
        return render_template('obtener_informe_detallado.html',preceptor=Preceptor.query.filter_by(correo=session['user_id']).first())

    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug = True, port=5000)