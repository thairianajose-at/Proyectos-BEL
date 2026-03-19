import flet as ft
from services.zabbix import SERVICIOS_EMPRESA, obtener_metricas_reales
from utilidades.colors import palettet
from utilidades.fonts import appFonts

def dashboard_view(page: ft.Page):
    
    page.fonts = appFonts.FONTS_DICT

    def ir_a_metricas(nombre):
        page.go(f"/logs/{nombre}")

  
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = ft.colors.SURFACE_VARIANT if is_dark else ft.colors.WHITE
    title_color = ft.colors.WHITE if is_dark else palettet.secundary

    cards = []
    for servicio in SERVICIOS_EMPRESA:
       
        metricas = obtener_metricas_reales(servicio["nombre"])
        cpu_val = metricas.get("cpu", 0) / 100
        ram_val = metricas.get("ram", 0) / 100
        estado = metricas.get("estado", "Offline")

      
        btn_style = ft.ButtonStyle(
            color={
                ft.MaterialState.HOVERED: palettet.primary,
                ft.MaterialState.DEFAULT: palettet.secundary,
            },
            bgcolor={
                ft.MaterialState.HOVERED: palettet.secundary,
                ft.MaterialState.DEFAULT: ft.colors.TRANSPARENT,
            },
            padding=ft.padding.all(0),
            shape=ft.RoundedRectangleBorder(radius=0),
            animation_duration=300,
        )

        card_content = ft.Card(
            elevation=3,
            content=ft.Container(
                padding=15,
                border_radius=12,
                bgcolor=card_bg,
                content=ft.Column([
                    
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.DNS_ROUNDED, color=palettet.secundary, size=30),
                        title=ft.Text(servicio["nombre"], style=appFonts.LABEL, weight="bold", color=title_color),
                        subtitle=ft.Text(f"IP: {servicio['ip']}", style=appFonts.BODY, color="grey"),
                        trailing=ft.Container(
                            content=ft.Text(estado, size=9, weight="bold", color="white"),
                            bgcolor=palettet.red if estado == "Online" else "red",
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=5
                        ),
                    ),
                    
                    ft.Divider(height=1, thickness=0.5, color=palettet.secundary),
                    
                
                    ft.Container(
                        padding=ft.padding.symmetric(vertical=10, horizontal=5),
                        content=ft.Column([
                          
                            ft.Row([
                                ft.Text("CPU", size=10, weight="bold", color=title_color),
                                ft.Text(f"{int(cpu_val*100)}%", size=10, weight="bold", color=palettet.cpu),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.ProgressBar(value=cpu_val, color=palettet.cpu, bgcolor=ft.colors.BLACK12, height=8),
                            
                            ft.Container(height=8),
                        
                            ft.Row([
                                ft.Text("RAM", size=10, weight="bold", color=title_color),
                                ft.Text(f"{int(ram_val*100)}%", size=10, weight="bold", color=palettet.ram),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.ProgressBar(value=ram_val, color=palettet.ram, bgcolor=ft.colors.BLACK12, height=8),
                        ])
                    ),
                    
                    
                    ft.Row([
                        ft.Container(
                            border=ft.border.all(1, palettet.secundary),
                            border_radius=8,
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                            width=200, 
                            height=35,
                            content=ft.Row([
                                ft.Container(
                                    expand=True,
                                    content=ft.TextButton(
                                        content=ft.Text("LOGS", size=9, weight="bold"),
                                        style=btn_style,
                                        on_click=lambda _, n=servicio["nombre"]: ir_a_metricas(n)
                                    ),
                                ),
                                ft.VerticalDivider(width=1, color=palettet.secundary, thickness=1),
                                ft.Container(
                                    expand=True,
                                    content=ft.TextButton(
                                        content=ft.Text("WEB", size=9, weight="bold"),
                                        style=btn_style,
                                        on_click=lambda _, url=servicio["url"]: page.launch_url(url)
                                    ),
                                ),
                            ], spacing=0)
                        )
                    ], alignment=ft.MainAxisAlignment.END)
                ])
            )
        )

  
        cards.append(
            ft.Container(
                content=card_content,
                on_hover=lambda e: setattr(e.control, "scale", 1.02 if e.data == "true" else 1.0) or e.control.update(),
                animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
            )
        )

    return ft.Container(
        content=ft.Column([
           
            ft.Row([
                ft.Image(src="logo_bel.png", width=50, height=50),
                ft.Column([
                    ft.Text("MONITOR DE INFRAESTRUCTURA", style=appFonts.HEADER, size=20, color=palettet.secundary),
                    ft.Text("Visualización de métricas en tiempo real", style=appFonts.BODY, color="grey"),
                ], spacing=0)
            ]),
            
            ft.Divider(color=palettet.secundary, height=10),
            
          
            ft.ResponsiveRow(
                controls=[
                    ft.Column([card], col={"sm": 12, "md": 6, "lg": 4}) for card in cards
                ],
                spacing=15,
                run_spacing=15,
            ),
        ], spacing=15, scroll=ft.ScrollMode.ADAPTIVE),
        padding=20,
        expand=True
    )