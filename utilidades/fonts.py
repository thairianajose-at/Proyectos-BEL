import flet as ft

class appFonts:

    ARIMO = "Arimo"
    
 
    FONTS_DICT = {
        ARIMO: "https://fonts.gstatic.com/s/arimo/v28/P5sfzZqS-bE46DU_Vn7_x76fPyvc9as.ttf"
    }

    HEADER = ft.TextStyle(
        size=28, 
        weight=ft.FontWeight.BOLD, 
        font_family=ARIMO
    )
    
    LABEL = ft.TextStyle(
        size=16, 
        weight=ft.FontWeight.W_500, 
        font_family=ARIMO
    )
    
    BODY = ft.TextStyle(
        size=14, 
        font_family=ARIMO
    )