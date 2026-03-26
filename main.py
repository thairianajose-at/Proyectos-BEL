import flet as ft
import asyncio
import sys
import warnings
import socket
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
    crear_tablas()  
    db = SessionLocal()
    try:
        if not db.query(Usuario).first():
            crear_usuario("admin", "admin123", rol="admin")
            crear_usuario("wilder1", "wilder1234", rol="devops")
    finally:
        db.close()

def main(page: ft.Page):
    inicializar_sistema()
 
    page.title = "Monitor JAC & BEL"
    page.theme_mode = ft.ThemeMode.LIGHT 
    page.fonts = appFonts.FONTS_DICT
    page.theme = ft.Theme(font_family=appFonts.ARIMO)
    
    page.window_width = 1250
    page.window_height = 850

    def route_change(e):
        page.views.clear()
        
        # --- LOGIN ---
        if page.route == "/":
            page.views.append(ft.View("/", [login_view(page)], padding=0))
     
        # --- DASHBOARD ---
        elif page.route == "/dashboard":
            if not page.session.get("user_name"):
                page.go("/")
                return

            page.views.append(
                ft.View(
                    "/dashboard", 
                    [dashboard_view(page)],
                    padding=0,
                    appbar=ft.AppBar(
                        toolbar_height=70,
                        bgcolor=palettet.secundary,
                        elevation=0,
                        
                        leading_width=70,
                        leading=None, 
                        title=ft.Row([
                            ft.Container(
                                padding=ft.padding.only(left=10),
                                content=ft.Image(src="logo_bel.png", fit="contain", height=40)
                            ),
                            
                        ], alignment="start"),
                        center_title=False,
                        actions=[
                            
                            ft.Container(
                                bgcolor=ft.colors.with_opacity(0.15, ft.colors.WHITE),
                                padding=ft.padding.symmetric(horizontal=15, vertical=8),
                                border_radius=20,
                                border=ft.border.all(1, ft.colors.with_opacity(0.2, "white")),
                                content=ft.Row([
                                    ft.Icon(ft.icons.PERSON_PIN_ROUNDED, color=palettet.primary, size=18),
                                    ft.Text(f"{page.session.get('user_name')}".upper(), color=palettet.primary, weight="w500", size=12),
                                ], spacing=8)
                            ),
                            ft.IconButton(
                                icon=ft.icons.LOGOUT_ROUNDED, 
                                icon_color=ft.colors.RED_ACCENT_200,
                                tooltip="Cerrar Sesión",
                                on_click=lambda _: [page.session.clear(), page.go("/")]
                            ),
                            ft.Container(width=15)
                        ]
                    )
                )
            )
        
        # --- LOGS ---
        elif page.route.startswith("/logs/"):
            nombre_raw = page.route.split("/")[-1]
            nombre_app = nombre_raw.replace("%20", " ").replace("+", " ")
            
            page.views.append(
                ft.View(
                    page.route, 
                    [logs_view(page, nombre_app)],
                    padding=0,
                    appbar=ft.AppBar(
                        toolbar_height=70,
                        bgcolor=palettet.secundary,
                        elevation=0,
                        leading=ft.IconButton(ft.icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_color="white", on_click=lambda _: page.go("/dashboard")),
                        title=ft.Text(f"LOGS: {nombre_app}".upper(), color="white", weight="bold", size=18),
                        center_title=True,
                    )
                )
            )
        page.update()

    page.on_route_change = route_change
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")