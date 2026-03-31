import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import os
import base64
import sys
from PIL import Image

# --- RESOLUCIÓN DE RUTAS PARA EXE ---
def get_asset_path(relative_path):
    """Obtiene la ruta absoluta para recursos, compatible con PyInstaller"""
    if getattr(sys, 'frozen', False):
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# --- CONFIGURACIÓN DE PÁGINA ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

st.set_page_config(
    page_title="Astor simulador",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# --- CONFIGURACIÓN DE TEMAS ---
is_dark = st.session_state.theme == 'dark'

if is_dark:
    BG_COLOR = "#080A0F"
    SIDEBAR_BG = "#050505"
    TEXT_COLOR = "#FEFFFF"
    ACCENT_COLOR = "#6BA4A4" 
    GOLD_COLOR = "#DFBF72"
    CARD_BG = "#252932"
    INPUT_BG = "#13161C"
    EXPANDER_BG = "#052429"
    RADIAL_OPACITY = "1A"
    SUNSET_COLOR = "#E6C200" # Oro en oscuro
    BORDER_COLOR = "#6BA4A422"
else:
    # Modo Claro (Identidad Astor Original)
    BG_COLOR = "#F0F2F5"      # Fondo General (Blanco Azulado)
    BG_GRADIENT_END = "#E2E8F0" # Gris Azulado
    SIDEBAR_BG = "#FFFFFF"
    TEXT_COLOR = "#1E3A8A"    # Azul Astor (Primary)
    ACCENT_COLOR = "#3B82F6"  # Azul Acento
    GOLD_COLOR = "#1E3A8A"    # Azul para títulos en claro
    CARD_BG = "#FFFFFF"       # Blanco Marfil
    INPUT_BG = "#F1F5F9"
    EXPANDER_BG = "#F8FAFC"
    RADIAL_OPACITY = "08"
    SUNSET_COLOR = "#F59E0B"  # Naranja Sunset
    BORDER_COLOR = "#E5E7EB"
    TEXT_SECONDARY = "#64748B" # Gris Grafito
    TITLE_COLOR = "#364350"    # Color específico del logo solicitado

COLORES = [
    "#EF4444",  # Rojo Coral
    "#FBBF24",  # Amarillo Ámbar
    "#10B981",  # Verde Esmeralda
    "#3B82F6",  # Azul Acento
    "#1E3A8A"   # Azul Astor
]

# --- MARCA DE AGUA ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_watermark_excel(is_dark=True):
    """Genera una versión transparente y rotada del logo para el fondo de Excel"""
    # Usar logo blanco para fondo oscuro y logo oscuro para fondo claro
    logo_filename = "1-07.png" if is_dark else "1-01.png"
    logo_path = get_asset_path(logo_filename)
    if not os.path.exists(logo_path):
        return None
    
    target_path = f"watermark_excel_{'dark' if is_dark else 'light'}.png"
    # Forzar regeneración para aplicar cambios de opacidad/tamaño
    if os.path.exists(target_path):
        try:
            os.remove(target_path)
        except:
            pass
    
    try:
        img = Image.open(logo_path).convert("RGBA")
        # Ajustar tamaño para que coincida más con la escala visual (100px)
        img.thumbnail((110, 110), Image.Resampling.LANCZOS)
        
        # Rotar -30 grados (como en la app)
        img = img.rotate(-30, expand=True, resample=Image.Resampling.BICUBIC)
        
        # Aplicar transparencia sutil al logo
        # En modo claro necesitamos un poco más de opacidad para ser visto
        opacity_val = 0.08 if is_dark else 0.12
        alpha = img.split()[3]
        alpha = alpha.point(lambda p: p * opacity_val)
        img.putalpha(alpha)
        
        # Invertir colores si es modo claro para que el logo se vea sobre blanco (si es necesario)
        # El logo 1-07 es oscuro, sobre blanco se ve bien. 
        # Pero si el usuario prefiere el 1-01 para claro, podríamos usarlo.
        
        # Crear un lienzo dinámico
        canvas_size = 120 
        fondo_color = (5, 5, 5, 255) if is_dark else (255, 255, 255, 255)
        canvas = Image.new("RGBA", (canvas_size, canvas_size), fondo_color)
        
        # Centrar el logo en el lienzo
        img_w, img_h = img.size
        offset = ((canvas_size - img_w) // 2, (canvas_size - img_h) // 2)
        canvas.paste(img, offset, img)
        
        canvas.save(target_path)
        return target_path
    except Exception:
        return None

watermark_css = ""
logo_watermark = get_asset_path("1-07.png")
if os.path.exists(logo_watermark):
    bin_str = get_base64_of_bin_file(logo_watermark)
    invert_val = 1 if is_dark else 0
    watermark_css = f"""
    .stApp::before {{
        content: "";
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: 150px;
        background-repeat: repeat;
        transform: rotate(-30deg);
        opacity: {0.05 if is_dark else 0.03};
        filter: brightness(0) invert({invert_val});
        z-index: 99;
        pointer-events: none;
    }}
    """


st.markdown(f"""
    <style>
    {watermark_css}
    
    /* Fondo General */
    /* Quitar franja blanca superior */
    header[data-testid="stHeader"] {{
        background: transparent !important;
        color: transparent !important;
    }}
    
    [data-testid="stHeader"] {{
        display: none !important;
    }}

    .stApp {{ 
        background: 
            radial-gradient(circle at 10% 20%, #E04343{RADIAL_OPACITY} 0%, transparent 50%),
            radial-gradient(circle at 90% 10%, #00CC6A{RADIAL_OPACITY} 0%, transparent 50%),
            radial-gradient(circle at 50% 80%, #B800D6{RADIAL_OPACITY} 0%, transparent 50%),
            radial-gradient(circle at 80% 90%, #5A8B8B{RADIAL_OPACITY if is_dark else '03'} 0%, transparent 40%),
            {BG_COLOR if is_dark else f'linear-gradient(135deg, {BG_COLOR} 0%, {BG_GRADIENT_END} 100%)'} !important;
        color: {TEXT_COLOR};
        background-attachment: fixed;
    }}
    .stApp::after {{
        display: none !important;
    }}
    
    /* Sidebar Ancho Fijo */
    [data-testid="stSidebar"] {{
        background: {SIDEBAR_BG} !important;
        border-right: 1px solid {BORDER_COLOR};
        min-width: 350px !important;
        max-width: 350px !important;
        width: 350px !important;
    }}
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
        color: {TEXT_COLOR} !important;
        text-shadow: {'0 0 10px '+TEXT_COLOR+'33' if is_dark else 'none'} !important;
    }}
    
    /* Expanders */
    div[data-testid="stExpander"] {{
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 8px;
        background-color: {EXPANDER_BG} !important;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }}
    div[data-testid="stExpander"]:hover {{
        border-color: {ACCENT_COLOR} !important;
        box-shadow: 0 0 15px {ACCENT_COLOR}11;
    }}
    div[data-testid="stExpander"] details summary {{
        background-color: transparent !important;
        color: {TEXT_COLOR} !important;
        font-weight: 600;
        border-radius: 8px;
    }}
    
    /* Labels Globales de Inputs */
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stCheckbox label, .stMultiSelect label, .stSlider label {{
        color: {ACCENT_COLOR if is_dark else TEXT_SECONDARY} !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.8px !important;
        margin-bottom: 5px !important;
    }}
    
    /* Inputs */
    .stTextInput input, .stNumberInput input {{
        color: {TEXT_COLOR} !important;
        background-color: {INPUT_BG} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 4px;
    }}
    
    .stNumberInput button {{
        background-color: {INPUT_BG} !important;
        color: {TEXT_COLOR} !important;
        border: 1px solid {BORDER_COLOR} !important;
    }}
    
    /* Selectboxes */
    div[data-baseweb="select"] {{
        background-color: {INPUT_BG} !important;
        color: {TEXT_COLOR} !important;
        border-radius: 4px !important;
    }}
    
    div[data-baseweb="select"] > div {{
        background-color: transparent !important;
        color: {TEXT_COLOR} !important;
    }}
    
    /* Lista desplegable de Selectbox */
    ul[data-baseweb="menu"] {{
        background-color: {SIDEBAR_BG} !important;
        color: {TEXT_COLOR} !important;
    }}
    
    li[data-baseweb="option"] {{
        background-color: transparent !important;
        color: {TEXT_COLOR} !important;
    }}
    
    li[data-baseweb="option"]:hover {{
        background-color: {ACCENT_COLOR}22 !important;
    }}
    
    /* Checkboxes y Radio labels (específico para el texto al lado del cuadro/radio) */
    div[data-testid="stCheckbox"] label p, 
    div[role="radiogroup"] label p {{
        color: {ACCENT_COLOR if is_dark else TEXT_COLOR} !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
    }}
    
    /* Captions */
    [data-testid="stCaptionContainer"] {{
        color: {ACCENT_COLOR if is_dark else TEXT_SECONDARY} !important;
        font-weight: 700 !important;
        opacity: 1.0 !important;
    }}
    
    /* Tarjetas de Métricas */
    [data-testid="stMetric"] {{
        background-color: {CARD_BG};
        padding: 20px;
        border-radius: 12px;
        border: 1px solid {BORDER_COLOR};
        box-shadow: 0 4px 20px rgba(0, 0, 0, {0.4 if is_dark else 0.05});
        text-align: center;
    }}
    [data-testid="stMetric"]:hover {{
        transform: translateY(-5px);
        border-color: {ACCENT_COLOR};
        box-shadow: 0 0 20px {ACCENT_COLOR}33;
    }}
    [data-testid="stMetric"] label {{ color: {ACCENT_COLOR if is_dark else TEXT_SECONDARY} !important; font-weight: 900; letter-spacing: 1px; }}
    [data-testid="stMetric"] [data-testid="stMetricValue"] {{ 
        color: {SUNSET_COLOR} !important; 
        font-weight: 800; 
        font-size: 1.8rem;
        text-shadow: {('0 0 15px ' + SUNSET_COLOR + '66') if is_dark else 'none'};
    }}

    /* Headings */
    h2, h3, h4 {{ 
        color: {GOLD_COLOR} !important; 
        font-family: 'Cinzel', serif !important;
        text-shadow: 0 0 10px {GOLD_COLOR}33;
    }}
    
    .white-title {{
        color: {TITLE_COLOR if not is_dark else TEXT_COLOR} !important;
        font-family: 'Cinzel', serif !important;
        text-shadow: {('0 0 15px ' + TEXT_COLOR + '33') if is_dark else 'none'} !important;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: transparent;
        gap: 10px;
    }}
    .stTabs [data-baseweb="tab-list"] button {{
        background-color: {CARD_BG} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 20px !important;
    }}
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        border-color: {ACCENT_COLOR if is_dark else TEXT_COLOR} !important;
        border-bottom: 2px solid {ACCENT_COLOR if is_dark else TEXT_COLOR} !important;
        background-color: {'#303641' if is_dark else '#F8FAFC'} !important;
    }}
    .stTabs [data-baseweb="tab-list"] button p {{
        color: {TEXT_COLOR} !important;
        font-size: 1rem !important;
        font-weight: bold !important;
    }}
    
    /* Button Global */
    .stButton button, .stDownloadButton button {{
        background-color: {CARD_BG if is_dark else '#FFFFFF'} !important;
        color: {ACCENT_COLOR if is_dark else TEXT_COLOR} !important;
        border: 1px solid {ACCENT_COLOR+'44' if is_dark else '#D1D5DB'} !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        text-transform: none !important;
        letter-spacing: 0.5px !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.3s ease !important;
        box-shadow: {('0 2px 5px rgba(0,0,0,0.2)') if is_dark else '0 2px 4px rgba(0,0,0,0.05)'} !important;
    }}
    .stButton button:hover, .stDownloadButton button:hover {{
        background-color: {ACCENT_COLOR if is_dark else '#F8FAFC'} !important;
        color: {'#FFFFFF' if is_dark else TEXT_COLOR} !important;
        box-shadow: 0 4px 12px {ACCENT_COLOR+'44' if is_dark else 'rgba(0,0,0,0.1)'} !important;
        border-color: {ACCENT_COLOR if is_dark else TEXT_COLOR} !important;
    }}

    /* Dataframe y Tablas */
    table, thead, tbody, tr, th, td {{
        background-color: {CARD_BG} !important;
        color: {TEXT_COLOR} !important;
        border: 1px solid {TEXT_COLOR}11 !important;
    }}
    
    th {{
        background-color: {'#303641' if is_dark else '#E2E8F0'} !important;
        color: {ACCENT_COLOR if is_dark else TEXT_COLOR} !important;
        text-transform: uppercase !important;
        font-weight: bold !important;
    }}

    /* Contenedor stDataFrame */
    div[data-testid="stDataFrame"], div[data-testid="stDataFrame"] div {{
        background-color: {CARD_BG} !important;
    }}

    /* Eliminar cualquier rastro de blanco en el área de la tabla */
    [data-testid="stDataFrame"] section {{
        background-color: {CARD_BG} !important;
    }}
    
    /* Scrollbars para tablas */
    [data-testid="stDataFrame"] ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    [data-testid="stDataFrame"] ::-webkit-scrollbar-thumb {{
        background: {ACCENT_COLOR}33;
        border-radius: 10px;
    }}
    [data-testid="stDataFrame"] ::-webkit-scrollbar-thumb:hover {{
        background: {ACCENT_COLOR};
    }}
    </style>
""", unsafe_allow_html=True)

# --- BOTÓN DE MODO CLARO/OSCURO ---
with st.sidebar:
    mode_label = "🌙 Modo Oscuro" if is_dark else "☀️ Modo Claro"
    if st.button(mode_label, key="theme_toggle", use_container_width=True):
        st.session_state.theme = 'light' if is_dark else 'dark'
        st.rerun()
    st.markdown("<hr style='margin: 10px 0; opacity: 0.2;'>", unsafe_allow_html=True)

# --- ESTADO DE LA SESIÓN ---
if 'num_escenarios' not in st.session_state:
    st.session_state.num_escenarios = 3

if 'aportaciones_extra' not in st.session_state:
    st.session_state.aportaciones_extra = []

def agregar_escenario():
    if st.session_state.num_escenarios < 5:
        st.session_state.num_escenarios += 1

def quitar_escenario():
    if st.session_state.num_escenarios > 1:
        st.session_state.num_escenarios -= 1

def agregar_extra(opcion, anio, mes, monto):
    st.session_state.aportaciones_extra.append({
        "opcion": opcion, # Puede ser "Todas" o un entero (1, 2, 3...)
        "anio": anio,
        "mes": mes,
        "monto": monto
    })

def borrar_extras():
    st.session_state.aportaciones_extra = []

# --- FUNCIONES AUXILIARES ---
def obtener_porcentaje_bono(monto_mensual):
    """Calcula el porcentaje de bono según la tabla de aportación (Base Anual)"""
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

# --- MOTOR DE CÁLCULO (Aportación SIEMPRE MENSUAL + EXTRAS + CAMBIO MES 19) ---
def calcular_escenario(monto_aporte, edad, tasa_anual, inflacion_activa, tasa_inflacion, isr_retencion, plazo_anos=25, opcion_id=1, extras=[], monto_mes_19=None):
    # El plazo por defecto es 25 años, pero puede ser modificado (ej. para el cálculo a edad 65)
    meses_totales = int(plazo_anos * 12)
    
    monto_actual = float(monto_aporte)
    
    # --- CÁLCULO DINÁMICO DEL BONO (Basado en la aportación inicial) ---
    bono_porcentaje = obtener_porcentaje_bono(monto_actual)
    
    # Cargos según PDF
    tasa_gestion_mensual = 0.001        # 0.1% Mensual sobre Saldo Total
    tasa_admin_trimestral = 0.009       # 0.9% Trimestral sobre SALDO INICIAL
    
    # Cargo Fijo en UDIS (Mes 19+)
    cargo_fijo_udis = 15.0
    valor_udi_inicial = 8.25 # Valor aproximado actual
    
    # Conversión de tasas
    tasa_interes_mensual_fondo = (tasa_anual / 100) / 12 # Tasa del usuario (10% default)
    tasa_interes_mensual_bono = (0.09) / 12  # Tasa fija del 9% para el bono (NO VISIBLE)
    
    datos = []
    
    valor_udi_actual = valor_udi_inicial
    factor_inflacion_acumulado = 1.0 # Para rastrear la inflación total y aplicarla a cambios futuros
    
    # Cubetas de Saldo SEPARADAS para aplicar tasas distintas
    # Estas variables ACUMULAN el saldo mes a mes.
    saldo_bono = 0.0            # Solo el dinero del bono (crece al 9%)
    saldo_inicial_aport = 0.0   # Aportaciones mes 1-18 (crece al % usuario)
    saldo_regular = 0.0         # Aportaciones mes 19+ (crece al % usuario)
    
    acumulado_aportado = 0.0
    
    # Calcular aportación anualizada para el bono (Siempre es monto mensual * 12)
    monto_anualizado = monto_actual * 12

    # El bono se acredita mensualmente el año 1 a la cubeta bono
    bono_mensual_ano1 = (monto_anualizado * bono_porcentaje) / 12

    for mes in range(1, meses_totales + 1):
        anio_actual = (mes - 1) // 12 + 1
        mes_del_ano = (mes - 1) % 12 + 1
        
        # AJUSTE DE EDAD: Año 1 = Edad Inicial + 1
        edad_actual = edad + anio_actual 
        
        # 1. Ajuste Inflacionario Anual
        if inflacion_activa and mes > 1 and (mes - 1) % 12 == 0:
            factor_inflacion = (1 + tasa_inflacion / 100)
            factor_inflacion_acumulado *= factor_inflacion
            monto_actual *= factor_inflacion
            valor_udi_actual *= factor_inflacion # El valor de la UDI sube con la inflación
        
        # --- CAMBIO DE APORTACIÓN MES 19 ---
        # Solo aplicar si el monto es diferente al inicial (para no romper la inflación si es igual)
        if mes == 19 and monto_mes_19 is not None and monto_mes_19 > 0 and monto_mes_19 != monto_inicial:
            # Interpretar el nuevo monto como "Valor Presente" y ajustarlo por la inflación acumulada
            monto_actual = float(monto_mes_19) * factor_inflacion_acumulado
            
        # 2. Aportación Regular (SIEMPRE MENSUAL)
        aportacion_periodo = monto_actual
        
        # 3. Revisar si hay Aportaciones Extraordinarias
        monto_extra_mes = 0.0
        for extra in extras:
            es_opcion_correcta = (extra['opcion'] == "Todas") or (extra['opcion'] == opcion_id)
            if es_opcion_correcta and extra['anio'] == anio_actual and extra['mes'] == mes_del_ano:
                monto_extra_mes += extra['monto']

        # 4. Asignar Aportaciones a Cubetas
        bono_mes = bono_mensual_ano1 if anio_actual == 1 else 0.0
        
        # Distribución:
        # - Bono -> Cubeta Bono
        # - Aportación Regular Mes 1-18 -> Cubeta Inicial Aport
        # - Aportación Regular Mes 19+ -> Cubeta Regular
        # - Extras -> Cubeta Regular
        
        saldo_bono += bono_mes
        
        if mes <= 18:
            saldo_inicial_aport += aportacion_periodo
        else:
            saldo_regular += aportacion_periodo
        
        saldo_regular += monto_extra_mes
            
        acumulado_aportado += (aportacion_periodo + monto_extra_mes)

        # 5. Generar Intereses (Tasas Diferenciadas sobre lo ACUMULADO)
        # Aquí es donde se asegura que el capital de los primeros 18 meses sigue creciendo.
        interes_bono = saldo_bono * tasa_interes_mensual_bono          # 9% Fijo
        interes_inicial = saldo_inicial_aport * tasa_interes_mensual_fondo # Tasa Usuario
        interes_regular = saldo_regular * tasa_interes_mensual_fondo       # Tasa Usuario
        
        saldo_bono += interes_bono
        saldo_inicial_aport += interes_inicial
        saldo_regular += interes_regular
        
        interes_total_mes = interes_bono + interes_inicial + interes_regular
        
        # 6. Aplicar Cargos
        # A) Cargo de Gestión: 0.1% mensual a TODO
        # Lo aplicamos proporcionalmente o directo a cada cubeta
        cg_bono = saldo_bono * tasa_gestion_mensual
        cg_ini = saldo_inicial_aport * tasa_gestion_mensual
        cg_reg = saldo_regular * tasa_gestion_mensual
        
        saldo_bono -= cg_bono
        saldo_inicial_aport -= cg_ini
        saldo_regular -= cg_reg
        
        cargo_gestion_total = cg_bono + cg_ini + cg_reg
        
        # B) Cargo Administrativo Variable: 0.9% Trimestral SOLO sobre Saldo Inicial (Bono + Inicial Aport)
        cargo_admin_var = 0.0
        if mes % 3 == 0: # Mes 3, 6, 9...
            cav_bono = saldo_bono * tasa_admin_trimestral
            cav_ini = saldo_inicial_aport * tasa_admin_trimestral
            
            saldo_bono -= cav_bono
            saldo_inicial_aport -= cav_ini
            
            cargo_admin_var = cav_bono + cav_ini
            
        # C) Cargo Administrativo Fijo: 15 UDIS a partir del mes 19
        cargo_fijo_total = 0.0
        if mes >= 19:
            cargo_fijo_total = cargo_fijo_udis * valor_udi_actual
            # Prioridad de cobro: Regular -> Inicial -> Bono
            remanente = cargo_fijo_total
            
            if saldo_regular >= remanente:
                saldo_regular -= remanente
                remanente = 0
            else:
                remanente -= saldo_regular
                saldo_regular = 0
                
            if remanente > 0:
                if saldo_inicial_aport >= remanente:
                    saldo_inicial_aport -= remanente
                    remanente = 0
                else:
                    remanente -= saldo_inicial_aport
                    saldo_inicial_aport = 0
            
            if remanente > 0:
                saldo_bono -= remanente # Último recurso

        cargos_totales_mes = cargo_gestion_total + cargo_admin_var + cargo_fijo_total
        
        # Saldos Agregados
        saldo_total = saldo_bono + saldo_inicial_aport + saldo_regular
        
        # --- CÁLCULO DE SALDO DISPONIBLE Y NETO (REGLAS ACTUALIZADAS) ---
        
        # 1. Disponibilidad:
        # - Antes de los 65: Solo Saldo Regular (Saldo Inicial + Bono está bloqueado).
        # - A los 65 o más: TODO es disponible (Inicial + Regular + Bono).
        if edad_actual >= 65 or anio_actual >= 25:
            saldo_disponible = saldo_total
        else:
            saldo_disponible = saldo_regular
        
        # 2. Impuestos (ISR):
        # - Antes de los 65: Se aplica retención sobre lo disponible.
        # - A los 65 o más: Exento de impuestos.
        if edad_actual >= 60:
            saldo_neto_disponible = saldo_disponible
        else:
            saldo_neto_disponible = saldo_disponible * (1 - (isr_retencion/100))
        
        # 3. Retención ALLIANZ (Tasas específicas por año)
        # Año 1: 0.00%
        # Año 2: 0.43%
        # Año 3: 0.61%
        # Año 4: 0.77%
        # Año 5-9: 0.90%
        # Año 10-14: 3.19%
        # Año 15-19: 6.18%
        # Año 20+: 8.18%
        
        tasa_retencion_allianz = 0.0
        if edad_actual >= 60:
            tasa_retencion_allianz = 0.0
        elif anio_actual == 1: tasa_retencion_allianz = 0.00
        elif anio_actual == 2: tasa_retencion_allianz = 0.0043
        elif anio_actual == 3: tasa_retencion_allianz = 0.0061
        elif anio_actual == 4: tasa_retencion_allianz = 0.0077
        elif 5 <= anio_actual <= 9: tasa_retencion_allianz = 0.0090
        elif 10 <= anio_actual <= 14: tasa_retencion_allianz = 0.0319
        elif 15 <= anio_actual <= 19: tasa_retencion_allianz = 0.0618
        else: tasa_retencion_allianz = 0.0818
        
        saldo_neto_allianz = saldo_disponible * (1 - tasa_retencion_allianz)
        
        datos.append({
            "Mes Global": mes,
            "Año": anio_actual,
            "Edad": int(edad_actual),
            "Aportación Acumulada": acumulado_aportado,
            "Saldo de Fondo": saldo_total,
            "Saldo Disponible": saldo_disponible,
            "Saldo Disponible Neto": saldo_neto_disponible,
            "Post retención": saldo_neto_allianz,
            "Aportación": aportacion_periodo + monto_extra_mes, 
            "Bono": bono_mes,
            "Interés Generado": interes_total_mes,
            "Cargos": cargos_totales_mes,
            "Saldo Final": saldo_total # Alias para compatibilidad con gráficas anteriores
        })
        
    return pd.DataFrame(datos), bono_porcentaje

# --- NAVEGACIÓN PRINCIPAL ---
# Usamos un contenedor principal para simular pestañas en la pantalla principal
st.markdown("""
    <style>
    .nav-container {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 30px;
        border-bottom: 1px solid #6BA4A433;
        padding-bottom: 10px;
    }
    .nav-button {
        padding: 10px 20px;
        border-radius: 8px 8px 0 0;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.3s;
    }
    </style>
""", unsafe_allow_html=True)

if 'radio_seleccion_modulo' not in st.session_state:
    st.session_state.radio_seleccion_modulo = "📊 Simulador de Retiro"

# Selector en el tope de la pantalla (o sidebar)
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    seleccion = st.radio("Módulo Principal", ["📊 Simulador de Retiro", "✨ Nuevo Simulador"], label_visibility="collapsed", key="radio_seleccion_modulo")
    st.markdown("<hr style='margin: 10px 0; opacity: 0.1;'>", unsafe_allow_html=True)

if st.session_state.radio_seleccion_modulo == "✨ Nuevo Simulador":
    # --- PANTALLA NUEVO SIMULADOR ---
    logo_filename = "1-07.png" if is_dark else "1-01.png"
    logo_sidebar = get_asset_path(logo_filename)
    
    with st.sidebar:
        if os.path.exists(logo_sidebar):
            st.image(logo_sidebar, use_column_width=True)
        st.title("Configuración")
        st.subheader("Costo de Esperar")
        m_meta = st.session_state.get("meta_retiro_val", 10000000)
        meta_retiro = st.number_input(f"Meta de retiro (${m_meta:,.0f})", min_value=100000, value=m_meta, step=500000, format="%d", key="meta_retiro_val")
        edad_inicial = st.number_input("Edad a la que quieres empezar", min_value=18, max_value=70, value=18, step=1)
        edad_retiro = st.selectbox("Edad a la que te quieres retirar", [60, 65, 70, 75], index=0)
        rendimiento_anual = st.number_input("Rendimiento Anual Estimado (%)", min_value=1.0, value=10.0, step=0.5)

    logo_filename_dash = "1-08.png" if is_dark else "1-01-copy.png"
    logo_dash = get_asset_path(logo_filename_dash)
    if os.path.exists(logo_dash):
        bin_str_logo = get_base64_of_bin_file(logo_dash)
        st.markdown(f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-bottom: 30px; opacity: 0.8;">
                <img src="data:image/png;base64,{bin_str_logo}" style="width: 150px; margin-bottom: 10px;">
                <h1 class="white-title" style="margin: 0; padding: 0; line-height: 1.0; font-weight: 700; letter-spacing: 2px; font-size: 3.5rem;">ASTOR SIMULADOR</h1>
                <h2 style="color: {ACCENT_COLOR};">EL COSTO DE ESPERAR</h2>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"<h3 style='text-align: center; color: {GOLD_COLOR};'>Para llegar a ${meta_retiro:,.2f} a los {edad_retiro} años</h3>", unsafe_allow_html=True)
    st.write("Esta tabla muestra cuánto tendría que aportar mensualmente una persona según la edad a la que comience a invertir, asumiendo un rendimiento constante.")
    
    # Lógica Matemática
    datos_tabla = []
    
    for edad in range(int(edad_inicial), int(edad_retiro)):
        años_inversion = edad_retiro - edad
        meses_inversion = años_inversion * 12
        tasa_mensual = (rendimiento_anual / 100.0) / 12.0
        
        if tasa_mensual > 0:
            aportacion_mensual = (meta_retiro * tasa_mensual) / (((1 + tasa_mensual) ** meses_inversion) - 1)
        else:
            aportacion_mensual = meta_retiro / meses_inversion
            
        aportacion_acumulada = aportacion_mensual * meses_inversion
        rendimientos_generados = meta_retiro - aportacion_acumulada
        
        datos_tabla.append({
            "Edad": edad,
            "Aportación Mensual": aportacion_mensual,
            "Aportación Acumulada": aportacion_acumulada,
            "Rendimiento": rendimientos_generados,
            "Suma Total": meta_retiro
        })
        
    if datos_tabla:
        df_espera = pd.DataFrame(datos_tabla)
        
        # Formatear la tabla usando pandas Styler y convertirla a HTML manual para evitar el quiebre del componente st.dataframe
        html_table = (
            df_espera.style
            .format({
                "Aportación Mensual": "${:,.2f}",
                "Aportación Acumulada": "${:,.2f}",
                "Rendimiento": "${:,.2f}",
                "Suma Total": "${:,.2f}",
                "Edad": "{:.0f}"
            })
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
</style>
<div class="tabla-espera" style="height: 400px; overflow-y: auto; border: 1px solid {BORDER_COLOR}; border-radius: 10px; background-color: {CARD_BG};">
{html_table}
</div>
""", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráfica de aportación requerida
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_espera["Edad"].astype(str).tolist(),
            y=df_espera["Aportación Mensual"].tolist(),
            marker_color=COLORES[3],
            name="Aportación Mensual"
        ))
        
        fig.update_layout(
            title=f"Aportación Mensual Requerida según Edad de Inicio",
            xaxis_title="Edad de Inicio",
            yaxis_title="Aportación Mensual ($)",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT_COLOR),
            margin=dict(t=50, b=40)
        )
        
        fig.update_yaxes(tickformat="$,.0f", gridcolor="rgba(128,128,128,0.2)", automargin=True)
        fig.update_xaxes(gridcolor="rgba(128,128,128,0.2)", automargin=True)
        
        st.plotly_chart(fig, use_container_width=True, theme=None)
        
    else:
        st.warning("La edad inicial debe ser menor a la edad de retiro.")

    st.stop() # Detenemos aquí para que no cargue el otro simulador

# --- CONTINÚA SIMULADOR DE RETIRO ORIGINAL ---
# --- SIDEBAR ---
with st.sidebar:
    # --- LOGO ---
    logo_filename = "1-07.png" if is_dark else "1-01.png"
    logo_sidebar = get_asset_path(logo_filename)
    try:
        if os.path.exists(logo_sidebar):
            st.image(logo_sidebar, use_column_width=True)
        else:
            st.markdown(f"""
                <div style="text-align: center; padding: 10px; border-bottom: 2px solid {COLORES[0]}; margin-bottom: 20px;">
                    <h2 style="color: {TEXT_COLOR}; margin:0;">ASTOR</h2>
                    <p style="color: #6b7280; font-size: 0.8rem; margin:0;">ASESORÍA FINANCIERA Y SEGUROS</p>
                </div>
            """, unsafe_allow_html=True)
    except Exception:
        pass

    st.title("Configuración")
    
    with st.expander("👤 Datos del Cliente", expanded=True):
        nombre = st.text_input("Nombre", "Cliente Ejemplo")
        edad = st.number_input("Edad Actual", 18, 70, 35)
        tipo_plan = st.selectbox("Tipo de Plan", ["Art. 93 (No Deducible)", "Art. 185 (Deducible)"])

    with st.expander("⚙️ Parámetros Globales", expanded=True):
        frecuencia_vista = st.selectbox("Vista de Tabla/Gráfica", ["Mensual", "Semestral", "Anual"], index=2)
        col_inf1, col_inf2 = st.columns(2)
        opcion_inflacion = col_inf1.selectbox("Inflación", ["Activada", "Desactivada"])
        inflacion_activa = True if opcion_inflacion == "Activada" else False
        tasa_inflacion = col_inf2.number_input("% Inflación", 0.0, 10.0, 4.0, 0.1)
        # CAMBIO: Default a 10.0%
        tasa_anual = st.number_input("Rendimiento Anual (%)", 1.0, 100.0, 10.0, 0.5) 
        isr = st.number_input("Retención ISR Final (%)", 0.0, 35.0, 20.0)

    # Lista para guardar detalles de bonos y configuración de escenarios
    escenarios_config = []
    detalles_bonos = []

    with st.expander("💰 Comparativa de Inversión", expanded=True):
        st.caption(f"Escenarios activos: {st.session_state.num_escenarios}/5")
        
        for i in range(st.session_state.num_escenarios):
            color = COLORES[i]
            st.markdown(f"<div style='color:{color}; font-weight:900; margin-bottom:2px;'>Escenario de inversión {i+1}</div>", unsafe_allow_html=True)
            val_defecto = 3000 + (i * 1000)
            
            # 1. Monto Inicial
            # ETIQUETA VIVO (Separador de miles)
            m_val = st.session_state.get(f"monto_{i}", float(val_defecto))
            st.markdown(f"<div style='font-size: 0.85rem; font-weight: 900; color: {color}; margin-bottom: -15px;'> ${m_val:,.0f}</div>", unsafe_allow_html=True)
            monto = st.number_input(f"Monto Mensual {i+1}", min_value=2000, value=val_defecto, step=500, key=f"monto_{i}", label_visibility="collapsed")
            
            # 2. Checkbox para cambio en mes 19
            usar_cambio_m19 = st.checkbox(f"Modificar a partir del Mes 19", key=f"chk_m19_{i}")
            monto_m19 = None
            if usar_cambio_m19:
                # ETIQUETA VIVO M19
                m19_val = st.session_state.get(f"val_m19_{i}", float(monto))
                st.markdown(f"<div style='font-size: 0.8rem; font-weight: 800; color: {ACCENT_COLOR}; margin-bottom: -15px;'>Nuevo Monto: ${m19_val:,.0f}</div>", unsafe_allow_html=True)
                monto_m19 = st.number_input(f"Nuevo Monto Mes 19+ (Escenario de inversión {i+1})", min_value=2000, value=monto, step=500, key=f"val_m19_{i}")
            
            # Guardar configuración para cálculo posterior
            escenarios_config.append({
                "monto_inicial": monto,
                "monto_mes_19": monto_m19
            })
            
            # Calcular bono para mostrarlo en el siguiente cuadro
            bono_calc = obtener_porcentaje_bono(monto)
            bono_dinero = (monto * 12) * bono_calc
            detalles_bonos.append({
                "opcion": i + 1,
                "color": color,
                "pct": bono_calc,
                "monto": bono_dinero
            })
            
            st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
            
        c_add, c_del = st.columns(2)
        with c_add:
            if st.session_state.num_escenarios < 5: st.button("➕ Agregar", on_click=agregar_escenario)
            else: st.button("➕ Max", disabled=True)
        with c_del:
            if st.session_state.num_escenarios > 1: st.button("➖ Quitar", on_click=quitar_escenario)
            else: st.button("➖ Min", disabled=True)

    # --- NUEVA SECCIÓN DE APORTACIONES EXTRA ---
    with st.expander("💰 Aportaciones Extraordinarias"):
        st.caption("Proyecta ingresos adicionales (aguinaldos, bonos, ventas).")
        
        # Formulario para agregar
        # Opciones para el select: "Todas" + "Escenario de inversión 1", "Escenario de inversión 2", etc.
        opciones_disponibles = ["Todas"] + [f"Escenario de inversión {i+1}" for i in range(st.session_state.num_escenarios)]
        
        c_opc, c_monto = st.columns([1, 1])
        sel_opcion = c_opc.selectbox("Aplicar a:", opciones_disponibles)
        # ETIQUETA VIVO EXTRA
        ex_val = st.session_state.get("val_extra", 10000.0)
        c_monto.markdown(f"<div style='font-size: 0.8rem; font-weight: bold; color: {TEXT_COLOR}; margin-bottom: -15px;'>${ex_val:,.0f}</div>", unsafe_allow_html=True)
        val_extra = c_monto.number_input("Monto ($)", min_value=0.0, value=10000.0, step=1000.0, key="val_extra")
        
        sel_freq = st.selectbox("Frecuencia", ["Única vez", "Anual (Todos los años)"])
        
        anios_to_add = []
        meses_to_add = []
        dict_montos = {} # Para guardar montos por mes
        
        if sel_freq == "Única vez":
            c_anio, c_mes = st.columns(2)
            sel_anio = c_anio.number_input("Año del Plan", 1, 25, 1)
            sel_mes = c_mes.number_input("Mes del Año", 1, 12, 12)
            anios_to_add = [sel_anio]
            meses_to_add = [sel_mes]
            dict_montos[sel_mes] = val_extra
        else:
            meses_to_add = st.multiselect("Meses del Año", 
                                          options=list(range(1, 13)), 
                                          default=[12],
                                          format_func=lambda x: ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"][x-1])
            anios_to_add = list(range(1, 26))
            
            if meses_to_add:
                st.markdown("<div style='font-size: 0.85rem; font-weight: bold; margin-bottom: 5px;'>Montos por mes:</div>", unsafe_allow_html=True)
                # Mostrar inputs en 2 columnas para que no ocupen tanto espacio vertical
                m_cols = st.columns(2)
                for i, m in enumerate(sorted(meses_to_add)):
                    nom_mes_largo = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"][m-1]
                    with m_cols[i % 2]:
                        # ETIQUETA VIVO BULK
                        bulk_val = st.session_state.get(f"bulk_m_{m}", float(val_extra))
                        st.markdown(f"<div style='font-size: 0.8rem; font-weight: bold; color: {TEXT_COLOR}; margin-bottom: -15px;'>${bulk_val:,.0f}</div>", unsafe_allow_html=True)
                        dict_montos[m] = st.number_input(f"{nom_mes_largo}", min_value=0.0, value=val_extra, step=1000.0, key=f"bulk_m_{m}")
        
        if st.button("➕ Agregar Aportación Extra"):
            if not meses_to_add:
                st.error("Debes seleccionar al menos un mes.")
            else:
                # Convertir la selección de texto a ID (1, 2, 3... o "Todas")
                op_id = "Todas" if sel_opcion == "Todas" else int(sel_opcion.split(" ")[-1])
                
                # Agregar para cada año y mes seleccionado con su monto correspondiente
                for a in anios_to_add:
                    for m in meses_to_add:
                        monto_m = dict_montos.get(m, val_extra)
                        agregar_extra(op_id, a, m, monto_m)
                st.rerun()

        # Listado de extras agregadas
        if st.session_state.aportaciones_extra:
            st.markdown("---")
            st.markdown("**Extras Agregadas:**")
            for idx, ex in enumerate(st.session_state.aportaciones_extra):
                target = "Todas las opciones" if ex['opcion'] == "Todas" else f"Escenario de inversión {ex['opcion']}"
                st.markdown(f"""
                <div style="font-size: 0.8rem; padding: 5px; border-bottom: 1px solid #eee;">
                    <b>${ex['monto']:,.0f}</b> en Año {ex['anio']}, Mes {ex['mes']} <br>
                    <span style="color: #6b7280;">({target})</span>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("🗑️ Borrar Todas"):
                borrar_extras()

# --- PROCESAMIENTO ---
resultados = []
resultados_65 = [] 

eje_x_data_col = "Año" 
x_axis_title = "Año"

anios_para_65 = max(65 - edad, 25)

for idx, config in enumerate(escenarios_config):
    opcion_actual_id = idx + 1
    monto_inicial = config["monto_inicial"]
    monto_mes_19 = config["monto_mes_19"]
    
    # 1. Cálculo PRINCIPAL (25 años)
    df_raw, bono_pct = calcular_escenario(
        monto_inicial, edad, tasa_anual, inflacion_activa, tasa_inflacion, isr, 
        plazo_anos=25, 
        opcion_id=opcion_actual_id, 
        extras=st.session_state.aportaciones_extra,
        monto_mes_19=monto_mes_19 # Pasamos el nuevo parámetro
    )
    
    # 2. Cálculo RETIRO A LOS 65
    df_65, _ = calcular_escenario(
        monto_inicial, edad, tasa_anual, inflacion_activa, tasa_inflacion, isr, 
        plazo_anos=anios_para_65,
        opcion_id=opcion_actual_id, 
        extras=st.session_state.aportaciones_extra,
        monto_mes_19=monto_mes_19 # Pasamos el nuevo parámetro también aquí
    )
    
    # Pre-calcular Aportación Anual (Total del año actual para cada fila)
    df_raw['Aportación Anual'] = df_raw.groupby('Año')['Aportación'].transform('sum')
    df_65['Aportación Anual'] = df_65.groupby('Año')['Aportación'].transform('sum')

    # --- LOGICA DE AGRUPACIÓN ---
    if frecuencia_vista == "Mensual":
        df_display = df_raw.copy()
        eje_x_data_col = "Mes Global"
        x_axis_title = "Meses"
    elif frecuencia_vista == "Semestral":
        df_raw["Semestre"] = (df_raw["Mes Global"] - 1) // 6 + 1
        df_display = df_raw.groupby("Semestre").agg({
            "Año": "last", "Edad": "max",
            "Aportación Anual": "max", 
            "Aportación Acumulada": "last",
            "Saldo de Fondo": "last",
            "Saldo Disponible": "last",
            "Saldo Disponible Neto": "last",
            "Post retención": "last"
        }).reset_index()
        eje_x_data_col = "Semestre"
        x_axis_title = "Semestres"
    else: # Anual
        df_display = df_raw.groupby("Año").agg({
            "Edad": "max", 
            "Aportación Anual": "max",
            "Aportación Acumulada": "last",
            "Saldo de Fondo": "last",
            "Saldo Disponible": "last",
            "Saldo Disponible Neto": "last",
            "Post retención": "last"
        }).reset_index()
        eje_x_data_col = "Año"
        x_axis_title = "Años"

    resultados.append({
        "id": opcion_actual_id, "monto_inicial": monto_inicial, "color": COLORES[idx],
        "df_display": df_display, 
        "df_65_display": None, # Se llenará si aplica
        "saldo_final": df_display.iloc[-1]["Post retención"], "bono_pct": bono_pct,
        "monto_mes_19": monto_mes_19 
    })
    
    # --- LOGICA DE AGRUPACIÓN PARA 65 AÑOS (Si aplica) ---
    if edad <= 39:
        if frecuencia_vista == "Anual":
            df_65_display = df_65.groupby("Año").agg({
                "Edad": "max", "Aportación Anual": "max", "Aportación Acumulada": "last",
                "Saldo de Fondo": "last", "Saldo Disponible": "last", "Post retención": "last"
            }).reset_index()
        elif frecuencia_vista == "Semestral":
            df_65["Semestre"] = (df_65["Mes Global"] - 1) // 6 + 1
            df_65_display = df_65.groupby("Semestre").agg({
                "Año": "last", "Edad": "max", "Aportación Anual": "max", "Aportación Acumulada": "last",
                "Saldo de Fondo": "last", "Saldo Disponible": "last", "Post retención": "last"
            }).reset_index()
        else: # Mensual
            df_65_display = df_65.copy()
            
        resultados[-1]["df_65_display"] = df_65_display

    saldo_65 = df_65.iloc[-1]["Saldo Final"]
    aportado_65 = df_65.iloc[-1]["Aportación Acumulada"]
    resultados_65.append({
        "id": opcion_actual_id, "monto_inicial": monto_inicial, "color": COLORES[idx],
        "saldo_final_65": saldo_65,
        "total_aportado_65": aportado_65,
        "rendimiento_65": saldo_65 - aportado_65,
        "monto_mes_19": monto_mes_19 
    })

# --- DASHBOARD ---
logo_filename_dash = "1-08.png" if is_dark else "1-01-copy.png"
logo_dash = get_asset_path(logo_filename_dash)
if os.path.exists(logo_dash):
    bin_str_logo = get_base64_of_bin_file(logo_dash)
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&display=swap');
        </style>
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-bottom: 30px;">
            <img src="data:image/png;base64,{bin_str_logo}" style="width: 180px; margin-bottom: 20px;">
            <h1 class="white-title" style="margin: 0; padding: 0; line-height: 1.0; font-weight: 700; letter-spacing: 2px; font-size: 4.5rem;">ASTOR SIMULADOR</h1>
        </div>
    """, unsafe_allow_html=True)
else:
    st.title("Simulador")
st.markdown(f"Proyección para <span style='color: {TEXT_COLOR}; font-size: 1.2rem; font-weight: bold;'>{nombre.title()}</span> | Plan: **{tipo_plan}**", unsafe_allow_html=True)

# --- DASHBOARD UNIFICADO ---
# Columnas con divisores continuos (Reutilizaremos la especificación de columnas)
cols_spec = []
for i in range(len(resultados)):
    cols_spec.append(1)
    if i < len(resultados) - 1:
        cols_spec.append(0.05) 

# --- SECCIÓN 1: BONO DE BIENVENIDA ---
st.markdown(f'<h3 style="color: {TEXT_COLOR}; font-size: 2rem; text-align: center; margin-top: 20px; margin-bottom: 25px;">🎁 Bono de bienvenida</h3>', unsafe_allow_html=True)

cols_bono = st.columns(cols_spec)
for idx in range(len(resultados)):
    res = resultados[idx]
    with cols_bono[idx * 2]:
        # Buscar el bono correspondiente
        item_bono = next((b for b in detalles_bonos if b['opcion'] == res['id']), None)
        if item_bono:
            # Obtener el monto inicial del escenario para mostrarlo arriba como en las otras secciones
            monto_escenario = res['monto_inicial']
            st.markdown(f"""
            <div style="background-color: {CARD_BG}; border: 1px solid {item_bono['color']}; border-radius: 10px; padding: 20px; text-align: center; border-top: 5px solid {item_bono['color']}; box-shadow: 0 4px 15px rgba(0,0,0,{0.3 if is_dark else 0.1}); margin-bottom: 15px;">
            <h4 style="color: {item_bono['color']}; font-weight: bold; margin-bottom: 10px;">${monto_escenario:,.0f} Al mes</h4>
            <p style="color: {TEXT_COLOR if not is_dark else ACCENT_COLOR}; font-size: 1.0rem; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.7;">Bono acreditado:</p>
            <div style="color: {item_bono['color']}; font-size: 2.5rem; font-weight: bold; margin: 5px 0; text-shadow: {('0 0 10px ' + item_bono['color'] + '44') if is_dark else 'none'};">${item_bono['monto']:,.0f}</div>
            <div style="color: {item_bono['color']}; font-weight: bold; font-size: 1.15rem;">({item_bono['pct']*100:.0f}%)</div>
            <div style="color: {item_bono['color']}; font-size: 1.15rem; font-weight: bold; margin-top: 8px;">+${item_bono['monto']/12:,.0f} al mes</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="height: 120px;"></div>', unsafe_allow_html=True)
    
    # Divisor Bono (Altura ajustada)
    if idx < len(resultados) - 1:
        with cols_bono[idx * 2 + 1]:
            st.markdown(f"""
            <div style="display: flex; justify-content: center; gap: 6px; height: 160px; margin: 5px auto;">
            <div style="width: 2px; height: 100%; background-color: {res['color']}; border-radius: 10px; opacity: 0.4;"></div>
            <div style="width: 2px; height: 100%; background-color: {res['color']}; border-radius: 10px; opacity: 0.4;"></div>
            </div>
            """, unsafe_allow_html=True)

# --- SECCIÓN 2: 25 AÑOS ---
st.markdown(f'<h3 style="color: {TEXT_COLOR}; font-size: 2rem; text-align: center; margin-top: 30px; margin-bottom: 25px;">{edad + 25} años</h3>', unsafe_allow_html=True)

cols_25 = st.columns(cols_spec)
for idx in range(len(resultados)):
    res = resultados[idx]
    with cols_25[idx * 2]:
        # Logica 25 Años
        last_row = res['df_display'].iloc[-1]
        total_aportado = last_row['Aportación Acumulada']
        rendimiento = res['saldo_final'] - total_aportado
        
        monto_m19_val = res.get('monto_mes_19')
        texto_mes_19_25 = f"<div style='color: {GOLD_COLOR}; font-size: 0.85rem; margin-top:-2px; margin-bottom: 5px; height: 20px;'>{'Mes 19+: <b>$' + f'{monto_m19_val:,.0f}' + '</b>' if monto_m19_val is not None else ''}</div>"

        st.markdown(f"""
        <div style="background-color: {CARD_BG}; border: 1px solid {res['color']}88; border-radius: 10px; padding: 25px 20px; text-align: center; border-top: 5px solid {res['color']}; box-shadow: 0 4px 15px rgba(0,0,0,{0.3 if is_dark else 0.1}); margin-bottom: 15px; min-height: 280px; display: flex; flex-direction: column;">
            <div style="flex: 0;">
                <h4 style="color: {res['color']}; font-weight: bold; margin-bottom: 5px;">${res['monto_inicial']:,.0f} Al mes</h4>
                {texto_mes_19_25}
            </div>
            <div style="flex: 1; display: flex; align-items: center; justify-content: center;">
                <div style="color: {res['color']}; font-size: 2.5rem; font-weight: bold; text-shadow: {('0 0 15px ' + res['color'] + '44') if is_dark else 'none'};">${res['saldo_final']:,.0f}</div>
            </div>
            <div style="flex: 0; margin-top: 20px; border-top: 1px solid {ACCENT_COLOR if is_dark else BORDER_COLOR}; padding-top: 10px; font-size: 1.0rem;">
                <div style="color: {TEXT_COLOR}; font-weight: bold;">Aportado: ${total_aportado:,.0f}</div>
                <div style="color: {res['color']}; font-weight: bold;">Rendimiento: +${rendimiento:,.0f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Divisor 25 Años
    if idx < len(resultados) - 1:
        with cols_25[idx * 2 + 1]:
            st.markdown(f"""
            <div style="display: flex; justify-content: center; gap: 6px; height: 320px; margin: 5px auto;">
            <div style="width: 2px; height: 100%; background-color: {res['color']}; border-radius: 10px; opacity: 0.4;"></div>
            <div style="width: 2px; height: 100%; background-color: {res['color']}; border-radius: 10px; opacity: 0.4;"></div>
            </div>
            """, unsafe_allow_html=True)

# --- SECCIÓN 3: RETIRO ---
proy_edad_retiro = edad + anios_para_65
st.markdown(f'<h3 style="color: {TEXT_COLOR}; font-size: 2rem; text-align: center; margin-top: 30px; margin-bottom: 25px;">{proy_edad_retiro} años</h3>', unsafe_allow_html=True)

cols_retiro = st.columns(cols_spec)
for idx in range(len(resultados)):
    res = resultados[idx]
    r65 = resultados_65[idx]
    with cols_retiro[idx * 2]:
        monto_m19_val_retiro = r65.get('monto_mes_19')
        texto_mes_19 = f"<div style='color: {GOLD_COLOR}; font-size: 0.85rem; margin-top:-2px; margin-bottom: 5px; height: 20px;'>{'Mes 19+: <b>$' + f'{monto_m19_val_retiro:,.0f}' + '</b>' if monto_m19_val_retiro is not None else ''}</div>"

        st.markdown(f"""
        <div style="background-color: {CARD_BG}; border: 1px solid {r65['color']}88; border-radius: 10px; padding: 25px 20px; text-align: center; border-top: 5px solid {r65['color']}; box-shadow: 0 4px 15px rgba(0,0,0,{0.3 if is_dark else 0.1}); min-height: 280px; display: flex; flex-direction: column;">
            <div style="flex: 0;">
                <h4 style="color: {r65['color']}; font-weight: bold; margin-bottom: 5px;">${r65['monto_inicial']:,.0f} Al mes</h4>
                {texto_mes_19}
            </div>
            <div style="flex: 1; display: flex; align-items: center; justify-content: center;">
                <div style="color: {r65['color']}; font-size: 2.5rem; font-weight: bold; text-shadow: {('0 0 15px ' + r65['color'] + '44') if is_dark else 'none'};">${r65['saldo_final_65']:,.0f}</div>
            </div>
            <div style="flex: 0; margin-top: 20px; border-top: 1px solid {ACCENT_COLOR if is_dark else BORDER_COLOR}; padding-top: 10px; font-size: 1.0rem;">
                <div style="color: {TEXT_COLOR};">Aportado: <b>${r65['total_aportado_65']:,.0f}</b></div>
                <div style="color: {r65['color']}; font-weight: bold;">Rendimiento: +${r65['rendimiento_65']:,.0f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Divisor Retiro
    if idx < len(resultados) - 1:
        with cols_retiro[idx * 2 + 1]:
            st.markdown(f"""
            <div style="display: flex; justify-content: center; gap: 6px; height: 320px; margin: 5px auto;">
            <div style="width: 2px; height: 100%; background-color: {res['color']}; border-radius: 10px; opacity: 0.4;"></div>
            <div style="width: 2px; height: 100%; background-color: {res['color']}; border-radius: 10px; opacity: 0.4;"></div>
            </div>
            """, unsafe_allow_html=True)

st.write("---")
tabs_nombres = ["📊 Gráfica Comparativa", "📋 Tabla Dinámica"]
if edad <= 39:
    tabs_nombres.append(f"📋 Tabla Dinámica {edad + 25}-65")

tabs = st.tabs(tabs_nombres)
tab_grafica = tabs[0]
tab_tabla = tabs[1]
if edad <= 39:
    tab_tabla_65 = tabs[2]

with tab_grafica:
    st.subheader("Crecimiento de Capital en el Tiempo")
    fig = go.Figure()
    for res in resultados:
        fig.add_trace(go.Scatter(
            x=res["df_display"][eje_x_data_col].tolist(), 
            y=res["df_display"]["Saldo de Fondo"].tolist(),
            mode='lines', 
            name=f'<b>Escenario de inversión {res["id"]}</b>',
            line=dict(color=res["color"], width=3)
        ))
    fig.update_layout(
        xaxis_title=x_axis_title, 
        yaxis_title="Saldo Acumulado",
        hovermode="x unified", 
        template="plotly_dark", 
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        height=450,
        legend=dict(
            orientation="h", 
            y=1.1, 
            x=0.5, 
            xanchor="center",
            font=dict(family="Inter, sans-serif", size=16, color=TEXT_COLOR)
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=14, color=TEXT_COLOR),
        xaxis=dict(
            title=dict(text=f"<b>{x_axis_title}</b>", font=dict(family="Inter, sans-serif", size=18, color=ACCENT_COLOR)),
            tickfont=dict(family="Inter, sans-serif", size=15, color=TEXT_COLOR),
            gridcolor="#0a3a42"
        ),
        yaxis=dict(
            title=dict(text="<b>Saldo Acumulado</b>", font=dict(family="Inter, sans-serif", size=18, color=ACCENT_COLOR)),
            tickfont=dict(family="Inter, sans-serif", size=15, color=TEXT_COLOR),
            tickprefix="$",
            gridcolor="#0a3a42"
        )
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)


    def highlight_age_60(row):
        is_age_60 = row["Edad"] == 60
        # Regresando al verde suave que el usuario prefiere
        return ['background-color: #dcfce7 !important; color: #166534 !important; font-weight: bold !important;' if is_age_60 else '' for _ in row]

with tab_tabla:
    col_sel, col_dump = st.columns([1, 3])
    opciones_select = [r['id'] for r in resultados]
    id_seleccionado = col_sel.selectbox("Ver detalle de:", opciones_select, format_func=lambda x: f"Escenario de inversión {x}")
    seleccion = next(item for item in resultados if item["id"] == id_seleccionado)
    color_ver = seleccion["color"]
    
    st.markdown(f"<h4 style='color:{TEXT_COLOR}; text-align: center;'>Detalle {frecuencia_vista} - Escenario de inversión ${seleccion['monto_inicial']:,.0f}</h4>", unsafe_allow_html=True)
    
    # Columnas específicas solicitadas
    # ELIMINADA: "Saldo Disponible Neto"
    cols_to_show = ["Año", "Edad", "Aportación Anual", "Aportación Acumulada", "Saldo de Fondo", "Saldo Disponible", "Post retención"]
    
    # Si es mensual o semestral, añadimos la columna de periodo
    if frecuencia_vista != "Anual":
        # Insertar al principio
        cols_to_show.insert(0, eje_x_data_col)
    # --- TABLA BONITA CON BARRAS DE PROGRESO ---
    # --- TABLA HTML PERSONALIZADA ---
    # Convertimos a HTML para tener control TOTAL del estilo y evitar el fondo blanco de Streamlit
    html_table = (
        seleccion["df_display"][cols_to_show].style
        .format({
            "Aportación Anual": "${:,.0f}",
            "Aportación Acumulada": "${:,.0f}", 
            "Saldo de Fondo": "${:,.0f}", 
            "Saldo Disponible": "${:,.0f}", 
            "Post retención": "${:,.0f}",
            "Año": "{:.0f}", 
            "Edad": "{:.0f}"
        })
        .apply(highlight_age_60, axis=1)
        .set_properties(**{'text-align': 'center'})
        .hide(axis="index")
        .to_html()
    )
    
    st.markdown(f"""
<div style="height: 500px; overflow-y: auto; border: 1px solid {BORDER_COLOR}; border-radius: 10px; background-color: {CARD_BG};">
{html_table}
</div>
""", unsafe_allow_html=True)

if edad <= 39:
    with tab_tabla_65:
        col_sel_65, col_dump_65 = st.columns([1, 3])
        id_sel_65 = col_sel_65.selectbox("Ver detalle extra de:", opciones_select, format_func=lambda x: f"Escenario de inversión {x}", key="sel_65")
        sel_65 = next(item for item in resultados if item["id"] == id_sel_65)
        
        st.markdown(f"<h4 style='color:{TEXT_COLOR}; text-align: center;'>Detalle edad {edad + 25} a 65 años - Escenario de inversión ${sel_65['monto_inicial']:,.0f}</h4>", unsafe_allow_html=True)
        
        df_65_show = sel_65["df_65_display"]
        # Filtrar solo periodos posteriores al año 25
        df_65_show = df_65_show[df_65_show["Año"] > 25]
        
        # --- TABLA HTML PERSONALIZADA (65 años) ---
        html_table_65 = (
            df_65_show[cols_to_show].style
            .format({
                "Aportación Anual": "${:,.0f}",
                "Aportación Acumulada": "${:,.0f}", 
                "Saldo de Fondo": "${:,.0f}", 
                "Saldo Disponible": "${:,.0f}", 
                "Post retención": "${:,.0f}",
                "Año": "{:.0f}", 
                "Edad": "{:.0f}"
            })
            .apply(highlight_age_60, axis=1)
            .set_properties(**{'text-align': 'center'})
            .hide(axis="index")
            .to_html()
        )
        
        st.markdown(f"""
<div style="height: 500px; overflow-y: auto; border: 1px solid {BORDER_COLOR}; border-radius: 10px; background-color: {CARD_BG};">
{html_table_65}
</div>
""", unsafe_allow_html=True)


# 3. EXPORTACIÓN CSV


# 3. EXPORTACIÓN CSV
# 3. EXPORTACIÓN EXCEL PROFESIONAL (Multi-Hoja)
def generar_excel(res_list, nombre_cte):
    output = io.BytesIO()
    # Usaremos xlsxwriter obligatoriamente para el formato avanzado
    try:
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
    except:
        # Fallback básico si explota algo o no está instalado
        writer = pd.ExcelWriter(output, engine='openpyxl')
        
    workbook = writer.book
    
    # ---------------------------------------------------------
    # MODO IMPORTANTE: SI NO TENEMOS XLSXWRITER, MODO SIMPLE
    # ---------------------------------------------------------
    if writer.engine != 'xlsxwriter':
        # Exportación simple para evitar errores
        for r in res_list:
            cols_export_basic = ["Año", "Edad", "Aportación Anual", "Aportación Acumulada", "Saldo de Fondo", "Saldo Disponible", "Post retención"]
            if frecuencia_vista != "Anual": cols_export_basic.insert(0, eje_x_data_col)
            r['df_display'][cols_export_basic].to_excel(writer, sheet_name=f"Escenario {r['id']}", index=False)
        writer.close()
        return output.getvalue()

    # --- SÍ TENEMOS XLSXWRITER: FORMATOS AVANZADOS ---
    
    # --- CONFIGURACIÓN DINÁMICA DE COLORES EXCEL ---
    if is_dark:
        COLOR_FONDO = '#050505'       # Negro Profundo
        COLOR_GRADIENTE_1 = '#092B30' # Petrol Oscuro
        COLOR_GRADIENTE_2 = '#050505' # Transición a Negro
        COLOR_TEXTO_MAIN = '#FFFFFF'  # Blanco
        COLOR_ORO = '#E6C200'         # Oro Atenuado
        COLOR_ACCENTO = '#1a3a42'     # Cian Oscuro
        BORDER_EXCEL = COLOR_ORO
        HEADER_BG = COLOR_GRADIENTE_1
        LOGO_FILE = "1-06.png"
    else:
        # Modo Claro (Identidad Astor Original)
        COLOR_FONDO = '#FFFFFF'       # Blanco Puro
        COLOR_GRADIENTE_1 = '#1E3A8A' # Azul Astor (Primary)
        COLOR_GRADIENTE_2 = '#FFFFFF' 
        COLOR_TEXTO_MAIN = '#FFFFFF'  # Para textos sobre fondo azul
        COLOR_TEXTO_DARK = '#1E3A8A'  # Para textos sobre fondo blanco
        COLOR_ORO = '#1E3A8A'         # Azul Marino en lugar de Oro en claro
        COLOR_ACCENTO = '#F0F2F5'     # Gris suave de fondo
        BORDER_EXCEL = '#1E3A8A'
        HEADER_BG = '#1E3A8A'
        LOGO_FILE = "1-06 copy.png"
    
    # --- ESTILOS COMPLEJOS (BOXED DESIGN) ---
    # Título Principal con Color Sólido Premium
    fmt_title_main = workbook.add_format({
        'bold': True, 'font_size': 24, 'font_color': COLOR_TEXTO_MAIN,
        'bg_color': HEADER_BG,
        'align': 'center', 'valign': 'vcenter', 'border': 2, 'border_color': BORDER_EXCEL,
        'font_name': 'Georgia'
    })
    
    # Título de Escenario (Borde Oro, Texto Blanco)
    fmt_title_scenario = workbook.add_format({
        'bold': True, 'font_size': 18, 'font_color': COLOR_TEXTO_MAIN,
        'bg_color': HEADER_BG,
        'align': 'center', 'valign': 'vcenter', 'border': 2, 'border_color': BORDER_EXCEL,
        'text_wrap': True,
        'font_name': 'Georgia'
    })
    
    # Encabezados de Sección (Totalmente transparente para ver marca de agua)
    fmt_section_header = workbook.add_format({
        'bold': True, 'font_size': 14, 'font_color': COLOR_TEXTO_MAIN, 
        'bg_color': HEADER_BG,
        'align': 'center', 'valign': 'vcenter', 'border': 2, 'border_color': BORDER_EXCEL
    })
    
    fmt_box_label = workbook.add_format({
        'font_size': 11, 'font_color': '#64748B' if not is_dark else '#9ca3af', 'align': 'center', 'valign': 'top', 'bold': True,
        'bg_color': COLOR_FONDO
    })
    
    fmt_box_data = workbook.add_format({
        'font_size': 16, 'font_color': COLOR_TEXTO_DARK if not is_dark else COLOR_TEXTO_MAIN, 'align': 'center', 'valign': 'vcenter',
        'border': 2, 'border_color': BORDER_EXCEL, 'bold': True
    })
    
    fmt_box_data_currency = workbook.add_format({
        'font_size': 16, 'font_color': COLOR_TEXTO_DARK if not is_dark else COLOR_TEXTO_MAIN, 'align': 'center', 'valign': 'vcenter',
        'border': 2, 'border_color': BORDER_EXCEL, 'bold': True, 'num_format': '$#,##0'
    })
    
    # NUEVO: Formato específico para la fila del cliente (Dorado en oscuro)
    fmt_client_info = workbook.add_format({
        'font_size': 16, 'font_color': COLOR_ORO if is_dark else COLOR_TEXTO_DARK, 'align': 'center', 'valign': 'vcenter',
        'border': 2, 'border_color': BORDER_EXCEL, 'bold': True
    })

    # Encabezado de Tabla Principal (Transparente, Texto Blanco, Borde Oro)
    fmt_header_table = workbook.add_format({
        'bold': True, 'font_size': 12, 'font_color': COLOR_TEXTO_MAIN,
        'bg_color': HEADER_BG,
        'border': 1, 'border_color': BORDER_EXCEL, 'align': 'center', 'valign': 'vcenter'
    })
    
    # Celdas de Datos (Sin bg_color para que la marca de agua sea visible "dentro")
    fmt_cell_text = workbook.add_format({'font_size': 12, 'border': 1, 'border_color': BORDER_EXCEL, 'align': 'center', 'font_color': COLOR_TEXTO_DARK if not is_dark else COLOR_TEXTO_MAIN})
    fmt_cell_num = workbook.add_format({'font_size': 12, 'border': 1, 'border_color': BORDER_EXCEL, 'align': 'center', 'font_color': COLOR_TEXTO_DARK if not is_dark else COLOR_TEXTO_MAIN})
    fmt_cell_currency = workbook.add_format({'font_size': 12, 'border': 1, 'border_color': BORDER_EXCEL, 'align': 'center', 'num_format': '$#,##0', 'font_color': COLOR_TEXTO_DARK if not is_dark else COLOR_TEXTO_MAIN})
    
    # Formatos con Highlight (Edad 60) - Manteniendo el verde suave para legibilidad sobre el oscuro
    fmt_cell_text_highlight = workbook.add_format({'font_size': 12, 'border': 1, 'align': 'center', 'bg_color': '#dcfce7', 'font_color': '#166534', 'bold': True})
    fmt_cell_num_highlight = workbook.add_format({'font_size': 12, 'border': 1, 'align': 'center', 'bg_color': '#dcfce7', 'font_color': '#166534', 'bold': True})
    fmt_cell_currency_highlight = workbook.add_format({'font_size': 12, 'border': 1, 'align': 'center', 'num_format': '$#,##0', 'bg_color': '#dcfce7', 'font_color': '#166534', 'bold': True})

    fmt_bold_label = workbook.add_format({'bold': True, 'font_size': 12, 'font_color': BORDER_EXCEL, 'bg_color': COLOR_FONDO})
    
    # --- HOJA 1: PORTADA / RESUMEN EJECUTIVO ---
    ws_portada = workbook.add_worksheet("Portada")
    ws_portada.hide_gridlines(2) # Ocultar gridlines para que brille el fondo oscuro
    
    # --- MARCA DE AGUA ---
    watermark_file = get_watermark_excel(is_dark=is_dark)
    if watermark_file:
        ws_portada.set_background(watermark_file)
    
    # --- PROTECCIÓN ---
    # Bloquear objetos (logo) para que no se puedan mover o borrar
    ws_portada.protect()

    # --- CONFIGURACIÓN DE ESPACIOS (Garantizar que nada se vea aplastado) ---
    for r_idx in range(0, 10):
        ws_portada.set_row(r_idx, 25) # Altura generosa para la cabecera
    
    # --- SECCIÓN 0: CABECERA Y LOGO ---
    logo_portada = get_asset_path(LOGO_FILE)
    if os.path.exists(logo_portada):
        # Logo en esquina A1/B1 con escala clara
        ws_portada.insert_image('A1', logo_portada, {'x_scale': 0.10, 'y_scale': 0.10, 'x_offset': 15, 'y_offset': 10, 'object_positioned': 1})

    # Título Principal centrado respecto a la zona de datos
    ws_portada.merge_range('D3:F6', "Astor simulador", fmt_title_main)
    
    # --- SECCIÓN 1: DATOS DEL CLIENTE ---
    row = 25 # MÁXIMO AIRE: Bajamos hasta la fila 25 para que nada se encime
    ws_portada.merge_range(row, 1, row, 6, "Información del Cliente", fmt_section_header)
    row += 2
    
    # Fila de etiquetas
    ws_portada.merge_range(row, 1, row, 2, "Nombre del Cliente", fmt_box_label) # Merge para que quepa el label
    ws_portada.merge_range(row, 3, row, 5, "Plan Seleccionado", fmt_box_label)
    ws_portada.write(row, 6, "Edad Actual", fmt_box_label)
    row += 1
    
    # Fila de valores (Boxed)
    ws_portada.set_row(row, 45) 
    # MERGE para el nombre del cliente para que no se corte NUNCA
    ws_portada.merge_range(row, 1, row, 2, nombre_cte.title(), fmt_client_info)
    ws_portada.merge_range(row, 3, row, 5, tipo_plan, fmt_client_info)
    ws_portada.write(row, 6, f"{edad} años", fmt_client_info)
    
    # --- SECCIÓN 3: RESUMEN COMPARATIVO ---
    row += 6 
    ws_portada.merge_range(row, 1, row, 6, "Resumen de Escenarios Proyectados", fmt_section_header)
    
    # Aplicar a Portada (hasta fila 80 para cubrir todo el resumen)
    # Ya no se requiere aplicar_patron_watermark manual
    row += 2
    
    # Encabezados Tabla Resumen
    headers_res = ["Escenario De Inversión", "Aportación Mensual", "Aportación Mes 19+", "Saldo Final", "Bono Inicial"]
    for col, h in enumerate(headers_res):
        ws_portada.write(row, 1 + col, h, fmt_header_table)
    
    # Filas Tabla Resumen
    row += 1
    for r in res_list:
        ws_portada.set_row(row, 20)
        ws_portada.write(row, 1, f"Escenario {r['id']}", fmt_cell_text)
        ws_portada.write(row, 2, r['monto_inicial'], fmt_cell_currency)
        
        # Monto Mes 19
        if r.get('monto_mes_19') and r['monto_mes_19'] > 0:
             ws_portada.write(row, 3, r['monto_mes_19'], fmt_cell_currency)
        else:
             ws_portada.write(row, 3, "-", fmt_cell_text)

        ws_portada.write(row, 4, r['saldo_final'], fmt_cell_currency)
        ws_portada.write(row, 5, f"{r['bono_pct']*100:.0f}%", fmt_cell_num)
        row += 1
        
    # Ajustar anchos Portada (Más grandes y centrados)
    ws_portada.set_column(0, 0, 5)   # A: Margen
    ws_portada.set_column(1, 1, 25)  # B: Escenario (Widen from 15)
    ws_portada.set_column(2, 2, 25)  # C
    ws_portada.set_column(3, 3, 25)  # D
    ws_portada.set_column(4, 4, 30)  # E
    ws_portada.set_column(5, 5, 20)  # F
    ws_portada.set_column(6, 6, 20)  # G
    
    # Ocultar sobrante en Portada para efecto Dashboard limpio
    ws_portada.set_column('H:XFD', None, None, {'hidden': True})
    ws_portada.set_default_row(hide_unused_rows=True) 
    ws_portada.write(row + 2, 1, "") 


    # ---------------------------------------------------------
    # HOJAS DE DETALLE (UNA POR OPCIÓN)
    # ---------------------------------------------------------
    cols_export = ["Año", "Edad", "Aportación Acumulada", "Saldo de Fondo", "Saldo Disponible", "Post retención"]
    if frecuencia_vista != "Anual": cols_export.insert(0, eje_x_data_col)
    
    for r in res_list:
        sh_name = f"Escenario {r['id']}"
        ws_detail = workbook.add_worksheet(sh_name)
        ws_detail.hide_gridlines(2)
        if watermark_file:
            ws_detail.set_background(watermark_file)
        ws_detail.protect() # Bloquear el logo

        # --- AJUSTE DE ESPACIOS (Igual que la Portada) ---
        for r_idx in range(0, 10):
            ws_detail.set_row(r_idx, 22) # Altura balanceada para cabecera
            
        # --- LOGO EN ESCENARIOS ---
        logo_escenario = get_asset_path(LOGO_FILE)
        if os.path.exists(logo_escenario):
            # Logo en esquina A1 como en Portada
            ws_detail.insert_image('A1', logo_escenario, {'x_scale': 0.10, 'y_scale': 0.10, 'x_offset': 15, 'y_offset': 10, 'object_positioned': 1})
        
        # Título de la Hoja (Dos líneas: Título arriba, cifra abajo)
        ws_detail.merge_range('D3:E5', f"PROYECCIÓN:\n${r['monto_inicial']:,.0f}", fmt_title_scenario)
        
        # Cajas de resumen rápido (Buscamos balance - Fila 12)
        row_brief = 12
        ws_detail.write(row_brief, 1, "Aportación Mensual", fmt_box_label)
        ws_detail.write(row_brief, 2, "Aportación 19+", fmt_box_label)
        ws_detail.write(row_brief, 3, "Saldo Final Estimado", fmt_box_label)
        
        row_brief += 1
        ws_detail.set_row(row_brief, 40)
        ws_detail.write(row_brief, 1, r['monto_inicial'], fmt_box_data_currency)
        m19_val = r.get('monto_mes_19') if r.get('monto_mes_19') else r['monto_inicial']
        ws_detail.write(row_brief, 2, m19_val, fmt_box_data_currency)
        ws_detail.write(row_brief, 3, r['saldo_final'], fmt_box_data_currency)
        
        # Espacio final antes de la tabla (Suficiente respiro - Fila 20)
        start_row = 20

        
        # Escribir Headers
        for col_num, value in enumerate(cols_export):
            ws_detail.write(start_row, col_num, value, fmt_header_table)

        # Escribir Datos
        data_row = start_row + 1
        df_display = r['df_display'][cols_export]
        
        def write_rows(ws, df, start_r):
            curr_r = start_r
            for _, row_data in df.iterrows():
                is_age_60 = row_data.get("Edad") == 60
                
                for col_num, col_name in enumerate(cols_export):
                    val = row_data[col_name]
                    
                    if col_name in ["Aportación Acumulada", "Saldo de Fondo", "Saldo Disponible", "Post retención"]:
                        fmt = fmt_cell_currency_highlight if is_age_60 else fmt_cell_currency
                        ws.write(curr_r, col_num, val, fmt)
                    elif col_name in ["Año", "Edad"]:
                        fmt = fmt_cell_num_highlight if is_age_60 else fmt_cell_num
                        ws.write(curr_r, col_num, val, fmt)
                    else:
                        fmt = fmt_cell_text_highlight if is_age_60 else fmt_cell_text
                        ws.write(curr_r, col_num, val, fmt)
                curr_r += 1
            return curr_r

        data_row = write_rows(ws_detail, df_display, data_row)
            
        # --- TABLA EXTRA (25-65) SI EXISTE ---
        if r.get('df_65_display') is not None:
            data_row += 2
            ws_detail.merge_range(data_row, 0, data_row, len(cols_export) - 1, f"Proyección a Retiro (Edad {edad + 25} a 65)", fmt_section_header)
            data_row += 1
            # Headers otra vez
            for col_num, value in enumerate(cols_export):
                ws_detail.write(data_row, col_num, value, fmt_header_table)
            data_row += 1
            
            df_65_export = r['df_65_display'][r['df_65_display']["Año"] > 25][cols_export]
            data_row = write_rows(ws_detail, df_65_export, data_row)
            
            
        # Ajustar anchos Detalle (Más cómodos)
        ws_detail.set_column(0, 0, 20)  # A: Logo / Col 1
        ws_detail.set_column(1, 1, 12)  # B
        ws_detail.set_column(2, 2, 25)  # C
        ws_detail.set_column(3, 3, 25)  # D
        ws_detail.set_column(4, 4, 25)  # E
        ws_detail.set_column(5, 5, 25)  # F
        
        # Ocultar sobrante en Escenarios
        last_col_letter = chr(ord('A') + len(cols_export))
        ws_detail.set_column(f'{last_col_letter}:XFD', None, None, {'hidden': True})
        ws_detail.set_default_row(hide_unused_rows=True)
        ws_detail.write(data_row + 2, 0, "")

    writer.close()
    return output.getvalue()

excel_data = generar_excel(resultados, nombre)
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
st.download_button(
    label="💾 Descargar Reporte (Excel)",
    data=excel_data,
    file_name=f"Simulacion_{nombre.replace(' ', '_')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
