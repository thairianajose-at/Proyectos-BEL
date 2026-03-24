import flet as ft
from services.zabbix import SERVICIOS_EMPRESA, obtener_metricas_reales
from utilidades.colors import palettet
from utilidades.fonts import appFonts

def dashboard_view(page: ft.Page):
    page.fonts = appFonts.FONTS_DICT
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = ft.colors.SURFACE_VARIANT if is_dark else ft.colors.WHITE
    
    servicios_controles = {}

    def crear_card_monitoreo(servicio):
    
        cpu_rod = ft.BarChartRod(from_y=0, to_y=0, color=palettet.cpu, width=12, border_radius=4)
        ram_rod = ft.BarChartRod(from_y=0, to_y=0, color=palettet.ram, width=12, border_radius=4)
        red_rod = ft.BarChartRod(from_y=0, to_y=0, color=palettet.red, width=12, border_radius=4)

        chart = ft.BarChart(
            bar_groups=[
                ft.BarChartGroup(x=0, bar_rods=[cpu_rod]),
                ft.BarChartGroup(x=1, bar_rods=[ram_rod]),
                ft.BarChartGroup(x=2, bar_rods=[red_rod]),
            ],
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=0, label=ft.Text("C", size=8, weight="bold")),
                    ft.ChartAxisLabel(value=1, label=ft.Text("R", size=8, weight="bold")),
                    ft.ChartAxisLabel(value=2, label=ft.Text("N", size=8, weight="bold")),
                ],
            ),
            max_y=110,
            animate=1000,
            height=80,
            width=100,
        )

        status_text = ft.Text("...", size=9, weight="bold", color="white")
        status_container = ft.Container(
            content=status_text, bgcolor=ft.colors.GREY_400,
            padding=ft.padding.symmetric(horizontal=8, vertical=4), border_radius=5
        )

        servicios_controles[servicio["nombre"]] = {
            "cpu_rod": cpu_rod, "ram_rod": ram_rod, "red_rod": red_rod,
            "status_container": status_container, "status_text": status_text
        }

        return ft.Container(
            on_hover=lambda e: setattr(e.control, "scale", 1.02 if e.data == "true" else 1.0) or e.control.update(),
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
            content=ft.Card(
                elevation=3,
                content=ft.Container(
                    padding=15, bgcolor=card_bg, border_radius=12,
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.DNS_ROUNDED, color=palettet.secundary),
                            title=ft.Text(servicio["nombre"], size=14, weight="bold"),
                            subtitle=ft.Text(servicio["ip"], size=11),
                            trailing=status_container,
                        ),
                        ft.Row([
                            ft.Column([
                                ft.Text("Rendimiento", size=10, weight="bold", opacity=0.7),
                                chart
                            ], expand=True),
                            ft.VerticalDivider(),
                            ft.Column([
                                ft.IconButton(ft.icons.REMOVE_RED_EYE_ROUNDED, 
                                            icon_color=palettet.accent,
                                            on_click=lambda _: page.go(f"/logs/{servicio['nombre']}")),
                                ft.IconButton(ft.icons.LANGUAGE_ROUNDED, 
                                            icon_color=palettet.secundary,
                                            on_click=lambda _: page.launch_url(servicio["url"])),
                            ], alignment=ft.MainAxisAlignment.CENTER)
                        ], height=100)
                    ])
                )
            )
        )

    async def actualizar_dashboard():
        for s in SERVICIOS_EMPRESA:
            try:
                m = obtener_metricas_reales(s["nombre"])
                c = servicios_controles[s["nombre"]]
                
                c["cpu_rod"].to_y = m.get("cpu", 0)
                c["ram_rod"].to_y = m.get("ram", 0)
                c["red_rod"].to_y = m.get("red", 0)
                
                estado = m.get("estado", "Offline")
                c["status_text"].value = estado
                c["status_container"].bgcolor = palettet.red if estado == "Online" else "red"
                page.update()
            except:
                pass

    cards_ui = [ft.Column([crear_card_monitoreo(s)], col={"sm": 12, "md": 6, "lg": 4}) for s in SERVICIOS_EMPRESA]

    layout = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Image(src="logo_bel.png", width=40, height=40),
                ft.Text("Monitor de infraestructura BEL", style=appFonts.HEADER, size=22),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(height=1),
            ft.ResponsiveRow(controls=cards_ui, spacing=15),
        ], scroll=ft.ScrollMode.ADAPTIVE),
        padding=20, expand=True
    )

    page.run_task(actualizar_dashboard)
    return layout