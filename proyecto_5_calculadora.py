# -*- coding: utf-8 -*-
"""
Calculadora de Retiro y Costo de Postergar (Proyecto 5%)
--------------------------------------------------------
Este script contiene el motor matemático de proyección y el optimizador de 
búsqueda binaria para calcular el plan de retiro (estilo Allianz).
Compara la aportación necesaria comenzando hoy frente a haber iniciado a los 24 años.
"""

import pandas as pd

def obtener_porcentaje_bono(monto_mensual):
    """
    Calcula el porcentaje de bono de bienvenida según la aportación mensual
    (basado en la tabla de tabulación anualizada de la póliza).
    """
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

def calcular_escenario(monto_aporte, edad_inicial, tasa_anual, inflacion_activa, tasa_inflacion, isr_retencion=0.0, plazo_anos=25):
    """
    Proyecta el crecimiento del fondo mes a mes aplicando:
    - Incremento inflacionario anual de la aportación (si está activo).
    - Acreditación mensual del bono de bienvenida durante el primer año.
    - Tasas de interés diferenciadas por cubetas (póliza de Allianz).
    - Cargo de gestión del 0.1% mensual sobre el saldo total.
    - Cargo administrativo del 0.9% trimestral sobre el saldo inicial.
    - Cargo fijo de 15 UDIS mensuales (a partir del mes 19).
    - Tabla de cargos por rescate anticipado (retención Allianz).
    """
    meses_totales = int(plazo_anos * 12)
    monto_inicial = float(monto_aporte)
    monto_actual = float(monto_aporte)
    bono_porcentaje = obtener_porcentaje_bono(monto_actual)
    
    tasa_gestion_mensual = 0.001
    tasa_admin_trimestral = 0.009
    cargo_fijo_udis = 15.0
    valor_udi_inicial = 8.25
    
    tasa_interes_mensual_fondo = (tasa_anual / 100) / 12
    tasa_interes_mensual_bono = (0.09) / 12  # El bono crece al 9% de interés interno
    
    datos = []
    valor_udi_actual = valor_udi_inicial
    factor_inflacion_acumulado = 1.0
    
    # Cubetas de saldo
    saldo_bono = 0.0
    saldo_inicial_aport = 0.0
    saldo_regular = 0.0
    acumulado_aportado = 0.0
    
    monto_anualizado = monto_actual * 12
    bono_mensual_ano1 = (monto_anualizado * bono_porcentaje) / 12

    for mes in range(1, meses_totales + 1):
        anio_actual = (mes - 1) // 12 + 1
        mes_del_ano = (mes - 1) % 12 + 1
        edad_actual = edad_inicial + (mes // 12)
        
        # Ajuste inflacionario anual
        if inflacion_activa and mes > 1 and (mes - 1) % 12 == 0:
            factor_inflacion = (1 + tasa_inflacion / 100)
            factor_inflacion_acumulado *= factor_inflacion
            monto_actual *= factor_inflacion
            valor_udi_actual *= factor_inflacion
        
        aportacion_periodo = monto_actual
        
        # Acreditación del bono (sólo primer año)
        bono_mes = bono_mensual_ano1 if anio_actual == 1 else 0.0
        saldo_bono += bono_mes
        
        # Distribución de aportación regular
        if mes <= 18:
            saldo_inicial_aport += aportacion_periodo
        else:
            saldo_regular += aportacion_periodo
        
        acumulado_aportado += aportacion_periodo

        # Generar Intereses
        interes_bono = saldo_bono * tasa_interes_mensual_bono
        interes_inicial = saldo_inicial_aport * tasa_interes_mensual_fondo
        interes_regular = saldo_regular * tasa_interes_mensual_fondo
        
        saldo_bono += interes_bono
        saldo_inicial_aport += interes_inicial
        saldo_regular += interes_regular
        
        # Aplicar cargos
        cg_bono = saldo_bono * tasa_gestion_mensual
        cg_ini = saldo_inicial_aport * tasa_gestion_mensual
        cg_reg = saldo_regular * tasa_gestion_mensual
        
        saldo_bono -= cg_bono
        saldo_inicial_aport -= cg_ini
        saldo_regular -= cg_reg
        
        cargo_admin_var = 0.0
        if mes % 3 == 0:
            cav_bono = saldo_bono * tasa_admin_trimestral
            cav_ini = saldo_inicial_aport * tasa_admin_trimestral
            saldo_bono -= cav_bono
            saldo_inicial_aport -= cav_ini
            cargo_admin_var = cav_bono + cav_ini
            
        cargo_fijo_total = 0.0
        if mes >= 19:
            cargo_fijo_total = cargo_fijo_udis * valor_udi_actual
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
                saldo_bono -= remanente

        cargos_totales_mes = (cg_bono + cg_ini + cg_reg) + cargo_admin_var + cargo_fijo_total
        saldo_total = saldo_bono + saldo_inicial_aport + saldo_regular
        
        # Disponibilidad
        if anio_actual >= 25 or edad_actual >= 70:
            saldo_disponible = saldo_total
        else:
            saldo_disponible = saldo_regular
        
        # Retención Allianz (salida anticipada)
        tasa_retencion_allianz = 0.0
        if (edad_actual >= 60 and anio_actual >= 5) or edad_actual >= 70:
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
            "Post retención": saldo_neto_allianz,
            "Aportación": aportacion_periodo,
            "Bono": bono_mes,
            "Interés Generado": (interes_bono + interes_inicial + interes_regular),
            "Cargos": cargos_totales_mes
        })
        
    return pd.DataFrame(datos), bono_porcentaje

def encontrar_aporte_necesario(meta_objetivo, edad_ini, plazo_y, tasa_anual, infl_activa, tasa_infl, isr=0.0):
    """
    Encuentra con extrema precisión el aporte inicial mensual requerido para
    alcanzar una meta de retiro utilizando búsqueda binaria.
    """
    low = 1.0  # Aporte mínimo inicial
    
    r_m = (tasa_anual / 100) / 12
    if r_m > 0:
        base = (meta_objetivo * r_m) / (((1 + r_m) ** (plazo_y * 12)) - 1)
    else:
        base = meta_objetivo / (plazo_y * 12)
        
    high = base * 10.0  # Techo del rango de búsqueda
    
    for _ in range(40):
        mid = (low + high) / 2
        df_temp, _ = calcular_escenario(mid, edad_ini, tasa_anual, infl_activa, tasa_infl, isr_retencion=isr, plazo_anos=plazo_y)
        final_val = df_temp['Saldo de Fondo'].iloc[-1]
        
        if final_val < meta_objetivo:
            low = mid
        else:
            high = mid
            
    return (low + high) / 2

# =====================================================================
# SCRIPT DE EJECUCIÓN (MODIFICA ESTOS PARÁMETROS PARA HACER TUS PRUEBAS)
# =====================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("           CALCULADORA STANDALONE - PROYECTO 5%         ")
    print("=" * 60)

    # 1. ENTRADAS DE CONFIGURACIÓN
    edad_actual = 35             # Edad del cliente hoy (ej. 35 años)
    edad_retiro = 65             # Edad a la que se desea retirar (ej. 65 años)
    renta_mensual_deseada = 50000.0  # Retiro mensual deseado (pesos hoy)
    tasa_anual_rend = 10.0       # Tasa de rendimiento estimada (anual)
    inflacion_activa = True      # Si las aportaciones crecen para mitigar inflación
    tasa_inflacion = 4.0         # % de inflación anual estimado
    patrimonio_actual = 0.0      # Patrimonio que ya tiene el cliente hoy (opcional)
    blindar_poder_adq = False    # Inflar la renta de retiro para mantener poder adquisitivo

    # 2. CÁLCULOS PRELIMINARES
    años_inversion_hoy = edad_retiro - edad_actual
    r_anual_dec = tasa_anual_rend / 100.0

    # Lógica de Blindaje de Poder Adquisitivo
    if blindar_poder_adq:
        renta_calculada = renta_mensual_deseada * ((1 + (tasa_inflacion / 100)) ** años_inversion_hoy)
    else:
        renta_calculada = renta_mensual_deseada

    meta_retiro = (renta_calculada * 12) / (r_anual_dec if r_anual_dec > 0 else 0.01)
    fv_patrimonio = patrimonio_actual * ((1 + r_anual_dec) ** años_inversion_hoy)
    meta_neta = max(0.0, meta_retiro - fv_patrimonio)

    # 3. APORTACIÓN EMPEZANDO HOY
    aporte_hoy = encontrar_aporte_necesario(
        meta_neta, edad_actual, años_inversion_hoy, tasa_anual_rend, inflacion_activa, tasa_inflacion
    )

    print(f"CLIENTE: Edad {edad_actual} | Retiro a los {edad_retiro} años | Meta: ${meta_neta:,.2f}")
    print(f"--> Aportación Mensual recomendada hoy: ${aporte_hoy:,.2f}")
    print("-" * 60)

    # 4. LÓGICA DE PROYECTO 5% (COMENZANDO A LOS 24 AÑOS)
    if edad_actual > 24:
        plazo_desde_24 = edad_retiro - 24
        
        # Aportación si hubiera conocido el proyecto a los 24 años
        aporte_24 = encontrar_aporte_necesario(
            meta_retiro, 24, plazo_desde_24, tasa_anual_rend, inflacion_activa, tasa_inflacion
        )
        
        # Proyectar el plan desde los 24 años
        df_24, _ = calcular_escenario(
            aporte_24, 24, tasa_anual_rend, inflacion_activa, tasa_inflacion, plazo_anos=plazo_desde_24
        )
        
        # Buscar el saldo que debería tener hoy (a su edad actual)
        fila_hoy = df_24[df_24['Edad'] == edad_actual]
        if not fila_hoy.empty:
            patrimonio_necesario = fila_hoy['Saldo de Fondo'].iloc[0]
        else:
            patrimonio_necesario = 0.0
            
        print("SI HUBIERAS CONOCIDO EL PROYECTO A LOS 24 AÑOS:")
        print(f"1. Aportación Mensual a los 24 años: ${aporte_24:,.2f}")
        print(f"2. Patrimonio actual necesario hoy (edad {edad_actual}): ${patrimonio_necesario:,.2f}")
        print("\n* Explicación: Si hubieras empezado a los 24 años, tu aportación mensual")
        print(f"  sería de solo ${aporte_24:,.0f} y hoy ya tendrías un saldo acumulado de ${patrimonio_necesario:,.0f}")
        print(f"  en tu fondo de inversión.")
    else:
        print("El cliente tiene 24 años o menos. ¡Ya se encuentra en la edad óptima de inicio!")
    
    print("=" * 60)
