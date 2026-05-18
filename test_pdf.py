import sys
import pandas as pd
import plotly.graph_objects as go
from pdf_astor import generar_pdf_reporte

# Dummy data
resultados = [
    {"id": 1, "monto_inicial": 3000, "color": "#ff0000", "saldo_final": 500000, "df_display": pd.DataFrame({"Año": [1,2], "Edad": [30,31], "Aportación Anual": [36000, 36000], "Aportación Acumulada": [36000, 72000], "Saldo de Fondo": [38000, 78000]})}
]
resultados_65 = [
    {"id": 1, "monto_inicial": 3000, "color": "#ff0000", "saldo_final_65": 1000000, "total_aportado_65": 500000, "rendimiento_65": 500000}
]
detalles_bonos = [
    {"opcion": 1, "pct": 0.5, "monto": 15000}
]

fig = go.Figure()
fig.add_trace(go.Scatter(x=[1,2,3], y=[1,2,3]))

try:
    print("Generating PDF...")
    pdf_bytes = generar_pdf_reporte(
        nombre="Test", tipo_plan="Plan 1", detalles_bonos=detalles_bonos,
        resultados=resultados, resultados_65=resultados_65,
        anios_horizonte=25, edad=30, anios_para_retiro=35, fig=fig
    )
    print(type(pdf_bytes))
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
