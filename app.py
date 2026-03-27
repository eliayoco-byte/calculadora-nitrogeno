import streamlit as st

st.set_page_config(page_title="FertiliApp N-P-K", layout="centered", page_icon="🌱")

# ─────────────────────────────────────────────
# BASE DE DATOS
# ─────────────────────────────────────────────
CULTIVOS = {
    "Café": {"N": 200, "P2O5": 50, "K2O": 250},
    "Cacao": {"N": 100, "P2O5": 60, "K2O": 120},
    "Caña de Azúcar": {"N": 160, "P2O5": 80, "K2O": 190},
    "Cítricos": {"N": 150, "P2O5": 45, "K2O": 140},
    "Manual": {"N": 0, "P2O5": 0, "K2O": 0},
}

FERT_SIMPLES = {
    "Urea (46-0-0)": [46, 0, 0],
    "DAP (18-46-0)": [18, 46, 0],
    "MAP (11-52-0)": [11, 52, 0],
    "Cloruro de Potasio (0-0-60)": [0, 0, 60],
    "Sulfato de Amonio (21-0-0)": [21, 0, 0],
    "Superfosfato Triple (0-46-0)": [0, 46, 0],
    "Nitrato de Amonio (34-0-0)": [34, 0, 0],
}

FERT_COMPUESTOS = {
    "17-6-18-2 (Completo)": [17, 6, 18],
    "Triple 15 (15-15-15)": [15, 15, 15],
    "10-30-10": [10, 30, 10],
    "15-4-23-4 (Cafetero)": [15, 4, 23],
    "13-26-6": [13, 26, 6],
    "10-20-20": [10, 20, 20],
    "25-4-24": [25, 4, 24],
}

ALL_FERT = {**FERT_SIMPLES, **FERT_COMPUESTOS}

# ─────────────────────────────────────────────
# ESTILOS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f5f7f2; }
    div[data-testid="stMetricValue"] { color: #2e7d32; font-size: 1.6rem; }
    .block-container { max-width: 720px; }
    .stTabs [data-baseweb="tab-list"] { gap: 0px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #fff;
        border: 1px solid #d4c4a8;
        padding: 10px 24px;
        font-weight: 700;
    }
    .stTabs [aria-selected="true"] {
        background-color: #8B6F47 !important;
        color: white !important;
        border-color: #8B6F47 !important;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #d4c4a8;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style="background: linear-gradient(135deg, #2D6A4F, #40916C, #74C69D);
            padding: 30px 20px; border-radius: 16px; text-align: center; color: white; margin-bottom: 20px;">
    <div style="font-size: 24px; font-weight: 700; letter-spacing: 3px;">N · P · K</div>
    <h1 style="margin: 5px 0; font-size: 32px;">FertiliApp</h1>
    <p style="opacity: 0.85; font-size: 14px;">Asistente de Fertilización de Precisión — William Fernando Cortés</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECCIÓN 1: CULTIVO
# ─────────────────────────────────────────────
st.subheader("1. Objetivo del Cultivo")

crop_sel = st.selectbox("Cultivo:", list(CULTIVOS.keys()))
base = CULTIVOS[crop_sel]

col1, col2, col3 = st.columns(3)
req_n = col1.number_input("Meta N (kg/ha)", value=float(base["N"]), min_value=0.0, step=10.0)
req_p = col2.number_input("Meta P₂O₅ (kg/ha)", value=float(base["P2O5"]), min_value=0.0, step=5.0)
req_k = col3.number_input("Meta K₂O (kg/ha)", value=float(base["K2O"]), min_value=0.0, step=10.0)

st.divider()

# ─────────────────────────────────────────────
# SECCIÓN 2: ANÁLISIS DE SUELO
# ─────────────────────────────────────────────
st.subheader("2. Análisis de Suelo")
st.info("Ingrese los valores de su análisis de laboratorio.")

mo_suelo = st.number_input("Materia Orgánica (%)", 0.0, 20.0, 3.0, step=0.1)
col_p, col_k = st.columns(2)
p_ppm = col_p.number_input("Fósforo (ppm)", 0.0, 500.0, 15.0, step=1.0)
k_meq = col_k.number_input("Potasio (meq/100g)", 0.0, 5.0, 0.25, step=0.01)

with st.expander("Configuración Física del Suelo"):
    col_da, col_prof = st.columns(2)
    da = col_da.number_input("Densidad Aparente (g/cm³)", 0.5, 1.7, 1.25, step=0.01)
    prof = col_prof.number_input("Profundidad Muestreo (cm)", 10, 40, 20)

    st.write("**Tasa de Mineralización del N**")
    frac_min_opciones = {
        "Baja (0.01) — Suelos fríos, arcillosos o compactados": 0.01,
        "Media (0.02) — Condiciones templadas, textura franca": 0.02,
        "Alta (0.03) — Suelos cálidos, sueltos, bien aireados": 0.03,
    }
    frac_min_sel = st.radio(
        "Seleccione la tasa según las condiciones de su suelo:",
        list(frac_min_opciones.keys()),
        index=1,
        label_visibility="collapsed",
    )
    frac_min = frac_min_opciones[frac_min_sel]

st.divider()

# ─────────────────────────────────────────────
# CÁLCULOS BASE (suelo)
# ─────────────────────────────────────────────
masa_suelo = (prof / 100) * 10000 * (da * 1000)
n_suelo = (mo_suelo / 100) * masa_suelo * 0.05 * frac_min
p_suelo = p_ppm * 2 * (prof / 20) * 2.29
k_suelo = k_meq * 391 * da * (prof / 10) * 1.2

def_n = max(0.0, req_n - n_suelo)
def_p = max(0.0, req_p - (p_suelo * 0.2))
def_k = max(0.0, req_k - (k_suelo * 0.5))

# ─────────────────────────────────────────────
# SECCIÓN 3: FERTILIZANTE
# ─────────────────────────────────────────────
st.subheader("3. Fertilizante a Usar")

tab_simple, tab_compuesto = st.tabs(["Simples (hasta 3)", "Compuestos"])

with tab_simple:
    st.caption("Active hasta 3 fuentes simples para cubrir N, P y K por separado.")

    # Fuente 1 - N
    st.markdown("**Fuente 1 — Nitrógeno**")
    f1_activo = st.checkbox("Activar Fuente 1", value=True, key="f1")
    if f1_activo:
        col_f1a, col_f1b = st.columns([3, 1])
        f1_fert = col_f1a.selectbox("Producto fuente 1:", list(FERT_SIMPLES.keys()), key="f1_fert")
        f1_obj = col_f1b.selectbox("Objetivo:", ["N", "P₂O₅", "K₂O"], index=0, key="f1_obj")
    else:
        f1_fert, f1_obj = None, None

    # Fuente 2 - P
    st.markdown("**Fuente 2 — Fósforo**")
    f2_activo = st.checkbox("Activar Fuente 2", value=True, key="f2")
    if f2_activo:
        col_f2a, col_f2b = st.columns([3, 1])
        f2_fert = col_f2a.selectbox("Producto fuente 2:", list(FERT_SIMPLES.keys()), index=1, key="f2_fert")
        f2_obj = col_f2b.selectbox("Objetivo:", ["N", "P₂O₅", "K₂O"], index=1, key="f2_obj")
    else:
        f2_fert, f2_obj = None, None

    # Fuente 3 - K
    st.markdown("**Fuente 3 — Potasio**")
    f3_activo = st.checkbox("Activar Fuente 3", value=True, key="f3")
    if f3_activo:
        col_f3a, col_f3b = st.columns([3, 1])
        f3_fert = col_f3a.selectbox("Producto fuente 3:", list(FERT_SIMPLES.keys()), index=3, key="f3_fert")
        f3_obj = col_f3b.selectbox("Objetivo:", ["N", "P₂O₅", "K₂O"], index=2, key="f3_obj")
    else:
        f3_fert, f3_obj = None, None

with tab_compuesto:
    comp_fert = st.selectbox("Producto compuesto:", list(FERT_COMPUESTOS.keys()))
    comp_vals = FERT_COMPUESTOS[comp_fert]
    st.markdown(
        f"**N** {comp_vals[0]}% · **P₂O₅** {comp_vals[1]}% · **K₂O** {comp_vals[2]}%"
    )

st.divider()

eficiencia = st.slider("Eficiencia de aplicación (%)", 20, 100, 60)
precio_ton = st.number_input("Precio Tonelada (COP $)", min_value=500000, max_value=10000000, value=2300000, step=50000)

st.divider()

# ─────────────────────────────────────────────
# SECCIÓN 4: RESULTADOS
# ─────────────────────────────────────────────
st.subheader("4. Recomendación Final")

# Detectar modo activo
# Streamlit tabs no tienen estado directo, así que calculamos ambos y mostramos ambos
eff = eficiencia / 100


def calc_simple_fuente(fert_name, objetivo):
    """Calcula kg/ha y aportes para una fuente simple."""
    comp = FERT_SIMPLES.get(fert_name, [0, 0, 0])
    obj_map = {"N": (def_n, 0), "P₂O₅": (def_p, 1), "K₂O": (def_k, 2)}
    deficit, idx = obj_map[objetivo]
    nec_real = deficit / eff
    conc = comp[idx]
    kg = (nec_real / conc) * 100 if conc > 0 else 0
    bultos = kg / 50
    costo = (kg / 1000) * precio_ton
    aporte_n = (kg * comp[0]) / 100
    aporte_p = (kg * comp[1]) / 100
    aporte_k = (kg * comp[2]) / 100
    return {
        "nombre": fert_name, "objetivo": objetivo,
        "kg": kg, "bultos": bultos, "costo": costo,
        "aporteN": aporte_n, "aporteP": aporte_p, "aporteK": aporte_k,
    }


# ── RESULTADOS SIMPLES ──
with tab_simple:
    fuentes = []
    if f1_activo and f1_fert:
        fuentes.append(calc_simple_fuente(f1_fert, f1_obj))
    if f2_activo and f2_fert:
        fuentes.append(calc_simple_fuente(f2_fert, f2_obj))
    if f3_activo and f3_fert:
        fuentes.append(calc_simple_fuente(f3_fert, f3_obj))

    if fuentes:
        st.markdown("---")
        st.markdown("#### Recomendación — Mezcla de Simples")

        for f in fuentes:
            with st.container():
                ca, cb = st.columns([2, 1])
                ca.markdown(f"**{f['nombre']}** — cubre {f['objetivo']}")
                cb.metric("Aplicar", f"{f['kg']:.1f} kg/ha")
                ca.caption(f"{f['bultos']:.1f} bultos · ${f['costo']:,.0f} COP/ha")

        # Totales
        total_n = sum(f["aporteN"] for f in fuentes)
        total_p = sum(f["aporteP"] for f in fuentes)
        total_k = sum(f["aporteK"] for f in fuentes)
        total_costo = sum(f["costo"] for f in fuentes)

        nec_real_n = def_n / eff
        nec_real_p = def_p / eff
        nec_real_k = def_k / eff
        falta_n = max(0, nec_real_n - total_n)
        falta_p = max(0, nec_real_p - total_p)
        falta_k = max(0, nec_real_k - total_k)

        st.success(f"**Inversión total estimada: ${total_costo:,.0f} COP/ha**")

        st.markdown("**Aporte combinado:**")
        c1, c2, c3 = st.columns(3)
        c1.metric("N aportado", f"{total_n:.1f} kg/ha",
                   delta="Cubierto" if falta_n <= 1 else f"Faltan {falta_n:.1f}",
                   delta_color="normal" if falta_n <= 1 else "inverse")
        c2.metric("P₂O₅ aportado", f"{total_p:.1f} kg/ha",
                   delta="Cubierto" if falta_p <= 1 else f"Faltan {falta_p:.1f}",
                   delta_color="normal" if falta_p <= 1 else "inverse")
        c3.metric("K₂O aportado", f"{total_k:.1f} kg/ha",
                   delta="Cubierto" if falta_k <= 1 else f"Faltan {falta_k:.1f}",
                   delta_color="normal" if falta_k <= 1 else "inverse")
    else:
        st.warning("Active al menos una fuente para ver la recomendación.")

# ── RESULTADOS COMPUESTO ──
with tab_compuesto:
    conc_n = FERT_COMPUESTOS[comp_fert][0]
    conc_p = FERT_COMPUESTOS[comp_fert][1]
    conc_k = FERT_COMPUESTOS[comp_fert][2]
    nec_real = def_n / eff
    kg_prod = (nec_real / conc_n) * 100 if conc_n > 0 else 0
    bultos = kg_prod / 50
    costo = (kg_prod / 1000) * precio_ton

    aporte_n = (kg_prod * conc_n) / 100
    aporte_p = (kg_prod * conc_p) / 100
    aporte_k = (kg_prod * conc_k) / 100

    nec_real_p = def_p / eff
    nec_real_k = def_k / eff
    falta_p_c = max(0, nec_real_p - aporte_p)
    falta_k_c = max(0, nec_real_k - aporte_k)

    st.markdown("---")
    st.markdown(f"#### Recomendación — {comp_fert}")

    st.success(f"### Aplicar: {kg_prod:.1f} kg/ha")
    m1, m2, m3 = st.columns(3)
    m1.metric("Bultos 50 kg", f"{bultos:.1f}")
    m2.metric("Inversión", f"${costo:,.0f} COP/ha")
    m3.metric("N suelo", f"{n_suelo:.1f} kg/ha")

    st.markdown(f"**Con {bultos:.1f} bultos de {comp_fert} usted aporta:**")
    a1, a2, a3 = st.columns(3)
    a1.metric("N aportado", f"{aporte_n:.1f} kg/ha",
              delta="Cubierto" if aporte_n >= def_n else f"Faltan {def_n - aporte_n:.1f}",
              delta_color="normal" if aporte_n >= def_n else "inverse")
    a2.metric("P₂O₅ aportado", f"{aporte_p:.1f} kg/ha",
              delta="Cubierto" if falta_p_c <= 1 else f"Faltan {falta_p_c:.1f}",
              delta_color="normal" if falta_p_c <= 1 else "inverse")
    a3.metric("K₂O aportado", f"{aporte_k:.1f} kg/ha",
              delta="Cubierto" if falta_k_c <= 1 else f"Faltan {falta_k_c:.1f}",
              delta_color="normal" if falta_k_c <= 1 else "inverse")

    # Complementos sugeridos
    if falta_p_c > 1 or falta_k_c > 1:
        st.warning("**Sugerencia — Complementar con simples:**")
        if falta_p_c > 1:
            mejor_p = "DAP (18-46-0)"
            conc_p_s = FERT_SIMPLES[mejor_p][1]
            kg_p = (falta_p_c / conc_p_s) * 100 if conc_p_s > 0 else 0
            st.markdown(
                f"- **{mejor_p}**: {kg_p:.1f} kg/ha ({kg_p/50:.1f} bultos) "
                f"— para cubrir {falta_p_c:.1f} kg de P₂O₅ faltante"
            )
        if falta_k_c > 1:
            mejor_k = "Cloruro de Potasio (0-0-60)"
            conc_k_s = FERT_SIMPLES[mejor_k][2]
            kg_k = (falta_k_c / conc_k_s) * 100 if conc_k_s > 0 else 0
            st.markdown(
                f"- **{mejor_k}**: {kg_k:.1f} kg/ha ({kg_k/50:.1f} bultos) "
                f"— para cubrir {falta_k_c:.1f} kg de K₂O faltante"
            )

# ─────────────────────────────────────────────
# DETALLE DEL SUELO
# ─────────────────────────────────────────────
with st.expander("Ver detalle del suelo"):
    ds1, ds2, ds3 = st.columns(3)
    ds1.metric("N disponible suelo", f"{n_suelo:.1f} kg/ha")
    ds2.metric("P₂O₅ disponible suelo", f"{p_suelo:.1f} kg/ha")
    ds3.metric("K₂O disponible suelo", f"{k_suelo:.1f} kg/ha")
    dd1, dd2, dd3 = st.columns(3)
    dd1.metric("Déficit neto N", f"{def_n:.1f} kg/ha")
    dd2.metric("Déficit neto P₂O₅", f"{def_p:.1f} kg/ha")
    dd3.metric("Déficit neto K₂O", f"{def_k:.1f} kg/ha")

st.divider()

# ─────────────────────────────────────────────
# ADVERTENCIA
# ─────────────────────────────────────────────
st.warning(
    "Consulte siempre con un Ingeniero Agrónomo antes de la aplicación. "
    "Esta herramienta es orientativa y no reemplaza el criterio profesional."
)

# ─────────────────────────────────────────────
# REFERENCIAS BIBLIOGRÁFICAS
# ─────────────────────────────────────────────
with st.expander("Base Metodológica y Referencias"):

    st.markdown("#### Fórmulas utilizadas")
    st.code("""
N disponible del suelo:
  N = (MO/100) × Masa_suelo × 0.05 × Coef_min
  Masa_suelo = (Prof/100) × 10.000 m² × (DA × 1000)

P₂O₅ disponible (ppm → kg/ha):
  P₂O₅ = ppm × 2 × (Prof/20) × 2.29
  Factor 2.29 = conversión P elemental a P₂O₅

K₂O disponible (meq/100g → kg/ha):
  K₂O = meq × 391 × DA × (Prof/10) × 1.2
  Factor 1.2 = conversión K elemental a K₂O

Dosis de fertilizante:
  kg/ha = (Déficit / Eficiencia) / (Concentración/100)
""", language=None)

    st.markdown("#### Supuestos del modelo")
    st.markdown("""
- El 5% de la materia orgánica del suelo corresponde a nitrógeno total (relación C:N ≈ 10:1, con 58% de C en la MO).
- Solo el 20% del P del suelo se considera rápidamente disponible para el cultivo en el ciclo productivo.
- Solo el 50% del K intercambiable del suelo se considera disponible para absorción en el ciclo.
- Coeficientes de mineralización: 1% (baja), 2% (media), 3% (alta), según temperatura y textura del suelo.
- La eficiencia de aplicación ajusta pérdidas por volatilización, lixiviación y fijación.
""")

    st.markdown("#### Requerimientos nutricionales de cultivos")
    st.markdown("""
- **Café:** N=200, P₂O₅=50, K₂O=250 kg/ha — Basado en Sadeghian (2008), Cenicafé.
- **Cacao:** N=100, P₂O₅=60, K₂O=120 kg/ha — Basado en Fedecacao & ICA, Manual de fertilización.
- **Caña de Azúcar:** N=160, P₂O₅=80, K₂O=190 kg/ha — Basado en Cenicaña, Series técnicas.
- **Cítricos:** N=150, P₂O₅=45, K₂O=140 kg/ha — Basado en ICA & Corpoica, Guía de manejo integrado.
""")

    st.markdown("#### Referencias bibliográficas")
    st.markdown("""
[1] Havlin, J. L., Tisdale, S. L., Nelson, W. L., & Beaton, J. D. (2014). *Soil Fertility and Fertilizers: An Introduction to Nutrient Management* (8.ª ed.). Pearson Education.

[2] Sadeghian, S. (2008). *Fertilidad del suelo y nutrición del café en Colombia: Guía práctica*. Cenicafé, Boletín Técnico N.º 32. Chinchiná, Colombia.

[3] ICA – Instituto Colombiano Agropecuario. (2015). *Manual de fertilización y nutrición de cultivos tropicales*. Bogotá, Colombia.

[4] Osorio, N. W. (2014). Manejo de nutrientes en suelos del trópico. *Universidad Nacional de Colombia*, Sede Medellín. Editorial UNAL.

[5] Cenicaña. (2012). *El cultivo de la caña de azúcar en la zona azucarera de Colombia*. Centro de Investigación de la Caña de Azúcar de Colombia. Cali.

[6] Brady, N. C., & Weil, R. R. (2017). *The Nature and Properties of Soils* (15.ª ed.). Pearson.

[7] FAO. (2006). *Plant nutrition for food security: A guide for integrated nutrient management*. FAO Fertilizer and Plant Nutrition Bulletin, 16. Roma.

[8] Fedecacao. (2013). *Guía técnica para el cultivo del cacao* (3.ª ed.). Federación Nacional de Cacaoteros. Bogotá, Colombia.
""")

    st.info(
        "**Nota:** Los factores de conversión (P→P₂O₅ = 2.29; K→K₂O = 1.2; meq K→kg = 391) "
        "son constantes estequiométricas estándar utilizadas internacionalmente en ciencia del suelo. "
        "Los requerimientos por cultivo son valores promedio para condiciones colombianas y deben "
        "ajustarse según variedad, edad de la plantación y zona agroecológica."
    )

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center; color:#999; font-size:12px; padding:20px 0;'>"
    "FertiliApp v2.0 — William Fernando Cortés · 2026"
    "</div>",
    unsafe_allow_html=True,
)
