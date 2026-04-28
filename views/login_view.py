import flet as ft
import asyncio
from controladores.crud import validar_usuario
from utilidades.colors import palettet

def login_view(page: ft.Page):
    
    # Validacion de sesion 
    # Si el usuario ya tiene sesión activa y por algún motivo llega aquí, 
    # lo manda directo al dashboard.
    if page.session.get("user_name"):
        page.go("/dashboard")

    async def on_login_click(e):
        user_val = user_input.value.strip()
        pass_val = pass_input.value.strip()

        #  Validación de campos vacíos
        if not user_val or not pass_val:
            mostrar_error("Por favor, llene todos los campos")
            return

        # Bloqueo visual de seguridad
        btn_login.disabled = True
        btn_text.value = "VERIFICANDO..."
        user_input.disabled = True
        pass_input.disabled = True
        page.update()
        
        await asyncio.sleep(0.5)
        
        try:
            # Validación contra Base de Datos
            usuario = validar_usuario(user_val, pass_val)

            if usuario:
                #  Persistencia de Sesión
                # Guardamos los datos para que el main.py y dashboard los reconozcan
                page.session.set("user_name", usuario["username"])
                #Se asefura que el rol sea siempre un string limpio
                rol_asignado = str(usuario.get("rol", "admin")).lower()
                page.session.set("user_rol", rol_asignado) 
                
                # Feedback visual de éxito
                btn_login.bgcolor = palettet.success
                btn_text.value = "ACCESO EXITOSO"
                page.update()
                
                await asyncio.sleep(0.8) 
                page.go("/dashboard")
            else:
                # 4. Error de credenciales
                mostrar_error("Usuario o contraseña incorrectos")
        
        except Exception as ex:
            # Validación ante caídas de DB o errores 
            print(f"Error en Login: {ex}")
            mostrar_error("Error de conexión con el servidor")

    def mostrar_error(mensaje):
        # Reactivamos la interfaz
        btn_login.disabled = False
        user_input.disabled = False
        pass_input.disabled = False
        btn_text.value = "INICIAR SESIÓN"
        
        # SnackBar mejorado para feedback
        page.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje, weight="bold", color=palettet.primary), 
            bgcolor=palettet.danger,
            action="OK"
        )
        page.snack_bar.open = True  
        page.update()

    # TEXTFIELDS
    user_input = ft.TextField(
        hint_text="Nombre de usuario",
        width=320, height=50,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.BLACK),
        border_radius=25,
        border_color=ft.colors.TRANSPARENT,
        prefix_icon=ft.icons.PERSON_OUTLINE_ROUNDED,
        cursor_color=palettet.secundary,
        hint_style=ft.TextStyle(color=palettet.text_sub),
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
        hint_style=ft.TextStyle(color=palettet.text_sub),
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

    #ESTRUCTURA RESPONSISE
    return ft.ResponsiveRow(
        expand=True,
        spacing=0,
        controls=[
            # PANEL IZQUIERDO: FORMULARIO
            ft.Container(
                col={"sm": 12, "md": 6},
                bgcolor=palettet.primary,
                padding=40,
                content=ft.Column(
                    [
                        ft.Image(src="logo_bel.png", width=90),
                        ft.Text("Acceso de usuario", size=26, weight="bold", color=palettet.secundary),
                        ft.Text("Sistema de monitoreo JAC & BEL", size=12, color=palettet.text_sub),
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
            # PANEL DERECHO: DISEÑO
            ft.Container(
                col={"xs": 0, "md": 6},
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[palettet.accent, palettet.secundary],
                ),
                content=ft.Stack([
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
                                    color=palettet.primary, size=13, opacity=0.8,
                                    text_align="center"
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