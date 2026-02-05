import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import urllib.parse
import os

# --- CONFIGURACIÓN ---
URL_LECTURA_SOCIOS = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv&gid=0"
URL_LECTURA_RESERVAS = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/export?format=csv&gid=1298454736"
URL_ESCRITURA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"
CELULAR_ADMIN = "549XXXXXXXXXX" # <--- ¡PONÉ TU NÚMERO ACÁ!

st.set_page_config(page_title="Arca S&S", layout="centered")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# Intentamos conexión
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    conn = None

def leer_datos():
    try:
        df_s = pd.read_csv(URL_LECTURA_SOCIOS)
        df_r = pd.read_csv(URL_LECTURA_RESERVAS)
        df_s.columns = [str(c).strip().lower() for c in df_s.columns]
        df_r.columns = [str(c).strip().lower() for c in df_r.columns]
        return df_s, df_r
    except:
        return pd.DataFrame(), pd.DataFrame()

def intentar_guardar(df_socios, df_reservas, mensaje_wpp):
    try:
        if conn:
            conn.update(spreadsheet=URL_ESCRITURA, worksheet="Reservas", data=df_reservas)
            conn.update(spreadsheet=URL_ESCRITURA, worksheet="Socios", data=df_socios)
            st.balloons()
            st.success("✅ ¡Guardado en el sistema!")
            st.rerun()
        else:
            raise Exception("Sin conexión")
    except:
        texto = urllib.parse.quote(mensaje_wpp)
