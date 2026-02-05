import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os

# URL DE TU PLANILLA - Verificada por tus capturas
URL_ARCA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"

st.set_page_config(page_title="Arca S&S", layout="centered")

# Ocultar menús de sistema
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# Logo
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2: st.image("logo.png", use_container_width=True)

st.title("🏋️ Arca S&S")

# Conexión oficial
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 1. Leer Socios
    df_socios = conn.read(spreadsheet=URL_ARCA, worksheet="Socios", ttl=0)
    
    # Limpiar nombres de columnas por si acaso
    df_socios.columns = [str(c).strip().lower() for c in df_socios.columns]

    if 'nombre' in df_socios.columns:
        nombres = df_socios['nombre'].dropna().unique().tolist()
        
        st.success("✅ Sistema Listo")
        alumno = st.selectbox("¿Quién entrena hoy?", ["Seleccionar..."] + nombres)
        
        if alumno != "Seleccionar...":
            st.write(f"### Hola **{alumno}**")
            fec = st.date_input("Elegí el día")
            hor = st.selectbox("Horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
            
            if st.button("CONFIRMAR RESERVA", use_container_width=True):
                # 2. Guardado en hoja 'Reservas'
                # Leemos lo que ya hay para no pisar nada
                df_reservas = conn.read(spreadsheet=URL_ARCA, worksheet="Reservas", ttl=0)
                
                # Creamos la fila nueva (Usamos socio_id como pusiste en tu captura)
                nueva_fila = pd.DataFrame([{
                    "id": len(df_reservas) + 1,
                    "socio_id": alumno, 
                    "fecha": str(fec),
                    "hora": hor
                }])
                
                # Unimos y subimos
                df_final = pd.concat([df_reservas, nueva_fila], ignore_index=True)
                conn.update(spreadsheet=URL_ARCA, worksheet="Reservas", data=df_final)
                
                st.balloons()
                st.success(f"¡Reserva confirmada {alumno}!")
    else:
        st.error("No encuentro la columna 'nombre' en Socios.")

except Exception as e:
    st.error("Error al conectar con el Drive.")
    st.info("Recordá compartir la planilla con el mail de Streamlit como EDITOR.")
