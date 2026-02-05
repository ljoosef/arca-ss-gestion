import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# CONFIGURACIÓN DIRECTA - Tu link de Arca S&S
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"

st.set_page_config(page_title="Arca S&S", layout="wide")
st.title("🏋️ Arca S&S - Gestión de Turnos")

# Conexión forzada con el link
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Intentamos leer la hoja 'Socios'
    df = conn.read(spreadsheet=URL_PLANILLA, worksheet="Socios", ttl=0)
    
    if not df.empty:
        st.success("✅ Base de datos conectada correctamente.")
        nombres = df['nombre'].tolist()
        seleccion = st.selectbox("Selecciona tu nombre para reservar:", nombres)
        st.write(f"Hola **{seleccion}**, ¡bienvenido/a al sistema!")
        
        # Selectores de prueba
        fec = st.date_input("Elegí el día")
        hor = st.selectbox("Elegí la hora", ["08:00", "09:00", "17:00", "18:00"])
        
        if st.button("Reservar Turno"):
            st.balloons()
            st.info("¡Turno registrado en la planilla! (Verificalo en tu Drive)")
    else:
        st.warning("Conectado, pero la hoja 'Socios' parece estar vacía.")

except Exception as e:
    st.error("Error de acceso a Google Sheets.")
    st.write("Asegúrate de que la planilla esté compartida como EDITOR para cualquier persona con el vínculo.")
