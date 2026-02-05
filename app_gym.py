import streamlit as st
import pandas as pd

# LINK DE EXPORTACIÓN DIRECTA (Asegúrate de copiarlo todo)
URL_ARCA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv&gid=1298454736"

st.set_page_config(page_title="Arca S&S", layout="wide")
st.title("🏋️ Arca S&S - Gestión de Turnos")

try:
    # Leemos la planilla directamente
    df = pd.read_csv(URL_ARCA)
    
    # Limpiamos nombres de columnas
    df.columns = df.columns.str.strip().str.lower()

    if not df.empty and 'nombre' in df.columns:
        st.success("✅ ¡Conectado! Ya puedes reservar tu clase.")
        
        # Quitamos espacios en los nombres de la lista
        lista_nombres = df['nombre'].dropna().unique().tolist()
        
        seleccion = st.selectbox("¿Quién va a entrenar hoy?", lista_nombres)
        
        st.write(f"### Hola {seleccion}")
        fec = st.date_input("Elegí el día")
        hor = st.selectbox("Elegí la hora", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
        
        if st.button("Confirmar Reserva"):
            st.balloons()
            st.success(f"¡Reserva confirmada para {seleccion}!")
            st.info("Recordá que podés cancelar hasta 15 minutos antes.")
    else:
        st.warning("Revisa que en la celda A1 de tu Drive diga la palabra: nombre")

except Exception as e:
    st.error("Error de conexión con Google Drive.")
    st.write("Leandro, probá refrescando la página en 10 segundos.")
