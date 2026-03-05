import streamlit as st

# Configuración para móvil
st.set_page_config(page_title="FertiliApp 2026", layout="centered")

# --- BASE DE DATOS ---
CULTIVOS = {
    "Café": {"N": 200, "P2O5": 50, "K2O": 250},
    "Cacao": {"N": 100, "P2O5": 60, "K2O": 120},
    "Caña de Azúcar": {"N": 160, "P2O5": 80, "K2O": 190},
    "Cítricos": {"N": 150, "P2O5": 45, "K2O": 140},
    "Manual": {"N": 0, "P2O5": 0, "K2O": 0}
}

FERTILIZANTES = {
    "Urea (46% N)": [46, 0, 0],
    "DAP (18% N - 46% P)": [18, 46, 0],
    "Cloruro Potasio (60% K)": [0, 0, 60],
    "17-6-18 (Completo)": [17, 6, 18],
    "Triple 15": [15, 15, 15]
}

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stNumberInput, .stSelectbox { border: 2px solid #2e7d32 !important; }
    div[data-testid="stMetricValue"] { color: #2e7d32; font-size: 1.8rem; }
    .box-input { background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 5px solid #2196f3; margin-bottom: 20px; }
    .box-result { background-color: #e8f5e9; padding: 20px; border-radius: 15px; border-left: 5px solid #4caf50; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌱 FertiliApp: N-P-K")
st.caption("Asistente de Fertilización de Precisión - William Fernando Cortes")

# --- SECCIÓN 1: REQUERIMIENTOS DEL CULTIVO ---
st.subheader("1. Objetivo del Cultivo")
with st.container():
    col_a, col_b = st.columns(2)
    crop_sel = col_a.selectbox("Cultivo:", list(CULTIVOS.keys()))
    
    # Valores base
    base_n = CULTIVOS[crop_sel]["N"]
    base_p = CULTIVOS[crop_sel]["P2O5"]
    base_k = CULTIVOS[crop_sel]["K2O"]

    req_n = st.number_input("Meta N (kg/ha)", value=float(base_n))
    req_p = st.number_input("Meta P2O5 (kg/ha)", value=float(base_p))
    req_k = st.number_input("Meta K2O (kg/ha)", value=float(base_k))

# --- SECCIÓN 2: DATOS DEL ANÁLISIS DE SUELO (INPUT) ---
st.markdown('<div class="box-input">', unsafe_allow_html=True)
st.subheader("2. Resultados del Laboratorio")
st.info("Ingrese los valores de su análisis de suelo:")

mo_suelo = st.number_input("Materia Orgánica (%)", 0.0, 20.0, 3.0)
p_ppm = st.number_input("Fósforo (ppm o mg/kg)", 0.0, 500.0, 15.0)
k_meq = st.number_input("Potasio (meq/100g)", 0.0, 5.0, 0.25)

with st.expander("Configuración Física del Suelo"):
    da = st.number_input("Densidad Aparente (g/cm³)", 0.5, 1.7, 1.25)
    prof = st.number_input("Profundidad Muestreo (cm)", 10, 40, 20)
    frac_min = st.select_slider("Mineralización N", options=[0.01, 0.02, 0.03], value=0.02)
st.markdown('</div>', unsafe_allow_html=True)

# --- LÓGICA DE CONVERSIÓN ---
# 1. N disponible del suelo
masa_suelo = (prof / 100) * 10000 * (da * 1000)
n_disponible_suelo = (mo_suelo / 100) * masa_suelo * 0.05 * frac_min

# 2. P disponible (Conversión ppm a kg/ha P2O5)
# Factor simplificado: ppm * 2 (para 20cm) * 2.29 (P a P2O5)
p_disponible_suelo = p_ppm * 2 * (prof / 20) * 2.29

# 3. K disponible (Conversión meq/100g a kg/ha K2O)
# Factor: meq * 391 * DA * (Prof/10) * 1.2 (K a K2O)
k_disponible_suelo = k_meq * 391 * da * (prof / 10) * 1.2

# --- SECCIÓN 3: CÁLCULO DE FERTILIZANTE ---
st.subheader("3. Fertilizante a usar")
fert_sel = st.selectbox("Seleccione Producto:", list(FERTILIZANTES.keys()))
eficiencia = st.slider("Eficiencia de aplicación (%)", 20, 100, 60)
precio_ton = st.number_input("Precio Tonelada (USD)", 200, 1500, 540)

# Déficit Neto
def_n = max(0.0, req_n - n_disponible_suelo)
def_p = max(0.0, req_p - (p_disponible_suelo * 0.2)) # Solo 20% del P del suelo suele ser disponible rápido
def_k = max(0.0, req_k - (k_disponible_suelo * 0.5)) # Solo 50% del K del suelo

# Ajuste por eficiencia
necesidad_real_n = def_n / (eficiencia/100)

# Cantidad de producto comercial basado en N
conc_n = FERTILIZANTES[fert_sel][0]
if conc_n > 0:
    kg_producto = (necesidad_real_n / conc_n) * 100
else:
    kg_producto = 0

bultos = kg_producto / 50
costo = (kg_producto / 1000) * precio_ton

# --- SECCIÓN 4: RESULTADOS (OUTPUT) ---
st.markdown('<div class="box-result">', unsafe_allow_html=True)
st.subheader("📊 Recomendación Final")

col1, col2 = st.columns(2)
col1.metric("N del Suelo", f"{n_disponible_suelo:.1f} kg")
col2.metric("P2O5 Suelo", f"{p_disponible_suelo:.1f} kg")

st.write(f"Para cubrir el Nitrógeno con **{fert_sel}**:")
st.success(f"### APLICAR: {kg_producto:.1f} kg/ha")
st.info(f"Equivale a: **{bultos:.1f} bultos de 50kg**")
st.metric("Inversión estimada", f"${costo:.2f} USD/ha")

with st.expander("Ver balance P y K"):
    st.write(f"Necesidad neta P2O5: {def_p:.1f} kg/ha")
    st.write(f"Necesidad neta K2O: {def_k:.1f} kg/ha")
    st.caption("Nota: El cálculo de bultos se basa en cubrir el Nitrógeno. Si el fertilizante es un complejo (N-P-K), verifique si los otros elementos quedan cubiertos.")
st.markdown('</div>', unsafe_allow_html=True)

st.warning("⚠️ Consulte siempre con un Ingeniero Agrónomo antes de la aplicación.")
