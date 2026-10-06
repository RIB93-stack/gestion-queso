import flet as ft
import sqlite3
import csv
import os
from datetime import datetime, timedelta

# Ruta escribible compatible con Android y PC
def _ruta_escribible(nombre):
    # En Android, el HOME apunta a un directorio privado escribible de la app.
    # En PC, expanduser("~") apunta a la carpeta del usuario.
    base = os.path.expanduser("~")
    return os.path.join(base, nombre)

DB = _ruta_escribible("queso_app.db")

# ================== BASE DE DATOS ==================
def cx(): return sqlite3.connect(DB)

def init_db():
    c = cx()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS produccion(
        id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT,
        libras REAL, precio REAL, total REAL);
    CREATE TABLE IF NOT EXISTS distribuidores(
        id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE,
        activo INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS prov_leche(
        id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE,
        activo INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS trabajadores(
        id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE,
        activo INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS ventas(
        id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT,
        distribuidor_id INTEGER, libras REAL, precio REAL, total REAL);
    CREATE TABLE IF NOT EXISTS compras_leche(
        id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT,
        prov_id INTEGER, litros REAL, precio REAL, total REAL);
    CREATE TABLE IF NOT EXISTS trabajos(
        id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT,
        trabajador_id INTEGER, descripcion TEXT, monto REAL);
    CREATE TABLE IF NOT EXISTS pagos_recibidos(
        id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT,
        distribuidor_id INTEGER, monto REAL);
    CREATE TABLE IF NOT EXISTS pagos_leche(
        id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT,
        prov_id INTEGER, monto REAL);
    CREATE TABLE IF NOT EXISTS pagos_trabajadores(
        id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT,
        trabajador_id INTEGER, monto REAL);
    """)
    c.commit(); c.close()

# ---------- FECHAS ----------
def parse_fecha(f):
    try: return datetime.strptime(f.strip(), "%d/%m/%Y").date()
    except: return None

def hoy_str(): return datetime.now().strftime("%d/%m/%Y")

def rango(periodo):
    h = datetime.now().date()
    if periodo == "hoy":     return h, h
    if periodo == "semana":  return h - timedelta(days=7), h
    if periodo == "mes":     return h - timedelta(days=30), h
    if periodo == "año":     return h - timedelta(days=365), h
    return None, None

def filtrar(lista, idx, periodo):
    if periodo == "todo": return lista
    d1, d2 = rango(periodo)
    if not d1: return lista
    return [r for r in lista if parse_fecha(r[idx]) and d1 <= parse_fecha(r[idx]) <= d2]

def filtrar_custom(lista, idx, d1, d2):
    return [r for r in lista if parse_fecha(r[idx]) and d1 <= parse_fecha(r[idx]) <= d2]

# ---- DISTRIBUIDORES ----
def get_dist(a=True):
    c = cx(); q = "SELECT id,nombre,activo FROM distribuidores"
    if a: q += " WHERE activo=1"
    q += " ORDER BY nombre"; r = c.execute(q).fetchall(); c.close(); return r

def add_dist(n):
    try:
        c = cx(); c.execute("INSERT INTO distribuidores(nombre) VALUES(?)", (n,))
        c.commit(); c.close(); return True, "OK"
    except sqlite3.IntegrityError: return False, "Ya existe"

def upd_dist(i, n):
    c = cx(); c.execute("UPDATE distribuidores SET nombre=? WHERE id=?", (n, i))
    c.commit(); c.close()

def tog_dist(i, a):
    c = cx(); c.execute("UPDATE distribuidores SET activo=? WHERE id=?", (a, i))
    c.commit(); c.close()

# ---- PROVEEDORES LECHE ----
def get_leche(a=True):
    c = cx(); q = "SELECT id,nombre,activo FROM prov_leche"
    if a: q += " WHERE activo=1"
    q += " ORDER BY nombre"; r = c.execute(q).fetchall(); c.close(); return r

def add_leche(n):
    try:
        c = cx(); c.execute("INSERT INTO prov_leche(nombre) VALUES(?)", (n,))
        c.commit(); c.close(); return True, "OK"
    except sqlite3.IntegrityError: return False, "Ya existe"

def upd_leche(i, n):
    c = cx(); c.execute("UPDATE prov_leche SET nombre=? WHERE id=?", (n, i))
    c.commit(); c.close()

def tog_leche(i, a):
    c = cx(); c.execute("UPDATE prov_leche SET activo=? WHERE id=?", (a, i))
    c.commit(); c.close()

# ---- TRABAJADORES ----
def get_trab(a=True):
    c = cx(); q = "SELECT id,nombre,activo FROM trabajadores"
    if a: q += " WHERE activo=1"
    q += " ORDER BY nombre"; r = c.execute(q).fetchall(); c.close(); return r

def add_trab(n):
    try:
        c = cx(); c.execute("INSERT INTO trabajadores(nombre) VALUES(?)", (n,))
        c.commit(); c.close(); return True, "OK"
    except sqlite3.IntegrityError: return False, "Ya existe"

def upd_trab(i, n):
    c = cx(); c.execute("UPDATE trabajadores SET nombre=? WHERE id=?", (n, i))
    c.commit(); c.close()

def tog_trab(i, a):
    c = cx(); c.execute("UPDATE trabajadores SET activo=? WHERE id=?", (a, i))
    c.commit(); c.close()

# ---- PRODUCCIÓN ----
def add_prod(f, l, p):
    c = cx(); c.execute("INSERT INTO produccion(fecha,libras,precio,total) VALUES(?,?,?,?)",
                       (f, l, p, l*p)); c.commit(); c.close()

def upd_prod(i, f, l, p):
    c = cx(); c.execute("UPDATE produccion SET fecha=?,libras=?,precio=?,total=? WHERE id=?",
                       (f, l, p, l*p, i)); c.commit(); c.close()

def get_prod():
    c = cx(); r = c.execute("SELECT id,fecha,libras,precio,total FROM produccion ORDER BY id DESC LIMIT 500").fetchall()
    c.close(); return r

def del_prod(i):
    c = cx(); c.execute("DELETE FROM produccion WHERE id=?", (i,)); c.commit(); c.close()

# ---- VENTAS ----
def add_venta(f, d, l, p):
    c = cx(); c.execute("INSERT INTO ventas(fecha,distribuidor_id,libras,precio,total) VALUES(?,?,?,?,?)",
                       (f, d, l, p, l*p)); c.commit(); c.close()

def upd_venta(i, f, d, l, p):
    c = cx(); c.execute("UPDATE ventas SET fecha=?,distribuidor_id=?,libras=?,precio=?,total=? WHERE id=?",
                       (f, d, l, p, l*p, i)); c.commit(); c.close()

def get_ventas():
    c = cx()
    r = c.execute("""SELECT v.id, v.fecha, d.nombre, v.libras, v.precio, v.total, v.distribuidor_id
        FROM ventas v JOIN distribuidores d ON d.id=v.distribuidor_id
        ORDER BY v.id DESC LIMIT 500""").fetchall()
    c.close(); return r

def del_venta(i):
    c = cx(); c.execute("DELETE FROM ventas WHERE id=?", (i,)); c.commit(); c.close()

# ---- COMPRAS LECHE ----
def add_compra_l(f, p, l, pr):
    c = cx(); c.execute("INSERT INTO compras_leche(fecha,prov_id,litros,precio,total) VALUES(?,?,?,?,?)",
                       (f, p, l, pr, l*pr)); c.commit(); c.close()

def upd_compra_l(i, f, p, l, pr):
    c = cx(); c.execute("UPDATE compras_leche SET fecha=?,prov_id=?,litros=?,precio=?,total=? WHERE id=?",
                       (f, p, l, pr, l*pr, i)); c.commit(); c.close()

def get_compras_l():
    c = cx()
    r = c.execute("""SELECT c.id, c.fecha, p.nombre, c.litros, c.precio, c.total, c.prov_id
        FROM compras_leche c JOIN prov_leche p ON p.id=c.prov_id
        ORDER BY c.id DESC LIMIT 500""").fetchall()
    c.close(); return r

def del_compra_l(i):
    c = cx(); c.execute("DELETE FROM compras_leche WHERE id=?", (i,)); c.commit(); c.close()

# ---- TRABAJOS ----
def add_trabajo(f, t, desc, m):
    c = cx(); c.execute("INSERT INTO trabajos(fecha,trabajador_id,descripcion,monto) VALUES(?,?,?,?)",
                       (f, t, desc, m)); c.commit(); c.close()

def upd_trabajo(i, f, t, desc, m):
    c = cx(); c.execute("UPDATE trabajos SET fecha=?,trabajador_id=?,descripcion=?,monto=? WHERE id=?",
                       (f, t, desc, m, i)); c.commit(); c.close()

def get_trabajos():
    c = cx()
    r = c.execute("""SELECT t.id, t.fecha, w.nombre, t.descripcion, t.monto, t.trabajador_id
        FROM trabajos t JOIN trabajadores w ON w.id=t.trabajador_id
        ORDER BY t.id DESC LIMIT 500""").fetchall()
    c.close(); return r

def del_trabajo(i):
    c = cx(); c.execute("DELETE FROM trabajos WHERE id=?", (i,)); c.commit(); c.close()

# ---- PAGOS ----
def add_pago_rec(f, d, m):
    c = cx(); c.execute("INSERT INTO pagos_recibidos(fecha,distribuidor_id,monto) VALUES(?,?,?)", (f, d, m))
    c.commit(); c.close()

def upd_pago_rec(i, f, d, m):
    c = cx(); c.execute("UPDATE pagos_recibidos SET fecha=?,distribuidor_id=?,monto=? WHERE id=?",
                       (f, d, m, i)); c.commit(); c.close()

def del_pago_rec(i):
    c = cx(); c.execute("DELETE FROM pagos_recibidos WHERE id=?", (i,)); c.commit(); c.close()

def get_pagos_rec():
    c = cx()
    r = c.execute("""SELECT p.id, p.fecha, d.nombre, p.monto, p.distribuidor_id FROM pagos_recibidos p
        JOIN distribuidores d ON d.id=p.distribuidor_id ORDER BY p.id DESC LIMIT 500""").fetchall()
    c.close(); return r

def add_pago_l(f, p, m):
    c = cx(); c.execute("INSERT INTO pagos_leche(fecha,prov_id,monto) VALUES(?,?,?)", (f, p, m))
    c.commit(); c.close()

def upd_pago_l(i, f, p, m):
    c = cx(); c.execute("UPDATE pagos_leche SET fecha=?,prov_id=?,monto=? WHERE id=?",
                       (f, p, m, i)); c.commit(); c.close()

def del_pago_l(i):
    c = cx(); c.execute("DELETE FROM pagos_leche WHERE id=?", (i,)); c.commit(); c.close()

def get_pagos_l():
    c = cx()
    r = c.execute("""SELECT p.id, p.fecha, pr.nombre, p.monto, p.prov_id FROM pagos_leche p
        JOIN prov_leche pr ON pr.id=p.prov_id ORDER BY p.id DESC LIMIT 500""").fetchall()
    c.close(); return r

def add_pago_trab(f, t, m):
    c = cx(); c.execute("INSERT INTO pagos_trabajadores(fecha,trabajador_id,monto) VALUES(?,?,?)", (f, t, m))
    c.commit(); c.close()

def upd_pago_trab(i, f, t, m):
    c = cx(); c.execute("UPDATE pagos_trabajadores SET fecha=?,trabajador_id=?,monto=? WHERE id=?",
                       (f, t, m, i)); c.commit(); c.close()

def del_pago_trab(i):
    c = cx(); c.execute("DELETE FROM pagos_trabajadores WHERE id=?", (i,)); c.commit(); c.close()

def get_pagos_trab():
    c = cx()
    r = c.execute("""SELECT p.id, p.fecha, w.nombre, p.monto, p.trabajador_id FROM pagos_trabajadores p
        JOIN trabajadores w ON w.id=p.trabajador_id ORDER BY p.id DESC LIMIT 500""").fetchall()
    c.close(); return r

# ---- SALDOS ----
def saldo_dist(d):
    c = cx()
    v = c.execute("SELECT COALESCE(SUM(total),0) FROM ventas WHERE distribuidor_id=?", (d,)).fetchone()[0]
    p = c.execute("SELECT COALESCE(SUM(monto),0) FROM pagos_recibidos WHERE distribuidor_id=?", (d,)).fetchone()[0]
    c.close(); return v - p

def saldo_leche(p):
    c = cx()
    co = c.execute("SELECT COALESCE(SUM(total),0) FROM compras_leche WHERE prov_id=?", (p,)).fetchone()[0]
    pg = c.execute("SELECT COALESCE(SUM(monto),0) FROM pagos_leche WHERE prov_id=?", (p,)).fetchone()[0]
    c.close(); return co - pg

def saldo_trab(t):
    c = cx()
    tj = c.execute("SELECT COALESCE(SUM(monto),0) FROM trabajos WHERE trabajador_id=?", (t,)).fetchone()[0]
    pg = c.execute("SELECT COALESCE(SUM(monto),0) FROM pagos_trabajadores WHERE trabajador_id=?", (t,)).fetchone()[0]
    c.close(); return tj - pg

def stats():
    c = cx()
    pl = c.execute("SELECT COALESCE(SUM(libras),0) FROM produccion").fetchone()[0]
    pv = c.execute("SELECT COALESCE(SUM(total),0) FROM produccion").fetchone()[0]
    v  = c.execute("SELECT COALESCE(SUM(total),0) FROM ventas").fetchone()[0]
    cl = c.execute("SELECT COALESCE(SUM(total),0) FROM compras_leche").fetchone()[0]
    tj = c.execute("SELECT COALESCE(SUM(monto),0) FROM trabajos").fetchone()[0]
    pr = c.execute("SELECT COALESCE(SUM(monto),0) FROM pagos_recibidos").fetchone()[0]
    pg_l = c.execute("SELECT COALESCE(SUM(monto),0) FROM pagos_leche").fetchone()[0]
    pg_t = c.execute("SELECT COALESCE(SUM(monto),0) FROM pagos_trabajadores").fetchone()[0]
    c.close()
    return {"prod_l":pl, "prod_v":pv, "ventas":v, "leche":cl, "trabajos":tj,
            "por_cobrar":v-pr, "debe_leche":cl-pg_l, "debe_trab":tj-pg_t,
            "ganancia":v-cl-tj}

# ================== EXPORTAR ==================
def exportar_csv(nombre, encabezados, filas):
    try:
        ruta = _ruta_escribible(nombre)
        with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f); w.writerow(encabezados); w.writerows(filas)
        return True, ruta
    except Exception as e:
        return False, str(e)

# ================== UI ==================
def main(page: ft.Page):
    page.title = "Gestión de Queso"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 12
    page.bgcolor = ft.colors.GREY_100

    init_db()

    estado = {"vista": 0, "periodo": "todo"}
    contenido = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=10)

    def snack(msg, color=ft.colors.GREEN_700):
        page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def titulo(t, ico=None):
        row = []
        if ico: row.append(ft.Icon(ico, size=22, color=ft.colors.BLUE_700))
        row.append(ft.Text(t, size=18, weight=ft.FontWeight.BOLD))
        return ft.Row(row)

    def tarjeta(t, v, color, ico):
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ico, color=color, size=22),
                        ft.Text(t, size=11, color=ft.colors.GREY_700)], spacing=6),
                ft.Text(v, size=17, weight=ft.FontWeight.BOLD, color=color)
            ], spacing=4),
            padding=12, border_radius=12, bgcolor=ft.colors.WHITE, expand=True)

    def cerrar_dialogo(e=None):
        page.dialog.open = False
        page.update()

    def confirmar(desc, accion):
        def eliminar(e):
            accion()
            page.dialog.open = False
            snack("Registro eliminado", ft.colors.ORANGE)

        page.dialog = ft.AlertDialog(
            title=ft.Text("⚠️ Eliminar registro"),
            content=ft.Text(f"¿Seguro que quieres eliminar:\n\n{desc}?\n\nEsta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.ElevatedButton("Eliminar", bgcolor=ft.colors.RED, color=ft.colors.WHITE, on_click=eliminar)
            ])
        page.dialog.open = True
        page.update()

    def dialogo_campos(titulo_d, campos, on_guardar):
        inputs = []
        for label, valor, tipo in campos:
            if tipo == "num":
                inputs.append(ft.TextField(label=label, value=str(valor) if valor else "",
                                           keyboard_type=ft.KeyboardType.NUMBER, dense=True))
            elif tipo == "dropdown":
                opts, val = valor
                inputs.append(ft.Dropdown(label=label,
                                          value=str(val) if val else None,
                                          options=[ft.dropdown.Option(str(k), v) for k, v in opts],
                                          dense=True))
            else:
                inputs.append(ft.TextField(label=label, value=str(valor) if valor else "", dense=True))

        def guardar(e):
            try:
                on_guardar(inputs)
                page.dialog.open = False
                page.update()
            except Exception as ex:
                snack(f"Error: {ex}", ft.colors.RED)

        page.dialog = ft.AlertDialog(
            title=ft.Text(f"✏️ {titulo_d}"),
            content=ft.Column(inputs, tight=True, spacing=10, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.ElevatedButton("Guardar", icon=ft.icons.SAVE, on_click=guardar)
            ])
        page.dialog.open = True
        page.update()

    def pedir_rango(on_ok):
        f1 = ft.TextField(label="Desde (dd/mm/aaaa)", dense=True)
        f2 = ft.TextField(label="Hasta (dd/mm/aaaa)", value=hoy_str(), dense=True)

        def aplicar(e):
            d1 = parse_fecha(f1.value); d2 = parse_fecha(f2.value)
            if not d1 or not d2:
                snack("Fecha inválida. Usa dd/mm/aaaa", ft.colors.RED); return
            if d1 > d2:
                snack("'Desde' no puede ser mayor que 'Hasta'", ft.colors.RED); return
            page.dialog.open = False
            page.update()
            on_ok(d1, d2)

        page.dialog = ft.AlertDialog(
            title=ft.Text("Rango personalizado"),
            content=ft.Column([f1, f2], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.ElevatedButton("Aplicar", on_click=aplicar)
            ])
        page.dialog.open = True
        page.update()

    def barra_filtro(on_change, on_export):
        dd = ft.Dropdown(
            label="Filtrar por fecha", dense=True, value=estado["periodo"], expand=True,
            options=[ft.dropdown.Option(k, v) for k, v in [
                ("todo", "📅 Todo"), ("hoy", "Hoy"), ("semana", "Últimos 7 días"),
                ("mes", "Últimos 30 días"), ("año", "Último año"),
                ("personalizado", "📆 Personalizado...")]])
        def cambio(e):
            if dd.value == "personalizado":
                pedir_rango(lambda d1, d2: (estado.update({"periodo": "custom"}), on_change()))
            else:
                estado["periodo"] = dd.value; on_change()
        dd.on_change = cambio
        return ft.Row([
            ft.Container(dd, expand=True),
            ft.IconButton(ft.icons.FILE_DOWNLOAD, icon_color=ft.colors.GREEN_700,
                          tooltip="Exportar a CSV", on_click=on_export)
        ], spacing=8)

    # ============ VISTA: INICIO ============
    def v_inicio():
        s = stats()
        ctrls = [
            titulo("Resumen general", ft.icons.DASHBOARD),
            ft.Row([
                tarjeta("Producción", f"{s['prod_l']:.1f} lb", ft.colors.BLUE, ft.icons.AGRICULTURE),
                tarjeta("Valor prod.", f"${s['prod_v']:.0f}", ft.colors.BLUE_700, ft.icons.ATTACH_MONEY),
            ], spacing=10),
            ft.Row([
                tarjeta("Ventas", f"${s['ventas']:.0f}", ft.colors.GREEN, ft.icons.SELL),
                tarjeta("Leche", f"${s['leche']:.0f}", ft.colors.ORANGE, ft.icons.WATER_DROP),
            ], spacing=10),
            ft.Row([
                tarjeta("Trabajos", f"${s['trabajos']:.0f}", ft.colors.BROWN, ft.icons.ENGINEERING),
                tarjeta("Ganancia", f"${s['ganancia']:.0f}",
                        ft.colors.GREEN_700 if s['ganancia'] >= 0 else ft.colors.RED,
                        ft.icons.TRENDING_UP),
            ], spacing=10),
            ft.Row([
                tarjeta("Te deben", f"${s['por_cobrar']:.0f}", ft.colors.RED, ft.icons.ACCOUNT_BALANCE_WALLET),
                tarjeta("Debes leche", f"${s['debe_leche']:.0f}", ft.colors.PURPLE, ft.icons.PAYMENT),
            ], spacing=10),
            tarjeta("Debes a trabajadores", f"${s['debe_trab']:.0f}", ft.colors.BROWN, ft.icons.ENGINEERING),
            ft.Divider(),
            titulo("Distribuidores (te deben)", ft.icons.PEOPLE),
        ]
        for d in get_dist():
            sd = saldo_dist(d[0])
            ctrls.append(ft.Container(content=ft.Row([
                ft.Text(d[1], expand=True, weight=ft.FontWeight.W_500),
                ft.Text(f"${sd:.0f}", color=ft.colors.RED if sd > 0 else ft.colors.GREEN,
                        weight=ft.FontWeight.BOLD)
            ]), padding=10, border_radius=8, bgcolor=ft.colors.WHITE))

        ctrls.append(ft.Divider())
        ctrls.append(titulo("Proveedores de leche (les debes)", ft.icons.WATER_DROP))
        for p in get_leche():
            sp = saldo_leche(p[0])
            ctrls.append(ft.Container(content=ft.Row([
                ft.Text(p[1], expand=True, weight=ft.FontWeight.W_500),
                ft.Text(f"${sp:.0f}", color=ft.colors.PURPLE if sp > 0 else ft.colors.GREEN,
                        weight=ft.FontWeight.BOLD)
            ]), padding=10, border_radius=8, bgcolor=ft.colors.WHITE))

        ctrls.append(ft.Divider())
        ctrls.append(titulo("Trabajadores (les debes)", ft.icons.ENGINEERING))
        for w in get_trab():
            sw = saldo_trab(w[0])
            ctrls.append(ft.Container(content=ft.Row([
                ft.Text(w[1], expand=True, weight=ft.FontWeight.W_500),
                ft.Text(f"${sw:.0f}", color=ft.colors.BROWN if sw > 0 else ft.colors.GREEN,
                        weight=ft.FontWeight.BOLD)
            ]), padding=10, border_radius=8, bgcolor=ft.colors.WHITE))
        return ctrls

    # ============ VISTA: PRODUCCIÓN ============
    def v_produccion():
        f_f = ft.TextField(label="Fecha", value=hoy_str(), dense=True)
        f_l = ft.TextField(label="Libras", keyboard_type=ft.KeyboardType.NUMBER, dense=True, expand=True)
        f_p = ft.TextField(label="Precio/lb", value="600", keyboard_type=ft.KeyboardType.NUMBER, dense=True, expand=True)
        f_t = ft.TextField(label="Valor estimado", read_only=True, dense=True)

        def calc(e=None):
            try: f_t.value = f"{float(f_l.value or 0)*float(f_p.value or 0):.0f}"
            except: f_t.value = "0"
            page.update()
        f_l.on_change = calc; f_p.on_change = calc

        lista = ft.Column(spacing=6)
        lbl = ft.Text("", weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700)

        def render(datos):
            lista.controls.clear()
            tl = sum(r[2] for r in datos); tv = sum(r[4] for r in datos)
            lbl.value = f"📊 {len(datos)} registros  |  {tl:.1f} lb  |  ${tv:,.0f}"
            for r in datos:
                def editar(e, reg=r):
                    def on_ok(inp):
                        if not parse_fecha(inp[0].value):
                            snack("Fecha inválida", ft.colors.RED); return
                        upd_prod(reg[0], inp[0].value, float(inp[1].value), float(inp[2].value))
                        snack("Actualizado"); refrescar()
                    dialogo_campos("Editar producción",
                                   [("Fecha", reg[1], "text"),
                                    ("Libras", reg[2], "num"),
                                    ("Precio/lb", reg[3], "num")], on_ok)
                def eliminar(e, reg=r):
                    confirmar(f"Producción del {reg[1]}\n{reg[2]:.1f} lb × ${reg[3]:.0f} = ${reg[4]:.0f}",
                              lambda: (del_prod(reg[0]), refrescar()))
                lista.controls.append(ft.Container(content=ft.Row([
                    ft.Column([
                        ft.Text(r[1], size=12, color=ft.colors.GREY_700),
                        ft.Text(f"{r[2]:.1f} lb × ${r[3]:.0f}", size=13)
                    ], spacing=0, expand=True),
                    ft.Text(f"${r[4]:.0f}", weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_700),
                    ft.IconButton(ft.icons.EDIT, icon_color=ft.colors.BLUE, icon_size=18, on_click=editar),
                    ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=ft.colors.RED, icon_size=18, on_click=eliminar)
                ]), padding=10, border_radius=8, bgcolor=ft.colors.WHITE))
            page.update()

        def refrescar():
            if estado["periodo"] == "custom":
                return
            render(filtrar(get_prod(), 1, estado["periodo"]))

        def guardar(e):
            if not f_l.value: snack("Ingresa las libras", ft.colors.RED); return
            if not parse_fecha(f_f.value): snack("Fecha inválida", ft.colors.RED); return
            add_prod(f_f.value, float(f_l.value), float(f_p.value))
            f_l.value = ""; f_t.value = ""
            snack("Guardado"); refrescar()

        def exportar(e):
            datos = filtrar(get_prod(), 1, estado["periodo"])
            filas = [(r[1], r[2], r[3], r[4]) for r in datos]
            ok, res = exportar_csv(f"produccion_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                   ["Fecha", "Libras", "Precio", "Total"], filas)
            snack(f"✔ {res}" if ok else f"Error: {res}",
                  ft.colors.GREEN_700 if ok else ft.colors.RED)

        ctrls = [
            titulo("Registrar producción", ft.icons.AGRICULTURE),
            ft.Container(content=ft.Column([
                f_f, ft.Row([f_l, f_p]), f_t,
                ft.ElevatedButton("Guardar producción", icon=ft.icons.SAVE, on_click=guardar,
                                  bgcolor=ft.colors.BLUE, color=ft.colors.WHITE)
            ], spacing=10), padding=14, border_radius=12, bgcolor=ft.colors.WHITE),
            ft.Divider(),
            titulo("Historial", ft.icons.HISTORY),
            barra_filtro(refrescar, exportar),
            lbl, lista
        ]
        refrescar()
        return ctrls

    # ============ VISTA: VENTAS ============
    def v_ventas():
        dists = get_dist()
        if not dists:
            return [titulo("Ventas", ft.icons.SELL),
                    ft.Text("Agrega distribuidores en 'Usuarios'.", italic=True, color=ft.colors.RED)]

        dd = ft.Dropdown(label="Distribuidor",
                         options=[ft.dropdown.Option(str(d[0]), d[1]) for d in dists], dense=True)
        f_f = ft.TextField(label="Fecha", value=hoy_str(), dense=True)
        f_l = ft.TextField(label="Libras", keyboard_type=ft.KeyboardType.NUMBER, dense=True, expand=True)
        f_p = ft.TextField(label="Precio/lb", value="600", keyboard_type=ft.KeyboardType.NUMBER, dense=True, expand=True)
        f_t = ft.TextField(label="Total", read_only=True, dense=True)

        def calc(e=None):
            try: f_t.value = f"{float(f_l.value or 0)*float(f_p.value or 0):.0f}"
            except: f_t.value = "0"
            page.update()
        f_l.on_change = calc; f_p.on_change = calc

        def guardar(e):
            if not dd.value or not f_l.value: snack("Completa los datos", ft.colors.RED); return
            if not parse_fecha(f_f.value): snack("Fecha inválida", ft.colors.RED); return
            add_venta(f_f.value, int(dd.value), float(f_l.value), float(f_p.value))
            snack("Venta registrada"); refrescar()

        dd2 = ft.Dropdown(label="Distribuidor que pagó",
                          options=[ft.dropdown.Option(str(d[0]), f"{d[1]} (debe ${saldo_dist(d[0]):.0f})")
                                   for d in dists], dense=True)
        f_fp = ft.TextField(label="Fecha", value=hoy_str(), dense=True, expand=True)
        f_m = ft.TextField(label="Monto", keyboard_type=ft.KeyboardType.NUMBER, dense=True, expand=True)

        def guardar_pago(e):
            if not dd2.value or not f_m.value: snack("Completa los datos", ft.colors.RED); return
            if not parse_fecha(f_fp.value): snack("Fecha inválida", ft.colors.RED); return
            add_pago_rec(f_fp.value, int(dd2.value), float(f_m.value))
            snack("Pago registrado"); refrescar()

        hist = ft.Column(spacing=6)
        hist_pagos = ft.Column(spacing=6)
        lbl = ft.Text("", weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_700)

        def refrescar():
            if estado["periodo"] == "custom": return
            datos = filtrar(get_ventas(), 1, estado["periodo"])
            hist.controls.clear()
            total = sum(r[5] for r in datos)
            lbl.value = f"📊 {len(datos)} ventas  |  ${total:,.0f}"
            for r in datos:
                def editar(e, reg=r):
                    opts = [(d[0], d[1]) for d in get_dist()]
                    def on_ok(inp):
                        if not parse_fecha(inp[0].value):
                            snack("Fecha inválida", ft.colors.RED); return
                        upd_venta(reg[0], inp[0].value, int(inp[1].value),
                                  float(inp[2].value), float(inp[3].value))
                        snack("Actualizado"); refrescar()
                    dialogo_campos("Editar venta",
                                   [("Fecha", reg[1], "text"),
                                    ("Distribuidor", (opts, reg[6]), "dropdown"),
                                    ("Libras", reg[3], "num"),
                                    ("Precio/lb", reg[4], "num")], on_ok)
                def eliminar(e, reg=r):
                    confirmar(f"Venta del {reg[1]} a {reg[2]}\n{reg[3]:.1f} lb = ${reg[5]:.0f}",
                              lambda: (del_venta(reg[0]), refrescar()))
                hist.controls.append(ft.Container(content=ft.Row([
                    ft.Column([
                        ft.Text(f"{r[1]} • {r[2]}", size=12, color=ft.colors.GREY_700),
                        ft.Text(f"{r[3]:.1f} lb × ${r[4]:.0f}", size=13)
                    ], spacing=0, expand=True),
                    ft.Text(f"${r[5]:.0f}", weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_700),
                    ft.IconButton(ft.icons.EDIT, icon_color=ft.colors.BLUE, icon_size=18, on_click=editar),
                    ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=ft.colors.RED, icon_size=18, on_click=eliminar)
                ]), padding=10, border_radius=8, bgcolor=ft.colors.WHITE))

            pagos = filtrar(get_pagos_rec(), 1, estado["periodo"])
            hist_pagos.controls.clear()
            for r in pagos:
                def editar_p(e, reg=r):
                    opts = [(d[0], d[1]) for d in get_dist()]
                    def on_ok(inp):
                        if not parse_fecha(inp[0].value):
                            snack("Fecha inválida", ft.colors.RED); return
                        upd_pago_rec(reg[0], inp[0].value, int(inp[1].value), float(inp[2].value))
                        snack("Actualizado"); refrescar()
                    dialogo_campos("Editar pago recibido",
                                   [("Fecha", reg[1], "text"),
                                    ("Distribuidor", (opts, reg[4]), "dropdown"),
                                    ("Monto", reg[3], "num")], on_ok)
                def eliminar_p(e, reg=r):
                    confirmar(f"Pago de {reg[2]} del {reg[1]}: ${reg[3]:.0f}",
                              lambda: (del_pago_rec(reg[0]), refrescar()))
                hist_pagos.controls.append(ft.Container(content=ft.Row([
                    ft.Column([
                        ft.Text(f"{r[1]} • {r[2]}", size=12, color=ft.colors.GREY_700),
                        ft.Text("Pago recibido", size=13, color=ft.colors.GREEN)
                    ], spacing=0, expand=True),
                    ft.Text(f"${r[3]:.0f}", weight=ft.FontWeight.BOLD, color=ft.colors.GREEN),
                    ft.IconButton(ft.icons.EDIT, icon_color=ft.colors.BLUE, icon_size=18, on_click=editar_p),
                    ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=ft.colors.RED, icon_size=18, on_click=eliminar_p)
                ]), padding=10, border_radius=8, bgcolor=ft.colors.GREEN_50))
            page.update()

        def exportar(e):
            datos = filtrar(get_ventas(), 1, estado["periodo"])
            filas = [(r[1], r[2], r[3], r[4], r[5]) for r in datos]
            ok, res = exportar_csv(f"ventas_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                   ["Fecha", "Distribuidor", "Libras", "Precio", "Total"], filas)
            snack(f"✔ {res}" if ok else f"Error: {res}",
                  ft.colors.GREEN_700 if ok else ft.colors.RED)

        ctrls = [
            titulo("Registrar venta", ft.icons.SELL),
            ft.Container(content=ft.Column([
                dd, f_f, ft.Row([f_l, f_p]), f_t,
                ft.ElevatedButton("Guardar venta", icon=ft.icons.SAVE, on_click=guardar,
                                  bgcolor=ft.colors.GREEN, color=ft.colors.WHITE)
            ], spacing=10), padding=14, border_radius=12, bgcolor=ft.colors.WHITE),
            titulo("Registrar pago recibido", ft.icons.PAYMENT),
            ft.Container(content=ft.Column([
                dd2, ft.Row([f_fp, f_m]),
                ft.ElevatedButton("Guardar pago", icon=ft.icons.SAVE, on_click=guardar_pago,
                                  bgcolor=ft.colors.BLUE, color=ft.colors.WHITE)
            ], spacing=10), padding=14, border_radius=12, bgcolor=ft.colors.WHITE),
            ft.Divider(),
            titulo("Historial de ventas", ft.icons.HISTORY),
            barra_filtro(refrescar, exportar),
            lbl, hist,
            titulo("Historial de pagos recibidos", ft.icons.PAYMENT),
            hist_pagos
        ]
        refrescar()
        return ctrls

    # ============ VISTA: LECHE ============
    def v_leche():
        provs = get_leche()
        if not provs:
            return [titulo("Compra de leche", ft.icons.WATER_DROP),
                    ft.Text("Agrega proveedores en 'Usuarios'.", italic=True, color=ft.colors.RED)]

        dd = ft.Dropdown(label="Proveedor de leche",
                         options=[ft.dropdown.Option(str(p[0]), p[1]) for p in provs], dense=True)
        f_f = ft.TextField(label="Fecha", value=hoy_str(), dense=True)
        f_l = ft.TextField(label="Litros", keyboard_type=ft.KeyboardType.NUMBER, dense=True, expand=True)
        f_p = ft.TextField(label="Precio/litro", keyboard_type=ft.KeyboardType.NUMBER, dense=True, expand=True)
        f_t = ft.TextField(label="Total", read_only=True, dense=True)

        def calc(e=None):
            try: f_t.value = f"{float(f_l.value or 0)*float(f_p.value or 0):.0f}"
            except: f_t.value = "0"
            page.update()
        f_l.on_change = calc; f_p.on_change = calc

        def guardar(e):
            if not dd.value or not f_l.value: snack("Completa los datos", ft.colors.RED); return
            if not parse_fecha(f_f.value): snack("Fecha inválida", ft.colors.RED); return
            add_compra_l(f_f.value, int(dd.value), float(f_l.value), float(f_p.value))
            snack("Compra registrada"); refrescar()

        dd2 = ft.Dropdown(label="Proveedor al que pagué",
                          options=[ft.dropdown.Option(str(p[0]), f"{p[1]} (debes ${saldo_leche(p[0]):.0f})")
                                   for p in provs], dense=True)
        f_fp = ft.TextField(label="Fecha", value=hoy_str(), dense=True, expand=True)
        f_m = ft.TextField(label="Monto", keyboard_type=ft.KeyboardType.NUMBER, dense=True, expand=True)

        def guardar_pago(e):
            if not dd2.value or not f_m.value: snack("Completa los datos", ft.colors.RED); return
            if not parse_fecha(f_fp.value): snack("Fecha inválida", ft.colors.RED); return
            add_pago_l(f_fp.value, int(dd2.value), float(f_m.value))
            snack("Pago registrado"); refrescar()

        hist = ft.Column(spacing=6)
        hist_pagos = ft.Column(spacing=6)
        lbl = ft.Text("", weight=ft.FontWeight.BOLD, color=ft.colors.ORANGE_700)

        def refrescar():
            if estado["periodo"] == "custom": return
            datos = filtrar(get_compras_l(), 1, estado["periodo"])
            hist.controls.clear()
            total = sum(r[5] for r in datos)
            lbl.value = f"📊 {len(datos)} compras  |  ${total:,.0f}"
            for r in datos:
                def editar(e, reg=r):
                    opts = [(p[0], p[1]) for p in get_leche()]
                    def on_ok(inp):
                        if not parse_fecha(inp[0].value):
                            snack("Fecha inválida", ft.colors.RED); return
                        upd_compra_l(reg[0], inp[0].value, int(inp[1].value),
                                     float(inp[2].value), float(inp[3].value))
                        snack("Actualizado"); refrescar()
                    dialogo_campos("Editar compra",
                                   [("Fecha", reg[1], "text"),
                                    ("Proveedor", (opts, reg[6]), "dropdown"),
                                    ("Litros", reg[3], "num"),
                                    ("Precio/litro", reg[4], "num")], on_ok)
                def eliminar(e, reg=r):
                    confirmar(f"Compra del {reg[1]} a {reg[2]}",
                              lambda: (del_compra_l(reg[0]), refrescar()))
                hist.controls.append(ft.Container(content=ft.Row([
                    ft.Column([
                        ft.Text(f"{r[1]} • {r[2]}", size=12, color=ft.colors.GREY_700),
                        ft.Text(f"{r[3]:.1f} L × ${r[4]:.0f}", size=13)
                    ], spacing=0, expand=True),
                    ft.Text(f"${r[5]:.0f}", weight=ft.FontWeight.BOLD, color=ft.colors.ORANGE_700),
                    ft.IconButton(ft.icons.EDIT, icon_color=ft.colors.BLUE, icon_size=18, on_click=editar),
                    ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=ft.colors.RED, icon_size=18, on_click=eliminar)
                ]), padding=10, border_radius=8, bgcolor=ft.colors.WHITE))

            pagos = filtrar(get_pagos_l(), 1, estado["periodo"])
            hist_pagos.controls.clear()
            for r in pagos:
                def editar_p(e, reg=r):
                    opts = [(p[0], p[1]) for p in get_leche()]
                    def on_ok(inp):
                        if not parse_fecha(inp[0].value):
                            snack("Fecha inválida", ft.colors.RED); return
                        upd_pago_l(reg[0], inp[0].value, int(inp[1].value), float(inp[2].value))
                        snack("Actualizado"); refrescar()
                    dialogo_campos("Editar pago",
                                   [("Fecha", reg[1], "text"),
                                    ("Proveedor", (opts, reg[4]), "dropdown"),
                                    ("Monto", reg[3], "num")], on_ok)
                def eliminar_p(e, reg=r):
                    confirmar(f"Pago a {reg[2]}: ${reg[3]:.0f}",
                              lambda: (del_pago_l(reg[0]), refrescar()))
                hist_pagos.controls.append(ft.Container(content=ft.Row([
                    ft.Column([
                        ft.Text(f"{r[1]} • {r[2]}", size=12, color=ft.colors.GREY_700),
                        ft.Text("Pago realizado", size=13, color=ft.colors.PURPLE)
                    ], spacing=0, expand=True),
                    ft.Text(f"${r[3]:.0f}", weight=ft.FontWeight.BOLD, color=ft.colors.PURPLE),
                    ft.IconButton(ft.icons.EDIT, icon_color=ft.colors.BLUE, icon_size=18, on_click=editar_p),
                    ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=ft.colors.RED, icon_size=18, on_click=eliminar_p)
                ]), padding=10, border_radius=8, bgcolor=ft.colors.PURPLE_50))
            page.update()

        def exportar(e):
            datos = filtrar(get_compras_l(), 1, estado["periodo"])
            filas = [(r[1], r[2], r[3], r[4], r[5]) for r in datos]
            ok, res = exportar_csv(f"leche_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                   ["Fecha", "Proveedor", "Litros", "Precio", "Total"], filas)
            snack(f"✔ {res}" if ok else f"Error: {res}",
                  ft.colors.GREEN_700 if ok else ft.colors.RED)

        ctrls = [
            titulo("Registrar compra de leche", ft.icons.WATER_DROP),
            ft.Container(content=ft.Column([
                dd, f_f, ft.Row([f_l, f_p]), f_t,
                ft.ElevatedButton("Guardar compra", icon=ft.icons.SAVE, on_click=guardar,
                                  bgcolor=ft.colors.ORANGE, color=ft.colors.WHITE)
            ], spacing=10), padding=14, border_radius=12, bgcolor=ft.colors.WHITE),
            titulo("Registrar pago al proveedor", ft.icons.PAYMENT),
            ft.Container(content=ft.Column([
                dd2, ft.Row([f_fp, f_m]),
                ft.ElevatedButton("Guardar pago", icon=ft.icons.SAVE, on_click=guardar_pago,
                                  bgcolor=ft.colors.PURPLE, color=ft.colors.WHITE)
            ], spacing=10), padding=14, border_radius=12, bgcolor=ft.colors.WHITE),
            ft.Divider(),
            titulo("Historial de compras", ft.icons.HISTORY),
            barra_filtro(refrescar, exportar),
            lbl, hist,
            titulo("Historial de pagos", ft.icons.PAYMENT),
            hist_pagos
        ]
        refrescar()
        return ctrls

    # ============ VISTA: TRABAJADORES ============
    def v_trabajadores():
        trabs = get_trab()
        if not trabs:
            return [titulo("Trabajadores", ft.icons.ENGINEERING),
                    ft.Text("Agrega trabajadores en 'Usuarios'.", italic=True, color=ft.colors.RED)]

        dd = ft.Dropdown(label="Trabajador",
                         options=[ft.dropdown.Option(str(t[0]), t[1]) for t in trabs], dense=True)
        f_f = ft.TextField(label="Fecha", value=hoy_str(), dense=True)
        f_d = ft.TextField(label="Descripción (ej: 50 quesos)", dense=True)
        f_m = ft.TextField(label="Monto a pagar", keyboard_type=ft.KeyboardType.NUMBER, dense=True)

        def guardar(e):
            if not dd.value or not f_m.value: snack("Completa los datos", ft.colors.RED); return
            if not parse_fecha(f_f.value): snack("Fecha inválida", ft.colors.RED); return
            add_trabajo(f_f.value, int(dd.value), f_d.value or "Trabajo", float(f_m.value))
            snack("Trabajo registrado"); refrescar()

        dd2 = ft.Dropdown(label="Trabajador al que pagué",
                          options=[ft.dropdown.Option(str(t[0]), f"{t[1]} (debes ${saldo_trab(t[0]):.0f})")
                                   for t in trabs], dense=True)
        f_fp = ft.TextField(label="Fecha", value=hoy_str(), dense=True, expand=True)
        f_mp = ft.TextField(label="Monto pagado", keyboard_type=ft.KeyboardType.NUMBER, dense=True, expand=True)

        def guardar_pago(e):
            if not dd2.value or not f_mp.value: snack("Completa los datos", ft.colors.RED); return
            if not parse_fecha(f_fp.value): snack("Fecha inválida", ft.colors.RED); return
            add_pago_trab(f_fp.value, int(dd2.value), float(f_mp.value))
            snack("Pago registrado"); refrescar()

        hist = ft.Column(spacing=6)
        hist_pagos = ft.Column(spacing=6)
        lbl = ft.Text("", weight=ft.FontWeight.BOLD, color=ft.colors.BROWN)

        def refrescar():
            if estado["periodo"] == "custom": return
            datos = filtrar(get_trabajos(), 1, estado["periodo"])
            hist.controls.clear()
            total = sum(r[4] for r in datos)
            lbl.value = f"📊 {len(datos)} trabajos  |  ${total:,.0f}"
            for r in datos:
                def editar(e, reg=r):
                    opts = [(t[0], t[1]) for t in get_trab()]
                    def on_ok(inp):
                        if not parse_fecha(inp[0].value):
                            snack("Fecha inválida", ft.colors.RED); return
                        upd_trabajo(reg[0], inp[0].value, int(inp[1].value),
                                    inp[2].value or "Trabajo", float(inp[3].value))
                        snack("Actualizado"); refrescar()
                    dialogo_campos("Editar trabajo",
                                   [("Fecha", reg[1], "text"),
                                    ("Trabajador", (opts, reg[5]), "dropdown"),
                                    ("Descripción", reg[3], "text"),
                                    ("Monto", reg[4], "num")], on_ok)
                def eliminar(e, reg=r):
                    confirmar(f"Trabajo del {reg[1]} • {reg[2]}\n{reg[3]} = ${reg[4]:.0f}",
                              lambda: (del_trabajo(reg[0]), refrescar()))
                hist.controls.append(ft.Container(content=ft.Row([
                    ft.Column([
                        ft.Text(f"{r[1]} • {r[2]}", size=12, color=ft.colors.GREY_700),
                        ft.Text(r[3], size=13)
                    ], spacing=0, expand=True),
                    ft.Text(f"${r[4]:.0f}", weight=ft.FontWeight.BOLD, color=ft.colors.BROWN),
                    ft.IconButton(ft.icons.EDIT, icon_color=ft.colors.BLUE, icon_size=18, on_click=editar),
                    ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=ft.colors.RED, icon_size=18, on_click=eliminar)
                ]), padding=10, border_radius=8, bgcolor=ft.colors.WHITE))

            pagos = filtrar(get_pagos_trab(), 1, estado["periodo"])
            hist_pagos.controls.clear()
            for r in pagos:
                def editar_p(e, reg=r):
                    opts = [(t[0], t[1]) for t in get_trab()]
                    def on_ok(inp):
                        if not parse_fecha(inp[0].value):
                            snack("Fecha inválida", ft.colors.RED); return
                        upd_pago_trab(reg[0], inp[0].value, int(inp[1].value), float(inp[2].value))
                        snack("Actualizado"); refrescar()
                    dialogo_campos("Editar pago",
                                   [("Fecha", reg[1], "text"),
                                    ("Trabajador", (opts, reg[4]), "dropdown"),
                                    ("Monto", reg[3], "num")], on_ok)
                def eliminar_p(e, reg=r):
                    confirmar(f"Pago a {reg[2]}: ${reg[3]:.0f}",
                              lambda: (del_pago_trab(reg[0]), refrescar()))
                hist_pagos.controls.append(ft.Container(content=ft.Row([
                    ft.Column([
                        ft.Text(f"{r[1]} • {r[2]}", size=12, color=ft.colors.GREY_700),
                        ft.Text("Pago realizado", size=13, color=ft.colors.PURPLE)
                    ], spacing=0, expand=True),
                    ft.Text(f"${r[3]:.0f}", weight=ft.FontWeight.BOLD, color=ft.colors.PURPLE),
                    ft.IconButton(ft.icons.EDIT, icon_color=ft.colors.BLUE, icon_size=18, on_click=editar_p),
                    ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=ft.colors.RED, icon_size=18, on_click=eliminar_p)
                ]), padding=10, border_radius=8, bgcolor=ft.colors.PURPLE_50))
            page.update()

        def exportar(e):
            datos = filtrar(get_trabajos(), 1, estado["periodo"])
            filas = [(r[1], r[2], r[3], r[4]) for r in datos]
            ok, res = exportar_csv(f"trabajos_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                   ["Fecha", "Trabajador", "Descripción", "Monto"], filas)
            snack(f"✔ {res}" if ok else f"Error: {res}",
                  ft.colors.GREEN_700 if ok else ft.colors.RED)

        ctrls = [
            titulo("Registrar trabajo", ft.icons.ENGINEERING),
            ft.Container(content=ft.Column([
                dd, f_f, f_d, f_m,
                ft.ElevatedButton("Guardar trabajo", icon=ft.icons.SAVE, on_click=guardar,
                                  bgcolor=ft.colors.BROWN, color=ft.colors.WHITE)
            ], spacing=10), padding=14, border_radius=12, bgcolor=ft.colors.WHITE),
            titulo("Registrar pago", ft.icons.PAYMENT),
            ft.Container(content=ft.Column([
                dd2, ft.Row([f_fp, f_mp]),
                ft.ElevatedButton("Guardar pago", icon=ft.icons.SAVE, on_click=guardar_pago,
                                  bgcolor=ft.colors.PURPLE, color=ft.colors.WHITE)
            ], spacing=10), padding=14, border_radius=12, bgcolor=ft.colors.WHITE),
            ft.Divider(),
            titulo("Historial de trabajos", ft.icons.HISTORY),
            barra_filtro(refrescar, exportar),
            lbl, hist,
            titulo("Historial de pagos", ft.icons.PAYMENT),
            hist_pagos
        ]
        refrescar()
        return ctrls

    # ============ VISTA: USUARIOS ============
    def abrir_dialogo_usuario(tipo, item=None):
        nombres = {"dist":"distribuidor", "leche":"proveedor de leche", "trab":"trabajador"}
        t = f"{'Editar' if item else 'Nuevo'} {nombres[tipo]}"
        f_n = ft.TextField(label="Nombre", value=item[1] if item else "", dense=True, autofocus=True)

        def guardar(e):
            n = (f_n.value or "").strip()
            if not n: snack("Ingresa el nombre", ft.colors.RED); return
            if tipo == "dist":
                if item: upd_dist(item[0], n)
                else:
                    ok, m = add_dist(n)
                    if not ok: snack(m, ft.colors.RED); return
            elif tipo == "leche":
                if item: upd_leche(item[0], n)
                else:
                    ok, m = add_leche(n)
                    if not ok: snack(m, ft.colors.RED); return
            else:
                if item: upd_trab(item[0], n)
                else:
                    ok, m = add_trab(n)
                    if not ok: snack(m, ft.colors.RED); return
            page.dialog.open = False
            snack("Guardado")
            cargar_vista(5)

        page.dialog = ft.AlertDialog(
            title=ft.Text(t),
            content=ft.Column([f_n], tight=True, spacing=10),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.ElevatedButton("Guardar", on_click=guardar)
            ])
        page.dialog.open = True
        page.update()

    def seccion(nombre, items, saldo_fn, color_add, tipo, tog_fn):
        ctrls = [titulo(nombre, ft.icons.PERSON)]
        ctrls.append(ft.ElevatedButton("➕ Agregar", icon=ft.icons.ADD,
                                       bgcolor=color_add, color=ft.colors.WHITE,
                                       on_click=lambda e: abrir_dialogo_usuario(tipo)))
        for it in items:
            s = saldo_fn(it[0])
            estado_txt = "" if it[2] else " (inactivo)"
            def editar(e, i=it): abrir_dialogo_usuario(tipo, i)
            def toggle(e, i=it[0], a=it[2]):
                tog_fn(i, 0 if a else 1); cargar_vista(5)
            ctrls.append(ft.Container(content=ft.Row([
                ft.Column([
                    ft.Text(f"{it[1]}{estado_txt}", weight=ft.FontWeight.W_500),
                    ft.Text(f"Saldo: ${s:.0f}", size=12, color=ft.colors.GREY_700)
                ], expand=True, spacing=2),
                ft.IconButton(ft.icons.EDIT, icon_color=ft.colors.BLUE, on_click=editar),
                ft.IconButton(ft.icons.TOGGLE_ON if it[2] else ft.icons.TOGGLE_OFF,
                              icon_color=ft.colors.GREEN if it[2] else ft.colors.GREY,
                              on_click=toggle)
            ]), padding=8, border_radius=8, bgcolor=ft.colors.WHITE))
        return ctrls

    def v_usuarios():
        ctrls = [ft.Text("Gestión de usuarios", size=20, weight=ft.FontWeight.BOLD)]
        ctrls += seccion("Distribuidores (te deben)", get_dist(False), saldo_dist,
                         ft.colors.GREEN, "dist", tog_dist)
        ctrls.append(ft.Divider())
        ctrls += seccion("Proveedores de leche (les debes)", get_leche(False), saldo_leche,
                         ft.colors.ORANGE, "leche", tog_leche)
        ctrls.append(ft.Divider())
        ctrls += seccion("Trabajadores (les debes)", get_trab(False), saldo_trab,
                         ft.colors.BROWN, "trab", tog_trab)
        return ctrls

    # ============ NAVEGACIÓN ============
    vistas = [v_inicio, v_produccion, v_ventas, v_leche, v_trabajadores, v_usuarios]

    def cargar_vista(idx):
        estado["vista"] = idx
        contenido.controls.clear()
        try:
            contenido.controls.extend(vistas[idx]())
        except Exception as ex:
            contenido.controls.append(ft.Text(f"Error: {ex}", color=ft.colors.RED))
        page.update()

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        on_change=lambda e: cargar_vista(e.control.selected_index),
        destinations=[
            ft.NavigationDestination(icon=ft.icons.DASHBOARD, label="Inicio"),
            ft.NavigationDestination(icon=ft.icons.AGRICULTURE, label="Produc."),
            ft.NavigationDestination(icon=ft.icons.SELL, label="Ventas"),
            ft.NavigationDestination(icon=ft.icons.WATER_DROP, label="Leche"),
            ft.NavigationDestination(icon=ft.icons.ENGINEERING, label="Trabaj."),
            ft.NavigationDestination(icon=ft.icons.PEOPLE, label="Usuar."),
        ])

    page.appbar = ft.AppBar(
        title=ft.Row([
            ft.Text("🧀", size=28),
            ft.Text("Gestión de Queso", size=18, weight=ft.FontWeight.BOLD),
        ], spacing=8),
        bgcolor=ft.colors.BLUE_700,
        color=ft.colors.WHITE,
        center_title=False,
    )
    page.add(contenido)
    cargar_vista(0)

ft.app(target=main)
