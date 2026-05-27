"""
Simulador de Mercado e Intervenciones del Estado
Economía para Ingenieros — UNSTA
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Simulador de Mercado — UNSTA",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS Global ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

.block-container { padding-top: 1.2rem; padding-bottom: 1rem; }

/* ── METRIC CARDS ── */
.metric-grid { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 14px; }
.metric-card {
    background: #0f1117;
    border: 1px solid #2a2d3a;
    border-radius: 8px;
    padding: 12px 18px;
    min-width: 130px;
    flex: 1;
    transition: border-color .2s;
}
.metric-card:hover { border-color: #4a5080; }
.metric-card .m-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: #7a7f9a;
    font-family: 'IBM Plex Mono', monospace;
}
.metric-card .m-value {
    font-size: 20px;
    font-weight: 700;
    margin-top: 4px;
    font-family: 'IBM Plex Mono', monospace;
}
.metric-card .m-unit {
    font-size: 10px;
    color: #7a7f9a;
    margin-top: 1px;
    font-family: 'IBM Plex Mono', monospace;
}

/* ── INFO BOX ── */
.info-box {
    background: #0f1117;
    border-left: 3px solid #4a7cc7;
    border-radius: 0 6px 6px 0;
    padding: 14px 18px;
    font-size: 13.5px;
    color: #c8cdd8;
    margin-top: 14px;
    line-height: 1.75;
}
.info-box .section-title {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #4a7cc7;
    margin-bottom: 8px;
    font-family: 'IBM Plex Mono', monospace;
}

/* ── FORMULA BOX ── */
.formula-box {
    background: #12151f;
    border: 1px solid #2a2d3a;
    border-radius: 6px;
    padding: 12px 18px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    color: #e2c97e;
    margin: 10px 0;
    line-height: 2;
}

/* ── SECTION HEADER ── */
.section-header {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #4a7cc7;
    margin: 16px 0 8px 0;
    font-family: 'IBM Plex Mono', monospace;
    border-bottom: 1px solid #1e2130;
    padding-bottom: 4px;
}

/* ── WARNING / ALERT ── */
.alert-box {
    background: #1a0f0f;
    border-left: 3px solid #a32d2d;
    border-radius: 0 6px 6px 0;
    padding: 10px 16px;
    font-size: 13px;
    color: #e08080;
    margin-top: 10px;
}
.ok-box {
    background: #0b1a12;
    border-left: 3px solid #0f6e56;
    border-radius: 0 6px 6px 0;
    padding: 10px 16px;
    font-size: 13px;
    color: #70c9a4;
    margin-top: 10px;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: #090b0f;
    border-right: 1px solid #1e2130;
}
section[data-testid="stSidebar"] .stRadio > label {
    color: #a0a5b8 !important;
}

/* ── STREAMLIT OVERRIDES ── */
h1 { font-size: 1.5rem !important; color: #e8eaf0 !important; font-weight: 700 !important; }
h2 { color: #c8cdd8 !important; }
.stNumberInput label { font-size: 12px !important; color: #8a8fa8 !important; }
.stSelectbox label { font-size: 12px !important; color: #8a8fa8 !important; }
.stSlider label { font-size: 12px !important; color: #8a8fa8 !important; }
div[data-testid="stMetricValue"] { font-family: 'IBM Plex Mono', monospace !important; }
</style>
""", unsafe_allow_html=True)

# ── COLORES ──────────────────────────────────────────────────────────────────
C_DEM        = "#4a9eff"
C_OF         = "#3ecf8e"
C_EQ         = "#f0c040"
C_INT        = "#ff6b6b"
C_SUB        = "#56d9a0"
C_TAX_SHADE  = "rgba(255,107,107,0.12)"
C_SUB_SHADE  = "rgba(86,217,160,0.12)"
C_EQ_SHADE   = "rgba(240,192,64,0.12)"
BG_PLOT      = "#0c0e14"
BG_PAPER     = "#0c0e14"
GRID_COLOR   = "#1e2130"
LINE_ZERO    = "#2a2d3a"

# ── FUNCIONES ECONÓMICAS ─────────────────────────────────────────────────────

def equilibrio(a, b, c, d):
    if (b + d) == 0:
        return None, None
    Pe = (a - c) / (b + d)
    Qe = a - b * Pe
    return Pe, Qe

def curva_dem_p(a, b, q):
    return (a - q) / b

def curva_of_p(c, d, q):
    return (q - c) / d

def puntos_a_eq(p1, q1, p2, q2):
    if (p2 - p1) == 0:
        return None, None
    b = (q1 - q2) / (p2 - p1)
    a = q1 + b * p1
    return a, b

# ── GRÁFICO BASE (fondo negro) ───────────────────────────────────────────────

def fig_base(height=430):
    fig = go.Figure()
    fig.update_layout(
        margin=dict(l=55, r=25, t=45, b=55),
        height=height,
        xaxis_title="Cantidad (Q)",
        yaxis_title="Precio (P)",
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.01,
            xanchor="right", x=1,
            font=dict(size=11, color="#9aa0b8"),
            bgcolor="rgba(0,0,0,0)",
        ),
        plot_bgcolor=BG_PLOT,
        paper_bgcolor=BG_PAPER,
        xaxis=dict(
            gridcolor=GRID_COLOR,
            zeroline=True, zerolinecolor=LINE_ZERO,
            tickfont=dict(color="#6a7090", size=11, family="IBM Plex Mono"),
            title_font=dict(color="#8a8fa8", size=12),
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            zeroline=True, zerolinecolor=LINE_ZERO,
            tickfont=dict(color="#6a7090", size=11, family="IBM Plex Mono"),
            title_font=dict(color="#8a8fa8", size=12),
        ),
        font=dict(family="IBM Plex Sans", size=12, color="#c8cdd8"),
    )
    return fig


def add_dem_trace(fig, a, b, q_max, name="Demanda", color=None, dash=None):
    """Traza curva de demanda asegurando que se extienda hasta el primer cuadrante."""
    q = np.linspace(0, q_max, 400)
    p = curva_dem_p(a, b, q)
    mask = (p >= 0) & (q >= 0)
    lkw = dict(color=color or C_DEM, width=2.8)
    if dash:
        lkw["dash"] = dash
    fig.add_trace(go.Scatter(
        x=q[mask], y=p[mask], mode="lines", name=name,
        line=lkw, hovertemplate="Q=%{x:.2f}<br>P=%{y:.2f}<extra></extra>"
    ))


def add_of_trace(fig, c, d, q_max, name="Oferta", color=None, dash=None):
    """Traza curva de oferta asegurando que se extienda hasta el primer cuadrante."""
    q = np.linspace(0, q_max, 400)
    p = curva_of_p(c, d, q)
    mask = (p >= 0) & (q >= 0)
    lkw = dict(color=color or C_OF, width=2.8)
    if dash:
        lkw["dash"] = dash
    fig.add_trace(go.Scatter(
        x=q[mask], y=p[mask], mode="lines", name=name,
        line=lkw, hovertemplate="Q=%{x:.2f}<br>P=%{y:.2f}<extra></extra>"
    ))


def add_eq_point(fig, Qe, Pe, name="Equilibrio", color=None):
    c = color or C_EQ
    fig.add_trace(go.Scatter(
        x=[Qe], y=[Pe], mode="markers+text", name=name,
        marker=dict(color=c, size=12, symbol="circle",
                    line=dict(color="#0c0e14", width=2)),
        text=[f"  ({Qe:.1f}, {Pe:.1f})"],
        textposition="middle right",
        textfont=dict(color=c, size=11, family="IBM Plex Mono"),
        hovertemplate=f"Q={Qe:.2f}<br>P={Pe:.2f}<extra></extra>"
    ))
    # líneas punteadas al eje
    fig.add_shape(type="line", x0=0, x1=Qe, y0=Pe, y1=Pe,
                  line=dict(color=c, dash="dot", width=1))
    fig.add_shape(type="line", x0=Qe, x1=Qe, y0=0, y1=Pe,
                  line=dict(color=c, dash="dot", width=1))


def dead_weight_triangle(fig, q_int, q_eq, p_sup, p_eq, p_inf, color="rgba(255,200,60,0.18)", name="Pérdida irrecuperable"):
    """
    Dibuja de forma precisa el triángulo de DWL acotado entre Q intervenida y Q de equilibrio libre,
    uniendo ordenadamente los 3 vértices: (Q_int, P_superior) -> (Q_eq, P_equilibrio) -> (Q_int, P_inferior).
    """
    fig.add_trace(go.Scatter(
        x=[q_int, q_eq, q_int, q_int],
        y=[p_sup, p_eq, p_inf, p_sup],
        fill="toself",
        fillcolor=color,
        mode="lines",
        line=dict(color=color.replace("0.15", "0.6").replace("0.18", "0.6"), width=1.5, dash="dot"),
        name=name,
        hovertemplate=f"<b>{name}</b><extra></extra>"
    ))

# ── HELPERS UI ───────────────────────────────────────────────────────────────

def metric_card(label, value, unit="", color="#f0c040"):
    return f"""<div class="metric-card">
        <div class="m-label">{label}</div>
        <div class="m-value" style="color:{color}">{value}</div>
        <div class="m-unit">{unit}</div>
    </div>"""


def render_metrics(*items):
    html = '<div class="metric-grid">'
    for label, value, unit, color in items:
        html += metric_card(label, value, unit, color)
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def info_box(content, title="Fundamentación teórica"):
    st.markdown(
        f'<div class="info-box"><div class="section-title">{title}</div>{content}</div>',
        unsafe_allow_html=True
    )


def formula_box(lines):
    inner = "<br>".join(lines)
    st.markdown(f'<div class="formula-box">{inner}</div>', unsafe_allow_html=True)


def section_header(text):
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


def input_mercado_base(prefix):
    section_header("Función de demanda — Qd = a − b·P")
    c1, c2 = st.columns(2)
    a = c1.number_input("a (intercepto)", value=100.0, step=1.0, key=f"{prefix}_a")
    b = c2.number_input("b (pendiente)",  value=2.0,  step=0.5, key=f"{prefix}_b")
    section_header("Función de oferta — Qs = c + d·P")
    c3, c4 = st.columns(2)
    c_ = c3.number_input("c (intercepto)", value=20.0, step=1.0, key=f"{prefix}_c")
    d  = c4.number_input("d (pendiente)",  value=2.0,  step=0.5, key=f"{prefix}_d")
    return a, b, c_, d


def exportar_pdf_boton(fig, nombre):
    try:
        import kaleido  # noqa
        buf = io.BytesIO()
        fig.write_image(buf, format="pdf", width=900, height=500)
        buf.seek(0)
        st.download_button(
            label="Exportar gráfico PDF",
            data=buf,
            file_name=f"{nombre}.pdf",
            mime="application/pdf"
        )
    except Exception:
        pass  # kaleido puede no estar instalado

# ── SIDEBAR ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="padding:12px 0 8px 0;">
        <div style="font-size:18px; font-weight:700; color:#e8eaf0; font-family:'IBM Plex Mono',monospace;">
            SIMULADOR<br>DE MERCADO
        </div>
        <div style="font-size:11px; color:#5a607a; margin-top:4px; letter-spacing:.05em;">
            ECONOMÍA PARA INGENIEROS — UNSTA
        </div>
    </div>
    <hr style="border-color:#1e2130; margin:8px 0 14px 0;">
    """, unsafe_allow_html=True)

    modulo = st.radio(
        "",
        [
            "Introducción",
            "Mercado competitivo",
            "Elasticidad de demanda",
            "Precio máximo",
            "Precio mínimo",
            "Impuesto",
            "Subsidio",
            "Cuota",
        ],
        label_visibility="collapsed"
    )

    st.markdown("""
    <hr style="border-color:#1e2130; margin:14px 0 10px 0;">
    <div style="font-size:10px; color:#3a3f52; font-family:'IBM Plex Mono',monospace; line-height:1.7;">
        Modelo base:<br>
        Qd = a − b·P<br>
        Qs = c + d·P<br><br>
        Trabajo Práctico<br>
        Prof. Raúl García
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# INTRODUCCIÓN
# ═══════════════════════════════════════════════════════════════════════════════

if modulo == "Introducción":
    st.title("Simulador de Mercado e Intervenciones del Estado")

    st.markdown("""
    <div style="color:#7a7f9a; font-size:14px; margin-bottom:24px; line-height:1.8;">
    Esta aplicación permite modelar y analizar mercados competitivos bajo distintos
    escenarios de intervención estatal, aplicando los conceptos de la microeconomía
    estándar utilizados en el curso de Economía para Ingenieros de la UNSTA.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="info-box">
        <div class="section-title">Módulos disponibles</div>
        <b style="color:#e8eaf0">1. Mercado competitivo</b> — Equilibrio de oferta y demanda<br>
        <b style="color:#e8eaf0">2. Elasticidad de demanda</b> — Método del punto medio<br>
        <b style="color:#e8eaf0">3. Precio máximo</b> — Techo de precio, escasez<br>
        <b style="color:#e8eaf0">4. Precio mínimo</b> — Piso de precio, excedente<br>
        <b style="color:#e8eaf0">5. Impuesto</b> — Cuña fiscal, incidencia tributaria<br>
        <b style="color:#e8eaf0">6. Subsidio</b> — Efecto sobre bienestar<br>
        <b style="color:#e8eaf0">7. Cuota</b> — Renta de cuota, pérdida de eficiencia<br>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="info-box">
        <div class="section-title">Modelo base</div>
        Las funciones lineales de oferta y demanda adoptadas son:<br><br>
        <span style="font-family:'IBM Plex Mono',monospace; color:#e2c97e">
        Qd = a − b·P &nbsp;&nbsp;→ demanda inversa: P = (a − Q) / b<br>
        Qs = c + d·P &nbsp;&nbsp;→ oferta inversa: P = (Q − c) / d
        </span><br><br>
        El equilibrio se obtiene igualando Qd = Qs, lo que da:<br>
        <span style="font-family:'IBM Plex Mono',monospace; color:#e2c97e">
        P* = (a − c) / (b + d)<br>
        Q* = a − b·P*
        </span>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MERCADO COMPETITIVO
# ═══════════════════════════════════════════════════════════════════════════════

elif modulo == "Mercado competitivo":
    st.title("Módulo 1 — Mercado competitivo")

    col_ctrl, col_graf = st.columns([1, 2.2])

    with col_ctrl:
        a, b, c, d = input_mercado_base("mc")

        section_header("Modo de ingreso")
        modo = st.radio("Modo de ingreso:", ["Parámetros directos", "Desde dos puntos"], key="mc_modo",
                        label_visibility="collapsed")

        if modo == "Desde dos puntos":
            section_header("Demanda — dos puntos")
            cc1, cc2 = st.columns(2)
            dp1 = cc1.number_input("P₁", value=10.0, key="mc_dp1")
            dq1 = cc2.number_input("Q₁", value=80.0, key="mc_dq1")
            dp2 = cc1.number_input("P₂", value=30.0, key="mc_dp2")
            dq2 = cc2.number_input("Q₂", value=40.0, key="mc_dq2")
            section_header("Oferta — dos puntos")
            oc1, oc2 = st.columns(2)
            op1 = oc1.number_input("P₁", value=5.0,  key="mc_op1")
            oq1 = oc2.number_input("Q₁", value=10.0, key="mc_oq1")
            op2 = oc1.number_input("P₂", value=20.0, key="mc_op2")
            oq2 = oc2.number_input("Q₂", value=55.0, key="mc_oq2")
            a2, b2 = puntos_a_eq(dp1, dq1, dp2, dq2)
            c2, d2 = puntos_a_eq(op1, oq1, op2, oq2)
            if a2 and c2:
                a, b, c, d = a2, b2, c2, d2
                st.markdown(
                    f'<div class="formula-box">Qd = {a:.2f} − {b:.2f}·P<br>Qs = {c:.2f} + {d:.2f}·P</div>',
                    unsafe_allow_html=True
                )

    Pe, Qe = equilibrio(a, b, c, d)

    precio_max_demanda = a / b if b > 0 else 0
    exc_consumidor = 0.5 * Qe * (precio_max_demanda - Pe)

    if c > 0:
        piso_oferta = 0.0
        exc_productor = ((Qe + c) / 2) * Pe
    else:
        piso_oferta = max(0.0, -c / d) if d > 0 else 0
        exc_productor = 0.5 * Qe * (Pe - piso_oferta)

    with col_graf:
        if Pe and Qe and Pe > 0 and Qe > 0:
            render_metrics(
                ("Precio de equilibrio", f"${Pe:.2f}", "$/unidad", C_DEM),
                ("Cantidad de equilibrio", f"{Qe:.2f}", "unidades", C_OF),
                ("Excedente del consumidor", f"${exc_consumidor:.2f}", "$", C_EQ),
                ("Excedente del productor",  f"${exc_productor:.2f}", "$", C_SUB),
            )

            q_max = Qe * 2.0
            fig = fig_base()
            add_dem_trace(fig, a, b, q_max)
            add_of_trace(fig, c, d, q_max)
            add_eq_point(fig, Qe, Pe)

            q_fill = np.linspace(0, Qe, 200)
            p_dem_fill = curva_dem_p(a, b, q_fill)
            fig.add_trace(go.Scatter(
                x=np.append(q_fill, [Qe, 0]),
                y=np.append(p_dem_fill, [Pe, Pe]),
                fill="toself",
                fillcolor="rgba(74,158,255,0.10)",
                mode="lines",
                line=dict(width=0),
                name="Excedente consumidor",
                hoverinfo="skip"
            ))
            
            p_of_fill = curva_of_p(c, d, q_fill)
            p_of_fill_clipped = np.maximum(p_of_fill, 0)
            fig.add_trace(go.Scatter(
                x=np.append(q_fill, [Qe, 0]),
                y=np.append(p_of_fill_clipped, [Pe, piso_oferta]), 
                fill="toself",
                fillcolor="rgba(62,207,142,0.10)",
                mode="lines",
                line=dict(width=0),
                name="Excedente productor",
                hoverinfo="skip"
            ))
            
            fig.update_layout(title=dict(
                text="Mercado competitivo — Equilibrio",
                font=dict(color="#9aa0b8", size=13)
            ))
            st.plotly_chart(fig, use_container_width=True)

            info_box(
                f"El equilibrio de mercado se alcanza cuando la cantidad demandada iguala a la cantidad ofrecida. "
                f"A un precio de <b style='color:{C_DEM}'>${Pe:.2f}</b> por unidad, los consumidores desean comprar "
                f"exactamente las <b style='color:{C_OF}'>{Qe:.2f} unidades</b> que los productores están dispuestos a vender.<br><br>"
                f"En este punto no existe ni escasez ni excedente: el mercado se vacía. "
                f"Cualquier precio superior al de equilibrio generaría un excedente de oferta (los vendedores producen más de lo que el mercado absorbe), "
                f"mientras que un precio inferior produciría escasez (los compradores desean más de lo que se ofrece).<br><br>"
                f"Las áreas sombreadas representan el <b style='color:{C_DEM}'>excedente del consumidor</b> "
                f"(diferencia entre lo que los consumidores están dispuestos a pagar y lo que efectivamente pagan) "
                f"y el <b style='color:{C_OF}'>excedente del productor</b> (diferencia entre el ingreso obtenido y el costo mínimo de producción)."
            )
        else:
            st.markdown('<div class="alert-box">Los parámetros no producen un equilibrio válido en el primer cuadrante. Revisá los valores de a, b, c, d.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ELASTICIDAD
# ═══════════════════════════════════════════════════════════════════════════════

elif modulo == "Elasticidad de demanda":
    st.title("Módulo 2 — Elasticidad-precio de la demanda")

    col_ctrl, col_graf = st.columns([1, 2.2])

    with col_ctrl:
        section_header("Punto A")
        c1, c2 = st.columns(2)
        p1 = c1.number_input("Precio P₁", value=10.0, step=1.0, key="e_p1")
        q1 = c2.number_input("Cantidad Q₁", value=80.0, step=5.0, key="e_q1")

        section_header("Punto B")
        c3, c4 = st.columns(2)
        p2 = c3.number_input("Precio P₂", value=20.0, step=1.0, key="e_p2")
        q2 = c4.number_input("Cantidad Q₂", value=60.0, step=5.0, key="e_q2")

        section_header("Ingreso total")
        it1 = p1 * q1
        it2 = p2 * q2
        st.markdown(
            f'<div class="formula-box">'
            f'IT(A) = P₁ × Q₁ = {p1:.2f} × {q1:.2f}<br>'
            f'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; = <b>${it1:.2f}</b><br><br>'
            f'IT(B) = P₂ × Q₂ = {p2:.2f} × {q2:.2f}<br>'
            f'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; = <b>${it2:.2f}</b>'
            f'</div>',
            unsafe_allow_html=True
        )

    varQ = (q2 - q1) / ((q1 + q2) / 2) if (q1 + q2) != 0 else 0
    varP = (p2 - p1) / ((p1 + p2) / 2) if (p1 + p2) != 0 else 0
    Ed   = abs(varQ / varP) if varP != 0 else float("inf")

    if Ed > 1:
        tipo = "Elástica"; color_ed = C_DEM
        it_texto = "Al subir el precio, el ingreso total <b>disminuye</b> (los consumidores reducen mucho su compra)."
    elif Ed < 1:
        tipo = "Inelástica"; color_ed = C_INT
        it_texto = "Al subir el precio, el ingreso total <b>aumenta</b> (los consumidores reducen poco su compra)."
    else:
        tipo = "Unitaria"; color_ed = C_EQ
        it_texto = "Al subir el precio, el ingreso total <b>no varía</b> (el efecto precio y cantidad se compensan exactamente)."

    it_dir = "Aumenta" if it2 > it1 else ("Disminuye" if it2 < it1 else "Sin cambio")
    color_it = C_OF if it2 > it1 else (C_INT if it2 < it1 else C_EQ)

    with col_graf:
        render_metrics(
            ("Elasticidad |Ed|",   f"{Ed:.4f}", "adimensional", color_ed),
            ("Clasificación",       tipo,        "",             color_ed),
            ("IT en A",            f"${it1:.2f}", "$",           C_DEM),
            ("IT en B",            f"${it2:.2f}", "$",           C_OF),
            ("Variación del IT",   it_dir,        "",            color_it),
        )

        fig = fig_base()
        fig.add_trace(go.Scatter(
            x=[q1, q2], y=[p1, p2],
            mode="lines",
            name="Segmento de demanda",
            line=dict(color=C_DEM, width=2.8)
        ))
        fig.add_trace(go.Scatter(
            x=[q1], y=[p1], mode="markers+text", name="Punto A",
            marker=dict(color=C_EQ, size=14, line=dict(color=BG_PLOT, width=2)),
            text=["  A"], textposition="middle right",
            textfont=dict(color=C_EQ, size=13, family="IBM Plex Mono")
        ))
        fig.add_trace(go.Scatter(
            x=[q2], y=[p2], mode="markers+text", name="Punto B",
            marker=dict(color=C_INT, size=14, line=dict(color=BG_PLOT, width=2)),
            text=["  B"], textposition="middle right",
            textfont=dict(color=C_INT, size=13, family="IBM Plex Mono")
        ))
        fig.add_shape(type="rect", x0=0, x1=q1, y0=0, y1=p1,
                      fillcolor="rgba(74,158,255,0.07)", line_color="rgba(74,158,255,0.3)",
                      line_width=1)
        fig.add_shape(type="rect", x0=0, x1=q2, y0=0, y1=p2,
                      fillcolor="rgba(255,107,107,0.07)", line_color="rgba(255,107,107,0.3)",
                      line_width=1)
        fig.update_layout(title=dict(text="Elasticidad-precio de la demanda", font=dict(color="#9aa0b8", size=13)))
        st.plotly_chart(fig, use_container_width=True)

    formula_box([
        "Método del punto medio (Mankiw):",
        "",
        "       ΔQ / Q̄       (Q₂ − Q₁) / [(Q₁ + Q₂) / 2]",
        "Ed = ————————— = ————————————————————————————",
        "       ΔP / P̄       (P₂ − P₁) / [(P₁ + P₂) / 2]",
        "",
        f"Ed = ({q2:.2f} − {q1:.2f}) / [({q1:.2f} + {q2:.2f}) / 2]",
        f"   ÷ ({p2:.2f} − {p1:.2f}) / [({p1:.2f} + {p2:.2f}) / 2]",
        f"",
        f"   = {varQ:.4f} / {varP:.4f} = |{Ed:.4f}|",
    ])

    info_box(
        f"La elasticidad-precio de la demanda mide la <b>sensibilidad de los consumidores ante cambios en el precio</b>. "
        f"Se utiliza el método del punto medio para obtener un valor simétrico independientemente de la dirección del cambio.<br><br>"
        f"El valor obtenido <b style='color:{color_ed}'>|Ed| = {Ed:.4f}</b> indica que la demanda es <b style='color:{color_ed}'>{tipo}</b>: "
        f"ante un aumento del 1% en el precio, la cantidad demandada varía en un {Ed:.2f}%.<br><br>"
        f"{it_texto}<br><br>"
        f"<b>Regla del ingreso total:</b><br>"
        f"• Demanda elástica (|Ed| > 1): precio ↑ → IT ↓<br>"
        f"• Demanda inelástica (|Ed| < 1): precio ↑ → IT ↑<br>"
        f"• Demanda unitaria (|Ed| = 1): precio ↑ → IT sin cambio"
    )

# ═══════════════════════════════════════════════════════════════════════════════
# PRECIO MÁXIMO
# ═══════════════════════════════════════════════════════════════════════════════

elif modulo == "Precio máximo":
    st.title("Módulo 3 — Precio máximo (techo de precio)")

    col_ctrl, col_graf = st.columns([1, 2.2])

    with col_ctrl:
        a, b, c, d = input_mercado_base("pm")
        section_header("Intervención del Estado")
        pmax = st.number_input("Precio máximo (Pmáx)", value=15.0, step=1.0, key="pm_pmax")

    Pe, Qe = equilibrio(a, b, c, d)
    Qd_pm = a - b * pmax
    Qs_pm = c + d * pmax
    escasez = max(0.0, Qd_pm - Qs_pm)
    efectivo = pmax < Pe if Pe else False

    with col_graf:
        if Pe and Qe:
            render_metrics(
                ("P libre de equilibrio", f"${Pe:.2f}",    "$/unidad",  C_DEM),
                ("Precio máximo fijado",  f"${pmax:.2f}",  "$/unidad",  C_INT),
                ("Qd al precio máximo",   f"{Qd_pm:.2f}",  "unidades",  C_DEM),
                ("Qs al precio máximo",   f"{Qs_pm:.2f}",  "unidades",  C_OF),
                ("Escasez",               f"{escasez:.2f}", "unidades",  C_INT if escasez > 0 else C_OF),
            )

            q_max = max(Qe, Qd_pm, Qs_pm) * 1.7
            fig = fig_base()
            add_dem_trace(fig, a, b, q_max)
            add_of_trace(fig, c, d, q_max)
            add_eq_point(fig, Qe, Pe, "Eq. libre")

            fig.add_shape(type="line", x0=0, x1=q_max, y0=pmax, y1=pmax,
                          line=dict(color=C_INT, width=2, dash="dash"))
            fig.add_annotation(
                x=q_max * 0.9, y=pmax,
                text=f"Pmáx = {pmax:.1f}",
                showarrow=False,
                font=dict(color=C_INT, size=11, family="IBM Plex Mono"),
                yshift=12
            )

            if escasez > 0:
                fig.add_trace(go.Scatter(
                    x=[Qs_pm, Qd_pm], y=[pmax, pmax],
                    mode="lines+markers",
                    name=f"Escasez ({escasez:.1f} u.)",
                    line=dict(color=C_INT, width=4),
                    marker=dict(size=9, color=C_INT)
                ))

                # Pérdida irrecuperable (DWL CORREGIDA)
                p_dem_at_qs = curva_dem_p(a, b, Qs_pm)
                dead_weight_triangle(fig, Qs_pm, Qe, p_dem_at_qs, Pe, pmax,
                                     color="rgba(255,200,60,0.15)", name="Pérdida irrecuperable (DWL)")

            fig.update_layout(title=dict(text="Precio máximo — Techo de precio", font=dict(color="#9aa0b8", size=13)))
            st.plotly_chart(fig, use_container_width=True)

            if efectivo:
                st.markdown(
                    f'<div class="alert-box"><b>Precio máximo efectivo:</b> Pmáx = ${pmax:.2f} está por debajo del precio de equilibrio libre (${Pe:.2f}). '
                    f'La intervención altera efectivamente el mercado, generando escasez de {escasez:.2f} unidades.</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="ok-box"><b>Precio máximo no efectivo:</b> Pmáx = ${pmax:.2f} está por encima del precio de equilibrio libre (${Pe:.2f}). '
                    f'El mercado sigue operando en su equilibrio natural; la intervención no tiene efecto real.</div>',
                    unsafe_allow_html=True
                )

            info_box(
                f"Un precio máximo (o <i>techo de precio</i>) es una regulación estatal que prohíbe cobrar por encima de un nivel determinado. "
                f"Su objetivo habitual es proteger a los consumidores de precios considerados excesivos.<br><br>"
                f"<b>Condición de efectividad:</b> el precio máximo solo altera el funcionamiento del mercado si se fija <b>por debajo del precio de equilibrio libre</b> (P* = ${Pe:.2f}). "
                f"De lo contrario, el mercado converge de todos modos al equilibrio sin restricción.<br><br>"
                f"Cuando el precio máximo es efectivo (Pmáx = ${pmax:.2f} {'< ' if efectivo else '> '}P* = ${Pe:.2f}), "
                f"los productores reducen su oferta (Qs = {Qs_pm:.2f}) mientras los consumidores demandan más (Qd = {Qd_pm:.2f}), "
                f"generando una <b style='color:{C_INT}'>escasez de {escasez:.2f} unidades</b>.<br><br>"
                f"La intervención produce además una <b style='color:#f0c040'>pérdida irrecuperable de bienestar</b> (área triangular en el gráfico): "
                f"transacciones mutuamente beneficiosas que dejan de realizarse."
            )

# ═══════════════════════════════════════════════════════════════════════════════
# PRECIO MÍNIMO
# ═══════════════════════════════════════════════════════════════════════════════

elif modulo == "Precio mínimo":
    st.title("Módulo 4 — Precio mínimo (piso de precio)")

    col_ctrl, col_graf = st.columns([1, 2.2])

    with col_ctrl:
        a, b, c, d = input_mercado_base("pn")
        section_header("Intervención del Estado")
        pmin = st.number_input("Precio mínimo (Pmín)", value=25.0, step=1.0, key="pn_pmin")

    Pe, Qe = equilibrio(a, b, c, d)
    Qd_pmin = a - b * pmin
    Qs_pmin = c + d * pmin
    excedente = max(0.0, Qs_pmin - Qd_pmin)
    efectivo = pmin > Pe if Pe else False

    with col_graf:
        if Pe and Qe:
            render_metrics(
                ("P libre de equilibrio", f"${Pe:.2f}",      "$/unidad",  C_DEM),
                ("Precio mínimo fijado",  f"${pmin:.2f}",    "$/unidad",  "#f0c040"),
                ("Qd al precio mínimo",   f"{Qd_pmin:.2f}",  "unidades",  C_DEM),
                ("Qs al precio mínimo",   f"{Qs_pmin:.2f}",  "unidades",  C_OF),
                ("Excedente de oferta",   f"{excedente:.2f}", "unidades",  "#f0c040" if excedente > 0 else C_OF),
            )

            q_max = max(Qe, Qs_pmin, Qd_pmin) * 1.7
            fig = fig_base()
            add_dem_trace(fig, a, b, q_max)
            add_of_trace(fig, c, d, q_max)
            add_eq_point(fig, Qe, Pe, "Eq. libre")

            fig.add_shape(type="line", x0=0, x1=q_max, y0=pmin, y1=pmin,
                          line=dict(color="#f0c040", width=2, dash="dash"))
            fig.add_annotation(
                x=q_max * 0.9, y=pmin,
                text=f"Pmín = {pmin:.1f}",
                showarrow=False,
                font=dict(color="#f0c040", size=11, family="IBM Plex Mono"),
                yshift=12
            )

            if excedente > 0 and Qd_pmin > 0:
                fig.add_trace(go.Scatter(
                    x=[Qd_pmin, Qs_pmin], y=[pmin, pmin],
                    mode="lines+markers",
                    name=f"Excedente oferta ({excedente:.1f} u.)",
                    line=dict(color="#f0c040", width=4),
                    marker=dict(size=9, color="#f0c040")
                ))
                
                # Pérdida irrecuperable (DWL CORREGIDA)
                p_of_at_qd = curva_of_p(c, d, Qd_pmin)
                dead_weight_triangle(fig, Qd_pmin, Qe, pmin, Pe, p_of_at_qd,
                                     color="rgba(255,200,60,0.15)", name="Pérdida irrecuperable (DWL)")

            fig.update_layout(title=dict(text="Precio mínimo — Piso de precio", font=dict(color="#9aa0b8", size=13)))
            st.plotly_chart(fig, use_container_width=True)

            if efectivo:
                st.markdown(
                    f'<div class="alert-box"><b>Precio mínimo efectivo:</b> Pmín = ${pmin:.2f} está por encima del precio de equilibrio libre (${Pe:.2f}). '
                    f'La intervención genera un excedente de oferta de {excedente:.2f} unidades.</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="ok-box"><b>Precio mínimo no efectivo:</b> Pmín = ${pmin:.2f} está por debajo del precio de equilibrio libre (${Pe:.2f}). '
                    f'El mercado opera naturalmente en su equilibrio sin restricción efectiva.</div>',
                    unsafe_allow_html=True
                )

            info_box(
                f"Un precio mínimo (o <i>piso de precio</i>) es una regulación estatal que prohíbe vender por debajo de un nivel determinado. "
                f"Su objetivo típico es garantizar ingresos mínimos a los productores (ej.: salario mínimo, precios agrícolas garantizados).<br><br>"
                f"<b>Condición de efectividad:</b> el precio mínimo solo altera el funcionamiento del mercado si se fija <b>por encima del precio de equilibrio libre</b> (P* = ${Pe:.2f}). "
                f"De lo contrario, el mercado alcanza su equilibrio sin que la regulación interfiera.<br><br>"
                f"Cuando el precio mínimo es efectivo (Pmín = ${pmin:.2f} {'> ' if efectivo else '< '}P* = ${Pe:.2f}), "
                f"los productores desean ofrecer más (Qs = {Qs_pmin:.2f}) de lo que los consumidores demandan (Qd = {Qd_pmin:.2f}), "
                f"generando un <b style='color:#f0c040'>excedente de oferta de {excedente:.2f} unidades</b>.<br><br>"
                f"La cantidad efectivamente transada es la menor entre oferta y demanda: <b>Q_transada = {min(Qd_pmin, Qs_pmin):.2f} u.</b> "
                f"Se produce también una <b style='color:#f0c040'>pérdida irrecuperable de eficiencia</b> (área triangular en el gráfico)."
            )

# ═══════════════════════════════════════════════════════════════════════════════
# IMPUESTO
# ═══════════════════════════════════════════════════════════════════════════════

elif modulo == "Impuesto":
    st.title("Módulo 5 — Impuesto: cuña fiscal e incidencia")

    col_ctrl, col_graf = st.columns([1, 2.2])

    with col_ctrl:
        a, b, c, d = input_mercado_base("imp")
        section_header("Impuesto")
        t     = st.number_input("Monto del impuesto (t)", value=10.0, min_value=0.0, step=1.0, key="imp_t")
        sobre = st.selectbox("Recae formalmente sobre", ["Vendedor", "Comprador"], key="imp_sobre")

        section_header("Incidencia tributaria — análisis")
        st.markdown("""
        <div style="font-size:12px; color:#7a7f9a; line-height:1.8;">
        La incidencia real del impuesto<br>
        no depende de quién lo paga<br>
        formalmente, sino de las<br>
        <b style="color:#c8cdd8">elasticidades relativas</b> de<br>
        oferta y demanda.
        </div>
        """, unsafe_allow_html=True)

    Pe, Qe = equilibrio(a, b, c, d)

    if sobre == "Vendedor":
        c2 = c - t * d
        Pe_c, Qe_t = equilibrio(a, b, c2, d)
        Pe_v = (Pe_c - t) if Pe_c else None
    else:
        a2 = a - t * b
        Pe_v, Qe_t = equilibrio(a2, b, c, d)
        Pe_c = (Pe_v + t) if Pe_v else None

    with col_graf:
        if Pe and Qe and Pe_c and Pe_v and Qe_t:
            recaudacion  = t * Qe_t
            inc_c = (Pe_c - Pe) / t if t else 0
            inc_v = (Pe - Pe_v) / t if t else 0

            render_metrics(
                ("P libre de equilibrio",  f"${Pe:.2f}",          "$/unidad",   C_EQ),
                ("P comprador (Pc)",        f"${Pe_c:.2f}",        "$/unidad",   C_INT),
                ("P vendedor (Pv)",         f"${Pe_v:.2f}",        "$/unidad",   C_OF),
                ("Q con impuesto",          f"{Qe_t:.2f}",         "unidades",   C_DEM),
                ("Recaudación fiscal",      f"${recaudacion:.2f}", "$",           C_EQ),
                ("Incid. comprador",        f"{inc_c*100:.1f}%",   "del impuesto", C_INT),
                ("Incid. vendedor",         f"{inc_v*100:.1f}%",   "del impuesto", C_OF),
            )

            q_max = max(Qe, Qe_t) * 1.8
            fig = fig_base()
            add_dem_trace(fig, a, b, q_max, "Demanda")
            add_of_trace(fig, c, d, q_max, "Oferta original")

            if sobre == "Vendedor":
                add_of_trace(fig, c2, d, q_max, "Oferta + impuesto", color=C_INT, dash="dash")
            else:
                add_dem_trace(fig, a - t * b, b, q_max, "Demanda − impuesto", color=C_INT, dash="dash")

            add_eq_point(fig, Qe, Pe, "Eq. sin impuesto", color=C_EQ)
            add_eq_point(fig, Qe_t, Pe_c, "Precio comprador", color=C_INT)

            fig.add_trace(go.Scatter(
                x=[Qe_t, Qe_t], y=[Pe_v, Pe_c],
                mode="lines+markers",
                name=f"Cuña fiscal (${t:.2f})",
                line=dict(color=C_INT, width=5),
                marker=dict(size=8, color=C_INT)
            ))

            fig.add_shape(type="rect", x0=0, x1=Qe_t, y0=Pe_v, y1=Pe_c,
                          fillcolor=C_TAX_SHADE,
                          line_color="rgba(255,107,107,0.25)", line_width=1)

            # Pérdida irrecuperable (DWL CORREGIDA)
            dead_weight_triangle(fig, Qe_t, Qe, Pe_c, Pe, Pe_v,
                                 color="rgba(255,200,60,0.15)", name="Pérdida irrecuperable (DWL)")

            fig.update_layout(title=dict(text="Impuesto — Cuña fiscal e incidencia", font=dict(color="#9aa0b8", size=13)))
            st.plotly_chart(fig, use_container_width=True)

            formula_box([
                f"Recaudación = t × Q' = ${t:.2f} × {Qe_t:.2f} = ${recaudacion:.2f}",
                "",
                f"Incidencia comprador = (Pc − Pe) / t = ({Pe_c:.2f} − {Pe:.2f}) / {t:.2f} = {inc_c*100:.1f}%",
                f"Incidencia vendedor  = (Pe − Pv) / t = ({Pe:.2f} − {Pe_v:.2f}) / {t:.2f} = {inc_v*100:.1f}%",
            ])

            info_box(
                f"El impuesto de <b style='color:{C_EQ}'>${t:.2f}</b> por unidad genera una <b>cuña fiscal</b> entre el precio que "
                f"paga el comprador (Pc = ${Pe_c:.2f}) y el precio que recibe el vendedor (Pv = ${Pe_v:.2f}). "
                f"La diferencia entre ambos es exactamente el monto del impuesto: Pc − Pv = ${Pe_c - Pe_v:.2f}.<br><br>"
                f"<b>Incidencia económica vs. legal:</b> aunque el impuesto recae formalmente sobre el {sobre.lower()}, "
                f"la carga real se distribuye entre ambos agentes según sus elasticidades. "
                f"El comprador absorbe el <b style='color:{C_INT}'>{inc_c*100:.1f}%</b> y el vendedor el <b style='color:{C_OF}'>{inc_v*100:.1f}%</b>.<br><br>"
                f"<b>Regla general:</b> cuanto más inelástica es la curva de un agente (menor sensibilidad al precio), "
                f"mayor es la parte del impuesto que termina soportando. "
                f"Si la demanda es perfectamente inelástica, el comprador absorbe el 100% del impuesto; "
                f"si la oferta es perfectamente inelástica, el vendedor absorbe el 100%.<br><br>"
                f"La <b style='color:#f0c040'>pérdida irrecuperable de bienestar</b> (triángulo DWL) represents las "
                f"transacciones que se dejaron de realizar debido al impuesto: hay un costo social neto "
                f"sobre y por encima de lo que recauda el Estado.",
                title="Cuña fiscal e incidencia tributaria"
            )

# ═══════════════════════════════════════════════════════════════════════════════
# SUBSIDIO
# ═══════════════════════════════════════════════════════════════════════════════

elif modulo == "Subsidio":
    st.title("Módulo 6 — Subsidio: efecto sobre equilibrio y bienestar")

    col_ctrl, col_graf = st.columns([1, 2.2])

    with col_ctrl:
        a, b, c, d = input_mercado_base("sub")
        section_header("Subsidio")
        s     = st.number_input("Monto del subsidio (s)", value=8.0, min_value=0.0, step=1.0, key="sub_s")
        sobre = st.selectbox("Recae formalmente sobre", ["Vendedor", "Comprador"], key="sub_sobre")

    Pe, Qe = equilibrio(a, b, c, d)

    if sobre == "Vendedor":
        c2 = c + s * d
        a2=a
        Pe_c, Qe_s = equilibrio(a, b, c2, d)
        Pe_v = (Pe_c + s) if Pe_c else None
    else:
        a2 = a + s * b
        c2=c
        Pe_c, Qe_s = equilibrio(a2, b, c, d)
        Pe_v = (Pe_c + s) if Pe_c else None

    with col_graf:
        if Pe and Qe and Pe_c and Pe_v and Qe_s:
            costo_total  = s * Qe_s
            gan_c        = Pe - Pe_c
            gan_v        = Pe_v - Pe
            inc_c        = gan_c / s if s else 0
            inc_v        = gan_v / s if s else 0

            render_metrics(
                ("P libre de equilibrio",  f"${Pe:.2f}",          "$/unidad",   C_EQ),
                ("P comprador (Pc)",        f"${Pe_c:.2f}",        "$/unidad",   C_SUB),
                ("P vendedor (Pv)",         f"${Pe_v:.2f}",        "$/unidad",   C_OF),
                ("Q con subsidio",          f"{Qe_s:.2f}",         "unidades",   C_DEM),
                ("Costo fiscal total",      f"${costo_total:.2f}", "$",           C_INT),
                ("Ganancia comprador",      f"${gan_c:.2f}",       "$/unidad",   C_SUB),
                ("Ganancia vendedor",       f"${gan_v:.2f}",       "$/unidad",   C_OF),
                ("Incid. comprador",        f"{inc_c*100:.1f}%",   "del subsidio", C_SUB),
                ("Incid. vendedor",         f"{inc_v*100:.1f}%",   "del subsidio", C_OF),
            )

            q_max = max(Qe, Qe_s) * 1.8
            fig = fig_base()
            add_dem_trace(fig, a, b, q_max, "Demanda")
            add_of_trace(fig, c, d, q_max, "Oferta original")
            if sobre == "Vendedor":
                add_of_trace(fig, c2, d, q_max, "Oferta + subsidio", color=C_SUB, dash="dash")

            add_eq_point(fig, Qe, Pe, "Eq. sin subsidio", color=C_EQ)
            add_eq_point(fig, Qe_s, Pe_c, "Precio comprador", color=C_SUB)

            fig.add_trace(go.Scatter(
                x=[Qe_s, Qe_s], y=[Pe_c, Pe_v],
                mode="lines+markers",
                name=f"Brecha subsidio (${s:.2f})",
                line=dict(color=C_SUB, width=5),
                marker=dict(size=8, color=C_SUB)
            ))

            fig.add_shape(type="rect", x0=0, x1=Qe_s, y0=Pe_c, y1=Pe_v,
                          fillcolor=C_SUB_SHADE,
                          line_color="rgba(86,217,160,0.25)", line_width=1)

            fig.update_layout(title=dict(text="Subsidio — Efecto sobre el equilibrio", font=dict(color="#9aa0b8", size=13)))
            st.plotly_chart(fig, use_container_width=True)

            formula_box([
                f"Costo fiscal total = s × Q' = ${s:.2f} × {Qe_s:.2f} = ${costo_total:.2f}",
                "",
                f"Ganancia comprador = Pe − Pc = {Pe:.2f} − {Pe_c:.2f} = ${gan_c:.2f}/u.",
                f"Ganancia vendedor  = Pv − Pe = {Pe_v:.2f} − {Pe:.2f} = ${gan_v:.2f}/u.",
                "",
                f"Incidencia comprador = {inc_c*100:.1f}% del subsidio",
                f"Incidencia vendedor  = {inc_v*100:.1f}% del subsidio",
            ])

            info_box(
                f"El subsidio de <b style='color:{C_SUB}'>${s:.2f}</b> por unidad actúa como una cuña positiva: "
                f"reduce el precio que paga el comprador (de ${Pe:.2f} a <b style='color:{C_SUB}'>${Pe_c:.2f}</b>) "
                f"y aumenta el precio que recibe el vendedor (de ${Pe:.2f} a <b style='color:{C_OF}'>${Pe_v:.2f}</b>). "
                f"La diferencia entre ambos precios es exactamente el monto del subsidio: Pv − Pc = ${Pe_v - Pe_c:.2f}.<br><br>"
                f"<b>Distribución del beneficio:</b> al igual que con el impuesto, la incidencia económica del subsidio "
                f"no depende de quién lo recibe formalmente, sino de las elasticidades relativas. "
                f"El comprador captura <b style='color:{C_SUB}'>${gan_c:.2f}</b> por unidad y el vendedor <b style='color:{C_OF}'>${gan_v:.2f}</b>. "
                f"El agente con la curva más inelástica captura una mayor proporción del subsidio.<br><br>"
                f"<b>Costo fiscal:</b> el Estado debe financiar ${costo_total:.2f} en total (s × Q'). "
                f"Los subsidios aumentan la cantidad transada (de {Qe:.2f} a {Qe_s:.2f} u.) pero implican un "
                f"costo social neto, ya que parte de las unidades adicionales tienen un valor social "
                f"menor que su costo de producción."
            )

# ═══════════════════════════════════════════════════════════════════════════════
# CUOTA
# ═══════════════════════════════════════════════════════════════════════════════

elif modulo == "Cuota":
    st.title("Módulo 7 — Cuota de producción")

    col_ctrl, col_graf = st.columns([1, 2.2])

    with col_ctrl:
        a, b, c, d = input_mercado_base("cu")
        section_header("Cuota")
        qbar = st.number_input("Cantidad máxima Q̄", value=30.0, min_value=0.1, step=1.0, key="cu_qbar")

    Pe, Qe = equilibrio(a, b, c, d)
    P_cuota  = (a - qbar) / b if b != 0 else None
    P_of_cuota = (qbar - c) / d if d != 0 else None

    with col_graf:
        if Pe and Qe and P_cuota and P_of_cuota:
            dp    = P_cuota - Pe
            renta = (P_cuota - P_of_cuota) * qbar

            render_metrics(
                ("P libre (sin cuota)",   f"${Pe:.2f}",         "$/unidad",  C_DEM),
                ("P con cuota (Pd)",       f"${P_cuota:.2f}",   "$/unidad",  C_INT),
                ("Alza de precio",         f"+${dp:.2f}",        "$/unidad",  C_INT if dp > 0 else C_OF),
                ("Q sin cuota",            f"{Qe:.2f}",          "unidades",  C_DEM),
                ("Q con cuota",            f"{qbar:.2f}",        "unidades",  C_EQ),
                ("Renta de cuota",         f"${renta:.2f}",      "$",         C_EQ),
            )

            q_max = max(Qe, qbar) * 1.8
            fig = fig_base()
            add_dem_trace(fig, a, b, q_max)
            add_of_trace(fig, c, d, q_max)
            add_eq_point(fig, Qe, Pe, "Eq. libre")

            fig.add_shape(type="line", x0=qbar, x1=qbar, y0=0, y1=P_cuota * 1.5,
                          line=dict(color=C_INT, width=2, dash="dash"))
            fig.add_annotation(
                x=qbar, y=P_cuota * 1.45,
                text=f"Q̄ = {qbar:.0f}",
                showarrow=False,
                font=dict(color=C_INT, size=11, family="IBM Plex Mono")
            )

            fig.add_trace(go.Scatter(
                x=[qbar], y=[P_cuota],
                mode="markers",
                name=f"P con cuota (${P_cuota:.2f})",
                marker=dict(color=C_INT, size=12, line=dict(color=BG_PLOT, width=2))
            ))

            fig.add_trace(go.Scatter(
                x=[qbar, qbar], y=[P_of_cuota, P_cuota],
                mode="lines+markers",
                name=f"Renta de cuota (${renta:.2f})",
                line=dict(color=C_EQ, width=5),
                marker=dict(size=8, color=C_EQ)
            ))

            fig.add_shape(type="line", x0=0, x1=qbar, y0=P_cuota, y1=P_cuota,
                          line=dict(color=C_INT, width=1, dash="dot"))

            # Pérdida irrecuperable (DWL CORREGIDA)
            dead_weight_triangle(fig, qbar, Qe, P_cuota, Pe, P_of_cuota,
                                 color="rgba(255,200,60,0.15)", name="Pérdida irrecuperable (DWL)")

            fig.update_layout(title=dict(text="Cuota — Renta de cuota y pérdida de eficiencia", font=dict(color="#9aa0b8", size=13)))
            st.plotly_chart(fig, use_container_width=True)

            formula_box([
                f"P con cuota = (a − Q̄) / b = ({a:.2f} − {qbar:.2f}) / {b:.2f} = ${P_cuota:.2f}",
                f"P oferta c/cuota = (Q̄ − c) / d = ({qbar:.2f} − {c:.2f}) / {d:.2f} = ${P_of_cuota:.2f}",
                "",
                f"Renta de cuota = (Pd − Ps) × Q̄ = ({P_cuota:.2f} − {P_of_cuota:.2f}) × {qbar:.2f} = ${renta:.2f}",
                f"Alza de precio = Pd − Pe = {P_cuota:.2f} − {Pe:.2f} = +${dp:.2f}",
            ])

            info_box(
                f"Una cuota limita la cantidad máxima que puede producirse u ofrecerse en el mercado a <b style='color:{C_INT}'>{qbar:.0f} unidades</b>, "
                f"por debajo del equilibrio libre de {Qe:.2f} u.<br><br>"
                f"Al restringir la oferta, el precio de mercado sube de ${Pe:.2f} a <b style='color:{C_INT}'>${P_cuota:.2f}</b> "
                f"(un alza de +${dp:.2f}). Los productores que obtienen una licencia de cuota "
                f"pueden vender al precio elevado (${P_cuota:.2f}) aunque su costo mínimo de producción "
                f"a esa cantidad sea solo ${P_of_cuota:.2f}. "
                f"Esa diferencia por unidad es la <b style='color:{C_EQ}'>renta de cuota</b>, que totaliza ${renta:.2f}.<br><br>"
                f"<b>Agentes económicos:</b><br>"
                f"• <b>Consumidores:</b> pagan más y compran menos → pierden bienestar.<br>"
                f"• <b>Productores con licencia:</b> capturan la renta de cuota → ganan bienestar.<br>"
                f"• <b>Sociedad:</b> sufre una pérdida irrecuperable de eficiencia (triángulo DWL) "
                f"por las transacciones que ya no se realizan.",
                title="Cuota de producción — Análisis de bienestar"
            )