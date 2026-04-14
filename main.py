import flet as ft
import asyncio
import sys
import warnings
from database.modelo import crear_tablas
from database.seed import ejecutar_seed 
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

def inicializar_sistema():
    crear_tablas()  
    ejecutar_seed() 

def main(page: ft.Page):
    inicializar_sistema()
 
    page.title = "Monitor JAC & BEL"
    page.theme_mode = ft.ThemeMode.LIGHT 
    page.fonts = appFonts.FONTS_DICT
    page.theme = ft.Theme(font_family=appFonts.ARIMO)
    
    page.window_width = 1250
    page.window_height = 850

    def route_change(e):
        # Limpieza absoluta de la lista de vistas para evitar pantallas blancas
        page.views.clear()
        
        user_name = page.session.get("user_name")
        user_rol = page.session.get("user_rol")
        
        # RUTA: LOGIN (Raíz o vacía)
        if page.route == "/" or page.route == "":
            page.views.append(
                ft.View(
                    "/", 
                    [login_view(page)], 
                    padding=0
                )
            )
     
        # RUTA: DASHBOARD 
        elif page.route == "/dashboard":
            if not user_name:
                page.go("/") # Redirigir si no hay sesión
                return

            page.views.append(
                ft.View(
                    "/dashboard", 
                    [dashboard_view(page)],
                    padding=0
                )
            )
        
        # RUTA: LOGS
        elif page.route.startswith("/logs/"):
            if not user_name or user_rol != "admin":
                page.go("/dashboard")
                return

            nombre_raw = page.route.split("/")[-1]
            nombre_app = nombre_raw.replace("%20", " ").replace("+", " ")
            
            page.views.append(
                ft.View(
                    page.route, 
                    [logs_view(page, nombre_app)],
                    padding=0
                )
            )
        
        page.update()

    page.on_route_change = route_change
    # Iniciamos la navegación
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")