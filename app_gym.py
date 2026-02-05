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
    # 1. LEER TODA LA HOJA 'Socios'
    df_socios = conn.read(spreadsheet=URL_ARCA, worksheet="Socios", ttl=0)
    
    # 2. LIMPIEZA DE COLUMNAS (Para que no falle si pusiste 'Nombre' con N mayúscula)
    df_socios.columns = [str(c).strip().lower() for c in df_socios.columns]

    # 3. VERIFICAR SI EXISTE LA COLUMNA
    if 'nombre' in df_socios.columns:
        # Quitamos filas vacías y tomamos los nombres
        nombres_lista = df_socios['nombre'].dropna().unique().tolist()
        
        if len(nombres_lista) > 0:
            st.success("✅ Base de datos lista.")
            alumno = st.selectbox("¿Quién entrena hoy?", ["Seleccionar..."] + nombres_lista)
            
            if alumno != "Seleccionar...":
                fec = st.date_input("Elegí el día")
                hor = st.selectbox("Elegí el horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
                
                if st.button("CONFIRMAR RESERVA", use_container_width=True):
                    # GUARDAR RESERVA
                    df_res = conn.read(spreadsheet=URL_ARCA, worksheet="Reservas", ttl=0)
                    nueva = pd.DataFrame([{"nombre": alumno, "fecha": str(fec), "hora": hor}])
                    df_final = pd.concat([df_res, nueva], ignore_index=True)
                    
                    conn.update(spreadsheet=URL_ARCA, worksheet="Reservas", data=df_final)
                    st.balloons()
                    st.success(f"¡Listo {alumno}! Turno guardado.")
        else:
            st.warning("⚠️ Cargá al menos un nombre en la planilla debajo de la palabra 'nombre'.")
    else:
        st.error(f"❌ No encuentro la columna 'nombre'. Columnas detectadas: {list(df_socios.columns)}")
        st.info("Asegurate de que en la celda B1 (o donde estén los nombres) diga exactamente: nombre")

except Exception as e:
    st.error("Error al conectar. Probá refrescando la página.")
