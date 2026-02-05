import streamlit as st
import pandas as pd

# URL DE EXPORTACIÓN DIRECTA (Ajustada para leer tu Drive)
URL_DATOS = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2_grYykSRTBXAZgLZvrnOJpM0/export?format=csv&gid=1298454736"

st.set_page_config(page_title="Arca S&S", layout="wide")
st.title("🏋️ Arca S&S - Gestión de Turnos")

try:
    # Leemos los datos directamente como CSV público
    df = pd.read_csv(URL_DATOS)
    
    # Limpiamos nombres de columnas por si hay espacios
    df.columns = df.columns.str.strip()

    if not df.empty and 'nombre' in df.columns:
        st.success("✅ Sistema conectado. Selecciona tu nombre.")
        lista_nombres = df['nombre'].dropna().tolist()
        
        seleccion = st.selectbox("¿Quién va a entrenar hoy?", lista_nombres)
        
        st.write(f"### Hola {seleccion}")
        fec = st.date_input("Elegí el día")
        hor = st.selectbox("Elegí la hora", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
        
        if st.button("Confirmar Reserva"):
            st.balloons()
            st.success(f"¡Reserva lista para {seleccion} el día {fec} a las {hor}!")
    else:
        st.warning("Asegúrate de que la primera columna de la planilla se llame 'nombre' (en minúsculas).")

except Exception as e:
    st.error("Error al leer la planilla. Verifica que esté compartida como 'Cualquier persona con el enlace'.")
