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
        TEXT_COLOR = "#1A2530"    # Elegant readable dark text
        TEXT_MUTED = "#4B5563"
        ACCENT_COLOR = "#0891B2"  # Cyan selected button
        GOLD_COLOR = "#DFBF72"    # Beautiful dynamic gold
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
            # No modificar 'nombre_cliente' directamente aquí (puede ser gestionado por el widget principal).
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
            
        # Rendimiento Anual Estimado (%) - Sincronizado y Modificable
        st.subheader("Rendimiento")
        rendimiento_anual = st.number_input(
            'Rendimiento Anual Estimado (%)', 
            min_value=1.0, 
            value=float(st.session_state.get("costos_rendimiento_anual", 10.0)), 
            step=0.5,
            key="costos_rendimiento_anual_interes",
            help="Modifica este valor para simular diferentes tasas de rendimiento anual."
        )
        st.session_state.costos_rendimiento_anual = rendimiento_anual
            
        st.subheader("Simulación de Suspensión")
        
        # Selección de Frecuencia de Visualización (Tiempo de Suspensión)
        frecuencia_def = st.session_state.get("interes_frecuencia", "Por año")
        frecuencia_sel = st.selectbox(
            "Tiempo de suspensión", 
            ["Por año", "Por mes"], 
            index=0 if frecuencia_def == "Por año" else 1,
            key="interes_frecuencia_input",
            help="Selecciona si deseas simular la suspensión a nivel de año completo o de un mes específico."
        )
        st.session_state.interes_frecuencia = frecuencia_sel
        
        # Parámetros del Paro
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
            # Mes de paro implícito (Fin de año)
            mes_paro_total = año_paro * 12
        else: # Por mes (Entrada directa del mes a partir del 18)
            mes_paro_total = st.number_input(
                "Mes de la Suspensión (Mes 18+)",
                min_value=18,
                max_value=300,
                value=int(st.session_state.get("interes_mes_paro_directo", 18)),
                step=1,
                key="interes_mes_paro_directo",
                help="Los primeros 17 meses son estrictamente obligatorios."
            )
            
            # Calcular año y mes de plan correspondientes
            año_paro = (mes_paro_total - 1) // 12 + 1
            mes_paro = (mes_paro_total - 1) % 12 + 1
            st.session_state.interes_ano_paro_mes = año_paro
            st.session_state.interes_mes_paro = mes_paro

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
            background: {"#EAEFF2" if not is_dark else "rgba(255, 255, 255, 0.03)"} !important; /* Elegant light grey in light mode, dark transparent in dark mode */
            background-color: {"#EAEFF2" if not is_dark else "rgba(255, 255, 255, 0.03)"} !important;
            padding: 8px !important;
            border-radius: 12px !important;
            border: 2px solid {"#BDC3C7" if not is_dark else "rgba(255, 255, 255, 0.05)"} !important; /* Elegant subtle grey border */
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
        
        /* Force individual tabs to be transparent to strip native dark backgrounds */
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
        
        /* Unselected active state/inactive buttons (aria-checked="false") - Force elegant legibility */
        div[data-testid="stSegmentedControl"] button[aria-checked="false"],
        .stSegmentedControl button[aria-checked="false"],
        div[data-testid="stSegmentedControl"] [role="radio"][aria-checked="false"],
        .stSegmentedControl [role="radio"][aria-checked="false"],
        div[data-testid="stSegmentedControl"] button[aria-checked="false"] p,
        div[data-testid="stSegmentedControl"] button[aria-checked="false"] div,
        div[data-testid="stSegmentedControl"] button[aria-checked="false"] span,
        div[data-testid="stSegmentedControl"] [role="radio"][aria-checked="false"] p,
        div[data-testid="stSegmentedControl"] [role="radio"][aria-checked="false"] div,
        div[data-testid="stSegmentedControl"] [role="radio"][aria-checked="false"] span,
        div[data-testid="stSegmentedControl"] button[aria-checked="false"] *,
        div[data-testid="stSegmentedControl"] [role="radio"][aria-checked="false"] * {{
            color: {"#1A2530" if not is_dark else "#A0AEC0"} !important; 
            background-color: transparent !important;
            background: transparent !important;
        }}
        
        /* Hover state for buttons */
        div[data-testid="stSegmentedControl"] button:hover,
        div[data-testid="stSegmentedControl"] [role="radio"]:hover,
        div[data-testid="stSegmentedControl"] button:hover p,
        div[data-testid="stSegmentedControl"] button:hover div,
        div[data-testid="stSegmentedControl"] button:hover span,
        div[data-testid="stSegmentedControl"] [role="radio"]:hover p,
        div[data-testid="stSegmentedControl"] [role="radio"]:hover div,
        div[data-testid="stSegmentedControl"] [role="radio"]:hover span,
        div[data-testid="stSegmentedControl"] button:hover *,
        div[data-testid="stSegmentedControl"] [role="radio"]:hover * {{
            color: {"#000000" if not is_dark else "#FEFFFF"} !important;
            background-color: {"rgba(0,0,0,0.06)" if not is_dark else "rgba(255,255,255,0.05)"} !important;
            background: {"rgba(0,0,0,0.06)" if not is_dark else "rgba(255,255,255,0.05)"} !important;
        }}
        
        /* Selected button (active state - aria-checked="true") */
        div[data-testid="stSegmentedControl"] button[aria-checked="true"], 
        .stSegmentedControl button[aria-checked="true"],
        div[data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"],
        .stSegmentedControl [role="radio"][aria-checked="true"],
        div[data-testid="stSegmentedControl"] [role="radiogroup"] button[aria-checked="true"],
        div[data-testid="stSegmentedControl"] [role="radiogroup"] [role="radio"][aria-checked="true"] {{
            background-color: #0891B2 !important; /* Beautiful corporate cyan key blue */
            background: #0891B2 !important;
            box-shadow: 0 4px 10px rgba(8, 145, 178, 0.3) !important;
            border-radius: 8px !important;
        }}
        
        div[data-testid="stSegmentedControl"] [aria-checked="true"] p,
        div[data-testid="stSegmentedControl"] [aria-checked="true"] div,
        div[data-testid="stSegmentedControl"] [aria-checked="true"] span,
        div[data-testid="stSegmentedControl"] [aria-checked="true"] * {{
            color: #FFFFFF !important; /* Hardcoded solid white text for active tab in both themes */
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
        # Evitar modificar la clave 'nombre_cliente' si el widget ya existe; sincronizamos solo el hub global.
        st.session_state['hub_nombre'] = nombre_cliente_sync.title()
        st.session_state['modulo_activo'] = "⏱️ Costo de Postergar"
        st.rerun()
    elif seleccion_nav == "📈 Planificador Financiero":
        st.session_state.modulo_activo = "📈 Planificador Financiero"
        st.rerun()

    # --- CALCULAR O RECUPERAR ESCENARIO BASE ---
    renta_def = st.session_state.get("renta_costos_sync", 50000.0)
    meta_retiro = (renta_def * 12) / 0.10 # 10% por defecto
    rendimiento_anual = st.session_state.get("costos_rendimiento_anual", 10.0)
    inflacion_activa = (st.session_state.get('inf_toggle_postergar', 'Activada') == 'Activada')
    tasa_inf_input = st.session_state.get('inf_val_postergar', 4.0)
    plazo_anos = 25

    # Si ya se ejecutó Costo de Postergar, recuperamos su tabla dinámica oficial para total precisión
    if "df_costos_postergar" in st.session_state:
        df_original = st.session_state.df_costos_postergar
    else:
        # Fallback de cálculo dinámico idéntico
        aporte_m = encontrar_aporte_necesario(
            meta_retiro, 
            int(edad_inicial), 
            plazo_anos, 
            rendimiento_anual, 
            inflacion_activa, 
            tasa_inf_input,
            isr=0.0
        )
        df_original, _ = calcular_escenario(
            aporte_m, 
            int(edad_inicial), 
            rendimiento_anual, 
            inflacion_activa, 
            tasa_inf_input,
            0.0, # isr_retencion
            plazo_anos=plazo_anos
        )

    # Asegurar que mes_paro_total no exceda la tabla
    if mes_paro_total > len(df_original):
        mes_paro_total = len(df_original)

    # --- SIMULACIÓN DE LA SUSPENSIÓN A PARTIR DEL MES SELECCIONADO ---
    r_m = (rendimiento_anual / 100) / 12
    datos_paro = []
    saldo_anterior = 0.0
    total_aportado_con_paro = 0.0
    
    for m in range(1, 301):
        idx_t = min(m - 1, len(df_original) - 1)
        fila_original = df_original.iloc[idx_t]
        edad_m = fila_original["Edad"]
        
        if m <= mes_paro_total:
            # Fase activa: Tomado de la simulación activa original
            aportacion_m = fila_original["Aportación"]
            interes_m = fila_original["Interés Generado"]
            saldo_final_m = fila_original["Saldo Final"]
            total_aportado_con_paro += aportacion_m
        else:
            # Fase suspendida: Crecimiento puro con interés compuesto
            aportacion_m = 0.0
            interes_m = saldo_anterior * r_m
            saldo_final_m = saldo_anterior + interes_m
            
        datos_paro.append({
            "No. de Mes del Plan": m,
            "No. de Año del Plan": (m - 1) // 12 + 1,
            "Edad": int(edad_m),
            "Aportación Mensual": aportacion_m,
            "Interés Generado": interes_m,
            "Saldo de Fondo": saldo_final_m
        })
        saldo_anterior = saldo_final_m
        
    df_paro = pd.DataFrame(datos_paro)
    
    saldo_al_suspender = df_paro.iloc[mes_paro_total - 1]["Saldo de Fondo"]
    final_con_paro = df_paro.iloc[-1]["Saldo de Fondo"]

    # --- MAESTRO HUD COMPUESTO ---
    nombre_cliente = st.session_state.get('nombre_cliente', '') or st.session_state.get('hub_nombre', '')
    
    # Calcular el número del mes del plan y año del plan para mostrar abajo
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
<div style="flex: 1; min-width: 280px; max-width: 380px; background-color: {CARD_BG}; border: 1px solid {GOLD_COLOR}; border-radius: 12px; padding: 25px; text-align: center; border-top: 5px solid {GOLD_COLOR}; box-shadow: 0 10px 25px rgba(0,0,0,0.4); min-height: 190px; height: auto; display: flex; flex-direction: column; justify-content: center;">
<p style="color: {TEXT_COLOR}; font-size: 0.85rem; margin: 0; text-transform: uppercase; letter-spacing: 1px; opacity: 0.6;">Saldo del fondo</p>
<div style="color: {GOLD_COLOR}; font-size: 2.3rem; font-weight: bold; margin: 5px 0; text-shadow: 0 0 10px {GOLD_COLOR}44;">${saldo_al_suspender:,.0f}</div>
<div style="color: {GOLD_COLOR}; font-weight: bold; font-size: 0.95rem; opacity: 0.8; text-transform: uppercase;">Mes {txt_mes_plan} | Año {txt_ano_plan}</div>
</div>
<div style="flex: 1; min-width: 280px; max-width: 380px; background-color: {CARD_BG}; border: 1px solid #34D399; border-radius: 12px; padding: 25px; text-align: center; border-top: 5px solid #34D399; box-shadow: 0 10px 25px rgba(0,0,0,0.4); min-height: 190px; height: auto; display: flex; flex-direction: column; justify-content: center;">
<p style="color: {TEXT_COLOR}; font-size: 0.85rem; margin: 0; text-transform: uppercase; letter-spacing: 1px; opacity: 0.6;">Fondo estimado</p>
<div style="color: #34D399; font-size: 2.3rem; font-weight: bold; margin: 5px 0; text-shadow: 0 0 10px #34D39944;">${final_con_paro:,.0f}</div>
<div style="color: #34D399; font-weight: bold; font-size: 0.9rem; opacity: 0.8;">VALOR AL VENCIMIENTO (25 AÑOS)</div>
</div>
<div style="flex: 1; min-width: 280px; max-width: 380px; background-color: {CARD_BG}; border: 1px solid #A855F7; border-radius: 12px; padding: 25px; text-align: center; border-top: 5px solid #A855F7; box-shadow: 0 10px 25px rgba(0,0,0,0.4); min-height: 190px; height: auto; display: flex; flex-direction: column; justify-content: center;">
<p style="color: {TEXT_COLOR}; font-size: 0.85rem; margin: 0; text-transform: uppercase; letter-spacing: 1px; opacity: 0.6;">Aportación Total Efectiva</p>
<div style="color: #A855F7; font-size: 2.3rem; font-weight: bold; margin: 5px 0; text-shadow: 0 0 10px #A855F744;">${total_aportado_con_paro:,.0f}</div>
<div style="color: #A855F7; font-weight: bold; font-size: 0.9rem; opacity: 0.8;">TOTAL INVERTIDO ANTES DEL PARO</div>
</div>
</div>
""", unsafe_allow_html=True)

    # --- TABS DE RESULTADOS ---
    tab_grafica, tab_tabla = st.tabs(["📈 Gráfica de Crecimiento", "📊 Tabla Dinámica"])
    
    with tab_grafica:
        # Gráfica de crecimiento acumulado usando Plotly
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
        if frecuencia_sel == "Por año":
            st.markdown(f"<h3 style='text-align: center; color: {GOLD_COLOR};'>Tabla Dinámica: Desglose de los Años sin Aportación</h3>", unsafe_allow_html=True)
            st.write(f"Esta tabla detalla de forma anualizada los años sin aportación (desde el momento de la suspensión hasta concluir los 25 años del plan):")
            
            # Filtrar para mostrar únicamente los fines de año posteriores al año de paro
            df_filtrado = df_paro[(df_paro["No. de Mes del Plan"] % 12 == 0) & (df_paro["No. de Año del Plan"] > año_paro)].copy()
            
            # Dar formato a los valores para visualización en tabla
            df_display = df_filtrado.copy()
            df_display["Aportación Anual"] = df_display["Aportación Mensual"] * 12
            df_display["Aportación Anual"] = df_display["Aportación Anual"].apply(lambda x: f"${x:,.2f}")
            df_display["Saldo de Fondo"] = df_display["Saldo de Fondo"].apply(lambda x: f"${x:,.2f}")
            df_display = df_display.rename(columns={"Saldo de Fondo": "Saldo de Fondo (Compuesto)"})
            
            columnas_finales = ["No. de Año del Plan", "Edad", "Aportación Anual", "Saldo de Fondo (Compuesto)"]
        else:
            st.markdown(f"<h3 style='text-align: center; color: {GOLD_COLOR};'>Tabla Dinámica: Desglose de los Meses sin Aportación</h3>", unsafe_allow_html=True)
            st.write(f"Esta tabla detalla de forma mensual los años sin aportación (desde el momento de la suspensión hasta concluir los 25 años del plan):")
            
            # Filtrar para mostrar únicamente desde el mes posterior al paro en adelante
            df_filtrado = df_paro[df_paro["No. de Mes del Plan"] > mes_paro_total].copy()
            
            # Dar formato a los valores para visualización en tabla
            df_display = df_filtrado.copy()
            df_display["Aportación Mensual"] = df_display["Aportación Mensual"].apply(lambda x: f"${x:,.2f}")
            df_display["Saldo de Fondo"] = df_display["Saldo de Fondo"].apply(lambda x: f"${x:,.2f}")
            df_display = df_display.rename(columns={"Saldo de Fondo": "Saldo de Fondo (Compuesto)"})
            
            columnas_finales = ["No. de Año del Plan", "No. de Mes del Plan", "Edad", "Aportación Mensual", "Saldo de Fondo (Compuesto)"]
            
        df_display = df_display[columnas_finales]
        
        # Convertir a HTML estilizado premium para evitar problemas de codificación de Streamlit en Windows
        html_table = (
            df_display.style
            .set_properties(**{'text-align': 'center'})
            .hide(axis="index")
            .to_html()
        )
        
        st.markdown(f"""
<style>
    .tabla-espera table {{
        width: 100% !important;
        margin: 0 auto !important;
        border-collapse: collapse;
        color: {TEXT_COLOR};
        font-family: 'Montserrat', sans-serif;
        font-size: 0.95rem;
    }}
    .tabla-espera th {{
        background-color: {ACCENT_COLOR}22 !important;
        color: {GOLD_COLOR} !important;
        font-weight: bold;
        padding: 12px;
        border-bottom: 2px solid {BORDER_COLOR};
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        text-align: center !important;
    }}
    .tabla-espera td {{
        padding: 10px;
        border-bottom: 1px solid {BORDER_COLOR};
    }}
    .tabla-espera tr:hover {{
        background-color: rgba(255,255,255,0.03);
    }}
</style>
<div class="tabla-espera" style="height: 400px; overflow-y: auto; border: 1px solid {BORDER_COLOR}; border-radius: 10px; background-color: {CARD_BG}; padding: 15px; box-shadow: inset 0 0 10px rgba(0,0,0,0.5);">
{html_table}
</div>
        """, unsafe_allow_html=True)
