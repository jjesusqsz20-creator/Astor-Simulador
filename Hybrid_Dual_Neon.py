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

st.set_page_config(page_title="Astor | Dual Neon Pop", layout="wide")

# --- CSS: DUAL NEON POP ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Montserrat:wght@300;600&display=swap');

    .stApp {{
        background-color: {BG_COLOR} !important;
        background-image: 
            radial-gradient(circle at 0% 0%, {ACCENT_COLOR}08 0%, transparent 50%),
            radial-gradient(circle at 100% 100%, {GOLD_COLOR}08 0%, transparent 50%) !important;
    }}
    
    header[data-testid="stHeader"] {{ background: transparent !important; }}
    [data-testid="stSidebar"] {{ background: {SIDEBAR_BG} !important; }}

    .main-title {{
        color: {TEXT_COLOR};
        font-family: 'Cinzel', serif;
        font-size: 5rem;
        text-align: center;
        letter-spacing: 2px;
        margin-top: 50px;
        margin-bottom: 40px;
    }}

    .dual-wrapper {{
        position: relative;
        width: 380px;
        height: 380px;
        margin: 20px auto;
        border-radius: 50%; /* Empezamos con círculo, pero el card interior es cuadrado */
        display: flex;
        align-items: center; justify-content: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}

    .dual-wrapper:hover {{
        transform: scale(1.1) rotate(2deg);
    }}

    /* EL PRIMER NEÓN (CIAN) */
    .dual-wrapper::before {{
        content: "";
        position: absolute;
        width: 110%;
        height: 110%;
        background-image: conic-gradient(transparent, {ACCENT_COLOR}, transparent 40%);
        animation: rotate-left 3s linear infinite;
        border-radius: 40px;
        z-index: 0;
    }}

    /* EL SEGUNDO NEÓN (ORO) */
    .dual-wrapper::after {{
        content: "";
        position: absolute;
        width: 110%;
        height: 110%;
        background-image: conic-gradient(transparent, {GOLD_COLOR}, transparent 40%);
        animation: rotate-right 3s linear infinite;
        border-radius: 40px;
        z-index: 0;
    }}

    @keyframes rotate-left {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}

    @keyframes rotate-right {{
        from {{ transform: rotate(360deg); }}
        to {{ transform: rotate(0deg); }}
    }}

    .dual-card {{
        position: relative;
        width: 100%;
        height: 100%;
        background: {CARD_BG};
        border-radius: 38px;
        z-index: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transition: all 0.3s;
        pointer-events: none;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
    }}

    .dual-wrapper:hover .dual-card {{
        background: {CARD_BG}F0;
        box-shadow: 0 0 40px {ACCENT_COLOR}33;
    }}

    .card-h1 {{
        font-family: 'Cinzel', serif;
        color: {TEXT_COLOR};
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
    }}

    .pop-badge {{
        background: {GOLD_COLOR}22;
        color: {GOLD_COLOR};
        padding: 5px 15px;
        border-radius: 20px;
        font-family: 'Montserrat';
        font-size: 0.65rem;
        font-weight: 800;
        letter-spacing: 2px;
        margin-top: 15px;
        border: 1px solid {GOLD_COLOR}44;
        transition: all 0.3s;
    }}
    
    .dual-wrapper:hover .pop-badge {{
        background: {GOLD_COLOR};
        color: {CARD_BG};
        transform: translateY(-5px);
    }}

    /* Botón Invisible Overlay */
    .stButton {{
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: 10;
    }}

    .stButton button {{
        width: 100% !important;
        height: 380px !important;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        cursor: pointer !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("Híbrido Dual")
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
            <img src="data:image/png;base64,{bin_str}" style="width: 180px;">
            <h1 class="main-title">ASTOR</h1>
            <p style="color: {ACCENT_COLOR}; letter-spacing: 8px; font-weight: 600; margin-top:-20px;">SIMULADOR</p>
        </div>
    """, unsafe_allow_html=True)

# --- CARDS ---
c1, c2, c3, c4, c5 = st.columns([1, 2, 0.5, 2, 1])

with c2:
    st.markdown(f"""
        <div class="dual-wrapper">
            <div class="dual-card">
                <div class="card-h1" style="font-size: 1.2rem; opacity: 0.7;">PROGRAMA</div>
                <div class="card-h1">5 - 100</div>
                <div class="pop-badge">ACCESO ELITE</div>
            </div>
    """, unsafe_allow_html=True)
    if st.button("Sistema 5-100", key="btn_d1"):
        st.success("Dual Action Pop!")
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="dual-wrapper">
            <div class="dual-card">
                <div class="card-h1" style="font-size: 1.2rem; opacity: 0.7;">PROYECTO</div>
                <div class="card-h1">COSTOS</div>
                <div class="pop-badge" style="color: {ACCENT_COLOR}; border-color: {ACCENT_COLOR}44; background: {ACCENT_COLOR}11;">MÓDULO ALFA</div>
            </div>
    """, unsafe_allow_html=True)
    if st.button("Nuevo Simulador", key="btn_d2"):
        st.success("Dual Action Pop!")
    st.markdown("</div>", unsafe_allow_html=True)
