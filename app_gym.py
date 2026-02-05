import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Arca S&S", layout="centered")

# Conexión ultra-directa
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        # Buscamos la pestaña 'Socios' usando el ID de los Secrets
        df_s = conn.read(worksheet="Socios", ttl=0)
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        return df_s
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame()

st.title("🏋️ Arca S&S")
df = cargar_datos()

if not df.empty:
    st.success("✅ ¡Conectado con éxito!")
    st.write("Lista de Alumnos:")
    st.dataframe(df[['nombre', 'apellido', 'saldo_clases']], hide_index=True)
    
    # Selector simple para probar
    alumno = st.selectbox("Seleccioná un alumno:", [""] + df['nombre'].tolist())
    if alumno:
        st.info(f"Hola {alumno}, bienvenido a Arca.")
