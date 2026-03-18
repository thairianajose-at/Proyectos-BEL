import flet as ft
from services.zabbix import obtener_metricas_reales
from utilidades.colors import palettet
from utilidades.fonts import appFonts 

def logs_view(page, nombre_app):
  
    page.fonts = appFonts.FONTS_DICT
    
    datos = obtener_metricas_reales(nombre_app)

    if "error" in datos:
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.SIGNAL_WIFI_OFF, size=60, color="red"),
                ft.Text(f"Error: {datos['error']}", style=appFonts.HEADER, color="red"),
                ft.ElevatedButton("Reintentar", on_click=lambda _: page.go("/dashboard"))
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )

   
    chart = ft.BarChart(
        bar_groups=[
            ft.BarChartGroup(
                x=0,
                bar_rods=[ft.BarChartRod(from_y=0, to_y=datos['cpu'], color=palettet.cpu, width=40, border_radius=6)],
            ),
            ft.BarChartGroup(
                x=1,
                bar_rods=[ft.BarChartRod(from_y=0, to_y=datos['ram'], color=palettet.ram, width=40, border_radius=6)],
            ),
            ft.BarChartGroup(
                x=2,
                bar_rods=[ft.BarChartRod(from_y=0, to_y=datos['red'], color=palettet.red, width=40, border_radius=6)],
            ),
        ],
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(value=0, label=ft.Text("CPU", style=appFonts.LABEL)),
                ft.ChartAxisLabel(value=1, label=ft.Text("RAM", style=appFonts.LABEL)),
                ft.ChartAxisLabel(value=2, label=ft.Text("RED", style=appFonts.LABEL)),
            ],
        ),
      
        max_y=110, 
        interactive=True,
        animate=500,
    )

    def crear_metrica_badge(icono, etiqueta, valor, color):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icono, color=color, size=20),
                ft.Text(f"{etiqueta}", style=appFonts.BODY, weight="bold"),
                ft.Text(f"{valor}%", style=appFonts.LABEL)
            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=10,
            width=100,
            border_radius=12,
            bgcolor=ft.colors.with_opacity(0.03, "white"),
            
            on_hover=lambda e: setattr(e.control, "offset", ft.transform.Offset(0, -0.1) if e.data == "true" else ft.transform.Offset(0, 0)) or e.control.update(),
            animate_offset=ft.animation.Animation(200),
        )

    return ft.Container(
        content=ft.Column(
            [
             
                ft.Text(f"SISTEMA: {nombre_app.upper()}", style=appFonts.BODY, opacity=0.6),
                ft.Text(f"{datos['estado']}", style=appFonts.HEADER, color="green"),
                
                ft.Divider(height=30, color=ft.colors.TRANSPARENT),


                ft.Container(
                    content=chart,
                    height=350, 
                    padding=ft.padding.only(top=20, bottom=10, left=10, right=10),
                    border_radius=20,
                    bgcolor=ft.colors.with_opacity(0.02, "white"),
                ),
                
                ft.Container(height=20),

              
                ft.Row([
                    crear_metrica_badge(ft.icons.MEMORY, "CPU", datos['cpu'], palettet.cpu),
                    crear_metrica_badge(ft.icons.STORAGE, "RAM", datos['ram'], palettet.ram),
                    crear_metrica_badge(ft.icons.LANGUAGE, "RED", datos['red'], palettet.red),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
                
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO 
        ),
        padding=25,
        expand=True
    )