import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Arca S&S", layout="centered")

# Conexión directa
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        # Intentamos leer la pestaña 'Socios'
        # ¡IMPORTANTE!: Verificá que en tu Excel se llame exactamente 'Socios'
        df_s = conn.read(worksheet="Socios", ttl=0)
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        return df_s
    except Exception as e:
        st.error(f"Error técnico: {e}")
        return pd.DataFrame()

st.title("🏋️ Arca S&S")
df = cargar_datos()

if not df.empty:
    st.success("✅ ¡CONECTADO!")
    st.write("Lista actual de socios:")
    st.dataframe(df[['nombre', 'apellido', 'saldo_clases']], hide_index=True)
    
    # Buscador para probar
    socio = st.selectbox("Ver socio:", [""] + df['nombre'].tolist())
    if socio:
        st.info(f"Socio seleccionado: {socio}")
else:
    st.warning("No se pudieron cargar los datos. Revisá que la pestaña en el Excel se llame exactamente 'Socios' (con S mayúscula y sin espacios).")
