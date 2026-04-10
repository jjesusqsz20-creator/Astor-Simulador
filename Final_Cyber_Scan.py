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

st.set_page_config(page_title="Astor | Cyber Scan", layout="wide")

# --- CSS: CYBER SCAN ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Montserrat:wght@300;600&display=swap');

    .stApp {{
        background-color: {BG_COLOR} !important;
        background-image: 
            linear-gradient(rgba(107, 164, 164, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(107, 164, 164, 0.05) 1px, transparent 1px) !important;
        background-size: 50px 50px !important;
    }}
    
    header[data-testid="stHeader"] {{ background: transparent !important; }}
    [data-testid="stSidebar"] {{ background: {SIDEBAR_BG} !important; }}

    .main-title {{
        color: {TEXT_COLOR};
        font-family: 'Cinzel', serif;
        font-size: 5rem;
        text-align: center;
        margin-top: 50px;
    }}

    .scan-wrapper {{
        position: relative;
        width: 380px;
        height: 380px;
        margin: 40px auto;
        border-radius: 15px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.05);
        display: flex;
        align-items: center; justify-content: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}

    .scan-wrapper:hover {{
        transform: scale(1.05);
        border-color: {ACCENT_COLOR};
    }}

    /* EL ESCANEO LÁSER VERTICAL */
    .scan-line {{
        position: absolute;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, transparent, {ACCENT_COLOR}, transparent);
        top: -10px;
        animation: scan-move 3s ease-in-out infinite alternate;
        z-index: 2;
        box-shadow: 0 0 15px {ACCENT_COLOR};
    }}

    @keyframes scan-move {{
        0% {{ top: -10px; opacity: 1; }}
        100% {{ top: 100%; opacity: 1; }}
    }}

    @keyframes scan-move-reverse {{
        0% {{ top: 100%; opacity: 1; }}
        100% {{ top: -10px; opacity: 1; }}
    }}

    .scan-card {{
        position: relative;
        width: 100%;
        height: 100%;
        background: {CARD_BG};
        z-index: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transition: all 0.3s;
    }}

    .scan-wrapper:hover .scan-card {{
        background: {CARD_BG}F0;
    }}

    .card-h1 {{
        font-family: 'Cinzel', serif;
        color: {TEXT_COLOR};
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
    }}

    .tech-badge {{
        background: transparent;
        color: {GOLD_COLOR};
        padding: 5px 15px;
        border: 1px solid {GOLD_COLOR}44;
        font-family: 'Montserrat';
        font-size: 0.65rem;
        font-weight: 800;
        letter-spacing: 3px;
        margin-top: 25px;
        transition: all 0.3s;
    }}
    
    .scan-wrapper:hover .tech-badge {{
        background: {GOLD_COLOR};
        color: {CARD_BG};
    }}

    /* EL BORDE LÁSER QUE APARECE SOLO AL HOVER */
    .scan-wrapper::before {{
        content: "";
        position: absolute;
        width: 120%;
        height: 120%;
        background-image: conic-gradient(transparent, {ACCENT_COLOR}, transparent 30%);
        animation: rotate-laser 3s linear infinite;
        z-index: 0;
        opacity: 0;
        transition: opacity 0.5s;
    }}

    .scan-wrapper:hover::before {{
        opacity: 1;
    }}

    @keyframes rotate-laser {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
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
    st.title("Finalista V16: Cyber Scan")
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
            <img src="data:image/png;base64,{bin_str}" style="width: 200px;">
            <h1 class="main-title">ASTOR TECH</h1>
        </div>
    """, unsafe_allow_html=True)

# --- CARDS ---
c1, c2, c3, c4, c5 = st.columns([1, 2, 0.5, 2, 1])

with c2:
    st.markdown(f"""
        <div class="scan-wrapper">
            <div class="scan-line"></div>
            <div class="scan-card">
                <div class="card-h1" style="font-size: 1.2rem; opacity: 0.7;">ASTOR</div>
                <div class="card-h1">SIMULADOR</div>
                <div class="tech-badge">SISTEMA 5-100</div>
            </div>
    """, unsafe_allow_html=True)
    if st.button("Sistema 5-100", key="btn_s1"):
        st.success("Cyber Scan Sequence Established")
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="scan-wrapper">
            <div class="scan-line" style="animation: scan-move-reverse 3s ease-in-out infinite alternate; background: linear-gradient(90deg, transparent, {GOLD_COLOR}, transparent); box-shadow: 0 0 15px {GOLD_COLOR};"></div>
            <div class="scan-card">
                <div class="card-h1" style="font-size: 1.2rem; opacity: 0.7;">PROYECTO</div>
                <div class="card-h1">COSTOS</div>
                <div class="tech-badge" style="border-color: {ACCENT_COLOR}; color: {ACCENT_COLOR};">MÓDULO ALFA</div>
            </div>
    """, unsafe_allow_html=True)
    if st.button("Nuevo Simulador", key="btn_s2"):
        st.success("Cyber Scan Sequence Established")
    st.markdown("</div>", unsafe_allow_html=True)
