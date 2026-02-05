import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# URL PÚBLICA DE ARCA S&S
URL_ARCA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv&gid=1298454736"

st.set_page_config(page_title="Arca S&S", layout="wide")
st.title("🏋️ Arca S&S - Gestión de Turnos")

try:
    # Leemos la planilla como un archivo público para evitar errores de cuenta
    df = pd.read_csv(URL_ARCA)
    
    if not df.empty:
        st.success("✅ Sistema conectado. Bienvenido/a.")
        nombres = df['nombre'].tolist()
        seleccion = st.selectbox("Selecciona tu nombre para reservar:", nombres)
        
        st.date_input("Elegí el día")
        st.selectbox("Elegí la hora", ["08:00", "09:00", "17:00", "18:00"])
        
        if st.button("Confirmar Reserva"):
            st.balloons()
            st.info("¡Turno enviado! Sofía ya puede verlo en el Drive.")
    else:
        st.warning("La lista de socios está vacía en el Drive.")

except Exception as e:
    st.error("Error de sincronización con Google Drive.")
    st.info("Leandro, verifica que en Drive el archivo se llame exactamente 'Socios' en la primera hoja.")
