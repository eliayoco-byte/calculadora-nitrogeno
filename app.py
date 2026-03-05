import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Calculadora de Nitrógeno 2026", page_icon="🌱")

def calcular_nitrogeno_pro(mo, da, prof, req, frac_min, eficiencia, precio_urea):
    # Masa de suelo (kg/ha)
    volumen_suelo_m3 = (prof / 100) * 10000
    masa_suelo_kg = volumen_suelo_m3 * (da * 1000)
    
    # N mineralizado (kg N/ha) - Asumiendo 5% de N en la MO
    n_mineralizado = (mo / 100) * masa_suelo_kg * 0.05 * frac_min
    
    # N neto a aplicar ajustado por eficiencia
    deficit_n = max(0.0, req - n_mineralizado)
    n_aplicar_ajustado = deficit_n / (eficiencia / 100)
    
    # Convertir a Urea (46% N)
    kg_urea = n_aplicar_ajustado / 0.46
    bultos_50kg = kg_urea / 50
    costo_total = (kg_urea / 1000) * precio_urea
    
    return n_mineralizado, n_aplicar_ajustado, kg_urea, bultos_50kg, costo_total

# --- INTERFAZ DE USUARIO ---
st.title("🌱 Calculadora de Fertilización Nitrogenada")
st.markdown("""
Esta herramienta estima la dosis de Nitrógeno basada en el aporte de la Materia Orgánica del suelo.
*Actualizado: Marzo 2026*
""")

# Dividir en columnas para los datos de entrada
col1, col2 = st.columns(2)

with col1:
    st.subheader("Datos del Suelo")
    mo = st.number_input("Materia Orgánica (%)", min_value=0.1, max_value=20.0, value=3.2, step=0.1)
    da = st.number_input("Densidad Aparente (g/cm³)", min_value=0.5, max_value=1.8, value=1.3, step=0.05)
    prof = st.number_input("Profundidad de muestreo (cm)", min_value=10, max_value=100, value=20)

with col2:
    st.subheader("Datos del Cultivo")
    req = st.number_input("Requerimiento del Cultivo (kg N/ha)", min_value=0, max_value=500, value=150)
    eficiencia = st.slider("Eficiencia de aplicación (%)", 10, 100, 60)
    frac_min = st.selectbox("Tasa de Mineralización anual", 
                            options=[0.015, 0.02, 0.03], 
                            format_func=lambda x: f"{x*100}% (Clima {'Frío' if x<0.02 else 'Templado' if x==0.02 else 'Cálido'})")

st.sidebar.header("Costos y Fertilizante")
precio_urea = st.sidebar.number_input("Precio Tonelada Urea (USD)", value=530.0)

# Botón de cálculo
if st.button("Calcular Dosis Ahora"):
    n_min, n_total, kg_urea, bultos, costo = calcular_nitrogeno_pro(mo, da, prof, req, frac_min, eficiencia, precio_urea)
    
    # Mostrar resultados en tarjetas
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("N Suelo (Aporta)", f"{n_min:.1f} kg/ha")
    c2.metric("N Neto a Aplicar", f"{n_total:.1f} kg/ha")
    c3.metric("Costo Estimado", f"${costo:.2f} USD")
    
    st.success(f"### Recomendación: Aplicar **{kg_urea:.1f} kg de Urea** por hectárea.")
    st.info(f"Equivale aproximadamente a **{bultos:.1f} bultos** (de 50kg) por hectárea.")
    
    # Recomendación técnica adicional
    if bultos > 4:
        st.warning("⚠️ **Nota:** La dosis es alta. Se recomienda fraccionar en 2 o 3 aplicaciones para evitar pérdidas por lixiviación.")

st.markdown("---")
st.caption("Fórmula: N_disp = MO% * Masa_Suelo * 0.05 * Tasa_Min. Eficiencia aplicada al déficit.")
