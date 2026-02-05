import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# URL BASE
URL_ARCA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit"

st.title("🔍 Diagnóstico Arca S&S")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Intentamos leer solo la primera pestaña para probar conexión
    df = conn.read(spreadsheet=URL_ARCA, worksheet="Socios", ttl=0)
    
    st.success("✅ ¡CONEXIÓN EXITOSA!")
    st.write("Datos encontrados en 'Socios':")
    st.dataframe(df.head())
    
    st.info("Si ves tus datos arriba, el problema era el código anterior. Avisame y te paso el definitivo.")

except Exception as e:
    st.error("❌ LA CONEXIÓN SIGUE FALLANDO")
    st.write("Detalle técnico del error:")
    st.code(str(e))
    
    if "400" in str(e):
        st.warning("El Error 400 indica que Google recibe la llave pero no encuentra la pestaña o el archivo. Revisá que la pestaña se llame 'Socios' (exactamente así).")
