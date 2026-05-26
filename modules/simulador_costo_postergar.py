import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
import calendar
import os

def render_simulador(get_asset_path, encontrar_aporte_necesario_original, calcular_escenario):
    
    # --- PARCHE LOCAL DE BÚSQUEDA BINARIA ---
    # La versión original asume que "low" es el aporte sin inflación. 
    # Con inflación alta, el aporte inicial requerido es mucho menor que ese "low",
    # lo que causa que el simulador se "atore" devolviendo siempre el valor de "low".
    def encontrar_aporte_necesario(meta_objetivo, edad_ini, plazo_y, tasa_anual, infl_activa, tasa_infl, isr=0.0):
        low = 1.0 # Empezamos desde un aporte inicial mínimo ($1)
        
        r_m = (tasa_anual / 100) / 12
        if r_m > 0:
            base = (meta_objetivo * r_m) / (((1 + r_m) ** (plazo_y * 12)) - 1)
        else:
            base = meta_objetivo / (plazo_y * 12)
            
        high = base * 10.0 # Techo alto para la búsqueda binaria
        
        for _ in range(40): # Mayor cantidad de iteraciones (40) por el rango más amplio
            mid = (low + high) / 2
            df_temp, _ = calcular_escenario(mid, edad_ini, tasa_anual, infl_activa, tasa_infl, isr_retencion=isr, plazo_anos=plazo_y)
            final_val = df_temp['Saldo de Fondo'].iloc[-1]
            
            if final_val < meta_objetivo:
                low = mid
            else:
                high = mid
                
        return (low + high) / 2
        
    def obtener_porcentaje_bono(monto_mensual):
        monto_anual = monto_mensual * 12
        if monto_anual < 24000:
            return 0.0
        elif monto_anual < 36000:
            return 0.55
        elif monto_anual < 60000:
            return 0.65
        elif monto_anual < 90000:
            return 0.75
        else:
            return 1.00
        
    # --- CONFIGURACIÓN DE TEMAS ---
    is_dark = st.session_state.get('theme', 'dark') == 'dark'

    if is_dark:
        TEXT_COLOR = "#FEFFFF"
        ACCENT_COLOR = "#6BA4A4" 
        GOLD_COLOR = "#DFBF72"
        CARD_BG = "#252932"
        BORDER_COLOR = "#6BA4A422"
    else:
        TEXT_COLOR = "#1E3A8A"
        ACCENT_COLOR = "#3B82F6"
        GOLD_COLOR = "#1E3A8A"
        CARD_BG = "#FFFFFF"
        BORDER_COLOR = "#E5E7EB"

    # --- PANTALLA NUEVO SIMULADOR ---
    logo_filename = "1-07.png" if is_dark else "1-01.png"
    logo_sidebar = get_asset_path(logo_filename)
    
    with st.sidebar:
        if os.path.exists(logo_sidebar):
            st.image(logo_sidebar, use_container_width=True)
        st.title("Configuración")
        
        with st.expander("👤 Datos del Cliente", expanded=True):
            nombre_def_p = st.session_state.get("nombre_cliente", "") or st.session_state.get("hub_nombre", "")
            nombre_input = st.text_input("Nombre", value=nombre_def_p, key="postergar_name_input").title()
            st.session_state.nombre_cliente = nombre_input
            st.session_state.hub_nombre = nombre_input
            
            today = date.today()
            st.markdown(f"<p style='margin-bottom: 5px; font-weight: 900; text-transform: uppercase; font-size: 0.88rem; letter-spacing: 0.8px; color: {ACCENT_COLOR if is_dark else '#555'};'>Fecha de Nacimiento</p>", unsafe_allow_html=True)
            cs_d, cs_m, cs_a = st.columns([1.5, 1.8, 1.2])

            if 'c_yn_costos' not in st.session_state: st.session_state.c_yn_costos = today.year - 25
            if 'c_mn_costos' not in st.session_state: st.session_state.c_mn_costos = "Enero"
            if 'c_dn_costos' not in st.session_state: st.session_state.c_dn_costos = 1
            
            with cs_a:
                y_s = st.number_input("Año ", 1940, today.year, value=int(st.session_state.c_yn_costos), key="postergar_birth_year", label_visibility="collapsed")
                st.session_state.c_yn_costos = y_s
            with cs_m:
                m_names = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                m_idx = m_names.index(st.session_state.c_mn_costos) if st.session_state.c_mn_costos in m_names else 0
                m_s_s = st.selectbox("Mes ", m_names, index=m_idx, key="postergar_birth_month", label_visibility="collapsed")
                st.session_state.c_mn_costos = m_s_s
                m_s = m_names.index(m_s_s) + 1
            with cs_d:
                num_days_s = calendar.monthrange(int(y_s), int(m_s))[1]
                d_idx = min(int(st.session_state.c_dn_costos) - 1, num_days_s - 1)
                d_s = st.selectbox("Día ", list(range(1, num_days_s + 1)), index=d_idx, key="postergar_birth_day", label_visibility="collapsed")
                st.session_state.c_dn_costos = d_s
            
            try:
                fecha_nac_s = date(int(y_s), int(m_s), int(d_s))
            except:
                fecha_nac_s = date(int(y_s), int(m_s), 1)
                
            edad_inicial = today.year - fecha_nac_s.year - ((today.month, today.day) < (fecha_nac_s.month, fecha_nac_s.day))
            st.markdown(f"<p style='margin-top: -15px; margin-bottom: 10px; font-size: 0.85rem; opacity: 0.8; font-weight: 600; color: {ACCENT_COLOR if is_dark else '#555'};'>EDAD DETECTADA: {edad_inicial} AÑOS</p>", unsafe_allow_html=True)
        
        st.subheader("Costo de Postergar")
        
        # Sincronización con el Hub (Renta mensual deseada)
        renta_def = st.session_state.get("renta_costos_sync", 50000.0)
        if "renta_sync_sidebar" in st.session_state:
            st.session_state.renta_costos_sync = float(st.session_state.renta_sync_sidebar)
            renta_def = st.session_state.renta_costos_sync
        
        renta_actual_label = renta_def
        # Etiqueta personalizada con formato resaltado
        st.markdown(f"<p style='margin-bottom: 5px; font-weight: 900; text-transform: uppercase; font-size: 0.88rem; letter-spacing: 0.8px; color: {ACCENT_COLOR if is_dark else '#555'};'>Retiro Mensual Deseado <span style='font-size: 1.25rem; font-weight: 900; color: {GOLD_COLOR if is_dark else '#000'};'>${renta_actual_label:,.0f}</span></p>", unsafe_allow_html=True)
        renta_mensual_sidebar = st.number_input("Retiro Mensual Deseado", min_value=1000.0, value=float(renta_def), step=5000.0, key="renta_sync_sidebar", label_visibility="collapsed")
        
        # Guardar valor actualizado en session_state persistente
        st.session_state.renta_costos_sync = float(renta_mensual_sidebar)
        
        # Actualizar default de retiro basado en la edad inicial
        # Regla: <=35 -> 60, >=36 -> 65. Tope 70.
        opciones_retiro = [60, 65, 70]
        # Filtrar para que solo muestre opciones mayores a la edad inicial
        opciones_retiro = [o for o in opciones_retiro if o > edad_inicial]
        if not opciones_retiro: opciones_retiro = [70] # Failsafe si el usuario tiene 70
        
        desired_default = 60 if edad_inicial <= 35 else 65
        e_retiro_state = st.session_state.get('costos_edad_retiro', desired_default)
        if e_retiro_state not in opciones_retiro:
            e_retiro_state = desired_default if desired_default in opciones_retiro else opciones_retiro[0]
        idx_retiro = opciones_retiro.index(e_retiro_state) if e_retiro_state in opciones_retiro else 0
        edad_retiro = st.selectbox('Edad a la que te quieres retirar', opciones_retiro, index=idx_retiro)
        rendimiento_anual = st.number_input('Rendimiento Anual Estimado (%)', min_value=1.0, value=10.0, step=0.5)
        st.markdown('<hr style="margin: 10px 0; opacity: 0.1;">', unsafe_allow_html=True)
        col_inf1, col_inf2 = st.columns(2)
        with col_inf1:
            st.markdown(f'<p style="margin-bottom: 5px; font-weight: 700; font-size: 0.8rem; color: {ACCENT_COLOR if is_dark else "#555"};">INFLACIÓN</p>', unsafe_allow_html=True)
            inflacion_opcion = st.selectbox('Inflación', ['Activada', 'Desactivada'], index=0, label_visibility='collapsed', key='inf_toggle_postergar')
        with col_inf2:
            st.markdown(f'<p style="margin-bottom: 5px; font-weight: 700; font-size: 0.8rem; color: {ACCENT_COLOR if is_dark else "#555"};">% INFLACIÓN</p>', unsafe_allow_html=True)
            tasa_inf_input = st.number_input('% Inflación', min_value=0.0, max_value=10.0, value=4.0, step=0.1, label_visibility='collapsed', key='inf_val_postergar')
        inflacion_activa = (inflacion_opcion == "Activada")
        
        # Blindar poder adquisitivo toggle
        st.markdown(f'<p style="margin-top: 10px; margin-bottom: 5px; font-weight: 700; font-size: 0.8rem; color: {ACCENT_COLOR if is_dark else "#555"};">BLINDAJE DE PODER ADQUISITIVO</p>', unsafe_allow_html=True)
        blindar_adquisitivo = st.toggle("Blindar poder adquisitivo", value=False, key="blindar_adquisitivo_postergar")
        
        tasa_inf_blindaje = 4.0
        if blindar_adquisitivo:
            st.markdown(f'<p style="margin-top: 5px; margin-bottom: 5px; font-weight: 700; font-size: 0.8rem; color: {ACCENT_COLOR if is_dark else "#555"};">% INFLACIÓN DE BLINDAJE</p>', unsafe_allow_html=True)
            tasa_inf_blindaje = st.number_input('% Inflación de Blindaje', min_value=0.0, max_value=10.0, value=4.0, step=0.1, key='inf_val_blindaje_postergar', label_visibility='collapsed')
        
        # Disparador Secreto Disfrazado (Icono de Seguridad) para Patrimonio Actual
        if 'show_patrimonio' not in st.session_state:
            st.session_state.show_patrimonio = False
        if 'patrimonio_persist' not in st.session_state:
            st.session_state.patrimonio_persist = 0.0
            
        st.markdown('<div id="secret-shield-trigger"></div>', unsafe_allow_html=True)
        if st.button("🛡️", key="secret_pat_shield_costos"):
            st.session_state.show_patrimonio = not st.session_state.show_patrimonio
            st.rerun()
        
        if st.session_state.show_patrimonio:
            patrimonio_actual = st.number_input("Patrimonio actual ($)", min_value=0.0, value=st.session_state.patrimonio_persist, step=10000.0, key="pat_input_widget_costos")
            st.session_state.patrimonio_persist = patrimonio_actual
        else:
            patrimonio_actual = st.session_state.patrimonio_persist

        años_inversion = edad_retiro - edad_inicial
        r_anual_dec = rendimiento_anual / 100.0
        
        # Lógica de Blindaje de Poder Adquisitivo: VF = VP * (1 + pi)^n
        if blindar_adquisitivo:
            tasa_blindaje = (tasa_inf_blindaje / 100.0)
            renta_mensual_calculada = renta_mensual_sidebar * ((1 + tasa_blindaje) ** años_inversion)
        else:
            renta_mensual_calculada = renta_mensual_sidebar
            
        meta_retiro = (renta_mensual_calculada * 12) / (r_anual_dec if r_anual_dec > 0 else 0.01)
        fv_patrimonio = patrimonio_actual * ((1 + r_anual_dec) ** años_inversion)
        meta_neta = max(0.0, meta_retiro - fv_patrimonio)
        st.session_state.meta_retiro_val = meta_retiro
        st.markdown('<hr style="margin: 10px 0; opacity: 0.1;">', unsafe_allow_html=True)
        frecuencia = st.selectbox('Frecuencia de Visualización', ['Mensual', 'Semestral', 'Anual'], index=2)
        dict_factores = {'Mensual': 1, 'Semestral': 6, 'Anual': 12}
        factor_frecuencia = dict_factores[frecuencia]
        label_dinamico = f'Aportación {frecuencia}'

    # --- LÓGICA DE CÁLCULO UNIFICADA (IGUALITO AL PROYECTO 5%) ---
    # Buscamos la aportación inicial necesaria para llegar a la meta real de hoy (sin inflar la meta a futuro).
    # Pasamos inflacion_activa=inflacion_activa para que la aportación CREZCA con el tiempo (Allianz Style)
    # y así arrancar con una cantidad más cómoda que llegará a la misma meta.
    aporte_m = encontrar_aporte_necesario(
        meta_neta, 
        int(edad_inicial), 
        años_inversion, 
        rendimiento_anual, 
        inflacion_activa, 
        tasa_inf_input,
        isr=0.0
    )
    
    # Generar el desglose REAL empezando HOY para usarlo en métricas y tablas
    df_costos_real, _ = calcular_escenario(
        aporte_m, 
        int(edad_inicial), 
        rendimiento_anual, 
        inflacion_activa, 
        tasa_inf_input,
        isr_retencion=0.0,
        plazo_anos=años_inversion
    )

    # Guardar la tabla dinámica completa para que sea consumida por la calculadora de suspensión
    st.session_state.df_costos_postergar = df_costos_real

    # Variable global para el dashboard y la tabla de costos
    aporte_m_metric = aporte_m

    # --- DASHBOARD UNIFICADO (CABECERA + MÉTRICAS + TABLA COSTE ESPERA) ---
    # Los cálculos de años_inversion, aporte_m, etc., ya están arriba
    
    # Definiciones para compatibilidad con Proyecto 5%
    rendimiento_retiro = rendimiento_anual 
    label_dinamico_retiro = f"Renta Anual ({rendimiento_retiro}%)"

    # Pre-calcular las filas de la tabla de costos para insertarlas en el bloque maestro
    costos_espera_list = []
    r_anual_dec = rendimiento_anual / 100.0
    r_mensual_dec = r_anual_dec / 12.0
    
    # Mostrar primeros 10 años, luego cada 5 años hasta la edad de retiro
    p_delays = list(range(1, 11))
    for extra_y in range(15, (edad_retiro - edad_inicial) + 5, 5):
        p_delays.append(extra_y)
        
    for p_delay in p_delays:
        edad_espera = edad_inicial + p_delay
        if edad_espera >= edad_retiro:
            break
            
        meses_e = (edad_retiro - edad_espera) * 12
        años_restantes = (edad_retiro - edad_espera)
        
        # El objetivo sigue siendo la meta neta real
        if meses_e > 0:
            aporte_e = encontrar_aporte_necesario(
                meta_neta, 
                int(edad_espera), 
                años_restantes, 
                rendimiento_anual, 
                inflacion_activa, 
                tasa_inf_input,
                isr=0.0
            )
            # Calcular el total pagado REAL (considerando incrementos por inflación si están activos)
            df_e, _ = calcular_escenario(aporte_e, int(edad_espera), rendimiento_anual, inflacion_activa, tasa_inf_input, isr_retencion=0.0, plazo_anos=años_restantes)
            total_pago = df_e['Aportación Acumulada'].iloc[-1]
        else:
            aporte_e = meta_neta
            total_pago = meta_neta
            
        rendimiento_total = meta_retiro - total_pago
        
        costos_espera_list.append({
            "edad": edad_espera,
            "aporte": aporte_e,
            "diff": aporte_e - aporte_m_metric,
            "sobre_costo_total": total_pago - (aporte_m_metric * 12 * (edad_retiro - edad_inicial)), # Simplificado o real? Usamos diferencia de totales
            "total_pago": total_pago,
            "rendimiento": rendimiento_total
        })

    # Generar el HTML de las filas
    # Fila Especial: HOY
    # Obtenemos el total REAL aportado hoy del plan principal (ya calculado arriba)
    # df_costos_real es el plan empezando HOY
    total_pago_hoy = df_costos_real['Aportación Acumulada'].iloc[-1]
    rendimiento_hoy = meta_retiro - total_pago_hoy

    rows_html_unified = f'<tr style="background-color: {ACCENT_COLOR}11; border-bottom: 2px solid {ACCENT_COLOR}33;">' \
                         f'<td style="padding: 15px; color: {ACCENT_COLOR}; font-weight: 800; text-align: center; text-transform: uppercase;">Hoy ({edad_inicial} años)</td>' \
                         f'<td style="padding: 15px; color: {ACCENT_COLOR}; font-family: Cinzel, serif; font-size: 1.25rem; font-weight: 800; text-align: center;">${aporte_m_metric:,.2f}</td>' \
                         f'<td style="padding: 15px; color: {ACCENT_COLOR}; font-weight: 800; text-align: center; letter-spacing: 1px;">-</td>' \
                         f'<td style="padding: 15px; color: {ACCENT_COLOR}; font-weight: 800; text-align: center; letter-spacing: 1px;">-</td>' \
                         f'<td style="padding: 15px; color: {ACCENT_COLOR}; font-weight: 800; text-align: center;">${total_pago_hoy:,.0f}</td>' \
                         f'<td style="padding: 15px; color: #34D399; font-weight: 800; text-align: center;">${rendimiento_hoy:,.0f}</td>' \
                         f'</tr>'

    for itm in costos_espera_list:
        sobre_costo_real = itm["total_pago"] - total_pago_hoy
        diff_clr = "#ff4b4b" if itm['diff'] > 0 else TEXT_COLOR
        bg_r = "rgba(255,255,255,0.03)" if itm['edad'] % 2 == 0 else "transparent"
        rows_html_unified += f'<tr style="background-color: {bg_r}; border-bottom: 1px solid rgba(255,255,255,0.05);">' \
                             f'<td style="padding: 15px; color: {TEXT_COLOR}; font-weight: bold; text-align: center;">{itm["edad"]} años</td>' \
                             f'<td style="padding: 15px; color: {ACCENT_COLOR}; font-family: Cinzel, serif; font-size: 1.25rem; font-weight: 700; text-align: center;">${itm["aporte"]:,.2f}</td>' \
                             f'<td style="padding: 15px; color: {diff_clr}; font-weight: bold; text-align: center;">+${itm["diff"]:,.2f}</td>' \
                             f'<td style="padding: 15px; color: {diff_clr}; font-weight: bold; text-align: center;">${sobre_costo_real:,.0f}</td>' \
                             f'<td style="padding: 15px; color: {TEXT_COLOR}; text-align: center;">${itm["total_pago"]:,.0f}</td>' \
                             f'<td style="padding: 15px; color: #34D399; font-weight: bold; text-align: center;">${itm["rendimiento"]:,.0f}</td>' \
                             f'</tr>'

    # Cálculos para el resumen narrativo
    meta_millones = meta_retiro / 1_000_000
    rendimiento_anual_monto = meta_retiro * (rendimiento_anual / 100.0)

    # Cálculo del bono de bienvenida basado en la aportación hoy
    bono_pct = obtener_porcentaje_bono(aporte_m_metric)
    bono_monto = (aporte_m_metric * 12) * bono_pct
    bono_mensual_ano1 = bono_monto / 12

    # --- PESTAÑAS DE NAVEGACIÓN SUPERIOR (Premium Tabs) ---
    st.markdown("""
        <style>
        div[data-testid="stSegmentedControl"] {
            display: flex;
            justify-content: center;
            margin-bottom: 30px !important;
            background: rgba(255, 255, 255, 0.03);
            padding: 8px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(5px);
        }
        div[data-testid="stSegmentedControl"] button {
            font-size: 1.05rem !important;
            font-weight: bold !important;
            padding: 8px 18px !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    opciones_nav = ["⏱️ Costo de Postergar", "📊 Plan de Acumulación", "🧮 Interés Compuesto", "📈 Planificador Financiero"]
    seleccion_nav = st.segmented_control(
        "Navegación Superior",
        options=opciones_nav,
        default="⏱️ Costo de Postergar",
        key="main_nav_pestañas_postergar",
        label_visibility="collapsed"
    )
    nombre_cliente = st.session_state.get('nombre_cliente', '') or st.session_state.get('hub_nombre', '')
    if seleccion_nav == "📊 Plan de Acumulación":
        base = float(aporte_m_metric)
        st.session_state.monto_1 = base
        st.session_state.monto_0 = max(1000.0, base - 1000.0)
        st.session_state.monto_2 = base + 1000.0
        st.session_state.num_escenarios = 3
        
        # Sincronizar nombre y modulo activo
        nombre_cliente_sync = st.session_state.get('nombre_cliente', '') or st.session_state.get('hub_nombre', '')
        st.session_state.hub_nombre = nombre_cliente_sync.title()
        
        # Calcular edad actual para hub_edad
        today = date.today()
        y_s_val = int(st.session_state.get('c_yn_costos', today.year - 25))
        m_names_list = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        m_s_s_val = st.session_state.get('c_mn_costos', 'Enero')
        m_s_val = m_names_list.index(m_s_s_val) + 1 if m_s_s_val in m_names_list else 1
        d_s_val = int(st.session_state.get('c_dn_costos', 1))
        try:
            birth_h = date(y_s_val, m_s_val, d_s_val)
        except:
            birth_h = date(y_s_val, m_s_val, 1)
        st.session_state.hub_edad = today.year - birth_h.year - ((today.month, today.day) < (birth_h.month, birth_h.day))
        
        st.session_state.modulo_activo = "📊 Plan de Acumulación"
        st.rerun()
    elif seleccion_nav == "🧮 Interés Compuesto":
        st.session_state.nombre_cliente = nombre_cliente.title()
        st.session_state.hub_nombre = nombre_cliente.title()
        st.session_state.modulo_activo = "🧮 Interés Compuesto"
        st.rerun()
    elif seleccion_nav == "📈 Planificador Financiero":
        st.session_state.modulo_activo = "📈 Planificador Financiero"
        st.rerun()

    # BLOQUE MAESTRO HUD UNIFICADO
    st.markdown(f"""
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-bottom: 10px; opacity: 0.9;">
    <h1 class="white-title special-elite" style="margin: 0; padding: 0; line-height: 1.0; font-size: 3.5rem;">COSTO DE POSTERGAR</h1>
    <h2 style="color: {ACCENT_COLOR}; text-transform: uppercase; letter-spacing: 2px; font-size: 1.2rem; margin-top: 10px;">EL COSTO DE LA ESPERA</h2>
</div>
<div style="text-align: center; margin-top: -15px; margin-bottom: 25px; font-size: 1.2rem; color: {TEXT_COLOR}; font-family: 'Montserrat', sans-serif;">
    Proyección para el cliente: <b>{nombre_cliente.title()}</b>
</div>
<div style="display: flex; gap: 20px; justify-content: center; margin-bottom: 40px; flex-wrap: wrap;">
<div style="flex: 1; min-width: 250px; max-width: 400px; background-color: {CARD_BG}; border: 1px solid #34D399; border-radius: 12px; padding: 25px; text-align: center; border-top: 5px solid #34D399; box-shadow: 0 10px 25px rgba(0,0,0,0.4); min-height: 190px; height: auto; display: flex; flex-direction: column; justify-content: center;">
<p style="color: {TEXT_COLOR}; font-size: 0.85rem; margin: 0; text-transform: uppercase; letter-spacing: 1px; opacity: 0.6;">{"Retiro Mensual Blindado" if blindar_adquisitivo else "Retiro Mensual"}</p>
<div style="color: #34D399; font-size: 2.3rem; font-weight: bold; margin: 5px 0; text-shadow: 0 0 10px #34D39944;">${renta_mensual_calculada:,.0f}</div>
<div style="color: #34D399; font-size: 0.95rem; opacity: 1.0; margin-top: 8px; font-weight: bold; text-transform: uppercase;">{f"Equivalente a ${renta_mensual_sidebar:,.0f} de hoy (con inflación al {tasa_inf_blindaje:.1f}%)" if blindar_adquisitivo else "Esta cantidad equivale al poder adquisitivo actual"}</div>
</div>
<div style="flex: 1; min-width: 250px; max-width: 400px; background-color: {CARD_BG}; border: 1px solid {GOLD_COLOR}; border-radius: 12px; padding: 25px; text-align: center; border-top: 5px solid {GOLD_COLOR}; box-shadow: 0 10px 25px rgba(0,0,0,0.4); min-height: 190px; height: auto; display: flex; flex-direction: column; justify-content: center;">
<p style="color: {TEXT_COLOR}; font-size: 0.85rem; margin: 0; text-transform: uppercase; letter-spacing: 1px; opacity: 0.6;">Meta de Retiro ({edad_retiro} años)</p>
<div style="color: {GOLD_COLOR}; font-size: 2.3rem; font-weight: bold; margin: 5px 0; text-shadow: 0 0 10px {GOLD_COLOR}44;">${meta_retiro:,.0f}</div>
<div style="color: {GOLD_COLOR}; font-weight: bold; font-size: 0.85rem; opacity: 0.85; text-transform: uppercase;">${meta_retiro:,.0f} x {rendimiento_anual:.1f}% = ${rendimiento_anual_monto:,.0f} ANUAL</div>
</div>
<div style="flex: 1; min-width: 250px; max-width: 400px; background-color: {CARD_BG}; border: 1px solid {ACCENT_COLOR}; border-radius: 12px; padding: 25px; text-align: center; border-top: 5px solid {ACCENT_COLOR}; box-shadow: 0 10px 25px rgba(0,0,0,0.4); min-height: 190px; height: auto; display: flex; flex-direction: column; justify-content: center;">
<p style="color: {TEXT_COLOR}; font-size: 0.85rem; margin: 0; text-transform: uppercase; letter-spacing: 1px; opacity: 0.6;">Aportación Mensual</p>
<div style="color: {ACCENT_COLOR}; font-size: 2.3rem; font-weight: bold; margin: 5px 0; text-shadow: 0 0 10px {ACCENT_COLOR}44;">${aporte_m_metric:,.2f}</div>
<div style="color: {ACCENT_COLOR}; font-weight: bold; font-size: 0.9rem; opacity: 0.8;">PARA LOGRAR LA META</div>
</div>
<div style="flex: 1; min-width: 250px; max-width: 400px; background-color: {CARD_BG}; border: 1px solid #A855F7; border-radius: 12px; padding: 25px; text-align: center; border-top: 5px solid #A855F7; box-shadow: 0 10px 25px rgba(0,0,0,0.4); min-height: 190px; height: auto; display: flex; flex-direction: column; justify-content: center;">
<p style="color: {TEXT_COLOR}; font-size: 0.85rem; margin: 0; text-transform: uppercase; letter-spacing: 1px; opacity: 0.6;">🎁 Bono de bienvenida (Hoy)</p>
<div style="color: #A855F7; font-size: 2.3rem; font-weight: bold; margin: 5px 0; text-shadow: 0 0 10px #A855F744;">${bono_monto:,.0f}</div>
<div style="color: #A855F7; font-weight: bold; font-size: 0.9rem; opacity: 0.8;">{bono_pct*100:.0f}% DE BONO ACREDITADO</div>
<div style="color: #A855F7; font-size: 0.7rem; opacity: 0.8; margin-top: 5px; font-weight: bold; text-transform: uppercase;">+${bono_mensual_ano1:,.0f} al mes en el Año 1</div>
</div>
</div>

<div style="width: 100%; background: {CARD_BG}; border: 1px solid {ACCENT_COLOR}33; border-top: 5px solid {ACCENT_COLOR}; border-radius: 12px; padding: 30px; margin-bottom: 45px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); text-align: center; position: relative; overflow: hidden;">
    <div style="position: absolute; top: 0; right: 0; width: 100px; height: 100px; background: radial-gradient(circle at top right, {ACCENT_COLOR}15, transparent); pointer-events: none;"></div>
    <p style="color: {TEXT_COLOR}; font-size: 1.35rem; line-height: 1.6; margin: 0; font-family: 'Montserrat', sans-serif;">
        Para garantizar un retiro mensual de <span style="color: {GOLD_COLOR}; font-weight: 800;">${renta_mensual_calculada:,.0f}</span>, 
        es indispensable consolidar un fondo de inversión de <span style="color: #34D399; font-weight: 800;">${meta_retiro:,.0f}</span> 
        que genere un rendimiento de <span style="color: {GOLD_COLOR}; font-weight: 800;">${rendimiento_anual_monto:,.0f}</span> anuales.
    </p>
    <div style="height: 1px; background: linear-gradient(90deg, transparent, {ACCENT_COLOR}44, transparent); margin: 25px auto; width: 70%;"></div>
    <p style="color: {TEXT_COLOR}; font-size: 1.35rem; line-height: 1.6; margin: 0; font-family: 'Montserrat', sans-serif; opacity: 0.95;">
        Por lo tanto, considerando que actualmente tienes <span style="color: #34D399; font-weight: 800;">{edad_inicial} años</span>, 
        el plan de acción requiere una aportación mensual de <span style="color: {GOLD_COLOR}; font-weight: 800;">${aporte_m_metric:,.2f}</span>.
    </p>
</div>
<div style="text-align: center; margin-bottom: 20px;">
    <h3 style="font-family: 'Cinzel', serif; color: {TEXT_COLOR}; border-bottom: 2px solid {GOLD_COLOR}; display: inline-block; padding-bottom: 5px; letter-spacing: 2px;">EL COSTO DE POSTERGAR</h3>
    <p style="color: {ACCENT_COLOR}; font-size: 1.1rem; margin-top: 10px; font-weight: bold;">¿Cuánto te cuesta cada año que esperas?</p>
    <p style="color: {TEXT_COLOR}; font-size: 0.95rem; margin-top: 5px; opacity: 0.8; max-width: 800px; margin-left: auto; margin-right: auto;">Como puedes ver, cada mes que pasa estás comprando el mismo retiro a un precio más caro. ¿Le ponemos pausa a esta fuga de dinero hoy o agendamos para el próximo mes con un costo todavía mayor?</p>
</div>
<div style="background: rgba(10, 10, 10, 0.5); border: 1px solid rgba(184, 134, 11, 0.2); border-radius: 12px; padding: 10px; box-shadow: 0 15px 35px rgba(0,0,0,0.6); margin-bottom: 40px;">
    <table style="width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif;">
        <thead style="border-bottom: 2px solid {GOLD_COLOR};">
            <tr>
                <th style="padding: 18px; color: {GOLD_COLOR}; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1.5px; text-align: center;">Si comienzas tu plan</th>
                <th style="padding: 18px; color: {GOLD_COLOR}; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1.5px; text-align: center;">Aportación Mensual</th>
                <th style="padding: 18px; color: {GOLD_COLOR}; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1.5px; text-align: center;">Sobre Costo Mensual</th>
                <th style="padding: 18px; color: {GOLD_COLOR}; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1.5px; text-align: center;">Monto total de sobre costo mensual</th>
                <th style="padding: 18px; color: {GOLD_COLOR}; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1.5px; text-align: center;">Monto total de aportación acumulada</th>
                <th style="padding: 18px; color: {GOLD_COLOR}; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1.5px; text-align: center;">Monto total de rendimiento acumulado</th>
            </tr>
        </thead>
        <tbody style="text-align: center;">{rows_html_unified}</tbody>
    </table>
</div>
<div style="text-align: center; margin-top: -30px; margin-bottom: 50px; opacity: 0.7;">
    <p style="color: {TEXT_COLOR}; font-size: 0.9rem; font-style: italic;">
        * Nota: Los montos de aportación y rendimiento acumulado consideran el periodo completo desde el inicio del plan hasta la edad de retiro ({edad_retiro} años).
    </p>
</div>
""", unsafe_allow_html=True)

    tab_grafica_postergar, tab_dinamica, tab_retiro = st.tabs(["📈 Gráfica de Costos", "📊 Tabla Dinámica", "💰 Etapa de Retiro"])

    with tab_dinamica:
        st.markdown(f"<h3 style='text-align: center; color: {GOLD_COLOR};'>Plan de Acumulación: ${meta_retiro:,.2f} a los {edad_retiro} años</h3>", unsafe_allow_html=True)
        st.write(f"Esta tabla muestra el desglose temporal de sus aportaciones e intereses hasta la meta de retiro.")
        
        # El DataFrame df_costos_real ya fue calculado arriba para HOY
        df_espera_full = df_costos_real.copy()
        
        # Adaptar el DataFrame a la frecuencia seleccionada (Mensual, Semestral, Anual)
        if frecuencia == "Anual":
            df_espera = df_costos_real.groupby('Año').agg({
                'Edad': 'last',
                'Aportación': 'sum',
                'Aportación Acumulada': 'last',
                'Saldo de Fondo': 'last',
                'Saldo Disponible': 'last',
                'Post retención': 'last'
            }).reset_index()
            df_espera.rename(columns={
                'Año': 'AÑO', 
                'Edad': 'EDAD', 
                'Aportación': 'APORTACIÓN ANUAL', 
                'Aportación Acumulada': 'APORTACIÓN ACUMULADA', 
                'Saldo de Fondo': 'SALDO DE FONDO', 
                'Saldo Disponible': 'SALDO DISPONIBLE', 
                'Post retención': 'POST RETENCIÓN'
            }, inplace=True)
            df_espera.insert(2, 'APORTACIÓN MENSUAL', df_costos_real.groupby('Año')['Aportación'].last().values)
        elif frecuencia == "Semestral":
            # Agrupar cada 6 meses
            df_costos_real['Semestre'] = (df_costos_real['Mes Global'] - 1) // 6 + 1
            df_espera = df_costos_real.groupby('Semestre').agg({
                'Año': 'last',
                'Edad': 'last',
                'Aportación': 'sum',
                'Aportación Acumulada': 'last',
                'Saldo de Fondo': 'last',
                'Saldo Disponible': 'last',
                'Post retención': 'last'
            }).reset_index()
            df_espera.rename(columns={
                'Semestre': 'PERIODO',
                'Año': 'AÑO', 
                'Edad': 'EDAD', 
                'Aportación': 'APORTACIÓN SEMESTRAL', 
                'Aportación Acumulada': 'APORTACIÓN ACUMULADA', 
                'Saldo de Fondo': 'SALDO DE FONDO', 
                'Saldo Disponible': 'SALDO DISPONIBLE', 
                'Post retención': 'POST RETENCIÓN'
            }, inplace=True)
            df_espera.insert(3, 'APORTACIÓN MENSUAL', df_costos_real.groupby('Semestre')['Aportación'].last().values)
        else:
            # Mensual
            df_espera = df_costos_real.copy()
            df_espera.rename(columns={
                'Mes Global': 'MES',
                'Año': 'AÑO', 
                'Edad': 'EDAD', 
                'Aportación': 'APORTACIÓN MENSUAL', 
                'Aportación Acumulada': 'APORTACIÓN ACUMULADA', 
                'Saldo de Fondo': 'SALDO DE FONDO', 
                'Saldo Disponible': 'SALDO DISPONIBLE'
            }, inplace=True)
            # Seleccionar únicamente las columnas solicitadas con AÑO primero, luego MES
            columnas_mensuales = ['AÑO', 'MES', 'EDAD', 'APORTACIÓN MENSUAL', 'APORTACIÓN ACUMULADA', 'SALDO DE FONDO', 'SALDO DISPONIBLE']
            df_espera = df_espera[columnas_mensuales]

        if not df_espera.empty:
            if frecuencia == "Mensual":
                col_aporte = "APORTACIÓN MENSUAL"
            else:
                col_aporte = next((c for c in df_espera.columns if "APORTACIÓN" in c and "ACUMULADA" not in c and c != "APORTACIÓN MENSUAL"), "APORTACIÓN ANUAL")
                
            col_periodo = next((c for c in df_espera.columns if c in ["AÑO", "PERIODO", "MES"]), "AÑO")
            
            format_dict = {
                col_aporte: "${:,.0f}",
                "APORTACIÓN ACUMULADA": "${:,.0f}",
                "SALDO DE FONDO": "${:,.0f}",
                "SALDO DISPONIBLE": "${:,.0f}",
                "POST RETENCIÓN": "${:,.0f}",
                "EDAD": "{:.0f}",
                col_periodo: "{:.0f}"
            }
            if "APORTACIÓN MENSUAL" in df_espera.columns:
                format_dict["APORTACIÓN MENSUAL"] = "${:,.0f}"
                
            html_table = (
                df_espera.style
                .format(format_dict)
                .set_properties(**{'text-align': 'center'})
                .hide(axis="index")
                .to_html()
            )
            
            st.markdown(f"""
<style>
    .tabla-espera table {{
        width: 100% !important;
        margin: 0 auto !important;
    }}
    .tabla-espera th {{
        text-align: center !important;
    }}
</style>
<div class="tabla-espera" style="height: 400px; overflow-y: auto; border: 1px solid {BORDER_COLOR}; border-radius: 10px; background-color: {CARD_BG};">
{html_table}
</div>
""", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            fig_g = go.Figure()
            fig_g.add_trace(go.Scatter(
                x=df_espera["AÑO"].tolist() if frecuencia == "Anual" else list(range(1, len(df_espera) + 1)),
                y=df_espera["SALDO DE FONDO"].tolist(),
                mode='lines+markers',
                fill='tozeroy',
                line=dict(color=ACCENT_COLOR, width=3),
                marker=dict(size=6, color=GOLD_COLOR),
                name="Saldo de Fondo"
            ))
            fig_g.update_layout(
                title=f"Crecimiento Proyectado del Saldo ({frecuencia})",
                xaxis_title="Tiempo",
                yaxis_title="Saldo Acumulado ($)",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color=TEXT_COLOR),
                margin=dict(t=50, b=40)
            )
            fig_g.update_yaxes(tickformat="$,.0f", gridcolor="rgba(128,128,128,0.1)")
            fig_g.update_xaxes(gridcolor="rgba(128,128,128,0.1)")
            st.plotly_chart(fig_g, use_container_width=True, theme=None, key="chart_growth_tab_dinamica")

    with tab_grafica_postergar:
        st.markdown(f"<h3 style='text-align: center; color: {GOLD_COLOR};'>Análisis del Costo de Postergar</h3>", unsafe_allow_html=True)
        
        if costos_espera_list:
            # Filtrar para evitar que la gráfica se dispare y arruine la escala (ej. no mostrar el costo de empezar el mismo año del retiro)
            df_c = pd.DataFrame(costos_espera_list)
            df_c_filtered = df_c[df_c["edad"] < edad_retiro].copy()
            
            if not df_c_filtered.empty:
                fig_c = go.Figure()
                fig_c.add_trace(go.Scatter(
                    x=df_c_filtered["edad"],
                    y=df_c_filtered["aporte"],
                    mode='lines+markers',
                    line=dict(color="#ff4b4b", width=3),
                    marker=dict(size=8, color=GOLD_COLOR),
                ))
                # Generar tickvals "bonitos" para log scale (1, 2, 5) que cubran el rango probable
                tick_vals = []
                for i in range(2, 7): # De 100 (10^2) a 1,000,000 (10^6)
                    base = 10**i
                    tick_vals.extend([base, base*2, base*5])
                
                fig_c.update_layout(
                    showlegend=False, 
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font_color=TEXT_COLOR,
                    yaxis_title=None,
                    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title="Edad de Inicio"),
                    yaxis=dict(
                        showgrid=True, 
                        gridcolor='rgba(255,255,255,0.05)', 
                        title=None,
                        tickformat="$,.0f"
                    )
                )
                fig_c.update_xaxes(gridcolor="rgba(128,128,128,0.1)", automargin=True)
                st.plotly_chart(fig_c, use_container_width=True, theme=None, key="chart_costo_espera_linear_focused")
            else:
                st.info("No hay suficientes datos para mostrar la progresión de costos antes de la edad de retiro.")
        

    with tab_retiro:
        st.markdown(f"<h3 style='text-align: center; color: {ACCENT_COLOR};'>Plan de Distribución: Etapa de Jubilación</h3>", unsafe_allow_html=True)
        
        # Nueva Lógica de Retiro Perpetuo (Interés Puro)
        # El pago mensual es simplemente el interés generado por el capital
        r_retiro_mensual = (rendimiento_retiro / 100.0) / 12.0
        pago_mensual_retiro = meta_retiro * r_retiro_mensual
            
        st.success(f"💰 Se estima una renta **perpetua** de **${pago_mensual_retiro:,.2f}** manteniendo el capital íntegro.")
        
        n_periodos_retiro = 25 # Mostramos 25 años por defecto en la tabla para visualizar la constancia
        datos_retiro = []
        
        for p in range(1, n_periodos_retiro + 1):
            monto_periodo_rec = pago_mensual_retiro * 12 # Rendimiento Anual
            
            # En un fondo perpetuo, el saldo remanente es siempre el capital inicial
            saldo_remanente = meta_retiro
                
            datos_retiro.append({
                "AÑO": p,
                "EDAD": edad_retiro + p,
                label_dinamico_retiro: monto_periodo_rec,
                "Rendimiento Mensual": monto_periodo_rec / 12.0,
                "Fondo de motor de retiro": saldo_remanente
            })
            
        if datos_retiro:
            df_retiro = pd.DataFrame(datos_retiro)
            html_table_ret = (
                df_retiro.style
                .format({
                    label_dinamico_retiro: "${:,.2f}",
                    "Rendimiento Mensual": "${:,.2f}",
                    "Fondo de motor de retiro": "${:,.2f}",
                    "EDAD": "{:.0f}",
                    "AÑO": "{:.0f}"
                })
                .set_properties(**{'text-align': 'center'})
                .hide(axis="index")
                .to_html()
            )
            
            st.markdown(f"""
<style>
    .tabla-espera table {{
        width: 100% !important;
    }}
    .tabla-espera th, .tabla-espera td {{
        text-align: center !important;
    }}
</style>
<div class="tabla-espera" style="height: 400px; overflow-y: auto; border: 1px solid {BORDER_COLOR}; border-radius: 10px; background-color: {CARD_BG};">
{html_table_ret}
</div>
""", unsafe_allow_html=True)
            
            pass
