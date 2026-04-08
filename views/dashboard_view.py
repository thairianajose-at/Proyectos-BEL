import flet as ft
import asyncio
import requests
import os
from sqlalchemy import func
from datetime import datetime
from fpdf import FPDF 
from database.config import SessionLocal
from database.modelo import Logs # Tu modelo con 'fecha' y 'detalles'
from services.lector_api import SERVICIOS_EMPRESA, obtener_metricas_reales
from utilidades.colors import palettet
from utilidades.fonts import appFonts

API_URL_REAL = "http://172.17.16.18:8000/api/containers"
CONFIG_SERVICIOS = {s["nombre"]: {"metrica": "cpu", "valor": 85} for s in SERVICIOS_EMPRESA}

def dashboard_view(page: ft.Page):
    user_rol = str(page.session.get("user_rol") or "Invitado").lower()
    user_name = page.session.get("user_name") or "Usuario"
    
    es_admin = "admin" in user_rol
    es_gerente = "gerente" in user_rol or "gerencia" in user_rol

    servicios_controles = {}

    # --- FUNCIÓN DE REPORTE GERENCIAL (PDF AUTOMÁTICO) ---
    def abrir_reporte_gerencial(e):
        db = SessionLocal()
        mes_actual = datetime.now().month
        anio_actual = datetime.now().year
        caidas, alertas = [], []
        
        try:
            # 1. Ranking de Caídas (Usando 'fecha' de tu modelo)
            caidas = db.query(Logs.servicio, func.count(Logs.id)).filter(
                Logs.nivel == "CRITICAL",
                func.extract('month', Logs.fecha) == mes_actual
            ).group_by(Logs.servicio).order_by(func.count(Logs.id).desc()).all()

            # 2. Alertas de Umbral (Usando 'detalles' que es JSON)
            alertas = db.query(Logs.detalles, func.count(Logs.id)).filter(
                Logs.nivel.in_(["WARNING", "ERROR"]),
                func.extract('month', Logs.fecha) == mes_actual
            ).group_by(Logs.detalles).all()

        except Exception as ex:
            print(f"Error en consulta DB: {ex}")
        finally:
            db.close()

        # Generación del documento
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, "REPORTE DE GESTIÓN DE INFRAESTRUCTURA - BEL", ln=True, align='C')
        pdf.set_font("Arial", size=10)
        pdf.cell(190, 10, f"Periodo: {mes_actual}/{anio_actual} | Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
        pdf.ln(10)

        # Tabla de Caídas
        pdf.set_fill_color(200, 30, 30)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(190, 8, " RANKING DE INDISPONIBILIDAD (CRITICAL)", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        for serv, cant in caidas:
            pdf.cell(130, 8, f" Servicio: {serv}", border=1)
            pdf.cell(60, 8, f" Total Caídas: {cant}", border=1, ln=True)
        
        pdf.ln(10)

        # Tabla de Umbrales
        pdf.set_fill_color(46, 125, 50) # Verde corporativo
        pdf.set_text_color(255, 255, 255)
        pdf.cell(190, 8, " ALERTAS DE RENDIMIENTO (DETALLES TÉCNICOS)", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        
        if not alertas:
            pdf.cell(190, 8, " Sin alertas registradas este mes.", border=1, ln=True)
        else:
            for det, cant in alertas:
                texto_detalle = str(det).replace("{", "").replace("}", "").replace("'", "")
                pdf.cell(150, 8, f" {texto_detalle[:65]}", border=1)
                pdf.cell(40, 8, f" Veces: {cant}", border=1, ln=True)

        nombre_pdf = f"Reporte_BEL_{mes_actual}_{anio_actual}.pdf"
        pdf.output(nombre_pdf)
        
        # --- APERTURA AUTOMÁTICA ---
        if os.name == 'nt': # Windows
            os.startfile(nombre_pdf)
        
        page.snack_bar = ft.SnackBar(ft.Text(f"Reporte generado y abierto: {nombre_pdf}"), bgcolor="green")
        page.snack_bar.open = True
        page.update()

    # --- LÓGICA DE AJUSTES ---
    def abrir_ajustes_umbral(nombre_servicio):
        conf = CONFIG_SERVICIOS[nombre_servicio]
        input_valor = ft.TextField(label="Límite %", value=str(conf["valor"]), width=110, border_color=palettet.accent)
        dropdown_met = ft.Dropdown(label="Métrica", value=conf["metrica"], width=230, border_color=palettet.accent,
            options=[ft.dropdown.Option("cpu", "USO DE CPU"), ft.dropdown.Option("ram", "USO DE RAM"), ft.dropdown.Option("red", "TRÁFICO RED")])

        def guardar(e):
            CONFIG_SERVICIOS[nombre_servicio] = {"metrica": dropdown_met.value, "valor": int(input_valor.value)}
            dialogo.open = False
            page.update()

        dialogo = ft.AlertDialog(
            title=ft.Text(f"AJUSTAR ALERTA: {nombre_servicio.upper()}", color=palettet.accent, weight="bold"),
            content=ft.Column([dropdown_met, input_valor], height=140, tight=True),
            actions=[ft.ElevatedButton("APLICAR", bgcolor=palettet.accent, color="white", on_click=guardar)],
        )
        page.dialog = dialogo
        dialogo.open = True
        page.update()

    dropdown_global = ft.Dropdown(
        value="cpu", label="FILTRAR MÉTRICA", width=220, height=60, text_size=13,
        color=palettet.accent, label_style=ft.TextStyle(color=palettet.accent),
        border_color=palettet.accent, focused_border_color=palettet.accent,
        options=[ft.dropdown.Option("cpu", "USO DE CPU"), ft.dropdown.Option("ram", "USO DE RAM"), ft.dropdown.Option("red", "TRÁFICO RED")],
        on_change=lambda _: page.update()
    )

    chart_macro = ft.BarChart(
        bar_groups=[], bottom_axis=ft.ChartAxis(labels=[]),
        left_axis=ft.ChartAxis(labels=[
            ft.ChartAxisLabel(value=0, label=ft.Text("0%", size=10, color=ft.colors.GREY_500)),
            ft.ChartAxisLabel(value=50, label=ft.Text("50%", size=10, color=ft.colors.GREY_500)),
            ft.ChartAxisLabel(value=100, label=ft.Text("100%", size=10, color=ft.colors.GREY_500)),
        ]),
        horizontal_grid_lines=ft.ChartGridLines(interval=20, color=ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE), width=1),
        border=ft.border.only(left=ft.BorderSide(1, ft.colors.GREY_300), bottom=ft.BorderSide(1, ft.colors.GREY_300)),
        max_y=110, animate=500, expand=True
    )

    def crear_gauge(valor, color, label):
        pie = ft.PieChart(sections=[ft.PieChartSection(valor, color=color, radius=7), ft.PieChartSection(100-valor, color=ft.colors.with_opacity(0.1, color), radius=7)], center_space_radius=12, height=45, width=45)
        txt = ft.Text(f"{int(valor)}%", size=8, weight="bold", color=color)
        return ft.Container(content=ft.Column([ft.Text(label, size=8, weight="bold"), ft.Stack([pie, ft.Container(content=txt, alignment=ft.alignment.center, width=45, height=45)])], horizontal_alignment="center", spacing=2)), pie, txt

    def crear_card_servicio(servicio):
        db = SessionLocal()
        caidas = db.query(func.count(Logs.id)).filter(Logs.servicio == servicio["nombre"], Logs.nivel == "CRITICAL").scalar() or 0
        db.close()

        cpu_c, cpu_p, cpu_t = crear_gauge(0, palettet.cpu, "CPU")
        ram_c, ram_p, ram_t = crear_gauge(0, palettet.ram, "RAM")
        red_c, red_p, red_t = crear_gauge(0, palettet.red, "RED")
        status_dot = ft.Container(width=10, height=10, border_radius=5, bgcolor=ft.colors.GREY_400)
        card_container = ft.Container(padding=15, bgcolor="white", border_radius=20, border=ft.border.all(1, "#E8E8E8"))
        
        caidas_txt = ft.Text(f"Caídas: {caidas}", size=10, color="red", weight="bold")
        servicios_controles[servicio["nombre"]] = {
            "cpu_sec": cpu_p.sections, "cpu_val": cpu_t, "ram_sec": ram_p.sections, "ram_val": ram_t,
            "red_sec": red_p.sections, "red_val": red_t, "dot": status_dot, "container": card_container,
            "caidas_txt": caidas_txt
        }

        btns = [ft.IconButton(ft.icons.OPEN_IN_NEW_ROUNDED, icon_size=18, on_click=lambda e: page.launch_url(servicio.get("url")))]
        if es_admin:
            btns.append(ft.IconButton(ft.icons.INSERT_CHART_OUTLINED_ROUNDED, icon_size=18, on_click=lambda _: page.go(f"/logs/{servicio['nombre']}")))
            btns.append(ft.IconButton(ft.icons.TUNE_ROUNDED, icon_color=palettet.accent, icon_size=18, on_click=lambda _: abrir_ajustes_umbral(servicio["nombre"])))

        card_container.content = ft.Column([
            ft.Row([ft.Icon(ft.icons.DNS_ROUNDED, size=18, color=palettet.secundary), ft.Text(servicio["nombre"].upper(), weight="bold", size=12, expand=True), status_dot]),
            ft.Divider(height=10, thickness=0.5),
            ft.Row([cpu_c, ram_c, red_c], alignment="spaceAround"),
            ft.Row([caidas_txt, ft.Row(btns, spacing=0)], alignment="spaceBetween")
        ], spacing=5)
        return ft.Container(content=card_container, col={"sm": 12, "md": 6, "lg": 4})

    async def actualizar_datos():
        while True:
            new_groups, new_labels = [], []
            metrica_filtro = dropdown_global.value or "cpu"
            color_barra = palettet.cpu if metrica_filtro == "cpu" else palettet.ram if metrica_filtro == "ram" else palettet.red
            
            try:
                res = requests.get(API_URL_REAL, timeout=2)
                api_data = res.json()
            except: api_data = []

            for i, s in enumerate(SERVICIOS_EMPRESA):
                container_real = next((c for c in api_data if c.get("name") == s["nombre"]), None)
                data = {"cpu": 0, "ram": 0, "red": 0, "estado": "Offline"}
                if container_real:
                    metrics = container_real.get("health", {}).get("metrics", {})
                    data = {"cpu": metrics.get("cpu_percent", 0), "ram": metrics.get("memory_percent", 0), "red": 15, "estado": "Online" if container_real.get("running") else "Offline"}
                else:
                    data = obtener_metricas_reales(s["nombre"])

                if s["nombre"] in servicios_controles:
                    ctrl = servicios_controles[s["nombre"]]
                    conf = CONFIG_SERVICIOS[s["nombre"]]
                    for k in ["cpu", "ram", "red"]:
                        ctrl[f"{k}_sec"][0].value = data[k]
                        ctrl[f"{k}_val"].value = f"{int(data[k])}%"

                    val_bar = data.get(metrica_filtro, 0)
                    new_groups.append(ft.BarChartGroup(x=i, bar_rods=[ft.BarChartRod(from_y=0, to_y=val_bar, width=22, color=color_barra, border_radius=5)]))
                    new_labels.append(ft.ChartAxisLabel(value=i, label=ft.Text(s["nombre"][:6].upper(), size=9, weight="bold")))

                    if data[conf["metrica"]] >= conf["valor"] or data["estado"] == "Offline":
                        ctrl["dot"].bgcolor = "red"
                        ctrl["container"].border = ft.border.all(2, "red")
                    else:
                        ctrl["dot"].bgcolor = palettet.accent
                        ctrl["container"].border = ft.border.all(1, "#E8E8E8")
            
            chart_macro.bar_groups = new_groups
            chart_macro.bottom_axis.labels = new_labels
            page.update()
            await asyncio.sleep(5)

    # --- DISEÑO DE CABECERA (IGUAL AL ORIGINAL) ---
    header = ft.Container(
        gradient=ft.LinearGradient(colors=[palettet.accent, palettet.secundary]),
        padding=30, border_radius=ft.border_radius.only(bottom_left=30, bottom_right=30),
        content=ft.Row([
            ft.Text(f"INFRAESTRUCTURA: {user_name.upper()}", color="white", size=20, weight="bold", expand=True),
            ft.IconButton(
                icon=ft.icons.PICTURE_AS_PDF_ROUNDED, 
                icon_color="white", icon_size=32, 
                visible=es_gerente, 
                on_click=abrir_reporte_gerencial
            )
        ])
    )

    panel_macro = ft.Container(
        visible=es_admin, padding=25, bgcolor="white", border_radius=20, margin=ft.margin.symmetric(horizontal=30),
        shadow=ft.BoxShadow(blur_radius=15, color="#0000000D"),
        content=ft.Column([
            ft.Row([ft.Text("MONITOREO COMPARATIVO", weight="bold", size=14, color=palettet.secundary), dropdown_global], alignment="spaceBetween"),
            ft.Container(chart_macro, height=180, padding=10)
        ])
    )

    layout = ft.Column(controls=[
        header, ft.Container(height=20), panel_macro, 
        ft.Container(padding=30, content=ft.ResponsiveRow(controls=[crear_card_servicio(s) for s in SERVICIOS_EMPRESA], spacing=20))
    ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    page.run_task(actualizar_datos)
    return layout