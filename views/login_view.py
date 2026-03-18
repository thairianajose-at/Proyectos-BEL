import flet as ft
from utilidades.colors import palettet
from utilidades.fonts import appFonts 

def login_view(page: ft.Page):
    # 1. Configuración de fuentes y Tema Global (Elimina el azul de raíz)
    page.fonts = appFonts.FONTS_DICT
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=palettet.accent,  # Esto hace que el cursor y la etiqueta sean verdes
        )
    )

    def on_login_click(e):
        btn_login.disabled = True
        btn_login.update()
        
        if user_input.value == "admin" and pass_input.value == "1234":
            page.go("/dashboard")
        else:
            btn_login.disabled = False
            page.snack_bar = ft.SnackBar(
                ft.Text("Credenciales incorrectas", style=appFonts.BODY), 
                bgcolor=ft.colors.RED_ACCENT
            )
            page.snack_bar.open = True
            page.update()

    # --- CAMPO DE USUARIO ---
    user_input = ft.TextField(
        label="Usuario", 
        width=320,
        border_radius=15,
        text_style=appFonts.BODY,
        label_style=appFonts.LABEL,
        border_color=palettet.secundary,
        prefix_icon=ft.icons.PERSON_ROUNDED,
        
        # Propiedades de enfoque
        focused_border_color=palettet.accent, # Borde verde al hacer clic
        cursor_color=palettet.accent,         # Puntero verde
        selection_color=ft.colors.with_opacity(0.3, palettet.accent),
        
        on_submit=on_login_click 
    )
    
    # --- CAMPO DE CONTRASEÑA ---
    pass_input = ft.TextField(
        label="Contraseña", 
        password=True, 
        can_reveal_password=True, 
        width=320, 
        border_radius=15,
        text_style=appFonts.BODY,
        label_style=appFonts.LABEL,
        border_color=palettet.secundary,
        prefix_icon=ft.icons.LOCK_ROUNDED,
        
        # Propiedades de enfoque
        focused_border_color=palettet.accent, # Borde verde al hacer clic
        cursor_color=palettet.accent,         # Puntero verde
        selection_color=ft.colors.with_opacity(0.3, palettet.accent),
        
        on_submit=on_login_click 
    )

    # --- BOTÓN DE INICIO ---
    btn_login = ft.ElevatedButton(
        text="INICIAR SESIÓN",
        width=320,
        height=50,
        bgcolor=palettet.accent,
        color=palettet.primary,
        on_click=on_login_click, 
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
        )
    )
    
    btn_login.text_style = ft.TextStyle(
        weight="bold", 
        font_family="Arimo", 
        size=14
    )

    # --- ESTRUCTURA DE LA VISTA ---
    return ft.Container(
        content=ft.Column(
            [
                ft.Container(height=40), 
                
                ft.Image(
                    src="logo_bel.png",
                    width=150,
                    height=150,
                    fit=ft.ImageFit.CONTAIN,
                ),
                
                ft.Text(
                    "SISTEMA DE MONITOREO", 
                    style=appFonts.HEADER,
                    color="#333333",
                    text_align=ft.TextAlign.CENTER
                ),
                
                ft.Text(
                    "Ingrese sus credenciales para continuar", 
                    style=appFonts.BODY,
                    color="grey",
                ),
                
                ft.Container(height=30),
                
                ft.Column(
                    [
                        user_input,
                        pass_input,
                    ], 
                    spacing=15, 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                
                ft.Container(height=15),
                
                ft.Container(
                    content=btn_login,
                    on_hover=lambda e: setattr(e.control, "scale", 1.05 if e.data == "true" else 1.0) or e.control.update(),
                    animate=ft.animation.Animation(300, ft.AnimationCurve.DECELERATE),
                ),
                
                ft.Container(expand=True), 
                
                ft.Text("© 2026 Corporación Bel", style=appFonts.BODY, size=11, opacity=0.6),
                ft.Container(height=20)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=40,
        expand=True,
        alignment=ft.alignment.center 
    )