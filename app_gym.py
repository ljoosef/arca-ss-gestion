import streamlit as st
import pandas as pd
import os

# URL MAESTRA (Lee todo el archivo)
URL_BASE = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv"

st.set_page_config(page_title="Arca S&S", layout="centered")

# Ocultar menús para vista de App
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# Logo
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2: st.image("logo.png", use_container_width=True)

st.title("🏋️ Arca S&S")

try:
    # Intentamos leer la hoja (probamos con el GID de Socios primero)
    url_socios = f"{URL_BASE}&gid=1298454736"
    df = pd.read_csv(url_socios)
    
    # Limpieza total de títulos
    df.columns = [str(c).strip().lower() for c in df.columns]

    if 'nombre' in df.columns:
        lista_nombres = df['nombre'].dropna().unique().tolist()
        
        st.success("✅ Sistema Conectado")
        alumno = st.selectbox("¿Quién entrena hoy?", ["Seleccionar..."] + lista_nombres)
        
        if alumno != "Seleccionar...":
            st.subheader(f"Hola {alumno}")
            fec = st.date_input("Elegí el día")
            hor = st.selectbox("Elegí el horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
            
            if st.button("CONFIRMAR RESERVA", use_container_width=True):
                st.balloons()
                st.success(f"¡Reserva confirmada! Avisale a Sofía: {hor} hs")
    else:
        st.error("⚠️ No encuentro la columna 'nombre'.")
        st.write("Columnas detectadas:", list(df.columns))

except Exception as e:
    st.error("Error al conectar. Refrescá la página en 10 segundos.")
