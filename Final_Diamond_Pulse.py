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

st.set_page_config(page_title="Astor | Diamond Pulse", layout="wide")

# --- CSS: DIAMOND PULSE ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Montserrat:wght@300;600&display=swap');

    .stApp {{
        background-color: {BG_COLOR} !important;
        background-image: 
            linear-gradient(45deg, {BG_COLOR} 25%, transparent 25%),
            linear-gradient(-45deg, {BG_COLOR} 25%, transparent 25%),
            linear-gradient(45deg, transparent 75%, {BG_COLOR} 75%),
            linear-gradient(-45deg, transparent 75%, {BG_COLOR} 75%) !important;
        background-size: 80px 80px !important;
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

    .diamond-wrapper {{
        position: relative;
        width: 380px;
        height: 380px;
        margin: 20px auto;
        display: flex;
        align-items: center; justify-content: center;
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}

    .diamond-wrapper:hover {{
        transform: scale(1.05) rotate(2deg);
    }}

    /* EL BORDE DE DIAMANTE */
    .diamond-border {{
        position: absolute;
        width: 106%;
        height: 106%;
        background: {ACCENT_COLOR};
        clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
        animation: diamond-pulse 2s infinite alternate;
        z-index: 0;
        opacity: 0.3;
        transition: opacity 0.4s;
    }}

    .diamond-wrapper:hover .diamond-border {{
        opacity: 1;
        background: linear-gradient({ACCENT_COLOR}, {GOLD_COLOR});
    }}

    @keyframes diamond-pulse {{
        from {{ transform: scale(0.98); opacity: 0.2; }}
        to {{ transform: scale(1.02); opacity: 0.6; }}
    }}

    .diamond-card {{
        position: relative;
        width: 100%;
        height: 100%;
        background: {CARD_BG};
        clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
        z-index: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }}

    .card-h2 {{
        font-family: 'Cinzel', serif;
        color: {TEXT_COLOR};
        font-size: 2.22rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
    }}

    .diamond-line {{
        width: 30px;
        height: 2px;
        background: {GOLD_COLOR};
        margin-top: 15px;
        transition: width 0.4s ease;
    }}

    .diamond-wrapper:hover .diamond-line {{
        width: 120px;
    }}

    /* Botón Invisible Overlay */
    .stButton {{
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: 10;
        clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
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
    st.title("Finalista V15: Diamond Pulse")
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
            <h1 class="main-title">ASTOR DIAMOND</h1>
        </div>
    """, unsafe_allow_html=True)

# --- CARDS ---
c1, c2, c3, c4, c5 = st.columns([1, 2, 0.5, 2, 1])

with c2:
    st.markdown(f"""
        <div class="diamond-wrapper">
            <div class="diamond-border"></div>
            <div class="diamond-card">
                <div class="card-h2" style="font-size: 1.2rem; opacity: 0.8;">SISTEMA</div>
                <div class="card-h2">OPTIMIZAR</div>
                <div class="diamond-line"></div>
                <div style="font-family: 'Montserrat'; color: {ACCENT_COLOR}; font-size: 0.6rem; letter-spacing: 2px; margin-top: 10px; font-weight: 800;">PREMIUM ACCESS</div>
            </div>
    """, unsafe_allow_html=True)
    if st.button("Sistema 5-100", key="btn_d1"):
        st.success("Diamond Pulse Sequence Established")
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="diamond-wrapper">
            <div class="diamond-border" style="animation-delay: 0.5s;"></div>
            <div class="diamond-card">
                <div class="card-h2" style="font-size: 1.2rem; opacity: 0.8;">PROYECTO</div>
                <div class="card-h2">ESTUDIO</div>
                <div class="diamond-line" style="background: {ACCENT_COLOR};"></div>
                <div style="font-family: 'Montserrat'; color: {GOLD_COLOR}; font-size: 0.6rem; letter-spacing: 2px; margin-top: 10px; font-weight: 800;">SIMULACIÓN V.I.P.</div>
            </div>
    """, unsafe_allow_html=True)
    if st.button("Nuevo Simulador", key="btn_d2"):
        st.success("Diamond Pulse Sequence Established")
    st.markdown("</div>", unsafe_allow_html=True)
