import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Reclutamiento", layout="wide")

st.title("Dashboard de Reclutamiento y Selección")

# URLs de tu Google Sheets
URL_SEGUIMIENTO = "https://docs.google.com/spreadsheets/d/1eA0NcY9hRHlFQuTKwd4ZGDZ_hhKtXqUdkpGeiM6Y2f8/export?format=csv&gid=829194331"
URL_VACANTES = "https://docs.google.com/spreadsheets/d/1eA0NcY9hRHlFQuTKwd4ZGDZ_hhKtXqUdkpGeiM6Y2f8/export?format=csv&gid=345065262"

@st.cache_data(ttl=60)
def cargar_datos():
    seguimiento = pd.read_csv(URL_SEGUIMIENTO)
    vacantes = pd.read_csv(URL_VACANTES)
    return seguimiento, vacantes

seguimiento, vacantes = cargar_datos()

# KPIs
st.subheader("Indicadores")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Postulaciones", len(seguimiento))

ingresos = len(seguimiento[seguimiento["Estado del proceso"] == "Ingresó"])
col2.metric("Ingresos", ingresos)

vacantes_abiertas = len(vacantes[vacantes["Estado"] != "Cubierta"])
col3.metric("Vacantes abiertas", vacantes_abiertas)

col4.metric("Vacantes totales", len(vacantes))

st.divider()

# Tablas
st.subheader("Seguimiento")
st.dataframe(seguimiento, use_container_width=True)

st.subheader("Vacantes")
st.dataframe(vacantes, use_container_width=True)
