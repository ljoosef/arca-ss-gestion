import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os

# URL DE TU PLANILLA
URL_ARCA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"

st.set_page_config(page_title="Arca S&S", layout="centered")

# Ocultar menús
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# Mostrar Logo
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2: st.image("logo.png", use_container_width=True)

st.title("🏋️ Arca S&S")

# Conectamos con el motor de Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 1. LEER SOCIOS (Usamos el GID que ya sabemos que funciona)
    df_socios = conn.read(spreadsheet=URL_ARCA, worksheet="Socios", ttl=0)
    df_socios.columns = [str(c).strip().lower() for c in df_socios.columns]

    if 'nombre' in df_socios.columns:
        nombres = df_socios['nombre'].dropna().unique().tolist()
        
        st.success("✅ Sistema en línea")
        alumno = st.selectbox("¿Quién entrena hoy?", ["Seleccionar..."] + nombres)
        
        if alumno != "Seleccionar...":
            st.write(f"### Hola **{alumno}**")
            fec = st.date_input("Elegí el día")
            hor = st.selectbox("Elegí el horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
            
            if st.button("CONFIRMAR RESERVA", use_container_width=True):
                # 2. PROCESO DE GUARDADO REAL
                # Leemos lo que ya hay en Reservas
                df_reservas = conn.read(spreadsheet=URL_ARCA, worksheet="Reservas", ttl=0)
                
                # Creamos la fila nueva
                nueva_fila = pd.DataFrame([{"nombre": alumno, "fecha": str(fec), "hora": hor}])
                
                # Juntamos todo
                df_actualizado = pd.concat([df_reservas, nueva_fila], ignore_index=True)
                
                # LO SUBIMOS AL DRIVE
                conn.update(spreadsheet=URL_ARCA, worksheet="Reservas", data=df_actualizado)
                
                st.balloons()
                st.success(f"¡Reserva confirmada para el {fec} a las {hor}!")
    else:
        st.error("No encuentro la columna 'nombre'.")

except Exception as e:
    st.error("Error de conexión al guardar.")
    st.info("Asegúrate de que la planilla esté compartida como EDITOR.")
