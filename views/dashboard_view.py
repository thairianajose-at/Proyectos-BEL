import flet as ft
import asyncio
from services.zabbix import SERVICIOS_EMPRESA, obtener_metricas_reales
from utilidades.colors import palettet
from utilidades.fonts import appFonts

#CONFIGURACIÓN DE UMBRALES (ADMIN) 
CONFIG_SERVICIOS = {s["nombre"]: {"metrica": "cpu", "valor": 85} for s in SERVICIOS_EMPRESA}

def dashboard_view(page: ft.Page):
    # Recuperación de Sesión y Roles
    user_rol = page.session.get("user_rol")
    user_name = page.session.get("user_name")
    
    es_admin = user_rol == "admin"
    es_gerente = user_rol == "gerente"

    page.fonts = appFonts.FONTS_DICT
    page.bgcolor = "#F5F7F9"
    
    servicios_controles = {}
    online_count = ft.Text("0", size=24, weight="bold", color=palettet.accent)
    offline_count = ft.Text("0", size=24, weight="bold", color=ft.colors.RED_700)

    # NAVEGACIÓN WEB CORREGIDA 
    def abrir_web(e, url_destino):
        if url_destino:
            # Si no tiene http, se lo agregamos para que el navegador no falle
            if not url_destino.startswith("http"):
                url_destino = f"https://{url_destino}"
            page.launch_url(url_destino)

    # COMPONENTES DE GRÁFICA (SOLO ADMIN) 
    dropdown_global = ft.Dropdown(
        value="cpu", label="FILTRAR MÉTRICA",
        width=220, height=60, text_size=13,
        color=palettet.accent, label_style=ft.TextStyle(color=palettet.accent),
        border_color=palettet.accent, focused_border_color=palettet.accent,
        options=[
            ft.dropdown.Option("cpu", "USO DE CPU"),
            ft.dropdown.Option("ram", "USO DE RAM"),
            ft.dropdown.Option("red", "TRÁFICO RED"),
        ],
        on_change=lambda _: page.update()
    )

    chart_macro = ft.BarChart(
        bar_groups=[],
        bottom_axis=ft.ChartAxis(labels=[]),
        left_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(value=0, label=ft.Text("0%", size=10, color=ft.colors.GREY_500)),
                ft.ChartAxisLabel(value=50, label=ft.Text("50%", size=10, color=ft.colors.GREY_500)),
                ft.ChartAxisLabel(value=100, label=ft.Text("100%", size=10, color=ft.colors.GREY_500)),
            ]
        ),
        horizontal_grid_lines=ft.ChartGridLines(
            interval=20, color=ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE), width=1,
        ),
        border=ft.border.only(left=ft.BorderSide(1, ft.colors.GREY_300), bottom=ft.BorderSide(1, ft.colors.GREY_300)),
        max_y=110, animate=500, expand=True
    )

    # AJUSTE TÉCNICO (ADMIN) 
    def abrir_ajustes_umbral(nombre_servicio):
        conf = CONFIG_SERVICIOS[nombre_servicio]
        input_valor = ft.TextField(label="Límite %", value=str(conf["valor"]), width=110, border_color=palettet.accent)
        dropdown_met = ft.Dropdown(label="Métrica", value=conf["metrica"], width=230, border_color=palettet.accent,
            options=[ft.dropdown.Option("cpu", "CPU"), ft.dropdown.Option("ram", "RAM"), ft.dropdown.Option("red", "RED")])

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

    # DISEÑO DE GAUGES 
    def crear_gauge(valor, color, label):
        pie = ft.PieChart(sections=[ft.PieChartSection(valor, color=color, radius=7), ft.PieChartSection(100-valor, color=ft.colors.with_opacity(0.1, color), radius=7)], center_space_radius=12, height=45, width=45)
        txt = ft.Text(f"{int(valor)}%", size=8, weight="bold", color=color)
        return ft.Container(content=ft.Column([ft.Text(label, size=8, weight="bold"), ft.Stack([pie, ft.Container(content=txt, alignment=ft.alignment.center, width=45, height=45)])], horizontal_alignment="center", spacing=2)), pie, txt

    # TARJETAS DE SERVICIO 
    def crear_card_servicio(servicio):
        cpu_c, cpu_p, cpu_t = crear_gauge(0, palettet.cpu, "CPU")
        ram_c, ram_p, ram_t = crear_gauge(0, palettet.ram, "RAM")
        red_c, red_p, red_t = crear_gauge(0, palettet.red, "RED")
        
        status_dot = ft.Container(width=10, height=10, border_radius=5, bgcolor=ft.colors.GREY_400)
        card_container = ft.Container(padding=15, bgcolor="white", border_radius=20, border=ft.border.all(1, "#E8E8E8"))

        servicios_controles[servicio["nombre"]] = {
            "cpu_sec": cpu_p.sections, "cpu_val": cpu_t, "ram_sec": ram_p.sections, "ram_val": ram_t,
            "red_sec": red_p.sections, "red_val": red_t, "dot": status_dot, "container": card_container
        }

        # CAPTURA DE URL INDIVIDUAL
        url_actual = servicio.get("url")

        # BOTONES: La flecha siempre está y ahora TIENE ACCIÓN
        btns = [
            ft.IconButton(
                ft.icons.OPEN_IN_NEW_ROUNDED, 
                icon_size=18, 
                tooltip="Abrir Web",
                on_click=lambda e: abrir_web(e, url_actual) 
            )
        ]

        if es_admin:
            btns.append(ft.IconButton(ft.icons.INSERT_CHART_OUTLINED_ROUNDED, icon_size=18, on_click=lambda _: page.go(f"/logs/{servicio['nombre']}"), tooltip="Ver Logs"))
            btns.append(ft.IconButton(ft.icons.TUNE_ROUNDED, icon_color=palettet.accent, icon_size=18, on_click=lambda _: abrir_ajustes_umbral(servicio["nombre"]), tooltip="Ajustar Alerta"))

        card_container.content = ft.Column([
            ft.Row([ft.Icon(ft.icons.DNS_ROUNDED, size=18, color=palettet.secundary), ft.Text(servicio["nombre"].upper(), weight="bold", size=12, expand=True), status_dot]),
            ft.Divider(height=10, thickness=0.5),
            ft.Row([cpu_c, ram_c, red_c], alignment="spaceAround"),
            ft.Row(btns, alignment="end", spacing=0)
        ], spacing=5)
        return ft.Container(content=card_container, col={"sm": 12, "md": 6, "lg": 4})

    # BUCLE EN TIEMPO REAL 
    async def actualizar_datos():
        while True:
            on_count = 0
            new_groups, new_labels = [], []
            m_global = dropdown_global.value 

            for i, s in enumerate(SERVICIOS_EMPRESA):
                try:
                    data = obtener_metricas_reales(s["nombre"])
                    ctrl = servicios_controles[s["nombre"]]
                    conf = CONFIG_SERVICIOS[s["nombre"]]

                    for k in ["cpu", "ram", "red"]:
                        ctrl[f"{k}_sec"][0].value = data[k]
                        ctrl[f"{k}_sec"][1].value = 100 - data[k]
                        ctrl[f"{k}_val"].value = f"{int(data[k])}%"

                    if data[conf["metrica"]] >= conf["valor"] or data["estado"] == "Offline":
                        ctrl["dot"].bgcolor = "red"
                        ctrl["container"].border = ft.border.all(2, "red")
                    else:
                        ctrl["dot"].bgcolor = palettet.accent
                        ctrl["container"].border = ft.border.all(1, "#E8E8E8")
                        on_count += 1

                    if es_admin:
                        color_barras = palettet.cpu if m_global == "cpu" else palettet.ram if m_global == "ram" else palettet.red
                        new_groups.append(ft.BarChartGroup(x=i, bar_rods=[ft.BarChartRod(from_y=0, to_y=data[m_global], color=color_barras, width=18, border_radius=4)]))
                        new_labels.append(ft.ChartAxisLabel(value=i, label=ft.Text(s["nombre"][:3].upper(), size=9, weight="bold")))
                except: continue

            if es_admin:
                chart_macro.bar_groups = new_groups
                chart_macro.bottom_axis.labels = new_labels
            
            online_count.value = str(on_count)
            offline_count.value = str(len(SERVICIOS_EMPRESA) - on_count)
            page.update()
            await asyncio.sleep(5)

    # ENSAMBLADO DE VISTA
    header = ft.Container(
        gradient=ft.LinearGradient(colors=[palettet.accent, palettet.secundary]),
        padding=30, border_radius=ft.border_radius.only(bottom_left=30, bottom_right=30),
        content=ft.Row([ft.Text(f"PANEL {user_rol.upper()}: {user_name.upper()}", color="white", size=22, weight="bold", expand=True)])
    )

    panel_macro = ft.Container(
        visible=es_admin, padding=25, bgcolor="white", border_radius=20, margin=ft.margin.symmetric(horizontal=30),
        shadow=ft.BoxShadow(blur_radius=15, color=ft.colors.with_opacity(0.1, "black")),
        content=ft.Column([
            ft.Row([ft.Text("MONITOREO GLOBAL (GRIDS)", weight="bold", size=16), dropdown_global], alignment="spaceBetween"),
            ft.Container(height=10),
            ft.Container(content=chart_macro, height=160, padding=ft.padding.only(left=10, right=10))
        ])
    )

    layout = ft.Column(controls=[
        header,
        ft.Container(padding=ft.padding.symmetric(horizontal=30), offset=ft.Offset(0, -0.15), content=ft.Row([
            ft.Container(expand=True, bgcolor="white", padding=15, border_radius=15, content=ft.Row([ft.Icon(ft.icons.CHECK_CIRCLE, color=palettet.accent), online_count])),
            ft.Container(expand=True, bgcolor="white", padding=15, border_radius=15, content=ft.Row([ft.Icon(ft.icons.DANGEROUS, color="red"), offline_count])),
        ], spacing=15)),
        panel_macro,
        ft.Container(padding=30, content=ft.ResponsiveRow(controls=[crear_card_servicio(s) for s in SERVICIOS_EMPRESA], spacing=20))
    ], scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    page.run_task(actualizar_datos)
    return layout