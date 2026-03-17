import flet as ft
from utilidades.colors import palettet

def login_view(page):
    def on_login_click(e):

        if user_input.value == "admin" and pass_input.value == "1234":
            page.go("/dashboard")
        else:
            page.snack_bar = ft.SnackBar(
                ft.Text("Credenciales incorrectas", color="white"), 
                bgcolor=ft.colors.RED_ACCENT
            )
            page.snack_bar.open = True
            page.update()

    

    user_input = ft.TextField(
        label="Usuario", 
        width=300, 
        border_color=palettet.secundary,
        prefix_icon=ft.icons.PERSON_OUTLINED,
        on_submit=on_login_click 
    )
    
    pass_input = ft.TextField(
        label="Contraseña", 
        password=True, 
        can_reveal_password=True, 
        width=300, 
        border_color=palettet.secundary,
        prefix_icon=ft.icons.LOCK_OUTLINED,
        on_submit=on_login_click 
    )

    return ft.Container(
        content=ft.Column(
            [
                ft.Image(
                    src="logo_bel.png",
                    width=180,
                    height=180,
                    fit=ft.ImageFit.CONTAIN,
                ),
                
                ft.Text(
                    "SISTEMA DE MONITOREO", 
                    size=22, 
                    weight="bold", 
                    color="#333333"
                ),
                
                ft.Text(
                    "Ingrese sus credenciales para continuar", 
                    size=14, 
                    color="grey"
                ),
                
                ft.Container(height=20),
                
                user_input,
                pass_input,
                
                ft.Container(height=10),
                
                ft.ElevatedButton(
                    text="INICIAR SESIÓN",
                    width=300,
                    height=50,
                    bgcolor=palettet.accent,
                    color=palettet.primary,
                    on_click=on_login_click, 
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    )
                ),
                
                ft.Container(height=20),
                
                ft.Text("© 2026 Corporación Bel", size=10, color="grey"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=40,
        expand=True,
    )