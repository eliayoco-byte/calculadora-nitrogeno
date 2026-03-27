import { useState, useMemo } from "react";

const CULTIVOS = {
  "Café": { N: 200, P2O5: 50, K2O: 250 },
  "Cacao": { N: 100, P2O5: 60, K2O: 120 },
  "Caña de Azúcar": { N: 160, P2O5: 80, K2O: 190 },
  "Cítricos": { N: 150, P2O5: 45, K2O: 140 },
  "Manual": { N: 0, P2O5: 0, K2O: 0 },
};

const FERT_SIMPLES = {
  "Urea (46-0-0)": [46, 0, 0],
  "DAP (18-46-0)": [18, 46, 0],
  "MAP (11-52-0)": [11, 52, 0],
  "Cloruro de Potasio (0-0-60)": [0, 0, 60],
  "Sulfato de Amonio (21-0-0)": [21, 0, 0],
  "Superfosfato Triple (0-46-0)": [0, 46, 0],
  "Nitrato de Amonio (34-0-0)": [34, 0, 0],
};

const FERT_COMPUESTOS = {
  "17-6-18-2 (Completo)": [17, 6, 18],
  "Triple 15 (15-15-15)": [15, 15, 15],
  "10-30-10": [10, 30, 10],
  "15-4-23-4 (Cafetero)": [15, 4, 23],
  "13-26-6": [13, 26, 6],
  "10-20-20": [10, 20, 20],
  "25-4-24": [25, 4, 24],
};

const ALL_FERT = { ...FERT_SIMPLES, ...FERT_COMPUESTOS };


export default function FertiliApp() {
  const [crop, setCrop] = useState("Café");
  const [reqN, setReqN] = useState(CULTIVOS["Café"].N);
  const [reqP, setReqP] = useState(CULTIVOS["Café"].P2O5);
  const [reqK, setReqK] = useState(CULTIVOS["Café"].K2O);
  const [mo, setMo] = useState(3.0);
  const [pPpm, setPPpm] = useState(15.0);
  const [kMeq, setKMeq] = useState(0.25);
  const [da, setDa] = useState(1.25);
  const [prof, setProf] = useState(20);
  const [fracMin, setFracMin] = useState(0.02);
  const [fertTipo, setFertTipo] = useState("simple");
  const [fert, setFert] = useState("Urea (46-0-0)");
  const [simples, setSimples] = useState([
    { fert: "Urea (46-0-0)", objetivo: "N", activo: true },
    { fert: "DAP (18-46-0)", objetivo: "P", activo: false },
    { fert: "Cloruro de Potasio (0-0-60)", objetivo: "K", activo: false },
  ]);
  const [eficiencia, setEficiencia] = useState(60);
  const [precio, setPrecio] = useState(2300000);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showBalance, setShowBalance] = useState(false);
  const [showRefs, setShowRefs] = useState(false);

  function handleCropChange(c) {
    setCrop(c);
    setReqN(CULTIVOS[c].N);
    setReqP(CULTIVOS[c].P2O5);
    setReqK(CULTIVOS[c].K2O);
  }

  function updateSimple(idx, field, value) {
    setSimples(prev => prev.map((s, i) => i === idx ? { ...s, [field]: value } : s));
  }

  const calc = useMemo(() => {
    const masaSuelo = (prof / 100) * 10000 * (da * 1000);
    const nSuelo = (mo / 100) * masaSuelo * 0.05 * fracMin;
    const pSuelo = pPpm * 2 * (prof / 20) * 2.29;
    const kSuelo = kMeq * 391 * da * (prof / 10) * 1.2;
    const defN = Math.max(0, reqN - nSuelo);
    const defP = Math.max(0, reqP - pSuelo * 0.2);
    const defK = Math.max(0, reqK - kSuelo * 0.5);
    const eff = eficiencia / 100;

    if (fertTipo === "simple") {
      // Calcular cada simple activo según su objetivo
      const detalles = simples.filter(s => s.activo).map(s => {
        const comp = FERT_SIMPLES[s.fert] || [0,0,0];
        let deficit = 0;
        let concIdx = 0;
        if (s.objetivo === "N") { deficit = defN; concIdx = 0; }
        else if (s.objetivo === "P") { deficit = defP; concIdx = 1; }
        else { deficit = defK; concIdx = 2; }
        const necReal = deficit / eff;
        const conc = comp[concIdx];
        const kgProd = conc > 0 ? (necReal / conc) * 100 : 0;
        const bultos = kgProd / 50;
        const costo = (kgProd / 1000) * precio;
        return {
          nombre: s.fert, objetivo: s.objetivo,
          kgProd, bultos, costo,
          aporteN: (kgProd * comp[0]) / 100,
          aporteP: (kgProd * comp[1]) / 100,
          aporteK: (kgProd * comp[2]) / 100,
        };
      });
      const totalN = detalles.reduce((a, d) => a + d.aporteN, 0);
      const totalP = detalles.reduce((a, d) => a + d.aporteP, 0);
      const totalK = detalles.reduce((a, d) => a + d.aporteK, 0);
      const totalCosto = detalles.reduce((a, d) => a + d.costo, 0);
      const necRealN = defN / eff;
      const necRealP = defP / eff;
      const necRealK = defK / eff;
      return {
        nSuelo, pSuelo, kSuelo, defN, defP, defK, modo: "simple",
        detalles, totalN, totalP, totalK, totalCosto,
        faltaN: Math.max(0, necRealN - totalN),
        faltaP: Math.max(0, necRealP - totalP),
        faltaK: Math.max(0, necRealK - totalK),
      };
    } else {
      // Compuesto: lógica original
      const concN = ALL_FERT[fert][0];
      const concP = ALL_FERT[fert][1];
      const concK = ALL_FERT[fert][2];
      const necReal = defN / eff;
      const kgProd = concN > 0 ? (necReal / concN) * 100 : 0;
      const bultos = kgProd / 50;
      const costo = (kgProd / 1000) * precio;
      const aporteN = (kgProd * concN) / 100;
      const aporteP = (kgProd * concP) / 100;
      const aporteK = (kgProd * concK) / 100;
      const necRealP = defP / eff;
      const necRealK = defK / eff;
      const faltaP = Math.max(0, necRealP - aporteP);
      const faltaK = Math.max(0, necRealK - aporteK);
      const complementos = [];
      if (faltaP > 1) {
        const m = "DAP (18-46-0)";
        const c = FERT_SIMPLES[m][1];
        const kg = c > 0 ? (faltaP / c) * 100 : 0;
        complementos.push({ nombre: m, kg, bultos: kg / 50, nutriente: "P₂O₅", falta: faltaP });
      }
      if (faltaK > 1) {
        const m = "Cloruro de Potasio (0-0-60)";
        const c = FERT_SIMPLES[m][2];
        const kg = c > 0 ? (faltaK / c) * 100 : 0;
        complementos.push({ nombre: m, kg, bultos: kg / 50, nutriente: "K₂O", falta: faltaK });
      }
      return {
        nSuelo, pSuelo, kSuelo, defN, defP, defK, modo: "compuesto",
        kgProd, bultos, costo,
        aporteN, aporteP, aporteK,
        faltaP, faltaK, complementos,
      };
    }
  }, [mo, pPpm, kMeq, da, prof, fracMin, reqN, reqP, reqK, fert, fertTipo, simples, eficiencia, precio]);

  const F = {
    sans: "'Nunito', 'Segoe UI', sans-serif",
    display: "'Playfair Display', Georgia, serif",
  };

  const C = {
    bg: "#F4F1EC",
    card: "#FFFFFF",
    green1: "#2D6A4F",
    green2: "#40916C",
    green3: "#74C69D",
    greenPale: "#D8F3DC",
    earth: "#8B6F47",
    earthLight: "#D4C4A8",
    accent: "#E76F51",
    text: "#1B1B1B",
    muted: "#6B705C",
    blue: "#2C6E9B",
    blueLight: "#E3F0FA",
  };

  const s = {
    app: {
      fontFamily: F.sans, background: `linear-gradient(175deg, ${C.bg} 0%, #EDE8E0 100%)`,
      minHeight: "100vh", padding: "12px", maxWidth: 520, margin: "0 auto",
    },
    header: {
      textAlign: "center", padding: "28px 16px 18px", marginBottom: 8,
      background: `linear-gradient(135deg, ${C.green1} 0%, ${C.green2} 60%, ${C.green3} 100%)`,
      borderRadius: 20, color: "#fff", position: "relative", overflow: "hidden",
    },
    headerOverlay: {
      position: "absolute", top: 0, left: 0, right: 0, bottom: 0, opacity: 0.06,
      backgroundImage: `repeating-linear-gradient(45deg, transparent, transparent 20px, #fff 20px, #fff 21px)`,
    },
    headerTitle: { fontFamily: F.display, fontSize: 30, fontWeight: 700, margin: 0, position: "relative" },
    headerSub: { fontSize: 13, opacity: 0.85, marginTop: 4, position: "relative", letterSpacing: 0.5 },
    section: {
      background: C.card, borderRadius: 16, padding: "20px 18px", marginBottom: 12,
      boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
    },
    sectionNum: {
      display: "inline-flex", alignItems: "center", justifyContent: "center",
      width: 28, height: 28, borderRadius: "50%", background: C.green1, color: "#fff",
      fontSize: 14, fontWeight: 700, marginRight: 10,
    },
    sectionTitle: { fontSize: 17, fontWeight: 700, color: C.green1, display: "flex", alignItems: "center", marginBottom: 14 },
    label: { fontSize: 13, fontWeight: 600, color: C.muted, marginBottom: 5, display: "block" },
    input: {
      width: "100%", padding: "10px 12px", borderRadius: 10, border: `1.5px solid ${C.earthLight}`,
      fontSize: 15, fontFamily: F.sans, background: "#FAFAF7", outline: "none",
      transition: "border-color 0.2s",
    },
    select: {
      width: "100%", padding: "10px 12px", borderRadius: 10, border: `1.5px solid ${C.earthLight}`,
      fontSize: 15, fontFamily: F.sans, background: "#FAFAF7", cursor: "pointer", outline: "none",
    },
    row: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 },
    row3: { display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10 },
    chipRow: { display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 14 },
    chip: (active) => ({
      padding: "8px 14px", borderRadius: 20, fontSize: 13, fontWeight: 600,
      cursor: "pointer", border: `1.5px solid ${active ? C.green2 : C.earthLight}`,
      background: active ? C.greenPale : "#fff", color: active ? C.green1 : C.muted,
      transition: "all 0.2s", userSelect: "none",
    }),
    resultBox: {
      background: `linear-gradient(135deg, ${C.green1} 0%, ${C.green2} 100%)`,
      borderRadius: 16, padding: "22px 18px", marginBottom: 12, color: "#fff",
      boxShadow: "0 4px 16px rgba(45,106,79,0.25)",
    },
    resultBig: { fontSize: 38, fontWeight: 800, fontFamily: F.display, textAlign: "center", margin: "8px 0" },
    resultUnit: { fontSize: 15, fontWeight: 400, opacity: 0.85 },
    metricRow: { display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginTop: 14 },
    metric: {
      background: "rgba(255,255,255,0.15)", borderRadius: 12, padding: "12px 8px", textAlign: "center",
    },
    metricVal: { fontSize: 18, fontWeight: 700 },
    metricLabel: { fontSize: 11, opacity: 0.8, marginTop: 2 },
    expandBtn: {
      display: "flex", alignItems: "center", gap: 6, background: "none",
      border: "none", color: C.blue, fontSize: 13, fontWeight: 600,
      cursor: "pointer", padding: "6px 0", fontFamily: F.sans,
    },
    tag: (color) => ({
      display: "inline-block", padding: "4px 10px", borderRadius: 8,
      fontSize: 12, fontWeight: 600, background: color + "18", color: color,
    }),
    slider: { width: "100%", accentColor: C.green2 },
    warning: {
      background: "#FFF3E0", border: `1px solid #FFB74D`, borderRadius: 12,
      padding: "12px 16px", fontSize: 13, color: "#E65100", display: "flex", gap: 8, alignItems: "flex-start",
    },
    fieldGroup: { marginBottom: 14 },
    blueBox: {
      background: C.blueLight, borderRadius: 12, padding: "12px 14px", marginBottom: 14,
      fontSize: 13, color: C.blue, display: "flex", gap: 8, alignItems: "flex-start",
    },
    balanceRow: {
      display: "flex", justifyContent: "space-between", padding: "8px 0",
      borderBottom: `1px solid ${C.earthLight}`, fontSize: 14,
    },
  };

  return (
    <div style={s.app}>
      <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Playfair+Display:wght@700&display=swap" rel="stylesheet" />

      {/* HEADER */}
      <div style={s.header}>
        <div style={s.headerOverlay} />
        <div style={{ fontSize: 28, position: "relative", fontWeight: 700, letterSpacing: 2 }}>N · P · K</div>
        <h1 style={s.headerTitle}>FertiliApp</h1>
        <p style={s.headerSub}>Asistente de Fertilización N-P-K · William Fernando Cortés</p>
      </div>

      {/* SECTION 1: CULTIVO */}
      <div style={s.section}>
        <div style={s.sectionTitle}><span style={s.sectionNum}>1</span> Objetivo del Cultivo</div>
        <div style={s.chipRow}>
          {Object.keys(CULTIVOS).map((c) => (
            <div key={c} style={s.chip(crop === c)} onClick={() => handleCropChange(c)}>
              {c}
            </div>
          ))}
        </div>
        <div style={s.row3}>
          <div style={s.fieldGroup}>
            <label style={s.label}>Meta N</label>
            <input type="number" style={s.input} value={reqN} onChange={(e) => setReqN(+e.target.value || 0)} />
            <span style={{ fontSize: 11, color: C.muted }}>kg/ha</span>
          </div>
          <div style={s.fieldGroup}>
            <label style={s.label}>Meta P₂O₅</label>
            <input type="number" style={s.input} value={reqP} onChange={(e) => setReqP(+e.target.value || 0)} />
            <span style={{ fontSize: 11, color: C.muted }}>kg/ha</span>
          </div>
          <div style={s.fieldGroup}>
            <label style={s.label}>Meta K₂O</label>
            <input type="number" style={s.input} value={reqK} onChange={(e) => setReqK(+e.target.value || 0)} />
            <span style={{ fontSize: 11, color: C.muted }}>kg/ha</span>
          </div>
        </div>
      </div>

      {/* SECTION 2: ANÁLISIS DE SUELO */}
      <div style={{ ...s.section, borderLeft: `4px solid ${C.blue}` }}>
        <div style={s.sectionTitle}><span style={{ ...s.sectionNum, background: C.blue }}>2</span> Análisis de Suelo</div>
        <div style={s.blueBox}>
          <span style={{ fontWeight: 700 }}>Lab</span>
          <span>Ingrese los valores de su análisis de laboratorio</span>
        </div>
        <div style={s.fieldGroup}>
          <label style={s.label}>Materia Orgánica (%)</label>
          <input type="number" step="0.1" min="0" max="20" style={s.input} value={mo} onChange={(e) => setMo(+e.target.value || 0)} />
        </div>
        <div style={s.row}>
          <div style={s.fieldGroup}>
            <label style={s.label}>Fósforo (ppm)</label>
            <input type="number" step="0.1" min="0" max="500" style={s.input} value={pPpm} onChange={(e) => setPPpm(+e.target.value || 0)} />
          </div>
          <div style={s.fieldGroup}>
            <label style={s.label}>Potasio (meq/100g)</label>
            <input type="number" step="0.01" min="0" max="5" style={s.input} value={kMeq} onChange={(e) => setKMeq(+e.target.value || 0)} />
          </div>
        </div>

        <button style={s.expandBtn} onClick={() => setShowAdvanced(!showAdvanced)}>
          {showAdvanced ? "▾" : "▸"} Configuración Física del Suelo
        </button>
        {showAdvanced && (
          <div style={{ background: "#F8F8F4", borderRadius: 12, padding: 14, marginTop: 8 }}>
            <div style={s.row}>
              <div style={s.fieldGroup}>
                <label style={s.label}>Densidad Aparente (g/cm³)</label>
                <input type="number" step="0.01" min="0.5" max="1.7" style={s.input} value={da} onChange={(e) => setDa(+e.target.value || 1)} />
              </div>
              <div style={s.fieldGroup}>
                <label style={s.label}>Profundidad (cm)</label>
                <input type="number" min="10" max="40" style={s.input} value={prof} onChange={(e) => setProf(+e.target.value || 20)} />
              </div>
            </div>
            <div style={s.fieldGroup}>
              <label style={s.label}>Tasa de Mineralización del N</label>
              <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
                {[
                  { val: 0.01, label: "Baja", desc: "Suelos fríos, arcillosos o compactados" },
                  { val: 0.02, label: "Media", desc: "Condiciones templadas, textura franca" },
                  { val: 0.03, label: "Alta", desc: "Suelos cálidos, sueltos, bien aireados" },
                ].map((opt) => (
                  <button
                    key={opt.val}
                    onClick={() => setFracMin(opt.val)}
                    style={{
                      flex: 1, padding: "10px 6px", borderRadius: 10, cursor: "pointer",
                      border: fracMin === opt.val ? `2px solid ${C.green2}` : `1.5px solid ${C.earthLight}`,
                      background: fracMin === opt.val ? C.greenPale : "#fff",
                      fontFamily: F.sans, transition: "all 0.2s",
                    }}
                  >
                    <div style={{ fontSize: 13, fontWeight: 700, color: fracMin === opt.val ? C.green1 : C.text }}>{opt.label}</div>
                    <div style={{ fontSize: 10, color: C.muted, marginTop: 3, lineHeight: 1.3 }}>{opt.desc}</div>
                    <div style={{ fontSize: 10, color: C.muted, fontFamily: "monospace", marginTop: 3 }}>coef. {opt.val}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* SECTION 3: FERTILIZANTE */}
      <div style={s.section}>
        <div style={s.sectionTitle}><span style={{ ...s.sectionNum, background: C.earth }}>3</span> Fertilizante a Usar</div>
        
        {/* Tabs Simple / Compuesto */}
        <div style={{ display: "flex", gap: 0, marginBottom: 14, borderRadius: 10, overflow: "hidden", border: `1.5px solid ${C.earthLight}` }}>
          <button
            onClick={() => setFertTipo("simple")}
            style={{
              flex: 1, padding: "10px 0", border: "none", fontSize: 13, fontWeight: 700,
              fontFamily: F.sans, cursor: "pointer",
              background: fertTipo === "simple" ? C.earth : "#fff",
              color: fertTipo === "simple" ? "#fff" : C.muted,
              transition: "all 0.2s",
            }}
          >
            Simples (hasta 3)
          </button>
          <button
            onClick={() => { setFertTipo("compuesto"); setFert(Object.keys(FERT_COMPUESTOS)[0]); }}
            style={{
              flex: 1, padding: "10px 0", border: "none", fontSize: 13, fontWeight: 700,
              fontFamily: F.sans, cursor: "pointer",
              background: fertTipo === "compuesto" ? C.earth : "#fff",
              color: fertTipo === "compuesto" ? "#fff" : C.muted,
              borderLeft: `1px solid ${C.earthLight}`,
              transition: "all 0.2s",
            }}
          >
            Compuestos
          </button>
        </div>

        {fertTipo === "simple" ? (
          <div>
            {simples.map((sl, idx) => {
              const objetivoLabels = { N: "Nitrógeno", P: "Fósforo", K: "Potasio" };
              const comp = FERT_SIMPLES[sl.fert] || [0,0,0];
              return (
                <div key={idx} style={{
                  background: sl.activo ? "#FAFAF7" : "#f0f0ec",
                  borderRadius: 12, padding: "12px 14px", marginBottom: 10,
                  border: sl.activo ? `1.5px solid ${C.green2}` : `1px solid ${C.earthLight}`,
                  opacity: sl.activo ? 1 : 0.6, transition: "all 0.2s",
                }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: sl.activo ? 10 : 0 }}>
                    <label style={{ fontSize: 13, fontWeight: 700, color: C.green1, display: "flex", alignItems: "center", gap: 8 }}>
                      <input
                        type="checkbox"
                        checked={sl.activo}
                        onChange={(e) => updateSimple(idx, "activo", e.target.checked)}
                        style={{ accentColor: C.green2, width: 16, height: 16 }}
                      />
                      Fuente {idx + 1} — {objetivoLabels[sl.objetivo]}
                    </label>
                    {sl.activo && (
                      <div style={{ display: "flex", gap: 4 }}>
                        <span style={s.tag(C.green1)}>N {comp[0]}%</span>
                        <span style={s.tag(C.blue)}>P {comp[1]}%</span>
                        <span style={s.tag(C.accent)}>K {comp[2]}%</span>
                      </div>
                    )}
                  </div>
                  {sl.activo && (
                    <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 10 }}>
                      <select style={{ ...s.select, fontSize: 13 }} value={sl.fert} onChange={(e) => updateSimple(idx, "fert", e.target.value)}>
                        {Object.keys(FERT_SIMPLES).map((f) => (
                          <option key={f} value={f}>{f}</option>
                        ))}
                      </select>
                      <select
                        style={{ ...s.select, fontSize: 13, width: 80 }}
                        value={sl.objetivo}
                        onChange={(e) => updateSimple(idx, "objetivo", e.target.value)}
                      >
                        <option value="N">N</option>
                        <option value="P">P₂O₅</option>
                        <option value="K">K₂O</option>
                      </select>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div style={s.fieldGroup}>
            <label style={s.label}>Producto</label>
            <select style={s.select} value={fert} onChange={(e) => setFert(e.target.value)}>
              {Object.keys(FERT_COMPUESTOS).map((f) => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>
            <div style={{ display: "flex", gap: 6, marginTop: 8 }}>
              <span style={s.tag(C.green1)}>N {ALL_FERT[fert][0]}%</span>
              <span style={s.tag(C.blue)}>P {ALL_FERT[fert][1]}%</span>
              <span style={s.tag(C.accent)}>K {ALL_FERT[fert][2]}%</span>
            </div>
          </div>
        )}

        <div style={{ ...s.fieldGroup, marginTop: 14 }}>
          <label style={s.label}>Eficiencia de aplicación: <strong>{eficiencia}%</strong></label>
          <input type="range" min="20" max="100" style={s.slider} value={eficiencia} onChange={(e) => setEficiencia(+e.target.value)} />
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: C.muted }}>
            <span>20%</span><span>60%</span><span>100%</span>
          </div>
        </div>
        <div style={s.fieldGroup}>
          <label style={s.label}>Precio Tonelada (COP $)</label>
          <input type="number" min="500000" max="10000000" step="50000" style={s.input} value={precio} onChange={(e) => setPrecio(+e.target.value || 0)} />
        </div>
      </div>

      {/* SECTION 4: RESULTADOS */}
      <div style={s.resultBox}>
        <div style={{ fontSize: 15, fontWeight: 700, textAlign: "center", opacity: 0.9 }}>Recomendación Final</div>

        {calc.modo === "simple" ? (
          /* ========== RESULTADOS SIMPLES ========== */
          <div>
            {/* Detalle por cada fuente simple activa */}
            {calc.detalles.map((d, i) => (
              <div key={i} style={{
                background: "rgba(255,255,255,0.12)", borderRadius: 12, padding: "12px 14px",
                marginTop: 12, display: "flex", justifyContent: "space-between", alignItems: "center",
                flexWrap: "wrap", gap: 8,
              }}>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 700 }}>{d.nombre}</div>
                  <div style={{ fontSize: 11, opacity: 0.8 }}>Cubre: {d.objetivo === "N" ? "Nitrógeno" : d.objetivo === "P" ? "Fósforo (P₂O₅)" : "Potasio (K₂O)"}</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: 22, fontWeight: 800 }}>{d.kgProd.toFixed(1)} <span style={{ fontSize: 12, fontWeight: 400 }}>kg/ha</span></div>
                  <div style={{ fontSize: 12, opacity: 0.85 }}>{d.bultos.toFixed(1)} bultos · ${d.costo.toLocaleString("es-CO", { maximumFractionDigits: 0 })} COP</div>
                </div>
              </div>
            ))}

            {/* Totales de costo */}
            <div style={{ textAlign: "center", marginTop: 16, padding: "12px 0", borderTop: "1px solid rgba(255,255,255,0.2)" }}>
              <div style={{ fontSize: 12, opacity: 0.8 }}>Inversión total estimada</div>
              <div style={{ fontSize: 26, fontWeight: 800, marginTop: 4 }}>
                ${calc.totalCosto.toLocaleString("es-CO", { maximumFractionDigits: 0 })} <span style={{ fontSize: 13, fontWeight: 400 }}>COP/ha</span>
              </div>
            </div>

            {/* Aporte combinado N-P-K */}
            <div style={{ background: "rgba(255,255,255,0.12)", borderRadius: 12, padding: 14, marginTop: 12 }}>
              <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 10, opacity: 0.9 }}>
                Aporte combinado de las fuentes seleccionadas:
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
                {[
                  { label: "Nitrógeno", val: calc.totalN, unit: "kg N/ha", falta: calc.faltaN },
                  { label: "Fósforo", val: calc.totalP, unit: "kg P₂O₅/ha", falta: calc.faltaP },
                  { label: "Potasio", val: calc.totalK, unit: "kg K₂O/ha", falta: calc.faltaK },
                ].map((n, i) => (
                  <div key={i} style={{ background: "rgba(255,255,255,0.12)", borderRadius: 10, padding: "10px 6px", textAlign: "center" }}>
                    <div style={{ fontSize: 11, opacity: 0.7 }}>{n.label}</div>
                    <div style={{ fontSize: 18, fontWeight: 800 }}>{n.val.toFixed(1)}</div>
                    <div style={{ fontSize: 11, opacity: 0.7 }}>{n.unit}</div>
                    <div style={{ fontSize: 11, marginTop: 4, color: n.falta <= 1 ? "#A7F3D0" : "#FCA5A5" }}>
                      {n.falta <= 1 ? "✓ Cubierto" : `Faltan ${n.falta.toFixed(1)}`}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* ========== RESULTADOS COMPUESTO ========== */
          <div>
            <div style={{ textAlign: "center", marginTop: 6, fontSize: 13, opacity: 0.8 }}>
              Para cubrir Nitrógeno con <strong>{fert}</strong>
            </div>
            <div style={s.resultBig}>
              {calc.kgProd.toFixed(1)} <span style={s.resultUnit}>kg/ha</span>
            </div>

            <div style={s.metricRow}>
              <div style={s.metric}>
                <div style={s.metricVal}>{calc.bultos.toFixed(1)}</div>
                <div style={s.metricLabel}>Bultos 50kg</div>
              </div>
              <div style={s.metric}>
                <div style={s.metricVal}>${(calc.costo).toLocaleString("es-CO", { maximumFractionDigits: 0 })}</div>
                <div style={s.metricLabel}>COP/ha</div>
              </div>
              <div style={s.metric}>
                <div style={s.metricVal}>{calc.nSuelo.toFixed(0)}</div>
                <div style={s.metricLabel}>N suelo kg</div>
              </div>
            </div>

            {/* Aporte del compuesto */}
            <div style={{ background: "rgba(255,255,255,0.12)", borderRadius: 12, padding: 14, marginTop: 16 }}>
              <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 10, opacity: 0.9 }}>
                Con {calc.bultos.toFixed(1)} bultos de {fert} usted aporta:
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
                {[
                  { label: "Nitrógeno", val: calc.aporteN, unit: "kg N/ha", ok: calc.aporteN >= calc.defN, faltaMsg: `Faltan ${(calc.defN - calc.aporteN).toFixed(1)}` },
                  { label: "Fósforo", val: calc.aporteP, unit: "kg P₂O₅/ha", ok: calc.faltaP <= 1, faltaMsg: `Faltan ${calc.faltaP.toFixed(1)}` },
                  { label: "Potasio", val: calc.aporteK, unit: "kg K₂O/ha", ok: calc.faltaK <= 1, faltaMsg: `Faltan ${calc.faltaK.toFixed(1)}` },
                ].map((n, i) => (
                  <div key={i} style={{ background: "rgba(255,255,255,0.12)", borderRadius: 10, padding: "10px 6px", textAlign: "center" }}>
                    <div style={{ fontSize: 11, opacity: 0.7 }}>{n.label}</div>
                    <div style={{ fontSize: 18, fontWeight: 800 }}>{n.val.toFixed(1)}</div>
                    <div style={{ fontSize: 11, opacity: 0.7 }}>{n.unit}</div>
                    <div style={{ fontSize: 11, marginTop: 4, color: n.ok ? "#A7F3D0" : "#FCA5A5" }}>
                      {n.ok ? "✓ Cubierto" : n.faltaMsg}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Complementos sugeridos */}
            {calc.complementos && calc.complementos.length > 0 && (
              <div style={{
                background: "rgba(255,200,50,0.15)", border: "1px solid rgba(255,200,50,0.3)",
                borderRadius: 12, padding: 14, marginTop: 12,
              }}>
                <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 10 }}>
                  Sugerencia — Complementar con simples:
                </div>
                {calc.complementos.map((c, i) => (
                  <div key={i} style={{
                    background: "rgba(255,255,255,0.15)", borderRadius: 10, padding: "10px 14px",
                    marginBottom: i < calc.complementos.length - 1 ? 8 : 0,
                    display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 6,
                  }}>
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 700 }}>{c.nombre}</div>
                      <div style={{ fontSize: 11, opacity: 0.8 }}>Para cubrir {c.falta.toFixed(1)} kg de {c.nutriente}</div>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: 18, fontWeight: 800 }}>{c.kg.toFixed(1)} <span style={{ fontSize: 12, fontWeight: 400 }}>kg/ha</span></div>
                      <div style={{ fontSize: 12, opacity: 0.8 }}>{c.bultos.toFixed(1)} bultos</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Balance expandible — compartido */}
        <div style={{ display: "flex", justifyContent: "center", marginTop: 14 }}>
          <button
            onClick={() => setShowBalance(!showBalance)}
            style={{
              background: "rgba(255,255,255,0.2)", border: "1px solid rgba(255,255,255,0.3)",
              color: "#fff", padding: "8px 18px", borderRadius: 10, fontSize: 13,
              fontWeight: 600, cursor: "pointer", fontFamily: F.sans,
            }}
          >
            {showBalance ? "▾ Ocultar" : "▸ Ver"} detalle del suelo
          </button>
        </div>

        {showBalance && (
          <div style={{ background: "rgba(255,255,255,0.12)", borderRadius: 12, padding: 14, marginTop: 12, fontSize: 14 }}>
            <div style={{ ...s.balanceRow, borderColor: "rgba(255,255,255,0.15)" }}>
              <span>N disponible suelo</span>
              <strong>{calc.nSuelo.toFixed(1)} kg/ha</strong>
            </div>
            <div style={{ ...s.balanceRow, borderColor: "rgba(255,255,255,0.15)" }}>
              <span>P₂O₅ disponible suelo</span>
              <strong>{calc.pSuelo.toFixed(1)} kg/ha</strong>
            </div>
            <div style={{ ...s.balanceRow, borderColor: "rgba(255,255,255,0.15)" }}>
              <span>K₂O disponible suelo</span>
              <strong>{calc.kSuelo.toFixed(1)} kg/ha</strong>
            </div>
            <div style={{ ...s.balanceRow, borderColor: "rgba(255,255,255,0.15)" }}>
              <span>Déficit neto N</span>
              <strong>{calc.defN.toFixed(1)} kg/ha</strong>
            </div>
            <div style={{ ...s.balanceRow, borderColor: "rgba(255,255,255,0.15)" }}>
              <span>Déficit neto P₂O₅</span>
              <strong>{calc.defP.toFixed(1)} kg/ha</strong>
            </div>
            <div style={{ ...s.balanceRow, border: "none" }}>
              <span>Déficit neto K₂O</span>
              <strong>{calc.defK.toFixed(1)} kg/ha</strong>
            </div>
          </div>
        )}
      </div>

      {/* WARNING */}
      <div style={s.warning}>
        <span style={{ fontSize: 18 }}>⚠️</span>
        <span>Consulte siempre con un Ingeniero Agrónomo antes de la aplicación. Esta herramienta es orientativa y no reemplaza el criterio profesional.</span>
      </div>

      {/* REFERENCIAS BIBLIOGRÁFICAS */}
      <div style={{ ...s.section, borderTop: `3px solid ${C.green1}` }}>
        <button
          onClick={() => setShowRefs(!showRefs)}
          style={{
            width: "100%", background: "none", border: "none", cursor: "pointer",
            fontFamily: F.sans, display: "flex", alignItems: "center", justifyContent: "space-between",
            padding: 0,
          }}
        >
          <span style={{ fontSize: 15, fontWeight: 700, color: C.green1 }}>
            Base Metodológica y Referencias
          </span>
          <span style={{ fontSize: 13, color: C.muted }}>{showRefs ? "▾" : "▸"}</span>
        </button>

        {showRefs && (
          <div style={{ marginTop: 16, fontSize: 12.5, color: C.text, lineHeight: 1.7 }}>

            <div style={{ fontWeight: 700, color: C.green1, marginBottom: 6, fontSize: 13 }}>
              Fórmulas utilizadas
            </div>

            <div style={{ background: "#F8F8F4", borderRadius: 10, padding: 14, marginBottom: 14, fontFamily: "monospace", fontSize: 11.5, lineHeight: 1.8 }}>
              <div><strong>N disponible del suelo:</strong></div>
              <div style={{ paddingLeft: 12 }}>N = (MO/100) × Masa_suelo × 0.05 × Coef_min</div>
              <div style={{ paddingLeft: 12, color: C.muted }}>Masa_suelo = (Prof/100) × 10.000 m² × (DA × 1000)</div>
              <div style={{ marginTop: 8 }}><strong>P₂O₅ disponible (ppm → kg/ha):</strong></div>
              <div style={{ paddingLeft: 12 }}>P₂O₅ = ppm × 2 × (Prof/20) × 2.29</div>
              <div style={{ paddingLeft: 12, color: C.muted }}>Factor 2.29 = conversión P elemental a P₂O₅</div>
              <div style={{ marginTop: 8 }}><strong>K₂O disponible (meq/100g → kg/ha):</strong></div>
              <div style={{ paddingLeft: 12 }}>K₂O = meq × 391 × DA × (Prof/10) × 1.2</div>
              <div style={{ paddingLeft: 12, color: C.muted }}>Factor 1.2 = conversión K elemental a K₂O</div>
              <div style={{ marginTop: 8 }}><strong>Dosis de fertilizante:</strong></div>
              <div style={{ paddingLeft: 12 }}>kg/ha = (Déficit / Eficiencia) / (Concentración/100)</div>
            </div>

            <div style={{ fontWeight: 700, color: C.green1, marginBottom: 6, fontSize: 13 }}>
              Supuestos del modelo
            </div>
            <div style={{ background: "#F8F8F4", borderRadius: 10, padding: 14, marginBottom: 14, fontSize: 12, lineHeight: 1.7 }}>
              <div style={{ marginBottom: 4 }}>• El 5% de la materia orgánica del suelo corresponde a nitrógeno total (relación C:N ≈ 10:1, con 58% de C en la MO).</div>
              <div style={{ marginBottom: 4 }}>• Solo el 20% del P del suelo se considera rápidamente disponible para el cultivo en el ciclo productivo.</div>
              <div style={{ marginBottom: 4 }}>• Solo el 50% del K intercambiable del suelo se considera disponible para absorción en el ciclo.</div>
              <div style={{ marginBottom: 4 }}>• Coeficientes de mineralización: 1% (baja), 2% (media), 3% (alta), según temperatura y textura del suelo.</div>
              <div>• La eficiencia de aplicación ajusta pérdidas por volatilización, lixiviación y fijación.</div>
            </div>

            <div style={{ fontWeight: 700, color: C.green1, marginBottom: 6, fontSize: 13 }}>
              Requerimientos nutricionales de cultivos
            </div>
            <div style={{ background: "#F8F8F4", borderRadius: 10, padding: 14, marginBottom: 14, fontSize: 12, lineHeight: 1.7 }}>
              <div style={{ marginBottom: 4 }}>• <strong>Café:</strong> N=200, P₂O₅=50, K₂O=250 kg/ha — Basado en Sadeghian (2008), Cenicafé.</div>
              <div style={{ marginBottom: 4 }}>• <strong>Cacao:</strong> N=100, P₂O₅=60, K₂O=120 kg/ha — Basado en Fedecacao & ICA, Manual de fertilización.</div>
              <div style={{ marginBottom: 4 }}>• <strong>Caña de Azúcar:</strong> N=160, P₂O₅=80, K₂O=190 kg/ha — Basado en Cenicaña, Series técnicas.</div>
              <div>• <strong>Cítricos:</strong> N=150, P₂O₅=45, K₂O=140 kg/ha — Basado en ICA & Corpoica, Guía de manejo integrado.</div>
            </div>

            <div style={{ fontWeight: 700, color: C.green1, marginBottom: 6, fontSize: 13 }}>
              Referencias bibliográficas
            </div>
            <div style={{ fontSize: 12, lineHeight: 1.8, color: C.muted }}>
              <div style={{ marginBottom: 6 }}>
                [1] Havlin, J. L., Tisdale, S. L., Nelson, W. L., & Beaton, J. D. (2014). <em>Soil Fertility and Fertilizers: An Introduction to Nutrient Management</em> (8.ª ed.). Pearson Education.
              </div>
              <div style={{ marginBottom: 6 }}>
                [2] Sadeghian, S. (2008). <em>Fertilidad del suelo y nutrición del café en Colombia: Guía práctica</em>. Cenicafé, Boletín Técnico N.º 32. Chinchiná, Colombia.
              </div>
              <div style={{ marginBottom: 6 }}>
                [3] ICA – Instituto Colombiano Agropecuario. (2015). <em>Manual de fertilización y nutrición de cultivos tropicales</em>. Bogotá, Colombia.
              </div>
              <div style={{ marginBottom: 6 }}>
                [4] Osorio, N. W. (2014). Manejo de nutrientes en suelos del trópico. <em>Universidad Nacional de Colombia</em>, Sede Medellín. Editorial UNAL.
              </div>
              <div style={{ marginBottom: 6 }}>
                [5] Cenicaña. (2012). <em>El cultivo de la caña de azúcar en la zona azucarera de Colombia</em>. Centro de Investigación de la Caña de Azúcar de Colombia. Cali.
              </div>
              <div style={{ marginBottom: 6 }}>
                [6] Brady, N. C., & Weil, R. R. (2017). <em>The Nature and Properties of Soils</em> (15.ª ed.). Pearson.
              </div>
              <div style={{ marginBottom: 6 }}>
                [7] FAO. (2006). <em>Plant nutrition for food security: A guide for integrated nutrient management</em>. FAO Fertilizer and Plant Nutrition Bulletin, 16. Roma.
              </div>
              <div>
                [8] Fedecacao. (2013). <em>Guía técnica para el cultivo del cacao</em> (3.ª ed.). Federación Nacional de Cacaoteros. Bogotá, Colombia.
              </div>
            </div>

            <div style={{
              marginTop: 14, padding: "10px 14px", background: C.greenPale, borderRadius: 10,
              fontSize: 11.5, color: C.green1, lineHeight: 1.6,
            }}>
              <strong>Nota:</strong> Los factores de conversión (P→P₂O₅ = 2.29; K→K₂O = 1.2; meq K→kg = 391) son constantes estequiométricas estándar utilizadas internacionalmente en ciencia del suelo. Los requerimientos por cultivo son valores promedio para condiciones colombianas y deben ajustarse según variedad, edad de la plantación y zona agroecológica.
            </div>
          </div>
        )}
      </div>

      <div style={{ textAlign: "center", padding: "12px 0 24px", fontSize: 11, color: C.muted }}>
        FertiliApp v2.0 — William Fernando Cortés · 2026
      </div>
    </div>
  );
}
