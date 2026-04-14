import flet as ft
import asyncio
import os
from sqlalchemy import func
from datetime import datetime, timedelta
from fpdf import FPDF 
from database.config import SessionLocal
from database.modelo import Logs, MetricasHistoricas
from services.lector_api import SERVICIOS_EMPRESA, obtener_metricas_reales
from utilidades.colors import palettet

# --- CONFIGURACIÓN DE UMBRALES (Se mantiene intacto) ---
CONFIG_SERVICIOS = {
    s["nombre"]: {"cpu": 80, "ram": 80, "red": 80, "dl": 80, "de": 80} 
    for s in SERVICIOS_EMPRESA
}

# Control de estado para no repetir notificaciones (Se mantiene intacto)
estado_alerta_actual = {s["nombre"]: None for s in SERVICIOS_EMPRESA}

def dashboard_view(page: ft.Page):
    user_rol = str(page.session.get("user_rol") or "admin").lower()
    user_name = page.session.get("user_name") or "Usuario BEL"
    
    es_admin = "admin" in user_rol
    es_gerente = any(x in user_rol for x in ["gerente", "gerencia"]) 
    servicios_controles = {}
    
    # Bandera para controlar el loop
    loop_activo = True

    # --- FUNCIÓN DE LOGOUT ---
    def cerrar_sesion(e):
        nonlocal loop_activo
        loop_activo = False   # Detener el loop inmediatamente
        page.session.clear()  # Borrar datos de la sesión
        page.go("/")

    # --- FUNCIÓN PARA VALIDAR UMBRALES ---
    def validar_umbral(value, campo_nombre):
        try:
            valor = int(value)
            if valor < 50:
                return 50, f"⚠️ {campo_nombre} no puede ser menor a 50%"
            elif valor > 100:
                return 100, f"⚠️ {campo_nombre} no puede ser mayor a 100%"
            return valor, None
        except ValueError:
            return 80, f"⚠️ {campo_nombre} debe ser un número válido"

    # --- 1. REPORTE PDF (Se mantiene intacto) ---
    def abrir_reporte_gerencial(e):
        db = SessionLocal()
        dias = int(selector_tiempo.value)
        limite = datetime.now() - timedelta(days=dias if dias > 1 else 0, hours=1 if dias == 1 else 0)
        try:
            caidas = db.query(Logs.servicio, func.count(Logs.id)).filter(Logs.nivel == "CRITICAL", Logs.fecha >= limite).group_by(Logs.servicio).all()
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(190, 10, "REPORTE GERENCIAL DE DISPONIBILIDAD", ln=True, align='C')
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(140, 10, " SERVICIO", border=1)
            pdf.cell(50, 10, " CAIDAS", border=1, ln=True)
            pdf.set_font("Arial", '', 12)
            for s, c in caidas:
                pdf.cell(140, 8, f" {s}", border=1)
                pdf.cell(50, 8, f" {c}", border=1, ln=True)
            path = "Reporte_BEL.pdf"
            pdf.output(path)
            if os.name == 'nt':
                os.startfile(path)
        finally:
            db.close()

    # --- 2. SELECTORES (Se mantiene intacto) ---
    selector_tiempo = ft.Dropdown(
        label="Periodo de caídas",
        value="30",
        width=180,
        text_size=12,
        dense=True,
        border_color=palettet.secundary,
        focused_border_color=palettet.accent,
        options=[
            ft.dropdown.Option("1", "Última Hora"),
            ft.dropdown.Option("24", "Últimas 24 Horas"),
            ft.dropdown.Option("7", "Últimos 7 Días"),
            ft.dropdown.Option("30", "Últimos 30 Días"),
        ],
        on_change=lambda _: page.update(),
        tooltip="Rango de tiempo para el reporte de caídas"
    )

    def get_selector_style():
        m_sel = list(selector_metrica.selected)[0] if selector_metrica.selected else "cpu"
        color_fondo = {"cpu": palettet.track_1, "ram": palettet.track_2, "red": palettet.track_3, "dl": palettet.track_4, "de": palettet.track_4}.get(m_sel, palettet.accent)
        return ft.ButtonStyle(
            color={"selected": ft.colors.WHITE, "": palettet.secundary},
            bgcolor={"selected": color_fondo, "": "transparent"},
            side={"selected": ft.BorderSide(0), "": ft.BorderSide(1, "#E2E8F0")},
            shape={"selected": ft.RoundedRectangleBorder(radius=8), "": ft.RoundedRectangleBorder(radius=8)},
            padding={"selected": 10, "": 10}
        )

    selector_metrica = ft.SegmentedButton(
        selected={"cpu"},
        allow_multiple_selection=False,
        show_selected_icon=False,
        segments=[
            ft.Segment(value="cpu", label=ft.Text("CPU", size=9, weight="bold")),
            ft.Segment(value="ram", label=ft.Text("RAM", size=9, weight="bold")),
            ft.Segment(value="red", label=ft.Text("RED", size=9, weight="bold")),
            ft.Segment(value="dl", label=ft.Text("D-L", size=9, weight="bold")),
            ft.Segment(value="de", label=ft.Text("D-E", size=9, weight="bold")),
        ],
        visible=es_admin,
        on_change=lambda e: (setattr(selector_metrica, "style", get_selector_style()), page.update()),
        tooltip="Selecciona la métrica a visualizar en el gráfico"
    )
    if es_admin:
        selector_metrica.style = get_selector_style()

    # --- 3. AJUSTES DE UMBRAL (MEJORADO - con validaciones) ---
    def abrir_ajustes_umbral(nombre_servicio):
        conf = CONFIG_SERVICIOS[nombre_servicio]
        
        # Campos con sus respectivos colores
        campos_color = {
            "cpu": {"color": palettet.track_1, "icono": ft.icons.MEMORY},
            "ram": {"color": palettet.track_2, "icono": ft.icons.STORAGE},
            "red": {"color": palettet.track_3, "icono": ft.icons.NETWORK_WIFI},
            "dl": {"color": palettet.track_4, "icono": ft.icons.DOWNLOAD},
            "de": {"color": palettet.track_4, "icono": ft.icons.UPLOAD},
        }
        
        # Mensajes de error
        errores = {k: ft.Text("", size=10, color=ft.colors.RED_600) for k in conf.keys()}
        
        fields = {}
        for k, v in conf.items():
            color_info = campos_color.get(k, {"color": palettet.accent})
            fields[k] = ft.TextField(
                label=k.upper(),
                value=str(v),
                width=100,
                dense=True,
                text_align="center",
                border_radius=8,
                border_color=color_info["color"],
                focused_border_color=color_info["color"],
                prefix_icon=color_info["icono"],
                suffix_text="%",
                text_style=ft.TextStyle(weight="bold", color=color_info["color"]),
                on_change=lambda e, campo=k: validar_campo_en_tiempo_real(e, campo)
            )
        
        def validar_campo_en_tiempo_real(e, campo):
            """Validación en tiempo real mientras el usuario escribe"""
            try:
                valor = int(e.control.value)
                if valor < 50:
                    errores[campo].value = f"⚠️ Mínimo 50%"
                    errores[campo].visible = True
                elif valor > 100:
                    errores[campo].value = f"⚠️ Máximo 100%"
                    errores[campo].visible = True
                else:
                    errores[campo].value = ""
                    errores[campo].visible = False
            except ValueError:
                errores[campo].value = f"⚠️ Número válido"
                errores[campo].visible = True
            page.update()
        
        def guardar(e):
            hay_error = False
            # Validar todos los campos antes de guardar
            for k, field in fields.items():
                valor, error = validar_umbral(field.value, k.upper())
                if error:
                    errores[k].value = error
                    errores[k].visible = True
                    hay_error = True
                else:
                    conf[k] = valor
                    field.value = str(valor)
                    errores[k].visible = False
            
            if hay_error:
                page.snack_bar = ft.SnackBar(
                    ft.Text("❌ Corrige los errores antes de guardar", size=12),
                    bgcolor=ft.colors.RED_600,
                    duration=3000
                )
                page.snack_bar.open = True
                page.update()
            else:
                diag.open = False
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"✅ Umbrales actualizados para {nombre_servicio}", size=12),
                    bgcolor=ft.colors.GREEN_600,
                    duration=2000
                )
                page.snack_bar.open = True
                page.update()
        
        # Crear filas organizadas por colores
        diag = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.TUNE_ROUNDED, color=palettet.accent, size=24),
                ft.Text(f"UMBRALES: {nombre_servicio}", size=16, weight="bold", color=palettet.text_sub)
            ], spacing=10),
            content=ft.Container(
                width=450,
                content=ft.Column([
                    ft.Text("⚙️ CONFIGURACIÓN DE LÍMITES", size=11, weight="bold", color=palettet.text_sub),
                    ft.Text("📏 Rango permitido: 50% - 100%", size=10, color=ft.colors.GREY_600),
                    ft.Divider(height=1, color="#E8EDF2"),
                    ft.Column([
                        ft.Row([
                            ft.Column([fields["cpu"], errores["cpu"]], spacing=2, horizontal_alignment="center"),
                            ft.Column([fields["ram"], errores["ram"]], spacing=2, horizontal_alignment="center"),
                        ], alignment="center", spacing=20),
                        ft.Row([
                            ft.Column([fields["red"], errores["red"]], spacing=2, horizontal_alignment="center"),
                        ], alignment="center"),
                        ft.Row([
                            ft.Column([fields["dl"], errores["dl"]], spacing=2, horizontal_alignment="center"),
                            ft.Column([fields["de"], errores["de"]], spacing=2, horizontal_alignment="center"),
                        ], alignment="center", spacing=20),
                    ], spacing=15, horizontal_alignment="center"),
                ], spacing=12, horizontal_alignment="center"),
                padding=20
            ),
            actions=[
                ft.TextButton("CANCELAR", on_click=lambda e: setattr(diag, "open", False) or page.update()),
                ft.ElevatedButton(
                    "💾 GUARDAR CAMBIOS",
                    bgcolor=palettet.accent,
                    color="white",
                    on_click=guardar,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                )
            ],
            shape=ft.RoundedRectangleBorder(radius=20),
            actions_alignment="end"
        )
        page.dialog = diag
        diag.open = True
        page.update()

    # --- 4. COMPONENTES DE LA CARD (Botones mejorados) ---
    def crear_gauge(valor, color, label):
        sa = ft.PieChartSection(valor, color=color, radius=8)
        sf = ft.PieChartSection(max(0, 100-valor), color=ft.colors.with_opacity(0.12, color), radius=8)
        txt = ft.Text(f"{int(valor)}", size=10, weight="bold", color=color)
        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=7, weight="bold", color=palettet.text_sub), 
                ft.Stack([
                    ft.PieChart(sections=[sa, sf], center_space_radius=12, height=50, width=50),
                    ft.Container(content=txt, alignment=ft.alignment.center, width=50, height=50)
                ])
            ], horizontal_alignment="center", spacing=4),
            ink=False
        ), sa, sf, txt

    def crear_card(s):
        cpu_c, cpu_sa, cpu_sf, cpu_t = crear_gauge(0, palettet.track_1, "CPU")
        ram_c, ram_sa, ram_sf, ram_t = crear_gauge(0, palettet.track_2, "RAM")
        red_c, red_sa, red_sf, red_t = crear_gauge(0, palettet.track_3, "RED")
        dl_c, dl_sa, dl_sf, dl_t = crear_gauge(0, palettet.track_4, "D-L")
        de_c, de_sa, de_sf, de_t = crear_gauge(0, palettet.track_4, "D-E")
        
        txt_caidas_num = ft.Text("0", size=18, weight="bold", color=palettet.danger)
        status_dot = ft.Container(width=10, height=10, border_radius=5, bgcolor=palettet.neutral)
        panel_extra = ft.Container(visible=False, content=ft.Row([red_c, dl_c, de_c], alignment="center", spacing=20))
        
        def toggle_panel(e):
            panel_extra.visible = not panel_extra.visible
            btn_det.icon = ft.icons.KEYBOARD_ARROW_UP_ROUNDED if panel_extra.visible else ft.icons.KEYBOARD_ARROW_DOWN_ROUNDED
            page.update()

        # Botones mejorados con estilo moderno
        btn_det = ft.IconButton(
            ft.icons.KEYBOARD_ARROW_DOWN_ROUNDED,
            on_click=toggle_panel,
            icon_size=20,
            icon_color=palettet.secundary,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                bgcolor=ft.colors.with_opacity(0.1, palettet.secundary)
            ),
            tooltip="Ver más métricas"
        )
        
        btn_web = ft.Container(
            content=ft.Icon(ft.icons.LANGUAGE_ROUNDED, size=18, color=ft.colors.BLUE_700),
            on_click=lambda _: page.launch_url(s["url"]),
            border_radius=10,
            padding=8,
            bgcolor=ft.colors.BLUE_50,
            tooltip="Abrir servicio web",
            ink=True
        )
        
        btn_log = ft.Container(
            content=ft.Icon(ft.icons.INSERT_CHART_ROUNDED, size=18, color=ft.colors.INDIGO_700),
            on_click=lambda _: page.go(f"/logs/{s['nombre']}"),
            border_radius=10,
            padding=8,
            bgcolor=ft.colors.INDIGO_50,
            visible=es_admin,
            tooltip="Ver logs históricos",
            ink=True
        )
        
        btn_cfg = ft.Container(
            content=ft.Icon(ft.icons.TUNE_ROUNDED, size=18, color=ft.colors.ORANGE_700),
            on_click=lambda _: abrir_ajustes_umbral(s["nombre"]),
            border_radius=10,
            padding=8,
            bgcolor=ft.colors.ORANGE_50,
            visible=es_admin,
            tooltip="Ajustar umbrales de alerta",
            ink=True
        )

        caidas_container = ft.Container(
            content=ft.Column([
                txt_caidas_num,
                ft.Text("CAÍDAS", size=8, weight="bold", color=palettet.text_sub),
            ], horizontal_alignment="center", spacing=2),
            padding=ft.padding.only(top=5, bottom=5, left=10, right=10),
            bgcolor=ft.colors.with_opacity(0.08, palettet.danger),
            border_radius=12,
            alignment=ft.alignment.center
        )

        card_container = ft.Container(
            padding=15,
            bgcolor=palettet.primary,
            border_radius=20,
            border=ft.border.all(1, "#E8EDF2"),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.colors.with_opacity(0.08, ft.colors.BLACK),
                offset=ft.Offset(0, 2)
            ),
            col={"sm": 12, "md": 6, "lg": 4},
            animate=ft.animation.Animation(200, "easeOut"),
            on_hover=lambda e: setattr(
                e.control, "shadow",
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=16,
                    color=ft.colors.with_opacity(0.12, ft.colors.BLACK),
                    offset=ft.Offset(0, 4)
                )
            ) if e.data == "true" else setattr(
                e.control, "shadow",
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=8,
                    color=ft.colors.with_opacity(0.08, ft.colors.BLACK),
                    offset=ft.Offset(0, 2)
                )
            ),
            content=ft.Column([
                ft.Row([
                    ft.Text(s["nombre"].upper(), weight="bold", size=11, color=ft.colors.BLACK87),
                    status_dot
                ]),
                ft.Divider(height=1, color="#E8EDF2"),
                ft.Row([
                    ft.Container(
                        content=cpu_c,
                        on_click=lambda _, m="cpu": setattr(selector_metrica, "selected", {m}) if es_admin else None,
                        tooltip="Ver CPU en gráfico" if es_admin else None
                    ),
                    ft.Container(
                        content=ram_c,
                        on_click=lambda _, m="ram": setattr(selector_metrica, "selected", {m}) if es_admin else None,
                        tooltip="Ver RAM en gráfico" if es_admin else None
                    ),
                ], alignment="center", spacing=40),
                panel_extra,
                ft.Divider(height=1, color="#E8EDF2"),
                ft.Row([
                    caidas_container,
                    ft.Row([btn_det, btn_web, btn_log, btn_cfg], spacing=8)
                ], alignment="spaceBetween")
            ], spacing=8)
        )

        servicios_controles[s["nombre"]] = {
            "metrics": {"cpu": (cpu_sa, cpu_sf, cpu_t), "ram": (ram_sa, ram_sf, ram_t), "red": (red_sa, red_sf, red_t), "dl": (dl_sa, dl_sf, dl_t), "de": (de_sa, de_sf, de_t)},
            "dot": status_dot,
            "caidas_label": txt_caidas_num,
            "main_container": card_container
        }
        return card_container

    # --- 5. GRÁFICA MACRO ---
    chart_macro = ft.BarChart(
        expand=True,
        max_y=100,
        interactive=True,
        left_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(value=0, label=ft.Text("0", size=10, weight="bold", color=palettet.text_sub)),
                ft.ChartAxisLabel(value=50, label=ft.Text("50", size=10, weight="bold", color=palettet.text_sub)),
                ft.ChartAxisLabel(value=100, label=ft.Text("100", size=10, weight="bold", color=palettet.text_sub)),
            ],
            labels_size=35
        ),
        horizontal_grid_lines=ft.ChartGridLines(
            interval=50,
            color=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE),
            width=1
        ),
        vertical_grid_lines=ft.ChartGridLines(
            interval=1,
            color=ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE),
            width=1
        ),
        visible=es_admin
    )

    # --- 6. LOOP DE DATOS Y ALERTAS (Corregido para Flet) ---
    async def loop():
        nonlocal loop_activo
        await asyncio.sleep(1)
        while loop_activo:
            try:
                # Verificar si la página aún está activa
                if not page or not page.session:
                    break
                
                db = SessionLocal()
                try:
                    m_sel = list(selector_metrica.selected)[0] if es_admin and selector_metrica.selected else "cpu"
                    c_bar = {"cpu": palettet.track_1, "ram": palettet.track_2, "red": palettet.track_3, "dl": palettet.track_4, "de": palettet.track_4}.get(m_sel, palettet.accent)
                    limite = datetime.now() - timedelta(days=int(selector_tiempo.value))
                    
                    new_groups, labels = [], []
                    for i, s in enumerate(SERVICIOS_EMPRESA):
                        data = obtener_metricas_reales(s["nombre"])
                        count_caidas = db.query(func.count(Logs.id)).filter(
                            Logs.servicio == s["nombre"],
                            Logs.nivel == "CRITICAL",
                            Logs.fecha >= limite
                        ).scalar()
                        
                        db.add(MetricasHistoricas(
                            servicio=s["nombre"],
                            cpu=data.get("cpu", 0),
                            ram=data.get("ram", 0),
                            red_bajada=data.get("red", 0),
                            disco_lectura=data.get("dl", 0),
                            disco_escritura=data.get("de", 0)
                        ))

                        if s["nombre"] in servicios_controles:
                            ctrl = servicios_controles[s["nombre"]]
                            for k, (sa, sf, txt) in ctrl["metrics"].items():
                                v = data.get(k, 0)
                                sa.value = v
                                sf.value = 100 - v
                                txt.value = f"{int(v)}"
                            ctrl["caidas_label"].value = str(count_caidas)

                            # --- TU LÓGICA DE ALERTAS (Intacta) ---
                            nivel_critico = False
                            nivel_advertencia = False
                            for metrica, valor in data.items():
                                if metrica in CONFIG_SERVICIOS[s["nombre"]]:
                                    umbral = CONFIG_SERVICIOS[s["nombre"]][metrica]
                                    if valor >= umbral:
                                        nivel_critico = True
                                        break
                                    elif valor >= (umbral * 0.85):
                                        nivel_advertencia = True

                            if nivel_critico:
                                ctrl["main_container"].bgcolor = "#FFF1F1"
                                ctrl["main_container"].border = ft.border.all(2, ft.colors.RED_700)
                                ctrl["dot"].bgcolor = ft.colors.RED_700
                                if estado_alerta_actual[s["nombre"]] != "RED":
                                    db.add(Logs(servicio=s["nombre"], nivel="CRITICAL", detalles=data))
                                    if loop_activo:  # Solo mostrar snackbar si el loop está activo
                                        page.snack_bar = ft.SnackBar(
                                            ft.Text(f"⚠️ CRÍTICO: {s['nombre']} superó umbrales"),
                                            bgcolor=ft.colors.RED_700,
                                            duration=4000
                                        )
                                        page.snack_bar.open = True
                                    estado_alerta_actual[s["nombre"]] = "RED"
                            elif nivel_advertencia:
                                ctrl["main_container"].bgcolor = "#FFFBEB"
                                ctrl["main_container"].border = ft.border.all(2, ft.colors.AMBER_600)
                                ctrl["dot"].bgcolor = ft.colors.AMBER_600
                                if estado_alerta_actual[s["nombre"]] != "YELLOW":
                                    db.add(Logs(servicio=s["nombre"], nivel="WARNING", detalles=data))
                                    if loop_activo:
                                        page.snack_bar = ft.SnackBar(
                                            ft.Text(f"⚠️ AVISO: {s['nombre']} cerca de umbrales"),
                                            bgcolor=ft.colors.AMBER_600,
                                            duration=4000
                                        )
                                        page.snack_bar.open = True
                                    estado_alerta_actual[s["nombre"]] = "YELLOW"
                            else:
                                ctrl["main_container"].bgcolor = palettet.primary
                                ctrl["main_container"].border = ft.border.all(1, "#E8EDF2")
                                ctrl["dot"].bgcolor = ft.colors.GREEN_400
                                estado_alerta_actual[s["nombre"]] = "NORMAL"

                        if es_admin:
                            new_groups.append(ft.BarChartGroup(
                                x=i,
                                bar_rods=[ft.BarChartRod(
                                    from_y=0,
                                    to_y=min(100, data.get(m_sel, 0)),
                                    width=24,
                                    color=c_bar,
                                    border_radius=4
                                )]
                            ))
                            labels.append(ft.ChartAxisLabel(
                                value=i,
                                label=ft.Text(s["nombre"][:6].upper(), size=8, weight="bold", color=palettet.text_sub)
                            ))

                    db.commit()
                    if es_admin and chart_macro and loop_activo:
                        chart_macro.bar_groups = new_groups
                        chart_macro.bottom_axis = ft.ChartAxis(labels=labels)
                        chart_macro.update()
                except Exception as e:
                    db.rollback()
                    print(f"Error en loop: {e}")
                finally:
                    db.close()

                if loop_activo:
                    page.update()
                    await asyncio.sleep(10)
            except Exception as e:
                print(f"Error en iteración del loop: {e}")
                if loop_activo:
                    await asyncio.sleep(10)

    # --- 7. LAYOUT FINAL (Con degradado VERDE y botón de salir) ---
    layout = ft.Column([
        # Header con degradado VERDE y botón de salir
        ft.Container(
            gradient=ft.LinearGradient(
                colors=["#2E7D32", "#1B5E20"],  # Degradado verde
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right
            ),
            padding=ft.padding.only(top=30, bottom=30, left=25, right=25),
            border_radius=ft.border_radius.only(bottom_left=30, bottom_right=30),
            content=ft.Row([
                ft.Column([
                    ft.Text("BEL MONITORING", color="white", size=20, weight="bold"),
                    ft.Text(f"Bienvenido, {user_name}", color=ft.colors.with_opacity(0.9, "white"), size=12),
                ], spacing=2),
                ft.Row([
                    ft.IconButton(
                        ft.icons.PICTURE_AS_PDF_ROUNDED,
                        icon_color="white",
                        bgcolor=ft.colors.with_opacity(0.2, "white"),
                        on_click=abrir_reporte_gerencial,
                        visible=es_gerente,
                        icon_size=20,
                        tooltip="Generar reporte PDF"
                    ),
                    ft.Container(width=5),
                    ft.Container(
                        content=ft.Icon(ft.icons.LOGOUT_ROUNDED, size=20, color="white"),
                        on_click=cerrar_sesion,
                        border_radius=10,
                        padding=8,
                        bgcolor=ft.colors.with_opacity(0.2, "white"),
                        tooltip="Cerrar sesión",
                        ink=True
                    ),
                ], spacing=5)
            ], alignment="spaceBetween")
        ),
        
        # Contenedor de métricas globales
        ft.Container(
            padding=ft.padding.only(left=25, right=25, top=20, bottom=10),
            content=ft.Column([
                ft.ResponsiveRow([
                    ft.Column([
                        ft.Text("MÉTRICAS GLOBALES", weight="bold", size=11, color=palettet.text_sub, visible=es_admin),
                        selector_metrica
                    ], col={"sm": 12, "md": 8}, spacing=5),
                    ft.Column([
                        selector_tiempo
                    ], col={"sm": 12, "md": 4}, horizontal_alignment="end"),
                ]),
                ft.Container(
                    chart_macro,
                    height=200,
                    padding=ft.padding.all(15),
                    bgcolor="#FFFFFF",
                    border_radius=16,
                    border=ft.border.all(1, "#E8EDF2"),
                    shadow=ft.BoxShadow(
                        blur_radius=4,
                        color=ft.colors.with_opacity(0.05, ft.colors.BLACK),
                        offset=ft.Offset(0, 1)
                    ),
                    margin=ft.margin.only(bottom=10),
                    visible=es_admin
                )
            ])
        ),
        
        # Grid de cards responsive
        ft.Container(
            padding=ft.padding.only(left=20, right=20, bottom=20, top=0),
            content=ft.ResponsiveRow(
                [crear_card(s) for s in SERVICIOS_EMPRESA],
                spacing=20,
                run_spacing=20
            )
        )
    ],
    scroll=ft.ScrollMode.ADAPTIVE,
    expand=True,
    spacing=0)

    # Usar page.run_task para iniciar el loop (método correcto en Flet)
    page.run_task(loop)
    return layout