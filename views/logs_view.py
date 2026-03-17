import flet as ft
from services.zabbix import obtener_metricas_reales
from utilidades.colors import palettet

def logs_view(page, nombre_app):

    datos = obtener_metricas_reales(nombre_app)

   
    if "error" in datos:
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.SIGNAL_WIFI_OFF, size=50, color="red"),
                ft.Text(f"Error: {datos['error']}", size=20, color="red"),
                ft.ElevatedButton("Reintentar", on_click=lambda _: page.go("/dashboard"))
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=50
        )

   
    chart = ft.BarChart(
        bar_groups=[
            ft.BarChartGroup(
                x=0,
                bar_rods=[ft.BarChartRod(from_y=0, to_y=datos['cpu'], color="#47af4c", width=40, border_radius=5)],
            ),
            ft.BarChartGroup(
                x=1,
                bar_rods=[ft.BarChartRod(from_y=0, to_y=datos['ram'], color="#2196f3", width=40, border_radius=5)],
            ),
            ft.BarChartGroup(
                x=2,
                bar_rods=[ft.BarChartRod(from_y=0, to_y=datos['red'], color="#ff9800", width=40, border_radius=5)],
            ),
        ],
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(value=0, label=ft.Text("CPU")),
                ft.ChartAxisLabel(value=1, label=ft.Text("RAM")),
                ft.ChartAxisLabel(value=2, label=ft.Text("RED")),
            ],
        ),
        max_y=100,
        interactive=True,
    )

   
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(f"Estado Actual: {datos['estado']}", color="green", weight="bold"),
                ft.Divider(),
                ft.Text("Consumo de Recursos (%)", size=18, weight="w500"),
                
              
                ft.Container(chart, height=300, padding=20),
                
             
                ft.Row([
                    ft.Icon(ft.icons.CIRCLE, color="#47af4c", size=12),
                    ft.Text(f"CPU: {datos['cpu']}%"),
                    ft.Icon(ft.icons.CIRCLE, color="#2196f3", size=12),
                    ft.Text(f"RAM: {datos['ram']}%"),
                    ft.Icon(ft.icons.CIRCLE, color="#ff9800", size=12),
                    ft.Text(f"Red: {datos['red']}%"),
                ], alignment=ft.MainAxisAlignment.CENTER),
                
                ft.Container(height=20),
                ft.ElevatedButton(
                    "VOLVER AL PANEL", 
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda _: page.go("/dashboard")
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=20
    )