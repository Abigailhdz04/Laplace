import sympy as sp

# ============================================================
# RESOLVEDOR DE EDO LINEALES POR TRANSFORMADA DE LAPLACE
# Versión para examen / salida normal en consola
# ============================================================

t = sp.symbols('t', real=True, positive=True)
s = sp.symbols('s', real=True)
Y = sp.Symbol('Y')

# ------------------------------------------------------------
# UTILIDADES DE IMPRESIÓN
# ------------------------------------------------------------

def barra(char="=", n=78):
    print(char * n)

def encabezado(texto):
    print()
    barra("=")
    print(texto)
    barra("=")

def subtitulo(texto):
    print()
    barra("-")
    print(texto)
    barra("-")

def mostrar_expr(etiqueta, expr):
    print(f"{etiqueta}")
    print(sp.pretty(expr, use_unicode=True))
    print()

def mostrar_eq(etiqueta, lhs, rhs):
    print(f"{etiqueta}")
    print(sp.pretty(sp.Eq(lhs, rhs), use_unicode=True))
    print()

# ------------------------------------------------------------
# ENTRADAS
# ------------------------------------------------------------

def leer_entero(mensaje, minimo=1):
    while True:
        try:
            valor = int(input(mensaje).strip())
            if valor < minimo:
                print(f"Ingresa un entero mayor o igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("Entrada no válida. Debes escribir un número entero.")

def leer_expr(mensaje):
    entorno = {
        "t": t,
        "s": s,
        "exp": sp.exp,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "sqrt": sp.sqrt,
        "pi": sp.pi,
        "E": sp.E,
        "Heaviside": sp.Heaviside,
        "DiracDelta": sp.DiracDelta,
        "u": sp.Heaviside
    }

    while True:
        texto = input(mensaje).strip()
        try:
            expr = sp.sympify(texto, locals=entorno)
            return sp.simplify(expr)
        except Exception as e:
            print("No se pudo interpretar la expresión.")
            print("Ejemplos válidos: 5, t**2+2, exp(3*t), sin(t), cos(3*t), Heaviside(t-1)")
            print(f"Detalle: {e}")

def capturar_datos():
    encabezado("Bienvenido a este resolvedor de examen de Laplace")
    print("Este programa resuelve EDO lineales con coeficientes constantes")
    print("usando Transformada de Laplace y muestra el desarrollo en consola.")
    print()
    print("Forma general:")
    print("a_n*y^(n)(t) + a_(n-1)*y^(n-1)(t) + ... + a_1*y'(t) + a_0*y(t) = f(t)")
    print()

    n = leer_entero("Ingresa el orden n de la ecuación diferencial: ", 1)

    print()
    print("Ahora captura los coeficientes desde la derivada de mayor orden hasta y(t).")
    coeficientes = []
    for orden in range(n, -1, -1):
        coef = leer_expr(f"Coeficiente de la derivada de orden {orden}: ")
        coeficientes.append(coef)

    print()
    f_t = leer_expr("Ingresa la función del lado derecho f(t): ")

    print()
    print("Captura las condiciones iniciales en t = 0")
    condiciones = []
    for k in range(n):
        if k == 0:
            ci = leer_expr("y(0) = ")
        elif k == 1:
            ci = leer_expr("y'(0) = ")
        else:
            ci = leer_expr(f"y^({k})(0) = ")
        condiciones.append(ci)

    return n, coeficientes, f_t, condiciones

# ------------------------------------------------------------
# CONSTRUCCIÓN DE LA EDO
# ------------------------------------------------------------

def construir_lado_izquierdo(n, coeficientes, y):
    lhs = 0
    for i, coef in enumerate(coeficientes):
        orden = n - i
        lhs += coef * sp.diff(y, t, orden)
    return sp.expand(lhs)

# ------------------------------------------------------------
# TRANSFORMADA DE LAPLACE DE DERIVADAS
# ------------------------------------------------------------

def laplace_derivada(orden, Ysimbolo, condiciones):
    """
    L{y^(orden)} = s^orden*Y - s^(orden-1)y(0) - s^(orden-2)y'(0) - ... - y^(orden-1)(0)
    """
    termino = s**orden * Ysimbolo
    for j in range(orden):
        termino -= s**(orden - 1 - j) * condiciones[j]
    return sp.expand(termino)

def transformar_lado_izquierdo(n, coeficientes, condiciones):
    lhs_s = 0
    for i, coef in enumerate(coeficientes):
        orden = n - i
        lhs_s += coef * laplace_derivada(orden, Y, condiciones)
    return sp.expand(lhs_s)

# ------------------------------------------------------------
# FRACCIONES PARCIALES
# ------------------------------------------------------------

def fracciones_parciales_seguras(expr):
    try:
        return sp.apart(expr, s)
    except Exception:
        expr = sp.together(expr)
        try:
            return sp.apart(expr, s)
        except Exception:
            return expr

# ------------------------------------------------------------
# VERIFICACIÓN
# ------------------------------------------------------------

def calcular_derivadas(y_t, n):
    derivadas = [sp.simplify(y_t)]
    for k in range(1, n + 1):
        derivadas.append(sp.simplify(sp.diff(y_t, t, k)))
    return derivadas

def verificar_edo(n, coeficientes, derivadas, f_t):
    lhs = 0
    for i, coef in enumerate(coeficientes):
        orden = n - i
        lhs += coef * derivadas[orden]
    lhs = sp.simplify(sp.expand(lhs))
    rhs = sp.simplify(sp.expand(f_t))
    diferencia = sp.simplify(sp.trigsimp(sp.expand(lhs - rhs)))
    return lhs, rhs, diferencia

def verificar_condiciones(derivadas, condiciones):
    resultados = []
    for k, esperado in enumerate(condiciones):
        try:
            obtenido = sp.simplify(sp.limit(derivadas[k], t, 0, dir='+'))
        except Exception:
            obtenido = sp.simplify(derivadas[k].subs(t, 0))
        correcto = sp.simplify(obtenido - esperado) == 0
        resultados.append((k, obtenido, esperado, correcto))
    return resultados

# ------------------------------------------------------------
# FORMATEO DE TEXTO
# ------------------------------------------------------------

def nombre_derivada(orden):
    if orden == 0:
        return "y(t)"
    elif orden == 1:
        return "y'(t)"
    elif orden == 2:
        return "y''(t)"
    else:
        return f"y^({orden})(t)"

def nombre_ci(orden):
    if orden == 0:
        return "y(0)"
    elif orden == 1:
        return "y'(0)"
    else:
        return f"y^({orden})(0)"

# ------------------------------------------------------------
# RESOLUCIÓN PRINCIPAL
# ------------------------------------------------------------

def resolver():
    n, coeficientes, f_t, condiciones = capturar_datos()

    y = sp.Function('y')(t)

    encabezado("DATOS DEL PROBLEMA")

    lhs_original = construir_lado_izquierdo(n, coeficientes, y)
    mostrar_eq("Ecuación diferencial ingresada:", lhs_original, f_t)

    print("Condiciones iniciales registradas:")
    for k, ci in enumerate(condiciones):
        print(f"  {nombre_ci(k)} = {sp.pretty(ci, use_unicode=True)}")
    print()

    # Paso 1
    subtitulo("PASO 1. Aplicación de la Transformada de Laplace")

    print("Se transforma cada término de la ecuación diferencial al dominio s.")
    print("Para las derivadas se usa la fórmula general con condiciones iniciales.")
    print()

    lhs_s = transformar_lado_izquierdo(n, coeficientes, condiciones)
    try:
        F_s = sp.laplace_transform(f_t, t, s, noconds=True)
    except Exception:
        F_s = sp.laplace_transform(f_t, t, s)[0]
    F_s = sp.simplify(F_s)

    mostrar_eq("Ecuación transformada en el dominio s:", lhs_s, F_s)

    # Paso 2
    subtitulo("PASO 2. Sustitución de condiciones iniciales")

    print("La ecuación anterior ya queda expresada con las condiciones iniciales sustituidas.")
    print("Esta es la ecuación algebraica que se resolverá para Y(s).")
    print()

    mostrar_eq("Ecuación algebraica resultante:", lhs_s, F_s)

    # Paso 3
    subtitulo("PASO 3. Despeje algebraico de Y(s)")

    solucion_Y = sp.solve(sp.Eq(lhs_s, F_s), Y)
    if not solucion_Y:
        print("No fue posible despejar Y(s). Revisa los datos de entrada.")
        return

    Y_s = sp.simplify(solucion_Y[0])
    mostrar_expr("Expresión obtenida para Y(s):", Y_s)

    # Paso 4
    subtitulo("PASO 4. Descomposición en fracciones parciales")

    Y_s_apart = fracciones_parciales_seguras(Y_s)
    mostrar_expr("Y(s) reescrita para facilitar la inversa de Laplace:", Y_s_apart)

    # Paso 5
    subtitulo("PASO 5. Transformada inversa de Laplace")

    try:
        y_t = sp.inverse_laplace_transform(Y_s_apart, s, t)
    except Exception:
        y_t = sp.inverse_laplace_transform(Y_s, s, t)

    mostrar_expr("Solución obtenida antes de simplificar:", y_t)

    # Paso 6
    subtitulo("PASO 6. Simplificación de la solución")

    y_t_simplificada = sp.simplify(sp.expand(y_t))
    mostrar_expr("Solución final simplificada y(t):", y_t_simplificada)

    # Paso 7
    subtitulo("PASO 7. Cálculo de derivadas necesarias")

    derivadas = calcular_derivadas(y_t_simplificada, n)
    for k in range(n + 1):
        mostrar_expr(f"{nombre_derivada(k)} =", derivadas[k])

    # Paso 8
    subtitulo("PASO 8. Sustitución en la ecuación original")

    lhs_verif, rhs_verif, diferencia = verificar_edo(n, coeficientes, derivadas, f_t)

    mostrar_expr("Lado izquierdo al sustituir y(t) y sus derivadas:", lhs_verif)
    mostrar_expr("Lado derecho original f(t):", rhs_verif)
    mostrar_expr("Diferencia Lado izquierdo - Lado derecho:", diferencia)

    # Paso 9
    subtitulo("PASO 9. Verificación de condiciones iniciales")

    resultados_ci = verificar_condiciones(derivadas, condiciones)
    for k, obtenido, esperado, correcto in resultados_ci:
        print(f"{nombre_ci(k)}")
        print(f"  valor calculado : {sp.pretty(obtenido, use_unicode=True)}")
        print(f"  valor esperado  : {sp.pretty(esperado, use_unicode=True)}")
        print(f"  coincidencia    : {'Sí' if correcto else 'No'}")
        print()

    # Paso 10
    subtitulo("PASO 10. Conclusión final")

    edo_correcta = (sp.simplify(diferencia) == 0)
    ci_correctas = all(x[3] for x in resultados_ci)

    if edo_correcta and ci_correctas:
        print("Resultado de la revisión:")
        print("La solución encontrada satisface la ecuación diferencial")
        print("y también cumple con todas las condiciones iniciales.")
        print()
        mostrar_expr("Respuesta final:", y_t_simplificada)
    elif ci_correctas and not edo_correcta:
        print("Las condiciones iniciales sí coinciden,")
        print("pero la simplificación simbólica no logró reducir la verificación a cero.")
        print("Conviene revisar manualmente la expresión mostrada en la diferencia.")
        print()
        mostrar_expr("Posible solución:", y_t_simplificada)
    else:
        print("La revisión no fue completamente satisfactoria.")
        print("Se recomienda verificar la captura de datos o revisar manualmente el caso.")
        print()
        mostrar_expr("Expresión obtenida:", y_t_simplificada)

    encabezado("FIN DEL PROCEDIMIENTO")

# ------------------------------------------------------------
# PUNTO DE ENTRADA
# ------------------------------------------------------------

if __name__ == "__main__":
    try:
        resolver()
    except KeyboardInterrupt:
        print("\nEjecución interrumpida por el usuario.")