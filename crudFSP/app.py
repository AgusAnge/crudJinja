# IMPORTAMOS LIBRERIAS NECESARIAS PARA HACER RENDERIZADO DE TEMPLATES
from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from flaskext.mysql import MySQL  # importacion para conexion con BD
from flask import send_from_directory
from datetime import datetime
import os


# CREAMOS LA APLICACION
app = Flask(__name__)

app.secret_key="Ange1994"

mysql = MySQL()
# conexion con bd mysql usando el host localhost
app.config["MYSQL_DATABASE_HOST"] = "localhost"
# usuario y contraseña para acceso a la BD
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = "12345678"
app.config["MYSQL_DATABASE_DB"] = "crud"
mysql.init_app(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA']=CARPETA #referencia a variable para almacenar ruta especifica


#CREACION DE UN ACCESO PARA PERMITIR LA VISUALIZACION DE LAS FOTOS
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)
    

# realizamos el ruteo
@app.route(
    "/"
)  # cuando se le hace la solicitud con la /, significa la solicitud al port
# 127.0.0.1:5000
# y automaticamente accedera al INDEX.HTML que ya se encuentra renderizado
def index():
    sql = "SELECT * FROM productos;"
    conn = mysql.connect()
    # conn, hace referencia a conexion de linea 11
    cursor = conn.cursor()  # creacion del cursor
    cursor.execute(sql)  # ejecucion de la instruccion sql

    productos = cursor.fetchall()  # trae todos los elementos de la BD
    print(productos)  # los muestra

    conn.commit()  # cierre de la conexion
    return render_template(
        "productos/index.html", productos=productos
    )  # envio de datos a index.html

@app.route("/create")
def create():
    return render_template("productos/create.html")


@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form["nombreProducto"]
    _precio = request.form["precioProducto"]
    _fotoProducto = request.files[
        "fotoProducto"
    ]
    _id=request.form['txtId']
    
    sql = "UPDATE productos SET nombre = %s, precio = %s WHERE id = %s;"
    datos = (_nombre, _precio,  _id)
    conn = mysql.connect()
    cursor = conn.cursor()  # creacion del cursor
    
    now = datetime.now()
    tiempo = now.strftime(
        "%Y%H%M%S"
    )  # se obtiene el tiempo en Años, horas, minutos y seg

    if _fotoProducto.filename != "":  # si el nombre de la foto no es vacio
        nuevoNombreFoto = (
            tiempo + _fotoProducto.filename
        )  # se genera un nuevo nombre concatenando
        _fotoProducto.save("uploads/" + nuevoNombreFoto)  # se la guarda
        
        cursor.execute("SELECT foto FROM productos WHERE id = %s", _id)
        fila=cursor.fetchall()
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
        cursor.execute("UPDATE productos SET foto=%s WHERE id=%s", (nuevoNombreFoto, _id))
        conn.commit()
        
    
    cursor.execute(sql, datos)  # ejecucion de la instruccion sql
    conn.commit()  # cierre de la conexion
    
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect() #conexion bd
    cursor = conn.cursor()  # creacion del cursor
    cursor.execute("SELECT * FROM productos WHERE id =%s", (id))  # ejecucion de la instruccion sql
    productos = cursor.fetchall()
    conn.commit()
    return render_template("productos/edit.html", productos=productos)  # redireccion a edit.html


@app.route("/destroy/<int:id>")
def destroy(id):
    conn = mysql.connect() #conexion bd
    cursor = conn.cursor()  # creacion del cursor
    cursor.execute("SELECT foto FROM productos WHERE id = %s", id)
    fila=cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
    cursor.execute("DELETE FROM productos WHERE id=%s", (id))  # ejecucion de la instruccion sql
    conn.commit()
    return redirect("/")  # redirecciona a la pagina anterior tras eliminar registro


@app.route("/store", methods=["POST"])
def storage():
    # recepcion de datos cargados por usuario en Create
    _nombre = request.form["nombreProducto"]
    _precio = request.form["precioProducto"]
    _fotoProducto = request.files[
        "fotoProducto"
    ]  # se recepciona como files ya que es info binaria

    if(_nombre=='') or _precio=='' or _fotoProducto=='':
        flash("Se deben llenar todos los campos")
        return redirect(url_for('create'))
        
    
    now = datetime.now()
    tiempo = now.strftime(
        "%Y%H%M%S"
    )  # se obtiene el tiempo en Años, horas, minutos y seg

    if _fotoProducto.filename != "":  # si el nombre de la foto no es vacio
        nuevoNombreFoto = (
            tiempo + _fotoProducto.filename
        )  # se genera un nuevo nombre concatenando
        _fotoProducto.save("uploads/" + nuevoNombreFoto)  # se la guarda

    sql = "INSERT INTO productos ( nombre, precio, foto) values (%s, %s, %s);"
    datos = (_nombre, _precio, nuevoNombreFoto)
    conn = mysql.connect()
    cursor = conn.cursor()  # creacion del cursor
    cursor.execute(sql, datos)  # ejecucion de la instruccion sql
    conn.commit()  # cierre de la conexion
    return redirect('/')


# HACEMOS QUE CORRA EN MODO DEBUG
if __name__ == "__main__":
    app.run(debug=True)
