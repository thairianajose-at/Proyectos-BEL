import flet as ft
import asyncio
from controladores.crud import validar_usuario
from utilidades.colors import palettet

def login_view(page: ft.Page):

    async def on_login_click(e):
        user_val = user_input.value.strip()
        pass_val = pass_input.value.strip()

        if not user_val or not pass_val:
            mostrar_error("Por favor, llene todos los campos")
            return

        btn_login.disabled = True
        btn_text.value = "VERIFICANDO..."
        page.update()
        
        await asyncio.sleep(0.5)
        usuario = validar_usuario(user_val, pass_val)

        if usuario:
            # GUARDAR ROL Y NOMBRE 
            page.session.set("user_name", usuario["username"])
            page.session.set("user_rol", usuario.get("rol", "admin")) # se guarda el rol (default admin si no existe)
            
            btn_login.bgcolor = ft.colors.GREEN_700
            btn_text.value = "ACCESO EXITOSO"
            page.update()
            await asyncio.sleep(0.8) 
            page.go("/dashboard")
        else:
            mostrar_error("Usuario o contraseña incorrectos")

    def mostrar_error(mensaje):
        btn_login.disabled = False
        btn_text.value = "INICIAR SESIÓN"
        page.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje, weight="bold", color=palettet.primary), 
            bgcolor=ft.colors.RED_700
        )
        page.snack_bar.open = True  
        page.update()

    user_input = ft.TextField(
        hint_text="Nombre de usuario",
        width=320, height=50,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.BLACK),
        border_radius=25,
        border_color=ft.colors.TRANSPARENT,
        prefix_icon=ft.icons.PERSON_OUTLINE_ROUNDED,
        cursor_color=palettet.secundary,
        hint_style=ft.TextStyle(color=ft.colors.GREY_500),
        text_style=ft.TextStyle(color=palettet.secundary),
        focused_border_color=palettet.accent,
        on_submit=on_login_click
    )
    
    pass_input = ft.TextField(
        hint_text="Contraseña",
        password=True, can_reveal_password=True,
        width=320, height=50,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.BLACK),
        border_radius=25,
        border_color=ft.colors.TRANSPARENT,
        prefix_icon=ft.icons.LOCK_OUTLINE_ROUNDED,
        cursor_color=palettet.secundary,
        hint_style=ft.TextStyle(color=ft.colors.GREY_500),
        text_style=ft.TextStyle(color=palettet.secundary),
        focused_border_color=palettet.accent,
        on_submit=on_login_click
    )

    btn_text = ft.Text("INICIAR SESIÓN", weight="bold", color=palettet.primary)
    
    btn_login = ft.ElevatedButton(
        content=btn_text,
        width=320, height=50,
        on_click=on_login_click,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=25),
            bgcolor={"": palettet.accent, ft.MaterialState.HOVERED: palettet.secundary},
            elevation={"": 2, ft.MaterialState.HOVERED: 8},
        )
    )

    return ft.Row(
        expand=True,
        spacing=0,
        controls=[
            # PANEL IZQUIERDO: FORMULARIO
            ft.Container(
                expand=True,
                bgcolor=palettet.primary,
                content=ft.Column(
                    [
                        ft.Image(src="logo_bel.png", width=90),
                        ft.Text("Acceso de usuario", size=26, weight="bold", color=palettet.secundary),
                        ft.Text("Sistema de monitoreo JAC & BEL", size=12, color=ft.colors.GREY_600),
                        ft.Container(height=30),
                        user_input,
                        ft.Container(height=10),
                        pass_input,
                        ft.Container(height=25),
                        btn_login,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ),
            # PANEL DERECHO: VISUAL CON TONALIDAD Y BURBUJAS
            ft.Container(
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[palettet.accent, palettet.secundary],
                ),
                content=ft.Stack([
                    # Burbujas decorativas
                    ft.Container(
                        width=200, height=200,
                        bgcolor=ft.colors.with_opacity(0.1, palettet.primary),
                        border_radius=100, top=-60, right=-60,
                    ),
                    ft.Container(
                        width=120, height=120,
                        bgcolor=ft.colors.with_opacity(0.05, palettet.primary),
                        border_radius=60, bottom=-30, left=-30,
                    ),
                    # Contenido Central Resaltado
                    ft.Container(
                        alignment=ft.alignment.center,
                        content=ft.Column(
                            [
                                ft.Container(
                                    content=ft.Icon(
                                        ft.icons.ANALYTICS_ROUNDED, 
                                        size=110, color=palettet.primary
                                    ),
                                    padding=20,
                                    border_radius=35,
                                    bgcolor=ft.colors.with_opacity(0.15, palettet.primary),
                                    border=ft.border.all(1, ft.colors.with_opacity(0.2, palettet.primary)),
                                ),
                                ft.Container(height=20),
                                ft.Text("JAC & BEL", color=palettet.primary, size=32, weight="bold"),
                                ft.Container(
                                    padding=8,
                                    border=ft.border.all(1, ft.colors.with_opacity(0.3, palettet.primary)),
                                    border_radius=8,
                                    content=ft.Text("MONITOR DEVOPS v2.0", color=palettet.primary, size=10, weight="bold"),
                                ),
                                ft.Container(height=15),
                                ft.Text(
                                    "Gestión de infraestructura y métricas", 
                                    color=palettet.primary, size=13, opacity=0.8
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    )
                ])
            )
        ]
    )