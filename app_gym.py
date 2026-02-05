import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURACIÓN ---
CLAVE_ADMIN = "arca2026"
# USA ESTA URL EXACTA (es la tuya con el final ajustado para lectura directa)
URL_FINAL = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"

st.set_page_config(page_title="Arca S&S", layout="wide")

# Conexión optimizada
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos(hoja):
    # Intentamos leer usando la URL directamente en la función
    return conn.read(spreadsheet=URL_FINAL, worksheet=hoja, ttl=0)

# --- INTERFAZ ---
st.sidebar.title("Menú Arca S&S")
es_admin = st.sidebar.checkbox("Acceso Administrador")
pwd = st.sidebar.text_input("Contraseña", type="password") if es_admin else ""

choice = st.sidebar.selectbox("Seleccionar:", ["Reservar Turno", "Panel Control"] if (es_admin and pwd == CLAVE_ADMIN) else ["Reservar Turno"])

# --- LÓGICA ---
if choice == "Reservar Turno":
    st.title("📅 Reserva de Clases")
    try:
        df = cargar_datos("Socios")
        if not df.empty:
            lista_socios = df['nombre'].tolist()
            socio = st.selectbox("Selecciona tu nombre", lista_socios)
            st.success(f"Conectado correctamente. ¡Hola {socio}!")
            # Aquí pueden seguir los selectores de fecha/hora
    except Exception as e:
        st.error("Todavía no puedo leer la planilla. Revisa los Secrets en Streamlit.")
        st.info("Asegúrate de que en 'Advanced Settings' > 'Secrets' pegaste el bloque que te pasé.")
