import flet as ft
import asyncio
import sys
import warnings

# Importaciones de tu estructura de proyecto
from utilidades.colors import palettet
from utilidades.fonts import appFonts
from views.login_view import login_view
from views.dashboard_view import dashboard_view
from views.logs_view import logs_view 


warnings.filterwarnings("ignore", category=DeprecationWarning)


if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

def main(page: ft.Page):
    page.title = "Monitor de Infraestructura Bel"
    page.window_icon = "logo_bel.png"
    page.theme_mode = ft.ThemeMode.LIGHT 
    

    page.fonts = appFonts.FONTS_DICT
    page.theme = ft.Theme(font_family=appFonts.ARIMO)
    page.dark_theme = ft.Theme(font_family=appFonts.ARIMO)

    def route_change(e):
        page.views.clear()
        
        
        if page.route == "/":
            page.views.append(
                ft.View(
                    route="/", 
                    controls=[login_view(page)], 
                    vertical_alignment=ft.MainAxisAlignment.CENTER, 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    padding=20
                )
            )
        
       
        elif page.route == "/dashboard":
            page.views.append(
                ft.View(
                    route="/dashboard",
                    controls=[dashboard_view(page)],
                    appbar=ft.AppBar(
                        leading_width=70,
                        leading=ft.Container(
                            content=ft.Image(
                                src="logo_bel.png", 
                                fit=ft.ImageFit.CONTAIN
                            ),
                            
                            padding=ft.padding.only(left=15, top=10, bottom=10),
                        ),
                        title=ft.Text(
                            "Monitoreo Bel", 
                            color=palettet.primary, 
                            weight=ft.FontWeight.BOLD,
                            size=20,
                        ),
                        bgcolor=palettet.secundary,
                        center_title=True,
                        elevation=0.5,
                        actions=[
                            ft.IconButton(
                                icon=ft.icons.LOGOUT_ROUNDED, 
                                icon_color=palettet.primary, 
                                tooltip="Cerrar Sesión",
                                on_click=lambda _: page.go("/")
                            ),
                            
                            ft.Container(width=10)
                        ]
                    )
                )
            )
        
     
        elif page.route.startswith("/logs/"):
         
            nombre_app = page.route.split("/")[-1].replace("%20", " ").replace("+", " ")
            
            page.views.append(
                ft.View(
                    route="/logs",
                    controls=[logs_view(page, nombre_app)],
                    appbar=ft.AppBar(
                        leading_width=70,
                        leading=ft.Container(
                            content=ft.Image(
                                src="logo_bel.png", 
                                fit=ft.ImageFit.CONTAIN
                            ),
                            padding=ft.padding.only(left=15, top=10, bottom=10),
                        ),
                        title=ft.Text(
                            f"Métricas: {nombre_app}", 
                            color=palettet.primary,
                            size=18,
                            weight=ft.FontWeight.W_600
                        ),
                        bgcolor=palettet.secundary,
                        center_title=True,
                        elevation=0.5,
                     
                        actions=[
                            ft.IconButton(
                                icon=ft.icons.ARROW_BACK_IOS_NEW_ROUNDED,
                                icon_color=palettet.primary,
                                tooltip="Volver al Dashboard",
                                on_click=lambda _: page.go("/dashboard")
                            ),
                            ft.Container(width=10)
                        ]
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