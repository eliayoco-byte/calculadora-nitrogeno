import streamlit as st
import pandas as pd

# 1. BASE DE DATOS DE CULTIVOS (Valores referenciales por ha/año para producción media)
CROP_DATABASE = {
    "Café (Producción)": {"N": 200, "P2O5": 50, "K2O": 250, "Info": "Basado en 3000 kg café pergamino/ha"},
    "Cacao (Adulto)": {"N": 100, "P2O5": 60, "K2O": 120, "Info": "Basado en 1000 kg grano seco/ha"},
    "Caña de Azúcar": {"N": 150, "P2O5": 80, "K2O": 200, "Info": "Promedio para caña planta/soca"},
    "Cítricos (Naranja/Limón)": {"N": 160, "P2O5": 50, "K2O": 150, "Info": "Árboles en plena producción (8+ años)"},
    "Personalizado": {"N": 0, "P2O5": 0, "K2O": 0, "Info": "Ingrese sus propios valores"}
}

# 2. BASE DE DATOS DE FERTILIZANTES
FERTILIZANTES = {
    "Urea (46-0-0)": [46, 0, 0],
    "DAP (18-46-0)": [18, 46, 0],
    "Cloruro de Potasio (0-0-60)": [0, 0, 60],
    "Sulfato de Amonio (21-0-0)": [21, 0, 0],
    "Sulpomag (0-0-22)": [0, 0, 22],
    "17-6-18 (Cafetero)": [17, 6, 18],
    "15-15-15 (Triple 15)": [15, 15, 15],
    "Otro (Personalizado)": [0, 0, 0]
}

st.set_page_config(page_title="Planificador N-P-K 2026", layout="wide")

st.title("🌱 Sistema de Recomendación Nutricional N-P-K")
st.markdown("Calcula las necesidades de fertilización según el cultivo y el aporte de Materia Orgánica.")

# --- SECCIÓN 1: SELECCIÓN DE CULTIVO ---
st.header("1. Requerimientos del Cultivo")
col_c1, col_c2 = st.columns([1, 2])

with col_c1:
    seleccion_cultivo = st.selectbox("Seleccione el Sistema Productivo", list(CROP_DATABASE.keys()))
    meta = CROP_DATABASE[seleccion_cultivo]
    st.info(f"📋 **Nota:** {meta['Info']}")

with col_c2:
    col_n, col_p, col_k = st.columns(3)
    req_n = col_n.number_input("Req. N (kg/ha)", value=float(meta['N']))
    req_p = col_p.number_input("Req. P2O5 (kg/ha)", value=float(meta['P2O5']))
    req_k = col_k.number_input("Req. K2O (kg/ha)", value=float(meta['K2O']))

# --- SECCIÓN 2: DATOS DEL SUELO ---
st.header("2. Aporte del Suelo (Materia Orgánica)")
with st.expander("Configurar parámetros del suelo"):
    c1, c2, c3, c4 = st.columns(4)
    mo = c1.number_input("Materia Orgánica (%)", 0.1, 15.0, 3.0)
    da = c2.number_input("Densidad Aparente (g/cm³)", 0.8, 1.6, 1.2)
    prof = c3.number_input("Profundidad (cm)", 10, 40, 20)
    frac_min = c4.selectbox("Clima (Mineralización)", [0.015, 0.02, 0.03], 
                           format_func=lambda x: "Frío (1.5%)" if x==0.015 else "Templado (2%)" if x==0.02 else "Cálido (3%)")

# --- LÓGICA DE CÁLCULO ---
# Nitrógeno mineralizado
masa_suelo = (prof / 100) * 10000 * (da * 1000)
n_suelo = (mo / 100) * masa_suelo * 0.05 * frac_min
n_neto = max(0.0, req_n - n_suelo)

# --- SECCIÓN 3: PLAN DE FERTILIZACIÓN ---
st.header("3. Elección de Fertilizantes")
col_f1, col_f2 = st.columns(2)

with col_f1:
    st.subheader("Selección de Productos")
    f_opcion = st.selectbox("Fertilizante Principal", list(FERTILIZANTES.keys()))
    if f_opcion == "Otro (Personalizado)":
        comp_n = st.number_input("% N", 0, 100, 0)
        comp_p = st.number_input("% P2O5", 0, 100, 0)
        comp_k = st.number_input("% K2O", 0, 100, 0)
    else:
        comp_n, comp_p, comp_k = FERTILIZANTES[f_opcion]

    eficiencia = st.slider("Eficiencia global de la aplicación (%)", 30, 95, 60)
    precio_ton = st.number_input("Precio por Tonelada (USD)", 200, 1500, 550)

# CÁLCULOS FINALES
# Ajuste por eficiencia
n_ajustado = n_neto / (eficiencia/100)
p_ajustado = req_p / (eficiencia/100)
k_ajustado = req_k / (eficiencia/100)

# Cálculo basado en el elemento limitante del fertilizante elegido (generalmente N)
if comp_n > 0:
    kg_ha_comercial = (n_ajustado / comp_n) * 100
else:
    kg_ha_comercial = 0

costo_ha = (kg_ha_comercial / 1000) * precio_ton

# --- RESULTADOS ---
st.divider()
res1, res2, res3, res4 = st.columns(4)

res1.metric("Aporte Suelo (N)", f"{n_suelo:.1f} kg/ha")
res2.metric("Déficit Neto (N)", f"{n_neto:.1f} kg/ha")
res3.metric(f"Cantidad de {f_opcion}", f"{kg_ha_comercial:.1f} kg/ha")
res4.metric("Costo Estimado", f"${costo_ha:.2f} USD")

# Tabla comparativa de necesidades
st.subheader("Resumen de Necesidades Totales (Ajustado por Eficiencia)")
df_resumen = pd.DataFrame({
    "Elemento": ["Nitrógeno (N)", "Fósforo (P2O5)", "Potasio (K2O)"],
    "Req. Cultivo (kg/ha)": [req_n, req_p, req_k],
    "Aporte Suelo (kg/ha)": [round(n_suelo,1), 0, 0],
    "Necesidad Real (c/Eficiencia)": [round(n_ajustado,1), round(p_ajustado,1), round(k_ajustado,1)]
})
st.table(df_resumen)

st.warning("⚠️ **Atención:** El aporte de P y K del suelo no se resta en este cálculo automático. Se recomienda consultar su análisis de suelo para ajustar P y K.")
