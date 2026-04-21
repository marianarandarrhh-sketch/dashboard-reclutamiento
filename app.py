import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Selección - Prácticas Profesionales",
    layout="wide",
)

# -----------------------------
# CONFIG
# -----------------------------
URL_SEGUIMIENTO = "https://docs.google.com/spreadsheets/d/1eA0NcY9hRHlFQuTKwd4ZGDZ_hhKtXqUdkpGeiM6Y2f8/export?format=csv&gid=829194331"
URL_VACANTES = "https://docs.google.com/spreadsheets/d/1eA0NcY9hRHlFQuTKwd4ZGDZ_hhKtXqUdkpGeiM6Y2f8/export?format=csv&gid=345065262"

ESTADOS_ORDEN = [
    "Nuevo",
    "Contactado",
    "Entrevista agendada",
    "Entrevistado",
    "Apto",
    "Finalista",
    "Ingresó",
    "Base futura",
    "No apto",
]

# -----------------------------
# LOAD
# -----------------------------
@st.cache_data(ttl=120)
def cargar_datos():
    seguimiento = pd.read_csv(URL_SEGUIMIENTO)
    vacantes = pd.read_csv(URL_VACANTES)
    return seguimiento, vacantes

seguimiento, vacantes = cargar_datos()

# -----------------------------
# LIMPIEZA
# -----------------------------
for col in ["Fecha", "Fecha contacto", "Fecha entrevista"]:
    if col in seguimiento.columns:
        seguimiento[col] = pd.to_datetime(seguimiento[col], errors="coerce", dayfirst=True)

for col in ["Fecha apertura", "Ingreso"]:
    if col in vacantes.columns:
        vacantes[col] = pd.to_datetime(vacantes[col], errors="coerce", dayfirst=True)

if "Puntaje" in seguimiento.columns:
    seguimiento["Puntaje"] = pd.to_numeric(seguimiento["Puntaje"], errors="coerce")

if "Días en proceso" in seguimiento.columns:
    seguimiento["Días en proceso"] = pd.to_numeric(seguimiento["Días en proceso"], errors="coerce")

if "Días abierta" in vacantes.columns:
    vacantes["Días abierta"] = pd.to_numeric(vacantes["Días abierta"], errors="coerce")

# -----------------------------
# HEADER
# -----------------------------
st.title("Dashboard de Selección")
st.caption("Prácticas profesionales | Seguimiento de candidatos y vacantes")

# -----------------------------
# SIDEBAR / FILTROS
# -----------------------------
st.sidebar.header("Filtros")

unidades_seg = []
if "Unidad de negocio" in seguimiento.columns:
    unidades_seg = sorted([x for x in seguimiento["Unidad de negocio"].dropna().astype(str).unique()])

areas_seg = []
if "Área de interés" in seguimiento.columns:
    areas_seg = sorted([x for x in seguimiento["Área de interés"].dropna().astype(str).unique()])

estado_seg = []
if "Estado del proceso" in seguimiento.columns:
    estado_seg = sorted([x for x in seguimiento["Estado del proceso"].dropna().astype(str).unique()])

unidad_sel = st.sidebar.multiselect("Unidad de negocio", unidades_seg, default=unidades_seg)
area_sel = st.sidebar.multiselect("Área de interés", areas_seg, default=areas_seg)
estado_sel = st.sidebar.multiselect("Estado del proceso", estado_seg, default=estado_seg)

vac_empresas = []
if "Empresa" in vacantes.columns:
    vac_empresas = sorted([x for x in vacantes["Empresa"].dropna().astype(str).unique()])

empresa_vac_sel = st.sidebar.multiselect("Empresa vacante", vac_empresas, default=vac_empresas)

# -----------------------------
# FILTRADO
# -----------------------------
seg = seguimiento.copy()
if "Unidad de negocio" in seg.columns and unidad_sel:
    seg = seg[seg["Unidad de negocio"].astype(str).isin(unidad_sel)]
if "Área de interés" in seg.columns and area_sel:
    seg = seg[seg["Área de interés"].astype(str).isin(area_sel)]
if "Estado del proceso" in seg.columns and estado_sel:
    seg = seg[seg["Estado del proceso"].astype(str).isin(estado_sel)]

vac = vacantes.copy()
if "Empresa" in vac.columns and empresa_vac_sel:
    vac = vac[vac["Empresa"].astype(str).isin(empresa_vac_sel)]

# -----------------------------
# KPIS
# -----------------------------
total_postulaciones = len(seg)

entrevistados = 0
if "Estado del proceso" in seg.columns:
    entrevistados = seg["Estado del proceso"].eq("Entrevistado").sum()

ingresos = 0
if "Estado del proceso" in seg.columns:
    ingresos = seg["Estado del proceso"].eq("Ingresó").sum()

base_futura = 0
if "Estado del proceso" in seg.columns:
    base_futura = seg["Estado del proceso"].eq("Base futura").sum()

promedio_puntaje = 0
if "Puntaje" in seg.columns and seg["Puntaje"].notna().any():
    promedio_puntaje = round(seg["Puntaje"].mean(), 2)

reentrevistables = 0
if "¿Reentrevistar?" in seg.columns:
    reentrevistables = seg["¿Reentrevistar?"].astype(str).str.upper().eq("SÍ").sum() + \
                       seg["¿Reentrevistar?"].astype(str).str.upper().eq("SI").sum()

vacantes_totales = len(vac)

vacantes_cubiertas = 0
if "Estado" in vac.columns:
    vacantes_cubiertas = vac["Estado"].astype(str).eq("Cubierta").sum()

vacantes_abiertas = 0
if "Estado" in vac.columns:
    vacantes_abiertas = (~vac["Estado"].astype(str).eq("Cubierta")).sum()

promedio_dias_abierta = 0
if "Días abierta" in vac.columns and vac["Días abierta"].notna().any():
    promedio_dias_abierta = round(vac["Días abierta"].mean(), 1)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Postulaciones", total_postulaciones)
c2.metric("Entrevistados", int(entrevistados))
c3.metric("Ingresos", int(ingresos))
c4.metric("Base futura", int(base_futura))

c5, c6, c7, c8 = st.columns(4)
c5.metric("Puntaje promedio", promedio_puntaje)
c6.metric("Reentrevistables", int(reentrevistables))
c7.metric("Vacantes abiertas", int(vacantes_abiertas))
c8.metric("Prom. días abierta", promedio_dias_abierta)

st.divider()

# -----------------------------
# GRÁFICOS FILA 1
# -----------------------------
g1, g2 = st.columns(2)

with g1:
    st.subheader("Pipeline de selección")
    if "Estado del proceso" in seg.columns and not seg.empty:
        pipeline = (
            seg["Estado del proceso"]
            .value_counts()
            .reindex(ESTADOS_ORDEN)
            .dropna()
            .reset_index()
        )
        pipeline.columns = ["Estado del proceso", "Cantidad"]
        fig = px.bar(
            pipeline,
            x="Estado del proceso",
            y="Cantidad",
            text="Cantidad",
        )
        fig.update_layout(height=400, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos para mostrar.")

with g2:
    st.subheader("Distribución por unidad")
    if "Unidad de negocio" in seg.columns and not seg.empty:
        por_unidad = seg["Unidad de negocio"].value_counts().reset_index()
        por_unidad.columns = ["Unidad de negocio", "Cantidad"]
        fig = px.pie(
            por_unidad,
            names="Unidad de negocio",
            values="Cantidad",
            hole=0.45,
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos para mostrar.")

# -----------------------------
# GRÁFICOS FILA 2
# -----------------------------
g3, g4 = st.columns(2)

with g3:
    st.subheader("Vacantes por estado")
    if "Estado" in vac.columns and not vac.empty:
        estado_vac = vac["Estado"].value_counts().reset_index()
        estado_vac.columns = ["Estado", "Cantidad"]
        fig = px.bar(
            estado_vac,
            x="Estado",
            y="Cantidad",
            text="Cantidad",
        )
        fig.update_layout(height=400, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos para mostrar.")

with g4:
    st.subheader("Vacantes por empresa")
    if "Empresa" in vac.columns and not vac.empty:
        por_empresa = vac["Empresa"].value_counts().reset_index()
        por_empresa.columns = ["Empresa", "Cantidad"]
        fig = px.bar(
            por_empresa,
            x="Empresa",
            y="Cantidad",
            text="Cantidad",
        )
        fig.update_layout(height=400, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos para mostrar.")

# -----------------------------
# GRÁFICOS FILA 3
# -----------------------------
g5, g6 = st.columns(2)

with g5:
    st.subheader("Promedio de días en proceso por unidad")
    if {"Unidad de negocio", "Días en proceso"}.issubset(seg.columns) and not seg.empty:
        dias_unidad = (
            seg.dropna(subset=["Unidad de negocio", "Días en proceso"])
               .groupby("Unidad de negocio", as_index=False)["Días en proceso"]
               .mean()
               .sort_values("Días en proceso", ascending=False)
        )
        dias_unidad["Días en proceso"] = dias_unidad["Días en proceso"].round(1)
        fig = px.bar(
            dias_unidad,
            x="Unidad de negocio",
            y="Días en proceso",
            text="Días en proceso",
        )
        fig.update_layout(height=400, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos para mostrar.")

with g6:
    st.subheader("Puntaje promedio por unidad")
    if {"Unidad de negocio", "Puntaje"}.issubset(seg.columns) and not seg.empty:
        puntaje_unidad = (
            seg.dropna(subset=["Unidad de negocio", "Puntaje"])
               .groupby("Unidad de negocio", as_index=False)["Puntaje"]
               .mean()
               .sort_values("Puntaje", ascending=False)
        )
        puntaje_unidad["Puntaje"] = puntaje_unidad["Puntaje"].round(2)
        fig = px.bar(
            puntaje_unidad,
            x="Unidad de negocio",
            y="Puntaje",
            text="Puntaje",
        )
        fig.update_layout(height=400, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos para mostrar.")

st.divider()

# -----------------------------
# TABLAS
# -----------------------------
t1, t2 = st.tabs(["Seguimiento", "Vacantes"])

with t1:
    st.subheader("Detalle de seguimiento")
    st.dataframe(seg, use_container_width=True, height=400)

with t2:
    st.subheader("Detalle de vacantes")
    st.dataframe(vac, use_container_width=True, height=400)
