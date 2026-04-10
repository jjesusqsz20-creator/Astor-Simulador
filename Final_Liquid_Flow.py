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

st.set_page_config(page_title="Astor | Liquid Flow", layout="wide")

# --- CSS: LIQUID FLOW ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Montserrat:wght@300;600&display=swap');

    .stApp {{
        background-color: {BG_COLOR} !important;
        background-image: 
            radial-gradient(at 50% 0%, {ACCENT_COLOR}11 0px, transparent 50%) !important;
    }}
    
    header[data-testid="stHeader"] {{ background: transparent !important; }}
    [data-testid="stSidebar"] {{ background: {SIDEBAR_BG} !important; }}

    .main-title {{
        color: {TEXT_COLOR};
        font-family: 'Cinzel', serif;
        font-size: 5rem;
        text-align: center;
        margin-top: 50px;
        margin-bottom: 20px;
    }}

    .liquid-wrapper {{
        position: relative;
        width: 380px;
        height: 380px;
        margin: 20px auto;
        border-radius: 40px;
        background: {ACCENT_COLOR}22;
        display: flex;
        align-items: center; justify-content: center;
        transition: all 0.6s cubic-bezier(0.6, -0.28, 0.735, 0.045); /* Efecto gota */
        filter: drop-shadow(0 0 10px {ACCENT_COLOR}33);
        overflow: visible;
    }}

    .liquid-wrapper:hover {{
        transform: scale(1.05) translateY(-10px);
        background: {ACCENT_COLOR}44;
        filter: drop-shadow(0 0 30px {ACCENT_COLOR}66);
    }}

    /* EL BORDE LÍQUIDO (BLOB ANIMADO) */
    .liquid-border {{
        position: absolute;
        top: -10px; left: -10px; right: -10px; bottom: -10px;
        background: linear-gradient(45deg, {ACCENT_COLOR}, {GOLD_COLOR}, {ACCENT_COLOR});
        background-size: 400% 400%;
        animation: liquid-gradient 8s ease infinite;
        border-radius: 45px;
        z-index: 0;
        opacity: 0.3;
        transition: opacity 0.4s;
    }}

    .liquid-wrapper:hover .liquid-border {{
        opacity: 1;
        animation-duration: 4s;
    }}

    @keyframes liquid-gradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    .liquid-card {{
        position: relative;
        width: 100%;
        height: 100%;
        background: {CARD_BG};
        border-radius: 40px;
        z-index: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }}

    .card-h2 {{
        font-family: 'Cinzel', serif;
        color: {TEXT_COLOR};
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
    }}

    .liquid-label {{
        background: {ACCENT_COLOR};
        color: {CARD_BG};
        padding: 5px 25px;
        border-radius: 50px;
        font-family: 'Montserrat';
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 2px;
        margin-top: 30px;
        box-shadow: 0 5px 15px {ACCENT_COLOR}44;
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
    st.title("Finalista V9: Liquid Flow")
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
            <h1 class="main-title">ASTOR S-100</h1>
        </div>
    """, unsafe_allow_html=True)

# --- CARDS ---
c1, c2, c3, c4, c5 = st.columns([1, 2, 0.5, 2, 1])

with c2:
    st.markdown(f"""
        <div class="liquid-wrapper">
            <div class="liquid-border"></div>
            <div class="liquid-card">
                <div class="card-h2" style="font-size: 1.2rem; opacity: 0.7;">PROGRAMA</div>
                <div class="card-h2">OPTIMIZAR</div>
                <div class="liquid-label">VER FLUJO</div>
            </div>
    """, unsafe_allow_html=True)
    if st.button("Sistema 5-100", key="btn_l1"):
        st.success("Fluid Experience Active")
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="liquid-wrapper">
            <div class="liquid-border"></div>
            <div class="liquid-card">
                <div class="card-h2" style="font-size: 1.2rem; opacity: 0.7;">PROYECTO</div>
                <div class="card-h2">ESTUDIO</div>
                <div class="liquid-label" style="background: {GOLD_COLOR};">SIMULAR</div>
            </div>
    """, unsafe_allow_html=True)
    if st.button("Nuevo Simulador", key="btn_l2"):
        st.success("Fluid Experience Active")
    st.markdown("</div>", unsafe_allow_html=True)
