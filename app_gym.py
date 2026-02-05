import streamlit as st
import pandas as pd
import os

# URL PÚBLICA DE SOCIOS (Esta no necesita permisos especiales)
URL_SOCIOS = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv&gid=0"

st.set_page_config(page_title="Arca S&S", layout="centered")

# Ocultar menús de sistema
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# Logo
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2: st.image("logo.png", use_container_width=True)

st.title("🏋️ Arca S&S")

try:
    # Leer los nombres directamente del link público
    df = pd.read_csv(URL_SOCIOS)
    
    # Limpiamos los títulos de las columnas
    df.columns = [str(c).strip().lower() for c in df.columns]

    if 'nombre' in df.columns:
        nombres = df['nombre'].dropna().unique().tolist()
        
        st.success("✅ Conexión Exitosa")
        alumno = st.selectbox("¿Quién entrena hoy?", ["Seleccionar..."] + nombres)
        
        if alumno != "Seleccionar...":
            st.write(f"### Hola **{alumno}**")
            fec = st.date_input("Elegí el día")
            hor = st.selectbox("Elegí el horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
            
            if st.button("CONFIRMAR RESERVA", use_container_width=True):
                st.balloons()
                st.success(f"¡Listo {alumno}! Tu turno de las {hor} fue solicitado.")
                st.info("Avisale a Sofía por WhatsApp para que lo anote en el Drive.")
    else:
        st.error("No encuentro la columna 'nombre'.")
        st.write("Veo estas columnas:", list(df.columns))

except Exception as e:
    st.error("Error de conexión rápida.")
    st.write("Asegúrate de que la planilla esté compartida como 'Cualquier persona con el enlace' en modo EDITOR.")
