import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
import calendar
import os

def render_calculadora(get_asset_path, encontrar_aporte_necesario, calcular_escenario):
    
    # --- CONFIGURACIÓN DE TEMAS ---
    is_dark = st.session_state.get('theme', 'dark') == 'dark'

    if is_dark:
        TEXT_COLOR = "#FEFFFF"
        TEXT_MUTED = "#9CA3AF"
        ACCENT_COLOR = "#6BA4A4" 
        GOLD_COLOR = "#DFBF72"
        CARD_BG = "#252932"
        BORDER_COLOR = "#6BA4A422"
    else:
        TEXT_COLOR = "#1A2530"
        TEXT_MUTED = "#4B5563"
        ACCENT_COLOR = "#0891B2"
        GOLD_COLOR = "#DFBF72"
        CARD_BG = "#FFFFFF"
        BORDER_COLOR = "#E2E8F0"

    # --- SIDEBAR ---
    logo_filename = "1-07.png" if is_dark else "1-01.png"
    logo_sidebar = get_asset_path(logo_filename)
    
    with st.sidebar:
        if os.path.exists(logo_sidebar):
            st.image(logo_sidebar, use_container_width=True)
        st.title("Configuración")
        
        with st.expander("👤 Datos del Cliente", expanded=True):
            nombre_def = st.session_state.get("nombre_cliente", "") or st.session_state.get("hub_nombre", "")
            nombre_input = st.text_input("Nombre", value=nombre_def, key="interes_name_input").title()
            st.session_state['hub_nombre'] = nombre_input
            
            today = date.today()
            st.markdown(f"<p style='margin-bottom: 5px; font-weight: 900; text-transform: uppercase; font-size: 0.88rem; letter-spacing: 0.8px; color: {ACCENT_COLOR if is_dark else '#555'};'>Fecha de Nacimiento</p>", unsafe_allow_html=True)
            cs_d, cs_m, cs_a = st.columns([1.5, 1.8, 1.2])

            if 'c_yn_costos' not in st.session_state: st.session_state.c_yn_costos = today.year - 25
            if 'c_mn_costos' not in st.session_state: st.session_state.c_mn_costos = "Enero"
            if 'c_dn_costos' not in st.session_state: st.session_state.c_dn_costos = 1
            
            with cs_a:
                y_s = st.number_input("Año ", 1940, today.year, value=int(st.session_state.c_yn_costos), key="interes_birth_year", label_visibility="collapsed")
                st.session_state.c_yn_costos = y_s
            with cs_m:
                m_names = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                m_idx = m_names.index(st.session_state.c_mn_costos) if st.session_state.c_mn_costos in m_names else 0
                m_s_s = st.selectbox("Mes ", m_names, index=m_idx, key="interes_birth_month", label_visibility="collapsed")
                st.session_state.c_mn_costos = m_s_s
                m_s = m_names.index(m_s_s) + 1
            with cs_d:
                num_days_s = calendar.monthrange(int(y_s), int(m_s))[1]
                d_idx = min(int(st.session_state.c_dn_costos) - 1, num_days_s - 1)
                d_s = st.selectbox("Día ", list(range(1, num_days_s + 1)), index=d_idx, key="interes_birth_day", label_visibility="collapsed")
                st.session_state.c_dn_costos = d_s
            
            try:
                fecha_nac_s = date(int(y_s), int(m_s), int(d_s))
            except:
                fecha_nac_s = date(int(y_s), int(m_s), 1)
                
            edad_inicial = today.year - fecha_nac_s.year - ((today.month, today.day) < (fecha_nac_s.month, fecha_nac_s.day))
            st.markdown(f"<p style='margin-top: -15px; margin-bottom: 10px; font-size: 0.85rem; opacity: 0.8; font-weight: 600; color: {ACCENT_COLOR if is_dark else '#555'};'>EDAD DETECTADA: {edad_inicial} AÑOS</p>", unsafe_allow_html=True)

        # --- CUADRO: PARÁMETROS GLOBALES (Rendimiento + Simulación de Suspensión) ---
        with st.expander("⚙️ Parámetros Globales", expanded=True):
            rendimiento_anual = st.number_input(
                'Rendimiento Anual Estimado (%)', 
                min_value=1.0, 
                value=float(st.session_state.get("costos_rendimiento_anual", 10.0)), 
                step=0.5,
                key="costos_rendimiento_anual_interes",
                help="Modifica este valor para simular diferentes tasas de rendimiento anual."
            )
            st.session_state.costos_rendimiento_anual = rendimiento_anual
            
            st.markdown(f"<p style='font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; color: {ACCENT_COLOR if is_dark else '#555'}; margin-top: 10px;'>Simulación de Suspensión</p>", unsafe_allow_html=True)
            
            # Frecuencia de suspensión — default: "Por mes"
            frecuencia_def = st.session_state.get("interes_frecuencia", "Por mes")
            frec_opts = ["Por año", "Por mes"]
            frec_idx = frec_opts.index(frecuencia_def) if frecuencia_def in frec_opts else 1
            frecuencia_sel = st.selectbox(
                "Tiempo de suspensión", 
                frec_opts, 
                index=frec_idx,
                key="interes_frecuencia_input",
                help="Selecciona si deseas simular la suspensión a nivel de año completo o de un mes específico."
            )
            st.session_state.interes_frecuencia = frecuencia_sel
            
            if frecuencia_sel == "Por año":
                año_paro = st.number_input(
                    "Suspender a partir del Año", 
                    min_value=2, 
                    max_value=25, 
                    value=int(st.session_state.get("interes_ano_paro", 5)),
                    step=1,
                    key="interes_ano_paro_input",
                    help="El Año 1 está bloqueado porque requiere los 18 meses obligatorios de aportación."
                )
                st.session_state.interes_ano_paro = año_paro
                mes_paro_total = año_paro * 12
                mes_paro = 12
            else:
                mes_paro_total = st.number_input(
                    "Mes de la Suspensión (Mes 18+)",
                    min_value=18,
                    max_value=300,
                    value=int(st.session_state.get("interes_mes_paro_directo", 19)),
                    step=1,
                    key="interes_mes_paro_directo",
                    help="Los primeros 17 meses son estrictamente obligatorios."
                )
                año_paro = (mes_paro_total - 1) // 12 + 1
                mes_paro = (mes_paro_total - 1) % 12 + 1
                st.session_state.interes_ano_paro_mes = año_paro
                st.session_state.interes_mes_paro = mes_paro

        # --- CUADRO: DISPOSICIÓN DE CAPITAL ---
        with st.expander("💰 Disposición de Capital", expanded=True):
            activar_disposicion = st.toggle("Activar Disposición de Capital", value=bool(st.session_state.get("interes_activar_disposicion", False)), key="interes_activar_disposicion_input")
            st.session_state.interes_activar_disposicion = activar_disposicion
            
            if activar_disposicion:
                st.markdown(
                    f"<p style='font-size: 0.78rem; opacity: 0.7; color: {TEXT_COLOR}; margin-top: -4px;'>Solo es posible disponer del capital a partir del <b>Mes 19</b> (completados los primeros 18 pagos obligatorios).</p>",
                    unsafe_allow_html=True
                )
                mes_disposicion = st.number_input(
                    "¿A partir de qué mes quieres disponer del capital?",
                    min_value=19,
                    max_value=300,
                    value=int(st.session_state.get("interes_mes_disposicion", 19)),
                    step=1,
                    key="interes_mes_disposicion_input",
                    help="No se puede retirar antes de completar las primeras 18 mensualidades."
                )
                st.session_state.interes_mes_disposicion = mes_disposicion
                
                tipo_disposicion = st.radio(
                    "¿Cómo quieres disponer del capital?",
                    ["Disponer todo el capital a partir del mes seleccionado", "Retirar una cantidad específica en el mes seleccionado"],
                    key="interes_tipo_disposicion"
                )
                
                monto_retiro_mensual = 0.0
                if tipo_disposicion == "Retirar una cantidad específica en el mes seleccionado":
                    monto_retiro_mensual = st.number_input(
                        "Cantidad a retirar ($)",
                        min_value=0.0,
                        value=float(st.session_state.get("interes_monto_retiro", 0.0)),
                        step=1000.0,
                        key="interes_monto_retiro_input"
                    )
                    st.session_state.interes_monto_retiro = monto_retiro_mensual
            else:
                # Valores por defecto si está desactivado para no romper el código
                mes_disposicion = 19
                tipo_disposicion = "Disponer todo el capital a partir del mes seleccionado"
                monto_retiro_mensual = 0.0

    # --- PESTAÑAS DE NAVEGACIÓN SUPERIOR ---
    opciones_nav = ["⏱️ Costo de Postergar", "📊 Plan de Acumulación", "🧮 Interés Compuesto", "📈 Planificador Financiero"]
    _, col_center_nav, _ = st.columns([2.5, 8, 1.5])
    with col_center_nav:
        st.markdown(f"""
        <style>
        div[data-testid="stSegmentedControl"], .stSegmentedControl {{
            position: relative !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin: 0 auto 30px auto !important;
            width: fit-content !important;
            background: {"#EAEFF2" if not is_dark else "rgba(255, 255, 255, 0.03)"} !important;
            background-color: {"#EAEFF2" if not is_dark else "rgba(255, 255, 255, 0.03)"} !important;
            padding: 8px !important;
            border-radius: 12px !important;
            border: 2px solid {"#BDC3C7" if not is_dark else "rgba(255, 255, 255, 0.05)"} !important;
            box-shadow: {"0 4px 15px rgba(0, 0, 0, 0.05)" if not is_dark else "0 4px 30px rgba(0, 0, 0, 0.1)"} !important;
            backdrop-filter: blur(5px) !important;
        }}
        div[data-testid="stSegmentedControl"] > div, .stSegmentedControl > div {{
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
            background: transparent !important;
            background-color: transparent !important;
        }}
        div[data-testid="stSegmentedControl"] [role="radiogroup"], .stSegmentedControl [role="radiogroup"] {{
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            gap: 10px !important;
            background: transparent !important;
            background-color: transparent !important;
        }}
        div[data-testid="stSegmentedControl"] button, 
        .stSegmentedControl button,
        div[data-testid="stSegmentedControl"] [role="radio"],
        .stSegmentedControl [role="radio"],
        div[data-testid="stSegmentedControl"] [role="radiogroup"] button,
        div[data-testid="stSegmentedControl"] [role="radiogroup"] [role="radio"] {{
            font-size: 1.02rem !important;
            font-weight: bold !important;
            padding: 8px 18px !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
            background-color: transparent !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
        div[data-testid="stSegmentedControl"] button[aria-checked="false"],
        .stSegmentedControl button[aria-checked="false"],
        div[data-testid="stSegmentedControl"] [role="radio"][aria-checked="false"],
        .stSegmentedControl [role="radio"][aria-checked="false"],
        div[data-testid="stSegmentedControl"] button[aria-checked="false"] *,
        div[data-testid="stSegmentedControl"] [role="radio"][aria-checked="false"] * {{
            color: {"#1A2530" if not is_dark else "#A0AEC0"} !important; 
            background-color: transparent !important;
            background: transparent !important;
        }}
        div[data-testid="stSegmentedControl"] button:hover *,
        div[data-testid="stSegmentedControl"] [role="radio"]:hover * {{
            color: {"#000000" if not is_dark else "#FEFFFF"} !important;
            background-color: {"rgba(0,0,0,0.06)" if not is_dark else "rgba(255,255,255,0.05)"} !important;
        }}
        div[data-testid="stSegmentedControl"] button[aria-checked="true"], 
        .stSegmentedControl button[aria-checked="true"],
        div[data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"],
        .stSegmentedControl [role="radio"][aria-checked="true"] {{
            background-color: #0891B2 !important;
            background: #0891B2 !important;
            box-shadow: 0 4px 10px rgba(8, 145, 178, 0.3) !important;
            border-radius: 8px !important;
        }}
        div[data-testid="stSegmentedControl"] [aria-checked="true"] * {{
            color: #FFFFFF !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        seleccion_nav = st.segmented_control(
            "Navegación Superior",
            options=opciones_nav,
            default="🧮 Interés Compuesto",
            key="main_nav_pestañas_interes",
            label_visibility="collapsed"
        )
    
    if seleccion_nav == "📊 Plan de Acumulación":
        st.session_state['modulo_activo'] = "📊 Plan de Acumulación"
        st.rerun()
    elif seleccion_nav == "⏱️ Costo de Postergar":
        nombre_cliente_sync = st.session_state.get('hub_nombre', '')
        st.session_state['hub_nombre'] = nombre_cliente_sync.title()
        st.session_state['modulo_activo'] = "⏱️ Costo de Postergar"
        st.rerun()
    elif seleccion_nav == "📈 Planificador Financiero":
        st.session_state.modulo_activo = "📈 Planificador Financiero"
        st.rerun()

    # --- Aportación Mensual (para el HUD) ---
    aporte_sync = st.session_state.get("aporte_m_metric", None)
    if aporte_sync is not None:
        aporte_display = float(aporte_sync)
    else:
        renta_fallback = st.session_state.get("renta_costos_sync", 50000.0)
        aporte_display = renta_fallback / 10.0

    # --- CALCULAR O RECUPERAR ESCENARIO BASE ---
    renta_def = st.session_state.get("renta_costos_sync", 50000.0)
    meta_retiro = (renta_def * 12) / 0.10
    rendimiento_anual = st.session_state.get("costos_rendimiento_anual", 10.0)
    inflacion_activa = (st.session_state.get('inf_toggle_postergar', 'Activada') == 'Activada')
    tasa_inf_input = st.session_state.get('inf_val_postergar', 4.0)
    plazo_anos = 25

    if "df_costos_postergar" in st.session_state:
        df_original = st.session_state.df_costos_postergar
    else:
        aporte_m = encontrar_aporte_necesario(
            meta_retiro, int(edad_inicial), plazo_anos,
            rendimiento_anual, inflacion_activa, tasa_inf_input, isr=0.0
        )
        df_original, _ = calcular_escenario(
            aporte_m, int(edad_inicial), rendimiento_anual,
            inflacion_activa, tasa_inf_input, 0.0, plazo_anos=plazo_anos
        )

    if mes_paro_total > len(df_original):
        mes_paro_total = len(df_original)

    # --- SIMULACIÓN CON SUSPENSIÓN + DISPOSICIÓN DE CAPITAL ---
    r_m = (rendimiento_anual / 100) / 12
    datos_paro = []
    saldo_anterior = 0.0
    total_aportado_con_paro = 0.0
    # El capital bloqueado es FIJO: el valor del fondo menos el saldo disponible
    # al momento de la suspensión. No crece con interés (es la "deuda" intocable).
    saldo_bloqueado_fijo = 0.0
    
    # Fondo fantasma para llevar la cuenta de los retiros y sus intereses perdidos
    fondo_retirado_fantasma = 0.0

    for m in range(1, 301):
        idx_t = min(m - 1, len(df_original) - 1)
        fila_original = df_original.iloc[idx_t]
        edad_m = fila_original["Edad"]
        saldo_insuficiente_m = False
        
        # 1. Crece el "agujero" de los retiros previos
        interes_fantasma_m = fondo_retirado_fantasma * r_m
        fondo_retirado_fantasma += interes_fantasma_m

        # Fase activa: leemos el cálculo exacto de Allianz (df_original) y le restamos el agujero
        if m <= mes_paro_total:
            aportacion_m = fila_original.get("Aportación Mensual", fila_original.get("Aportación", 0.0))
            interes_m_base = fila_original.get("Interés Generado", fila_original.get("Interés", 0.0))
            saldo_final_m_base = fila_original.get("Saldo de Fondo", fila_original.get("Saldo Final", 0.0))
            saldo_disponible_raw_base = fila_original.get("Saldo Disponible", 0.0)
            
            # Ajustamos los valores mostrados restando el agujero y su interés
            interes_m = max(0.0, interes_m_base - interes_fantasma_m)
            saldo_bruto = max(0.0, saldo_final_m_base - fondo_retirado_fantasma)
            saldo_disponible_m = max(0.0, saldo_disponible_raw_base - fondo_retirado_fantasma)
            
            saldo_disponible_pantalla = saldo_disponible_m
            total_aportado_con_paro += aportacion_m
            
            # Guardar el capital bloqueado FIJO al final de la fase activa
            # El capital base bloqueado no es afectado por retiros, sigue intacto (saldo - disponible)
            saldo_bloqueado_fijo = max(0.0, saldo_final_m_base - saldo_disponible_raw_base)

        # Fase suspendida: crecimiento puro a partir de lo que quedó
        else:
            aportacion_m = 0.0
            interes_m   = saldo_anterior * r_m
            saldo_bruto = saldo_anterior + interes_m
            saldo_disponible_m = max(0.0, saldo_bruto - saldo_bloqueado_fijo)
            saldo_disponible_pantalla = saldo_disponible_m

        retiro_m = 0.0

        # Aplicar disposición de capital de UNA SOLA VEZ en el mes seleccionado
        if activar_disposicion and m == mes_disposicion:
            if tipo_disposicion == "Disponer todo el capital a partir del mes seleccionado":
                retiro_m = saldo_disponible_m
                saldo_bruto -= retiro_m
                saldo_disponible_m = 0.0
                fondo_retirado_fantasma += retiro_m
            else:
                # Retiro de cantidad específica en el mes seleccionado
                if monto_retiro_mensual > saldo_disponible_m:
                    # No hay suficiente → marcar, no retirar
                    saldo_insuficiente_m = True
                    retiro_m = 0.0
                else:
                    retiro_m = monto_retiro_mensual
                    saldo_bruto -= retiro_m
                    saldo_disponible_m -= retiro_m
                    fondo_retirado_fantasma += retiro_m

        saldo_final_m = saldo_bruto

        datos_paro.append({
            "No. de Mes del Plan": m,
            "No. de Año del Plan": (m - 1) // 12 + 1,
            "Edad": int(edad_m),
            "Aportación Mensual": aportacion_m,
            "Interés Generado": interes_m,
            "Retiro": retiro_m,
            "Saldo Disponible": saldo_disponible_pantalla,
            "Saldo Insuficiente Flag": saldo_insuficiente_m,
            "Saldo de Fondo": saldo_final_m
        })
        saldo_anterior = saldo_final_m

    df_paro = pd.DataFrame(datos_paro)



    saldo_al_suspender = df_paro.iloc[mes_paro_total - 1]["Saldo de Fondo"]
    final_con_paro = df_paro.iloc[-1]["Saldo de Fondo"]

    # --- HUD PRINCIPAL ---
    nombre_cliente = st.session_state.get('nombre_cliente', '') or st.session_state.get('hub_nombre', '')
    txt_mes_plan = mes_paro_total
    txt_ano_plan = (mes_paro_total - 1) // 12 + 1

    st.markdown(f"""
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-bottom: 10px; opacity: 0.9;">
    <h1 class="white-title special-elite" style="margin: 0; padding: 0; line-height: 1.0; font-size: 3.5rem;">SUSPENSIÓN DE PLAN</h1>
    <h2 style="color: {ACCENT_COLOR}; text-transform: uppercase; letter-spacing: 2px; font-size: 1.2rem; margin-top: 10px;">EL IMPACTO DE LA ESPERA</h2>
</div>
<div style="text-align: center; margin-top: -15px; margin-bottom: 25px; font-size: 1.2rem; color: {TEXT_COLOR}; font-family: 'Montserrat', sans-serif;">
    Proyección para el cliente: <b>{nombre_cliente.title()}</b>
</div>
<div style="text-align: center; margin-bottom: 30px; font-size: 1.05rem; opacity: 0.8; font-weight: 600;">
    Punto de Suspensión: <span style="color: {GOLD_COLOR}; font-size: 1.2rem;">{f"Año {año_paro}" if frecuencia_sel == "Por año" else f"Año {año_paro}, Mes {mes_paro}"}</span> (Mes {mes_paro_total})
</div>
<div style="display: flex; gap: 20px; justify-content: center; margin-bottom: 40px; flex-wrap: wrap;">
<div style="flex: 1; min-width: 200px; max-width: 280px; background-color: {CARD_BG}; border: 1px solid {ACCENT_COLOR}; border-radius: 12px; padding: 25px; text-align: center; border-top: 5px solid {ACCENT_COLOR}; box-shadow: 0 10px 25px rgba(0,0,0,0.4); min-height: 190px; display: flex; flex-direction: column; justify-content: center;">
<p style="color: {TEXT_COLOR}; font-size: 0.85rem; margin: 0; text-transform: uppercase; letter-spacing: 1px; opacity: 0.6;">Aportación Mensual</p>
<div style="color: {ACCENT_COLOR}; font-size: 2.3rem; font-weight: bold; margin: 5px 0; text-shadow: 0 0 10px {ACCENT_COLOR}44;">${aporte_display:,.0f}</div>
<div style="color: {ACCENT_COLOR}; font-weight: bold; font-size: 0.85rem; opacity: 0.8; text-transform: uppercase;">Desde Costo de Postergar</div>
</div>
<div style="flex: 1; min-width: 200px; max-width: 280px; background-color: {CARD_BG}; border: 1px solid {GOLD_COLOR}; border-radius: 12px; padding: 25px; text-align: center; border-top: 5px solid {GOLD_COLOR}; box-shadow: 0 10px 25px rgba(0,0,0,0.4); min-height: 190px; display: flex; flex-direction: column; justify-content: center;">
<p style="color: {TEXT_COLOR}; font-size: 0.85rem; margin: 0; text-transform: uppercase; letter-spacing: 1px; opacity: 0.6;">Saldo del fondo</p>
<div style="color: {GOLD_COLOR}; font-size: 2.3rem; font-weight: bold; margin: 5px 0; text-shadow: 0 0 10px {GOLD_COLOR}44;">${saldo_al_suspender:,.0f}</div>
<div style="color: {GOLD_COLOR}; font-weight: bold; font-size: 0.95rem; opacity: 0.8; text-transform: uppercase;">Mes {txt_mes_plan} | Año {txt_ano_plan}</div>
</div>
<div style="flex: 1; min-width: 200px; max-width: 280px; background-color: {CARD_BG}; border: 1px solid #34D399; border-radius: 12px; padding: 25px; text-align: center; border-top: 5px solid #34D399; box-shadow: 0 10px 25px rgba(0,0,0,0.4); min-height: 190px; display: flex; flex-direction: column; justify-content: center;">
<p style="color: {TEXT_COLOR}; font-size: 0.85rem; margin: 0; text-transform: uppercase; letter-spacing: 1px; opacity: 0.6;">Fondo estimado</p>
<div style="color: #34D399; font-size: 2.3rem; font-weight: bold; margin: 5px 0; text-shadow: 0 0 10px #34D39944;">${final_con_paro:,.0f}</div>
<div style="color: #34D399; font-weight: bold; font-size: 0.9rem; opacity: 0.8;">VALOR AL VENCIMIENTO (25 AÑOS)</div>
</div>
<div style="flex: 1; min-width: 200px; max-width: 280px; background-color: {CARD_BG}; border: 1px solid #A855F7; border-radius: 12px; padding: 25px; text-align: center; border-top: 5px solid #A855F7; box-shadow: 0 10px 25px rgba(0,0,0,0.4); min-height: 190px; display: flex; flex-direction: column; justify-content: center;">
<p style="color: {TEXT_COLOR}; font-size: 0.85rem; margin: 0; text-transform: uppercase; letter-spacing: 1px; opacity: 0.6;">Aportación Total Efectiva</p>
<div style="color: #A855F7; font-size: 2.3rem; font-weight: bold; margin: 5px 0; text-shadow: 0 0 10px #A855F744;">${total_aportado_con_paro:,.0f}</div>
<div style="color: #A855F7; font-weight: bold; font-size: 0.9rem; opacity: 0.8;">TOTAL INVERTIDO ANTES DEL PARO</div>
</div>
</div>
    """, unsafe_allow_html=True)

    # --- TABS DE RESULTADOS ---
    tab_grafica, tab_tabla = st.tabs(["📈 Gráfica de Crecimiento", "📊 Tabla Dinámica"])
    
    with tab_grafica:
        df_anual = []
        for a in range(1, 26):
            mes_fin = a * 12
            df_anual.append({
                "Año Visual": f"Año {a}",
                "Saldo Con Paro": df_paro.iloc[mes_fin - 1]["Saldo de Fondo"]
            })
        df_anual_df = pd.DataFrame(df_anual)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_anual_df["Año Visual"],
            y=df_anual_df["Saldo Con Paro"],
            mode='lines+markers',
            name="Crecimiento Pasivo (Con Paro)",
            line=dict(color=ACCENT_COLOR, width=3),
            marker=dict(size=6)
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color=TEXT_COLOR,
            margin=dict(t=20, b=20, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickprefix="$")
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with tab_tabla:
        st.markdown(f"<h3 style='text-align: center; color: {GOLD_COLOR};'>Tabla Dinámica: Desglose Completo del Plan</h3>", unsafe_allow_html=True)
        
        frecuencia_sel = st.session_state.get("interes_frecuencia", "Por mes")
        año_paro = st.session_state.get("interes_ano_paro", 5)

        # Si la vista es "Por año", agrupar los datos
        if frecuencia_sel == "Por año":
            df_paro_grouped = df_paro.groupby("No. de Año del Plan").agg({
                "No. de Mes del Plan": "last", 
                "Edad": "last",
                "Aportación Mensual": "mean",
                "Interés Generado": "sum",
                "Retiro": "sum",
                "Saldo Disponible": "last",
                "Saldo Insuficiente Flag": "max",
                "Saldo de Fondo": "last"
            }).reset_index()
            
            aportacion_anual_sum = df_paro.groupby("No. de Año del Plan")["Aportación Mensual"].sum().reset_index()
            df_paro_grouped["Aportación Anual"] = aportacion_anual_sum["Aportación Mensual"]
            
            df_display = df_paro_grouped.copy()
            cols_show = ["No. de Año del Plan", "Edad", "Aportación Mensual", "Aportación Anual", "Interés Generado", "Saldo Disponible", "Saldo de Fondo"]
        else:
            df_display = df_paro.copy()
            cols_show = ["No. de Año del Plan", "No. de Mes del Plan", "Edad", "Aportación Mensual", "Interés Generado", "Saldo Disponible", "Saldo de Fondo"]

        # Reemplazar Saldo Disponible con "SALDO INSUFICIENTE" si la bandera está activa
        df_display["Saldo Disponible"] = df_display.apply(
            lambda r: "SALDO INSUFICIENTE" if r.get("Saldo Insuficiente Flag", False) else r["Saldo Disponible"], axis=1
        )

        # Formatear columnas monetarias
        for col in ["Aportación Mensual", "Aportación Anual", "Interés Generado", "Retiro", "Saldo de Fondo"]:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(lambda x: f"${x:,.2f}")
        
        # Saldo Disponible: puede ser número o "SALDO INSUFICIENTE"
        df_display["Saldo Disponible"] = df_display["Saldo Disponible"].apply(
            lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) else x
        )
        
        # Resaltar el mes de suspensión, el mes de disposición y las filas con saldo insuficiente
        def highlight_row(row):
            ano = row["No. de Año del Plan"]
            mes = row.get("No. de Mes del Plan", 0)
            saldo_disp = row["Saldo Disponible"]
            
            if saldo_disp == "SALDO INSUFICIENTE":
                return ['background-color: #EF444433; color: #EF4444; font-weight: bold;'] * len(row)
            elif mes == mes_disposicion and frecuencia_sel == "Por mes":
                return ['background-color: #34D39955; color: inherit; font-weight: bold;'] * len(row)
            elif frecuencia_sel == "Por año" and ano == año_paro:
                return ['background-color: #34D39955; color: inherit; font-weight: bold;'] * len(row)
            elif frecuencia_sel == "Por mes" and mes == mes_paro_total:
                return ['background-color: #34D39955; color: inherit; font-weight: bold;'] * len(row)
            return [''] * len(row)
        
        html_table = (
            df_display[cols_show].style
            .set_properties(**{'text-align': 'center'})
            .apply(highlight_row, axis=1)
            .hide(axis="index")
            .to_html()
        )

        
        # Añadir ID a la fila de suspensión para poder hacer scroll hacia ella
        # Ojo: reemplazar por un string que encuentre la fila exacta es complejo si Pandas cambia los IDs. 
        # Es más fácil inyectar el script con CSS selector:
        script_scroll = f"""
        <script>
            setTimeout(function() {{
                var rows = window.parent.document.querySelectorAll('iframe')[0].contentWindow.document.querySelectorAll('table tbody tr');
                if (rows && rows.length >= {mes_paro_total}) {{
                    rows[{mes_paro_total - 1}].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                }}
            }}, 500);
        </script>
        """
        # Mejor usar un enfoque sin romper la tabla, agregando un div oculto si hace falta o usando el tr: nth-child. Streamlit ejecuta esto en un iframe.
        # En Streamlit los scripts incrustados dentro de components no funcionan tan fácil si no están en `components.html`.
        # Vamos a probar inyectando un id en el HTML string crudo.
        html_lines = html_table.split("<tr>")
        target_row_idx = año_paro if frecuencia_sel == "Por año" else mes_paro_total
        
        if len(html_lines) > target_row_idx:
            # html_lines[0] is the thead, html_lines[1] is row 1, etc.
            html_lines[target_row_idx] = f'<tr id="row_suspension">' + html_lines[target_row_idx][4:] if html_lines[target_row_idx].startswith("    ") else f'<tr id="row_suspension">' + html_lines[target_row_idx]
            html_table = "<tr>".join(html_lines)
            
        script_scroll = """
        <script>
            var el = window.parent.document.getElementById('row_suspension');
            if (el) { el.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
        </script>
        """
        
        # Leyenda de colores
        leyenda = ""
        if frecuencia_sel == "Por año":
            leyenda += f"<span style='background:#34D39922; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 10px;'>🟢 Año de suspensión (Año {año_paro})</span>"
        else:
            leyenda += f"<span style='background:#34D39922; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 10px;'>🟢 Mes de suspensión (Mes {mes_paro_total})</span>"
        
        if activar_disposicion:
            leyenda += f"<span style='background:#34D39922; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem;'>🟢 Mes de disposición (Mes {mes_disposicion})</span>"
        
        if leyenda:
            st.markdown(f"<div style='margin-bottom: 10px;'>{leyenda}</div>", unsafe_allow_html=True)
        
        st.markdown(f"""
<style>
    .tabla-espera table {{
        width: 100% !important;
        margin: 0 auto !important;
        border-collapse: collapse;
        color: {TEXT_COLOR};
        font-family: 'Montserrat', sans-serif;
        font-size: 0.92rem;
    }}
    .tabla-espera th {{
        background-color: {ACCENT_COLOR}22 !important;
        color: {GOLD_COLOR} !important;
        font-weight: bold;
        padding: 12px;
        border-bottom: 2px solid {BORDER_COLOR};
        text-transform: uppercase;
        font-size: 0.82rem;
        letter-spacing: 0.5px;
        text-align: center !important;
        position: sticky;
        top: 0;
        z-index: 1;
    }}
    .tabla-espera td {{
        padding: 10px;
        border-bottom: 1px solid {BORDER_COLOR};
    }}
    .tabla-espera tr:hover {{
        background-color: rgba(255,255,255,0.03);
    }}
</style>
<div class="tabla-espera" id="tabla-container" style="height: 500px; overflow-y: auto; border: 1px solid {BORDER_COLOR}; border-radius: 10px; background-color: {CARD_BG}; padding: 15px; box-shadow: inset 0 0 10px rgba(0,0,0,0.5);">
{html_table}
</div>
<script>
    setTimeout(function() {{
        var rows = window.parent.document.querySelectorAll('iframe')[0].contentWindow.document.querySelectorAll('.tabla-espera tbody tr');
        if (rows && rows.length >= {mes_paro_total}) {{
            rows[{mes_paro_total - 1}].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        }}
    }}, 600);
</script>
        """, unsafe_allow_html=True)
