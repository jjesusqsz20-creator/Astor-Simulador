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

st.set_page_config(page_title="Astor | Neon Wave", layout="wide")

# --- CSS: NEON WAVE ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Montserrat:wght@300;600&display=swap');

    .stApp {{
        background-color: {BG_COLOR} !important;
        background-image: 
            radial-gradient(circle at 10% 20%, {ACCENT_COLOR}08 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, {GOLD_COLOR}08 0%, transparent 40%) !important;
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

    .wave-wrapper {{
        position: relative;
        width: 380px;
        height: 320px;
        margin: 40px auto;
        border-radius: 25px;
        display: flex;
        align-items: center; justify-content: center;
        transition: all 0.7s cubic-bezier(0.68, -0.6, 0.32, 1.6);
        background: transparent;
        overflow: hidden;
    }}

    .wave-wrapper:hover {{
        height: 480px;
        transform: translateY(-15px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.6);
    }}

    /* EL BORDE DE ONDA NEÓN */
    .wave-wrapper::before {{
        content: "";
        position: absolute;
        width: 150%;
        height: 150%;
        background-image: conic-gradient(
            transparent, 
            {ACCENT_COLOR}, 
            {GOLD_COLOR} 20%, 
            transparent 40%
        );
        animation: rotate-wave 3s linear infinite;
        filter: blur(5px);
        z-index: 0;
    }}

    @keyframes rotate-wave {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}

    .wave-card {{
        position: relative;
        width: calc(100% - 6px); /* Borde un poco más grueso */
        height: calc(100% - 6px);
        background: {CARD_BG};
        border-radius: 22px;
        z-index: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        padding-top: 50px;
        transition: all 0.3s;
        pointer-events: none;
    }}

    .card-h1 {{
        font-family: 'Cinzel', serif;
        color: {TEXT_COLOR};
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
    }}

    .wave-content {{
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.5s ease;
        text-align: center;
        margin-top: 40px;
    }}

    .wave-wrapper:hover .wave-content {{
        opacity: 1;
        transform: translateY(0);
        transition-delay: 0.2s;
    }}

    .wave-btn {{
        background: {GOLD_COLOR}22;
        color: {GOLD_COLOR};
        padding: 8px 30px;
        border-radius: 50px;
        font-family: 'Montserrat';
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 2px;
        margin-top: 30px;
        border: 1px solid {GOLD_COLOR}66;
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
    st.title("Finalista V13: Neon Wave")
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
            <h1 class="main-title">ASTOR S-100</h1>
        </div>
    """, unsafe_allow_html=True)

# --- CARDS ---
c1, c2, c3, c4, c5 = st.columns([1, 2, 0.5, 2, 1])

with c2:
    st.markdown(f"""
        <div class="wave-wrapper">
            <div class="wave-card">
                <div class="card-h1" style="font-size: 1.2rem; opacity: 0.8;">SISTEMA</div>
                <div class="card-h1">5 - 100</div>
                <div class="wave-content">
                    <p style="color: {TEXT_COLOR}B3; font-size: 0.85rem;">Simulación patrimonial dinámica e institucional.</p>
                    <div class="wave-btn">ENTRAR AL SISTEMA</div>
                </div>
            </div>
    """, unsafe_allow_html=True)
    if st.button("Sistema 5-100", key="btn_w1"):
        st.success("Wave Sequence Active")
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="wave-wrapper">
            <div class="wave-card">
                <div class="card-h1" style="font-size: 1.2rem; opacity: 0.8;">ESTUDIO</div>
                <div class="card-h1">COSTOS</div>
                <div class="wave-content">
                    <p style="color: {TEXT_COLOR}B3; font-size: 0.85rem;">Descubre tu potencial de ahorro en tiempo real.</p>
                    <div class="wave-btn">VER SIMULACIÓN</div>
                </div>
            </div>
    """, unsafe_allow_html=True)
    if st.button("Nuevo Simulador", key="btn_w2"):
        st.success("Wave Sequence Active")
    st.markdown("</div>", unsafe_allow_html=True)
