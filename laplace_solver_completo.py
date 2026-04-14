# =============================================================================
# laplace_solver_completo.py
# Solución PASO A PASO de EDO Lineales de coeficientes constantes
# mediante Transformada de Laplace — SymPy
#
# Universidad Tecnológica de San Juan del Río — Marzo 2026
#
# CÓMO EJECUTAR:
#   1. Instala SymPy si no lo tienes:
#         pip install sympy
#   2. Ejecuta el script:
#         python laplace_solver_completo.py
#   3. Sigue las instrucciones en pantalla.
#      Puedes elegir un EJEMPLO PREDEFINIDO (opción recomendada para probar)
#      o ingresar tu propia EDO manualmente.
#
# FORMATO DE EXPRESIONES (usa sintaxis Python/SymPy):
#   Constante      →  5
#   Polinomio      →  3*t**2 + 2*t - 1
#   Exponencial    →  exp(-2*t)
#   Senoidal       →  sin(3*t)   /   cos(3*t)
#   Escalón        →  Heaviside(t - 2)
#   Delta de Dirac →  DiracDelta(t - 1)
#   Combinaciones  →  3*exp(-t)*cos(2*t) + Heaviside(t-1)
#
# EJEMPLO DE EJECUCIÓN MANUAL:
#   EDO: y'' + 3y' + 2y = e^{-t}   y(0)=0, y'(0)=0
#   - Orden: 2
#   - Coef de y''  : 1
#   - Coef de y'   : 3
#   - Coef de y    : 2
#   - f(t)         : exp(-t)
#   - y(0)         : 0
#   - y'(0)        : 0
# =============================================================================

import sympy as sp

# ─────────────────────────────────────────────────────────────────────────────
# Símbolos globales
# ─────────────────────────────────────────────────────────────────────────────
t, s = sp.symbols('t s', real=True, positive=True)

# ─────────────────────────────────────────────────────────────────────────────
# Ejemplos predefinidos (para probar rápidamente)
# ─────────────────────────────────────────────────────────────────────────────
EJEMPLOS = {
    "1": {
        "desc": "y'' + 3y' + 2y = e^{-t},   y(0)=0, y'(0)=0  (Zill 7.2 #1)",
        "n": 2,
        "coefs": {2: 1, 1: 3, 0: 2},
        "f": sp.exp(-t),
        "conds": [sp.Integer(0), sp.Integer(0)],
    },
    "2": {
        "desc": "y'' - 4y = 0,   y(0)=1, y'(0)=0  (solución cosh)",
        "n": 2,
        "coefs": {2: 1, 1: 0, 0: -4},
        "f": sp.Integer(0),
        "conds": [sp.Integer(1), sp.Integer(0)],
    },
    "3": {
        "desc": "y'' + 4y = sin(2t),   y(0)=0, y'(0)=0  (resonancia)",
        "n": 2,
        "coefs": {2: 1, 1: 0, 0: 4},
        "f": sp.sin(2 * t),
        "conds": [sp.Integer(0), sp.Integer(0)],
    },
    "4": {
        "desc": "y' + 2y = 4,   y(0)=3  (EDO de primer orden)",
        "n": 1,
        "coefs": {1: 1, 0: 2},
        "f": sp.Integer(4),
        "conds": [sp.Integer(3)],
    },
    "5": {
        "desc": "y'' + 2y' + y = t*exp(-t),   y(0)=0, y'(0)=1",
        "n": 2,
        "coefs": {2: 1, 1: 2, 0: 1},
        "f": t * sp.exp(-t),
        "conds": [sp.Integer(0), sp.Integer(1)],
    },
    "6": {
        "desc": "y'' + y = Heaviside(t-π),   y(0)=0, y'(0)=0  (forzamiento escalón)",
        "n": 2,
        "coefs": {2: 1, 1: 0, 0: 1},
        "f": sp.Heaviside(t - sp.pi),
        "conds": [sp.Integer(0), sp.Integer(0)],
    },
}

# =============================================================================
# UTILIDADES DE IMPRESIÓN
# =============================================================================

def linea(char="─", n=70):
    print(char * n)

def titulo(texto):
    linea("═")
    print(f"  {texto}")
    linea("═")

def seccion(letra, texto):
    linea()
    print(f"  PASO {letra} — {texto}")
    linea()

def mostrar(descripcion, expr, latex_tambien=True):
    """Imprime expresión en forma legible y en LaTeX."""
    print(f"\n  ▶ {descripcion}")
    print(f"    {sp.pretty(expr, use_unicode=True)}")
    if latex_tambien:
        print(f"    LaTeX: ${sp.latex(expr)}$")

def mostrar_eq(descripcion, lhs, rhs, latex_tambien=True):
    """Imprime una ecuación lhs = rhs."""
    eq = sp.Eq(lhs, rhs)
    print(f"\n  ▶ {descripcion}")
    print(f"    {sp.pretty(eq, use_unicode=True)}")
    if latex_tambien:
        print(f"    LaTeX: ${sp.latex(eq)}$")

# =============================================================================
# MÓDULO 1 — Entrada de datos
# =============================================================================

def pedir_entero(mensaje, minimo=0):
    while True:
        try:
            v = int(input(mensaje))
            if v < minimo:
                raise ValueError
            return v
        except ValueError:
            print(f"  ✖ Ingresa un entero ≥ {minimo}.")

def pedir_expr(mensaje):
    """Lee expresión simbólica en t."""
    while True:
        texto = input(mensaje).strip()
        try:
            expr = sp.sympify(
                texto,
                locals={
                    "t": t, "s": s,
                    "Heaviside": sp.Heaviside,
                    "DiracDelta": sp.DiracDelta,
                    "exp": sp.exp, "sin": sp.sin, "cos": sp.cos,
                    "tan": sp.tan, "sqrt": sp.sqrt, "pi": sp.pi,
                    "E": sp.E,
                },
            )
            return expr
        except Exception as e:
            print(f"  ✖ Expresión no válida ({e}).")
            print("    Usa sintaxis Python: exp(-t), sin(2*t), Heaviside(t-1), etc.")

def elegir_modo():
    """Pide al usuario si desea ejemplo predefinido o entrada manual."""
    titulo("SOLVER DE EDO — TRANSFORMADA DE LAPLACE")
    print("\n  ¿Cómo deseas ingresar la EDO?")
    print("  [1-6] Ejemplo predefinido")
    print("  [M]   Ingreso manual")
    print()
    for k, ej in EJEMPLOS.items():
        print(f"  [{k}] {ej['desc']}")
    print()
    op = input("  Tu elección: ").strip().upper()
    return op

def obtener_datos():
    op = elegir_modo()

    if op in EJEMPLOS:
        ej = EJEMPLOS[op]
        print(f"\n  ✔ Ejemplo seleccionado: {ej['desc']}")
        return ej["n"], ej["coefs"], ej["f"], ej["conds"]

    # Modo manual
    print("\n  Forma general de la EDO:")
    print("  a_n·y^(n)(t) + ... + a_1·y'(t) + a_0·y(t) = f(t)\n")

    n = pedir_entero("  Orden n de la EDO (n ≥ 1): ", minimo=1)

    print(f"\n  Ingresa los {n + 1} coeficientes (de MAYOR a MENOR orden):")
    coefs_dict = {}
    for k in range(n, -1, -1):
        label = f"y''({k})" if k > 2 else {0: "y(t)", 1: "y'(t)", 2: "y''(t)"}.get(k, f"y^({k})(t)")
        c = pedir_expr(f"    Coeficiente de {label}: ")
        coefs_dict[k] = c

    print("\n  Función del lado derecho f(t):")
    f_expr = pedir_expr("    f(t) = ")

    print(f"\n  Condiciones iniciales en t = 0:")
    conds = []
    for k in range(n):
        label = "y(0)" if k == 0 else f"y^({k})(0)"
        c = pedir_expr(f"    {label} = ")
        conds.append(c)

    return n, coefs_dict, f_expr, conds

# =============================================================================
# MÓDULO 2 — Construcción de la EDO simbólica
# =============================================================================

def construir_edo(n, coefs_dict, y_func):
    """Devuelve la expresión simbólica del lado izquierdo de la EDO."""
    return sum(coefs_dict[k] * y_func.diff(t, k) for k in range(n, -1, -1))

# =============================================================================
# MÓDULO 3 — Transformada de Laplace (aplicación manual con condiciones)
# =============================================================================

def aplicar_laplace(n, coefs_dict, f_expr, conds):
    """
    Aplica L{} al LHS usando:
      L{y^(k)} = s^k·Y(s) - s^{k-1}·y(0) - s^{k-2}·y'(0) - ... - y^{k-1}(0)
    Devuelve (Lhs_en_s, F_s, Y_sym)
    """
    Y = sp.Function('Y')(s)

    # Transformada de f(t)
    F_s, _, _ = sp.laplace_transform(f_expr, t, s, noconds=True)
    F_s = sp.simplify(F_s)

    Lhs = sp.Integer(0)
    for k in range(n, -1, -1):
        a_k = coefs_dict[k]
        termino = s**k * Y
        for j in range(k):
            termino -= s**(k - 1 - j) * conds[j]
        Lhs += a_k * termino

    Lhs = sp.expand(Lhs)
    return Lhs, F_s, Y

# =============================================================================
# MÓDULO 4 — Despeje de Y(s)
# =============================================================================

def despejar_Y(Lhs, F_s, Y_sym):
    ecuacion = sp.Eq(Lhs, F_s)
    sol = sp.solve(ecuacion, Y_sym)
    if not sol:
        raise RuntimeError("No se pudo despejar Y(s). Revisa los coeficientes.")
    return sp.simplify(sol[0])

# =============================================================================
# MÓDULO 5 — Fracciones parciales e Inversa de Laplace
# =============================================================================

def fracciones_parciales(Y_expr):
    return sp.apart(Y_expr, s)

def transformada_inversa(Y_pf):
    y_raw = sp.inverse_laplace_transform(Y_pf, s, t)
    return sp.simplify(y_raw)

# =============================================================================
# MÓDULO 6 — Verificación completa
# =============================================================================

def verificar(n, coefs_dict, y_sol, f_expr, conds):
    """
    1) Sustituye y(t) en la EDO y comprueba que LHS - f(t) = 0
    2) Verifica cada condición inicial
    Devuelve (bool_edo, bool_conds, diferencia, lista_errores_ci)
    """
    # Calcular derivadas
    derivadas = [y_sol]
    for _ in range(n):
        derivadas.append(sp.diff(derivadas[-1], t))

    # Verificar EDO
    lhs_eval = sum(coefs_dict[k] * derivadas[k] for k in range(n + 1))
    diferencia = sp.simplify(sp.trigsimp(lhs_eval - f_expr))
    ok_edo = (diferencia == sp.Integer(0))

    # Verificar condiciones iniciales
    errores_ci = []
    for k in range(n):
        val = sp.limit(derivadas[k], t, 0, "+")
        err = sp.simplify(val - conds[k])
        errores_ci.append((k, val, conds[k], err == sp.Integer(0)))

    ok_conds = all(ok for _, _, _, ok in errores_ci)
    return ok_edo, ok_conds, diferencia, errores_ci

# =============================================================================
# MÓDULO 7 — Resumen LaTeX
# =============================================================================

def imprimir_latex_resumen(edo_eq, Y_expr, Y_pf, y_t, n, coefs_dict, conds, f_expr):
    linea("═")
    print("  RESUMEN — Código LaTeX listo para copiar en tu reporte")
    linea("═")

    # Construir cadena de condiciones iniciales
    ci_str = ""
    for k in range(n):
        label = "y(0)" if k == 0 else f"y^{{({k})}}(0)"
        ci_str += f"    {label} &= {sp.latex(conds[k])} \\\\\n"

    print(r"""
\begin{align*}
  \textbf{EDO:} &\quad """ + sp.latex(edo_eq) + r""" \\[6pt]
  \textbf{Cond. iniciales:} & \\
""" + ci_str + r"""  \\
  Y(s) &= """ + sp.latex(Y_expr) + r""" \\[4pt]
  Y(s)_{\text{fracc. parc.}} &= """ + sp.latex(Y_pf) + r""" \\[4pt]
  \Aboxed{y(t) &= """ + sp.latex(y_t) + r"""}
\end{align*}
""")

# =============================================================================
# MÓDULO 8 — Flujo principal
# =============================================================================

def resolver():
    # ── Obtener datos ──────────────────────────────────────────────────────
    n, coefs_dict, f_expr, conds = obtener_datos()

    y_func = sp.Function('y')(t)
    Y_sym  = sp.Function('Y')(s)

    # ══════════════════════════════════════════════════════════════════════
    # PASO A — EDO original y condiciones iniciales
    # ══════════════════════════════════════════════════════════════════════
    seccion("A", "EDO original y condiciones iniciales")

    lado_izq = construir_edo(n, coefs_dict, y_func)
    edo_eq   = sp.Eq(lado_izq, f_expr)

    print("\n  La EDO a resolver es:")
    mostrar_eq("EDO:", lado_izq, f_expr)

    print("\n  Condiciones iniciales:")
    for k in range(n):
        label = "y(0)" if k == 0 else f"y^({k})(0)"
        print(f"    {label} = {sp.pretty(conds[k], use_unicode=True)}"
              f"   →  LaTeX: ${sp.latex(conds[k])}$")

    input("\n  [Enter para continuar al Paso B]")

    # ══════════════════════════════════════════════════════════════════════
    # PASO B — Aplicar L{} a ambos lados
    # ══════════════════════════════════════════════════════════════════════
    seccion("B", "Aplicación de la Transformada de Laplace")

    print("""
  Se aplica L{} a ambos lados usando la propiedad de derivadas:

    L{y^(k)}(s) = s^k · Y(s) - s^(k-1)·y(0) - s^(k-2)·y'(0) - ... - y^(k-1)(0)
""")

    Lhs, F_s, Y_func = aplicar_laplace(n, coefs_dict, f_expr, conds)

    print("  Después de aplicar L{} al lado izquierdo:")
    mostrar("L{lado izquierdo} =", Lhs)
    print()
    print("  Transformada del lado derecho:")
    mostrar("L{f(t)} = F(s) =", F_s)

    input("\n  [Enter para continuar al Paso C]")

    # ══════════════════════════════════════════════════════════════════════
    # PASO C — Ecuación algebraica con condiciones sustituidas
    # ══════════════════════════════════════════════════════════════════════
    seccion("C", "Ecuación algebraica en s (condiciones ya sustituidas)")

    print("\n  Al sustituir las condiciones iniciales queda la ecuación algebraica:")
    mostrar_eq("Ecuación en Y(s):", Lhs, F_s)

    input("\n  [Enter para continuar al Paso D]")

    # ══════════════════════════════════════════════════════════════════════
    # PASO D — Despejar Y(s)
    # ══════════════════════════════════════════════════════════════════════
    seccion("D", "Despeje de Y(s)")

    try:
        Y_expr = despejar_Y(Lhs, F_s, Y_func)
    except RuntimeError as e:
        print(f"  ✖ Error: {e}")
        return

    print("\n  Despejando Y(s) de la ecuación algebraica:")
    mostrar("Y(s) =", Y_expr)

    input("\n  [Enter para continuar al Paso E]")

    # ══════════════════════════════════════════════════════════════════════
    # PASO E — Fracciones parciales
    # ══════════════════════════════════════════════════════════════════════
    seccion("E", "Descomposición en Fracciones Parciales  [apart()]")

    Y_pf = fracciones_parciales(Y_expr)
    print("\n  Descomponiendo Y(s) para poder aplicar la transformada inversa:")
    mostrar("Y(s) en fracciones parciales =", Y_pf)

    input("\n  [Enter para continuar al Paso F]")

    # ══════════════════════════════════════════════════════════════════════
    # PASO F — Transformada Inversa de Laplace
    # ══════════════════════════════════════════════════════════════════════
    seccion("F", "Transformada Inversa de Laplace  [inverse_laplace_transform()]")

    print("\n  Aplicando L^{-1}{} término a término (usando tablas/SymPy):")
    y_raw = sp.inverse_laplace_transform(Y_pf, s, t)
    mostrar("y(t) (antes de simplificar) =", y_raw)

    input("\n  [Enter para continuar al Paso G]")

    # ══════════════════════════════════════════════════════════════════════
    # PASO G — Solución final simplificada
    # ══════════════════════════════════════════════════════════════════════
    seccion("G", "Solución final simplificada  [simplify()]")

    y_t = sp.simplify(y_raw)
    print("\n  ┌─────────────────────────────────────────────────────────┐")
    mostrar("y(t) =", y_t)
    print("  └─────────────────────────────────────────────────────────┘")

    input("\n  [Enter para continuar al Paso H]")

    # ══════════════════════════════════════════════════════════════════════
    # PASO H — Cálculo de las n derivadas de y(t)
    # ══════════════════════════════════════════════════════════════════════
    seccion("H", f"Cálculo de las {n} derivada(s) de y(t)")

    derivadas = [y_t]
    for k in range(1, n + 1):
        dk = sp.simplify(sp.diff(derivadas[-1], t))
        derivadas.append(dk)
        label = "y'(t)" if k == 1 else f"y^({k})(t)"
        mostrar(f"{label} =", dk)

    input("\n  [Enter para continuar al Paso I]")

    # ══════════════════════════════════════════════════════════════════════
    # PASO I — Sustitución en la EDO original
    # ══════════════════════════════════════════════════════════════════════
    seccion("I", "Sustitución de y(t) y sus derivadas en la EDO original")

    lhs_eval = sum(coefs_dict[k] * derivadas[k] for k in range(n + 1))
    lhs_simplif = sp.simplify(sp.trigsimp(lhs_eval))

    print("\n  Sustituyendo en el lado izquierdo de la EDO:")
    mostrar("Lado izquierdo evaluado =", lhs_simplif)
    mostrar("f(t) =", f_expr)

    input("\n  [Enter para continuar al Paso J — VERIFICACIÓN]")

    # ══════════════════════════════════════════════════════════════════════
    # PASO J — Verificación completa (EDO + condiciones iniciales)
    # ══════════════════════════════════════════════════════════════════════
    seccion("J", "VERIFICACIÓN DE LA SOLUCIÓN")

    ok_edo, ok_conds, diferencia, errores_ci = verificar(
        n, coefs_dict, y_t, f_expr, conds
    )

    # ── Verificación de la EDO ──
    print("\n  ┌── Verificación de la EDO ──────────────────────────────┐")
    print(f"\n  LHS - f(t) = {sp.pretty(diferencia, use_unicode=True)}")
    if ok_edo:
        print("\n  ✔  LHS - f(t) = 0  →  y(t) SATISFACE la EDO  ✔")
    else:
        print("\n  ⚠  No se simplificó automáticamente a 0.")
        print("     Verifica manualmente si la expresión siguiente es 0:")
        print(f"     {sp.pretty(diferencia, use_unicode=True)}")
    print("  └──────────────────────────────────────────────────────────┘")

    # ── Verificación de condiciones iniciales ──
    print("\n  ┌── Verificación de condiciones iniciales ───────────────┐")
    for k, val_ci, cond_k, ok_k in errores_ci:
        label = "y(0)" if k == 0 else f"y^({k})(0)"
        estado = "✔" if ok_k else "✖"
        print(f"\n  {estado}  {label}:")
        print(f"      Valor calculado : {sp.pretty(sp.simplify(val_ci), use_unicode=True)}")
        print(f"      Valor requerido : {sp.pretty(cond_k, use_unicode=True)}")
    print("  └──────────────────────────────────────────────────────────┘")

    # ── Veredicto final ──
    print()
    if ok_edo and ok_conds:
        linea("*")
        print("  *** VERIFICACIÓN COMPLETA EXITOSA ***")
        print("  y(t) satisface tanto la EDO como todas las condiciones iniciales.")
        linea("*")
    elif ok_conds and not ok_edo:
        linea("-")
        print("  ⚠  Condiciones iniciales OK, pero la EDO no simplificó a 0 automáticamente.")
        print("     Prueba verificar manualmente (puede ser un límite de simplify).")
        linea("-")
    else:
        linea("-")
        print("  ✖  Verificación incompleta. Revisa los datos de entrada.")
        linea("-")

    input("\n  [Enter para ver el resumen LaTeX]")

    # ══════════════════════════════════════════════════════════════════════
    # RESUMEN LaTeX
    # ══════════════════════════════════════════════════════════════════════
    imprimir_latex_resumen(edo_eq, Y_expr, Y_pf, y_t, n, coefs_dict, conds, f_expr)

    linea("═")
    print("  FIN DE LA EJECUCIÓN — Puedes copiar el bloque LaTeX de arriba.")
    linea("═")
    print()


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================
if __name__ == "__main__":
    try:
        resolver()
    except KeyboardInterrupt:
        print("\n\n  Ejecución interrumpida por el usuario.")