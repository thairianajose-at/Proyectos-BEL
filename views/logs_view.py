import flet as ft
import asyncio
from services.lector_api import obtener_metricas_reales
from utilidades.colors import palettet
from utilidades.fonts import appFonts 

def logs_view(page: ft.Page, nombre_app: str):
    page.fonts = appFonts.FONTS_DICT
    
    # control de estado
    # Diccionario para que sea mutable y fácil de detener
    estado = {"loop_activo": True}
    controles_badges = {} 

    # funcion para los badges
    def crear_metrica_badge(icono, etiqueta, valor, color, clave_ref):
        texto_valor = ft.Text(f"{int(valor)}%", style=appFonts.LABEL, color=palettet.text_sub, size=12)
        container = ft.Container(
            content=ft.Column([
                ft.Icon(icono, color=color, size=22),
                ft.Text(etiqueta, style=appFonts.BODY, weight="bold", color=palettet.text_main, size=11),
                texto_valor
            ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15, border_radius=15, bgcolor=ft.colors.with_opacity(0.08, color), expand=True
        )
        controles_badges[clave_ref] = texto_valor
        return container

    # Gráfica de barras
    chart = ft.BarChart(
        bar_groups=[
            ft.BarChartGroup(x=0, bar_rods=[ft.BarChartRod(from_y=0, to_y=0, color=palettet.track_1, width=35, border_radius=6)]),
            ft.BarChartGroup(x=1, bar_rods=[ft.BarChartRod(from_y=0, to_y=0, color=palettet.track_2, width=35, border_radius=6)]),
            ft.BarChartGroup(x=2, bar_rods=[ft.BarChartRod(from_y=0, to_y=0, color=palettet.track_3, width=35, border_radius=6)]),
            ft.BarChartGroup(x=3, bar_rods=[ft.BarChartRod(from_y=0, to_y=0, color=palettet.track_4, width=35, border_radius=6)]),
            ft.BarChartGroup(x=4, bar_rods=[ft.BarChartRod(from_y=0, to_y=0, color=palettet.track_4, width=35, border_radius=6)]),
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
        animate=ft.animation.Animation(500, ft.AnimationCurve.DECELERATE),
    )

    dot_estado = ft.Container(width=10, height=10, border_radius=5, bgcolor=ft.colors.GREY_400)
    texto_estado = ft.Text("ESTADO: CARGANDO...", size=11, weight="bold", color=ft.colors.GREY_400)

    #Loop actualizacion cada 5seg
    async def update_loop():
        await asyncio.sleep(0.5)
        while estado["loop_activo"]:
            try:
                if not page: break
                
                datos = obtener_metricas_reales(nombre_app)
                
                if "error" not in datos and chart.page: # Validación .page para evitar crashes
                    # Gráfica
                    chart.bar_groups[0].bar_rods[0].to_y = datos.get('cpu', 0)
                    chart.bar_groups[1].bar_rods[0].to_y = datos.get('ram', 0)
                    chart.bar_groups[2].bar_rods[0].to_y = datos.get('red', 0)
                    chart.bar_groups[3].bar_rods[0].to_y = datos.get('dl', 0)
                    chart.bar_groups[4].bar_rods[0].to_y = datos.get('de', 0)
                    
                    # Badges
                    controles_badges["cpu"].value = f"{int(datos.get('cpu', 0))}%"
                    controles_badges["ram"].value = f"{int(datos.get('ram', 0))}%"
                    controles_badges["red"].value = f"{int(datos.get('red', 0))}%"
                    controles_badges["dl"].value = f"{int(datos.get('dl', 0))}%"
                    controles_badges["de"].value = f"{int(datos.get('de', 0))}%"
                    
                    # Estado
                    es_online = datos.get('estado') == "Online"
                    color_status = palettet.success if es_online else palettet.danger
                    dot_estado.bgcolor = color_status
                    texto_estado.value = f"ESTADO: {datos.get('estado', 'N/A').upper()}"
                    texto_estado.color = color_status
                    
                    page.update()
                
                # AQue se actualice cada 5 seg
                await asyncio.sleep(5) 
            except Exception as e:
                print(f"Loop detenido o error: {e}")
                break

    #Acción de salida
    def volver_dashboard(e):
        estado["loop_activo"] = False # Detenemos el loop de forma segura
        page.go("/dashboard")

    # Construcioon de la vista
    main_content = ft.Column(
        [
            ft.Row([
                ft.IconButton(
                    icon=ft.icons.ARROW_BACK_IOS_NEW_ROUNDED, 
                    icon_color=palettet.secundary,
                    on_click=volver_dashboard # Llamamos a la función de salida
                ),
                ft.Container(
                    content=ft.Icon(ft.icons.ANALYTICS_ROUNDED, size=30, color=palettet.primary),
                    bgcolor=palettet.accent, padding=10, border_radius=12,
                ),
                ft.Column([
                    ft.Text("MÉTRICAS DEL SISTEMA", size=10, weight="bold", color=palettet.text_sub, style=ft.TextStyle(letter_spacing=1.2)),
                    ft.Text(nombre_app.upper(), size=22, weight="bold", color=palettet.secundary),
                ], spacing=0, expand=True)
            ], alignment=ft.MainAxisAlignment.START),

            ft.Divider(height=10, color=ft.colors.TRANSPARENT),

            ft.Container(
                content=ft.Row([dot_estado, texto_estado], tight=True),
                padding=ft.padding.symmetric(horizontal=15, vertical=8),
                border_radius=20, border=ft.border.all(1, ft.colors.with_opacity(0.2, palettet.text_sub))
            ),

            ft.Container(height=20),

            ft.Container(
                content=chart, height=300, padding=25, border_radius=30,
                bgcolor=ft.colors.with_opacity(0.03, ft.colors.BLACK),
                border=ft.border.all(1, ft.colors.with_opacity(0.1, palettet.secundary))
            ),

            ft.Container(height=20),

            ft.ResponsiveRow([
                ft.Column([crear_metrica_badge(ft.icons.MEMORY_ROUNDED, "CPU", 0, palettet.track_1, "cpu")], col={"xs": 6, "md": 2.4}),
                ft.Column([crear_metrica_badge(ft.icons.STORAGE_ROUNDED, "RAM", 0, palettet.track_2, "ram")], col={"xs": 6, "md": 2.4}),
                ft.Column([crear_metrica_badge(ft.icons.LANGUAGE_ROUNDED, "RED", 0, palettet.track_3, "red")], col={"xs": 4, "md": 2.4}),
                ft.Column([crear_metrica_badge(ft.icons.DOWNLOAD_ROUNDED, "D-L", 0, palettet.track_4, "dl")], col={"xs": 4, "md": 2.4}),
                ft.Column([crear_metrica_badge(ft.icons.UPLOAD_ROUNDED, "D-E", 0, palettet.track_4, "de")], col={"xs": 4, "md": 2.4}),
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Container(height=30),
            ft.Text("SISTEMA DE MONITOREO JAC & BEL v2.0", size=9, color=palettet.text_sub, weight="bold")
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.ADAPTIVE
    )

    page.run_task(update_loop)

    return ft.Container(expand=True, bgcolor=palettet.primary, padding=25, content=main_content)