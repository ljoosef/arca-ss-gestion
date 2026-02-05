import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os

# CONFIGURACIÓN
URL_ARCA = "https://docs.google.com/spreadsheets/d/1w1Z2wb2isbD8uHbIFH2QgrYykSRTBXAZgLZvrnOJpM0/edit?usp=sharing"

st.set_page_config(page_title="Arca S&S - Gestión", layout="centered")

# --- BARRA LATERAL ---
st.sidebar.title("Menú Arca S&S")
modo = st.sidebar.radio("Ir a:", ["Vista Alumnos", "Administración 🔒"])

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    df_s = conn.read(spreadsheet=URL_ARCA, worksheet="Socios", ttl=0)
    df_r = conn.read(spreadsheet=URL_ARCA, worksheet="Reservas", ttl=0)
    # Limpieza de nombres de columnas
    df_s.columns = [str(c).strip().lower() for c in df_s.columns]
    df_r.columns = [str(c).strip().lower() for c in df_r.columns]
    return df_s, df_r

# --- MODO ALUMNOS ---
if modo == "Vista Alumnos":
    st.title("🏋️ Arca S&S")
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    
    df_socios, df_reservas = cargar_datos()
    
    if not df_socios.empty:
        # Unimos nombre y apellido para el selector
        df_socios['nombre_full'] = df_socios['nombre'] + " " + df_socios['apellido']
        alumno_sel = st.selectbox("Seleccioná tu nombre y apellido", [""] + df_socios['nombre_full'].tolist())
        
        if alumno_sel:
            # Obtener datos del alumno
            idx = df_socios[df_socios['nombre_full'] == alumno_sel].index[0]
            saldo = df_socios.at[idx, 'saldo_clases']
            
            st.info(f"Hola **{alumno_sel}**. Te quedan **{saldo}** clases en tu abono.")
            
            if saldo > 0:
                fec = st.date_input("Día de entrenamiento", min_value=pd.to_datetime("today"))
                hor = st.selectbox("Horario", ["08:00", "09:00", "10:00", "11:00", "17:00", "18:00", "19:00", "20:00"])
                
                if st.button("CONFIRMAR RESERVA", use_container_width=True):
                    # 1. Registrar la Reserva
                    nueva_reserva = pd.DataFrame([{"socio_id": alumno_sel, "fecha": str(fec), "hora": hor}])
                    df_r_actual = pd.concat([df_reservas, nueva_reserva], ignore_index=True)
                    conn.update(spreadsheet=URL_ARCA, worksheet="Reservas", data=df_r_actual)
                    
                    # 2. DESCUENTO AUTOMÁTICO
                    df_socios.at[idx, 'saldo_clases'] = saldo - 1
                    # Quitamos la columna temporal de nombre_full antes de subir
                    df_s_subir = df_socios.drop(columns=['nombre_full'])
                    conn.update(spreadsheet=URL_ARCA, worksheet="Socios", data=df_s_subir)
                    
                    st.balloons()
                    st.success(f"¡Tu horario está confirmado! En caso de que no puedas asistir, ¡avisanos!")
                    st.rerun()
            else
