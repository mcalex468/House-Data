import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="IA Predictora Vivienda",
    layout="wide"
)

# ─────────────────────────────────────────────
# ESTILOS
# ─────────────────────────────────────────────

st.markdown("""
<style>

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    color: white;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.metric-card {
    background: linear-gradient(135deg, #0f3460 0%, #533483 100%);
    border-radius: 16px;
    padding: 24px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    margin-bottom: 12px;
}

.metric-card h1 {
    font-size: 3rem;
    margin: 8px 0;
    font-weight: 800;
}

.badge-up {
    background:#16a34a;
    border-radius:12px;
    padding:6px 16px;
    font-weight:700;
    color:white;
}

.badge-down {
    background:#dc2626;
    border-radius:12px;
    padding:6px 16px;
    font-weight:700;
    color:white;
}

.explain-box {
    background: #f8fafc;
    border-left: 4px solid #7c3aed;
    border-radius: 8px;
    padding: 20px;
    color: #1e293b;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CARGA
# ─────────────────────────────────────────────

@st.cache_resource
def load_assets():

    df = pd.read_csv(
        "house_data_gold.csv",
        encoding="utf-8-sig"
    )

    model = joblib.load(
        "modelo_ipv_v2.pkl"
    )

    return df, model

try:

    df, model = load_assets()

except Exception as e:

    st.error(f"Error cargando archivos: {e}")
    st.stop()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

CCAA_LIST = sorted(df["CCAA"].unique())

with st.sidebar:

    st.title("Simulador IA")

    idx_madrid = (
        CCAA_LIST.index("Madrid")
        if "Madrid" in CCAA_LIST
        else 0
    )

    ccaa = st.selectbox(
        "Selecciona CCAA",
        CCAA_LIST,
        index=idx_madrid
    )

    # Datos históricos
    df_ccaa = (
        df[df["CCAA"] == ccaa]
        .sort_values("Año")
    )

    last_real = df_ccaa.iloc[-1]

    ipv_anterior = float(
        last_real["Precio_Vivienda_IPV"]
    )

    st.divider()

    st.subheader("Variables Económicas")

    # ─────────────────────────────
    # RENTA
    # ─────────────────────────────

    renta_sim = st.number_input(
        "Renta Media (€)",
        min_value=5000.0,
        max_value=70000.0,
        value=float(last_real["Renta_Media"]),
        step=100.0
    )

    # ─────────────────────────────
    # IPC
    # ─────────────────────────────

    ipc_sim = st.number_input(
        "Índice IPC IA",
        min_value=10.0,
        max_value=40.0,
        value=float(last_real["Indice_IPC"]),
        step=0.01
    )

    # ─────────────────────────────
    # DEMOGRAFÍA
    # ─────────────────────────────

    st.divider()

    st.subheader("Demografía")

    pob_base = float(
        last_real["Pct_Pob_Joven"]
    )

    crecimiento_pob = st.slider(
        "Variación población joven (%)",
        min_value=-10.0,
        max_value=10.0,
        value=0.0,
        step=0.1
    )

    pob_joven_sim = (
        pob_base *
        (1 + crecimiento_pob / 100)
    )

    st.info(
        f"Población joven IA: {pob_joven_sim:.2f}%"
    )

    st.caption(
        f"IPV Base 2022: {ipv_anterior:.2f}"
    )

# ─────────────────────────────────────────────
# FEATURE ENGINEERING
# ─────────────────────────────────────────────

# NUEVA VERSIÓN CORREGIDA
renta_ajustada_sim = (
    renta_sim / ipc_sim
    if ipc_sim > 0
    else 0
)

# INPUT IA
input_df = pd.DataFrame([{

    "CCAA": ccaa,

    "Indice_IPC": ipc_sim,

    "Renta_Media": renta_sim,

    "Renta_Ajustada_IPC":
        renta_ajustada_sim,

    "Pct_Pob_Joven":
        pob_joven_sim,

    "IPV_Anterior":
        ipv_anterior
}])

# ─────────────────────────────────────────────
# PREDICCIÓN
# ─────────────────────────────────────────────

ipv_pred = model.predict(input_df)[0]

dif = ipv_pred - ipv_anterior

pct = (
    dif / ipv_anterior
) * 100

# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

st.title("IA Predictora Vivienda")

st.markdown(
    f"### Región: {ccaa}"
)

st.divider()

c1, c2, c3 = st.columns(3)

# ─────────────────────────────
# PREDICCIÓN
# ─────────────────────────────

with c1:

    st.markdown(f"""
    <div class="metric-card">
        <p>Predicción IA</p>
        <h1>{ipv_pred:.2f}</h1>
        <p>IPV Proyectado</p>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────
# BASE
# ─────────────────────────────

with c2:

    st.markdown(f"""
    <div class="metric-card" style="background:#1a6b5a">
        <p>IPV Histórico</p>
        <h1>{ipv_anterior:.2f}</h1>
        <p>Base 2022</p>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────
# DIFERENCIA
# ─────────────────────────────

with c3:

    badge = (
        "badge-up"
        if dif > 0
        else "badge-down"
    )

    st.markdown(f"""
    <div class="metric-card" style="background:#4338ca">
        <p>Variación</p>
        <h1>{dif:+.2f}</h1>
        <span class="{badge}">
            {pct:+.2f}%
        </span>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GRÁFICO
# ─────────────────────────────────────────────

fig = go.Figure()

fig.add_trace(

    go.Scatter(
        x=df_ccaa["Año"],
        y=df_ccaa["Precio_Vivienda_IPV"],
        name="Histórico",
        line=dict(width=4)
    )
)

fig.add_trace(

    go.Scatter(
        x=[2022, 2023],
        y=[ipv_anterior, ipv_pred],
        name="Simulación IA",
        line=dict(
            dash="dash",
            width=4
        ),
        marker=dict(
            size=12,
            symbol="star"
        )
    )
)

fig.update_layout(

    title=f"Evolución IPV - {ccaa}",

    hovermode="x unified",

    height=450,

    plot_bgcolor="white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ─────────────────────────────────────────────
# ANÁLISIS IA
# ─────────────────────────────────────────────

st.markdown("## Interpretación IA")

col1, col2 = st.columns(2)

with col1:

    st.markdown(f"""
    <div class="explain-box">

    <strong>Economía simulada</strong><br><br>

    • IPC IA: {ipc_sim:.2f}<br>
    • Renta media: {renta_sim:,.0f} €<br>
    • Población joven: {pob_joven_sim:.2f}%<br>

    </div>
    """, unsafe_allow_html=True)

with col2:

    tendencia = (
        "alcista"
        if dif > 0
        else "correctiva"
    )

    st.markdown(f"""
    <div class="explain-box">

    <strong>Diagnóstico IA</strong><br><br>

    El modelo detecta una tendencia
    <strong>{tendencia}</strong>
    respecto al IPV previo.

    La predicción está influida por:

    • inercia histórica<br>
    • renta regional<br>
    • presión económica<br>
    • demografía joven<br>

    </div>
    """, unsafe_allow_html=True)