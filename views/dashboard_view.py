import flet as ft
import asyncio
from services.zabbix import SERVICIOS_EMPRESA, obtener_metricas_reales
from utilidades.colors import palettet
from utilidades.fonts import appFonts

CONFIG_SERVICIOS = {s["nombre"]: {"metrica": "cpu", "valor": 85} for s in SERVICIOS_EMPRESA}

def dashboard_view(page: ft.Page):
    page.fonts = appFonts.FONTS_DICT
    page.bgcolor = palettet.gris
    
    servicios_controles = {}
    
    online_count = ft.Text("0", size=24, weight="bold", color=palettet.accent)
    offline_count = ft.Text("0", size=24, weight="bold", color=ft.colors.RED_700)

    def abrir_ajustes_umbral(nombre_servicio):
        conf = CONFIG_SERVICIOS[nombre_servicio]
        
        input_valor = ft.TextField(
            label="Valor Crítico (%)", 
            value=str(conf["valor"]),
            suffix_text="%",
            width=120,
            color=palettet.secundary,
            cursor_color=palettet.accent, # Puntero Verde
            selection_color=ft.colors.with_opacity(0.3, palettet.accent), # Selección Verde
            focused_border_color=palettet.accent, 
            border_color=ft.colors.GREY_400,
            label_style=ft.TextStyle(color=palettet.secundary),
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        dropdown_metrica = ft.Dropdown(
            label="Métrica a Monitorear",
            value=conf["metrica"],
            color=palettet.secundary,
            focused_border_color=palettet.accent, 
            border_color=ft.colors.GREY_400,
            options=[
                ft.dropdown.Option("cpu", "Procesador (CPU)"),
                ft.dropdown.Option("ram", "Memoria (RAM)"),
                ft.dropdown.Option("red", "Tráfico (RED)"),
            ],
            width=240
        )

        def guardar_cambios(e):
            try:
                CONFIG_SERVICIOS[nombre_servicio]["valor"] = int(input_valor.value)
                CONFIG_SERVICIOS[nombre_servicio]["metrica"] = dropdown_metrica.value
                dialogo.open = False
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Configuración de {nombre_servicio} actualizada.", color=palettet.primary),
                    bgcolor=palettet.accent
                )
                page.snack_bar.open = True
                page.update()
            except ValueError:
                input_valor.error_text = "Ingresa un número"
                page.update()

        # Ventana de ajustes sin elementos azules
        dialogo = ft.AlertDialog(
            title=ft.Text(f"AJUSTES: {nombre_servicio.upper()}", size=16, weight="bold", color=palettet.secundary),
            content=ft.Column([
                ft.Text("Define el límite para marcar el nodo como CRÍTICO:", size=12, color=ft.colors.GREY_700),
                dropdown_metrica,
                input_valor,
            ], height=180, tight=True, spacing=20),
            actions=[
                # Botón Cancelar forzado a Gris (Cero Azul)
                ft.TextButton(
                    content=ft.Text("CANCELAR", color=ft.colors.GREY_700, weight="bold"),
                    on_click=lambda _: [setattr(dialogo, "open", False), page.update()],
                    style=ft.ButtonStyle(overlay_color=ft.colors.TRANSPARENT)
                ),
                # Botón Guardar con tu paleta (Verde Accent)
                ft.ElevatedButton(
                    content=ft.Text("GUARDAR CAMBIOS", weight="bold"),
                    bgcolor=palettet.accent, 
                    color=palettet.primary, 
                    on_click=guardar_cambios,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=15)
        )
        page.dialog = dialogo
        dialogo.open = True
        page.update()

    def crear_gauge(valor, color, label):
        pie = ft.PieChart(
            sections=[
                ft.PieChartSection(valor, color=color, radius=7, title=""),
                ft.PieChartSection(100 - valor, color=ft.colors.with_opacity(0.1, color), radius=7, title=""),
            ],
            center_space_radius=15, height=50, width=50,
        )
        val_text = ft.Text(f"{int(valor)}%", size=8, weight="bold", color=color)
        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=9, weight="bold", color=ft.colors.GREY_700),
                ft.Stack([pie, ft.Container(content=val_text, alignment=ft.alignment.center, width=50, height=50)])
            ], horizontal_alignment="center", spacing=2),
        ), pie, val_text

    def crear_card_servicio(servicio):
        cpu_cont, cpu_pie, cpu_txt = crear_gauge(0, palettet.cpu, "CPU")
        ram_cont, ram_pie, ram_txt = crear_gauge(0, palettet.ram, "RAM")
        red_cont, red_pie, red_txt = crear_gauge(0, palettet.red, "RED")
        
        status_dot = ft.Container(width=8, height=8, border_radius=4, bgcolor=ft.colors.GREY_400)
        status_text = ft.Text("ESPERANDO", size=9, weight="bold", color=ft.colors.GREY_600)
        
        card_container = ft.Container(
            padding=20, bgcolor=ft.colors.WHITE, border_radius=20, border=ft.border.all(1, "#E8E8E8"),
            animate=ft.animation.Animation(300, ft.AnimationCurve.DECELERATE),
        )

        servicios_controles[servicio["nombre"]] = {
            "cpu_sec": cpu_pie.sections, "cpu_val": cpu_txt,
            "ram_sec": ram_pie.sections, "ram_val": ram_txt,
            "red_sec": red_pie.sections, "red_val": red_txt,
            "dot": status_dot, "txt": status_text, "container": card_container
        }

        card_container.content = ft.Column([
            ft.Row([
                ft.Container(content=ft.Icon(ft.icons.DNS_ROUNDED, color=palettet.secundary, size=20), bgcolor=ft.colors.with_opacity(0.08, palettet.secundary), padding=10, border_radius=12),
                ft.Column([ft.Text(servicio["nombre"].upper(), size=14, weight="bold", color=palettet.secundary), ft.Text(servicio["ip"], size=10, color=ft.colors.GREY_500)], expand=True, spacing=0),
                ft.Column([status_dot, status_text], horizontal_alignment="center", spacing=2)
            ]),
            ft.Divider(height=20, thickness=0.5, color="#EEEEEE"),
            ft.Row([cpu_cont, ram_cont, red_cont], alignment="spaceAround"),
            ft.Row([
                ft.IconButton(ft.icons.OPEN_IN_NEW_ROUNDED, icon_size=18, on_click=lambda _: page.launch_url(servicio["url"])),
                ft.IconButton(ft.icons.INSERT_CHART_OUTLINED_ROUNDED, icon_size=18, on_click=lambda _: page.go(f"/logs/{servicio['nombre']}")),
                ft.IconButton(ft.icons.RESTART_ALT_ROUNDED, icon_color="orange"),
                ft.IconButton(icon=ft.icons.TUNE_ROUNDED, icon_color=palettet.accent, on_click=lambda _: abrir_ajustes_umbral(servicio["nombre"])),
            ], alignment="spaceBetween")
        ])
        return ft.Container(content=card_container, col={"sm": 12, "md": 6, "lg": 4})

    async def actualizar_dashboard():
        while True:
            on_count = 0
            for s in SERVICIOS_EMPRESA:
                try:
                    c = servicios_controles[s["nombre"]]
                    conf = CONFIG_SERVICIOS[s["nombre"]]
                    m = obtener_metricas_reales(s["nombre"])

                    for k in ["cpu", "ram", "red"]:
                        val = float(m[k])
                        c[f"{k}_sec"][0].value = val
                        c[f"{k}_sec"][1].value = 100 - val
                        c[f"{k}_val"].value = f"{int(val)}%"
                    
                    valor_actual = float(m[conf["metrica"]])
                    umbral_critico = float(conf["valor"])
                    margen_advertencia = umbral_critico - 10 

                    if m["estado"] == "Offline":
                        c["dot"].bgcolor = ft.colors.RED_700
                        c["txt"].value = "CAÍDO"
                        c["container"].border = ft.border.all(2, ft.colors.RED_700)
                        c["container"].bgcolor = ft.colors.with_opacity(0.05, ft.colors.RED_700)
                    elif valor_actual >= umbral_critico:
                        c["dot"].bgcolor = ft.colors.RED_ACCENT_400
                        c["txt"].value = "¡CRÍTICO!"
                        c["txt"].color = ft.colors.RED_ACCENT_400
                        c["container"].border = ft.border.all(2, ft.colors.RED_ACCENT_400)
                        c["container"].bgcolor = ft.colors.with_opacity(0.08, ft.colors.RED_ACCENT_400)
                        on_count += 1
                    elif valor_actual >= margen_advertencia:
                        c["dot"].bgcolor = ft.colors.ORANGE_700
                        c["txt"].value = "RIESGO"
                        c["txt"].color = ft.colors.ORANGE_700
                        c["container"].border = ft.border.all(2, ft.colors.ORANGE_700)
                        c["container"].bgcolor = ft.colors.with_opacity(0.08, ft.colors.ORANGE_400)
                        on_count += 1
                    else:
                        c["dot"].bgcolor = palettet.accent
                        c["txt"].value = "ACTIVO"
                        c["txt"].color = palettet.accent
                        c["container"].border = ft.border.all(1, "#E8E8E8")
                        c["container"].bgcolor = ft.colors.WHITE
                        on_count += 1
                except: continue
            
            online_count.value = str(on_count)
            offline_count.value = str(len(SERVICIOS_EMPRESA) - on_count)
            page.update()
            await asyncio.sleep(5)

    header = ft.Container(
        gradient=ft.LinearGradient(colors=[palettet.accent, palettet.secundary]),
        padding=ft.padding.only(left=30, right=30, top=40, bottom=50),
        border_radius=ft.border_radius.only(bottom_left=35, bottom_right=35),
        content=ft.Row([ft.Column([ft.Text("MONITOREO JAC & BEL", color=palettet.primary, size=28, weight="bold")], expand=True)])
    )

    def stat_box(label, value_control, icon, color):
        return ft.Container(
            expand=True, bgcolor=ft.colors.WHITE, padding=20, border_radius=22, border=ft.border.all(1, "#E8E8E8"),
            content=ft.Row([ft.Container(content=ft.Icon(icon, color=color, size=22), bgcolor=ft.colors.with_opacity(0.1, color), padding=12, border_radius=15), ft.Column([ft.Text(label, size=9, weight="bold", color=ft.colors.GREY_500), value_control], spacing=0)], spacing=15)
        )

    layout = ft.Column([
        header,
        ft.Container(padding=ft.padding.symmetric(horizontal=30), offset=ft.Offset(0, -0.25), content=ft.Row([
            stat_box("ACTIVOS / RIESGO", online_count, ft.icons.CHECK_CIRCLE_ROUNDED, palettet.accent),
            stat_box("CAÍDOS", offline_count, ft.icons.ERROR_ROUNDED, ft.colors.RED_700),
        ], spacing=20)),
        ft.Container(padding=ft.padding.only(left=30, right=30, bottom=30), content=ft.ResponsiveRow(controls=[crear_card_servicio(s) for s in SERVICIOS_EMPRESA], spacing=20))
    ], scroll=ft.ScrollMode.ADAPTIVE, spacing=0)

    page.run_task(actualizar_dashboard)
    return layout