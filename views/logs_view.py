import flet as ft
from services.lector_api import obtener_metricas_reales
from utilidades.colors import palettet
from utilidades.fonts import appFonts 

def logs_view(page: ft.Page, nombre_app: str):
    # Sincronizamos fuentes y configuración de página
    page.fonts = appFonts.FONTS_DICT
    
    # 1. OBTENCIÓN DE DATOS (Sincronizado al ritmo del Dashboard)
    datos = obtener_metricas_reales(nombre_app)

    # --- MANEJO DE ERRORES ---
    if "error" in datos:
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.SIGNAL_WIFI_OFF, size=60, color=palettet.danger),
                ft.Text(f"Error: {datos['error']}", style=appFonts.HEADER, color=palettet.danger),
                ft.ElevatedButton("Reintentar", on_click=lambda _: page.go("/dashboard"))
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center, expand=True
        )

    # --- GRÁFICA DE BARRAS (Tus barras y colores originales) ---
    chart = ft.BarChart(
        bar_groups=[
            ft.BarChartGroup(x=0, bar_rods=[ft.BarChartRod(from_y=0, to_y=datos.get('cpu', 0), color=palettet.track_1, width=35, border_radius=6)]),
            ft.BarChartGroup(x=1, bar_rods=[ft.BarChartRod(from_y=0, to_y=datos.get('ram', 0), color=palettet.track_2, width=35, border_radius=6)]),
            ft.BarChartGroup(x=2, bar_rods=[ft.BarChartRod(from_y=0, to_y=datos.get('red', 0), color=palettet.track_3, width=35, border_radius=6)]),
            ft.BarChartGroup(x=3, bar_rods=[ft.BarChartRod(from_y=0, to_y=datos.get('dl', 0), color=palettet.track_4, width=35, border_radius=6)]),
            ft.BarChartGroup(x=4, bar_rods=[ft.BarChartRod(from_y=0, to_y=datos.get('de', 0), color=palettet.track_4, width=35, border_radius=6)]),
        ],
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(value=0, label=ft.Text("CPU", style=appFonts.LABEL, color=palettet.text_sub)),
                ft.ChartAxisLabel(value=1, label=ft.Text("RAM", style=appFonts.LABEL, color=palettet.text_sub)),
                ft.ChartAxisLabel(value=2, label=ft.Text("RED", style=appFonts.LABEL, color=palettet.text_sub)),
                ft.ChartAxisLabel(value=3, label=ft.Text("D-L", style=appFonts.LABEL, color=palettet.text_sub)),
                ft.ChartAxisLabel(value=4, label=ft.Text("D-E", style=appFonts.LABEL, color=palettet.text_sub)),
            ],
        ),
        max_y=100,
        interactive=True,
        animate=ft.animation.Animation(500, ft.AnimationCurve.DECELERATE),
    )

    # --- FUNCIÓN PARA LOS BADGES ---
    def crear_metrica_badge(icono, etiqueta, valor, color):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icono, color=color, size=22),
                ft.Text(etiqueta, style=appFonts.BODY, weight="bold", color=palettet.text_main, size=11),
                ft.Text(f"{int(valor)}%", style=appFonts.LABEL, color=palettet.text_sub, size=12)
            ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15, border_radius=15, bgcolor=ft.colors.with_opacity(0.08, color), expand=True
        )

    color_estado = palettet.success if datos.get('estado') == "Online" else palettet.danger

    return ft.Container(
        expand=True,
        bgcolor=palettet.primary,
        padding=25,
        content=ft.Column(
            [
                # HEADER CON TU ICONO ORIGINAL
                ft.Row([
                    ft.IconButton(
                        icon=ft.icons.ARROW_BACK_IOS_NEW_ROUNDED, 
                        icon_color=palettet.secundary,
                        on_click=lambda _: page.go("/dashboard")
                    ),
                    ft.Container(
                        content=ft.Icon(ft.icons.ANALYTICS_ROUNDED, size=30, color=palettet.primary),
                        bgcolor=palettet.accent,
                        padding=10,
                        border_radius=12,
                    ),
                    ft.Column([
                        # Corrección del error de letter_spacing
                        ft.Text("MÉTRICAS DEL SISTEMA", size=10, weight="bold", color=palettet.text_sub, style=ft.TextStyle(letter_spacing=1.2)),
                        ft.Text(nombre_app.upper(), size=22, weight="bold", color=palettet.secundary),
                    ], spacing=0, expand=True)
                ], alignment=ft.MainAxisAlignment.START),

                ft.Divider(height=10, color=ft.colors.TRANSPARENT),

                # STATUS BADGE
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=10, height=10, border_radius=5, bgcolor=color_estado),
                        ft.Text(f"ESTADO: {datos.get('estado', 'N/A').upper()}", size=11, weight="bold", color=color_estado)
                    ], tight=True),
                    padding=ft.padding.symmetric(horizontal=15, vertical=8),
                    border_radius=20, border=ft.border.all(1, color_estado)
                ),

                ft.Container(height=20),

                # GRÁFICA PRINCIPAL
                ft.Container(
                    content=chart,
                    height=300,
                    padding=25,
                    border_radius=30,
                    bgcolor=ft.colors.with_opacity(0.03, ft.colors.BLACK),
                    border=ft.border.all(1, ft.colors.with_opacity(0.1, palettet.secundary))
                ),

                ft.Container(height=20),

                # MÉTRICAS EN TIEMPO REAL (Badges)
                ft.ResponsiveRow([
                    ft.Column([crear_metrica_badge(ft.icons.MEMORY_ROUNDED, "CPU", datos.get('cpu', 0), palettet.track_1)], col={"xs": 6, "md": 2.4}),
                    ft.Column([crear_metrica_badge(ft.icons.STORAGE_ROUNDED, "RAM", datos.get('ram', 0), palettet.track_2)], col={"xs": 6, "md": 2.4}),
                    ft.Column([crear_metrica_badge(ft.icons.LANGUAGE_ROUNDED, "RED", datos.get('red', 0), palettet.track_3)], col={"xs": 4, "md": 2.4}),
                    ft.Column([crear_metrica_badge(ft.icons.DOWNLOAD_ROUNDED, "D-L", datos.get('dl', 0), palettet.track_4)], col={"xs": 4, "md": 2.4}),
                    ft.Column([crear_metrica_badge(ft.icons.UPLOAD_ROUNDED, "D-E", datos.get('de', 0), palettet.track_4)], col={"xs": 4, "md": 2.4}),
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                
                ft.Container(height=30),
                ft.Text("SISTEMA DE MONITOREO JAC & BEL v2.0", size=9, color=palettet.text_sub, weight="bold")
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ADAPTIVE
        )
    )