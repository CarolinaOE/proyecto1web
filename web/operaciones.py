from datetime import date, datetime
from data import datos_data


def buscar_por_id(usuario_id):
    for u in datos_data["usuarios"]:
        if u["id"] == usuario_id:
            return u
    else:
        return None

#Funcion de FILTRAR USUARIOS por algun dato en concreto (consultar mediante formulario)
def filtrar_usuarios(criterio, valor):
    usuarios = datos_data["usuarios"]
    valor = valor.strip()

    if criterio == "nombre":
        v = valor.lower()
        return [u for u in usuarios
                if v in f'{u["nombre"]} {u["apellido1"]} {u["apellido2"]}'.lower()]

    elif criterio == "genero":
        return [u for u in usuarios if u["género"].lower() == valor.lower()]

    elif criterio == "tipo_cuenta":
        return [u for u in usuarios if u["tipo_cuenta"].lower() == valor.lower()]

    else:
        return []

#Funcion de CREAR CUENTA (añadir nuevos elementos)
def generar_cuenta():
    usados = {u["cuenta"] for u in datos_data["usuarios"]}
    n = 1000 + len(usados) + 1
    while f"ES12-1234-5678-{n}" in usados:
        n += 1
    return f"ES12-1234-5678-{n}"

#Funcion de VALIDACIÓN DE NUEVA CUENTA (validación del registro)
def validar_nuevo_usuario(form):
    errores = {}

    # Campos obligatorios
    for campo, etiqueta in [("nombre", "El nombre"), ("apellido1", "El primer apellido"),
                            ("usuario", "El número de documento")]:
        if not form.get(campo, "").strip():
            errores[campo] = f"{etiqueta} es obligatorio."

    # Documento ya registrado
    documento = form.get("usuario", "").strip().upper()
    if documento and any(u["usuario"].upper() == documento for u in datos_data["usuarios"]):
        errores["usuario"] = "Ya existe un cliente con ese documento."

    # Rango respecto al mínimo y máximo de la cantidad de saldo
    try:
        saldo = float(form.get("saldo", "").strip().replace(",", "."))
        if saldo < 0 or saldo > 1_000_000:
            errores["saldo"] = "El saldo inicial debe estar entre 0 y 1.000.000 €."
    except ValueError:
        errores["saldo"] = "El saldo inicial debe ser un número."

    # Dato numérico
    try:
        nac = datetime.strptime(form.get("fechaNacimiento", "").strip(), "%d/%m/%Y").date()
        hoy = date.today()
        edad = hoy.year - nac.year - ((hoy.month, hoy.day) < (nac.month, nac.day))
        if edad < 18:
            errores["general"] = "Tienes que ser mayor de edad para abrir una cuenta."
    except ValueError:
        errores["general"] = "La fecha de nacimiento debe tener el formato DD/MM/AAAA."

    return errores

#Funcion de CALCULAR ESTADÍSTICAS DE CLIENTES  (estadísticas)
def calcular_estadisticas():
    usuarios = datos_data["usuarios"]
    if not usuarios:
        return {"total": 0, "activos": 0, "inactivos": 0, "saldo_total": 0,
                "saldo_medio": 0, "mayor_saldo": None, "menor_saldo": None}

    saldos = [u["saldo"] for u in usuarios]
    activos = sum(1 for u in usuarios if u["activo"])
    return {
        "total": len(usuarios),
        "activos": activos,
        "inactivos": len(usuarios) - activos,
        "saldo_total": round(sum(saldos), 2),
        "saldo_medio": round(sum(saldos) / len(saldos), 2),
        "mayor_saldo": max(usuarios, key=lambda u: u["saldo"]),
        "menor_saldo": min(usuarios, key=lambda u: u["saldo"]),
    }

#Funcion de CALCULAR HIPOTECA (personalizada pequeña calculadora)
def calcular_hipoteca(capital, interes_anual, anos):
    if not capital or not interes_anual or not anos:
        return None
    
    cap = float(capital)
    interes = float(interes_anual)
    n = int(anos) * 12  # meses totales
        
    if cap <= 0 or n <= 0:
        return None  
    if interes == 0:
        cuota = cap / n
    else:
        i = (interes / 100) / 12  # interés mensual
        cuota = cap * (i * (1 + i)**n) / ((1 + i)**n - 1)
            
    total_pagar = cuota * n
    intereses_totales = total_pagar - cap
        
    return {
        "cuota_mensual": round(cuota, 2),
        "total_pagar": round(total_pagar, 2),
        "intereses_totales": round(intereses_totales, 2),
        "capital": cap,
        "anos": int(anos),
        "interes": interes
    }
    