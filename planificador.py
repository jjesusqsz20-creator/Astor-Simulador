import streamlit as st
import pandas as pd
import base64
import os
import plotly.express as px
import io
from PIL import Image

def render_planificador():

    def get_base64_of_bin_file(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()


    def get_asset_path(filename):
        return os.path.join(os.path.dirname(__file__), "assets", filename)


    def get_watermark_excel(is_dark_mode=False):
        """Genera una versión transparente y rotada del logo para el fondo de Excel"""
        logo_filename = "1-06.png" if is_dark_mode else "1-07.png"
        logo_path = get_asset_path(logo_filename)
        if not os.path.exists(logo_path):
            return None

        target_path = get_asset_path("watermark_excel.png")
        # Forzar regeneración para aplicar cambios de opacidad/tamaño
        if os.path.exists(target_path):
            try:
                os.remove(target_path)
            except Exception:
                pass

        try:
            img = Image.open(logo_path).convert("RGBA")
            # Ajustar tamaño para que coincida más con la escala visual (110px)
            img.thumbnail((110, 110), Image.Resampling.LANCZOS)

            # Rotar -30 grados (como en la app)
            img = img.rotate(-30, expand=True, resample=Image.Resampling.BICUBIC)

            # Aplicar transparencia (0.10 para un efecto muy sutil)
            alpha = img.split()[3]
            alpha = alpha.point(lambda p: p * 0.10)
            img.putalpha(alpha)

            # Crear un lienzo para el tiling (100px para densidad ultra-impactante)
            canvas_size = 100
            # Si es modo oscuro, el fondo del lienzo debe ser negro (0,0,0,255) para cubrir toda la hoja
            bg_color = (0, 0, 0, 255) if is_dark_mode else (0, 0, 0, 0)
            canvas = Image.new("RGBA", (canvas_size, canvas_size), bg_color)

            # Centrar el logo en el lienzo
            img_w, img_h = img.size
            offset = ((canvas_size - img_w) // 2, (canvas_size - img_h) // 2)
            canvas.paste(img, offset, img)

            canvas.save(target_path)
            return target_path
        except Exception:
            return None



    # --- INICIALIZACIÓN DE ESTADO (PERSISTENCIA ROBUSTA) ---
    # Sincronizar dark_mode con el tema global (dark por defecto, igual que los demás módulos)
    if 'dark_mode' not in st.session_state: st.session_state['dark_mode'] = True
    # Mantener sincronía con el toggle global de Astor.py
    st.session_state['dark_mode'] = (st.session_state.get('theme', 'dark') == 'dark')
    if 'nombre_cliente' not in st.session_state: st.session_state['nombre_cliente'] = "Cliente Ejemplo"
    if 'sidebar_ingreso' not in st.session_state: st.session_state['sidebar_ingreso'] = 25000
    if 'num_dependientes' not in st.session_state: st.session_state['num_dependientes'] = 0
    if 'sidebar_gastos_dep' not in st.session_state: st.session_state['sidebar_gastos_dep'] = 0
    if 'listo' not in st.session_state: st.session_state['listo'] = False

    # Inicializar todas las categorías posibles para evitar pérdida en reruns
    categorias_todas = [
        "🏠 Vivienda (Renta/hipoteca)", "🍎 Despensa", "🚗 Gasolina / Transporte", "⚡ Servicios (luz, agua, gas, internet)", "🧹 Personal de limpieza",
        "🎓 Educación / colegiatura", "🥂 Salidas y restaurante", "📺 Suscripciones y digital", "💅 Cuidado personal y ropa", 
        "🎨 Hobbies y proyectos", "🏋️ Gimnasio/club", "🐾 Mascotas (Comida y cuidados)", "🚲 Uber Eats / Delivery", "✈️ Viajes y Vacaciones", "📂 Otros gastos",
        "🚗 Crédito de auto", "💳 Tarjeta de crédito (Meses sin intereses)", "🏦 Otros créditos"
    ]

    # Definición de sub-listas globales
    nec_opciones = ["🏠 Vivienda (Renta/hipoteca)", "🍎 Despensa", "🚗 Gasolina / Transporte", "⚡ Servicios (luz, agua, gas, internet)", "🧹 Personal de limpieza"]
    est_opciones = ["🎓 Educación / colegiatura", "🥂 Salidas y restaurante", "📺 Suscripciones y digital", "💅 Cuidado personal y ropa", "🎨 Hobbies y proyectos", "🏋️ Gimnasio/club", "🐾 Mascotas (Comida y cuidados)", "🚲 Uber Eats / Delivery", "✈️ Viajes y Vacaciones", "📂 Otros gastos"]
    cred_opciones = ["🚗 Crédito de auto", "💳 Tarjeta de crédito (Meses sin intereses)", "🏦 Otros créditos"]

    for cat in categorias_todas:
        if f"val_{cat}" not in st.session_state: st.session_state[f"val_{cat}"] = 0
        if f"val_est_{cat}" not in st.session_state: st.session_state[f"val_est_{cat}"] = 0
        if f"val_cred_{cat}" not in st.session_state: st.session_state[f"val_cred_{cat}"] = 0
        if f"sidebar_chk_{cat}" not in st.session_state: st.session_state[f"sidebar_chk_{cat}"] = False
        if f"sidebar_chk_est_{cat}" not in st.session_state: st.session_state[f"sidebar_chk_est_{cat}"] = False
        if f"sidebar_chk_cred_{cat}" not in st.session_state: st.session_state[f"sidebar_chk_cred_{cat}"] = False

    # --- CÁLCULO DE SELECCIONES PERSISTENTES ---
    necesidades_sel = [cat for cat in nec_opciones if st.session_state.get(f"sidebar_chk_{cat}", False)]
    estilo_sel = [cat for cat in est_opciones if st.session_state.get(f"sidebar_chk_est_{cat}", False)]
    creditos_sel = [cat for cat in cred_opciones if st.session_state.get(f"sidebar_chk_cred_{cat}", False)]

    # --- SELECCIÓN DE ACTIVOS Y COLORES POR TEMA ---
    if st.session_state['dark_mode']:
        logo_header_file = "1-07.png"
        bg_style = """
            background: 
                radial-gradient(circle at 0% 0%, #E043431A 0%, transparent 40%),
                radial-gradient(circle at 100% 0%, #00CC6A1A 0%, transparent 40%),
                radial-gradient(circle at 50% 100%, #B800D61A 0%, transparent 40%),
                #080A0F !important;
        """
        root_vars = """
            --primary-blue: #FEFFFF;
            --accent-blue: #72A5A5;
            --border-color: #DFBF72;
            --bg-card: #1c2026;
            --input-bg: #13161C;
            --sidebar-bg: #050505;
            --expander-bg: #1c2026;
            --gold-text: #DFBF72;
            --value-color: #DFBF72;
            --main-title-color: #FFFFFF;
        """
    else:
        logo_header_file = "1-01.png"
        bg_style = """
            background: linear-gradient(135deg, #f0f2f5 0%, #e2e8f0 100%) !important;
        """
        root_vars = """
            --primary-blue: #1e3a8a;
            --accent-blue: #3B82F6;
            --border-color: #e5e7eb;
            --bg-card: #ffffff;
            --input-bg: #ffffff;
            --sidebar-bg: #ffffff;
            --expander-bg: #ffffff;
            --gold-text: #F59E0B;
            --value-color: #3B82F6;
            --main-title-color: #364350;
        """

    # --- ESTILOS DE BOTONES DINÁMICOS ---
    if st.session_state['dark_mode']:
        button_css = """
            /* Botón Principal - Glassmorphism */
            div.stButton > button {
                background: rgba(28, 32, 38, 0.8) !important;
                backdrop-filter: blur(10px) !important;
                -webkit-backdrop-filter: blur(10px) !important;
                color: #72A5A5 !important;
                border: 1.5px solid rgba(114, 165, 165, 0.3) !important;
                border-radius: 12px !important;
                padding: 12px 24px !important;
                font-weight: 700 !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2) !important;
            }
            div.stButton > button:hover {
                background: rgba(28, 32, 38, 0.95) !important;
                border-color: #72A5A5 !important;
                transform: translateY(-2px) !important;
            }
            /* Botón de Descarga - Glassmorphism */
            div.stDownloadButton > button {
                background: rgba(28, 32, 38, 0.8) !important;
                backdrop-filter: blur(10px) !important;
                -webkit-backdrop-filter: blur(10px) !important;
                color: #72A5A5 !important;
                border: 1.5px solid rgba(114, 165, 165, 0.3) !important;
                border-radius: 12px !important;
                padding: 12px 24px !important;
                font-weight: 700 !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2) !important;
            }
            div.stDownloadButton > button:hover {
                background: rgba(28, 32, 38, 0.95) !important;
                border-color: #72A5A5 !important;
                transform: translateY(-2px) !important;
            }
            /* Acentos de Tarjetas - Modo Oscuro (Dorado) */
            .glass-card.astor-card {
                border-left: 8px solid var(--border-color) !important;
            }
            .glass-card.semaforo-green {
                border-left: 8px solid #34D399 !important;
            }
            .glass-card.semaforo-yellow {
                border-left: 8px solid #FBBF24 !important;
            }
            .glass-card.semaforo-red {
                border-left: 8px solid #F87171 !important;
            }
            /* Cuadro de Métrica - Modo Oscuro (Dorado) */
            .astor-metric-box {
                background: var(--bg-card) !important;
                border: 2px solid var(--border-color) !important;
                border-left: 8px solid var(--border-color) !important;
                padding: 12px 20px !important;
                border-radius: 12px !important;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
                text-align: center !important;
                min-width: 270px !important;
            }
        """
    else:
        button_css = """
            /* Botón Principal - Light Solid */
            div.stButton > button {
                background-color: white !important;
                color: #1e3a8a !important;
                border: 1px solid #1e3a8a !important;
                border-radius: 8px !important;
                padding: 12px 24px !important;
                font-weight: 600 !important;
                transition: all 0.2s ease !important;
            }
            div.stButton > button:hover {
                background-color: #f3f4f6 !important;
                border-color: #3B82F6 !important;
                color: #3B82F6 !important;
            }
            /* Botón de Descarga - Light Solid (Naranja) */
            div.stDownloadButton > button {
                background-color: white !important;
                color: #F59E0B !important;
                border: 2px solid #F59E0B !important;
                border-radius: 12px !important;
                padding: 12px 24px !important;
                font-weight: 700 !important;
                transition: all 0.3s ease !important;
            }
            div.stDownloadButton > button:hover {
                background-color: #F59E0B !important;
                color: white !important;
            }
            /* Acentos de Tarjetas - Modo Claro (Azul Astor) */
            .glass-card.astor-card {
                border-left: 8px solid #3B82F6 !important;
            }
            .glass-card.semaforo-green {
                border-left: 8px solid #34D399 !important;
            }
            .glass-card.semaforo-yellow {
                border-left: 8px solid #FBBF24 !important;
            }
            .glass-card.semaforo-red {
                border-left: 8px solid #F87171 !important;
            }
            /* Cuadro de Métrica - Modo Claro (Azul Astor) */
            .astor-metric-box {
                background: white !important;
                border: 2px solid #3B82F6 !important;
                border-left: 8px solid #3B82F6 !important;
                padding: 12px 20px !important;
                border-radius: 12px !important;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
                text-align: center !important;
                min-width: 270px !important;
            }
        """

    # --- INYECCIÓN DE CSS PERSONALIZADO ---
    # 1. Variables dinámicas y fondo
    st.markdown(f"""
    <style>
    /* Forzar fondo general */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"] {{
        {bg_style}
    }}

    :root {{
        {root_vars}
    }}

    {button_css}
    </style>
    """, unsafe_allow_html=True)

    # 2. Estilos estáticos
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700;800;900&display=swap');

    /* 2. Sidebar Estilizada */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-color) !important;
    }

    /* 3. Estética de Textos - SOLO headings usan Cinzel */
    h1, h2, h3, h4 {
        color: var(--primary-blue) !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 700 !important;
    }

    /* Texto normal y labels: color del tema, fuente limpia */
    p, label {
        color: var(--primary-blue) !important;
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
        font-weight: 600 !important;
    }

    /* 4. LIMPIEZA TOTAL DE COMPONENTES NEGROS */
    /* Inputs de texto y números - LIMPIEZA Y ENFOQUE AZUL */
    .stTextInput input, .stNumberInput input {
        background-color: var(--input-bg) !important;
        color: var(--primary-blue) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 10px !important;
        padding-left: 25px !important; /* Espacio para el símbolo $ */
        caret-color: var(--primary-blue) !important;
    }

    /* Símbolo de pesos para Number Input */
    div[data-testid="stNumberInput"] [data-baseweb="input"] {
        position: relative !important;
    }

    div[data-testid="stNumberInput"] [data-baseweb="input"]::before {
        content: "$" !important;
        position: absolute !important;
        left: 12px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        color: var(--primary-blue) !important;
        font-weight: 600 !important;
        z-index: 10 !important;
        font-size: 1rem !important;
    }

    /* Quitar el brillo naranja/rojo de Streamlit y poner azul Astor */
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: var(--primary-blue) !important;
        box-shadow: 0 0 0 1px var(--primary-blue) !important;
        outline: none !important;
    }

    /* Asegurar que los contenedores no tengan bordes extra */
    div[data-baseweb="input"], div[data-baseweb="input"] > div {
        border: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
    }

    /* Botones de + y - (Number Input) - ELIMINAR EL NEGRO */
    div[data-testid="stNumberInput"] button {
        background-color: var(--bg-card) !important;
        color: var(--primary-blue) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
    }

    div[data-testid="stNumberInput"] button:hover {
        background-color: #e5e7eb !important;
        border-color: var(--accent-blue) !important;
    }

    /* Selectbox y Multiselect - ESTILO DE BOTÓN FINO (Sin doble borde) */
    div[data-baseweb="select"], [data-testid="stMultiselect"] {
        background-color: var(--input-bg) !important;
        border: 1px solid var(--primary-blue) !important;
        border-radius: 6px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }

    /* ELIMINAR BORDES INTERNOS QUE CAUSAN EL EFECTO DOBLE */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="select"] div,
    [data-testid="stMultiselect"] > div,
    [data-testid="stMultiselect"] div {
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
    }

    div[data-baseweb="select"]:hover, [data-testid="stMultiselect"]:hover {
        border-color: #3B82F6 !important;
        background-color: #f8fafc !important;
    }

    /* Iconos (Flechas) */
    div[data-testid="stSelectbox"] svg, div[data-testid="stMultiselect"] svg {
        fill: #1e3a8a !important;
    }

    /* Etiquetas del Multiselect (Tags) - ESTILO LIMPIO */
    span[data-baseweb="tag"] {
        background-color: var(--bg-card) !important;
        color: var(--primary-blue) !important;
        border-radius: 6px !important;
        padding: 2px 8px !important;
        font-weight: 500 !important;
        border: none !important;
    }

    /* Menú desplegable del selector */
    ul[role="listbox"], li[role="option"] {
        background-color: var(--bg-card) !important;
        color: var(--primary-blue) !important;
        border-radius: 4px !important;
    }

    li[role="option"]:hover {
        background-color: #f3f4f6 !important;
    }

    /* 5. Tarjetas Personalizadas (Básicas) */
    .card-container {
        background-color: var(--bg-card);
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 25px;
        border: 2px solid var(--border-color) !important;
    }

    .card-title {
        color: var(--primary-blue);
        font-size: 1.1rem;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 15px;
        letter-spacing: 0.5px;
    }

    .card-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--value-color) !important;
        margin: 10px 0;
    }

    /* 6. Métricas de Streamlit */
    [data-testid="stMetric"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }

    /* 6.5 Botón de Tema (Sidebar) */
    [data-testid="stSidebar"] div.stButton > button {
        background-color: var(--input-bg) !important;
        color: var(--primary-blue) !important;
        border: 1.5px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        margin-bottom: 20px !important;
    }

    [data-testid="stSidebar"] div.stButton > button:hover {
        border-color: var(--accent-blue) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    }

    /* 8. EXPANDER ESTILO BLOQUE (Como la imagen) */

    /* 8. EXPANDER ESTILO BLOQUE (Como la imagen) */
    div[data-testid="stExpander"] {
        background-color: var(--expander-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }

    div[data-testid="stExpander"] summary {
        background-color: var(--expander-bg) !important;
        padding: 15px !important;
    }

    div[data-testid="stExpander"] summary span {
        color: #1e3a8a !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        text-transform: none !important;
    }

    div[data-testid="stExpander"] summary:hover {
        background-color: var(--bg-card) !important;
    }

    /* Forzar que los inputs dentro del expander se vean limpios */
    div[data-testid="stExpander"] .stTextInput, 
    div[data-testid="stExpander"] .stNumberInput, 
    div[data-testid="stExpander"] .stSelectbox {
        margin-bottom: 10px !important;
    }

    /* Ocultar elementos innecesarios */
    #MainMenu, footer {visibility: hidden;}

    /* Botón para abrir/cerrar el menú lateral (Sidebar Toggle) */
    [data-testid="stSidebarCollapsedControl"] {
        background-color: var(--primary-blue) !important;
        color: white !important;
        border-radius: 0 8px 8px 0 !important;
        padding: 5px !important;
        left: 0 !important;
        top: 10px !important;
    }

    [data-testid="stSidebarCollapsedControl"] svg {
        fill: white !important;
    }

    /* Forzar fondo blanco y texto oscuro en tablas */
    div[data-testid="stTable"] {
        background-color: var(--bg-card) !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }

    div[data-testid="stTable"] table {
        color: var(--primary-blue) !important;
    }

    div[data-testid="stTable"] th {
        background-color: var(--expander-bg) !important;
        color: var(--primary-blue) !important;
        font-weight: 700 !important;
    }

    /* 10. LÍNEAS DIVISORIAS ENTRE COLUMNAS (Estilo Premium Cromático) */
    .col-separator {
        border-left: 2px solid var(--sep-color, #e2e8f0);
        border-right: 2px solid var(--sep-color, #e2e8f0);
        width: 6px;
        height: 100%;
        margin: 0 auto;
        opacity: 0.8;
    }

    /* 11. CONTORNOS Y EFECTO GLASSMORPHISM */
    /* Animación de entrada */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    [data-testid="column"] [data-testid="stVerticalBlockBorderWrapper"] {
        animation: fadeInUp 0.8s ease-out forwards;
        backdrop-filter: blur(10px) !important;
        background: var(--bg-card) !important;
        opacity: 1 !important;
        border: 1.5px solid var(--border-color) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="column"] [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.15) !important;
        background: rgba(255, 255, 255, 0.8) !important;
    }

    /* Columna 1: Azul */
    [data-testid="column"]:nth-of-type(1) [data-testid="stVerticalBlockBorderWrapper"] {
        border-top: 5px solid #3B82F6 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
    }

    /* Columna 3 (Sugerencia): Verde */
    [data-testid="column"]:nth-of-type(3) [data-testid="stVerticalBlockBorderWrapper"] {
        border-top: 5px solid #34D399 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
    }

    /* Columna 5 (Comparativa): Púrpura */
    [data-testid="column"]:nth-of-type(5) [data-testid="stVerticalBlockBorderWrapper"] {
        border-top: 5px solid #8B5CF6 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
    }

    /* 12. ESTILO PARA POPOVER (Checklist) - PURGA TOTAL DE NEGRO */
    /* Botón de activación */
    div[data-testid="stPopover"] button {
        background-color: var(--bg-card) !important;
        color: var(--primary-blue) !important;
        border: 1px solid var(--primary-blue) !important;
        border-radius: 8px !important;
        width: 100% !important;
        text-align: left !important;
    }

    /* LIMPIEZA ATÓMICA: Todo dentro del popover DEBE ser blanco */
    [data-testid="stPopoverContent"],
    [data-testid="stPopoverContent"] div,
    [data-testid="stPopoverContent"] span,
    [data-testid="stPopoverContent"] label,
    [data-baseweb="popover"],
    [data-baseweb="popover"] div {
        background-color: var(--bg-card) !important;
        background: var(--bg-card) !important;
        border: none !important;
    }

    /* MARCO AZUL EN EL CUADRITO DEL CHECK (SOLICITADO) */
    div[data-testid="stCheckbox"] [data-baseweb="checkbox"] > div:first-child {
        border: 2px solid var(--primary-blue) !important;
        background-color: var(--bg-card) !important;
        border-radius: 4px !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* PALOMINA AZUL */
    div[data-testid="stCheckbox"] svg path {
        fill: var(--primary-blue) !important;
    }

    /* TEXTO AZUL LIMPIO SIN BORDES */
    div[data-testid="stCheckbox"] label p {
        color: var(--primary-blue) !important;
        font-weight: 500 !important;
        border: none !important;
        background: transparent !important;
    }

    /* BORDE DEL POPOVER EXTERIOR */
    div[data-testid="stPopoverContent"] {
        border: 2px solid var(--primary-blue) !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
    }

    /* Botón LISTO Premium */
    .ready-button-container button {
        background-color: var(--primary-blue) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 40px !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2) !important;
        transition: all 0.3s ease !important;
        width: auto !important;
    }

    .ready-button-container button:hover {
        background-color: var(--accent-blue) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(30, 58, 138, 0.3) !important;
    }

    /* Bordes y sombras del popover */
    div[data-testid="stPopoverContent"] {
        border: 2px solid var(--primary-blue) !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1) !important;
    }

    /* 13. ESTILO DE TARJETAS DE CRISTAL (Glassmorphism -> Solid In Dark) */
    .glass-card {
        background-color: var(--bg-card) !important;
        backdrop-filter: blur(8px) !important;
        border: 1.5px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 12px 15px !important;
        margin-bottom: 25px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
        height: 115px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        overflow: hidden !important;
    }

    .astor-card {
        /* El borde se define dinámicamente arriba */
    }

    .semaforo-green {
        border-left: 6px solid #34D399 !important;
    }

    .semaforo-yellow {
        border-left: 6px solid #FBBF24 !important;
    }

    .semaforo-red {
        border-left: 6px solid #F87171 !important;
    }

    .glass-card:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08) !important;
        background: rgba(255, 255, 255, 0.8) !important;
    }

    .glass-card strong {
        color: var(--primary-blue) !important;
        font-size: 1rem !important;
    }

    .glass-card .card-label {
        color: var(--accent-blue) !important;
        font-size: 0.85rem !important;
        opacity: 0.9;
    }

    .glass-card .card-value-small {
        color: var(--gold-text) !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }

    /* 14. ESTILO PARA TARJETAS DE ENTRADA UNIFICADAS (ASTOR) */
    /* Selector Q - Apunta SOLO al bloque vertical más profundo que contiene el marcador */
    [data-testid="stMain"] div[data-testid="stVerticalBlock"]:has(>.astor-input-marker) {
        background: var(--bg-card) !important;
        border-left: 6px solid var(--gold-text) !important; 
        border-radius: 12px !important;
        padding: 15px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        border: 1px solid var(--border-color) !important;
    }

    /* Regla de Oro: Limpiar TOTALMENTE cualquier contenedor que sea padre de una tarjeta Astor */
    /* EXCEPCIÓN: Si el contenedor es el principal de la columna (marcado con borde), se respeta su padding */
    div[data-testid="stVerticalBlock"]:has(div[data-testid="stVerticalBlock"]:has(.astor-input-marker)) {
        background: transparent !important;
        border: none !important;
        border-left: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }

    /* Forzar transparencia en Columnas y Bloques de Layout para evitar duplicidad */
    [data-testid="stHorizontalBlock"], [data-testid="stVerticalBlock"]:has(> div > div > .astor-input-marker) ~ div {
        background: transparent !important;
    }

    /* Ajuste específico para que el contenedor con borde de Streamlit luzca bien con las tarjetas internas */
    div[data-testid="stVerticalBlockBordered"]:has(.astor-input-marker) {
        padding: 20px !important;
        background: var(--bg-card) !important; /* Un toque sutil de fondo para profundidad */
    }

    /* Resetear el estilo por defecto de Streamlit para los inputs */
    [data-testid="stMain"] div[data-testid="stNumberInput"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin-bottom: 0 !important;
        box-shadow: none !important;
    }

    .astor-input-marker {
        display: none;
    }

    /* 15. RESUMEN DE PERFIL PERSONALIZADO (HEADER) - Estilo Integrado sin Caja */
    .client-summary-container {
        margin-bottom: 30px !important;
        padding-top: 10px !important;
    }

    .client-summary-title {
        font-size: 2.2rem !important;
        color: var(--primary-blue) !important;
        font-weight: 700 !important;
        margin-bottom: 12px !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        font-family: 'Cinzel', serif !important;
    }

    /* NUEVAS CLASES PARA EL TÍTULO PRINCIPAL */
    .astor-main-title {
        margin: 0 !important;
        color: var(--main-title-color) !important;
        font-size: 2.2rem !important;
        line-height: 1.1 !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 900 !important;
        text-align: center !important;
    }

    .astor-main-subtitle {
        margin: 0 !important;
        color: var(--primary-blue) !important;
        font-size: 0.95rem !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        opacity: 0.8 !important;
        text-transform: uppercase !important;
        text-align: center !important;
    }

    .client-summary-details {
        display: flex !important;
        gap: 30px !important;
        color: var(--accent-blue) !important;
        font-size: 1.2rem !important;
        align-items: center !important;
    }

    .summary-detail-item {
        display: flex !important;
        align-items: baseline !important;
        gap: 10px !important;
    }

    .summary-detail-label {
        font-size: 1rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        color: var(--accent-blue) !important;
        opacity: 0.85;
    }

    .summary-detail-value {
        color: var(--value-color) !important;
        font-weight: 800 !important;
        font-size: 1.4rem !important;
    }
    /* Ajuste fino del campo interno */
    [data-testid="stMain"] div[data-testid="stNumberInput"] input {
        background: transparent !important;
        border: none !important;
        font-size: 1.1rem !important;
        color: var(--primary-blue) !important;
        font-weight: 600 !important;
    }

    div[data-testid="stNumberInput"] [data-testid="stNumberInputStepDown"],
    div[data-testid="stNumberInput"] [data-testid="stNumberInputStepUp"] {
        background: transparent !important;
        border: none !important;
        color: var(--accent-blue) !important;
        border-radius: 4px !important;
    }

    div[data-testid="stNumberInput"] button svg {
        fill: var(--accent-blue) !important;
        color: var(--accent-blue) !important;
    }

    /* 15. EXCEPCIÓN: QUITAR SÍMBOLO DE PESOS EN CAMPOS DE CANTIDAD */
    /* Usamos :has para detectar el step="1" que identifica campos de conteo vs moneda */
    div[data-testid="stNumberInput"]:has(input[step="1"]) [data-baseweb="input"]::before {
        display: none !important;
    }

    /* Ajustar el padding para que el número no se vea movido a la derecha sin el símbolo */
    div[data-testid="stNumberInput"]:has(input[step="1"]) input {
        padding-left: 10px !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # --- SIDEBAR: DATOS PERSONALES ---
    with st.sidebar:

        with st.expander("👤 Datos del Cliente", expanded=True):
            nombre = st.text_input("Nombre completo", key="nombre_cliente")

            # Estructura: Título -> Monto -> Input
            st.markdown("Ingreso mensual (MXN)")
            st.markdown(f'<p style="color: var(--value-color); font-weight: bold; margin-bottom: -15px; margin-top: -15px; font-size: 0.9rem;">$ {st.session_state.get("sidebar_ingreso", 25000):,.0f}</p>', unsafe_allow_html=True)
            ingreso_mensual = st.number_input("Ingreso mensual (MXN)", min_value=0, step=1000, key="sidebar_ingreso", label_visibility="collapsed")

            estado_civil = "n/a"
            vive_con = "n/a"

        with st.expander("👨‍👩‍👧 Dependientes económicos", expanded=True):
            # Combo box de 0 a 6
            opciones_dep = [0, 1, 2, 3, 4, 5, 6]
            num_dependientes = st.selectbox("Dependientes económicos", opciones_dep, key="num_dependientes")

            if num_dependientes > 0:
                st.markdown(f'<p style="color: var(--accent-blue); font-size: 0.85rem; margin-bottom: 10px;">Has seleccionado {num_dependientes} D. económico(s).</p>', unsafe_allow_html=True)
                # Mostrar la cantidad del 5% del ingreso por cada dependiente
                monto_por_dependiente = st.session_state.get("sidebar_ingreso", 25000) * 0.05
                for i in range(1, num_dependientes + 1):
                    st.markdown(f"""
                    <div style="border: 1px solid var(--border-color); border-radius: 8px; padding: 10px 15px; margin-bottom: 8px; background-color: var(--bg-card); display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                        <div style="color: var(--primary-blue); font-weight: 700; font-size: 0.85rem;">👨‍👧 D. económico {i}</div>
                        <div style="color: var(--value-color); font-weight: 800; font-size: 0.95rem;">$ {monto_por_dependiente:,.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Actualizar el total para el cálculo
                st.session_state['sidebar_gastos_dep'] = monto_por_dependiente * num_dependientes
            else:
                st.session_state['sidebar_gastos_dep'] = 0
                gastos_dependientes = 0

            # Lógica derivada para el motor de cálculo
            tiene_dependientes = num_dependientes > 0

        with st.expander("💸 Selección de gastos mensuales", expanded=True):
            st.markdown("### 🏠 Necesidades y servicios")
            with st.popover("📋 Seleccionar básicos", use_container_width=True):
                st.write("Marca los gastos que tienes:")
                for op in nec_opciones:
                    st.checkbox(op, key=f"sidebar_chk_{op}")

            st.markdown("### 🌟 Estilo de vida")
            with st.popover("📋 Seleccionar estilo", use_container_width=True):
                st.write("Marca tus gastos adicionales:")
                for op in est_opciones:
                    st.checkbox(op, key=f"sidebar_chk_est_{op}")

            st.markdown("### 💳 Créditos")
            with st.popover("📋 Seleccionar créditos", use_container_width=True):
                st.write("Selecciona tus deudas actuales:")
                for op in cred_opciones:
                    st.checkbox(op, key=f"sidebar_chk_cred_{op}")

    # --- CÁLCULO DE POTENCIAL REAL (Pre-Header) ---
    # Usamos los montos que el usuario ya ingresó en el estado de sesión
    total_gastos_reales_detectados = 0
    for cat in necesidades_sel: total_gastos_reales_detectados += st.session_state.get(f"val_{cat}", 0)
    for cat in estilo_sel: total_gastos_reales_detectados += st.session_state.get(f"val_est_{cat}", 0)
    for cat in creditos_sel: total_gastos_reales_detectados += st.session_state.get(f"val_cred_{cat}", 0)

    ahorro_inversion_pre = 0
    if ingreso_mensual > 0:
        excedente_real = ingreso_mensual - total_gastos_reales_detectados
        # 7.5% directo del ingreso mensual
        ahorro_inversion_pre = ingreso_mensual * 0.075

    # --- TÍTULO PRINCIPAL (Estilo Astor) ---
    # Intentar cargar el logo (Dinámico según tema)
    logo_path = get_asset_path(logo_header_file)
    logo_html = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{data}" style="width: 150px;">'
    else:
        logo_html = '<div style="background-color: #1e3a8a; color: white; padding: 10px; border-radius: 8px; font-weight: bold; margin-right: 15px; font-size: 20px;">ASTOR</div>'

    metric_html = ""
    if ahorro_inversion_pre > 0:
        metric_html = f'<div class="astor-metric-box"><div style="color: var(--accent-blue); font-size: 0.85rem; font-weight: 700; letter-spacing: 0.8px; margin-bottom: 4px;">💰 Potencial de inversión</div><div style="color: var(--value-color); font-size: 2rem; font-weight: 800; margin: 0;">$ {ahorro_inversion_pre:,.0f}</div></div>'

    st.markdown(f"""
    <div style="margin-bottom: 25px; display: flex; flex-direction: column; align-items: center; width: 100%;">
        <div style="margin-bottom: 15px; display: flex; justify-content: center; width: 100%;">
            {logo_html}
        </div>
        <div style="text-align: center; width: 100%;">
            <div class="astor-main-title">ASTOR PLANIFICADOR FINANCIERO PERSONAL</div>
            <div class="astor-main-subtitle">Optimiza tus finanzas y descubre tu potencial de inversión.</div>
        </div>
    </div>

    <div style="display: flex; justify-content: space-between; align-items: stretch; flex-wrap: wrap; gap: 20px; width: 100%;">
    <div class="astor-metric-box" style="margin: 0;">
    <div style="color: var(--accent-blue); font-size: 0.85rem; font-weight: 700; letter-spacing: 0.8px; margin-bottom: 4px;">👤 Cliente e Ingreso</div>
    <div style="color: var(--primary-blue); font-size: 1.3rem; font-weight: 800; margin: 0; line-height: 1.2;">{nombre.upper()}</div>
    <div style="color: var(--value-color); font-size: 1.1rem; font-weight: 800; margin-top: 2px;">$ {ingreso_mensual:,.0f}</div>
    </div>
    <div style="display: flex; justify-content: flex-end; flex-grow: 1;">
    {metric_html}
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)


    # --- CONFIGURACIÓN INICIAL DE ESTADO ---
    # (Ya se inicializó arriba)

    def marcar_listo():
        st.session_state.listo = True

    # --- HEADER Y PERFIL ---
    # --- SECCIÓN DE GASTOS (NUEVO ENFOQUE: SELECCIÓN INTELIGENTE) ---
    st.write("Selecciona las categorías que forman parte de tu vida actual. ASTOR calculará la distribución ideal basada en tu perfil.")

    # --- CÁLCULO DE DISTRIBUCIÓN (Model Weights) ---
    pesos_sugeridos = {
        "🏠 Vivienda (Renta/hipoteca)": 0.20,
        "🍎 Despensa": 0.125,
        "🚗 Gasolina / Transporte": 0.10,
        "⚡ Servicios (luz, agua, gas, internet)": 0.075,
        "🧹 Personal de limpieza": 0.05,
        "🎓 Educación / colegiatura": 0.05,
        "🥂 Salidas y restaurante": 0.10,
        "📺 Suscripciones y digital": 0.05,
        "💅 Cuidado personal y ropa": 0.05,
        "🎨 Hobbies y proyectos": 0.05,
        "🏋️ Gimnasio/club": 0.05,
        "🐾 Mascotas (Comida y cuidados)": 0.03,
        "🚲 Uber Eats / Delivery": 0.02,
        "✈️ Viajes y Vacaciones": 0.05,
        "📂 Otros gastos": 0.03,
        "🚗 Crédito de auto": 0.10,
        "💳 Tarjeta de crédito (Meses sin intereses)": 0.05,
        "🏦 Otros créditos": 0.05
    }

    # --- NORMALIZACIÓN DE DISTRIBUCIÓN (LÍMITE MÁXIMO DEL INGRESO) ---
    # Asegura que si se eligen muchas opciones, la suma sugerida no rebase el ingreso mensual.
    # El límite seguro es 92.5% (0.925) del ingreso, para siempre dejar íntegro el 7.5% de Inversión.
    _categorias_activas = necesidades_sel + estilo_sel + creditos_sel
    _suma_pesos_activas = sum(pesos_sugeridos.get(cat, 0) for cat in _categorias_activas)

    if _suma_pesos_activas > 0.925:
        _factor_ajuste = 0.925 / _suma_pesos_activas
        for cat in pesos_sugeridos:
            pesos_sugeridos[cat] *= _factor_ajuste

    # --- FUNCIÓN PARA EXPORTAR A EXCEL PROFESIONAL ---
    def generar_excel_astor(nombre, ingreso, montos_reales, pesos_sugeridos, todos_seleccionados, fig_real, fig_astor, fig_det, is_dark_mode=False):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet('Reporte Financiero')

            # --- CONFIGURACIÓN DE COLORES POR TEMA ---
            if is_dark_mode:
                c_header_bg = '#092B30'  # Verde azulado oscuro
                c_info_bg = '#092B30'    # Verde azulado oscuro
                c_title_bg = '#092B30'   # Verde azulado oscuro
                c_font = '#FEFFFF'       # Blanco/Casi blanco
                c_border = '#E6C200'     # Dorado solicitado
                c_cell_bg = '#000000'    # Fondo negro total
                logo_filename = "1-07 copy.png"
            else:
                c_header_bg = '#F59E0B'  # Naranja
                c_info_bg = '#111827'    # Azul/Negro Info
                c_title_bg = '#111827'
                c_font = '#FFFFFF'
                c_border = '#D1D5DB'     # Gris claro para modo blanco
                c_cell_bg = '#FFFFFF'    # Fondo blanco
                logo_filename = "Fondos Logos-06.png"

            # --- ESTILOS ---
            # Aplicar marca de agua de fondo si existe
            watermark_path = get_watermark_excel(is_dark_mode)
            if watermark_path and os.path.exists(watermark_path):
                worksheet.set_background(watermark_path)

            # Ocultar cuadrículas en modo oscuro para el efecto de fondo infinito
            if is_dark_mode:
                worksheet.hide_gridlines(2)

            orange_header = workbook.add_format({
                'bold': True, 'font_color': c_font, 'bg_color': c_header_bg,
                'border': 1, 'border_color': c_border, 'align': 'center', 'valign': 'vcenter'
            })
            info_header = workbook.add_format({
                'bold': True, 'font_color': c_font, 'bg_color': c_info_bg,
                'border': 1, 'border_color': c_border, 'align': 'center'
            })
            title_box_format = workbook.add_format({
                'bold': True, 'font_size': 20, 'font_color': c_font, 
                'bg_color': c_title_bg, 'border': 1, 'border_color': c_border,
                'align': 'center', 'valign': 'vcenter'
            })
            category_format = workbook.add_format({
                'bold': True, 'font_color': c_font if is_dark_mode else '#000000',
                'border': 1, 'border_color': c_border
            })
            if not is_dark_mode:
                category_format.set_bg_color(c_cell_bg)

            money_format = workbook.add_format({
                'num_format': '$#,##0', 'border': 1, 'border_color': c_border,
                'font_color': c_font if is_dark_mode else '#000000'
            })
            if not is_dark_mode:
                money_format.set_bg_color(c_cell_bg)

            text_center = workbook.add_format({
                'border': 1, 'border_color': c_border, 'align': 'center',
                'font_color': c_font if is_dark_mode else '#000000'
            })
            if not is_dark_mode:
                text_center.set_bg_color(c_cell_bg)

            # --- CABECERA ESTILO ASTOR ---
            # Insertar Logo
            logo_path = get_asset_path(logo_filename)
            if os.path.exists(logo_path):
                worksheet.insert_image('A1', logo_path, {'x_scale': 0.04, 'y_scale': 0.04, 'x_offset': 10, 'y_offset': 10})

            # Cuadro de Título
            worksheet.merge_range('C2:F3', 'Astor simulador', title_box_format)

            # Información del cliente
            worksheet.merge_range('B5:G5', 'Información del cliente', info_header) # Ampliado a G
            worksheet.write('B6', 'Nombre del cliente', orange_header)
            worksheet.write('C6', 'Ingreso Mensual', orange_header)
            worksheet.write('D6', 'Potencial Inversión', orange_header)
            worksheet.merge_range('E6:G6', 'Estrategia Patrimonial Astor', orange_header)

            # Calcular potencial para el Excel (7.5% directo del ingreso)
            total_sugerido_base = sum(ingreso * pesos_sugeridos.get(cat, 0) for cat in todos_seleccionados)
            excedente_excel = ingreso - total_sugerido_base
            potencial_excel = ingreso * 0.075

            worksheet.write('B7', nombre, text_center)
            worksheet.write('C7', ingreso, money_format)
            worksheet.write('D7', potencial_excel, money_format)
            worksheet.merge_range('E7:G7', 'Sugerencia personalizada Astor', text_center)

            # --- TABLA DE ANÁLISIS ---
            worksheet.merge_range('B9:F9', 'Resumen de Análisis Financiero', info_header)
            worksheet.write('B10', 'CATEGORÍA / CONCEPTO', orange_header)
            worksheet.write('C10', 'GASTO ACTUAL', orange_header)
            worksheet.write('D10', 'RECOMENDADO ASTOR', orange_header)
            worksheet.write('E10', 'DIFERENCIA', orange_header)
            worksheet.write('F10', 'ESTATUS', orange_header)

            row = 10
            for cat in todos_seleccionados:
                real = montos_reales.get(cat, 0)
                sugerido = ingreso * pesos_sugeridos.get(cat, 0)
                diferencia = sugerido - real

                diff_color = '#10B981' if diferencia >= 0 else '#EF4444'
                estatus = "✅ ÓPTIMO" if diferencia >= 0 else "⚠️ AJUSTAR"

                diff_format = workbook.add_format({
                    'num_format': '$#,##0', 'border': 1, 'border_color': c_border, 
                    'font_color': diff_color, 'bold': True
                })
                estatus_format = workbook.add_format({
                    'border': 1, 'border_color': c_border, 'font_color': diff_color, 
                    'align': 'center', 'bold': True
                })
                if not is_dark_mode:
                    diff_format.set_bg_color(c_cell_bg)
                    estatus_format.set_bg_color(c_cell_bg)

                worksheet.write(row, 1, cat, category_format)
                worksheet.write(row, 2, real, money_format)
                worksheet.write(row, 3, sugerido, money_format)
                worksheet.write(row, 4, diferencia, diff_format)
                worksheet.write(row, 5, estatus, estatus_format)
                row += 1

            # --- INTEGRACIÓN DE GRÁFICAS (Debajo de la Tabla) ---
            chart_row = row + 2
            try:
                buf_real = io.BytesIO(fig_real.to_image(format="png", width=600, height=450))
                buf_astor = io.BytesIO(fig_astor.to_image(format="png", width=600, height=450))
                buf_det = io.BytesIO(fig_det.to_image(format="png", width=600, height=450))

                worksheet.merge_range(f'B{chart_row}:F{chart_row}', 'VISUALIZACIÓN DE ESTRATEGIA', orange_header)
                worksheet.insert_image(f'B{chart_row + 2}', 'real.png', {'image_data': buf_real, 'x_scale': 0.7, 'y_scale': 0.7})
                worksheet.insert_image(f'B{chart_row + 18}', 'astor.png', {'image_data': buf_astor, 'x_scale': 0.7, 'y_scale': 0.7})
                worksheet.insert_image(f'B{chart_row + 34}', 'detalle.png', {'image_data': buf_det, 'x_scale': 0.7, 'y_scale': 0.7})
            except Exception as e:
                worksheet.write(f'B{chart_row + 2}', f"Gráficas no disponibles: {str(e)}")

            # --- PROTECCIÓN Y DISEÑO DE PÁGINA ---
            worksheet.protect()
            worksheet.hide_gridlines(2)

            # Ajustar anchos
            worksheet.set_column('A:A', 20)
            worksheet.set_column('B:B', 30)
            worksheet.set_column('C:F', 20)

            # Ocultar celdas sobrantes (Columnas y Filas)
            # Ocultar todo después de la columna G (índice 6)
            worksheet.set_column('G:XFD', None, None, {'hidden': True})

            # Ocultar filas de forma manual para no afectar las imágenes
            # Ocultamos un rango grande después de las gráficas
            for r in range(chart_row + 60, 1000):
                worksheet.set_row(r, None, None, {'hidden': True})

        return output.getvalue()

    # --- DEFINICIÓN DE CONTENEDORES (NUEVA ESTRUCTURA POR FILAS) ---
    # 1. Cabecera de Columnas (SOLO TÍTULOS)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    c_header1, s_header1, c_header2, s_header2, c_header3 = st.columns([1, 0.1, 1, 0.1, 1])

    with c_header1:
        st.markdown("<h4 style='text-align: center; color: var(--primary-blue); margin-bottom: 0; white-space: nowrap;'>📝 Registro de Gastos</h4>", unsafe_allow_html=True)

    with s_header1:
        # Separador Header 1 (Debe coincidir en estilo)
        st.markdown('<div class="col-separator" style="height: 100%; min-height: 60px; --sep-color: #3B82F6;"></div>', unsafe_allow_html=True)

    with c_header2:
        st.markdown("<h4 style='text-align: center; color: var(--primary-blue); margin-bottom: 0; white-space: nowrap;'>📈 Distribución Sugerida Astor</h4>", unsafe_allow_html=True)

    with s_header2:
        # Separador Header 2
        st.markdown('<div class="col-separator" style="height: 100%; min-height: 60px; --sep-color: #10B981;"></div>', unsafe_allow_html=True)

    with c_header3:
        st.markdown("<h4 style='text-align: center; color: var(--primary-blue); margin-bottom: 0; white-space: nowrap;'>📊 Comparativa Real</h4>", unsafe_allow_html=True)

    # Variables de recolección GLOBAL
    montos_reales = {}

    def render_section_row(titulo, categorias, key_prefix):
        if not categorias: return

        # Título de Sección que "Corta" las líneas (Estilo Pill Flotante)
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; margin: 30px 0 20px 0;">
            <div style="flex-grow: 1; height: 2px; background: linear-gradient(90deg, rgba(229,231,235,0) 0%, rgba(229,231,235,1) 20%, rgba(229,231,235,1) 80%, rgba(229,231,235,0) 100%);"></div>
            <div style="
                font-size: 1.3rem; 
                font-weight: 700; 
                color: var(--primary-blue); 
                padding: 0 20px; 
                margin: 0 20px;
                white-space: nowrap;
                z-index: 10;
            ">
                {titulo}
            </div>
            <div style="flex-grow: 1; height: 2px; background: linear-gradient(90deg, rgba(229,231,235,0) 0%, rgba(229,231,235,1) 20%, rgba(229,231,235,1) 80%, rgba(229,231,235,0) 100%);"></div>
        </div>
        """, unsafe_allow_html=True)

        c1, s1, c2, s2, c3 = st.columns([1, 0.1, 1, 0.1, 1])

        # 1. INPUTS
        with c1:
            if titulo == "🏠 Necesidades y Servicios":
                 st.markdown("<h4 style='text-align: center; color: var(--primary-blue); margin-bottom: 15px;'>Distribución Real</h4>", unsafe_allow_html=True)

            with st.container(border=True):
                for cat in categorias:
                    # Key generation logic handled here
                    effective_key = f"{key_prefix}{cat}" if key_prefix == "val_" else f"{key_prefix}{cat}"

                    with st.container():
                        st.markdown('<div class="astor-input-marker"></div>', unsafe_allow_html=True)
                        st.markdown(f'<div style="font-weight: 700; color: var(--primary-blue); margin-bottom: 2px;">{cat}</div>', unsafe_allow_html=True)
                        val_actual = st.session_state.get(effective_key, 0)
                        st.markdown(f'<div style="color: var(--value-color); font-weight: 800; font-size: 1.1rem; margin-bottom: 5px;">$ {val_actual:,.0f}</div>', unsafe_allow_html=True)
                        montos_reales[cat] = st.number_input(f"{cat}", min_value=0, step=500, key=effective_key, label_visibility="collapsed")

        # Separators
        min_height = 100 + (len(categorias) * 160)
        with s1:
            # Full height separator logic
            st.markdown(f'<div class="col-separator" style="height: 100%; min-height: {min_height}px; --sep-color: #3B82F6;"></div>', unsafe_allow_html=True)

        with s2:
            st.markdown(f'<div class="col-separator" style="height: 100%; min-height: {min_height}px; --sep-color: #10B981;"></div>', unsafe_allow_html=True)

        # 2. SUGERENCIAS
        with c2:
            if titulo == "🏠 Necesidades y Servicios" and st.session_state.listo:
                 st.markdown("<h4 style='text-align: center; color: #1e3a8a; margin-bottom: 15px; white-space: nowrap;'>Distribución Sugerida Astor</h4>", unsafe_allow_html=True)

            with st.container(border=True):
                if st.session_state.listo and ingreso_mensual > 0:
                    for cat in categorias:
                        monto = ingreso_mensual * pesos_sugeridos.get(cat, 0)
                        st.markdown(f"""
                            <div class="glass-card astor-card">
                                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                    <div style="flex-grow: 1; max-width: 70%; overflow: hidden; text-overflow: ellipsis;">
                                        <strong style="font-size: 0.92rem; line-height: 1.2; display: block;">{cat}</strong>
                                    </div>
                                    <div style="width: 28%; text-align: right;">
                                        <span class="card-label" style="font-size: 0.75rem;">Ideal: {pesos_sugeridos.get(cat, 0)*100:.1f}%</span>
                                    </div>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: 5px;">
                                    <span class="card-label">Sugerido:</span>
                                    <span class="card-value-small" style="font-weight: 800; color: var(--value-color);">${monto:,.0f}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                elif not st.session_state.listo:
                    st.info("💡 Esperando cálculo...")
                else:
                     st.warning("⚠️ Ingresa sueldo.")

        # 3. COMPARATIVA
        with c3:
            if titulo == "🏠 Necesidades y Servicios" and st.session_state.listo:
                 st.markdown("<h4 style='text-align: center; color: var(--primary-blue); margin-bottom: 15px;'>Análisis Semáforo Astor</h4>", unsafe_allow_html=True)

            with st.container(border=True):
                if st.session_state.listo and ingreso_mensual > 0:
                    for cat in categorias:
                        recomendado = ingreso_mensual * pesos_sugeridos.get(cat, 0)
                        real = montos_reales.get(cat, 0)
                        # Lógica de semáforo de 3 colores
                        if st.session_state.get('dark_mode', False):
                            # MODO OSCURO: Estilo Luminoso/Neón
                            if real <= recomendado:
                                color = "#00FF9D" # Verde Neón
                                icono = "✅"
                                glow_style = f"box-shadow: 0 0 15px {color}44, inset 0 0 10px {color}22; border-color: {color}88;"
                                tool_tip = f"Excelente control en {cat}. ¡Sigue así!"
                                semaforo_class = "semaforo-green"
                            elif real <= recomendado * 1.20:
                                color = "#FFDD00" # Amarillo Neón/Oro
                                icono = "⚠️"
                                glow_style = f"box-shadow: 0 0 15px {color}44, inset 0 0 10px {color}22; border-color: {color}88;"
                                tool_tip = f"Cuidado, estás cerca del límite sugerido para {cat}."
                                semaforo_class = "semaforo-yellow"
                            else:
                                color = "#FF3131" # Rojo Neón
                                icono = "🚨"
                                glow_style = f"box-shadow: 0 0 15px {color}44, inset 0 0 10px {color}22; border-color: {color}88;"
                                tool_tip = f"⚠️ Estás gastando demasiado en {cat}. Considera reducir este gasto."
                                semaforo_class = "semaforo-red"
                            text_shadow = f"text-shadow: 0 0 5px {color}44;"
                            val_glow = f"text-shadow: 0 0 8px {color}66;"
                        else:
                            # MODO CLARO: Estilo Original/Limpio
                            if real <= recomendado:
                                color = "#10B981" # Verde Estándar
                                icono = "✅"
                                tool_tip = f"Excelente control en {cat}. ¡Sigue así!"
                                semaforo_class = "semaforo-green"
                            elif real <= recomendado * 1.20:
                                color = "#F59E0B" # Ámbar/Naranja
                                icono = "⚠️"
                                tool_tip = f"Cuidado, estás cerca del límite sugerido para {cat}."
                                semaforo_class = "semaforo-yellow"
                            else:
                                color = "#EF4444" # Rojo Estándar
                                icono = "🚨"
                                tool_tip = f"⚠️ Estás gastando demasiado en {cat}. Considera reducir este gasto."
                                semaforo_class = "semaforo-red"
                            glow_style = ""
                            text_shadow = ""
                            val_glow = ""

                        st.markdown(f"""
                            <div class="glass-card {semaforo_class}" title="{tool_tip}" style="{glow_style} padding: 12px; border-radius: 12px; border: 1px solid var(--border-color); background: var(--bg-card); margin-bottom: 10px; cursor: help;">
                                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                    <div style="flex-grow: 1; max-width: 80%; overflow: hidden; text-overflow: ellipsis;">
                                        <strong style="font-size: 0.92rem; line-height: 1.2; display: block; {text_shadow}">{cat}</strong>
                                    </div>
                                    <div style="width: 15%; text-align: right;">
                                        <span style="font-size: 1.1rem; line-height: 1;">{icono}</span>
                                    </div>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: 5px;">
                                    <span class="card-label">Rec: <b style="color: var(--primary-blue);">${recomendado:,.0f}</b></span>
                                    <span style="color: {color}; font-weight: bold; font-size: 0.95rem; {val_glow}">Real: ${real:,.0f}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                elif not st.session_state.listo:
                    st.info("💡 Esperando cálculo...")

    # Ejecución por Secciones
    render_section_row("🏠 Necesidades y Servicios", necesidades_sel, "val_")
    render_section_row("🌟 Estilo de Vida", estilo_sel, "val_est_")
    render_section_row("💳 Créditos y Deudas", creditos_sel, "val_cred_")

    # Definición de categorías seleccionadas para cálculos globales
    todos_seleccionados = necesidades_sel + estilo_sel + creditos_sel

    # --- SECCIÓN DE TOTALES ---
    if st.session_state.listo and ingreso_mensual > 0:
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; margin: 50px 0 30px 0;">
            <div style="flex-grow: 1; height: 3px; background: linear-gradient(90deg, rgba(30,58,138,0) 0%, rgba(30,58,138,1) 50%, rgba(30,58,138,0) 100%);"></div>
            <div style="
                font-size: 2.2rem; 
                font-weight: 800; 
                color: var(--primary-blue); 
                padding: 0 30px; 
                text-transform: uppercase;
                letter-spacing: 2px;
            ">
                💰 Totales Generales
            </div>
            <div style="flex-grow: 1; height: 3px; background: linear-gradient(90deg, rgba(30,58,138,0) 0%, rgba(30,58,138,1) 50%, rgba(30,58,138,0) 100%);"></div>
        </div>
        """, unsafe_allow_html=True)

        c_tot1, s_tot1, c_tot2, s_tot2, c_tot3 = st.columns([1, 0.05, 1, 0.1, 1])

        total_real = sum(montos_reales.get(cat, 0) for cat in todos_seleccionados)
        total_sugerido = sum(ingreso_mensual * pesos_sugeridos.get(cat, 0) for cat in todos_seleccionados)

        with c_tot1:
            st.markdown("<h4 style='text-align: center; color: var(--primary-blue);'>Total Real</h4>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class="card-container" style="border-color: #3B82F6; padding: 20px; height: 160px; display: flex; flex-direction: column; justify-content: center;">
                    <div class="card-title">Suma de Gastos Actuales</div>
                    <div class="card-value" style="color: var(--accent-blue); margin-top: 10px;">$ {total_real:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)

        with s_tot1:
            st.markdown('<div class="col-separator" style="height: 100%; min-height: 180px; --sep-color: #3B82F6;"></div>', unsafe_allow_html=True)

        with c_tot2:
            st.markdown("<h4 style='text-align: center; color: var(--primary-blue);'>Total Sugerido</h4>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class="card-container" style="border-color: #10B981; padding: 20px; height: 160px; display: flex; flex-direction: column; justify-content: center;">
                    <div class="card-title">Sugerencia Ideal Astor</div>
                    <div class="card-value" style="color: #10B981; margin-top: 10px;">$ {total_sugerido:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)

        with s_tot2:
            st.markdown('<div class="col-separator" style="height: 100%; min-height: 180px; --sep-color: #10B981;"></div>', unsafe_allow_html=True)

        with c_tot3:
            # Comparativa Final de Totales
            st.markdown("<h4 style='text-align: center; color: var(--primary-blue); white-space: nowrap;'>Resumen</h4>", unsafe_allow_html=True)

            diff = ingreso_mensual - total_real
            # Nueva lógica de semáforo basada en el ingreso mensual
            pct_uso = (total_real / ingreso_mensual) if ingreso_mensual > 0 else 0

            if st.session_state.get('dark_mode', False):
                # MODO OSCURO: Estilo Luminoso
                if pct_uso <= 0.85:
                    color_res = "#00FF9D"; status_text = "SALUD FINANCIERA ÓPTIMA"; icon_res = "✅"
                    bg_res = "rgba(0, 255, 157, 0.08)"
                    glow_res = "box-shadow: 0 0 25px rgba(0, 255, 157, 0.3), inset 0 0 15px rgba(0, 255, 157, 0.1);"
                elif pct_uso <= 1.00:
                    color_res = "#FFDD00"; status_text = "CUIDADO: CERCA DEL LÍMITE"; icon_res = "⚠️"
                    bg_res = "rgba(255, 221, 0, 0.08)"
                    glow_res = "box-shadow: 0 0 25px rgba(255, 221, 0, 0.3), inset 0 0 15px rgba(255, 221, 0, 0.1);"
                else:
                    color_res = "#FF3131"; status_text = "EXCESO CRÍTICO: SOBREGIRADO"; icon_res = "🚨"
                    bg_res = "rgba(255, 49, 49, 0.08)"
                    glow_res = "box-shadow: 0 0 25px rgba(255, 49, 49, 0.3), inset 0 0 15px rgba(255, 49, 49, 0.1);"
                text_glow = f"text-shadow: 0 0 10px {color_res}66;"
                val_glow_res = f"text-shadow: 0 0 12px {color_res}88;"
                border_res = f"border-color: {color_res};"
            else:
                # MODO CLARO: Estilo Original
                if pct_uso <= 0.85:
                    color_res = "#10B981"; status_text = "SALUD FINANCIERA ÓPTIMA"; icon_res = "✅"
                    bg_res = "rgba(16, 185, 129, 0.1)"
                elif pct_uso <= 1.00:
                    color_res = "#F59E0B"; status_text = "CUIDADO: CERCA DEL LÍMITE"; icon_res = "⚠️"
                    bg_res = "rgba(245, 158, 11, 0.1)"
                else:
                    color_res = "#ef4444"; status_text = "EXCESO CRÍTICO: SOBREGIRADO"; icon_res = "🚨"
                    bg_res = "rgba(239, 68, 68, 0.1)"
                glow_res = ""; text_glow = ""; val_glow_res = ""
                border_res = "border-color: #8B5CF6;"

            st.markdown(f"""
                <div class="card-container" style="{border_res} background-color: {bg_res}; {glow_res} padding: 20px; height: 160px; display: flex; flex-direction: column; justify-content: center;">
                    <div class="card-title" style="color: {color_res}; font-weight: 800; {text_glow}">{icon_res} {status_text}</div>
                    <div style="font-size: 0.9rem; margin-top: 10px; color: var(--primary-blue);">
                        Diferencia mensual:<br>
                        <b style="font-size: 1.4rem; color: {color_res}; {val_glow_res}">${diff:,.0f}</b>
                    </div>
                </div>
            """, unsafe_allow_html=True)


    # Configurar el botón de listo al final del bloque de inputs si es necesario
    # Pero ahora estamos fuera del flujo normal...
    # Simplemente ponemos el botón en un contenedor centrado abajo de todo si no está listo
    if not st.session_state.listo:
        st.markdown("---")
        total_seleccionados = len(necesidades_sel) + len(estilo_sel) + len(creditos_sel)
        boton_habilitado = total_seleccionados >= 5

        col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
        with col_b2:
            if not boton_habilitado:
                st.markdown(f'<p style="color: #f87171; font-size: 0.8rem; text-align: center;">⚠️ Selecciona al menos 5 categorías ({total_seleccionados}/5)</p>', unsafe_allow_html=True)
            if st.button("✅ GENERAR ANÁLISIS ASTOR", on_click=marcar_listo, disabled=not boton_habilitado, use_container_width=True):
                pass

    # Recalcular todos_seleccionados para uso en gráficas
    # Análisis Avanzado Astor
    if st.session_state.listo and ingreso_mensual > 0:
        st.markdown("---")
        st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 30px; flex-wrap: wrap; gap: 20px; width: 100%;">
        <h2 style='margin: 0; color: var(--primary-blue); font-size: 2.5rem;'>◕ Análisis Avanzado Astor</h2>
        <div style="display: flex; justify-content: flex-end; flex-grow: 1;">
            {metric_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

        # Inicialización para evitar NameError
        fig_real, fig_astor, fig_det = None, None, None

        c_col1, c_sep1, c_col2, c_sep2, c_col3 = st.columns([1, 0.1, 1, 0.1, 1])

        with c_col1:
            with st.container(border=True):
                # Título removido a solicitud del usuario

                # Recopilar datos reales
                datos_reales = []
                for cat, monto in montos_reales.items():
                    if monto > 0:
                        datos_reales.append({"Categoría": cat, "Monto": monto})

                if datos_reales:
                    df_real = pd.DataFrame(datos_reales)
                    df_real['pct_ingreso'] = (df_real['Monto'] / ingreso_mensual) * 100

                    # Mostrar la Real ocupando todo el ancho de la columna c_col1 para igualar tamaño
                    st.markdown("<h4 style='text-align: center; color: var(--primary-blue); margin-bottom: 15px; white-space: nowrap;'>Distribución Real Actual</h4>", unsafe_allow_html=True)
                    df_real_nec = df_real[df_real['Categoría'].isin(todos_seleccionados)]
                    if not df_real_nec.empty:
                        fig_real = px.pie(df_real_nec, values='Monto', names='Categoría', 
                                         hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel,
                                         custom_data=['pct_ingreso'])
                        fig_real.update_traces(
                            textposition='inside',
                            textinfo='percent',
                            texttemplate='<b>%{label}</b><br>%{customdata[0]:.1f}%',
                            insidetextorientation='horizontal',
                            hovertemplate='<b>%{label}</b><br>Monto: $%{value:,.0f}<br>% del sueldo: %{customdata[0]:.1f}%<extra></extra>'
                        )
                        fig_real.update_layout(
                            showlegend=False, 
                            margin=dict(t=0, b=0, l=0, r=0), height=400,
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font=dict(color="#FEFFFF" if st.session_state['dark_mode'] else "#1e3a8a")
                        )
                        st.plotly_chart(fig_real, use_container_width=True)

                        # --- Leyenda personalizada tipo Tabla 2 COLUMNAS (SIMETRÍA) ---
                        colors = px.colors.qualitative.Pastel
                        legend_html = '<div style="margin-top: 10px; padding: 15px; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color); opacity: 0.9;">'
                        legend_html += '<table style="width: 100%; border-collapse: collapse; table-layout: fixed;">'
                        # Header para simetría
                        legend_html += f'''
                        <tr style="border-bottom: 2px solid rgba(30,58,138,0.15);">
                            <th style="text-align: left; padding: 8px 0; width: 75%; color: var(--primary-blue); font-size: 0.85rem; font-weight: 800;">CATEGORÍA</th>
                            <th style="text-align: right; padding: 8px 0; width: 25%; color: var(--accent-blue); font-size: 0.85rem; font-weight: 800;">REAL</th>
                        </tr>
                        '''
                        for i, row in df_real_nec.iterrows():
                            color = colors[i % len(colors)]
                            legend_html += f'''
    <tr style="border-bottom: 1px solid rgba(0,0,0,0.05);">
        <td style="padding: 8px 0; width: 75%; vertical-align: middle;">
            <div style="display: flex; align-items: center;">
                <div style="min-width: 10px; width: 10px; height: 10px; background-color: {color}; border-radius: 50%; margin-right: 10px; flex-shrink: 0;"></div>
                <div style="color: var(--primary-blue); font-weight: 600; font-size: 0.8rem; line-height: 1.2;">{row['Categoría']}</div>
            </div>
        </td>
        <td style="padding: 8px 0; width: 25%; text-align: right; vertical-align: middle; color: var(--primary-blue); font-weight: 700; font-size: 0.9rem; white-space: nowrap;">
            $ {row['Monto']:,.0f}
        </td>
    </tr>
    '''
                        legend_html += '</table></div>'
                        st.markdown(legend_html, unsafe_allow_html=True)
                    else:
                        st.caption("Sin datos de necesidades.")
                else:
                    st.info("Ingresa montos para ver la comparativa.")

        with c_col2:
            with st.container(border=True):
                st.markdown("<h4 style='text-align: center; color: var(--primary-blue); margin-bottom: 15px; white-space: nowrap;'>Distribución Sugerida Astor</h4>", unsafe_allow_html=True)
                datos_astor = []
                for cat in todos_seleccionados:
                    monto_sug = ingreso_mensual * pesos_sugeridos.get(cat, 0)
                    if monto_sug > 0:
                        datos_astor.append({"Categoría": cat, "Monto": monto_sug})

                if datos_astor:
                    df_astor = pd.DataFrame(datos_astor)
                    # Sincronización Astor: Calculamos el % ideal sobre el sueldo total para que coincida con las tarjetas
                    df_astor['pct_ingreso'] = (df_astor['Monto'] / ingreso_mensual) * 100

                    fig_astor = px.pie(df_astor, values='Monto', names='Categoría', 
                                      hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel,
                                      custom_data=['pct_ingreso'])

                    fig_astor.update_traces(
                        textposition='inside',
                        textinfo='label+percent',
                        texttemplate='<b>%{label}</b><br>%{customdata[0]:.1f}%',
                        insidetextorientation='horizontal',
                        hovertemplate='<b>%{label}</b><br>Monto sugerido: $%{value:,.0f}<br>% del sueldo: %{customdata[0]:.1f}%<extra></extra>'
                    )
                    fig_astor.update_layout(
                        showlegend=False, 
                        margin=dict(t=0, b=0, l=0, r=0), height=400,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#FEFFFF" if st.session_state['dark_mode'] else "#1e3a8a")
                    )
                    st.plotly_chart(fig_astor, use_container_width=True)

                    # --- Leyenda personalizada tipo Tabla 2 COLUMNAS (SIMETRÍA) ---
                    colors = px.colors.qualitative.Pastel
                    legend_html = '<div style="margin-top: 10px; padding: 15px; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color); opacity: 0.9;">'
                    legend_html += '<table style="width: 100%; border-collapse: collapse; table-layout: fixed;">'
                    # Header para simetría
                    legend_html += f'''
                    <tr style="border-bottom: 2px solid rgba(30,58,138,0.15);">
                        <th style="text-align: left; padding: 8px 0; width: 75%; color: var(--primary-blue); font-size: 0.85rem; font-weight: 800;">CATEGORÍA</th>
                        <th style="text-align: right; padding: 8px 0; width: 25%; color: #10B981; font-size: 0.85rem; font-weight: 800;">IDEAL</th>
                    </tr>
                    '''
                    for i, row in df_astor.iterrows():
                        color = colors[i % len(colors)]
                        legend_html += f'''
    <tr style="border-bottom: 1px solid rgba(0,0,0,0.05);">
        <td style="padding: 8px 0; width: 75%; vertical-align: middle;">
            <div style="display: flex; align-items: center;">
                <div style="min-width: 10px; width: 10px; height: 10px; background-color: {color}; border-radius: 50%; margin-right: 10px; flex-shrink: 0;"></div>
                <div style="color: var(--primary-blue); font-weight: 600; font-size: 0.8rem; line-height: 1.2;">{row['Categoría']}</div>
            </div>
        </td>
        <td style="padding: 8px 0; width: 25%; text-align: right; vertical-align: middle; color: var(--primary-blue); font-weight: 700; font-size: 0.9rem; white-space: nowrap;">
            $ {row['Monto']:,.0f}
        </td>
    </tr>
    '''
                    legend_html += '</table></div>'
                    st.markdown(legend_html, unsafe_allow_html=True)

        with c_col3:
            with st.container(border=True):
                st.markdown("<h4 style='text-align: center; color: var(--primary-blue); margin-bottom: 15px; white-space: nowrap;'>Balance Detallado</h4>", unsafe_allow_html=True)
                datos_detallados = []
                total_real_det = sum(montos_reales.get(cat, 0) for cat in todos_seleccionados)
                total_sugerido_det = sum(ingreso_mensual * pesos_sugeridos.get(cat, 0) for cat in todos_seleccionados)

                # 1. Categorías de Gasto
                for cat in todos_seleccionados:
                    real = montos_reales.get(cat, 0)
                    sugerido = ingreso_mensual * pesos_sugeridos.get(cat, 0)

                    # Definir color de semáforo para la gráfica
                    if real <= sugerido:
                        color_det = "#10B981" # Verde
                    elif real <= sugerido * 1.20:
                        color_det = "#F59E0B" # Amarillo
                    else:
                        color_det = "#EF4444" # Rojo

                    if real > 0 or sugerido > 0:
                        datos_detallados.append({
                            "Sección": cat, 
                            "Monto": real, 
                            "Monto_Real": real,
                            "Monto_Sugerido": sugerido,
                            "Categoría": cat,
                            "Color": color_det
                        })

                # 2. Agregar el remanente (Saldo Disponible)
                disponible_real = ingreso_mensual - total_real_det
                disponible_sug = ingreso_mensual - total_sugerido_det

                if disponible_real != 0 or disponible_sug != 0:
                    color_disponible = "#10B981" if disponible_real >= 0 else "#EF4444"
                    datos_detallados.append({
                        "Sección": "Saldo Disponible", 
                        "Monto": max(0, disponible_real),
                        "Monto_Real": disponible_real,
                        "Monto_Sugerido": disponible_sug,
                        "Categoría": "💰 Disponible",
                        "Color": color_disponible
                    })

                if datos_detallados:
                    df_det = pd.DataFrame(datos_detallados)
                    # % relativo al ingreso total (basado en real para el gráfico)
                    df_det['pct_ingreso'] = (df_det['Monto_Real'] / ingreso_mensual) * 100

                    fig_det = px.pie(df_det, values='Monto', names='Sección', 
                                     hole=0.4, color='Sección',
                                     color_discrete_map={row['Sección']: row['Color'] for _, row in df_det.iterrows()},
                                     custom_data=['pct_ingreso', 'Categoría'])

                    fig_det.update_traces(
                        textposition='inside',
                        textinfo='percent',
                        texttemplate='<b>%{customdata[1]}</b><br>%{customdata[0]:.1f}%',
                        insidetextorientation='horizontal',
                        hovertemplate='<b>%{customdata[1]}</b><br>Monto Real: $%{value:,.0f}<br>% del sueldo: %{customdata[0]:.1f}%<extra></extra>'
                    )
                    fig_det.update_layout(
                        showlegend=False, 
                        margin=dict(t=0, b=0, l=0, r=0), height=400,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#FEFFFF" if st.session_state['dark_mode'] else "#1e3a8a")
                    )
                    st.plotly_chart(fig_det, use_container_width=True)

                    # --- Leyenda personalizada tipo Tabla 3 COLUMNAS ---
                    legend_html = '<div style="margin-top: 10px; padding: 15px; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color); opacity: 0.9;">'
                    legend_html += '<table style="width: 100%; border-collapse: collapse; table-layout: fixed;">'
                    # Header
                    legend_html += f'''
                    <tr style="border-bottom: 2px solid rgba(30,58,138,0.15);">
                        <th style="text-align: left; padding: 8px 0; width: 50%; color: var(--primary-blue); font-size: 0.85rem; font-weight: 800;">CATEGORÍA</th>
                        <th style="text-align: right; padding: 8px 0; width: 25%; color: var(--accent-blue); font-size: 0.85rem; font-weight: 800;">REAL</th>
                        <th style="text-align: right; padding: 8px 0; width: 25%; color: #10B981; font-size: 0.85rem; font-weight: 800;">IDEAL</th>
                    </tr>
                    '''
                    for i, row in df_det.iterrows():
                        color = row['Color']
                        legend_html += f'''
    <tr style="border-bottom: 1px solid rgba(0,0,0,0.05);">
        <td style="padding: 8px 0; width: 50%; vertical-align: middle;">
            <div style="display: flex; align-items: center;">
                <div style="min-width: 10px; width: 10px; height: 10px; background-color: {color}; border-radius: 50%; margin-right: 10px; flex-shrink: 0;"></div>
                <div style="color: var(--primary-blue); font-weight: 600; font-size: 0.8rem; line-height: 1.2;">{row['Categoría']}</div>
            </div>
        </td>
        <td style="padding: 8px 0; width: 25%; text-align: right; vertical-align: middle; color: var(--primary-blue); font-weight: 700; font-size: 0.9rem; white-space: nowrap;">
            $ {max(0, row['Monto_Real']):,.0f}
        </td>
        <td style="padding: 8px 0; width: 25%; text-align: right; vertical-align: middle; color: var(--primary-blue); font-weight: 700; font-size: 0.9rem; white-space: nowrap;">
            $ {max(0, row['Monto_Sugerido']):,.0f}
        </td>
    </tr>
    '''
                    legend_html += '</table></div>'
                    st.markdown(legend_html, unsafe_allow_html=True)

                    # Generar datos de Excel para el botón que se muestra al final de la app
                    excel_data = generar_excel_astor(nombre, ingreso_mensual, montos_reales, pesos_sugeridos, todos_seleccionados, fig_real, fig_astor, fig_det, st.session_state['dark_mode'])

        with c_sep1:
            st.markdown('<div class="col-separator" style="min-height: 1000px; height: 100%; --sep-color: #3B82F6;"></div>', unsafe_allow_html=True)
        with c_sep2:
            st.markdown('<div class="col-separator" style="min-height: 1000px; height: 100%; --sep-color: #10B981;"></div>', unsafe_allow_html=True)




    if st.session_state.listo and ingreso_mensual > 0 and 'excel_data' in locals():
        st.markdown("---")
        col_btn_1, col_btn_2, col_btn_3 = st.columns([1, 1.2, 1])
        with col_btn_2:
            st.download_button(
                label="💾 Descargar Reporte (Excel)",
                data=excel_data,
                file_name=f"Reporte_Astor_{nombre.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            st.caption("<center>✨ Incluye gráficas y análisis detallado.</center>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 50px; padding-bottom: 20px;">
            ASTOR Financial Planner - Configura tus ingresos y gastos para comenzar.
        </div>
        """, unsafe_allow_html=True)

    # --- FIN DE CONFIGURACIÓN ---
