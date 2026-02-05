import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os

# URL de tu planilla
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"

st.set_page_config(page_title="Arca S&S - Reservas", layout="centered")

# Estética limpia
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# Logo
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2: st.image("logo.png", use_container_width=True)

st.title("🏋️ Arca S&S")
st.subheader("Reserva de Clases")

# Conexión usando los Secrets que guardaste
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Leer Socios
    df_socios = conn.read(spreadsheet=URL_PLANILLA, worksheet="Socios", ttl=0)
    
    if not df_socios.empty:
        nombres = df_socios['nombre'].dropna().tolist()
        alumno = st.selectbox("Seleccioná tu nombre", [""] + nombres)
        
        if alumno:
            fec = st.date_input("Día")
            hor = st.selectbox("Horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
            
            if st.button("CONFIRMAR RESERVA", use_container_width=True):
                # 1. Leer Reservas actuales
                df_reservas = conn.read(spreadsheet=URL_PLANILLA, worksheet="Reservas", ttl=0)
                
                # 2. Nueva fila
                nueva = pd.DataFrame([{"nombre": alumno, "fecha": str(fec), "hora": hor}])
                
                # 3. Guardar
                df_final = pd.concat([df_reservas, nueva], ignore_index=True)
                conn.update(spreadsheet=URL_PLANILLA, worksheet="Reservas", data=df_final)
                
                st.balloons()
                st.success(f"¡Listo {alumno}! Turno guardado para el {fec} a las {hor}.")
    else:
        st.warning("Cargá nombres en la pestaña 'Socios' de tu Drive.")

except Exception as e:
    st.error("Error de conexión.")
    st.info("Asegúrate de que la planilla esté compartida como EDITOR.")
