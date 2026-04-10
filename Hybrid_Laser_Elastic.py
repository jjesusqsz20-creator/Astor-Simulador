import streamlit as st
import os
import base64
import sys

# --- CONFIGURACIÓN DE COLORES OFICIALES ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

is_dark = st.session_state.theme == 'dark'

if is_dark:
    BG_COLOR = "#080A0F"
    SIDEBAR_BG = "#050505"
    TEXT_COLOR = "#FEFFFF"
    ACCENT_COLOR = "#6BA4A4" 
    GOLD_COLOR = "#DFBF72"
    CARD_BG = "#1A1D23"
else:
    BG_COLOR = "#F0F2F5"
    SIDEBAR_BG = "#FFFFFF"
    TEXT_COLOR = "#1E3A8A"
    ACCENT_COLOR = "#3B82F6"
    GOLD_COLOR = "#1E3A8A"
    CARD_BG = "#FFFFFF"

# --- RESOLUCIÓN DE RUTAS ---
def get_asset_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

st.set_page_config(page_title="Astor | Laser-Elastic Hybrid", layout="wide")

# --- CSS: LASER-ELASTIC HYBRID ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Montserrat:wght@300;600&display=swap');

    .stApp {{
        background-color: {BG_COLOR} !important;
        background-image: 
            radial-gradient(circle at 10% 20%, {ACCENT_COLOR}11 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, {GOLD_COLOR}11 0%, transparent 40%) !important;
    }}
    
    header[data-testid="stHeader"] {{ background: transparent !important; }}
    [data-testid="stSidebar"] {{ background: {SIDEBAR_BG} !important; }}

    .main-title {{
        color: {TEXT_COLOR};
        font-family: 'Cinzel', serif;
        font-size: 5rem;
        text-align: center;
        letter-spacing: 6px;
        margin-top: 50px;
        margin-bottom: 30px;
    }}

    /* EL CONTENEDOR QUE SE EXPANDE ELÁSTICAMENTE */
    .hybrid-wrapper {{
        position: relative;
        width: 380px;
        height: 320px; /* Altura inicial */
        margin: 40px auto;
        border-radius: 25px;
        overflow: hidden;
        display: flex;
        align-items: center; justify-content: center;
        transition: all 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}

    .hybrid-wrapper:hover {{
        height: 500px; /* Altura final */
        transform: translateY(-15px);
        box-shadow: 0 30px 60px rgba(0,0,0,0.7);
    }}

    /* EL EL LÁSER QUE ROTA */
    .hybrid-wrapper::before {{
        content: "";
        position: absolute;
        width: 160%;
        height: 160%;
        background-image: conic-gradient(
            transparent, 
            {ACCENT_COLOR}, 
            transparent 30%, 
            {GOLD_COLOR} 70%, 
            transparent
        );
        animation: rotate-laser 4s linear infinite;
        z-index: 0;
    }}

    @keyframes rotate-laser {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}

    /* EL CUERPO DE LA TARJETA */
    .hybrid-card {{
        position: relative;
        width: calc(100% - 4px);
        height: calc(100% - 4px);
        background: {CARD_BG};
        border-radius: 23px;
        z-index: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        padding-top: 50px;
        transition: background 0.4s;
        pointer-events: none;
    }}

    .hybrid-wrapper:hover .hybrid-card {{
        background: {CARD_BG}EB;
    }}

    .card-h1 {{
        font-family: 'Cinzel', serif;
        color: {TEXT_COLOR};
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 0 10px {TEXT_COLOR}33;
    }}

    .hidden-info {{
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.5s ease;
        text-align: center;
        margin-top: 40px;
        width: 80%;
    }}

    .hybrid-wrapper:hover .hidden-info {{
        opacity: 1;
        transform: translateY(0);
        transition-delay: 0.2s;
    }}

    .action-btn {{
        margin-top: 40px;
        background: {ACCENT_COLOR}33;
        border: 1px solid {ACCENT_COLOR};
        color: {TEXT_COLOR};
        padding: 10px 25px;
        border-radius: 50px;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        letter-spacing: 2px;
        font-size: 0.75rem;
        transition: all 0.3s;
    }}
    
    .hybrid-wrapper:hover .action-btn {{
        background: {ACCENT_COLOR};
        box-shadow: 0 0 15px {ACCENT_COLOR}66;
    }}

    /* Botón Invisible Overlay */
    .stButton {{
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: 10;
    }}

    .stButton button {{
        width: 100% !important;
        height: 100% !important;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        cursor: pointer !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("Híbrido Fusión")
    mode_label = "🌙 Modo Oscuro" if is_dark else "☀️ Modo Claro"
    if st.button(mode_label):
        st.session_state.theme = 'light' if is_dark else 'dark'
        st.rerun()

# --- HEADER: LOGO ---
logo_filename = "1-08.png" if is_dark else "1-01-copy.png"
logo_path = get_asset_path(logo_filename)
if os.path.exists(logo_path):
    bin_str = get_base64_of_bin_file(logo_path)
    st.markdown(f"""
        <div style="text-align: center; margin-top: 30px;">
            <img src="data:image/png;base64,{bin_str}" style="width: 220px;">
            <h1 class="main-title">ASTOR SIMULADOR</h1>
        </div>
    """, unsafe_allow_html=True)

# --- CARDS ---
c1, c2, c3, c4, c5 = st.columns([1, 2, 0.5, 2, 1])

with c2:
    st.markdown(f"""
        <div class="hybrid-wrapper">
            <div class="hybrid-card">
                <div class="card-h1" style="font-size: 1.4rem; opacity: 0.7;">SISTEMA</div>
                <div class="card-h1" style="margin-top:-5px;">5 - 100</div>
                <div class="hidden-info">
                    <p style="color: {TEXT_COLOR}B3;">Gestión patrimonial inteligente con proyecciones de alto rendimiento.</p>
                    <div class="action-btn">INGRESAR AL SISTEMA</div>
                </div>
            </div>
    """, unsafe_allow_html=True)
    if st.button("Sistema 5-100", key="btn_h1"):
        st.success("Fusion Mode Active")
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="hybrid-wrapper">
            <div class="hybrid-card">
                <div class="card-h1" style="font-size: 1.4rem; opacity: 0.7;">ESTUDIO</div>
                <div class="card-h1" style="margin-top:-5px;">DE COSTO</div>
                <div class="hidden-info">
                    <p style="color: {TEXT_COLOR}B3;">Descubre el costo real de esperar y optimiza tu ahorro.</p>
                    <div class="action-btn">COMENZAR ANÁLISIS</div>
                </div>
            </div>
    """, unsafe_allow_html=True)
    if st.button("Nuevo Simulador", key="btn_h2"):
        st.success("Fusion Mode Active")
    st.markdown("</div>", unsafe_allow_html=True)
