import io
import os
from fpdf import FPDF

class AstorPDF(FPDF):
    def __init__(self, is_dark=True):
        super().__init__()
        self.is_dark = is_dark
        # Colores principales de la aplicación Astor
        if is_dark:
            self.custom_bg_color = (11, 15, 25)      # Fondo principal (#0b0f19)
            self.custom_text_color = (255, 255, 255) # Texto blanco
            self.custom_accent_color = (212, 175, 55)# Dorado (#D4AF37)
            self.custom_card_bg = (30, 40, 50)       # Fondo de tarjetas
            self.custom_border_color = (60, 70, 80)  # Bordes sutiles
        else:
            self.custom_bg_color = (255, 255, 255)   # Blanco
            self.custom_text_color = (30, 40, 50)    # Texto oscuro
            self.custom_accent_color = (180, 140, 40)# Dorado oscuro
            self.custom_card_bg = (245, 245, 245)    # Fondo de tarjetas claro
            self.custom_border_color = (200, 200, 200)

    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(*self.custom_border_color)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    if len(hex_str) != 6:
        return (200, 200, 200)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def generar_pdf_reporte(nombre, tipo_plan, detalles_bonos, resultados, resultados_65, anios_horizonte, edad, anios_para_retiro, fig, is_dark=True):
    pdf = AstorPDF(is_dark)
    pdf.add_page()
    
    # Rellenar fondo
    if is_dark:
        pdf.set_fill_color(*pdf.custom_bg_color)
        pdf.rect(0, 0, 210, 297, 'F')

    # 1. Logo y Encabezado
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "1-08.png" if is_dark else "1-01.png")
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=85, y=10, w=40)
        pdf.set_y(50)
    else:
        pdf.set_y(20)
    
    pdf.set_font("helvetica", "B", 24)
    pdf.set_text_color(*pdf.custom_text_color)
    pdf.cell(0, 10, "SIMULADOR FINANCIERO", align="C", ln=True)
    
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Proyección para {nombre}  |  Plan: {tipo_plan}", align="C", ln=True)
    pdf.ln(10)

    # Configuración de dibujo de tarjetas
    card_w = 58
    card_h = 42
    start_x = (210 - (len(resultados) * card_w + (len(resultados)-1)*5)) / 2

    # --- 2. BONO DE BIENVENIDA ---
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(*pdf.custom_accent_color)
    pdf.cell(0, 10, "Bono de bienvenida", align="C", ln=True)
    pdf.ln(5)

    y_start = pdf.get_y()
    
    for idx, res in enumerate(resultados):
        item_bono = next((b for b in detalles_bonos if b['opcion'] == res['id']), None)
        x = start_x + idx * (card_w + 5)
        c_rgb = hex_to_rgb(res['color'])
        
        pdf.set_fill_color(*pdf.custom_card_bg)
        pdf.set_draw_color(*c_rgb)
        pdf.set_line_width(0.5)
        pdf.rect(x, y_start, card_w, card_h, 'DF')
        
        pdf.set_xy(x, y_start + 5)
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(*c_rgb)
        pdf.cell(card_w, 6, f"${res['monto_inicial']:,.0f} Al mes", align="C", ln=True)
        
        pdf.set_xy(x, y_start + 14)
        pdf.set_font("helvetica", "", 8)
        pdf.set_text_color(*pdf.custom_text_color)
        pdf.cell(card_w, 4, "Bono acreditado:", align="C", ln=True)
        
        if item_bono:
            pdf.set_xy(x, y_start + 18)
            pdf.set_font("helvetica", "B", 14)
            pdf.set_text_color(*c_rgb)
            pdf.cell(card_w, 8, f"${item_bono['monto']:,.0f}", align="C", ln=True)
            
            pdf.set_xy(x, y_start + 26)
            pdf.set_font("helvetica", "B", 9)
            pdf.cell(card_w, 5, f"({item_bono['pct']*100:.0f}%)", align="C", ln=True)
            
            pdf.set_xy(x, y_start + 32)
            pdf.set_text_color(*pdf.custom_text_color)
            pdf.cell(card_w, 5, f"+${item_bono['monto']/12:,.0f} al mes", align="C", ln=True)
            
    pdf.set_y(y_start + card_h + 10)

    # --- 3. HORIZONTE INICIAL ---
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(*pdf.custom_accent_color)
    pdf.cell(0, 10, f"{edad + anios_horizonte} años", align="C", ln=True)
    pdf.ln(5)

    card_h2 = 45
    y_start2 = pdf.get_y()
    
    for idx, res in enumerate(resultados):
        x = start_x + idx * (card_w + 5)
        c_rgb = hex_to_rgb(res['color'])
        
        pdf.set_fill_color(*pdf.custom_card_bg)
        pdf.set_draw_color(*c_rgb)
        pdf.rect(x, y_start2, card_w, card_h2, 'DF')
        
        last_row = res['df_display'].iloc[-1]
        total_aportado = last_row['Aportación Acumulada']
        rendimiento = res['saldo_final'] - total_aportado
        
        pdf.set_xy(x, y_start2 + 5)
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(*c_rgb)
        pdf.cell(card_w, 6, f"${res['monto_inicial']:,.0f} Al mes", align="C", ln=True)
        
        pdf.set_xy(x, y_start2 + 15)
        pdf.set_font("helvetica", "B", 15)
        pdf.set_text_color(*pdf.custom_text_color)
        pdf.cell(card_w, 10, f"${res['saldo_final']:,.0f}", align="C", ln=True)
        
        pdf.set_xy(x, y_start2 + 28)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(card_w, 5, f"Aportado: ${total_aportado:,.0f}", align="C", ln=True)
        
        pdf.set_xy(x, y_start2 + 34)
        pdf.set_font("helvetica", "B", 8)
        pdf.set_text_color(*c_rgb)
        pdf.cell(card_w, 5, f"Rendimiento: +${rendimiento:,.0f}", align="C", ln=True)

    pdf.set_y(y_start2 + card_h2 + 10)
    
    # --- 4. RETIRO ---
    proy_edad_retiro = edad + anios_para_retiro
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(*pdf.custom_accent_color)
    pdf.cell(0, 10, f"{proy_edad_retiro} años", align="C", ln=True)
    pdf.ln(5)

    card_h3 = 45
    y_start3 = pdf.get_y()
    
    for idx, r65 in enumerate(resultados_65):
        res = resultados[idx]
        x = start_x + idx * (card_w + 5)
        c_rgb = hex_to_rgb(res['color'])
        
        pdf.set_fill_color(*pdf.custom_card_bg)
        pdf.set_draw_color(*c_rgb)
        pdf.rect(x, y_start3, card_w, card_h3, 'DF')
        
        pdf.set_xy(x, y_start3 + 5)
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(*c_rgb)
        pdf.cell(card_w, 6, f"${r65['monto_inicial']:,.0f} Al mes", align="C", ln=True)
        
        pdf.set_xy(x, y_start3 + 15)
        pdf.set_font("helvetica", "B", 15)
        pdf.set_text_color(*pdf.custom_text_color)
        pdf.cell(card_w, 10, f"${r65['saldo_final_65']:,.0f}", align="C", ln=True)
        
        pdf.set_xy(x, y_start3 + 28)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(card_w, 5, f"Aportado: ${r65['total_aportado_65']:,.0f}", align="C", ln=True)
        
        pdf.set_xy(x, y_start3 + 34)
        pdf.set_font("helvetica", "B", 8)
        pdf.set_text_color(*c_rgb)
        pdf.cell(card_w, 5, f"Rendimiento: +${r65['rendimiento_65']:,.0f}", align="C", ln=True)

    # --- 5. GRÁFICA COMPARATIVA ---
    pdf.add_page()
    if is_dark:
        pdf.set_fill_color(*pdf.custom_bg_color)
        pdf.rect(0, 0, 210, 297, 'F')
    
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(*pdf.custom_accent_color)
    pdf.cell(0, 10, "Crecimiento de Capital en el Tiempo", align="C", ln=True)
    pdf.ln(5)

    try:
        img_bytes = fig.to_image(format="png", width=800, height=450, scale=2)
        img_io = io.BytesIO(img_bytes)
        pdf.image(img_io, x=15, y=pdf.get_y(), w=180)
    except Exception as e:
        pdf.set_text_color(255,0,0)
        pdf.cell(0, 10, "Error al generar gráfica", align="C", ln=True)
        
    # --- 6. TABLAS DINÁMICAS ---
    res_tabla = resultados[-1]
    
    pdf.add_page()
    if is_dark:
        pdf.set_fill_color(*pdf.custom_bg_color)
        pdf.rect(0, 0, 210, 297, 'F')
        
    c_rgb = hex_to_rgb(res_tabla['color'])
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(*c_rgb)
    pdf.cell(0, 10, f"Tabla de Detalle - Escenario Principal (${res_tabla['monto_inicial']:,.0f})", align="C", ln=True)
    pdf.ln(5)
    
    df = res_tabla["df_display"]
    cols = ["Año", "Edad", "Aportación Anual", "Aport. Acumulada", "Saldo Fondo"]
    if "Mes Global" in df.columns:
        cols[0] = "Mes"
        
    pdf.set_fill_color(*c_rgb)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 9)
    
    col_w = [25, 25, 40, 45, 45]
    start_x_tbl = (210 - sum(col_w)) / 2
    pdf.set_x(start_x_tbl)
    
    for i, col in enumerate(cols):
        pdf.cell(col_w[i], 8, col, border=1, align="C", fill=True)
    pdf.ln()
    
    pdf.set_font("helvetica", "", 8)
    fill = False
    
    for _, row in df.iterrows():
        if pdf.get_y() > 270:
            pdf.add_page()
            if is_dark:
                pdf.set_fill_color(*pdf.custom_bg_color)
                pdf.rect(0, 0, 210, 297, 'F')
            pdf.set_x(start_x_tbl)
            pdf.set_fill_color(*c_rgb)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("helvetica", "B", 9)
            for i, col in enumerate(cols):
                pdf.cell(col_w[i], 8, col, border=1, align="C", fill=True)
            pdf.ln()
            pdf.set_font("helvetica", "", 8)
            
        col_data = [
            str(int(row["Año"]) if "Mes Global" not in df.columns else int(row["Mes Global"])),
            str(int(row["Edad"])),
            f"${row['Aportación Anual']:,.0f}",
            f"${row['Aportación Acumulada']:,.0f}",
            f"${row['Saldo de Fondo']:,.0f}"
        ]
        
        pdf.set_x(start_x_tbl)
        if fill:
            pdf.set_fill_color(pdf.custom_card_bg[0], pdf.custom_card_bg[1], pdf.custom_card_bg[2])
        else:
            pdf.set_fill_color(pdf.custom_bg_color[0]+10, pdf.custom_bg_color[1]+10, pdf.custom_bg_color[2]+10)
            
        pdf.set_text_color(*pdf.custom_text_color)
        
        for i, dat in enumerate(col_data):
            pdf.cell(col_w[i], 6, dat, border=0, align="C", fill=True)
        pdf.ln()
        fill = not fill

    return pdf.output()
