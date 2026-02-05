import streamlit as st
import pandas as pd
import os

# URL DE DATOS
URL_ARCA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2_grYykSRTBXAZgLZvrnOJpM0/export?format=csv&gid=1298454736"

st.set_page_config(page_title="Arca S&S - Turnos", layout="centered")

# Ocultar menús de sistema
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div.block-container {padding-top: 2rem;}
    </style>
    """, unsafe_allow_html=True)

# MOSTRAR LOGO
if os.path.exists("logo.png"):
    # Esto centra la imagen en la pantalla
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", use_container_width=True)

st.markdown("<h2 style='text-align: center;'>Reserva de Clases</h2>", unsafe_allow_html=True)

try:
    df = pd.read_csv(URL_ARCA)
    df.columns = df.columns.str.strip().str.lower()
    
    if not df.empty and 'nombre' in df.columns:
        nombres = df['nombre'].dropna().unique().tolist()
        
        st.write("---")
        alumno = st.selectbox("¿Quién entrena hoy?", ["Seleccionar..."] + nombres)
        
        if alumno != "Seleccionar...":
            st.write(f"Hola **{alumno}**, elegí tu turno:")
            fec = st.date_input("Fecha")
            hor = st.selectbox("Horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
            
            if st.button("Confirmar Reserva", use_container_width=True):
                st.balloons()
                st.success(f"¡Listo {alumno}! Turno para el {fec} a las {hor} reservado.")
        else:
            st.info("Buscá tu nombre arriba para empezar.")
            
except Exception:
    st.error("Error al cargar la base de datos.")
