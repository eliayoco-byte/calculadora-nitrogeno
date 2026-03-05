import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Calculadora de Fertilización N - 2026", page_icon="🌾")

# Diccionario de fertilizantes comunes y su % de Nitrógeno
FERTILIZANTES = {
    "Urea": 46,
    "Nitrato de Amonio": 33.5,
    "Sulfato de Amonio": 21,
    "UAN (Solución líquida)": 32,
    "DAP (Fosfato Diamónico)": 18,
    "MAP (Fosfato Monoamónico)": 11,
    "Otro (Personalizado)": 0
}

def calcular_fertilizacion(mo, da, prof, req, frac_min, eficiencia, n_porcentaje, precio_ton):
    # 1. Masa de suelo (kg/ha)
    volumen_suelo_m3 = (prof / 100) * 10000
    masa_suelo_kg = volumen_suelo_m3 * (da * 1000)
    
    # 2. N mineralizado del suelo (kg N/ha)
    n_mineralizado = (mo / 100) * masa_suelo_kg * 0.05 * frac_min
    
    # 3. Déficit y ajuste por eficiencia
    deficit_n = max(0.0, req - n_mineralizado)
    n_necesario_real = deficit_n / (eficiencia / 100)
    
    # 4. Cálculo del fertilizante comercial
    if n_porcentaje > 0:
        kg_fertilizante = n_necesario_real / (n_porcentaje / 100)
        bultos_50kg = kg_fertilizante / 50
        costo_total = (kg_fertilizante / 1000) * precio_ton
    else:
        kg_fertilizante = bultos_50kg = costo_total = 0

    return n_mineralizado, n_necesario_real, kg_fertilizante, bultos_50kg, costo_total

# --- INTERFAZ ---
st.title("🌾 Calculadora de Nitrógeno Multiproducto")
st.markdown("Calcule la dosis exacta según el tipo de fertilizante y el aporte de su suelo.")

# Sidebar para parámetros económicos y de suelo
st.sidebar.header("⚙️ Configuración del Suelo")
mo = st.sidebar.number_input("Materia Orgánica (%)", 0.1, 20.0, 3.2)
da = st.sidebar.number_input("Densidad Aparente (g/cm³)", 0.5, 1.8, 1.3)
prof = st.sidebar.slider("Profundidad de Raíces (cm)", 10, 60, 20)
frac_min = st.sidebar.select_slider("Tasa de Mineralización", 
                                   options=[0.01, 0.015, 0.02, 0.03, 0.04], 
                                   value=0.02,
                                   help="Baja (Frío) -> Alta (Cálido)")

# Panel Principal
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Objetivo")
    req = st.number_input("Requerimiento Cultivo (kg N/ha)", 0, 500, 150)
    eficiencia = st.slider("Eficiencia de Aplicación (%)", 10, 100, 60, 
                          help="Urea al voleo: 40-60%. Enterado/Inyectado: 70-85%.")

with col2:
    st.subheader("🧪 Fertilizante")
    nombre_f = st.selectbox("Seleccione Fertilizante", list(FERTILIZANTES.keys()))
    
    if nombre_f == "Otro (Personalizado)":
        n_puro = st.number_input("% Nitrógeno del producto", 1.0, 100.0, 20.0)
    else:
        n_puro = FERTILIZANTES[nombre_f]
        st.info(f"Concentración de N: {n_puro}%")
    
    precio_ton = st.number_input(f"Precio Tonelada {nombre_f} (USD)", 100.0, 2000.0, 530.0)

# Cálculo
if st.button("CALCULAR DOSIS", use_container_width=True):
    n_min, n_real, kg_fert, bultos, costo = calcular_fertilizacion(
        mo, da, prof, req, frac_min, eficiencia, n_puro, precio_ton
    )

    st.divider()
    
    # Métricas clave
    m1, m2, m3 = st.columns(3)
    m1.metric("Aporte Suelo", f"{n_min:.1f} kg N/ha")
    m2.metric("Necesidad Real", f"{n_real:.1f} kg N/ha")
    m3.metric("Costo Total", f"${costo:.2f} USD")

    # Resultado destacado
    st.success(f"### Aplicar: **{kg_fert:.1f} kg/ha** de {nombre_f}")
    st.write(f"📦 Equivalente a: **{bultos:.1f} bultos de 50kg**")

    # Advertencias agronómicas
    if nombre_f == "Urea" and eficiencia < 50:
        st.warning("⚠️ **Pérdidas altas:** Estás perdiendo mucha Urea por volatilización. Considera enterrarla o usar un inhibidor de ureasa.")
    
    if n_real > 180:
        st.error("🚨 **Dosis Excesiva:** Aplicar más de 180kg de N puro en una sola vez puede quemar raíces o contaminar acuíferos. **¡Fracciona la dosis!**")

    if "Fosfato" in nombre_f:
        st.info("💡 **Nota:** Este producto también aporta Fósforo (P). Ajusta tu plan de fertilización fosfatada.")

st.markdown("---")
st.caption("© 2026 - Herramienta de Soporte a Decisiones Agronómicas")
