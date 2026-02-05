import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os

# URL DE TU PLANILLA
URL_ARCA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"

st.set_page_config(page_title="Arca S&S", layout="centered")

# Ocultar menús
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# Logo
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2: st.image("logo.png", use_container_width=True)

st.title("🏋️ Arca S&S")

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 1. LEER HOJA DE SOCIOS
    df_socios = conn.read(spreadsheet=URL_ARCA, worksheet="Socios", ttl=0)
    
    # 2. BUSCAR LA COLUMNA QUE TENGA LOS NOMBRES
    # Buscamos cualquier columna que se llame 'nombre' o 'nombre ' (ignorando mayúsculas)
    col_nombre = [c for c in df_socios.columns if 'nombre' in str(c).lower()]
    
    if col_nombre:
        nombre_col_real = col_nombre[0]
        nombres_lista = df_socios[nombre_col_real].dropna().unique().tolist()
        
        if len(nombres_lista) > 0:
            st.success("✅ ¡Conectado con éxito!")
            alumno = st.selectbox("¿Quién va a entrenar?", ["Seleccionar..."] + nombres_lista)
            
            if alumno != "Seleccionar...":
                st.write(f"Hola **{alumno}**, reservá tu lugar:")
                fec = st.date_input("Fecha")
                hor = st.selectbox("Horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
                
                if st.button("CONFIRMAR RESERVA", use_container_width=True):
                    # GUARDAR EN HOJA RESERVAS
                    df_res = conn.read(spreadsheet=URL_ARCA, worksheet="Reservas", ttl=0)
                    nueva = pd.DataFrame([{"nombre": alumno, "fecha": str(fec), "hora": hor}])
                    df_final = pd.concat([df_res, nueva], ignore_index=True)
                    
                    conn.update(spreadsheet=URL_ARCA, worksheet="Reservas", data=df_final)
                    st.balloons()
                    st.success(f"¡Reserva confirmada! Ya podés cerrar la app.")
        else:
            st.warning("⚠️ No encontré nombres debajo del título 'nombre'.")
    else:
        st.error("❌ No encuentro la columna 'nombre'.")
        st.write("Columnas que veo en tu Drive:", list(df_socios.columns))

except Exception as e:
    st.error("Error de comunicación. Refrescá la página.")
