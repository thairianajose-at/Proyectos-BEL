import flet as ft
from services.zabbix import SERVICIOS_EMPRESA
from utilidades.colors import palettet
from utilidades.fonts import appFonts

def dashboard_view(page):
    page.fonts = appFonts.FONTS_DICT

    def ir_a_metricas(nombre):
        page.go(f"/logs/{nombre}")

    cards = []
    for servicio in SERVICIOS_EMPRESA:
        
        
        btn_style = ft.ButtonStyle(
            color={
                ft.MaterialState.HOVERED: palettet.primary,
                ft.MaterialState.DEFAULT: palettet.secundary,
            },
            bgcolor={
                ft.MaterialState.HOVERED: palettet.secundary,
                ft.MaterialState.DEFAULT: ft.colors.TRANSPARENT,
            },
            padding=ft.padding.symmetric(horizontal=10),
            shape=ft.RoundedRectangleBorder(radius=0),
            animation_duration=300,
        )

        card_content = ft.Card(
            elevation=3,
            content=ft.Container(
                padding=15,
                border_radius=12,
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(
                            ft.icons.DASHBOARD_ROUNDED, 
                            color=palettet.secundary, 
                            size=30
                        ),
                        title=ft.Text(
                            servicio["nombre"], 
                            style=appFonts.LABEL, 
                            weight="bold"
                        ),
                        subtitle=ft.Text(
                            f"IP: {servicio['ip']}", 
                            style=appFonts.BODY,
                            color="grey"
                        ),
                    ),
                    
                    ft.Row(
                        [
                            ft.Container(
                                border=ft.border.all(1, palettet.secundary),
                                border_radius=8,
                                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                                width=240, 
                                height=40,
                                content=ft.Row(
                                    spacing=0,
                                    controls=[
                                    
                                        ft.Container(
                                            expand=True,
                                            content=ft.TextButton(
                                                content=ft.Row([
                                                    ft.Icon(ft.icons.BAR_CHART_ROUNDED, size=16),
                                                    ft.Text("LOGS", size=10, weight="bold", font_family="Arimo"),
                                                ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                                                style=btn_style,
                                                on_click=lambda _, n=servicio["nombre"]: ir_a_metricas(n)
                                            ),
                                        ),
                                        
                                        ft.VerticalDivider(width=1, color=palettet.secundary, thickness=1),
                                        
                                        
                                        ft.Container(
                                            expand=True,
                                            content=ft.TextButton(
                                                content=ft.Row([
                                                    ft.Icon(ft.icons.LANGUAGE_ROUNDED, size=16),
                                                    ft.Text("WEB", size=10, weight="bold", font_family="Arimo"),
                                                ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                                                style=btn_style,
                                                on_click=lambda _, url=servicio["url"]: page.launch_url(url)
                                            ),
                                        ),
                                    ],
                                )
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END, 
                    )
                ])
            )
        )

        cards.append(
            ft.Container(
                content=card_content,
                on_hover=lambda e: setattr(e.control, "scale", 1.01 if e.data == "true" else 1.0) or e.control.update(),
                animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
            )
        )

    return ft.Container(
        content=ft.Column(
            [
            
                ft.Row([
                    ft.Image(src="logo_bel.png", width=50, height=50),
                    ft.Column([
                        ft.Text("MONITOR DE INFRAESTRUCTURA", style=appFonts.HEADER, size=20, color=palettet.secundary),
                        ft.Text("Panel de Servicios Activos", style=appFonts.BODY, color="grey"),
                    ], spacing=0)
                ]),
                
                ft.Divider(color=palettet.secundary, height=10),
                
                ft.Column(
                    controls=cards, 
                    scroll=ft.ScrollMode.ADAPTIVE, 
                    expand=True,
                    spacing=10
                ),
            ],
            spacing=15,
        ),
        padding=20,
        expand=True
    )