import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import calendar
import os

# --- CONFIGURACIÓN ARCA S&S ---
CLAVE_ADMIN = "arca2026"
PACKS = {
    "Pack 8 clases ($45.000)": 8, "Pack 12 clases ($50.000)": 12,
    "Pack 16 clases ($55.000)": 16, "Pack 20 clases ($58.000)": 20
}
HORARIOS = ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"]
URL_SHEET = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"

st.set_page_config(page_title="Arca S&S", layout="wide")

# Conexión simple
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_hoja(nombre):
    # Forzamos la lectura de la URL configurada
    return conn.read(spreadsheet=URL_SHEET, worksheet=nombre, ttl=0)

# --- INTERFAZ ---
st.sidebar.title("Menú Arca S&S")
es_admin = st.sidebar.checkbox("Acceso Administrador")
pwd = st.sidebar.text_input("Contraseña", type="password") if es_admin else ""

if es_admin and pwd == CLAVE_ADMIN:
    menu = ["Reservar Turno", "Registrar Socio / Pago", "Panel de Control"]
else:
    menu = ["Reservar Turno"]

choice = st.sidebar.selectbox("Seleccionar:", menu)
hoy = datetime.now()

# --- LÓGICA DE VISTA ---
if choice == "Reservar Turno":
    st.title("📅 Reserva de Clases")
    try:
        df_socios = leer_hoja("Socios")
        if not df_socios.empty:
            nom = st.selectbox("Tu Nombre", df_socios['nombre'].tolist())
            st.info(f"Hola {nom}, selecciona tu fecha y hora.")
            fec = st.date_input("Fecha", min_value=hoy.date())
            hor = st.selectbox("Hora", HORARIOS)
            if st.button("Confirmar"):
                st.success("¡Reserva procesada! (Verifica tu saldo en la planilla)")
    except Exception as e:
        st.error("Error de conexión. Verifica que la planilla esté compartida como EDITOR.")

elif choice == "Registrar Socio / Pago":
    st.title("💳 Carga de Pagos")
    st.write("Usa este panel para dar de alta nuevos alumnos.")
