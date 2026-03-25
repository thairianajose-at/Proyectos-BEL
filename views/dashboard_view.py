import flet as ft
import asyncio
from services.zabbix import SERVICIOS_EMPRESA, obtener_metricas_reales
from utilidades.colors import palettet
from utilidades.fonts import appFonts
from database.config import SessionLocal
from database.modelo import Logs

# Configuración persistente de umbrales
CONFIG_SERVICIOS = {s["nombre"]: {"metrica": "CPU", "valor": 85, "reiniciando": False} for s in SERVICIOS_EMPRESA}

def dashboard_view(page: ft.Page):
    page.fonts = appFonts.FONTS_DICT
    page.bgcolor = "#F4F7F6" # Gris muy claro para resaltar las tarjetas blancas
    
    # Diccionario para guardar referencias a los controles que se actualizan
    servicios_controles = {}
    
    # Contadores globales
    online_count = ft.Text("0", size=24, weight="bold", color=palettet.accent)
    offline_count = ft.Text("0", size=24, weight="bold", color=ft.colors.RED_700)

    # --- FUNCIÓN PARA CREAR GAUGES (CÁPSULAS DE MÉTRICAS) ---
    def crear_gauge(valor, color, label):
        pie = ft.PieChart(
            sections=[
                ft.PieChartSection(valor, color=color, radius=6, title=""),
                ft.PieChartSection(100 - valor, color=ft.colors.with_opacity(0.1, color), radius=6, title=""),
            ],
            center_space_radius=15, height=50, width=50,
        )
        val_text = ft.Text(f"{valor}%", size=8, weight="bold")
        
        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=9, weight="bold", color=ft.colors.GREY_700),
                ft.Stack([
                    pie,
                    ft.Container(content=val_text, alignment=ft.alignment.center, width=50, height=50)
                ])
            ], horizontal_alignment="center", spacing=2),
            padding=5
        ), pie, val_text

    # --- FUNCIÓN PARA CREAR CADA TARJETA DE SERVICIO ---
    def crear_card_servicio(servicio):
        # Generar los 3 gauges y obtener sus referencias internas
        cpu_cont, cpu_pie, cpu_txt = crear_gauge(0, palettet.cpu, "CPU")
        ram_cont, ram_pie, ram_txt = crear_gauge(0, palettet.ram, "RAM")
        red_cont, red_pie, red_txt = crear_gauge(0, palettet.accent, "RED")
        
        status_dot = ft.Container(width=8, height=8, border_radius=4, bgcolor=ft.colors.GREY_400)
        status_text = ft.Text("ESPERANDO", size=9, weight="bold", color=ft.colors.GREY_600)
        
        card_container = ft.Container(
            padding=20,
            bgcolor=ft.colors.WHITE,
            border_radius=20,
            border=ft.border.all(1, "#E0E0E0"),
            animate=ft.animation.Animation(300, ft.AnimationCurve.DECELERATE),
        )

        # Guardamos las referencias para la función de actualización
        servicios_controles[servicio["nombre"]] = {
            "cpu_sec": cpu_pie.sections, "cpu_val": cpu_txt,
            "ram_sec": ram_pie.sections, "ram_val": ram_txt,
            "red_sec": red_pie.sections, "red_val": red_txt,
            "dot": status_dot, "txt": status_text, "container": card_container
        }

        # Lógica de Reinicio
        async def on_reinicio_click(e):
            CONFIG_SERVICIOS[servicio["nombre"]]["reiniciando"] = True
            db = SessionLocal()
            try:
                nuevo_log = Logs(servicio=servicio["nombre"], nivel="WARNING", detalles={"accion": "REINICIO", "ip": servicio["ip"]})
                db.add(nuevo_log)
                db.commit()
            finally: db.close()

            page.snack_bar = ft.SnackBar(ft.Text(f"Reiniciando {servicio['nombre']}..."), bgcolor="orange")
            page.snack_bar.open = True
            page.update()
            await asyncio.sleep(5)
            CONFIG_SERVICIOS[servicio["nombre"]]["reiniciando"] = False

        # Construcción visual de la tarjeta
        card_container.content = ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.icons.DNS_ROUNDED, color=palettet.secundary, size=20),
                    bgcolor=ft.colors.with_opacity(0.1, palettet.secundary),
                    padding=10, border_radius=12
                ),
                ft.Column([
                    ft.Text(servicio["nombre"].upper(), size=14, weight="bold", color=palettet.secundary),
                    ft.Text(servicio["ip"], size=10, color=ft.colors.GREY_500)
                ], expand=True, spacing=0),
                ft.Column([status_dot, status_text], horizontal_alignment="center", spacing=2)
            ]),
            ft.Divider(height=20, thickness=0.5, color="#EEEEEE"),
            ft.Row([cpu_cont, ram_cont, red_cont], alignment="spaceAround"),
            ft.Row([
                ft.IconButton(ft.icons.OPEN_IN_NEW_ROUNDED, icon_size=18, on_click=lambda _: page.launch_url(servicio["url"])),
                ft.IconButton(ft.icons.REORDER_ROUNDED, icon_size=18, on_click=lambda _: page.go(f"/logs/{servicio['nombre']}")),
                ft.IconButton(ft.icons.RESTART_ALT_ROUNDED, icon_color="orange", on_click=on_reinicio_click),
                ft.IconButton(ft.icons.TUNE_ROUNDED, icon_color=palettet.accent),
            ], alignment="spaceBetween")
        ])
        return ft.Container(content=card_container, col={"sm": 12, "md": 6, "lg": 4})

    # --- LÓGICA DE ACTUALIZACIÓN EN TIEMPO REAL ---
    async def actualizar_dashboard():
        while True:
            on_count = 0
            for s in SERVICIOS_EMPRESA:
                try:
                    c = servicios_controles[s["nombre"]]
                    conf = CONFIG_SERVICIOS[s["nombre"]]
                    
                    m = {"cpu": 0, "ram": 0, "red": 0, "estado": "Offline"} if conf["reiniciando"] else obtener_metricas_reales(s["nombre"])

                    # Actualizar Gauges
                    for k in ["cpu", "ram", "red"]:
                        val = m[k]
                        c[f"{k}_sec"][0].value = val
                        c[f"{k}_sec"][1].value = 100 - val
                        c[f"{k}_val"].value = f"{val}%"
                    
                    metrica_critica = m[conf["metrica"].lower()]
                    
                    if m["estado"] == "Offline":
                        c["dot"].bgcolor = ft.colors.RED_700
                        c["txt"].value = "REINICIANDO..." if conf["reiniciando"] else "CAÍDO"
                        c["txt"].color = ft.colors.RED_700
                        c["container"].border = ft.border.all(1.5, ft.colors.RED_700)
                    elif metrica_critica >= conf["valor"]:
                        c["container"].border = ft.border.all(2, ft.colors.RED_ACCENT_400)
                        c["txt"].value = "CRÍTICO"
                        c["txt"].color = ft.colors.RED_ACCENT_400
                        on_count += 1
                    else:
                        c["dot"].bgcolor = palettet.accent
                        c["txt"].value = "ACTIVO"
                        c["txt"].color = palettet.accent
                        c["container"].border = ft.border.all(1, "#E0E0E0")
                        on_count += 1
                except: continue
            
            online_count.value = str(on_count)
            offline_count.value = str(len(SERVICIOS_EMPRESA) - on_count)
            page.update()
            await asyncio.sleep(5)

    # --- DISEÑO DEL LAYOUT (ESTILO LOGIN) ---
    header = ft.Container(
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
            colors=[palettet.accent, palettet.secundary],
        ),
        padding=ft.padding.only(left=30, right=30, top=40, bottom=50),
        border_radius=ft.border_radius.only(bottom_left=35, bottom_right=35),
        content=ft.Row([
            ft.Column([
                ft.Text("PANEL DE CONTROL INFRAESTRUCTURA", color=palettet.primary, size=10, weight="bold", opacity=0.7),
                ft.Text("MONITOREO JAC & BEL", color=palettet.primary, size=24, weight="bold"),
            ], expand=True),
            ft.Icon(ft.icons.NOTIFICATIONS_NONE_ROUNDED, color="white", size=20)
        ])
    )

    def stat_box(label, value_control, icon, color):
        return ft.Container(
            expand=True, bgcolor=ft.colors.WHITE, padding=20, border_radius=22,
            border=ft.border.all(1, "#E8E8E8"),
            content=ft.Row([
                ft.Container(content=ft.Icon(icon, color=color, size=22), bgcolor=ft.colors.with_opacity(0.1, color), padding=12, border_radius=15),
                ft.Column([ft.Text(label, size=9, weight="bold", color=ft.colors.GREY_500), value_control], spacing=0)
            ], spacing=15)
        )

    # Ensamblado Final
    layout = ft.Column([
        header,
        ft.Container(
            padding=ft.padding.symmetric(horizontal=30),
            offset=ft.Offset(0, -0.25),
            content=ft.Row([
                stat_box("NODOS ACTIVOS", online_count, ft.icons.CHECK_CIRCLE_ROUNDED, palettet.accent),
                stat_box("NODOS CAÍDOS", offline_count, ft.icons.ERROR_ROUNDED, ft.colors.RED_700),
            ], spacing=20)
        ),
        ft.Container(
            padding=ft.padding.only(left=30, right=30, bottom=30),
            content=ft.ResponsiveRow(
                controls=[crear_card_servicio(s) for s in SERVICIOS_EMPRESA], 
                spacing=20
            )
        )
    ], scroll=ft.ScrollMode.ADAPTIVE, spacing=0)

    # Iniciar la tarea de actualización
    page.run_task(actualizar_dashboard)
    
    return layout