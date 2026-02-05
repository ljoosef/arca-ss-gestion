import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os

# CONFIGURACIÓN
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"

st.set_page_config(page_title="Arca S&S - Reservas", layout="centered")

# Ocultar menús para vista limpia
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# Logo
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2: st.image("logo.png", use_container_width=True)

st.title("📅 Reserva tu Clase")

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 1. Leer Socios para el selector
    df_socios = conn.read(spreadsheet=URL_PLANILLA, worksheet="Socios", ttl=0)
    
    if not df_socios.empty:
        nombres = df_socios['nombre'].dropna().tolist()
        alumno = st.selectbox("Seleccioná tu nombre", [""] + nombres)
        
        if alumno:
            fec = st.date_input("Día de la clase")
            hor = st.selectbox("Horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
            
            if st.button("CONFIRMAR RESERVA", use_container_width=True):
                # 2. Leer Reservas actuales para no borrar lo anterior
                df_reservas = conn.read(spreadsheet=URL_PLANILLA, worksheet="Reservas", ttl=0)
                
                # 3. Crear la nueva reserva
                nueva_reserva = pd.DataFrame([{
                    "nombre": alumno,
                    "fecha": str(fec),
                    "hora": hor
                }])
                
                # 4. Unir y Guardar
                df_final = pd.concat([df_reservas, nueva_reserva], ignore_index=True)
                conn.update(spreadsheet=URL_PLANILLA, worksheet="Reservas", data=df_final)
                
                st.balloons()
                st.success(f"¡Listo {alumno}! Tu turno de las {hor} fue guardado.")
    else:
        st.warning("No hay socios cargados en la planilla.")

except Exception as e:
    st.error("Error de conexión. Revisá que la planilla esté como EDITOR.")
