import streamlit as st
import pandas as pd
import os

# URL DE EXPORTACIÓN DIRECTA
URL_SOCIOS = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv&gid=1298454736"

st.set_page_config(page_title="Arca S&S", layout="centered")

# Estética de App
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# Logo
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2: st.image("logo.png", use_container_width=True)

st.title("🏋️ Arca S&S")

try:
    # LEER DATOS
    df = pd.read_csv(URL_SOCIOS)
    
    # Limpiamos los nombres de las columnas para que no haya errores
    df.columns = [str(c).strip().lower() for c in df.columns]

    # BUSCAMOS LA COLUMNA QUE CONTENGA LA PALABRA 'NOMBRE'
    col_encontrada = [c for c in df.columns if 'nombre' in c]

    if col_encontrada:
        col_real = col_encontrada[0]
        lista_nombres = df[col_real].dropna().unique().tolist()
        
        st.success("✅ Sistema Listo")
        alumno = st.selectbox("¿Quién entrena hoy?", ["Seleccionar..."] + lista_nombres)
        
        if alumno != "Seleccionar...":
            st.subheader(f"Hola {alumno}")
            fec = st.date_input("Fecha")
            hor = st.selectbox("Horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
            
            if st.button("CONFIRMAR RESERVA", use_container_width=True):
                st.balloons()
                st.success(f"¡Reserva capturada! Avisale a Sofía: {hor} hs")
    else:
        st.error("❌ No encuentro la columna 'nombre'.")
        st.write("Columnas que detecto en tu Drive:", list(df.columns))
        st.info("Asegurate de que en la celda A1 de tu planilla diga 'nombre'.")

except Exception as e:
    st.error("Error al cargar los datos. Refrescá la página.")
