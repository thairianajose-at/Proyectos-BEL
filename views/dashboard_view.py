import flet as ft
from services.zabbix import SERVICIOS_EMPRESA
from utilidades.colors import palettet

def dashboard_view(page):
    
    def ir_a_metricas(nombre):
        page.go(f"/logs/{nombre}")

    cards = []
    for servicio in SERVICIOS_EMPRESA:
        cards.append(
            ft.Card(
                elevation=2,
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.DASHBOARD_ROUNDED, color=palettet.secundary, size=30),
                            title=ft.Text(servicio["nombre"], weight="bold", size=16),
                            subtitle=ft.Text(f"IP: {servicio['ip']}", color="grey"),
                        ),
                       
                        ft.Row(
                            [
                                ft.TextButton(
                                    "VER MÉTRICAS", 
                                    style=ft.ButtonStyle(
                                        color={
                                            ft.MaterialState.HOVERED: palettet.primary,
                                            ft.MaterialState.DEFAULT: palettet.secundary,
                                        },
                                        bgcolor={
                                            ft.MaterialState.HOVERED: palettet.secundary,
                                            ft.MaterialState.DEFAULT: palettet.primary,
                                        },
                                        overlay_color=palettet.secundary,
                                    ),
                                    icon=ft.icons.INSERT_CHART_OUTLINED,
                                    on_click=lambda _, n=servicio["nombre"]: ir_a_metricas(n)
                                ),
                                ft.TextButton(
                                    "WEB", 
                                    style=ft.ButtonStyle(
                                        color={
                                            ft.MaterialState.HOVERED: palettet.primary,
                                            ft.MaterialState.DEFAULT: palettet.secundary, 
                                        },
                                        bgcolor={
                                            ft.MaterialState.HOVERED: palettet.secundary,
                                            ft.MaterialState.DEFAULT: palettet.primary, 
                                        },
                                    ),
                                    icon=ft.icons.LANGUAGE,
                                    on_click=lambda _, url=servicio["url"]: page.launch_url(url)
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        )
                    ]) 
                )
            ) 
        )

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Image(
                            src="logo_bel.png", 
                            width=50,
                            height=50,
                            fit=ft.ImageFit.CONTAIN,
                        ),
                        ft.Column([
                            ft.Text("MONITOR DE INFRAESTRUCTURA", size=22, weight="bold", color=palettet.secundary),
                            ft.Text("Gestión de Infraestructura", size=12, color="grey"),
                        ], spacing=0)
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                
                ft.Divider(color=palettet.secundary, height=20),
                
                ft.Text("Servicios Activos", size=18, weight="w500"),
               
                ft.Column(
                    controls=cards,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True 
                ),
            ],
            spacing=15,
        ),
        padding=20,
        expand=True
    )