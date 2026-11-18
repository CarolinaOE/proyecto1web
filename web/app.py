from flask import Flask, render_template, request, redirect, url_for
from data import datos_data
from operaciones import (buscar_por_id, filtrar_usuarios, calcular_estadisticas,
                         validar_nuevo_usuario, generar_cuenta, calcular_hipoteca)

app = Flask(__name__)

@app.context_processor    #BASE.HTML (variables que quiero que se usen en todas las plantillas como lema y datos)
def datos_globales():
    # Variables disponibles en TODAS las plantillas 
    return {
        "nombre_banco": datos_data["nombre_banco"],
        "lema_banco": datos_data["lema_banco"],
        "usuarios": datos_data["usuarios"],
    }
#-------------------------------------

@app.route("/")         #INDEX.HTML (PÁGINA INICIO)
def index():
    return render_template("index.html")


@app.route("/listaUsuarios") #LISTADO.HTML (PÁGINA DE LISTADO DE ELEMENTOS)
def listado():
    return render_template("listado.html", 
                           usuarios=datos_data["usuarios"])


@app.route("/usuario/<int:usuario_id>")   #DETALLE.HTML (PÁGINA DE DETALLE)
def detalle(usuario_id):     #en este caso busca por el número id (1,2....hasta 11)
    usuario = buscar_por_id(usuario_id)
    if not usuario:
        error = "El usuario solicitado no existe en el sistema."
        return render_template("detalle.html", 
                               usuario=None, 
                               error=error)
    return render_template("detalle.html", 
                           usuario=usuario, 
                           error=None) 


@app.route("/buscarUsuario", methods=["GET"])
def buscar():
    criterio = request.args.get("criterio", "")
    valor = request.args.get("valor", "").strip()
    resultados = []

    if criterio and valor:
        resultados = filtrar_usuarios(criterio, valor)

    return render_template("buscar.html", 
                           resultados=resultados, 
                           criterio=criterio, 
                           valor=valor)


@app.route("/registro", methods=["GET", "POST"])  #metodo get para el formulario vacio, post para enviar datos
def registro():
    errores = {}
    datos_previos = {}

    if request.method == "POST":
        datos_previos = request.form
        errores = validar_nuevo_usuario(request.form)   #antes de nada valida con la funcion de validar_nuevo_usuario

        if not errores: #añadir nuevo usuario si no sale errores
            nuevo_id = max((u.get("id", 0) for u in datos_data["usuarios"]), default=0) + 1

            nuevo_usuario = {
                "id": nuevo_id,
                "nombre": request.form["nombre"].strip(),
                "apellido1": request.form["apellido1"].strip(),
                "apellido2": request.form.get("apellido2", "").strip(),
                "documento": request.form.get("documento", "DNI"),
                "usuario": request.form["usuario"].strip().upper(),
                "fechaNacimiento": request.form["fechaNacimiento"].strip(),
                "nacionalidad": request.form.get("nacionalidad", "española").strip(),
                "género": request.form["género"],
                "email": request.form["email"].strip(),
                "telefono": request.form["telefono"].strip(),
                "tipo_cuenta": request.form.get("cuenta_tipo", "Corriente"),
                "cuenta": generar_cuenta(),
                "saldo": float(request.form["saldo"].replace(",", ".")),
                "activo": True,
            }
            datos_data["usuarios"].append(nuevo_usuario)  #envia el añadido al listado de usuarios
            return redirect(url_for("listado"))

    return render_template("registro.html", 
                           errores=errores, 
                           datos_previos=datos_previos)


@app.route("/estadisticas")
def estadisticas():
    stats = calcular_estadisticas()
    return render_template("estadisticas.html", stats=stats)


@app.route("/simulador", methods=["GET", "POST"])
def simuladorHipoteca():
    resultado = None
    # Valores por defecto para cuando se carga la página por primera vez (GET)
    capital = "0"
    interes = "2.5"
    anos = "20"

    if request.method == "POST":
        capital = request.form.get("capital", "")
        interes = request.form.get("interes", "")
        anos = request.form.get("anos", "")
        
        resultado = calcular_hipoteca(capital, interes, anos)

    return render_template("simulador.html", 
                           resultado=resultado, 
                           capital=capital, 
                           interes=interes, 
                           anos=anos)


@app.route("/contacto")
def contacto():
    return render_template("contacto.html")

