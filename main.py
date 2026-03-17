import flet as ft
import asyncio
import sys
import warnings
from utilidades.colors import palettet


warnings.filterwarnings("ignore", category=DeprecationWarning)

from views.login_view import login_view
from views.dashboard_view import dashboard_view
from views.logs_view import logs_view  

if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except:
        pass

def main(page: ft.Page):

    page.title = "Monitor de Infraestructura Bel"
    
   
    page.theme_mode = ft.ThemeMode.LIGHT
    
   
    page.window_icon = "logo_bel.png" 

    def route_change(e):
        page.views.clear()
        
        
        if page.route == "/":
            page.views.append(
                ft.View(
                    "/", 
                    [login_view(page)], 
                    vertical_alignment=ft.MainAxisAlignment.CENTER, 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    padding=20
                )
            )
        
       
        elif page.route == "/dashboard":
            page.views.append(
                ft.View(
                    "/dashboard",
                    [dashboard_view(page)],
                    appbar=ft.AppBar(
                        leading=ft.Container(
                            content=ft.Image(src="logo_bel.png", fit=ft.ImageFit.CONTAIN),
                            padding=6
                            
                        ),
                        title=ft.Text("MONITOREO BEL", color=palettet .primary, weight="bold"),
                        bgcolor=palettet .secundary,
                        center_title=True,
                        actions=[
                            ft.IconButton(
                                icon=ft.icons.LOGOUT_ROUNDED, 
                                icon_color=palettet .primary, 
                                on_click=lambda _: page.go("/")
                            )
                        ]
                    )
                )
            )
        
       
        elif page.route.startswith("/logs/"):
           
            nombre_app = page.route.split("/")[-1].replace("%20", " ").replace("+", " ")
            
            page.views.append(
                ft.View(
                    "/logs",
                    [logs_view(page, nombre_app)],
                    appbar=ft.AppBar(
                        title=ft.Text(f"Métricas: {nombre_app}", color=palettet .primary),
                        bgcolor=palettet .accent,
                        center_title=True
                    )
                )
            )
            
        page.update()

    def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
   
    page.go(page.route) 

if __name__ == "__main__":
 
    ft.app(
        target=main, 
        assets_dir="assets",
        view=ft.AppView.WEB_BROWSER 
    )