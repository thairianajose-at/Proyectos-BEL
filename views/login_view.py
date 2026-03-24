import flet as ft
import time
from controladores.crud import validar_usuario
from utilidades.colors import palettet
from utilidades.fonts import appFonts 

def login_view(page: ft.Page):
    page.fonts = appFonts.FONTS_DICT
    
    
    loading_ring = ft.ProgressRing(
        width=20, height=20, stroke_width=2, 
        color=palettet.primary, visible=False
    )

    def on_login_click(e):
        user_val = user_input.value.strip()
        pass_val = pass_input.value.strip()

        if not user_val or not pass_val:
            mostrar_error("Por favor, llene todos los campos")
            return

      
        login_btn_control = btn_login.content 
        login_btn_control.disabled = True
        
        login_btn_control.content = ft.Row(
            [loading_ring, ft.Text(" VERIFICANDO...", weight="bold", color=palettet.primary)], 
            alignment="center",
            spacing=10
        )
        loading_ring.visible = True
        page.update()
        
    
        usuario = validar_usuario(user_val, pass_val)

        if usuario:
            page.session.set("user_name", usuario["username"])
            page.session.set("user_role", usuario["rol"])
            
            login_btn_control.bgcolor = ft.colors.GREEN_600
            login_btn_control.content = ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE_ROUNDED, color="white")
            page.update()
            
            time.sleep(0.6) 
            page.go("/dashboard")
        else:
            #
            mostrar_error("Usuario o contraseña incorrectos")

    def mostrar_error(mensaje):
        login_btn_control = btn_login.content
        login_btn_control.disabled = False
        login_btn_control.content = ft.Text("INICIAR SESIÓN", weight="bold", color=palettet.primary)
        loading_ring.visible = False
        
        
        page.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje, color="white"),
            bgcolor=ft.colors.RED_ACCENT_400,
            duration=3000,
        )
        page.snack_bar.open = True  
        page.update()


    user_input = ft.TextField(
        label="Usuario", 
        width=320,
        border_radius=15,
        prefix_icon=ft.icons.PERSON_ROUNDED,
        focused_border_color=palettet.accent, 
        on_submit=on_login_click 
    )
    
    pass_input = ft.TextField(
        label="Contraseña", 
        password=True, 
        can_reveal_password=True, 
        width=320, 
        border_radius=15,
        prefix_icon=ft.icons.LOCK_ROUNDED,
        focused_border_color=palettet.accent, 
        on_submit=on_login_click 
    )
    btn_login = ft.Container(
        content=ft.ElevatedButton(
            content=ft.Text("INICIAR SESIÓN", weight="bold", color=palettet.primary),
            width=320,
            height=50,
            on_click=on_login_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                bgcolor={
                    "": palettet.accent,           
                    "hovered": palettet.secundary,  
                    "disabled": palettet.accent,    
                },
                color={"": palettet.primary},
                elevation={"hovered": 8, "": 2},
            )
        ),
        on_hover=lambda e: setattr(e.control, "scale", 1.02 if e.data == "true" else 1.0) or e.control.update(),
        animate_scale=ft.animation.Animation(300, ft.AnimationCurve.DECELERATE),
    )

    return ft.Container(
        content=ft.Column(
            [
                ft.Container(height=40), 
                ft.Image(src="logo_bel.png", width=140, height=140, fit=ft.ImageFit.CONTAIN),
                ft.Text("SISTEMA DE MONITOREO", style=appFonts.HEADER, size=24, color=ft.colors.BLUE_GREY_900),
                ft.Text("Infraestructura & Data Center", style=appFonts.BODY, color="grey", italic=True),
                ft.Container(height=30),
                user_input,
                pass_input,
                ft.Container(height=10),
                btn_login,
                ft.Container(expand=True), 
                ft.Text("© 2026 Corporación BEL - DevOps Unit", style=appFonts.BODY, size=11, opacity=0.5),
                ft.Container(height=10)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=40,
        expand=True,
        alignment=ft.alignment.center,
        bgcolor=ft.colors.GREY_50 if page.theme_mode == ft.ThemeMode.LIGHT else ft.colors.BLACK
    )