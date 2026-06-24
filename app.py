"""
=====================================================================
 Estadísticas de Asistencia a Citas
 ConfiguroWeb · 2026 · Python real en el navegador (PyScript)
=====================================================================
"""
from pyscript import document, window
from js import localStorage
import json
import math

APP_CLAVE = "python_estadisticas_asistencia_datos"
VERSION = "1.0.0"


# =====================================================================
#  Lógica de negocio
# =====================================================================
class Calculadora:
    """Modelo de cálculo de Estadísticas de Asistencia a Citas."""

    def __init__(self, total, asistieron, cancelaron):
        self.total = float(total)
        self.asistieron = float(asistieron)
        self.cancelaron = float(cancelaron)

    def calcular(self):
        """Ejecuta el cálculo principal y devuelve un dict de resultados."""

        no_show = self.total - self.asistieron - self.cancelaron
        if self.total == 0:
            return {"error": "El total no puede ser 0."}
        tasa_asist = self.asistieron / self.total * 100
        tasa_no = no_show / self.total * 100
        tasa_cancel = self.cancelaron / self.total * 100
        return {"no_show": no_show, "asist": tasa_asist, "no_show_pct": tasa_no, "cancel_pct": tasa_cancel}


    def diagnostico(self, resultados):
        """Texto explicativo del resultado."""

        if resultados["no_show_pct"] > 20:
            return "⚠️ Alto índice de no-show. Implementa recordatorios automáticos."
        return "✅ Índice de asistencia saludable."



# =====================================================================
#  Formateadores
# =====================================================================
def fmt_moneda(v):
    if v is None:
        return "—"
    if math.isinf(v):
        return "∞"
    return f"${v:,.0f}"

def fmt_num(v):
    if v is None:
        return "—"
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return f"{v:,}"

def fmt_pct(v):
    if v is None:
        return "—"
    return f"{v:.1f}%"


# =====================================================================
#  Persistencia localStorage
# =====================================================================
def cargar_guardado():
    try:
        raw = localStorage.getItem(APP_CLAVE)
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    return None

def guardar_ls(datos):
    try:
        localStorage.setItem(APP_CLAVE, json.dumps(datos))
        return True
    except Exception:
        return False


# =====================================================================
#  UI helpers
# =====================================================================
def input_float(eid):
    el = document.querySelector(f"#{eid}")
    if not el or not el.value:
        return 0.0
    try:
        return float(el.value)
    except (ValueError, TypeError):
        return 0.0

def mostrar(html, clase=""):
    caja = document.querySelector("#resultado")
    caja.innerHTML = html
    caja.classList.remove("hidden", "is-error", "is-success")
    if clase:
        caja.classList.add(clase)


# =====================================================================
#  Handlers
# =====================================================================
def calcular_handler(event=None):
    """Lee inputs, instancia, calcula y muestra."""

    c = Calculadora(input_float("total"), input_float("asistieron"), input_float("cancelaron"))
    r = c.calcular()
    if "error" in r:
        mostrar(f'❌ {r["error"]}', clase="is-error"); return
    html = f"""
      <div class="result-value">📊 Asistencia: {fmt_pct(r["asist"])}</div>
      <p class="result-detail">No-show: <strong>{fmt_num(r["no_show"])} ({fmt_pct(r["no_show_pct"])})</strong></p>
      <p class="result-detail">Cancelaciones: <strong>{fmt_pct(r["cancel_pct"])}</strong></p>
      <p class="result-detail">{c.diagnostico(r)}</p>
    """
    mostrar(html, clase="is-success")



def guardar_datos(event=None):
    datos = {
            "total": input_float("total"),
            "asistieron": input_float("asistieron"),
            "cancelaron": input_float("cancelaron"),
        "version": VERSION,
    }
    ok = guardar_ls(datos)
    if ok:
        mostrar("💾 Datos guardados en este navegador.", clase="is-success")
    else:
        mostrar("❌ No se pudieron guardar los datos.", clase="is-error")


def cargar_al_inicio():
    datos = cargar_guardado()
    if not datos:
        return
    try:
        if "total" in datos:
            document.querySelector("#total").value = datos["total"]
        if "asistieron" in datos:
            document.querySelector("#asistieron").value = datos["asistieron"]
        if "cancelaron" in datos:
            document.querySelector("#cancelaron").value = datos["cancelaron"]
        aviso = document.querySelector("#resultado")
        aviso.innerHTML = "📂 Datos cargados. Pulsa <em>Calcular</em>."
        aviso.classList.remove("hidden")
    except Exception:
        pass


def inicializar():
    cargar_al_inicio()
    window.dispatchEvent(window.Event.new("py:ready"))

inicializar()
