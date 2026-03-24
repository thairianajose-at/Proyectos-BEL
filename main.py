import flet as ft
import asyncio
import sys
import warnings
from database.modelo import crear_tablas, Usuario
from database.config import SessionLocal, engine
from controladores.crud import crear_usuario

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
    """Asegura la estructura de la BD y precarga el equipo de infraestructura"""
    crear_tablas()  
    db = SessionLocal()
    try:
        usuario_existente = db.query(Usuario).first()
        if not usuario_existente:
            print(" Configuración inicial: Cargando personal de infraestructura...")
            crear_usuario("admin", "admin123", rol="admin")
            crear_usuario("wilder1", "wilder1234", rol="devops")
            print("Usuarios cargados exitosamente.")
    except Exception as e:
        print(f"Error en inicialización: {e}")
    finally:
        db.close()

def main(page: ft.Page):
   
    inicializar_sistema()
 
    page.title = "Monitor de Infraestructura Bel"
    page.theme_mode = ft.ThemeMode.LIGHT 
    page.fonts = appFonts.FONTS_DICT
    page.theme = ft.Theme(font_family=appFonts.ARIMO)
    
   
    page.window_width = 1200
    page.window_height = 800
    page.window_min_width = 800
    page.window_min_height = 600

    def route_change(e):
        page.views.clear()
        
        
        if page.route == "/":
            page.views.append(
                ft.View(
                    route="/", 
                    controls=[login_view(page)], 
                    vertical_alignment=ft.MainAxisAlignment.CENTER, 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    padding=0 
                )
            )
     
        
        elif page.route == "/dashboard":
         
            if not page.session.get("user_name"):
                page.go("/")
                return

            page.views.append(
                ft.View(
                    route="/dashboard",
                    controls=[dashboard_view(page)],
                    appbar=ft.AppBar(
                        leading_width=70,
                        leading=ft.Container(
                            content=ft.Image(src="logo_bel.png", fit=ft.ImageFit.CONTAIN),
                            padding=ft.padding.only(left=15, top=10, bottom=10),
                        ),
                        title=ft.Text("Monitoreo Bel - Panel Principal", 
                                    color=palettet.primary, weight="bold", size=20),
                        bgcolor=palettet.secundary,
                        center_title=True,
                        actions=[
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.icons.ACCOUNT_CIRCLE_OUTLINED, color=palettet.primary, size=20),
                                    ft.Text(f"{page.session.get('user_name')}".upper(), 
                                           color=palettet.primary, weight="bold"),
                                ]),
                                padding=ft.padding.only(right=10)
                            ),
                            ft.IconButton(
                                icon=ft.icons.LOGOUT_ROUNDED, 
                                icon_color=palettet.primary, 
                                tooltip="Cerrar Sesión",
                                on_click=lambda _: [page.session.clear(), page.go("/")]
                            ),
                            ft.Container(width=10)
                        ]
                    )
                )
            )
        
        
        elif page.route.startswith("/logs/"):
            if not page.session.get("user_name"):
                page.go("/")
                return

            
            nombre_raw = page.route.split("/")[-1]
            nombre_app = nombre_raw.replace("%20", " ").replace("+", " ")
            
            page.views.append(
                ft.View(
                    route=page.route,
                    controls=[logs_view(page, nombre_app)],
                    appbar=ft.AppBar(
                        leading=ft.IconButton(
                            icon=ft.icons.ARROW_BACK_IOS_NEW_ROUNDED, 
                            icon_color=palettet.primary,
                            on_click=lambda _: page.go("/dashboard")
                        ),
                        title=ft.Text(f"Análisis: {nombre_app}", color=palettet.primary, weight="bold"),
                        bgcolor=palettet.secundary,
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
    
 
    page.go("/")

if __name__ == "__main__":
    ft.app( 
        target=main, 
        assets_dir="assets", 
        view=ft.AppView.FLET_APP 
    )