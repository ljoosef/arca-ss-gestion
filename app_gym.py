import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os

# URL DE TU PLANILLA - Verificada
URL_ARCA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"

st.set_page_config(page_title="Arca S&S", layout="centered")

# Ocultar basura visual
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# Logo
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2: st.image("logo.png", use_container_width=True)

st.title("🏋️ Arca S&S")

# Conectamos
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # LEER SOCIOS
    df_socios = conn.read(spreadsheet=URL_ARCA, worksheet="Socios", ttl=0)
    
    # Limpiar nombres de columnas (por si acaso)
    df_socios.columns = df_socios.columns.str.strip().str.lower()

    if not df_socios.empty:
        nombres = df_socios['nombre'].dropna().unique().tolist()
        alumno = st.selectbox("¿Quién entrena hoy?", ["Seleccionar..."] + nombres)
        
        if alumno != "Seleccionar...":
            fec = st.date_input("Elegí el día")
            hor = st.selectbox("Elegí el horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
            
            if st.button("CONFIRMAR RESERVA", use_container_width=True):
                # Intentar guardar
                df_res = conn.read(spreadsheet=URL_ARCA, worksheet="Reservas", ttl=0)
                nueva = pd.DataFrame([{"nombre": alumno, "fecha": str(fec), "hora": hor}])
                df_final = pd.concat([df_res, nueva], ignore_index=True)
                
                conn.update(spreadsheet=URL_ARCA, worksheet="Reservas", data=df_final)
                st.balloons()
                st.success(f"¡Listo {alumno}! Turno guardado.")
    else:
        st.warning("No se encontraron nombres. Revisá la columna 'nombre' en el Drive.")

except Exception as e:
    st.error("Error de acceso a la planilla.")
    st.info("Leandro, revisá el botón azul de COMPARTIR en Google Drive: debe decir 'Cualquier persona con el enlace' y 'EDITOR'.")
